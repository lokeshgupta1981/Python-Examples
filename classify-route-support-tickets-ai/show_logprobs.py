"""Print the answer and the per-token probabilities for one ticket.

Usage: python show_logprobs.py [ticket_id] [--bare]
--bare sends only the ticket text, without the system prompt.
"""
import json
import math
import sys

from triage import HERE, call_model, zero_shot_messages

args = [a for a in sys.argv[1:] if not a.startswith("--")]
bare = "--bare" in sys.argv
ticket_id = int(args[0]) if args else 1

tickets = {t["id"]: t for t in map(json.loads, (HERE / "tickets.jsonl").read_text().splitlines())}
text = tickets[ticket_id]["text"]
messages = [{"role": "user", "content": text}] if bare else zero_shot_messages(text)

response = call_model(messages)
print(response.message.content)
for token in response.logprobs or []:
    line = f"{token.token!r} {math.exp(token.logprob):.6f}"
    others = [t for t in (token.top_logprobs or []) if t.token != token.token]
    if others and math.exp(token.logprob) < 0.9995:  # show alternatives only where the model hesitated
        line += " alternatives: " + ", ".join(
            f"{t.token!r} {math.exp(t.logprob):.4f}" for t in others[:2])
    print(line)
