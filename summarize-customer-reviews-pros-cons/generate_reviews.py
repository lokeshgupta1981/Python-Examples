"""Write reviews.csv and planted_aspects.csv for the example.

The script plants sentences about known aspects into a known number of
reviews, so we know the true counts (for example, 24 reviews praise the
battery life). It also adds reviews that say nothing useful, filler
sentences, one empty review, one duplicate, a fake email address and a
fake phone number, so the cleaning step has something to do.

The output is deterministic (fixed random seed).
"""
import csv
import random

SKU = "TG-HL300"   # the TrailGear headlamp
REVIEWS = 60       # distinct, non-empty reviews

# aspect, polarity, number of reviews, sentences to pick from
PLANTED = [
    ("battery life", "pro", 24, [
        "One charge got me through a whole weekend trip.",
        "The battery lasts for days of evening walks.",
        "Battery life is excellent, I charge it once a week.",
        "It ran all night on the low setting without dying.",
    ]),
    ("brightness", "pro", 18, [
        "The floodlight mode lights the whole campsite.",
        "Very bright, I can see the trail far ahead.",
        "The beam is strong enough for night running.",
    ]),
    ("comfort", "pro", 12, [
        "The headband is soft and doesn't press on my forehead.",
        "So light I forget I'm wearing it.",
        "Comfortable even after hours on my head.",
    ]),
    ("charging port", "con", 7, [
        "Water got in because the charging port cover popped open.",
        "The rubber flap over the USB port keeps coming loose.",
        "The charging port is loose and the cable falls out.",
    ]),
    ("mode button", "con", 6, [
        "The button is confusing, I keep ending up in strobe mode.",
        "You have to click through every mode to turn it off.",
        "The mode button is hard to press with gloves on.",
    ]),
    ("strap breaks", "con", 5, [
        "The elastic strap snapped after a month.",
        "The strap stretched out and now it slides down.",
        "The buckle on the strap cracked on the second trip.",
    ]),
    ("battery life", "con", 4, [
        "The battery died after two hours on high.",
        "On the brightest setting the battery drains fast.",
    ]),
]

# reviews that mention battery life (pro) twice, so two planted sentences
# describe one review; the count of distinct reviews stays 24
DOUBLE_BATTERY_PRO = 2

FILLER = [
    "Not sure yet if I'd recommend it.",
    "Arrived two days after I ordered it.",
    "Bought it for a trip next month.",
    "The box was a bit dented.",
    "Got this as a gift for my brother.",
]

USELESS = [
    "It's a headlamp.",
    "Ordered it on a Tuesday.",
    "Haven't really used it yet, will update later.",
    "My second order from this shop.",
    "Bought it for a trip next month.",
    "Okay.",
    "Arrived on time, packaging was fine.",
    "Gift for my dad, he hasn't opened it yet.",
]


def main(seed=42):
    rnd = random.Random(seed)
    ids = [f"R{i:02d}" for i in range(1, REVIEWS + 1)]
    sentences = {rid: [] for rid in ids}
    planted = []

    useful = ids[:]
    rnd.shuffle(useful)
    useless = set(useful[-len(USELESS):])        # these get no planted aspect
    useful = [rid for rid in useful if rid not in useless]

    for aspect, polarity, count, variants in PLANTED:
        chosen = rnd.sample(useful, count)
        for n, rid in enumerate(chosen):
            text = variants[n % len(variants)]
            sentences[rid].append(text)
            planted.append((rid, aspect, polarity, text))
        if aspect == "battery life" and polarity == "pro":
            for rid in chosen[:DOUBLE_BATTERY_PRO]:
                text = "I barely think about charging it."
                sentences[rid].append(text)
                planted.append((rid, aspect, polarity, text))

    # "Not sure yet if I'd recommend it." in exactly six reviews
    for rid in rnd.sample(sorted(set(ids) - useless), 6):
        sentences[rid].append(FILLER[0])
    for rid in rnd.sample(sorted(set(ids) - useless), 10):
        sentences[rid].append(rnd.choice(FILLER[1:]))
    for rid, text in zip(sorted(useless), USELESS):
        sentences[rid].append(text)

    # a neutral opening sentence, so no two reviews have the same text
    openers = [f"Used it {when} for {what}." for when in
               ("last week", "for a month", "all summer", "twice now", "every day")
               for what in ("camping", "night runs", "fishing", "car repairs", "hiking",
                            "dog walks", "reading in the tent", "a power cut", "caving",
                            "trail running", "work in the attic", "a festival")]
    rnd.shuffle(openers)
    for rid, opener in zip(sorted(set(ids) - useless), openers):
        sentences[rid].insert(0, opener)

    # personal data that the cleaning step must mask (fake values)
    with_email, with_phone = rnd.sample(sorted(set(ids) - useless), 2)
    sentences[with_email].append("Questions? Write to sam.rivera@example.com.")
    sentences[with_phone].append("The seller called me back at 555-201-4477.")

    rows = []
    for rid in ids:
        parts = sentences[rid]
        parts[1:] = rnd.sample(parts[1:], len(parts) - 1)
        polarities = [p for r, _, p, _ in planted if r == rid]
        pros, cons = polarities.count("pro"), polarities.count("con")
        rating = 3 if pros == cons else (5 if pros > cons else 2)
        rows.append({"review_id": rid, "sku": SKU, "rating": rating, "text": " ".join(parts)})

    rows.append({**rows[4], "review_id": "R61"})                       # duplicate text
    rows.append({"review_id": "R62", "sku": SKU, "rating": 4, "text": ""})  # empty

    with open("reviews.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["review_id", "sku", "rating", "text"])
        writer.writeheader()
        writer.writerows(rows)
    with open("planted_aspects.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["review_id", "aspect", "polarity", "sentence"])
        writer.writerows(planted)
    print(f"wrote {len(rows)} rows to reviews.csv and {len(planted)} planted sentences "
          "to planted_aspects.csv")


if __name__ == "__main__":
    main()
