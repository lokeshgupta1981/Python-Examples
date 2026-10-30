"""Categorizes bank transactions with merchant rules, a local LLM and a review queue.

Usage: python bankcat.py data/next.csv
"""

import re

import pandas as pd

CITIES = r"\b(LONDON|LEEDS|MANCHESTER|BRISTOL)\b"


def clean_description(text: str) -> str:
    """Uppercases the text, masks the card number and collapses spaces."""
    text = text.upper().strip()
    text = re.sub(r"\bCARD \d{4}\b", "CARD", text)
    return re.sub(r"\s+", " ", text)


def merchant_key(clean: str) -> str:
    """Reduces a cleaned description to the part that names the merchant."""
    key = re.sub(r"\bREF\b.*$", "", clean)          # payment references
    key = re.sub(r"\*.*$", "", key)                 # order ids after '*'
    key = re.sub(r"\.(COM|CO\.UK|IO)\b", "", key)   # web addresses
    key = re.sub(CITIES, "", key)
    key = re.sub(r"\b\w*\d\w*\b", "", key)          # anything with digits
    return re.sub(r"\s+", " ", key).strip()


def load_transactions(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"description": str})
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")
    df["amount"] = df["amount"].astype(float)
    df["clean"] = df["description"].map(clean_description)
    df["key"] = df["clean"].map(merchant_key)
    df["direction"] = df["amount"].map(lambda a: "in" if a > 0 else "out")
    return df


from collections import Counter, defaultdict


def learn_rules(labelled: pd.DataFrame, min_rows: int = 2) -> pd.DataFrame:
    """Keeps a (key, direction) pair when it repeats and always had one category."""
    seen = defaultdict(Counter)
    for row in labelled.itertuples():
        seen[(row.key, row.direction)][row.label] += 1
    rules = []
    for (key, direction), counts in seen.items():
        if len(counts) == 1 and sum(counts.values()) >= min_rows:
            rules.append((key, direction, next(iter(counts))))
    return pd.DataFrame(rules, columns=["pattern", "direction", "category"])


def apply_rules(df: pd.DataFrame, rules: pd.DataFrame) -> pd.Series:
    """Returns the rule category per row, or None; the longest pattern wins."""
    table = sorted(rules.itertuples(), key=lambda r: -len(r.pattern))

    def match(row):
        for rule in table:
            same_start = row.key == rule.pattern or row.key.startswith(rule.pattern + " ")
            if same_start and row.direction == rule.direction:
                return rule.category
        return None

    return df.apply(match, axis=1)


from typing import Literal

from pydantic import BaseModel, Field

Category = Literal[
    "Office supplies", "Software", "Travel", "Meals", "Utilities", "Rent",
    "Payroll", "Bank fees", "Taxes", "Sales income", "Refunds", "Other",
]


class Categorization(BaseModel):
    category: Category
    confidence: Literal["high", "medium", "low"]
    reason: str = Field(description="At most 12 words")


import json

from categories import CATEGORIES


def system_prompt() -> str:
    lines = [f"- {name}: {meaning}" for name, meaning in CATEGORIES.items()]
    return (
        "You categorize transactions from a small UK business bank account.\n"
        "Pick exactly one category from this list:\n" + "\n".join(lines) + "\n\n"
        "A negative amount is money out, a positive amount is money in.\n"
        "Confidence: high when the description clearly shows the category, "
        "medium when it is likely but not certain, low when you are guessing.\n"
        "If the description does not say enough, answer Other with low confidence.\n"
        "Reply with JSON only."
    )


def row_text(clean: str, amount: float) -> str:
    direction = "money in" if amount > 0 else "money out"
    return f"Description: {clean}\nAmount: {amount:.2f} GBP ({direction})"


def build_messages(clean: str, amount: float, examples: list[dict]) -> list[dict]:
    messages = [{"role": "system", "content": system_prompt()}]
    for ex in examples:
        answer = {"category": ex["category"], "confidence": "high",
                  "reason": ex["reason"]}
        messages.append({"role": "user", "content": row_text(ex["clean"], ex["amount"])})
        messages.append({"role": "assistant", "content": json.dumps(answer)})
    messages.append({"role": "user", "content": row_text(clean, amount)})
    return messages


