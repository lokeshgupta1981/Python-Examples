"""Step 7: a person accepts, changes or skips every proposal, and decisions.csv records it.

Usage: python review.py [results.json]
Answers can be piped in for a test run, one per line; an empty line stands for Enter.
"""
import csv
import json
import sys

ORDER = ["URGENT", "REVIEW", "NEEDS_REPLY", "FYI", "SPAM_LIKE"]
KEYS = {"u": "URGENT", "n": "NEEDS_REPLY", "f": "FYI", "s": "SPAM_LIKE"}
CAREFUL = {"URGENT", "SPAM_LIKE", "REVIEW"}  # these always need an explicit answer


def ask(row: dict) -> str:
    careful = row["category"] in CAREFUL
    prompt = (" [y] accept [u/n/f/s] change [k] skip > " if careful
              else " [Enter] accept [u/n/f/s] change [k] skip > ")
    while True:
        try:
            answer = input(prompt).strip().lower()
        except EOFError:
            answer = "k"  # no more input: leave it in the inbox
        if not sys.stdin.isatty():  # echo piped answers, so the log shows them
            print(answer or "(Enter)")
        if answer == "y" or (answer == "" and not careful):
            return row["category"]
        if answer in KEYS:
            return KEYS[answer]
        if answer == "k":
            return "SKIP"


def proposals(results: dict) -> list[dict]:
    rows = []
    for file, entry in results.items():
        guarded = entry["guarded"]
        answer = guarded["result"] or {}
        if entry["rule"]:
            category, reason, items = entry["rule"], "header rule", []
        elif guarded["status"] != "ok":
            category, reason = "REVIEW", guarded["problem"]
            items = answer.get("action_items", [])
        else:
            category, reason = answer["category"], answer["reason"]
            items = answer["action_items"]
        rows.append({"file": file, "category": category, "model": answer.get("category"),
                     "reason": reason, "action_items": items})
    return sorted(rows, key=lambda r: (ORDER.index(r["category"]), r["file"]))


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "results.json"
    with open(path) as f:
        rows = proposals(json.load(f))
    decisions = []
    for row in rows:
        print(f"\n{row['category']:<11} {row['file']}  {row['reason']}")
        if row["category"] == "REVIEW":
            print(f"            model said: {row['model']}")
        for action in row["action_items"]:
            print(f"            - {action['task']} (\"{action['quote']}\")")
        decision = ask(row)
        if row["category"] == "REVIEW" and decision == "REVIEW":
            decision = "SKIP"  # a person must pick a real category
        decisions.append({"file": row["file"], "proposed": row["category"],
                          "decision": decision})
    with open("decisions.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "proposed", "decision"])
        writer.writeheader()
        writer.writerows(decisions)
    changed = sum(d["decision"] not in (d["proposed"], "SKIP") for d in decisions)
    print(f"\n{len(decisions)} decisions, {changed} changed, written to decisions.csv")


if __name__ == "__main__":
    main()
