# Spot Unhappy Customers in Support Messages With AI

Example project for the howtodoinjava.com article
"How to Spot Unhappy Customers in Support Messages With AI".

The project compares two ways to find risky messages in a support queue for OrderDesk, an
online office-supplies store:

- VADER, a rule-based sentiment word list, as a baseline.
- A local LLM in Ollama that describes each message in a fixed JSON shape: sentiment, anger,
  churn intent, escalation risk and an evidence quote.

Plain Python validates the LLM answer (one retry, then a VADER fallback) and decides whether
to alert a team lead. Two scripts measure both approaches on 50 labelled messages, try two tuned
alert rules and a two-stage setup (VADER first, LLM only for messages that are not clearly positive).

## Files

| File | What it does |
|---|---|
| `detector.py` | `vader_score()`, the `CustomerSignal` schema, the system prompt, `ask_model()`, `llm_score()` with validation and one retry, and the alert rules `should_alert()` and `vader_alert()` |
| `messages.csv` | 50 labelled support messages in arrival order (`sentiment`, `should_escalate`, `case`) |
| `evaluate.py` | Runs VADER and the LLM on every message and writes `results.csv` one row at a time (resumes if interrupted) |
| `report.py` | Reads `results.csv` and prints sentiment reports, alert confusion matrices, the comparison table, the trap table, speed and token counts (no model call) |
| `requirements.txt` | Pinned library versions |

## Versions

- Python 3.12 or later (the article's run used Python 3.13)
- `vaderSentiment==3.3.2`, `ollama==0.6.3` (Python client), `pydantic==2.14.1`, `scikit-learn==1.9.1`
- Ollama server with `qwen2.5:7b` (the article's run used Ollama 0.40.11)

## How to run

```bash
ollama pull qwen2.5:7b
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python detector.py "Third time I'm writing about this. Fine, I'll just cancel."
python evaluate.py               # slow on a CPU: 50 model calls, about 20 s each on 2 cores
python report.py
```

`evaluate.py` also takes `--model`, `--limit N`, `--data FILE` and `--out FILE`, for example
`python evaluate.py --model qwen2.5:3b --limit 3 --out smoke.csv` for a quick check, then
`python report.py smoke.csv`.

## Which model produced the article's numbers

All numbers in the article (accuracy, recall, precision, the trap table, 20.5 seconds median
compute per message, 266 prompt and 52 output tokens) were measured by the author with
`qwen2.5:7b` on Ollama 0.40.11, CPU only on a shared 2-core machine, one run.

Note on the data: the original `messages.csv` used for the article was not preserved. The file
in this folder is a reconstruction with the same composition: 20 negative, 20 neutral and
10 positive messages, 18 that should escalate, the same traps (5 polite cancellations,
3 sarcastic messages, 2 calm legal threats, 5 technical messages, 3 angry messages about small
issues, 4 repeat contacts) and the same three customers who write twice. Every message quoted in
the article is included (with the article's ID where it gives one), and VADER gives the published scores for them
(0.0, 0.7096 and 0.8516). 13 messages score 0.5 or more, as in the article. The other messages are
new, so a fresh run will not reproduce the published tables exactly.

The code was smoke-tested against `qwen2.5:3b`; those runs only check that the code works and
are not the article's results.
