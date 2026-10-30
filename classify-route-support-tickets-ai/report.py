"""Read results.csv, print the accuracy and threshold tables, save summary.json.

Usage: python report.py [results.csv]
It does not call the model, so trying another threshold takes a second.
"""
import csv
import json
import statistics
import sys
from collections import defaultdict

from triage import CONFIG, HERE, QUEUES

THRESHOLDS = [0.5, 0.7, 0.9, 0.95, 0.99, 0.999]
CATEGORIES = [c["name"] for c in CONFIG["categories"]]

path = HERE / (sys.argv[1] if len(sys.argv) > 1 else "results.csv")
with path.open() as f:
    rows = list(csv.DictReader(f))

by_prompt = defaultdict(list)
for r in rows:
    r["confidence"] = float(r["confidence"])
    # right_team: the predicted and the expected category map to the same queue
    r["right_team"] = (r["category"] != "INVALID"
                       and QUEUES[r["category"]] == QUEUES[r["expected_category"]])
    by_prompt[r["prompt"]].append(r)

summary = {}
for prompt, items in by_prompt.items():
    n = len(items)
    per_category = {}
    for c in CATEGORIES + ["All"]:
        subset = [r for r in items if c == "All" or r["expected_category"] == c]
        per_category[c] = {
            "tickets": len(subset),
            "category_correct": sum(r["category"] == r["expected_category"] for r in subset),
            "priority_correct": sum(r["priority"] == r["expected_priority"] for r in subset)}
    thresholds = [{"threshold": None, "auto_routed": n,
                   "wrong_team_in_auto": sum(not r["right_team"] for r in items),
                   "to_humans": 0}]
    for t in THRESHOLDS:
        auto = [r for r in items if r["category"] != "INVALID" and r["confidence"] >= t]
        thresholds.append({
            "threshold": t, "auto_routed": len(auto),
            "wrong_team_in_auto": sum(not r["right_team"] for r in auto),
            "to_humans": n - len(auto)})
    summary[prompt] = {
        "tickets": n,
        "invalid": sum(r["category"] == "INVALID" for r in items),
        "retries": sum(int(r["attempts"]) > 1 for r in items),
        "median_model_ms": statistics.median(int(r["model_ms"]) for r in items),
        "median_prompt_tokens": statistics.median(int(r["prompt_tokens"]) for r in items),
        "per_category": per_category,
        "thresholds": thresholds}

for prompt, s in summary.items():
    print(f"\n== {prompt}: {s['tickets']} tickets, {s['invalid']} invalid, "
          f"{s['retries']} retries, median model time {s['median_model_ms'] / 1000:.1f} s, "
          f"median prompt tokens {s['median_prompt_tokens']}")
    print(f"{'category':<10} {'tickets':>7} {'cat ok':>7} {'prio ok':>7}")
    for c, v in s["per_category"].items():
        print(f"{c:<10} {v['tickets']:>7} {v['category_correct']:>7} {v['priority_correct']:>7}")
    print(f"{'threshold':<10} {'auto':>5} {'wrong team':>10} {'to humans':>9}")
    for t in s["thresholds"]:
        label = "none" if t["threshold"] is None else str(t["threshold"])
        print(f"{label:<10} {t['auto_routed']:>5} {t['wrong_team_in_auto']:>10} {t['to_humans']:>9}")

(HERE / "summary.json").write_text(json.dumps(summary, indent=2))
