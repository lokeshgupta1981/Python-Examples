"""Ways to suggest a PO line for an invoice line that has no matching item code.

Every pairer returns (po_line_id or None, number of model calls).
matcher.accept_pair() checks the suggestion before it is used.
"""
import time

import ollama
from pydantic import BaseModel, Field, ValidationError
from rapidfuzz import fuzz, process, utils

client = ollama.Client(timeout=600)
MODEL_TIME = {"seconds": 0.0, "calls": 0, "invalid": 0}
LOG = []  # every model suggestion, for the report


def candidates(line, free_po_lines, limit=3):
    """Top PO lines by string similarity: (po_line_id, description, score)."""
    choices = {p.po_line_id: p.description for p in free_po_lines}
    found = process.extract(line.description, choices, scorer=fuzz.token_set_ratio,
                            processor=utils.default_process, limit=limit)
    return [(key, desc, score) for desc, score, key in found]


def rapidfuzz_pairer(cutoff=60):
    def pair(line, free_po_lines):
        best = candidates(line, free_po_lines, limit=1)
        if best and best[0][2] >= cutoff:
            return best[0][0], 0
        return None, 0
    pair.label = "rapidfuzz"
    return pair


class LineMatch(BaseModel):
    po_line_id: str = Field(description="One of the candidate ids, or NONE")
    reason: str = Field(description="At most 12 words")


PAIR_PROMPT = """You match one invoice line to a purchase order (PO) line.
A match must be the same product: same item, model number, size, colour and pack size.
Different wording for the same product is a match. A similar but different product is not.
Reply with JSON only: {"po_line_id": "<a candidate id or NONE>", "reason": "<at most 12 words>"}"""


def llm_pairer(model="qwen2.5:3b", min_score=None, replay=None):
    def pair(line, free_po_lines):
        options = candidates(line, free_po_lines)
        listing = "\n".join(f"{key}: {desc}" for key, desc, _ in options)
        prompt = f"Invoice line: {line.description}\n\nCandidates:\n{listing}"
        if replay is not None:  # reuse logged answers of an earlier run instead of calling the model
            answer = replay[(line.description, listing)]
        else:
            answer = ask(model, PAIR_PROMPT, prompt, LineMatch.model_json_schema(), max_tokens=60)
        try:
            match = LineMatch.model_validate_json(answer)
        except ValidationError:
            MODEL_TIME["invalid"] += 1
            LOG.append({"line": line.description, "candidates": listing, "answer": answer})
            return None, 1
        LOG.append({"line": line.description, "candidates": listing,
                    "po_line_id": match.po_line_id, "reason": match.reason})
        scores = {key: score for key, _, score in options}
        if match.po_line_id not in scores:
            return None, 1
        if min_score is not None and scores[match.po_line_id] < min_score:
            return None, 1  # the model and string similarity disagree
        return match.po_line_id, 1
    pair.label = model
    return pair


EXPLAIN_PROMPT = """You write notes for an accounts payable clerk.
The invoice below is on hold. The exceptions were found by rules and are correct.
Write two short sentences: what is wrong, and what the clerk should check.
Use only the facts given. Do not invent numbers."""


def explain(model, invoice, result):
    facts = "\n".join(f"- {e.code}" + (f" (line {e.line_no})" if e.line_no else "") + f": {e.detail}"
                      for e in result.exceptions)
    prompt = (f"Invoice {invoice.invoice_number} from {invoice.vendor_name}, "
              f"PO {invoice.po_number}, total {invoice.total} {invoice.currency}.\nExceptions:\n{facts}")
    return ask(model, EXPLAIN_PROMPT, prompt, None, max_tokens=90).strip()


def ask(model, system, prompt, schema, max_tokens):
    start = time.perf_counter()
    response = client.chat(model=model,
                           messages=[{"role": "system", "content": system},
                                     {"role": "user", "content": prompt}],
                           format=schema,
                           options={"temperature": 0, "seed": 42, "num_predict": max_tokens})
    MODEL_TIME["seconds"] += time.perf_counter() - start
    MODEL_TIME["calls"] += 1
    return response.message.content
