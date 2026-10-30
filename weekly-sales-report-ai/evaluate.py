"""Compare three ways of writing the report:

- raw:   the model gets 56 rows of daily revenue (2 weeks x 7 days x 4 regions)
         for 2026-W42 and adds them up itself, one call, no check
- first: the first fact table and prompt (no differences, no alerts, no rule 5)
- final: the final fact table and prompt, as in report.py

Each approach goes through the same number check. Results go to
results/evaluation.json; the final reports go to results/<approach>-<week>.json
so a person can read them and record wrong claims in hand_review.json.

Usage: python evaluate.py [--model qwen2.5:7b] [--weeks 2026-W40 2026-W41 ...]
"""
import argparse
import json
import time
from pathlib import Path

import report as r

WEEKS = ["2026-W40", "2026-W41", "2026-W42", "2026-W43"]
RAW_WEEK = "2026-W42"

SYSTEM_RAW = """You write the weekly sales report for BeanBox, an online coffee shop.
Work out the weekly numbers from the daily rows you get.
Highlights are good news, risks are problems to watch. One sentence each.
Leave fact_ids empty. Plain business English, no greetings."""


class Recorder:
    """Wraps generate_narrative() to keep every reply and its duration."""

    def __init__(self):
        self.calls = []
        self.original = r.generate_narrative

    def __call__(self, messages, model=r.MODEL, **kwargs):
        started = time.perf_counter()
        narrative, raw = self.original(messages, model, **kwargs)
        self.calls.append({"seconds": round(time.perf_counter() - started, 1), "reply": raw})
        return narrative, raw


def raw_prompt(orders, week):
    weeks = sorted(orders["week"].unique())
    two = orders[orders["week"].isin([weeks[weeks.index(week) - 1], week])]
    daily = two.groupby(["date", "region"])["revenue"].sum().round(2).reset_index()
    rows = "\n".join(f"{d:%Y-%m-%d},{reg},{rev}" for d, reg, rev in daily.itertuples(index=False))
    return (f"Write the report for week {week}. Compare it with the week before.\n"
            f"Daily revenue by region (date,region,revenue), {len(daily)} rows:\n{rows}")


def stories_found(narrative, facts, events, week):
    """Planted stories for this week that a highlight or risk cites."""
    planted = [e["fact_id"] for e in events if e["week"] == week]
    cited = {i for line in narrative.highlights + narrative.risks for i in line.fact_ids}
    return len(planted), sum(1 for p in planted if p in cited)


def run(approach, orders, week, product_names, events, model, recorder):
    facts = r.build_facts(orders, week)
    first_call = len(recorder.calls)
    if approach == "raw":
        messages = [{"role": "system", "content": SYSTEM_RAW},
                    {"role": "user", "content": raw_prompt(orders, week)}]
        narrative, _ = r.generate_narrative(messages, model)
        problems, numbers = r.check_numbers(narrative, facts, product_names)
        log, used = [{"attempt": 0, "numbers": numbers, "problems": problems}], 0
        planted = [e for e in events if e["week"] == week]
        risky = " ".join(x.text for x in narrative.highlights + narrative.risks)
        stories = (len(planted), sum(1 for e in planted if "North" in risky))
    else:
        if approach == "first":
            facts = r.build_first_facts(orders, week)
            saved = r.SYSTEM, r.build_prompt
            r.SYSTEM, r.build_prompt = r.SYSTEM_FIRST, r.build_prompt_first
        try:
            narrative, log, used = r.write_checked_narrative(week, facts, product_names, model)
        finally:
            if approach == "first":
                r.SYSTEM, r.build_prompt = saved
        stories = stories_found(narrative, facts, events, week)
    return {
        "approach": approach, "week": week,
        "attempts": len(log),
        "numbers_first": log[0]["numbers"],
        "blocking_first": r.blocking(log[0]["problems"]),
        "fallbacks": used,
        "planted": stories[0], "planted_found": stories[1],
        "missing_alerts": r.missing_alerts(narrative, facts),
        "review_words": r.review_words(narrative),
        "calls": recorder.calls[first_call:],
        "final": narrative.model_dump(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=r.MODEL)
    parser.add_argument("--weeks", nargs="*", default=WEEKS)
    parser.add_argument("--approaches", nargs="*", default=["raw", "first", "final"])
    args = parser.parse_args()

    orders = r.load_orders()
    product_names = sorted(orders["product"].unique())
    events = json.loads(Path("planted_events.json").read_text())
    recorder = Recorder()
    r.generate_narrative = recorder

    out = Path("results")
    out.mkdir(exist_ok=True)
    results = []
    for approach in args.approaches:
        weeks = [RAW_WEEK] if approach == "raw" else args.weeks
        for week in weeks:
            result = run(approach, orders, week, product_names, events, args.model, recorder)
            results.append(result)
            (out / f"{approach}-{week}.json").write_text(json.dumps(result, indent=2))
            print(f"{approach} {week}: attempts={result['attempts']} "
                  f"numbers_first={result['numbers_first']} "
                  f"blocking_first={len(result['blocking_first'])} "
                  f"stories={result['planted_found']}/{result['planted']} "
                  f"seconds={[c['seconds'] for c in result['calls']]}")
    (out / "evaluation.json").write_text(json.dumps(
        {"model": args.model, "results": results}, indent=2))

    review = Path("hand_review.json")
    if not review.exists():  # one entry per report, filled in by a person
        review.write_text(json.dumps(
            [{"approach": x["approach"], "week": x["week"], "wrong_claims": [],
              "bad_news_as_highlight": []} for x in results], indent=2))


if __name__ == "__main__":
    main()
