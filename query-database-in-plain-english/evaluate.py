"""Measure execution accuracy: run every question through ask() and compare the rows.

python evaluate.py                       ask the model, save results.json, print the summary
python evaluate.py --rescore             compare the saved SQL again without calling the model
python evaluate.py --model qwen2.5:3b    use another local model
python evaluate.py --limit 3             only the first 3 questions (a quick smoke test)
"""
import argparse
import json
import sqlite3
import time
from collections import Counter
from pathlib import Path

import ask

HERE = Path(__file__).parent
RESULTS = HERE / "results.json"


def value_matches(g, e):
    """A number matches when it rounds to the expected value (5.58 matches 5.6)."""
    if isinstance(e, (int, float)) and isinstance(g, (int, float)):
        decimals = len(repr(float(e)).split(".")[1].rstrip("0")) if isinstance(e, float) else 0
        return abs(g - e) < 1e-6 or round(g, decimals) == e
    return str(g).strip().lower() == str(e).strip().lower()


def row_matches(got_row, expected_row):
    """Every expected value appears in the row; extra columns and column order don't matter."""
    unused = list(got_row)
    for e in expected_row:
        hit = next((i for i, g in enumerate(unused) if value_matches(g, e)), None)
        if hit is None:
            return False
        unused.pop(hit)
    return True


def same_result(got, expected, ordered):
    if len(got) != len(expected):
        return False
    if ordered:
        return all(row_matches(g, e) for g, e in zip(got, expected))
    unused = list(got)
    for e in expected:
        hit = next((i for i, g in enumerate(unused) if row_matches(g, e)), None)
        if hit is None:
            return False
        unused.pop(hit)
    return True


def score(item, result):
    """Add 'correct' to a result by running both queries on the read-only connection."""
    if result["status"] != "answered":
        return {**result, "correct": False}
    _, expected = ask.run_query(item["sql"])
    try:
        _, got = ask.run_query(result["sql"])
    except sqlite3.Error:
        return {**result, "correct": False}
    return {**result, "correct": same_result(got, expected, item["ordered"])}


def summary(results):
    counts = Counter()
    for r in results:
        if r["status"] != "answered":
            counts["Blocked, refused or failed"] += 1
        elif r["correct"]:
            counts["Correct"] += 1
        elif r["answer"] is not None:
            counts["Wrong, sentence shown to the user"] += 1
        else:
            counts["Wrong, sentence hidden by the numbers check"] += 1
    total = len(results)
    for label in ("Correct", "Wrong, sentence shown to the user",
                  "Wrong, sentence hidden by the numbers check", "Blocked, refused or failed"):
        print(f"{label:<45} {counts[label]:>3}")
    print(f"{'Total':<45} {total:>3}")
    retried = [r for r in results if r["retries"]]
    print(f"Retried after an SQL error: {len(retried)}, "
          f"correct after the retry: {sum(r['correct'] for r in retried)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rescore", action="store_true")
    parser.add_argument("--model", default=ask.MODEL)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    ask.MODEL = args.model
    items = json.loads((HERE / "questions.json").read_text())[:args.limit]

    if args.rescore:
        saved = json.loads(RESULTS.read_text())
        results = [score(item, r) for item, r in zip(items, saved["results"])]
    else:
        results = []
        for n, item in enumerate(items, 1):
            start = time.monotonic()
            result = score(item, ask.ask(item["q"]))
            result["seconds"] = round(time.monotonic() - start, 1)
            results.append(result)
            print(f"{n:>2}. {result['status']:<8} correct={result['correct']!s:<5} "
                  f"{result['seconds']:>6}s  {item['q']}")
    RESULTS.write_text(json.dumps({"model": ask.MODEL, "today": ask.TODAY, "results": results},
                                  indent=2, default=str))
    summary(results)


if __name__ == "__main__":
    main()
