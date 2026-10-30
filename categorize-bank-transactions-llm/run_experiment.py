"""Compares rules only, LLM only, rules + LLM and batched rules + LLM on September.

Usage:
    python run_experiment.py                      # full run, 60 + 2 model calls
    python run_experiment.py --model qwen2.5:3b   # another local model
    python run_experiment.py --model qwen2.5:3b --limit 6   # smoke test, 7 calls

Writes data/rules.csv, data/llm_answers.csv, data/predictions.csv (rules + LLM)
and data/review.csv (the rows of rules + LLM that need a person).
"""

import argparse

import pandas as pd
from pydantic import BaseModel, ValidationError

import bankcat
from bankcat import (Category, apply_rules, check_answer, classify, learn_rules,
                     load_transactions, pick_examples, route, row_text, system_prompt)


class BatchAnswer(BaseModel):
    id: int
    category: Category
    confidence: str
    reason: str


class BatchReply(BaseModel):
    answers: list[BatchAnswer]


def classify_batch(rows: pd.DataFrame, examples: list[dict]) -> dict[int, BatchAnswer]:
    """Sends several rows in one call; returns the answers by row id."""
    shown = "\n\n".join(f"{row_text(ex['clean'], ex['amount'])}\nAnswer: {ex['category']}"
                        for ex in examples)
    batch = "\n\n".join(f"Id: {row.id}\n{row_text(row.clean, row.amount)}"
                        for row in rows.itertuples())
    messages = [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": "Solved examples:\n\n" + shown + "\n\n"
         "Categorize each of these transactions and answer every id:\n\n" + batch},
    ]
    response = bankcat.client.chat(
        model=bankcat.MODEL, messages=messages,
        format=BatchReply.model_json_schema(),
        options={"temperature": 0, "num_predict": 60 * len(rows)},
    )
    reply = BatchReply.model_validate_json(response.message.content)
    return {a.id: a for a in reply.answers}


def one_row_answers(test: pd.DataFrame, examples: list[dict]) -> pd.DataFrame:
    """One model call per row, for every row in test."""
    out = []
    for row in test.itertuples():
        try:
            answer, info = classify(row.clean, row.amount, examples)
            out.append({"id": row.id, "category": answer.category,
                        "confidence": answer.confidence, "reason": answer.reason, **info})
        except ValidationError:
            out.append({"id": row.id, "category": None, "confidence": "none",
                        "reason": "invalid model reply"})
        print(f"  {row.id:>3} {row.clean[:40]:<40} {out[-1]['category']} "
              f"({out[-1]['confidence']})", flush=True)
    return pd.DataFrame(out)


def finish(test: pd.DataFrame, final: pd.Series, confidence: pd.Series) -> pd.DataFrame:
    """Adds the final category and the routing decision to a copy of test."""
    result = test.copy()
    result["final"] = final
    result["confidence"] = confidence
    result["routed"] = [
        "accept" if conf == "rule" else
        ("review" if pd.isna(cat) else route(conf, check_answer(cat, amount)))
        for cat, conf, amount in zip(result["final"], result["confidence"], result["amount"])
    ]
    return result


def summarize(name: str, test: pd.DataFrame, calls: int) -> dict:
    decided = test["routed"] == "accept"        # accepted without a person
    correct = test["final"] == test["label"]    # matches the label
    auto = int(decided.sum())
    auto_right = int((decided & correct).sum())
    accuracy = round(100 * auto_right / auto, 1) if auto else 0.0
    review = len(test) - auto
    return {"setup": name,
            "decided": f"{auto} ({100 * auto / len(test):.1f}%)",
            "accuracy on decided": f"{accuracy}%",
            "sent to review": f"{review} ({100 * review / len(test):.1f}%)",
            "wrong accepted": auto - auto_right,
            "model calls": calls}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=bankcat.MODEL)
    parser.add_argument("--limit", type=int, help="smoke test: only the first N rows")
    parser.add_argument("--batch-size", type=int, default=20)
    args = parser.parse_args()
    bankcat.MODEL = args.model

    history = load_transactions("data/history.csv")
    test = load_transactions("data/test.csv")
    rules = learn_rules(history)
    rules.to_csv("data/rules.csv", index=False)
    examples = pick_examples(history)

    test["rule"] = apply_rules(test, rules)
    no_rule = test[test["rule"].isna()]
    print(f"{len(rules)} rules, {test['rule'].notna().sum()} of {len(test)} rows matched")

    if args.limit:   # smoke test: only the first N rows of the month
        test = test.head(args.limit).copy()
        no_rule = test[test["rule"].isna()]

    print(f"LLM only, 1 row per call, model {bankcat.MODEL}:")
    answers = one_row_answers(test, examples)
    answers.to_csv("data/llm_answers.csv", index=False)
    by_id = answers.set_index("id")
    llm_cat = test["id"].map(by_id["category"])
    llm_conf = test["id"].map(by_id["confidence"])

    has_rule = test["rule"].notna()
    setups = {
        "Rules only": finish(test, test["rule"], has_rule.map({True: "rule", False: "none"})),
        "LLM only, 1 row per call": finish(test, llm_cat, llm_conf),
        "Rules + LLM": finish(test, test["rule"].fillna(llm_cat),
                              llm_conf.where(~has_rule, "rule")),
    }
    calls = {"Rules only": 0, "LLM only, 1 row per call": len(test),
             "Rules + LLM": len(no_rule)}

    batched = {}
    for start in range(0, len(no_rule), args.batch_size):
        chunk = no_rule.iloc[start:start + args.batch_size]
        try:
            batched.update(classify_batch(chunk, examples))
        except ValidationError:
            print("  a batch reply did not match the schema")
    got = test["id"].isin(batched.keys()) & ~has_rule
    print(f"Batched: answers for {got.sum()} of {len(no_rule)} rows, "
          f"ids not sent: {sorted(set(batched) - set(no_rule['id']))}")
    batch_cat = test["id"].map(lambda i: batched[i].category if i in batched else None)
    batch_conf = test["id"].map(lambda i: batched[i].confidence if i in batched else "none")
    name = f"Rules + LLM, {args.batch_size} rows per call"
    setups[name] = finish(test, test["rule"].fillna(batch_cat.where(~has_rule)),
                          batch_conf.where(~has_rule, "rule"))
    calls[name] = -(-len(no_rule) // args.batch_size)

    table = pd.DataFrame([summarize(n, df, calls[n]) for n, df in setups.items()])
    print(table.to_string(index=False))

    llm = setups["LLM only, 1 row per call"]
    print(f"LLM only matched the label on {(llm['final'] == llm['label']).sum()} of {len(llm)}")
    for level in ("high", "medium", "low"):
        rows = llm[llm["confidence"] == level]
        print(f"  {level}: {(rows['final'] == rows['label']).sum()} of {len(rows)} right")

    best = setups["Rules + LLM"]
    best["source"] = has_rule.map({True: "rule", False: "llm"})
    best[["id", "final", "source", "confidence", "routed"]].to_csv(
        "data/predictions.csv", index=False)
    review = best[best["routed"] == "review"].merge(answers[["id", "reason"]], on="id")
    review = review.rename(columns={"final": "suggested"})
    review[["id", "description", "amount", "suggested", "confidence", "reason"]].assign(
        corrected_category="").to_csv("data/review.csv", index=False)
    print(f"{len(review)} rows written to data/review.csv")


if __name__ == "__main__":
    main()
