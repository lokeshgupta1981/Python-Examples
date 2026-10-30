# Generate Product Descriptions From Catalog Data With AI

Example project for the howtodoinjava.com article "How to Generate Product Descriptions From Catalog Data With AI".

The script reads a product catalog CSV, asks a local model in Ollama for product copy (title, description, 3 to 5 bullets, meta title, meta description) as JSON that matches a Pydantic schema, and checks every answer in plain code:

- schema and length limits (Pydantic),
- invented numbers and spec words (every one must be in the row),
- attribute names the model claims to have used,
- banned marketing words and exclamation marks.

A row that fails is retried once with the list of violations. Rows that pass go to `results/descriptions_import.csv`; rows that fail twice go to `results/needs_review.csv` with the reasons and the last answer. Every attempt is logged in `results/run_log.json` with the model name and the prompt version.

## Files

| File | What it does |
|---|---|
| `data/catalog.csv` | 12 products of TrailGear, a made-up outdoor shop; 3 rows are deliberately sparse (name and category only) |
| `data/brand_voice.md`, `data/banned_words.txt` | Tone of voice and words that must not appear |
| `data/labels.csv` | Hand labels: does the first answer for a row contain an invented claim? |
| `catalog.py` | Loads the CSV, drops empty cells, adds units |
| `schema.py` | `ProductCopy` Pydantic model |
| `prompt.py` | System prompt (voice, rules, schema) and the fact lines |
| `checks.py` | Fact check and style check, no model needed |
| `generate.py` | The pipeline: generate, check, retry once, export |
| `evaluate.py` | Compares the checker's flags on the first answers with `data/labels.csv` |
| `recheck.py` | Re-checks the saved answers with a wider claim vocabulary, no model calls |
| `schema_probe.py` | One call that tests whether Ollama enforces `maxLength` and `maxItems` (not run for the article) |
| `test_checks.py` | Unit tests for the checks |
| `sample-output/` | The files from the run quoted in the article |

Product names, SKUs and prices come from the TrailGear dataset of the article "Semantic Search for a Product Catalog in Spring Boot"; the structured attributes were added for this example.

## Versions

- Python 3.12 (3.11 or later, because of pandas 3.1)
- ollama 0.6.3, pydantic 2.14.2, pandas 3.1.0 (`requirements.txt`)
- Ollama server 0.40.13 with `qwen2.5:3b`

## How to run

```bash
ollama pull qwen2.5:3b

python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m unittest test_checks      # no model needed
python generate.py                  # all rows; "python generate.py 3" for the first 3
python evaluate.py
python recheck.py
python schema_probe.py
```

## Which numbers are in the article

All numbers in the article come from one run of `generate.py` on 2026-10-31 with `qwen2.5:3b` (temperature 0, `num_predict` 500) on a shared, CPU-only Ollama 0.40.13: 2 vCPUs of an Intel Xeon at 2.10 GHz, no GPU. The files of that run are in `sample-output/`.

- 8 rows passed on the first attempt, 2 after the retry, 2 went to review.
- 16 model calls, median 35.2 s per call, 550 s of model time in total (9 min 11 s wall clock).
- Hand labels: 5 of 12 first answers contained an invented claim; `checks.py` flagged 1 of them, with no false alarms. `recheck.py` flags all 5, plus the dry bag.
- No answer contained an invented number.

A different model, Ollama version or machine will give different text and timings. The labels in `data/labels.csv` belong to the answers in `sample-output/run_log.json`; after a new run, label the new answers before running `evaluate.py`.
