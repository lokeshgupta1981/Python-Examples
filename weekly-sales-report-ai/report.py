"""Write the BeanBox weekly sales report: pandas computes the numbers, a local
Ollama model writes the narrative, and code checks every number in it.

Usage: python report.py --week 2026-W43 [--model qwen2.5:7b]
"""
import argparse
import json
import re
from pathlib import Path

import markdown
import matplotlib
import ollama
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field
from weasyprint import HTML

matplotlib.use("Agg")  # draw charts without a display
import matplotlib.pyplot as plt  # noqa: E402

MODEL = "qwen2.5:7b"  # the article's numbers were measured with this model
MAX_RETRIES = 2
REGION_ALERT = -20.0  # flag a region down 20% or more
RETURN_ALERT = 0.06   # flag a channel with more than 6% returns


# ---------------------------------------------------------------- Step 2

def load_orders(path="orders.csv"):
    orders = pd.read_csv(path, parse_dates=["date"])
    orders["revenue"] = orders["units"] * orders["unit_price"] * (1 - orders["discount"])
    iso = orders["date"].dt.isocalendar()
    orders["week"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)
    return orders


def weekly_numbers(orders, by=None):
    keys = ["week"] + ([by] if by else [])
    weekly = orders.groupby(keys).agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "nunique"),
        units=("units", "sum"),
        return_rate=("returned", "mean"),
    )
    weekly["aov"] = weekly["revenue"] / weekly["orders"]
    if by:  # one column per region, channel or product
        weekly = weekly.unstack(by)
    return weekly


# ---------------------------------------------------------------- Step 3

def money(x):
    return "$" + f"{x:,.0f}"  # 26150.5 -> "$26,150"


def pct(x):
    return f"{x:+.1f}%"  # -12.43 -> "-12.4%"


def signed_money(x):
    sign = "+" if x >= 0 else "-"
    return sign + "$" + f"{abs(x):,.0f}"  # -971.9 -> "-$972"


def signed_count(x):
    return f"{x:+,.0f}"  # -37 -> "-37"


def rate(x):
    return f"{x * 100:.1f}%"  # 0.0412 -> "4.1%"


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def change(now, before):
    if pd.isna(before) or before == 0:
        return None  # no change for a product that is new
    return (now - before) / before * 100


def build_facts(orders, week):
    facts = []

    def add(fact_id, label, value, display, alert=False):
        facts.append({"id": fact_id, "label": label,
                      "value": None if value is None else round(float(value), 4),
                      "display": display, "alert": alert})

    total = weekly_numbers(orders)
    weeks = list(total.index)
    prev = weeks[weeks.index(week) - 1]
    now, before = total.loc[week], total.loc[prev]

    add("revenue", f"Revenue {week}", now.revenue, money(now.revenue))
    add("revenue_prev", f"Revenue {prev}", before.revenue, money(before.revenue))
    diff = change(now.revenue, before.revenue)
    add("revenue_change", "Revenue change vs last week", diff, pct(diff))
    add("revenue_change_amount", "Revenue change in dollars vs last week",
            now.revenue - before.revenue, signed_money(now.revenue - before.revenue))

    add("orders", f"Orders {week}", now.orders, f"{now.orders:,.0f}")
    add("orders_prev", f"Orders {prev}", before.orders, f"{before.orders:,.0f}")
    diff = change(now.orders, before.orders)
    add("orders_change", "Orders change vs last week", diff, pct(diff))
    add("orders_change_count", "Orders change in orders vs last week",
        now.orders - before.orders, signed_count(now.orders - before.orders))

    add("aov", f"Average order value {week}", now.aov, f"${now.aov:,.2f}")
    add("aov_prev", f"Average order value {prev}", before.aov, f"${before.aov:,.2f}")
    diff = change(now.aov, before.aov)
    add("aov_change", "Average order value change vs last week", diff, pct(diff))
    add("return_rate", f"Return rate {week}", now.return_rate, rate(now.return_rate))

    region = weekly_numbers(orders, "region")["revenue"]
    for name in region.columns:
        r_now, r_before = region.loc[week, name], region.loc[prev, name]
        add(f"{slug(name)}_revenue", f"{name} region revenue", r_now, money(r_now))
        diff = change(r_now, r_before)
        add(f"{slug(name)}_change", f"{name} region revenue change",
            diff, pct(diff), alert=bool(diff <= REGION_ALERT))

    returns = weekly_numbers(orders, "channel")["return_rate"]
    for name in returns.columns:
        r_now = returns.loc[week, name]
        add(f"{slug(name)}_return_rate", f"{name} channel return rate",
            r_now, rate(r_now), alert=bool(r_now > RETURN_ALERT))

    products = weekly_numbers(orders, "product")["revenue"]
    this_week = products.loc[week].dropna().sort_values(ascending=False)
    new = [n for n in this_week.index if pd.isna(products.loc[prev, n])]
    picked = list(this_week.index[:2]) + list(this_week.index[-2:]) + new
    for name in dict.fromkeys(picked):  # top two, bottom two and new, no duplicates
        p_now = this_week[name]
        p_before = products.loc[prev, name]
        diff = change(p_now, p_before)
        add(f"{slug(name)}_revenue", f"{name} product revenue", p_now, money(p_now))
        add(f"{slug(name)}_change", f"{name} product revenue change", diff,
            "new product" if diff is None else pct(diff), alert=diff is None)
    return facts


