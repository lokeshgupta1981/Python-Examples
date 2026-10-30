"""Step 8: compare the extracted fields and statuses with labels.json.

Run after `python extract.py clean` and `python extract.py photo`. Makes no model calls.
"""
import json
import re
import statistics
from difflib import SequenceMatcher
from pathlib import Path

from extract import validate
from policy import apply_policy, load_yaml
from receipt_schema import Receipt

AMOUNTS = ["amount_before_tax", "tax", "tip", "total"]
FIELDS = ["merchant", "date", "currency", "amount_before_tax", "tax", "tip", "total", "category"]
KEY_FIELDS = ["merchant", "date", "currency", "total", "category"]  # the fields the policy uses
NAMES = {"merchant": "Merchant", "date": "Date", "currency": "Currency",
         "amount_before_tax": "Amount before tax", "tax": "Tax", "tip": "Tip",
         "total": "Total", "category": "Category"}


def field_ok(field, got, want):
    if field in AMOUNTS:
        return got is not None and abs(got - want) <= 0.01
    if field == "merchant":
        return got is not None and SequenceMatcher(
            None, got.lower().strip(), want.lower().strip()).ratio() >= 0.85
    return got == want


def wrong_fields(receipt, label, fields=FIELDS):
    if receipt is None:
        return list(fields)
    return [f for f in fields if not field_ok(f, receipt.get(f), label[f])]


def regex_total(text):
    """The last number on the last line that contains TOTAL."""
    lines = [l for l in text.splitlines() if "total" in l.lower()]
    numbers = re.findall(r"\d+[.,]\d{2}", lines[-1]) if lines else []
    return float(numbers[-1].replace(",", ".")) if numbers else None


def relaxed_problems(receipt):
    """validate() without the rule that every amount must be present."""
    problems = validate(Receipt.model_validate(receipt))
    return [p for p in problems if p != "amount before tax, tax or tip missing"]


def main():
    labels = json.loads(Path("labels.json").read_text())
    policy, trip = load_yaml("policy.yaml"), load_yaml("trip.yaml")
    expected = {l["file"]: l["status"] for l in apply_policy(
        [{"file": f, "receipt": r, "problems": []} for f, r in labels.items()], policy, trip)}

    sets = {s: json.loads(Path(f"results_{s}.json").read_text()) for s in ("clean", "photo")}
    print(f"{'Field':<20}{'clean':>8}{'photo':>8}")
    for field in FIELDS + ["every field"]:
        row = []
        for results in sets.values():
            fields = FIELDS if field == "every field" else [field]
            row.append(sum(not wrong_fields(r["receipt"], labels[r["file"]], fields)
                           for r in results))
        print(f"{NAMES.get(field, 'Every field'):<20}{row[0]:>8}{row[1]:>8}")

    for name, results in sets.items():
        lines = apply_policy(results, policy, trip)
        by_file = {r["file"]: r for r in results}
        statuses = [l["status"] for l in lines]
        passed = [l for l in lines if l["status"] != "review"]
        print(f"\n== {name} images ({len(results)} receipts)")
        for status in ("approved", "flagged", "review"):
            print(f"{status:<10}{statuses.count(status)}")
        print("status as expected", sum(l["status"] == expected[l["file"]] for l in lines))
        wrong = [l["file"] for l in passed
                 if wrong_fields(by_file[l["file"]]["receipt"], labels[l["file"]])]
        print("approved or flagged with a wrong field", len(wrong), wrong)
        missed = [l["file"] for l in lines
                  if l["status"] == "approved" and expected[l["file"]] == "flagged"]
        print("approved although it should have been flagged", len(missed), missed)
        for l in lines:
            if l["status"] != expected[l["file"]] or l["file"] in wrong:
                print(f"  {l['file']}: {l['status']} (expected {expected[l['file']]}) "
                      f"{l['reason']}")

        texts = {f.stem: f.read_text() for f in Path("ocr", name).glob("*.txt")}
        regex_ok = sum(field_ok("total", regex_total(texts.get(f, "")), labels[f]["total"])
                       for f in by_file)
        print("regex total right", regex_ok)
        relaxed = [r for r in results if r["receipt"] and not relaxed_problems(r["receipt"])]
        relaxed_wrong = [r["file"] for r in relaxed
                         if wrong_fields(r["receipt"], labels[r["file"]], KEY_FIELDS)]
        print(f"relaxed rule passes {len(relaxed)}, with a wrong key field "
              f"{len(relaxed_wrong)} {relaxed_wrong}")
        print("median seconds per receipt", statistics.median(r["seconds"] for r in results))
        print("median model seconds", statistics.median(r["model_seconds"] for r in results))
        print("median prompt tokens", statistics.median(r["prompt_tokens"] for r in results),
              "output tokens", statistics.median(r["output_tokens"] for r in results))


if __name__ == "__main__":
    main()
