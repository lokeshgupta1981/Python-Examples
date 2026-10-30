"""Classify every test ticket with both prompts and save one row per ticket and prompt.

Usage: python evaluate.py [--model qwen2.5:7b] [--limit N] [--out results.csv]
Rows already in the output file are skipped, so an interrupted run continues.
"""
import argparse
import csv
import json
import time

import triage
from triage import HERE, category_confidence, classify, few_shot_messages, zero_shot_messages

PROMPTS = {"zero-shot": zero_shot_messages, "few-shot": few_shot_messages}
FIELDS = ["prompt", "id", "expected_category", "expected_priority", "category", "priority",
          "confidence", "runner_up", "runner_up_confidence", "attempts",
          "prompt_tokens", "output_tokens", "model_ms", "wall_ms"]

parser = argparse.ArgumentParser()
parser.add_argument("--model", default=triage.MODEL)
parser.add_argument("--limit", type=int, default=None, help="only the first N test tickets")
parser.add_argument("--out", default="results.csv")
args = parser.parse_args()
triage.MODEL = args.model  # call_model() reads this at call time

tickets = [json.loads(line)
           for line in (HERE / "tickets-test.jsonl").read_text().splitlines()][:args.limit]
out = HERE / args.out
done = set()
if out.exists():
    with out.open() as f:
        done = {(row["prompt"], int(row["id"])) for row in csv.DictReader(f)}

with out.open("a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    if not done:
        writer.writeheader()
    for prompt, build in PROMPTS.items():
        for ticket in tickets:
            if (prompt, ticket["id"]) in done:
                continue
            start = time.perf_counter()
            result, response, attempts = classify(build(ticket["text"]))
            wall_ms = round((time.perf_counter() - start) * 1000)
            confidence, runner_up, runner_up_conf = (
                category_confidence(response) if result else (0.0, "", 0.0))
            category = result.category.value if result else "INVALID"
            priority = result.priority.value if result else "INVALID"
            model_ms = round(((response.prompt_eval_duration or 0)
                              + (response.eval_duration or 0)) / 1e6)
            writer.writerow({
                "prompt": prompt, "id": ticket["id"],
                "expected_category": ticket["category"],
                "expected_priority": ticket["priority"],
                "category": category, "priority": priority,
                "confidence": f"{confidence:.6f}", "runner_up": runner_up,
                "runner_up_confidence": f"{runner_up_conf:.6f}", "attempts": attempts,
                "prompt_tokens": response.prompt_eval_count,
                "output_tokens": response.eval_count,
                "model_ms": model_ms, "wall_ms": wall_ms})
            f.flush()
            verdict = "ok" if category == ticket["category"] else "BAD"
            print(f"{prompt} #{ticket['id']} {verdict} {category} {priority} "
                  f"conf={confidence:.4f} {wall_ms} ms", flush=True)