def build_first_facts(orders, week):
    """The first fact table from the article: no differences and no alerts."""
    first = [dict(f, alert=False) for f in build_facts(orders, week)
             if f["id"] not in ("revenue_change_amount", "orders_change_count")]
    return first


# ---------------------------------------------------------------- Step 4

SYSTEM = """You write the weekly sales report for BeanBox, an online coffee shop.
Rules:
1. Use only the facts in the fact table. Do not calculate, round, add or compare numbers.
2. Copy every number exactly as its "display" string, for example $26,150 or -12.4%.
3. For every sentence, list the ids of the facts it uses in fact_ids.
4. Highlights are good news, risks are problems to watch. One sentence each.
5. Every fact listed under "Must mention" needs its own highlight or risk.
6. Plain business English, no greetings."""

# The first version of the prompt: no rule 5 and no "Must mention" line.
SYSTEM_FIRST = SYSTEM.replace(
    '5. Every fact listed under "Must mention" needs its own highlight or risk.\n'
    "6. Plain", "5. Plain")


def build_prompt(week, facts):
    table = [{"id": f["id"], "label": f["label"], "display": f["display"]} for f in facts]
    alerts = [f["id"] for f in facts if f.get("alert")]
    return (f"Write the report for week {week}.\n"
            f"Fact table:\n{json.dumps(table, indent=1)}\n"
            f"Must mention: {', '.join(alerts) or 'nothing this week'}")


def build_prompt_first(week, facts):
    table = [{"id": f["id"], "label": f["label"], "display": f["display"]} for f in facts]
    return f"Write the report for week {week}.\nFact table:\n{json.dumps(table, indent=1)}"


# ---------------------------------------------------------------- Step 5

class Line(BaseModel):
    text: str = Field(max_length=300)
    fact_ids: list[str] = Field(max_length=4)


class Narrative(BaseModel):
    summary: Line
    highlights: list[Line] = Field(min_length=1, max_length=4)
    risks: list[Line] = Field(min_length=1, max_length=3)
    week_over_week: Line


def generate_narrative(messages, model=MODEL, temperature=0.0, seed=1):
    response = ollama.chat(
        model=model,
        messages=messages,
        format=Narrative.model_json_schema(),
        options={"temperature": temperature, "seed": seed, "num_predict": 700},
    )
    narrative = Narrative.model_validate_json(response.message.content)
    return narrative, response.message.content


# ---------------------------------------------------------------- Step 6

NUMBER = re.compile(r"[-+]?\$?\d[\d,]*(?:\.\d+)?%?")
ALLOWED = [re.compile(p, re.IGNORECASE) for p in (
    r"\b\d{4}-W\d{2}\b",       # 2026-W43
    r"\bweek\s+\d{1,2}\b",     # week 43
    r"\b\d{4}-\d{2}-\d{2}\b",  # 2026-10-19
)]
REVIEW_WORDS = re.compile(r"\b(doubled|tripled|halved|twice|half)\b", re.IGNORECASE)


def number_key(text):
    digits = text.replace("$", "").replace(",", "").replace("%", "").lstrip("+-")
    return round(float(digits), 2), text.endswith("%")


def numbers_in(text, product_names):
    for name in product_names:  # "Decaf 500g" is a name, not a number
        text = re.sub(re.escape(name), " ", text, flags=re.IGNORECASE)
    for pattern in ALLOWED:
        text = pattern.sub(" ", text)
    return [m.group().rstrip(",") for m in NUMBER.finditer(text)]


def lines_of(narrative):
    yield "summary", narrative.summary
    for line in narrative.highlights:
        yield "highlights", line
    for line in narrative.risks:
        yield "risks", line
    yield "week_over_week", narrative.week_over_week


def looks_cut(text):
    return not text.rstrip().endswith((".", "!", "?")) or not text.isascii()


def check_numbers(narrative, facts, product_names):
    known = {number_key(f["display"]): f["id"] for f in facts if f["value"] is not None}
    problems, numbers = [], 0
    for part, line in lines_of(narrative):  # summary, highlights, risks, week_over_week
        for number in numbers_in(line.text, product_names):
            numbers += 1
            key = number_key(number)
            if key not in known:
                problems.append({"part": part, "number": number, "kind": "not_in_table"})
            elif known[key] not in line.fact_ids:
                problems.append({"part": part, "number": number, "kind": "not_cited"})
        if looks_cut(line.text):
            problems.append({"part": part, "number": "", "kind": "cut_off"})
    return problems, numbers


def review_words(narrative):
    """Words such as "doubled" carry a number without digits; a person checks them."""
    return [(part, m.group()) for part, line in lines_of(narrative)
            for m in REVIEW_WORDS.finditer(line.text)]


