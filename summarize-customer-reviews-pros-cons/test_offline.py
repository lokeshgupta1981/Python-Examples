"""Checks for every step that does not need a model. Run: python test_offline.py"""
import pandas as pd

import generate_reviews
import summarize as s

generate_reviews.main()
reviews = s.load_reviews("reviews.csv", "TG-HL300")
assert len(pd.read_csv("reviews.csv")) == 62
assert len(reviews) == 60, len(reviews)
texts = " ".join(r["text"] for r in reviews)
assert "<EMAIL>" in texts and "<PHONE>" in texts and "@example.com" not in texts

batches = s.make_batches(reviews)
assert [len(b) for b in batches] == [10] * 6
print("batch estimates:", [sum(s.estimate_tokens(r["text"]) for r in b) for b in batches])

r1 = reviews[0]
quote = r1["text"].split(".")[0].upper() + "  ."  # case, spacing and end punctuation
points = [
    {"review_id": r1["review_id"], "aspect": "X", "polarity": "pro", "quote": quote},
    {"review_id": r1["review_id"], "aspect": "X", "polarity": "pro", "quote": "not in the review"},
    {"review_id": "R99", "aspect": "X", "polarity": "pro", "quote": quote},
]
kept, rejected = s.check_quotes(points, reviews)
assert len(kept) == 1 and len(rejected) == 2

points = ([{"review_id": f"R{i}", "aspect": "Battery Life ", "polarity": "pro", "quote": "a"} for i in range(5)]
          + [{"review_id": "R0", "aspect": "long battery", "polarity": "pro", "quote": "bb"}]  # same review
          + [{"review_id": f"R{i}", "aspect": "strap", "polarity": "con", "quote": "c"} for i in range(2)])
mapping = {"battery life": "battery", "long battery": "battery", "strap": "strap"}
table = s.count_points(points, mapping, 60)
assert table.to_dict("records") == [
    {"aspect": "battery", "polarity": "pro", "reviews": 5, "quote": "a", "share": 8}], table

assert s.check_summary("Of 60 customers, 5 (8%) praise the battery.", table, 60) == []
problems = s.check_summary('Most of the 12 buyers say "great".', table, 60)
assert len(problems) == 3, problems

answers = iter(["Most buyers love it.", "Some buyers like the battery."])
overview, problems = s.summarize(lambda t, n, feedback="": next(answers), table, 60)
assert overview == "Some buyers like the battery." and problems == []
print(s.summary_card("headlamp", overview, table, 60))
print("all offline checks passed")
