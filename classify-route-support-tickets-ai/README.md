# Classify and Route Support Tickets With AI in Python

Example project for the howtodoinjava.com article
"How to Classify and Route Support Tickets With AI in Python".

A local model in Ollama reads a support ticket for OrderDesk, an online office-supplies store,
and answers with a category and a priority in a fixed JSON shape. Plain Python validates the
answer, turns the probability of the first category token into a confidence score, and routes
the ticket to a team queue, or to a `human-triage` queue when the confidence is below a threshold.
Two scripts measure zero-shot and few-shot prompts on 60 labelled tickets and build a threshold table.

## Files

| File | What it does |
|---|---|
| `categories.json` | Categories, priorities, their definitions and team queues |
| `triage.py` | The classifier: prompts, Ollama call with a JSON schema and logprobs, validation with one retry, confidence score, routing |
| `show_logprobs.py` | Prints the answer and per-token probabilities for one ticket (`--bare` sends it without the system prompt) |
| `tickets.jsonl` | 100 labelled tickets |
| `make_test_set.py` | Picks 10 tickets per category (seed 42) into `tickets-test.jsonl` |
| `tickets-test.jsonl` | The 60 test tickets |
| `tickets-examples.jsonl` | 6 solved tickets for the few-shot prompt (not in the test set) |
| `evaluate.py` | Runs both prompts over the test tickets, writes `results.csv` (resumes if interrupted) |
| `report.py` | Reads `results.csv`, prints accuracy and threshold tables, writes `summary.json` (no model call) |

## Versions

- Python 3.12 or later (the article's run used Python 3.13)
- `ollama==0.6.3` (Python client), `pydantic==2.14.1`
- Ollama server with `qwen2.5:7b` (the article's run used Ollama 0.40.11)

## How to run

```bash
ollama pull qwen2.5:7b
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python triage.py "The courier left my parcel at number 41 instead of 14 and now it is gone."
python show_logprobs.py 1
python show_logprobs.py 1 --bare

python make_test_set.py          # optional, tickets-test.jsonl is included
python evaluate.py               # slow on a CPU: 120 model calls
python report.py
```

`evaluate.py` also takes `--model`, `--limit N` and `--out FILE`, for example
`python evaluate.py --model qwen2.5:3b --limit 3 --out smoke.csv` for a quick check, then
`python report.py smoke.csv`.

## Which model produced the article's numbers

All numbers in the article (accuracy, confidence values, timings and the threshold table) were
measured by the author with `qwen2.5:7b`, one run per prompt. `THRESHOLD = 0.99` in `triage.py`
comes from that table.

Note on the data: the original ticket files used for the article were not preserved. The ticket
files in this folder are a reconstruction. Tickets 1, 60, 68, 72, 74 and 94 are the ones quoted in
the article and are part of the test set, but the other tickets are new, so a fresh run will
not reproduce the published tables exactly. Rebuild the threshold table from your own results
before you change `THRESHOLD`.

The code was smoke-tested against `qwen2.5:3b`; those runs only check that the code works and
are not the article's results.
