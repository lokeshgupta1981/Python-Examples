# Match Invoices to Purchase Orders With AI

Example project for the howtodoinjava.com article
[How to Match Invoices to Purchase Orders Automatically With AI](https://howtodoinjava.com/ai/match-invoices-purchase-orders-ai/).

It shows a two-way and three-way invoice matcher in which plain Python rules make
every approve-or-hold decision. A local LLM (through Ollama) is used only to pair
invoice lines that are worded differently from the purchase order, and to write a
short explanation for each held invoice.

## Files

| File | What it does |
|---|---|
| `generate_cases.py` | Writes 40 synthetic cases to `data/` (POs, goods receipts, invoice JSON files, labels). Fixed seed 42. |
| `matcher.py` | Pydantic models, header checks, item-code pairing, suggestion check, price and quantity tolerances. No model calls. |
| `pairers.py` | `rapidfuzz` pairer, LLM pairer with structured output (`LineMatch`), and the explanation prompt. |
| `evaluate.py` | Runs one configuration on the 40 invoices and compares with `data/labels.csv`; writes `results/`. |

## Versions

Python 3.13.18 (3.12+ works), ollama 0.6.3, pydantic 2.14.2, pandas 3.1.0, rapidfuzz 3.14.6,
faker 40.44.0. Ollama server 0.40.13 with `qwen2.5:3b` (Q4_K_M, 1.9 GB).

## How to run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen2.5:3b

python generate_cases.py
python evaluate.py two-way       # rules only, invoice vs PO
python evaluate.py three-way     # rules only, with goods receipts
python evaluate.py rapidfuzz     # three-way + string similarity (cutoff 60)
python evaluate.py rapidfuzz:50  # another cutoff
python evaluate.py qwen2.5:3b --explain   # three-way + model pairing + explanations
python evaluate.py qwen2.5:3b+agree --replay   # accept a model pair only if rapidfuzz scores it >= 60
```

Model calls use temperature 0, seed 42 and a `num_predict` limit.

## Which model produced the article's numbers

All model numbers in the article were measured with `qwen2.5:3b` (Q4_K_M) on Ollama 0.40.13,
CPU only, on 2 vCPUs of an Intel Xeon at 2.10 GHz, temperature 0, seed 42.

| Configuration | Correct decisions | False approvals | False holds | Lines paired correctly (of 27) |
|---|---|---|---|---|
| two-way | 27 | 5 | 8 | 3 |
| three-way | 32 | 0 | 8 | 3 |
| rapidfuzz, cutoff 50 | 37 | 3 | 0 | 24 |
| rapidfuzz, cutoff 60 | 38 | 0 | 2 | 21 |
| qwen2.5:3b | 35 | 1 | 4 | 19 |
| qwen2.5:3b+agree (replayed answers) | 35 | 0 | 5 | 19 |

Model time: 27 pairing calls took 267.4 s (9.9 s per call); 21 explanations took 371.1 s
(17.7 s each). The `+agree` row reuses the 27 logged answers (`--replay`) because the agreement
rule is applied in code after the model has answered. Other cutoffs: `python evaluate.py rapidfuzz:50`
(and `rapidfuzz:70`: 33 correct, 0 false approvals, 7 false holds, 14 lines paired correctly).

The `results/` folder holds the files from those runs: decisions per invoice, the logged model
suggestions (`suggestions-qwen2.5_3b.json`) and the explanations (`exceptions.csv`).
