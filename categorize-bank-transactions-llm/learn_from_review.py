"""Plays the reviewer for September, learns rules from the finished month, and
shows every new rule with the rows it came from before anything is saved.

Run it after run_experiment.py. It writes data/rules_after_review.csv and never
changes data/rules.csv; copy the file over it once a person has checked the rules.
"""

import pandas as pd

from bankcat import apply_rules, learn_rules, load_transactions


def play_reviewer(review: pd.DataFrame) -> pd.DataFrame:
    """Fills the empty corrected_category cells from the September labels."""
    labels = load_transactions("data/test.csv").set_index("id")["label"]
    review = review.copy()
    review["corrected_category"] = review["id"].map(labels)
    return review


def finished_month(predictions: pd.DataFrame, review: pd.DataFrame) -> pd.DataFrame:
    """September with its final category: rule, accepted model answer or review."""
    month = load_transactions("data/test.csv").drop(columns="label")
    final = predictions.set_index("id")["final"]
    source = predictions.set_index("id")["source"].map({"rule": "rule", "llm": "model"})
    corrected = review.set_index("id")["corrected_category"]
    month["label"] = month["id"].map(final)
    month["source"] = month["id"].map(source)
    reviewed = month["id"].isin(corrected.index)
    month.loc[reviewed, "label"] = month["id"].map(corrected)
    month.loc[reviewed, "source"] = "review"
    return month


def show_new_rules(added: pd.DataFrame, month: pd.DataFrame) -> None:
    """Prints each new rule with the rows it came from, for a person to check."""
    for rule in added.itertuples():
        print(f"{rule.pattern} ({rule.direction}) -> {rule.category}")
        rows = month[(month["key"] == rule.pattern)
                     & (month["direction"] == rule.direction)]
        for row in rows.itertuples():
            print(f"    row {row.id}: {row.description} [{row.source}]")


def main() -> None:
    predictions = pd.read_csv("data/predictions.csv")
    review = play_reviewer(pd.read_csv("data/review.csv"))
    old_rules = pd.read_csv("data/rules.csv")

    ONE_OFF = {"Refunds", "Other"}   # never turned into merchant rules

    september = finished_month(predictions, review)
    repeatable = september[~september["label"].isin(ONE_OFF)]
    month_rules = learn_rules(repeatable, min_rows=1)
    new_rules = (pd.concat([old_rules, month_rules])
                 .drop_duplicates(subset=["pattern", "direction"], keep="first"))

    added = new_rules.iloc[len(old_rules):]
    sources = september.set_index("id")["source"]
    print(f"{len(added)} new rules; sources of the September rows: "
          f"{sources.value_counts().to_dict()}")
    show_new_rules(added, september)
    new_rules.to_csv("data/rules_after_review.csv", index=False)

    october = load_transactions("data/next.csv")
    for name, rules in (("old rules", old_rules), ("old + new rules", new_rules)):
        covered = int(apply_rules(october, rules).notna().sum())
        print(f"October with {name}: {covered} of {len(october)} rows "
              f"({100 * covered / len(october):.1f}%)")


if __name__ == "__main__":
    main()
