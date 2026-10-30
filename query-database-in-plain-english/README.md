# Query a Database in Plain English (Text-to-SQL With a Safety Gate)

Example project for the howtodoinjava.com article "How to Let Business Users Query a Database in Plain English".

A local model (Ollama) turns a business question into SQLite SQL and explains the result.
Plain Python code decides whether the SQL runs:

- `check_sql()` parses the SQL with sqlglot: exactly one query, no write node anywhere in the
  tree (also inside `WITH`), only the four known tables, and at most 200 rows.
- `run_query()` uses a read-only connection (`?mode=ro`) and stops a query after 5 seconds.
- `numbers_match()` hides the model's sentence if it contains a number that is not in the rows,
  the question or the SQL.
- `ask()` retries once after an SQL error, never after a blocked query.
- `evaluate.py` measures execution accuracy on the 25 questions in `questions.json`.

## Files

| File | What it does |
|---|---|
| `make_db.py` | Creates `shop.db`: 300 customers, 16 products, 2,380 made-up orders (seeded, repeatable) |
| `schema.md` | The schema description and business terms the model reads before every question |
| `ask.py` | The tool: prompt, safety gate, read-only run, explanation, numbers check, retry |
| `gate_demo.py` | Sends six queries through the gate, then two straight to the read-only connection |
| `questions.json` | 25 questions with hand-written expected SQL (4 with `"ordered": true`) |
| `evaluate.py` | Runs all questions, compares rows, writes `results.json`; `--rescore` skips the model |

## Versions

Python 3.12 or later (tested on 3.13.18 with SQLite 3.53.1), Ollama 0.40.11,
ollama 0.6.3, sqlglot 30.24.0, pydantic 2.14.1.

## How to run

```bash
ollama pull qwen2.5:7b
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python make_db.py
python gate_demo.py                       # no model needed
python ask.py "What are the top 5 products by revenue last quarter?"
python evaluate.py                        # all 25 questions, 2 to 4 minutes each on a 2-core CPU
python evaluate.py --rescore              # compare the saved SQL again without the model
python evaluate.py --model qwen2.5:3b --limit 3   # quick smoke test with a smaller model
```

## Which model produced the article's numbers

The results in the article (17 of 25 correct, 7 wrong answers with a sentence shown, 1 hidden
by the numbers check, 6 retries of which 4 were then correct) were measured by the author with
**qwen2.5:7b** on the original question set and data.

The original `questions.json` and data generator were not preserved. The versions in this folder
were rebuilt from the article (same sizes, same schema description, same example question), so a
new run gives similar, but not identical, numbers.

`gate_demo-output.txt` is a real run of `gate_demo.py` and matches the article. The model parts
were smoke-tested with qwen2.5:3b only (see below); those results are not the article's numbers.

## Smoke test with qwen2.5:3b (2026-10-31)

On a shared 2-core CPU Ollama server:

- `python ask.py "How many customers do we have?"` with qwen2.5:3b: answered in 62 s,
  SQL `SELECT COUNT(id) FROM customers LIMIT 200`, result 300, sentence "We have 300 customers."
  passed the numbers check.
- `python evaluate.py --model qwen2.5:3b --limit 3`: question 1 answered and scored correct
  (163 s). The run was stopped after that because the shared server was queued with other jobs.
- `python evaluate.py --rescore` was checked offline on a hand-made `results.json`.
