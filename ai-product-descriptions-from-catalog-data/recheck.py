"""Re-runs the fact check on the saved first answers with a wider vocabulary.

No model calls: it reads results/run_log.json (or sample-output/run_log.json).
"""
import json
import re
import sys
from pathlib import Path

import checks
from catalog import load_catalog
from schema import ProductCopy

CLAIMS = ["dry", "lightweight", "compact", "tough", "durable", "comfortable"]
WATERPROOF = re.compile(r"\d+\s*mm|ipx[78]", re.IGNORECASE)


def check_claims(copy, facts):
    text = checks.copy_text(copy).lower()
    source = " ".join(facts.values()).lower()
    violations = [f"unsupported claim: {word}" for word in CLAIMS
                  if re.search(rf"\b{word}\b", text) and not re.search(rf"\b{word}\b", source)]
    if re.search(r"\bwaterproof\b", text) and not WATERPROOF.search(
            facts.get("waterproof_rating", "")):
        violations.append("unsupported claim: waterproof")
    return violations


log_path = Path(sys.argv[1] if len(sys.argv) > 1 else "results/run_log.json")
facts = {p["sku"]: p["facts"] for p in load_catalog("data/catalog.csv")}
for row in json.loads(log_path.read_text()):
    copy = ProductCopy.model_validate_json(row["attempts"][0]["raw"])
    found = checks.check_facts(copy, facts[row["sku"]]) + check_claims(copy, facts[row["sku"]])
    print(f"{row['sku']}: {', '.join(found) or 'ok'}")
