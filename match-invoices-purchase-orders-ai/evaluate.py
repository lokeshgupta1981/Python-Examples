"""Runs the matcher on the 40 labelled invoices and compares with labels.csv.

  python evaluate.py two-way            rules only, invoice vs PO
  python evaluate.py three-way          rules only, adds the goods receipt
  python evaluate.py rapidfuzz          three-way + string similarity pairing (cutoff 60)
  python evaluate.py rapidfuzz:50       the same with another cutoff
  python evaluate.py qwen2.5:3b         three-way + model pairing
  python evaluate.py qwen2.5:3b --explain   also writes explanations to exceptions.csv
  python evaluate.py qwen2.5:3b+agree   accept a model pair only if its rapidfuzz score is at least 60
  python evaluate.py qwen2.5:3b+agree --replay   same, reusing the model answers logged by the qwen2.5:3b run
"""
import csv
import json
import sys
import time
from pathlib import Path

import pandas as pd

import pairers
from matcher import load_data, load_invoice, match_invoice

HERE = Path(__file__).parent
DATA = HERE / "data"
RESULTS = HERE / "results"


def run(config: str, explain: bool):
    mode = "two-way" if config == "two-way" else "three-way"
    pairer = None
    if config.startswith("rapidfuzz"):  # "rapidfuzz" or "rapidfuzz:50"
        cutoff = int(config.split(":")[1]) if ":" in config else 60
        pairer = pairers.rapidfuzz_pairer(cutoff=cutoff)
    elif config.endswith("+agree"):
        model = config.removesuffix("+agree")
        replay = None
        if "--replay" in sys.argv:  # the logged answers of "python evaluate.py <model>"
            log = RESULTS / f"suggestions-{model.replace(':', '_')}.json"
            replay = {(d["line"], d["candidates"]): json.dumps({"po_line_id": d["po_line_id"], "reason": d["reason"]})
                      for d in json.loads(log.read_text())}
        pairer = pairers.llm_pairer(model, min_score=60, replay=replay)
    elif config not in ("two-way", "three-way"):
        pairer = pairers.llm_pairer(config)

    pos, receipts = load_data(DATA)
    labels = pd.read_csv(DATA / "labels.csv", keep_default_na=False).set_index("invoice_file")
    line_labels = pd.read_csv(DATA / "line_labels.csv", keep_default_na=False)

    seen, rows, held = set(), [], []
    start = time.perf_counter()
    for path in sorted((DATA / "invoices").glob("*.json")):
        invoice = load_invoice(path)
        result = match_invoice(invoice, pos, receipts, seen, mode=mode, pairer=pairer)
        codes = ";".join(sorted({e.code for e in result.exceptions}))
        label = labels.loc[path.name]
        rows.append({"invoice_file": path.name, "planted": label.planted,
                     "expected": label.expected_decision, "decision": result.decision,
                     "expected_codes": label.expected_codes, "codes": codes,
                     "model_calls": result.model_calls, "pairs": result.pairs})
        if result.decision == "hold":
            held.append((invoice, result))
    elapsed = time.perf_counter() - start

    df = pd.DataFrame(rows)
    false_approvals = df[(df.expected == "hold") & (df.decision == "approve")]
    false_holds = df[(df.expected == "approve") & (df.decision == "hold")]

    # pairing accuracy on invoice lines that have no item code
    attempted = line_labels[line_labels.invoice_file.isin(
        df[~df.codes.str.contains("PO_NOT_FOUND|DUPLICATE")].invoice_file)]
    pairs = {r.invoice_file: r.pairs for r in df.itertuples()}
    correct_pairs = sum(pairs[r.invoice_file].get(r.line_no, "") == r.expected_po_line
                        for r in attempted.itertuples())

    summary = {
        "config": config,
        "invoices": len(df),
        "correct_decisions": int((df.expected == df.decision).sum()),
        "exact_codes": int((df.expected_codes == df.codes).sum()),
        "false_approvals": false_approvals.invoice_file.tolist(),
        "false_holds": false_holds.invoice_file.tolist(),
        "lines_without_code": len(attempted),
        "lines_paired_correctly": int(correct_pairs),
        "model_calls": int(df.model_calls.sum()),
        "invalid_model_answers": pairers.MODEL_TIME["invalid"],
        "pairing_model_seconds": round(pairers.MODEL_TIME["seconds"], 1),
        "run_seconds": round(elapsed, 1),
    }

    if explain:
        before = pairers.MODEL_TIME["seconds"]
        with open(RESULTS / "exceptions.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["invoice_file", "invoice_number", "codes", "details", "explanation"])
            for invoice, result in held:
                text = pairers.explain(config, invoice, result)
                w.writerow([next(r["invoice_file"] for r in rows if r["pairs"] is result.pairs),
                            invoice.invoice_number,
                            ";".join(e.code for e in result.exceptions),
                            " | ".join(e.detail for e in result.exceptions), text])
        summary["explanations"] = len(held)
        summary["explain_model_seconds"] = round(pairers.MODEL_TIME["seconds"] - before, 1)

    name = config.replace(":", "_").replace("+", "-")
    df.drop(columns="pairs").to_csv(RESULTS / f"decisions-{name}.csv", index=False)
    (RESULTS / f"summary-{name}.json").write_text(json.dumps(summary, indent=2))
    if pairers.LOG and "--replay" not in sys.argv:
        (RESULTS / f"suggestions-{name}.json").write_text(json.dumps(pairers.LOG, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    run(sys.argv[1], "--explain" in sys.argv)
