"""A short check that every model step runs: one batch of 5 reviews.

With qwen2.5:3b, a batch of 10 reviews can exceed num_predict=1024 and raise a
ValidationError for cut-off JSON, so the smoke test uses smaller batches.

Usage: MODEL=qwen2.5:3b python smoke_test.py   (after python generate_reviews.py)
The article's numbers come from run.py with qwen2.5:7b on all 60 reviews.
"""
import os
import time

import summarize as s

s.MODEL = os.environ.get("MODEL", s.MODEL)
print("model:", s.MODEL)
reviews = s.load_reviews("reviews.csv", "TG-HL300")
batch = s.make_batches(reviews, max_reviews=5)[0]

start = time.time()
points = s.extract_points(batch)
kept, rejected = s.check_quotes(points, batch)
print(f"extract: {len(points)} points, {len(rejected)} rejected by the quote check")
mapping, missing = s.merge_aspects(kept)
print(f"merge: {len(mapping)} labels into {len(set(mapping.values()))} aspects, missing {missing}")
table = s.count_points(kept, mapping, len(batch))
overview, problems = s.summarize(s.write_summary, table, len(batch))
print(s.summary_card("headlamp", overview, table, len(batch)))
print("summary problems:", problems)
answer = s.single_prompt(batch)
print(f"single prompt: {len(answer['claims'])} claims")
print(f"done in {time.time() - start:.0f} s")
