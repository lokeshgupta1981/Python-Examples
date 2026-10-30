import json
import sys
import time
from pathlib import Path

import ollama
import pandas as pd
from pydantic import ValidationError

from catalog import load_catalog
from checks import check_facts, check_style
from prompt import PROMPT_VERSION, build_messages
from schema import ProductCopy

MODEL = "qwen2.5:3b"
OPTIONS = {"temperature": 0, "num_predict": 500}
DATA = Path("data")
OUT = Path("results")


def write_copy(messages):
    started = time.perf_counter()
    response = ollama.chat(model=MODEL, messages=messages,
                           format=ProductCopy.model_json_schema(), options=OPTIONS)
    seconds = time.perf_counter() - started
    raw = response.message.content
    try:
        copy = ProductCopy.model_validate_json(raw)
    except ValidationError as error:
        problems = [f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in error.errors()]
        return None, raw, problems, seconds
    return copy, raw, [], seconds


def check(copy, facts, banned_words):
    return check_facts(copy, facts) + check_style(copy, banned_words)


def process(product, voice, banned_words):
    messages = build_messages(product["facts"], voice)
    attempts = []
    for attempt in (1, 2):
        copy, raw, violations, seconds = write_copy(messages)
        if copy:
            violations = check(copy, product["facts"], banned_words)
        attempts.append({"raw": raw, "violations": violations, "seconds": round(seconds, 1)})
        if not violations:
            return copy, attempts
        messages += [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": "Your answer broke these rules:\n- "
             + "\n- ".join(violations)
             + "\nWrite it again. Fix only these problems and use only the listed facts."},
        ]
    return None, attempts


def main(limit):
    voice = (DATA / "brand_voice.md").read_text()
    banned_words = (DATA / "banned_words.txt").read_text().split()
    products = load_catalog(DATA / "catalog.csv")[:limit]
    OUT.mkdir(exist_ok=True)
    passed, review, log = [], [], []

    for product in products:
        copy, attempts = process(product, voice, banned_words)
        status = "review" if copy is None else f"passed on attempt {len(attempts)}"
        print(f"{product['sku']}: {status} "
              f"({' + '.join(str(a['seconds']) for a in attempts)} s)")
        for a in attempts:
            for v in a["violations"]:
                print(f"    {v}")
        log.append({"sku": product["sku"], "model": MODEL, "prompt": PROMPT_VERSION,
                    "status": status, "attempts": attempts})
        if copy:
            passed.append({"sku": product["sku"], "title": copy.title,
                           "body": copy.description, "bullets": " | ".join(copy.bullets),
                           "seo_title": copy.meta_title,
                           "seo_description": copy.meta_description})
        else:
            review.append({"sku": product["sku"],
                           "reasons": "; ".join(attempts[-1]["violations"]),
                           "last_answer": attempts[-1]["raw"]})

    pd.DataFrame(passed).to_csv(OUT / "descriptions_import.csv", index=False)
    pd.DataFrame(review, columns=["sku", "reasons", "last_answer"]).to_csv(
        OUT / "needs_review.csv", index=False)
    (OUT / "run_log.json").write_text(json.dumps(log, indent=2))
    print(f"{len(passed)} passed, {len(review)} sent to review")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
