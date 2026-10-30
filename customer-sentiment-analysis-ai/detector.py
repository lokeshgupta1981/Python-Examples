"""Unhappy customer detector for OrderDesk support messages.

VADER gives a quick mood score, a local LLM in Ollama describes the customer
in a fixed JSON shape, and plain Python decides whether to alert a team lead.

Usage: python detector.py "Third time I'm writing about this. Fine, I'll just cancel."
"""
import sys
from typing import Literal

import ollama
from pydantic import BaseModel, ValidationError
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- Section 3: score messages with VADER -------------------------------------

vader = SentimentIntensityAnalyzer()


def vader_score(text: str) -> tuple[str, float]:
    compound = vader.polarity_scores(text)["compound"]  # from -1 to 1
    if compound >= 0.05:  # thresholds from the README
        return "positive", compound
    if compound <= -0.05:
        return "negative", compound
    return "neutral", compound


# --- Section 4.1: the LLM output schema ------------------------------------------

class CustomerSignal(BaseModel):
    sentiment: Literal["negative", "neutral", "positive"]
    anger: Literal["none", "mild", "strong"]
    churn_intent: bool
    escalation_risk: Literal["low", "medium", "high"]
    evidence: str


# --- Section 4.2: ask the local LLM ------------------------------------------------

MODEL = "qwen2.5:7b"
client = ollama.Client(timeout=600)  # a CPU-only model can take a while

SYSTEM_PROMPT = """\
You read customer messages sent to OrderDesk, an online office-supplies store.
Describe the customer, not the topic. Words such as 'error', 'crash' or 'kill the process'
in a technical report are not negative by themselves.

sentiment: the customer's tone. negative = displeasure, frustration or sarcasm.
  neutral = a question or a calm, factual request, even about a problem.
  positive = thanks, praise or satisfaction.
anger: none, mild or strong.
churn_intent: true only if the customer says they will cancel, close the account,
  stop ordering or move to another supplier, or that they are considering it.
escalation_risk: how urgently a team lead should read this message.
  high = a legal or formal claim, a payment dispute, churn intent, a repeated contact
  about an unresolved problem, or a problem that stops the customer's business.
  medium = a real problem that makes the customer clearly unhappy.
  low = questions, praise, and small annoyances.
evidence: copy the few words from the message that best support your answer, exactly.

Reply with JSON only."""


def ask_model(messages: list[dict]) -> ollama.ChatResponse:
    return client.chat(
        model=MODEL,
        messages=messages,
        format=CustomerSignal.model_json_schema(),  # the answer must match this schema
        options={"temperature": 0, "num_predict": 512},  # caps a runaway reply
        think=False)


# --- Section 4.3: validate the LLM output ----------------------------------------

def evidence_found(signal: CustomerSignal, text: str) -> bool:
    quote = " ".join(signal.evidence.lower().split())
    return bool(quote) and quote in " ".join(text.lower().split())


def llm_score(text: str
              ) -> tuple[CustomerSignal | None, int, list[ollama.ChatResponse]]:
    """Returns the validated signal (or None), the number of calls, and the responses."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}]
    responses = []
    for attempt in (1, 2):
        response = ask_model(messages)
        responses.append(response)
        try:
            signal = CustomerSignal.model_validate_json(response.message.content)
            if evidence_found(signal, text):
                return signal, attempt, responses
            problem = "The evidence is not an exact quote from the message."
        except ValidationError as error:
            problem = f"The JSON is invalid: {error}"
        messages += [{"role": "assistant", "content": response.message.content},
                     {"role": "user",
                      "content": problem + " Reply again with JSON only."}]
    return None, 2, responses  # unscored after one retry


# --- Section 5: the alert rule ----------------------------------------------------

VADER_ALERT_SCORE = -0.5  # alert when the compound score is at or below this value


def should_alert(signal: CustomerSignal | None, compound: float,
                 earlier_negative: bool) -> tuple[bool, str]:
    """Plain code decides on the alert. The model only describes the message."""
    if signal is None:  # unscored: fall back to VADER
        return compound <= VADER_ALERT_SCORE, "unscored, VADER fallback"
    if signal.escalation_risk == "high":
        return True, "high escalation risk"
    if signal.churn_intent:
        return True, "churn intent"
    if signal.sentiment == "negative" and earlier_negative:
        return True, "second negative message"
    return False, ""


def vader_alert(compound: float, earlier_negative: bool) -> tuple[bool, str]:
    if compound <= VADER_ALERT_SCORE:
        return True, "very negative score"
    if compound <= -0.05 and earlier_negative:
        return True, "second negative message"
    return False, ""


if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) or "Third time I'm writing about this. Fine, I'll just cancel."
    label, compound = vader_score(text)
    print(f"VADER: {label} ({compound})")
    signal, calls, _ = llm_score(text)
    print(f"LLM ({MODEL}, {calls} call(s)): {signal}")
    print("Alert:", should_alert(signal, compound, earlier_negative=False))
