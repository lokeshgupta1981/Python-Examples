# AI Email Triage Pipeline in Python

Example project for the howtodoinjava.com article
"How to Build an AI Email Triage Pipeline in Python".

The pipeline sorts the support inbox of OrderDesk, a small online office-supplies store, into
URGENT, NEEDS_REPLY, FYI and SPAM_LIKE, and extracts up to three action items per email.
Header rules file the obvious mail, a local model in Ollama proposes a category and action
items as JSON for the rest, plain Python checks that every quote comes from the email, and a
person approves every move in the terminal. Nothing is sent or deleted.

## Files

| File | What it does |
|---|---|
| `make_mailbox.py` | Writes 30 synthetic emails to `mailbox/inbox/` and the expected answers to `labels.csv` |
| `mail_reader.py` | Reads `.eml` files into `EmailItem` objects (`html_to_text()`, `clean()`) |
| `rules.py` | Header rules (`List-Unsubscribe`, `Auto-Submitted`) with a watch list |
| `triage.py` | JSON schema, prompts, Ollama call, quote check, one retry, status |
| `run_triage.py` | Triages every email (plus the naive prompt for the two injected emails), writes `results.json`, resumes if interrupted |
| `review.py` | Terminal review of every proposal, writes `decisions.csv` |
| `apply.py` | Moves approved emails into `mailbox/urgent`, `needs-reply`, `fyi`, `spam-like` and writes `digest.md` |
| `evaluate.py` | Compares `results.json` with `labels.csv` for three setups, writes `summary.json` |
| `imap_source.py` | Reads unseen mail and moves mail over IMAP (tested only against a fake connection) |
| `test_offline.py` | Offline tests with a fake model and a fake IMAP connection |

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

python make_mailbox.py           # 30 .eml files and labels.csv
python triage.py mailbox/inbox/u07.eml   # one email
python run_triage.py             # the model calls, writes results.json (slow on a CPU)
python review.py                 # writes decisions.csv
python apply.py                  # moves the files, writes digest.md
python evaluate.py               # writes summary.json
```

`run_triage.py` also takes `--model`, `--limit N` and `--out FILE`, for example
`python run_triage.py --model qwen2.5:3b --limit 2 --out smoke.json` for a quick check, then
`python evaluate.py smoke.json`.

To test the review without typing, pipe one answer per line (an empty line is Enter):
`python review.py < answers.txt`.

The offline tests need no Ollama server:

```bash
python -m unittest test_offline -v
```

For a real mailbox, set `IMAP_HOST`, `IMAP_USER` and `IMAP_APP_PASSWORD` and use the functions
in `imap_source.py`. Note that `move()` calls EXPUNGE, which removes every message flagged
`\Deleted` in the selected folder.

## Which model produced the article's numbers

All numbers in the article (correct categories, URGENT recall, action items found, the
`needs_review` cases and 33.6 seconds of model compute per email on a shared 2-core CPU) were
measured by the author with `qwen2.5:7b`, one run, temperature 0.

Note on the data: the original mailbox used for the article was not preserved.
`make_mailbox.py` is a reconstruction that matches every email the article describes
(7 URGENT, 10 NEEDS_REPLY, 8 FYI, 5 SPAM_LIKE, 17 expected action items, 5 emails labeled by
the rules, the PayFast status alert, the ink newsletter, the printer email u03, the phishing
email s02 and the two injected emails n08 and s05). The other emails are new, so a fresh run
will not reproduce the published table exactly, and a different model gives different results.
