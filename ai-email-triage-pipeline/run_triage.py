"""Step 6: triage every email in the inbox and save the proposals to results.json.

Every email goes to the model, also the ones the header rules label, so evaluate.py can
compare "model only", "broad rules + model" and "rules with watch list + model" from one run.
The injected emails (labels.csv, injected=yes) also go through the naive prompt.
The script saves after every email, so an interrupted run resumes where it stopped.

Usage: python run_triage.py [--model NAME] [--limit N] [--out FILE]
"""
import argparse
import csv
import json
from pathlib import Path

import triage
from mail_reader import read_folder
from rules import prelabel


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=triage.MODEL)
    parser.add_argument("--limit", type=int, default=None, help="only the first N emails")
    parser.add_argument("--out", default="results.json")
    args = parser.parse_args()
    triage.MODEL = args.model

    with open("labels.csv", newline="") as f:
        injected = {row["file"] for row in csv.DictReader(f) if row["injected"] == "yes"}

    out = Path(args.out)
    results = json.loads(out.read_text()) if out.exists() else {}
    items = read_folder(Path("mailbox/inbox"))[:args.limit]
    for number, item in enumerate(items, 1):
        if item.file in results:
            continue  # done in an earlier run
        row = {"rule": prelabel(item), "broad_rule": prelabel(item, set()),
               "guarded": triage.triage(item)}
        if item.file in injected:
            row["naive"] = triage.triage(item, guarded=False)
        results[item.file] = row
        out.write_text(json.dumps(results, indent=2))  # save after every email
        answer = row["guarded"]["result"] or {}
        print(f"{number:2}/{len(items)} {item.file}: {answer.get('category')} "
              f"({row['guarded']['status']}, {row['guarded']['seconds']} s)")

    calls = [r[k] for r in results.values() for k in ("guarded", "naive") if k in r]
    seconds = sum(c["seconds"] for c in calls)
    print(f"{len(calls)} triage calls, {seconds / max(len(results), 1):.1f} s of model "
          f"compute per email, model {triage.MODEL}")


if __name__ == "__main__":
    main()
