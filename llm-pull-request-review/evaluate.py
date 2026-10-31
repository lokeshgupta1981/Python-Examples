"""Measure the reviewer on the planted-bug PRs.

    python evaluate.py run qwen2.5:3b     # calls the model once per hunk, writes raw-<model>.json
    python evaluate.py score              # scores every raw-*.json, writes results.csv
    python evaluate.py show qwen2.5:3b pr-9-injection   # prints one PR's stored review

The model runs once per PR at temperature 0 with no threshold. The thresholds
are applied afterwards to the same raw comments, so every row of results.csv
comes from the same model answers.
"""
import csv
import glob
import json
import sys
import time
from collections import Counter

from pydantic import ValidationError

from reviewer import (Hunk, HunkReview, filter_comments, local_diff, parse_hunks,
                      print_report, review_hunk)

REPO = "orderdesk-lite"
THRESHOLDS = [0.0, 0.5, 0.7, 0.9]
MAIN_SET = [f"pr-{n}" for n in range(1, 9)]      # 6 planted bugs + 2 clean refactors


def run(model: str) -> None:
    labels = json.load(open("labels.json"))
    results = []
    for branch in labels:
        start = time.perf_counter()
        hunks = []
        for hunk in parse_hunks(local_diff(REPO, "main", branch)):
            entry = {"path": hunk.path, "text": hunk.text,
                     "added_lines": sorted(hunk.added_lines)}
            try:
                entry["comments"] = review_hunk(hunk, model).model_dump()["comments"]
            except (ValidationError, Exception) as e:   # keep going, record it
                entry["error"] = f"{type(e).__name__}: {str(e)[:300]}"
            hunks.append(entry)
        seconds = round(time.perf_counter() - start, 1)
        results.append({"branch": branch, "seconds": seconds, "hunks": hunks})
        print(f"{branch}: {seconds} s, "
              f"{sum(len(h.get('comments', [])) for h in hunks)} raw comment(s)", flush=True)
    out = f"raw-{model.replace(':', '_')}.json"
    json.dump({"model": model, "results": results}, open(out, "w"), indent=2)
    print("wrote", out)


def is_correct(finding, label) -> bool:
    return (label is not None and finding.path == label["path"]
            and abs(finding.line - label["line"]) <= 2
            and finding.category == label["category"])


def score() -> None:
    labels = json.load(open("labels.json"))
    rows = []
    for raw_file in sorted(glob.glob("raw-*.json")):
        raw = json.load(open(raw_file))
        for threshold in THRESHOLDS:
            posted = correct = found = clean = 0
            dropped = Counter()
            seconds = []
            for result in raw["results"]:
                branch = result["branch"]
                if not branch.startswith(tuple(MAIN_SET)):
                    continue
                seconds.append(result["seconds"])
                findings = []
                for h in result["hunks"]:
                    if "error" in h:
                        dropped["invalid model output"] += 1
                        continue
                    hunk = Hunk(h["path"], h["text"], set(h["added_lines"]))
                    review = HunkReview.model_validate({"comments": h["comments"]})
                    findings += filter_comments(hunk, review, threshold, dropped)
                label = labels[branch]
                hits = [f for f in findings if is_correct(f, label)]
                posted += len(findings)
                correct += len(hits)
                found += 1 if hits else 0
                clean += len(findings) if label is None else 0
            rows.append({
                "model": raw["model"], "threshold": threshold,
                "comments_posted": posted, "correct": correct,
                "precision": round(correct / posted, 2) if posted else "",
                "bugs_found_of_6": found, "comments_on_clean_prs": clean,
                "dropped_line_check": dropped["line is not an added line"],
                "dropped_threshold": dropped["below threshold"],
                "invalid_outputs": dropped["invalid model output"],
                "avg_seconds_per_pr": round(sum(seconds) / len(seconds), 1),
            })
    with open("results.csv", "w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(row)


def show(model: str, branch: str, threshold: float = 0.7) -> None:
    raw = json.load(open(f"raw-{model.replace(':', '_')}.json"))
    [result] = [r for r in raw["results"] if r["branch"] == branch]
    findings, dropped = [], Counter()
    for h in result["hunks"]:
        if "error" in h:
            dropped["invalid model output"] += 1
            continue
        hunk = Hunk(h["path"], h["text"], set(h["added_lines"]))
        review = HunkReview.model_validate({"comments": h["comments"]})
        findings += filter_comments(hunk, review, threshold, dropped)
    print_report(findings, dropped)


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(sys.argv[2])
    elif sys.argv[1] == "show":
        show(sys.argv[2], sys.argv[3])
    else:
        score()
