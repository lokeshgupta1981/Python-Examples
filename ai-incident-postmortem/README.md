# AI Incident Postmortem Draft With Python

Example project for the howtodoinjava.com article
[How to Draft an AI Incident Postmortem With Python](https://howtodoinjava.com/ai/ai-incident-postmortem/).

## What it shows

Code merges a Slack channel export, alert events and a deploy log into one
numbered timeline, computes every time and duration, and masks names and
secrets. A local model on Ollama writes only the prose sections of a blameless
postmortem (summary, impact, root cause, contributing factors, action items) as
JSON that matches a pydantic schema. Code then checks every date, time,
duration and event id in the draft, flags blaming wording and vague action
items, and renders a Markdown draft for a person to review.

## Files

| File | What it does |
|---|---|
| `generate_incidents.py` | Writes the four sample incidents into `incidents/` (Slack export, `alerts.json`, `deploys.log`, `roles.json`) and `incidents/labels.json` |
| `postmortem.py` | Steps 1 to 8: load, timeline, facts, masking, prompt, schema, draft, checks, render |
| `postmortem.md.j2` | Jinja2 template of the Markdown draft |
| `evaluate.py` | Drafts each incident with and without the computed facts and scores the drafts |
| `rescore.py` | Re-checks the drafts saved in `results/` without calling the model |
| `test_checks.py` | Offline tests of the timeline, masking and checks (no model needed) |

## Versions

Python 3.12 or later (tested on 3.13), Ollama 0.40.x, `ollama` 0.6.3,
`pydantic` 2.14.1, `Jinja2` 3.1.6.

## How to run

```bash
ollama pull qwen2.5:7b
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python generate_incidents.py
python -m unittest test_checks                              # no model needed
python postmortem.py incidents/checkout-outage --dry-run    # prints the prompt
python postmortem.py incidents/checkout-outage              # writes postmortem-draft.md
python evaluate.py                                          # 4 incidents x 2 variants
python rescore.py                                           # re-check saved drafts
```

`postmortem.py` and `evaluate.py` take `--model` to try another Ollama model.
`rescore.py` also prints your own root-cause verdicts if you add a
`hand_check.json` such as `{"checkout-outage--facts": "Right"}`.

## Which model produced the article's numbers

All numbers and drafts in the article were measured by the author with
`qwen2.5:7b` on Ollama, on a shared 2-core CPU (170.9 to 428.1 seconds per
draft). The original eight drafts are not part of this folder, so a new run
gives different drafts.

The dry-run output and the offline tests reproduce the article exactly
(24 events, 5 masked for the checkout outage). A smoke test with the smaller
`qwen2.5:3b` ran the full pipeline: it stated the right 40-minute impact for the
checkout outage, but its root cause was only a list of event ids. Use 7b or
larger for useful prose.
