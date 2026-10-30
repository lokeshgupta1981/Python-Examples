# Categorize Bank Transactions With an LLM in Python

Example code for the howtodoinjava.com article
[How to Categorize Bank Transactions With an LLM in Python](https://howtodoinjava.com/?p=48052).

It categorizes the rows of a small UK business bank export in three layers:

1. Merchant rules learned from months that are already categorized.
2. A local LLM in Ollama for the rows no rule matches. The answer is restricted to
   a fixed category list with a JSON schema (structured output).
3. A code check and a review file: only high-confidence answers that pass the
   check are accepted; everything else goes to `review.csv` for a person.

At month end, the finished rows become new rules, and every new rule is shown
with its source rows before it is saved.

## Files

| File | What it does |
|---|---|
| `categories.py` | The 12 categories with definitions, and the money-in / money-out sets |
| `bankcat.py` | Cleaning, merchant keys, rules, schema, prompt, model call, check, routing, `categorize_month()` |
| `generate_transactions.py` | Writes the fictional sample data in `data/` |
| `run_experiment.py` | Compares rules only, LLM only, rules + LLM and batched rules + LLM on September |
| `learn_from_review.py` | Plays the reviewer, learns rules from the finished month, shows them, measures October |
| `data/history.csv` | July and August, categorized (64 rows) |
| `data/test.csv` | September, labelled test set (60 rows) |
| `data/next.csv` | October (44 rows) |

## Versions

- Python 3.12 or later (tested on 3.13)
- ollama 0.6.3, pydantic 2.14.1, pandas 3.1.0, Faker 40.43.0 (`requirements.txt`)
- Ollama with `qwen2.5:7b` (the default in `bankcat.py`)

## How to run

```bash
ollama pull qwen2.5:7b

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python generate_transactions.py      # writes data/history.csv, test.csv, next.csv
python run_experiment.py             # 60 one-row calls + 2 batched calls
python learn_from_review.py          # new rules, then October coverage

python bankcat.py data/next.csv      # one month: categorized.csv and review.csv
```

`run_experiment.py --model qwen2.5:3b --limit 6` runs a short smoke test with
another model on the first 6 September rows (7 model calls).

## Where the article's numbers come from

The results in the article (for example 52 of 60 rows decided at 98.1% accuracy
with 29 model calls, and the batched setup's 6 wrong accepted answers) were
measured by the author with `qwen2.5:7b` in Ollama. Model answers vary with the
model, the Ollama version and the hardware, so a new run can differ.

This folder was rebuilt from the article's code blocks; the code in the article
is unchanged. `generate_transactions.py`, `run_experiment.py` (apart from the
`summarize()` lines shown in the article), the `stats()` and `main()` glue in
`bankcat.py`, and the reviewer step in `learn_from_review.py` were written again
for this folder. The rebuilt data reproduces the article's model-free numbers:
25 rules from the 64 history rows, 31 of 60 September rows matched by rules (all
correct), and 31 of 44 October rows covered by the old rules. When the model
answers like the article's run (correct, except the MailKite row as Office
supplies), `learn_from_review.py` also gives 19 new rules and 41 of 44 October
rows (93.2%).

What was checked while rebuilding:

- Every part that does not need a model, with the model call replaced by a stub.
- A smoke test of the model parts with `qwen2.5:3b` on 6 rows (7 calls): the
  schema, the one-row calls, the batched call and the review file all worked.
  The 3b answers are not used anywhere in the article.

All names in the data are fictional.
