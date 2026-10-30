# AI Lead Scoring With Logistic Regression and a Local LLM

Example code for the howtodoinjava.com article "AI Lead Scoring With Logistic
Regression and a Local LLM".

A scikit-learn logistic regression scores inbound B2B leads from their form fields
(one-hot encoded). A local LLM in Ollama reads the free-text message and returns a few
fixed signals (intent, urgency, quantity, reason) as structured JSON, which become extra
columns for the same model. The project compares three scorers on 500 held-out leads:
fields only, fields + LLM signals, and the LLM alone (on a 25-lead sample).

## Files

| File | What it does |
|---|---|
| `generate_leads.py` | Writes `history.csv` (2,500 past leads with `converted`) and `new_leads.csv` (100 new leads). Conversion follows a hidden rule on the log-odds scale; `true_probability` is stored so the best possible ranking can be measured. |
| `scorer.py` | Seniority mapping, `read_message()` with structured output and a `NEUTRAL` fallback, feature columns, training, tier and reason, metrics, and the LLM-alone scorer. |
| `evaluate.py` | Reads each distinct message once (cached in `signals_cache.json`), trains both models on the first 2,000 leads, scores the 500 held-out leads, runs the LLM-alone sample, writes `results.json`. |
| `score_new_leads.py` | Trains the combined model on the same 2,000 leads and writes `leads_scored.csv` for the CRM. |

## Versions

- Python 3.12 or later (tested with 3.13)
- Ollama with `qwen2.5:7b`
- Libraries pinned in `requirements.txt` (pandas 3.1, scikit-learn 1.9, ollama 0.6, pydantic 2.14, httpx 0.28)

## How to run

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
ollama pull qwen2.5:7b
python generate_leads.py
python evaluate.py                 # add --skip-llm-alone to skip the 25 LLM-alone calls
python score_new_leads.py
```

`evaluate.py` makes 24 model calls for the signals plus 25 for the LLM-alone sample.
On a CPU without a GPU, expect about 10 to 15 seconds per call with `qwen2.5:7b`.
The cache lets an interrupted run continue where it stopped.

To try another model without editing the code, set it before the run, for example:

```bash
python -c "import scorer; scorer.MODEL = 'qwen2.5:3b'; import evaluate; evaluate.main()"
```

## Which model produced the article's numbers

All numbers in the article (AUC 0.652 / 0.801 / 0.842, top-20% shares, weights,
tiers, the 12.8-second median call) were measured by the author with **qwen2.5:7b**
on Ollama 0.40.11, CPU only.

This project was rebuilt from the article's code blocks. `generate_leads.py` follows the
hidden rule described in the article (buying +1.5, support -1.2, other -2.5, urgency and
50+ units add a little, country has no effect), but it is a reconstruction, so the data
and the resulting numbers differ slightly from the article's run (for example, 34.8%
of past leads convert here, against 34.3% in the article). The pipeline itself was
smoke-tested against `qwen2.5:3b`; those numbers are not used in the article.
