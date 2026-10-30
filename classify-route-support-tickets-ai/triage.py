import json
import math
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import ollama
from pydantic import BaseModel, ValidationError

MODEL = "qwen2.5:7b"
THRESHOLD = 0.99  # chosen from the measured threshold table (see report.py)
HUMAN_QUEUE = "human-triage"

HERE = Path(__file__).parent
CONFIG = json.loads((HERE / "categories.json").read_text())
QUEUES = {c["name"]: c["queue"] for c in CONFIG["categories"]}
EXAMPLES = [json.loads(line)
            for line in (HERE / "tickets-examples.jsonl").read_text().splitlines()]

client = ollama.Client(timeout=1800)  # a CPU-only model can take a while


# Step 1: categories, priorities and the answer shape

class Category(str, Enum):
    BILLING = "BILLING"
    SHIPPING = "SHIPPING"
    RETURNS = "RETURNS"
    ACCOUNT = "ACCOUNT"
    TECHNICAL = "TECHNICAL"
    OTHER = "OTHER"


class Priority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class TicketResult(BaseModel):
    category: Category
    priority: Priority


# Step 2: the zero-shot prompt

def system_prompt() -> str:
    lines = ["You sort customer support tickets for OrderDesk, "
             "an online office-supplies store.",
             "Choose one category:"]
    lines += [f"{c['name']}: {c['definition']}" for c in CONFIG["categories"]]
    lines.append("Choose one priority:")
    lines += [f"{p['name']}: {p['definition']}" for p in CONFIG["priorities"]]
    lines.append('Reply with JSON only: {"category": "...", "priority": "..."}')
    return "\n".join(lines)


def zero_shot_messages(ticket_text: str) -> list[dict]:
    return [{"role": "system", "content": system_prompt()},
            {"role": "user", "content": ticket_text}]


# Step 3: call Ollama with a JSON schema and token probabilities

def call_model(messages: list[dict]) -> ollama.ChatResponse:
    return client.chat(
        model=MODEL,
        messages=messages,
        format=TicketResult.model_json_schema(),  # the answer must match this schema
        options={"temperature": 0, "num_predict": 64},  # the answer is ~15 tokens
        logprobs=True,  # return a probability per token
        top_logprobs=3)  # and the 3 most likely alternatives


# Step 4: validate the model output, retry once

def classify(messages: list[dict]
             ) -> tuple[TicketResult | None, ollama.ChatResponse, int]:
    response = call_model(messages)
    try:
        return TicketResult.model_validate_json(response.message.content), response, 1
    except ValidationError as error:
        retry = messages + [
            {"role": "assistant", "content": response.message.content},
            {"role": "user", "content": f"That answer is invalid: {error}. "
                                        "Reply again with valid JSON only."}]
        response = call_model(retry)
        try:
            result = TicketResult.model_validate_json(response.message.content)
            return result, response, 2
        except ValidationError:
            return None, response, 2


# Step 5: confidence score from the token probabilities

def category_confidence(response: ollama.ChatResponse) -> tuple[float, str, float]:
    """Probability of the first token of the category value, plus the runner-up."""
    content = response.message.content
    tokens = response.logprobs or []
    if "".join(t.token for t in tokens) != content:
        return 0.0, "", 0.0  # can't line tokens up: treat as unsure
    key = content.find('"category"')
    value_start = content.find('"', content.find(":", key)) + 1
    position = 0
    for token in tokens:
        position += len(token.token)
        if position > value_start:  # this token holds the first value character
            others = [t for t in token.top_logprobs if t.token != token.token]
            runner_up = others[0] if others else None
            return (math.exp(token.logprob),
                    runner_up.token if runner_up else "",
                    math.exp(runner_up.logprob) if runner_up else 0.0)
    return 0.0, "", 0.0


# Step 6: the few-shot prompt

def few_shot_messages(ticket_text: str) -> list[dict]:
    messages = [{"role": "system", "content": system_prompt()}]
    for example in EXAMPLES:
        answer = {"category": example["category"], "priority": example["priority"]}
        messages.append({"role": "user", "content": example["text"]})
        messages.append({"role": "assistant", "content": json.dumps(answer)})
    messages.append({"role": "user", "content": ticket_text})
    return messages


# Step 7: route to a team queue or the human queue

@dataclass
class RoutingDecision:
    queue: str
    category: str | None
    priority: str | None
    confidence: float
    reason: str


def route(result: TicketResult | None, confidence: float,
          threshold: float = THRESHOLD) -> RoutingDecision:
    if result is None:
        return RoutingDecision(HUMAN_QUEUE, None, None, 0.0, "invalid answer")
    category, priority = result.category.value, result.priority.value
    if confidence < threshold:
        return RoutingDecision(HUMAN_QUEUE, category, priority, confidence,
                               "low confidence")
    return RoutingDecision(QUEUES[category], category, priority, confidence, "confident")


def triage(ticket_text: str, few_shot: bool = True) -> RoutingDecision:
    build = few_shot_messages if few_shot else zero_shot_messages
    messages = build(ticket_text)
    result, response, _ = classify(messages)
    confidence = category_confidence(response)[0] if result else 0.0
    return route(result, confidence)


if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) or "I was charged twice for order 1043."
    print(triage(text))
