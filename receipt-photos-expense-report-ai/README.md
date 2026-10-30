# Receipt Photos to Expense Report With AI

Example code for the howtodoinjava.com article
"How to Turn Receipt Photos Into Expense Reports With AI".

A receipt photo goes through Pillow and Tesseract OCR, a local Ollama model fills a
Pydantic `Receipt` schema (structured output), and plain Python code checks the amounts
and the expense policy. Every receipt ends up approved, flagged with a reason, or sent
to review, and the result is written as a CSV and a PDF expense report.

## Files

| File | What it does |
|---|---|
| `generate_receipts.py` | Draws 15 synthetic travel receipts (clean PNG and phone-like JPEG) and writes `labels.json` |
| `receipt_schema.py` | The `Receipt` Pydantic model whose JSON schema is sent to the model |
| `extract.py` | `prepare_image()`, `ocr()`, `ask_model()`, `validate()`, `extract()`; writes `results_<set>.json` and `ocr/<set>/` |
| `policy.py` | `load_yaml()` and `apply_policy()` (duplicates, trip dates, weekends, meal and per-receipt limits) |
| `report.py` | `build_report()`: `expense_report.csv` and `expense_report.pdf` |
| `evaluate.py` | Field accuracy, statuses, regex baseline and the relaxed rule, compared with `labels.json` (no model calls) |
| `ocr_check.py` | How many printed amounts Tesseract finds with and without `prepare_image()` (no model calls) |
| `policy.yaml`, `trip.yaml` | The expense policy and the trip |

## Versions

Python 3.12 or later, Tesseract 5.3.4, Ollama with `qwen2.5:7b`, and the packages in
`requirements.txt` (ollama, pydantic, pytesseract, pillow, pandas, reportlab, PyYAML, Faker).

## How to run

```bash
# Tesseract: sudo apt install tesseract-ocr   (macOS: brew install tesseract)
ollama pull qwen2.5:7b
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python generate_receipts.py        # receipts/clean, receipts/photo, labels.json
python ocr_check.py photo          # optional, OCR only
python extract.py clean            # 15 model calls
python extract.py photo            # 15 model calls
python report.py photo             # expense_report.csv and expense_report.pdf
python evaluate.py
```

`extract.py` saves after every receipt and skips receipts it already has, so an
interrupted run continues where it stopped. Delete `results_*.json` to start over.

## About the numbers in the article

The article's results (field accuracy, statuses, timings) were measured by the author
with `qwen2.5:7b` on a 2-core CPU without a GPU; the 30 model calls took about 45 minutes.

The original project files were lost, so this folder was rebuilt from the article's
code listings. The listings in the article are unchanged; the generator, `ask_model()`,
the full `apply_policy()`, the PDF part of `build_report()`, `evaluate.py` and
`ocr_check.py` were written again from the article's description. The receipts keep
every value the article names (for example receipt 7 at 63.00 EUR, receipt 11 at
91.94 USD with a 15.00 tip, receipt 12 at 155.94 USD), but the images are not
pixel-identical to the author's, so a new run gives OCR results and model answers
that differ in detail from the published ones.

The rebuilt project was checked as follows: the generator, OCR, `ocr_check.py`,
the policy, the report and `evaluate.py` ran offline (with model answers simulated from
`labels.json`), and two receipts went through `extract()` against a local `qwen2.5:3b`
as a smoke test. The published numbers are the author's `qwen2.5:7b` results.
