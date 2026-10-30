"""Runs VADER and the LLM on every labelled message and saves one row per message.

Each row is written as soon as it is ready, so an interrupted run resumes where it stopped.

Usage:
    python evaluate.py                                    # all 50 messages, qwen2.5:7b
    python evaluate.py --model qwen2.5:3b --limit 3 --out smoke.csv
"""
import argparse
import csv
import os
import time

import detector

FIELDS = ["id", "customer", "text", "sentiment", "should_escalate", "case",
          "vader_label", "vader_compound",
          "llm_sentiment", "llm_anger", "llm_churn", "llm_risk", "llm_evidence",
          "llm_calls", "prompt_tokens", "output_tokens", "compute_seconds", "wall_seconds"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=detector.MODEL)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--data", default="messages.csv")
    parser.add_argument("--out", default="results.csv")
    args = parser.parse_args()
    detector.MODEL = args.model

    with open(args.data, newline="", encoding="utf-8") as f:
        messages = list(csv.DictReader(f))[:args.limit]

    done = set()
    if os.path.exists(args.out):
        with open(args.out, newline="", encoding="utf-8") as f:
            done = {row["id"] for row in csv.DictReader(f)}

    new_file = not os.path.exists(args.out)
    with open(args.out, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        for message in messages:
            if message["id"] in done:
                continue
            text = message["text"]
            vader_label, compound = detector.vader_score(text)

            started = time.perf_counter()
            signal, calls, responses = detector.llm_score(text)
            wall = time.perf_counter() - started

            # Ollama reports durations in nanoseconds; compute = prompt + output evaluation
            compute = sum((r.prompt_eval_duration or 0) + (r.eval_duration or 0)
                          for r in responses) / 1e9
            row = dict(message,
                       vader_label=vader_label, vader_compound=compound,
                       llm_sentiment=signal.sentiment if signal else "UNSCORED",
                       llm_anger=signal.anger if signal else "UNSCORED",
                       llm_churn=signal.churn_intent if signal else "UNSCORED",
                       llm_risk=signal.escalation_risk if signal else "UNSCORED",
                       llm_evidence=signal.evidence if signal else "",
                       llm_calls=calls,
                       prompt_tokens=responses[-1].prompt_eval_count,
                       output_tokens=responses[-1].eval_count,
                       compute_seconds=round(compute, 2),
                       wall_seconds=round(wall, 2))
            writer.writerow(row)
            f.flush()
            print(f"{message['id']}: VADER {vader_label} {compound:+.4f} | "
                  f"LLM {row['llm_sentiment']}/{row['llm_anger']}/churn={row['llm_churn']}/"
                  f"{row['llm_risk']} | {calls} call(s), {compute:.1f} s")


if __name__ == "__main__":
    main()
