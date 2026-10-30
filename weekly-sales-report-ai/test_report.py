"""Checks for the parts that don't need the model. Run: python -m pytest -q"""
from pathlib import Path

import report as r

FACTS = [
    {"id": "revenue", "label": "Revenue 2026-W40", "value": 26150.5, "display": "$26,150", "alert": False},
    {"id": "revenue_prev", "label": "Revenue 2026-W39", "value": 24800.0, "display": "$24,800", "alert": False},
    {"id": "revenue_change", "label": "Revenue change vs last week", "value": 5.44, "display": "+5.4%", "alert": False},
    {"id": "north_change", "label": "North region revenue change", "value": -12.43, "display": "-12.4%", "alert": True},
    {"id": "cold_brew_kit_change", "label": "Cold Brew Kit product revenue change", "value": None,
     "display": "new product", "alert": True},
]
PRODUCTS = ["Decaf 500g", "Cold Brew Kit"]


def line(text, *ids):
    return r.Line(text=text, fact_ids=list(ids))


def narrative(summary, highlights=None, risks=None):
    return r.Narrative(summary=summary,
                       highlights=highlights or [line("Sales were steady.")],
                       risks=risks or [line("Nothing to watch.")],
                       week_over_week=line("Revenue was $26,150.", "revenue"))


def test_formatting_helpers():
    assert r.money(26150.5) == "$26,150"
    assert r.pct(-12.43) == "-12.4%"
    assert r.signed_money(-971.9) == "-$972"
    assert r.slug("Cold Brew Kit") == "cold_brew_kit"
    assert r.change(5, 0) is None


def test_number_key_ignores_sign_and_format():
    assert r.number_key("$26,150") == r.number_key("26,150")
    assert r.number_key("-12.4%") == r.number_key("12.4%")
    assert r.number_key("12.4%") != r.number_key("12.4")


def test_numbers_in_skips_weeks_dates_and_product_names():
    text = "In 2026-W43 (week 43, from 2026-10-19) Decaf 500g sold $1,432, down 6.4%."
    assert r.numbers_in(text, PRODUCTS) == ["$1,432", "6.4%"]


def test_number_not_in_table_blocks():
    n = narrative(line("Revenue increased by $1,350 to $26,150, a +5.4% increase.",
                       "revenue", "revenue_change"))
    problems, numbers = r.check_numbers(n, FACTS, PRODUCTS)
    assert numbers == 4
    assert r.blocking(problems) == [{"part": "summary", "number": "$1,350", "kind": "not_in_table"}]


def test_uncited_number_does_not_block():
    n = narrative(line("North revenue fell 12.4%."))
    problems, _ = r.check_numbers(n, FACTS, PRODUCTS)
    assert problems == [{"part": "summary", "number": "12.4%", "kind": "not_cited"}]
    assert r.blocking(problems) == []


def test_cut_off_and_non_ascii_lines_block():
    assert r.looks_cut("Revenue rose to $26,150 and")
    assert r.looks_cut("Revenue rose to $26,150。")
    assert not r.looks_cut("Revenue rose to $26,150.")


def test_fallback_rewrites_only_failing_lines():
    n = narrative(line("Revenue rose by $1,350 to $26,150.", "revenue"))
    fixed, used = r.fallback(n, FACTS, PRODUCTS)
    assert used == 1
    assert fixed.summary.text == "[check] Revenue 2026-W40 is $26,150."
    assert fixed.week_over_week.text == "Revenue was $26,150."


def test_missing_alerts():
    n = narrative(line("Revenue was $26,150.", "revenue"),
                  risks=[line("North revenue fell 12.4%.", "north_change")])
    assert r.missing_alerts(n, FACTS) == ["cold_brew_kit_change"]


def test_fact_table_and_render(tmp_path):
    orders = r.load_orders()
    facts = r.build_facts(orders, "2026-W43")
    ids = {f["id"] for f in facts}
    assert {"revenue", "revenue_change_amount", "orders_change_count",
            "north_change", "cold_brew_kit_change"} <= ids
    alerts = [f["id"] for f in facts if f["alert"]]
    assert alerts == ["marketplace_return_rate", "cold_brew_kit_change"]
    assert len(r.build_first_facts(orders, "2026-W43")) == len(facts) - 2

    n = narrative(line("Revenue was $26,150.", "revenue"))
    pdf = r.render_report(orders, "2026-W43", facts, n, out_dir=tmp_path)
    assert Path(pdf).stat().st_size > 10_000
    assert "| Revenue |" in (tmp_path / "report-2026-W43.md").read_text()
