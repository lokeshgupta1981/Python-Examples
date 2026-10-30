"""Run the batched pipeline and the single prompt, then score both.

Usage:
    python generate_reviews.py
    python run.py                 # qwen2.5:7b, as in the article
    MODEL=qwen2.5:3b python run.py
"""
import json
import os
import sys

import pandas as pd

import summarize as s

SKU = "TG-HL300"
s.MODEL = os.environ.get("MODEL", s.MODEL)

# --- record Ollama's statistics for every model call ------------------------

CALLS = []
_call_model = s.call_model

def recorded_call_model(prompt, schema, num_predict):
    result, response = _call_model(prompt, schema, num_predict)
    CALLS.append({"step": STEP, "prompt_tokens": response.prompt_eval_count,
                  "output_tokens": response.eval_count,
                  "seconds": response.total_duration / 1e9})
    return result, response

s.call_model = recorded_call_model
STEP = ""

# --- scoring: map a reported aspect name to a planted aspect ----------------
# Written before the run. The first rule whose keyword appears in the name
# (with the same polarity) decides; a name no rule matches is "not planted".

RULES = [
    ("battery life", ["battery", "runtime"]),
    ("brightness", ["bright", "light", "beam", "flood"]),
    ("comfort", ["comfort", "fit", "weight", "headband"]),
    ("charging port", ["charg", "port", "water"]),
    ("mode button", ["button", "mode"]),
    ("strap breaks", ["strap", "durab"]),
]

def planted_name(name, polarity, truth):
    name = name.lower()
    for aspect, keywords in RULES:
        if (aspect, polarity) in truth and any(k in name for k in keywords):
            return aspect
    return None

def score(reported, truth):
    """reported: list of (name, polarity, count). Returns counts per planted aspect."""
    found = {}
    for name, polarity, count in reported:
        aspect = planted_name(name, polarity, truth)
        if aspect is not None:
            found.setdefault((aspect, polarity), count)  # the first match counts
    rows = {key: found.get(key, 0) for key in truth}
    missed = sum(1 for key in truth if key not in found)
    error = sum(abs(rows[key] - truth[key]) for key in truth) / len(truth)
    return rows, missed, error

def model_stats(step):
    calls = [c for c in CALLS if c["step"] == step]
    return (len(calls), sum(c["seconds"] for c in calls),
            sum(c["output_tokens"] for c in calls), max(c["prompt_tokens"] for c in calls))


def main():
    global STEP
    print("model:", s.MODEL)
    reviews = s.load_reviews("reviews.csv", SKU)
    masked = sum("<EMAIL>" in r["text"] or "<PHONE>" in r["text"] for r in reviews)
    print(f"{len(reviews)} reviews, {masked} with masked personal data")

    planted = pd.read_csv("planted_aspects.csv")
    truth = (planted.groupby(["aspect", "polarity"])["review_id"].nunique().to_dict())
    print(f"{len(planted)} planted sentences, true counts: {truth}")

    batches = s.make_batches(reviews)
    estimates = [sum(s.estimate_tokens(r["text"]) for r in b) for b in batches]
    print(f"{len(batches)} batches, estimated tokens {estimates}")

    # --- batched pipeline ---------------------------------------------------
    STEP = "pipeline"
    points = []
    for i, batch in enumerate(batches, 1):
        found = s.extract_points(batch)
        print(f"batch {i}: {len(found)} points, prompt tokens {CALLS[-1]['prompt_tokens']}")
        points += found
    kept, rejected = s.check_quotes(points, reviews)
    print(f"{len(points)} points, {len(rejected)} rejected by the quote check")
    for p in rejected:
        print("  rejected:", p)

    mapping, missing = s.merge_aspects(kept)
    print(f"{len(mapping)} labels, {len(set(mapping.values()))} aspects, missing: {missing}")
    table = s.count_points(kept, mapping, len(reviews))
    print(table.to_string(index=False))

    overview, problems = s.summarize(s.write_summary, table, len(reviews))
    print("summary problems:", problems)
    card = s.summary_card("headlamp", overview, table, len(reviews))
    with open("summary_headlamp.md", "w", encoding="utf-8") as f:
        f.write(card)
    print(card)

    pipeline = [(r.aspect, r.polarity, r.reviews) for r in table.itertuples()]
    results = {"pipeline": score(pipeline, truth) + model_stats("pipeline")}

    # --- single prompt, file order and reversed ------------------------------
    for label, order in (("single, file order", reviews), ("single, reversed", reviews[::-1])):
        STEP = label
        answer = s.single_prompt(order)
        claims = [(c["aspect"], c["polarity"], c["reviews"]) for c in answer["claims"]]
        print(f"\n{label}: {answer['overview']}")
        for c in answer["claims"]:
            ok = s.normalize(c["quote"]) in " ".join(s.normalize(r["text"]) for r in reviews)
            print(f"  {c['polarity']}: {c['aspect']}, {c['reviews']} reviews, quote found: {ok}")
        results[label] = score(claims, truth) + model_stats(label)

    # --- report ------------------------------------------------------------
    print("\napproach | calls | model time | output tokens | max prompt tokens"
          " | planted not reported | mean count error")
    for label, (rows, missed, error, calls, secs, out, prompt) in results.items():
        print(f"{label} | {calls} | {secs:.0f} s | {out} | {prompt} | {missed} | {error:.1f}")
    print("\nplanted aspect | true | " + " | ".join(results))
    for key, true in truth.items():
        print(f"{key[0]} ({key[1]}) | {true} | "
              + " | ".join(str(r[0][key]) for r in results.values()))
    with open("calls.json", "w", encoding="utf-8") as f:
        json.dump(CALLS, f, indent=1)


if __name__ == "__main__":
    sys.exit(main())
