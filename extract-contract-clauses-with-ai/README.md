# Extract Key Clauses and Dates From Contracts With AI

Example code for the howtodoinjava.com article "How to Extract Key Clauses and Dates From
Contracts With AI".

A local Ollama model reads service agreements and returns five terms (parties, effective date,
initial term, renewal terms, governing law), each with the sentence it came from. Plain Python
then checks that every quote is really in the contract and that the value follows from it,
calculates the term end and the last day to send a non-renewal notice, writes those deadlines
to an iCalendar file, and sends every failed check to `review.csv` for a person.

This code finds and quotes contract terms. It is not legal advice.

## Files

| File | What it does |
|---|---|
| `make_contracts.py` | Writes 6 fictional service agreements to `contracts/` and the expected answers to `labels.json` |
| `extractor.py` | The extractor: clauses, keyword search, model call, quote check, deadlines, calendar and review list |
| `evaluate.py` | Runs all contracts with keyword-selected clauses and with the whole contract, scores them against `labels.json`, writes `results.json` |
| `check_without_model.py` | Runs every step except the model call with hand-written answers; needs no Ollama server |
| `contracts/`, `labels.json` | The generated sample contracts and labels (all companies and people are invented) |

## Versions

Python 3.12 or later (the article's numbers were measured on Python 3.13), Ollama with the
`qwen2.5:7b` model, and the packages pinned in `requirements.txt`:
ollama 0.6.3, pydantic 2.14.1, pypdf 6.21.2, icalendar 7.3.0, fpdf2 2.8.9.

## How to run

```bash
ollama pull qwen2.5:7b
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python make_contracts.py          # contracts/C1.pdf ... C6.pdf and labels.json
python check_without_model.py     # all steps except the model, no Ollama needed
python extractor.py               # contract-deadlines.ics and review.csv for all contracts
python evaluate.py                # 12 model calls, prints the scores, writes results.json
```

Ollama must be running at http://localhost:11434. Both `extractor.py` and `evaluate.py` take
`--model` to try another model, and `evaluate.py` takes `--contracts C1 C3` to run a subset.
`extractor.py` calculates deadlines from today; `evaluate.py` uses 2026-10-26, the day the
labels were worked out for.

## Which model produced the article's numbers

The accuracy table in the article (29 of 30 fields correct as returned, 28 verified and 2 sent
to a person after the check, 0 verified but wrong, 349 vs 938 average prompt tokens) was measured
by the author with `qwen2.5:7b` on a shared 2-core CPU server. On a CPU, one contract takes
several minutes.

The original sample contracts were rebuilt for this repository. `make_contracts.py` reproduces
the facts the article prints (C6 has 37 clauses, clauses 21.3 and 21.4 on page 4, the keyword
search keeps 0, 2.1, 10.1, 21.3 and 21.4), and all labelled deadlines match the article.
Model output differs between models and model versions, so expect your counts to differ from the
article's; a smaller model such as `qwen2.5:3b` makes more mistakes, which the quote check sends
to `review.csv`.
