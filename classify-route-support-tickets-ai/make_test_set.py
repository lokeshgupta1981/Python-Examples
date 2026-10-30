"""Pick 10 tickets per category from tickets.jsonl into tickets-test.jsonl."""
import json
import random
from pathlib import Path

HERE = Path(__file__).parent
PER_CATEGORY = 10
SEED = 42  # fixed seed: every run picks the same 60 tickets

config = json.loads((HERE / "categories.json").read_text())
tickets = [json.loads(line) for line in (HERE / "tickets.jsonl").read_text().splitlines()]

rng = random.Random(SEED)
test = []
for category in (c["name"] for c in config["categories"]):
    pool = sorted((t for t in tickets if t["category"] == category), key=lambda t: t["id"])
    test += rng.sample(pool, PER_CATEGORY)
test.sort(key=lambda t: t["id"])

(HERE / "tickets-test.jsonl").write_text("".join(json.dumps(t) + "\n" for t in test))
print(f"wrote {len(test)} tickets to tickets-test.jsonl")