def blocking(problems):
    return [p for p in problems if p["kind"] in ("not_in_table", "cut_off")]


def retry_message(problems):
    lines = []
    for p in problems:
        if p["kind"] == "not_in_table":
            lines.append(f'- In {p["part"]}, the number {p["number"]} is not a display '
                         "string in the fact table.")
        else:
            lines.append(f'- In {p["part"]}, a sentence is cut off or not in English.')
    return ("Your report has these problems:\n" + "\n".join(lines) +
            "\nWrite the whole report again. Use only display strings from the fact "
            "table, keep every sentence short and end it with a period.")


def fallback(narrative, facts, product_names):
    by_id = {f["id"]: f for f in facts}
    known = {number_key(f["display"]) for f in facts if f["value"] is not None}
    used = 0

    def fix(line):
        nonlocal used
        bad = [n for n in numbers_in(line.text, product_names)
               if number_key(n) not in known]
        if not bad and not looks_cut(line.text):
            return line  # this line passes, keep it
        used += 1
        cited = [by_id[i] for i in line.fact_ids if i in by_id]
        text = "; ".join(f"{f['label']} is {f['display']}" for f in cited)
        return Line(text=f"[check] {text or 'see the numbers table'}.",
                    fact_ids=[f["id"] for f in cited])

    return Narrative(summary=fix(narrative.summary),
                     highlights=[fix(x) for x in narrative.highlights],
                     risks=[fix(x) for x in narrative.risks],
                     week_over_week=fix(narrative.week_over_week)), used


def write_checked_narrative(week, facts, product_names, model=MODEL):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": build_prompt(week, facts)}]
    log = []
    for attempt in range(MAX_RETRIES + 1):  # MAX_RETRIES = 2
        narrative, raw = generate_narrative(messages, model)
        problems, numbers = check_numbers(narrative, facts, product_names)
        log.append({"attempt": attempt, "numbers": numbers, "problems": problems})
        if not blocking(problems):
            return narrative, log, 0
        messages += [{"role": "assistant", "content": raw},
                     {"role": "user", "content": retry_message(blocking(problems))}]
    narrative, used = fallback(narrative, facts, product_names)
    return narrative, log, used


def missing_alerts(narrative, facts):
    cited = {i for line in narrative.highlights + narrative.risks for i in line.fact_ids}
    return [f["id"] for f in facts if f["alert"] and f["id"] not in cited]


# ---------------------------------------------------------------- Step 7

CSS = """
@page { size: A4; margin: 16mm; }
body { font-family: sans-serif; font-size: 10pt; color: #222; }
h1 { font-size: 16pt; color: #1f5f99; margin: 0 0 8px; }
h2 { font-size: 12pt; color: #1f5f99; margin: 12px 0 4px; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #ccc; padding: 3px 6px; text-align: right; }
th:first-child, td:first-child { text-align: left; }
img { width: 100%; }
ul { margin: 0; padding-left: 18px; }
"""


def revenue_chart(orders, week, path):
    revenue = weekly_numbers(orders)["revenue"]
    colors = ["#1f5f99" if w == week else "#a9c4de" for w in revenue.index]
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.bar([w[-3:] for w in revenue.index], revenue.values, color=colors)
    ax.set_ylabel("Revenue ($)")
    ax.set_title("Revenue by week")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def render_report(orders, week, facts, narrative, out_dir="reports"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    chart = f"revenue-{week}.png"
    revenue_chart(orders, week, out / chart)

    env = Environment(loader=FileSystemLoader("templates"), autoescape=False)
    text = env.get_template("report.md.j2").render(
        week=week, facts={f["id"]: f for f in facts}, chart=chart, n=narrative)
    (out / f"report-{week}.md").write_text(text)

    body = markdown.markdown(text, extensions=["tables"])
    html = f"<html><head><style>{CSS}</style></head><body>{body}</body></html>"
    (out / f"report-{week}.html").write_text(html)
    HTML(string=html, base_url=str(out)).write_pdf(out / f"report-{week}.pdf")
    return out / f"report-{week}.pdf"


# ---------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description="Write the weekly sales report.")
    parser.add_argument("--week", required=True, help="ISO week, for example 2026-W43")
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--orders", default="orders.csv")
    parser.add_argument("--out", default="reports")
    args = parser.parse_args()

    orders = load_orders(args.orders)
    product_names = sorted(orders["product"].unique())
    facts = build_facts(orders, args.week)
    narrative, log, used = write_checked_narrative(args.week, facts, product_names,
                                                   model=args.model)
    pdf = render_report(orders, args.week, facts, narrative, args.out)
    missing = missing_alerts(narrative, facts)
    Path(args.out, f"log-{args.week}.json").write_text(json.dumps(
        {"week": args.week, "model": args.model, "attempts": log, "fallbacks": used,
         "missing_alerts": missing, "review_words": review_words(narrative)}, indent=2))
    print(f"{args.week}: attempts={len(log)} "
          f"mismatches_first={len(blocking(log[0]['problems']))} "
          f"fallbacks={used} missing_alerts={missing} report={pdf}")


if __name__ == "__main__":
    main()
