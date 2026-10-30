# Summarize Customer Reviews Into Pros and Cons With AI

Example code for the howtodoinjava.com article
[How to Summarize Customer Reviews Into Pros and Cons With AI](https://howtodoinjava.com/ai/summarize-customer-reviews-pros-cons/).

It summarizes 60 reviews of a headlamp into a card of pros and cons. A local
model (Ollama) extracts each pro and con with a quote, merges similar aspect
names and words a short overview. Plain Python code removes empty and duplicate
reviews, masks emails and phone numbers, checks every quote against its review,
counts distinct reviews per aspect and checks the overview for invented numbers.
For comparison, `run.py` also asks the model for the whole summary, counts
included, in one prompt with all 60 reviews, and scores both approaches against
the known (planted) counts.

## Files

| File | What it does |
|---|---|
| `generate_reviews.py` | Writes `reviews.csv` (62 rows) and `planted_aspects.csv` (78 planted sentences with known true counts) |
| `summarize.py` | All pipeline functions shown in the article, plus the single-prompt comparison |
| `run.py` | Runs the pipeline and the single prompt (file order and reversed), writes `summary_headlamp.md`, prints the scores and Ollama's token and time statistics |
| `test_offline.py` | Checks every step that needs no model (cleaning, batching, quote check, counting, summary check) |
| `smoke_test.py` | A quick check that every model step runs, on one batch of 10 reviews |

## Versions

- Python 3.12 or later (tested on 3.13)
- ollama 0.6.3, pydantic 2.14.1, pandas 3.1.0 (see `requirements.txt`)
- Ollama with `qwen2.5:7b`

## How to Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen2.5:7b

python generate_reviews.py
python test_offline.py                  # no model needed
python run.py                           # full run, about 54 minutes of model time on a 2-core CPU
MODEL=qwen2.5:3b python smoke_test.py   # quick check with a smaller model
```

`MODEL` overrides the model name in `summarize.py`.

## Which Model Produced the Article's Numbers

The numbers in the article (for example, 12 instead of 24 battery reviews from the
single prompt, and a mean count error of 2.6 for the pipeline) were measured by the
author with `qwen2.5:7b` on a shared two-core CPU server. The original data files of
that run were not kept; `generate_reviews.py` rebuilds a dataset with the same planted
counts (24, 18, 12, 7, 6, 5 and 4 reviews, 78 planted sentences), but not the same
review texts. A new run therefore gives somewhat different numbers, and review
ids such as R12 and R23 in the article refer to the original run.

The generated files contain a fake email address and phone number on purpose, to show
the masking step. They are ignored by `.gitignore`; delete them after a run.