EXAMPLE_REASONS = {
    "Office supplies": "order from an office supplies shop",
    "Meals": "card payment at a cafe",
    "Payroll": "salary reference on a transfer to a person",
    "Sales income": "customer pays one of our invoices",
    "Bank fees": "monthly fee charged by the bank",
    "Utilities": "direct debit to an electricity supplier",
}


def pick_examples(history: pd.DataFrame) -> list[dict]:
    """Takes the first history row for each category in EXAMPLE_REASONS."""
    examples = []
    for category, reason in EXAMPLE_REASONS.items():
        row = history[history["label"] == category].iloc[0]
        examples.append({"clean": row["clean"],
                         "amount": float(row["amount"]),
                         "category": category,
                         "reason": reason})
    return examples


import os
import time

from ollama import Client

MODEL = "qwen2.5:7b"
TIMEOUT = float(os.environ.get("OLLAMA_TIMEOUT", "300"))
client = Client(host="http://localhost:11434", timeout=TIMEOUT)


def classify(clean: str, amount: float, examples: list[dict]):
    """Returns the answer and the call's timing and token counts."""
    start = time.perf_counter()
    response = client.chat(
        model=MODEL,
        messages=build_messages(clean, amount, examples),
        format=Categorization.model_json_schema(),
        options={"temperature": 0, "num_predict": 80},
    )
    answer = Categorization.model_validate_json(response.message.content)
    return answer, stats(response, start)


from categories import CATEGORIES, MONEY_IN_ONLY, MONEY_OUT_ONLY


def check_answer(category: str, amount: float) -> list[str]:
    problems = []
    if category not in CATEGORIES:
        problems.append("unknown category")
    if amount < 0 and category in MONEY_IN_ONLY:
        problems.append(f"{category} on money out")
    if amount > 0 and category in MONEY_OUT_ONLY:
        problems.append(f"{category} on money in")
    return problems


def route(confidence: str, problems: list[str]) -> str:
    """Accepts only clean, high-confidence answers; a person reviews the rest."""
    return "accept" if confidence == "high" and not problems else "review"


from pydantic import ValidationError


def categorize_month(path: str, rules: pd.DataFrame, examples: list[dict]) -> None:
    """Writes categorized.csv (accepted rows) and review.csv (rows for a person)."""
    df = load_transactions(path)
    df["category"] = apply_rules(df, rules)
    df["confidence"], df["reason"], df["routed"] = "rule", "", "accept"

    for row in df[df["category"].isna()].itertuples():
        try:
            answer, _ = classify(row.clean, row.amount, examples)
        except ValidationError:
            df.loc[row.Index, ["confidence", "reason", "routed"]] = [
                "none", "invalid model reply", "review"]
            continue
        problems = check_answer(answer.category, row.amount)
        df.loc[row.Index, ["category", "confidence", "reason", "routed"]] = [
            answer.category, answer.confidence, answer.reason,
            route(answer.confidence, problems)]

    cols = ["id", "date", "description", "amount", "category", "confidence", "reason"]
    df.loc[df["routed"] == "accept", cols].to_csv("categorized.csv", index=False)
    review = df.loc[df["routed"] == "review", cols].assign(corrected_category="")
    review.to_csv("review.csv", index=False)


def stats(response, start: float) -> dict:
    """Timing and token counts of one model call."""
    return {"seconds": round(time.perf_counter() - start, 2),
            "prompt_tokens": response.prompt_eval_count,
            "output_tokens": response.eval_count}


def main() -> None:
    import sys
    from pathlib import Path

    history = load_transactions("data/history.csv")
    rules_file = Path("data/rules.csv")
    rules = pd.read_csv(rules_file) if rules_file.exists() else learn_rules(history)
    categorize_month(sys.argv[1], rules, pick_examples(history))


if __name__ == "__main__":
    main()
