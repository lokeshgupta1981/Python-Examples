# Weekly Sales Report With AI

Example project for the howtodoinjava.com article
"How to Turn Sales Data Into a Weekly Written Report With AI".

pandas computes every number of a weekly sales report, a local Ollama model writes only the
sentences around a fact table of those numbers, and code checks every number in the model's reply
before a Jinja2 template renders the report as Markdown, HTML and PDF.

## What is in the folder

| File | What it does |
|---|---|
| `make_data.py` | Writes `orders.csv` (12 weeks of order lines for the fictional shop BeanBox, 2026-W32 to 2026-W43) and `planted_events.json` (three planted stories) |
| `report.py` | The whole pipeline: weekly numbers, fact table, prompt, model call, number check with retries and fallback, rendering |
| `templates/report.md.j2` | The report template; the numbers table is filled from the facts, never from the model |
| `evaluate.py` | Compares raw daily rows, the first fact table and the final fact table for 2026-W40 to 2026-W43 and writes `results/` and an empty `hand_review.json` to fill in by hand |
| `schedule_report.py` | Runs `report.py` every Monday at 07:00 with APScheduler; `--next` prints the next fire times |
| `test_report.py` | Tests for everything that doesn't need the model |

## Versions

- Python 3.12 or later (tested with Python 3.13)
- Ollama 0.40.11 with `qwen2.5:7b`
- The Python packages pinned in `requirements.txt`
- WeasyPrint needs Pango from the operating system. On Ubuntu:
  `sudo apt install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libharfbuzz-subset0`

## How to run

```bash
ollama pull qwen2.5:7b
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python make_data.py                 # orders.csv and planted_events.json
python -m pytest -q                 # no model needed
python report.py --week 2026-W43    # reports/report-2026-W43.pdf, .md, .html and log
python evaluate.py                  # 9 reports, about 11 model calls
python schedule_report.py --next    # next Monday fire times
```

Use `--model` on `report.py` or `evaluate.py` to try another Ollama model.

A cron line that does the same as `schedule_report.py`:

```bash
0 7 * * 1 cd /path/to/weekly-sales-report-ai && .venv/bin/python report.py --week $(date -d "7 days ago" +\%G-W\%V) >> report.log 2>&1
```

## Which model produced the article's numbers

All numbers and model results in the article (the weekly table, the 31 facts for 2026-W43, the
evaluation table, the 129 to 402 seconds per call) were measured by the author with
**`qwen2.5:7b`** on the author's original data set. That data set and the original code were not
kept. This folder rebuilds the project from the article's code; `make_data.py` here plants the same
three stories, but its random rows differ, so it writes 5,419 lines instead of 5,293 and its weekly
totals differ from the article. The 2026-W43 fact table here has 33 facts instead of 31, because the
new Cold Brew Kit is not among the two smallest products and is added on its own.

The model parts were smoke-tested with `qwen2.5:3b` (Ollama, 2 vCPU, CPU only, shared server) only
to confirm that the code runs end to end: `python report.py --week 2026-W43 --model qwen2.5:3b`
made 3 model calls in 364 seconds, the check blocked a cut-off summary and two numbers that were not
in the fact table, two lines ended as "[check]" fallbacks, and the PDF rendered with the chart.
Those 3b results are not the article's numbers. `evaluate.py` was not run with a model in this rebuild.
