"""Measures the saved results. Makes no model call.

Usage: python report.py [results.csv]
"""
import csv
import statistics
import sys
import time
from collections import defaultdict

from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             precision_score, recall_score)

from detector import CustomerSignal, should_alert, vader, vader_alert

LABELS = ["negative", "neutral", "positive"]
TWO_STAGE_SKIP = 0.5  # VADER compound at or above this skips the LLM as clearly positive

path = sys.argv[1] if len(sys.argv) > 1 else "results.csv"
with open(path, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))


def signal_of(row) -> CustomerSignal | None:
    """Rebuilds the validated LLM answer from a saved row (None when unscored)."""
    if row["llm_sentiment"] == "UNSCORED":
        return None
    return CustomerSignal(sentiment=row["llm_sentiment"], anger=row["llm_anger"],
                          churn_intent=row["llm_churn"] == "True",
                          escalation_risk=row["llm_risk"], evidence=row["llm_evidence"])


# --- the alert rules, applied to saved rows -----------------------------------

def vader_rule(row, earlier_negative):
    compound = float(row["vader_compound"])
    alert, reason = vader_alert(compound, earlier_negative)
    return alert, reason, row["vader_label"] == "negative"


def llm_rule(row, earlier_negative):
    signal = signal_of(row)
    compound = float(row["vader_compound"])
    alert, reason = should_alert(signal, compound, earlier_negative)
    label = signal.sentiment if signal else row["vader_label"]
    negative = label == "negative"
    return alert, reason, negative


def llm_strong_anger_rule(row, earlier_negative):
    """Tuned rule: the section 5 rule, plus an alert when the anger is strong."""
    alert, reason, negative = llm_rule(row, earlier_negative)
    if not alert and row["llm_anger"] == "strong":
        return True, "strong anger", negative
    return alert, reason, negative


def llm_medium_rule(row, earlier_negative):
    """Tuned rule: the section 5 rule, plus an alert when the risk is medium."""
    alert, reason, negative = llm_rule(row, earlier_negative)
    if not alert and row["llm_risk"] == "medium":
        return True, "medium risk", negative
    return alert, reason, negative


def skipped(row) -> bool:
    return float(row["vader_compound"]) >= TWO_STAGE_SKIP


def two_stage_rule(row, earlier_negative):
    """VADER first; clearly positive messages never reach the LLM."""
    if skipped(row):
        return vader_rule(row, earlier_negative)
    return llm_rule(row, earlier_negative)


def alerts(rule):
    """Applies a rule in message order and tracks earlier negatives per customer."""
    negative_before = defaultdict(bool)
    decisions = []
    for row in rows:
        alert, reason, negative = rule(row, negative_before[row["customer"]])
        decisions.append((alert, reason))
        negative_before[row["customer"]] |= negative
    return decisions


# --- sentiment labels per approach -------------------------------------------

def llm_label(row):
    return row["llm_sentiment"] if row["llm_sentiment"] != "UNSCORED" else row["vader_label"]


expected = [row["sentiment"] for row in rows]
escalate = [row["should_escalate"] == "yes" for row in rows]

approaches = {
    "VADER": ([row["vader_label"] for row in rows], vader_rule),
    "LLM, section 5 rule": ([llm_label(row) for row in rows], llm_rule),
    "Two-stage": ([row["vader_label"] if skipped(row) else llm_label(row) for row in rows],
                  two_stage_rule),
    "LLM + strong anger": ([llm_label(row) for row in rows], llm_strong_anger_rule),
    "LLM + medium risk": ([llm_label(row) for row in rows], llm_medium_rule),
}

summary = {}
for name, (labels, rule) in approaches.items():
    fired = [alert for alert, _ in alerts(rule)]
    print(f"===== {name} =====")
    print(classification_report(expected, labels, labels=LABELS, zero_division=0))
    print("Alert confusion matrix (rows = should_escalate no/yes, columns = alert)")
    print(confusion_matrix(escalate, fired, labels=[False, True]))
    missed = [row["id"] for row, e, a in zip(rows, escalate, fired) if e and not a]
    false_alarms = [row["id"] for row, e, a in zip(rows, escalate, fired) if a and not e]
    print("Missed escalations:", missed)
    print("False alarms:", false_alarms)
    alert_precision = precision_score(escalate, fired, zero_division=0)
    alert_recall = recall_score(escalate, fired, zero_division=0)
    negative_recall = recall_score(expected, labels, labels=["negative"],
                                   average=None, zero_division=0)[0]
    summary[name] = (accuracy_score(expected, labels), negative_recall,
                     sum(a and e for a, e in zip(fired, escalate)), sum(escalate),
                     sum(fired), alert_precision, alert_recall)
    print()

print("Approach            | Sentiment acc | Negative recall | Alert recall | Alert precision")
for name, (acc, neg, hits, total, fired_count, _, _) in summary.items():
    print(f"{name:19} | {acc:13.0%} | {neg:15.0%} | {hits:2} of {total:2}     | "
          f"{hits} of {fired_count}")
print(f"Two-stage: LLM ran on {sum(not skipped(row) for row in rows)} of {len(rows)} messages")
print()

# --- tricky cases ------------------------------------------------------------------

vader_fired = [a for a, _ in alerts(vader_rule)]
llm_fired = [a for a, _ in alerts(llm_rule)]
print("Trap            | Messages | VADER sentiment | LLM sentiment | VADER alert | LLM alert")
cases = sorted({row["case"] for row in rows if row["case"]})
for case in cases:
    idx = [i for i, row in enumerate(rows) if row["case"] == case]
    print(f"{case:15} | {len(idx):8} | "
          f"{sum(rows[i]['vader_label'] == expected[i] for i in idx):15} | "
          f"{sum(llm_label(rows[i]) == expected[i] for i in idx):13} | "
          f"{sum(vader_fired[i] == escalate[i] for i in idx):11} | "
          f"{sum(llm_fired[i] == escalate[i] for i in idx):9}")
print()

# --- speed and tokens ----------------------------------------------------------------

compute = [float(row["compute_seconds"]) for row in rows]
median = statistics.median(compute)
print(f"LLM compute per message: median {median:.1f} s, min {min(compute):.1f} s, "
      f"max {max(compute):.1f} s, about {86400 / median:,.0f} messages a day")
print(f"Tokens: median prompt {statistics.median(int(r['prompt_tokens']) for r in rows):.0f}, "
      f"median output {statistics.median(int(r['output_tokens']) for r in rows):.0f}, "
      f"longest output {max(int(r['output_tokens']) for r in rows)}")
print(f"Answers valid on the first attempt: {sum(r['llm_calls'] == '1' for r in rows)} "
      f"of {len(rows)}")

texts = [row["text"] for row in rows]
repeats = 200
started = time.perf_counter()
for _ in range(repeats):
    for text in texts:
        vader.polarity_scores(text)
elapsed = time.perf_counter() - started
print(f"VADER: about {repeats * len(texts) / elapsed:,.0f} messages per second")
