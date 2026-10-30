"""Step 9: compare results.json with labels.csv, print the table and write summary.json.

A setup takes the rule label where it has one, and the model's category otherwise
(also for needs_review emails). An expected action item counts as found when all its
key words appear in one extracted item: in the task text alone, or in the task plus quote.
Usage: python evaluate.py [results.json]
"""
import csv
import json
import sys
from pathlib import Path

from triage import words

SETUPS = {"Model only": None, "Broad rules + model": "broad_rule",
          "Rules with watch list + model": "rule"}


def found(expected: str, actions: list[dict], with_quote: bool) -> bool:
    keys = expected.split()
    for action in actions:
        text = action["task"] + (" " + action["quote"] if with_quote else "")
        if all(key in words(text) for key in keys):
            return True
    return False


def main() -> None:
    results = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else "results.json").read_text())
    with open("labels.csv", newline="") as f:
        labels = [row for row in csv.DictReader(f) if row["file"] in results]

    urgent = [row for row in labels if row["category"] == "URGENT"]
    expected_total = sum(len([a for a in row["action_items"].split(";") if a]) for row in labels)
    summary = {}
    print(f"{'Setup':<31} {'Correct':>9} {'URGENT':>7} {'Items (task)':>13} "
          f"{'Items (task+quote)':>19} {'Model reads':>12}")
    for setup, rule_key in SETUPS.items():
        correct, recall, task_only, with_quote, reads, misses = 0, 0, 0, 0, 0, []
        for row in labels:
            entry = results[row["file"]]
            rule = entry[rule_key] if rule_key else None
            answer = entry["guarded"]["result"] or {}
            category = rule or answer.get("category")
            actions = [] if rule else answer.get("action_items", [])
            reads += rule is None
            if category == row["category"]:
                correct += 1
                recall += row["category"] == "URGENT"
            else:
                misses.append(f"{row['file']}: expected {row['category']}, got {category}")
            for expected in filter(None, row["action_items"].split(";")):
                task_only += found(expected, actions, False)
                with_quote += found(expected, actions, True)
        summary[setup] = {"correct": correct, "emails": len(labels), "urgent_found": recall,
                          "urgent": len(urgent), "items_task": task_only,
                          "items_task_quote": with_quote, "items_expected": expected_total,
                          "model_reads": reads, "misses": misses}
        print(f"{setup:<31} {correct:>4} of {len(labels):<2} {recall:>2} of {len(urgent)} "
              f"{task_only:>6} of {expected_total:<3} {with_quote:>11} of {expected_total:<4} "
              f"{reads:>8}")
    for setup, data in summary.items():
        for miss in data["misses"]:
            print(f"  {setup}: {miss}")

    print("\nStatus of the guarded prompt:",
          {s: sum(r["guarded"]["status"] == s for r in results.values())
           for s in ("ok", "needs_review", "invalid")})
    for file, entry in results.items():
        if "naive" in entry:
            for prompt in ("guarded", "naive"):
                run = entry[prompt]
                answer = run["result"] or {}
                tasks = [a["task"] for a in answer.get("action_items", [])]
                print(f"  {file} {prompt}: {answer.get('category')} ({run['status']}) {tasks}")
    Path("summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
