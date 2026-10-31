# LLM Pull Request Review

Example code for the howtodoinjava.com article
"How to Review Pull Requests Automatically With an LLM".

A small Python reviewer that:

1. gets a pull request diff from local git (or the GitHub REST API),
2. splits it into hunks with `unidiff` and maps every added line to its new line number,
3. reviews each hunk with a checklist prompt and a local Ollama model, using a JSON schema
   (pydantic) for the answer,
4. drops comments that point to a line that was not added, fall below a confidence
   threshold, or repeat,
5. prints the comments, or posts them as one GitHub review with `event: COMMENT`.

It also contains a demo repository generator with planted bugs, an evaluation script,
offline tests, and a GitHub Actions workflow for a self-hosted runner.

## Files

| File | What it does |
|---|---|
| `reviewer.py` | The reviewer (`review` and `post` commands) |
| `make_repo.py` | Creates the `orderdesk-lite` git repository with 10 PR branches and writes `labels.json` |
| `labels.json` | File, line and category of each planted bug (`null` for the clean refactors) |
| `evaluate.py` | Runs the model on every branch (`run`) and scores the comments (`score`) |
| `test_reviewer.py` | Offline tests: line mapping, filtering, the review payload (no model, no GitHub) |
| `.github/workflows/llm-pull-request-review.yml` | Workflow to copy into your own private repository |
| `raw-*.json`, `results.csv`, `run-*.log` | The measured run used in the article |

## Versions

Python 3.13, ollama (Python library) 0.6.3, unidiff 1.0.1, pydantic 2.14.2, requests 2.34.2,
pytest 9.2.0. Ollama server 0.40.13.

## How to run

```bash
python -m venv venv && . venv/bin/activate
pip install -r requirements.txt
ollama pull qwen2.5:3b

python make_repo.py                  # creates ./orderdesk-lite and labels.json
python -m pytest -q                  # offline tests

python reviewer.py review --repo orderdesk-lite --base main --head pr-2-orders-by-status
python evaluate.py run qwen2.5:3b    # one model call per hunk, about 10 calls
python evaluate.py score             # writes results.csv
python evaluate.py show qwen2.5:3b pr-9-injection   # print one stored review
```

Set `REVIEW_MODEL` (or `--model`) to use another Ollama model, and `OLLAMA_HOST` if Ollama
does not run on localhost:11434.

## Which model produced the article's numbers

All numbers in the article come from `qwen2.5:3b` (Q4_K_M, 1.9 GB) and `qwen3:1.7b`
(thinking off) on Ollama 0.40.13, CPU only, 2 vCPUs (Intel Xeon 2.10 GHz), temperature 0,
one run per PR branch (qwen2.5:3b: 212 s for all 10 branches; qwen3:1.7b: 263 s). The raw model answers are in `raw-qwen2.5_3b.json` and
`raw-qwen3_1.7b.json`. A larger coder model (for example `qwen2.5-coder:7b`) was not run
for the article.

## GitHub Actions

Copy `reviewer.py` and `requirements.txt` to `tools/llm-review/` in your repository and the
workflow to `.github/workflows/`. Use it only in a private repository with a self-hosted
runner that has Ollama installed. The review step has no token; only the post step gets
`GITHUB_TOKEN`, and it only creates a review with `event: COMMENT`. The workflow was not
run for the article; `test_reviewer.py` checks the request it sends against a local stub
server.
