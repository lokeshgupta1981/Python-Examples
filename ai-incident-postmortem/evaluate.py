"""Drafts each sample incident twice, with and without the computed facts, and scores the drafts.

    python evaluate.py                    # qwen2.5:7b, all incidents
    python evaluate.py --model qwen2.5:3b --only checkout-outage
"""
import argparse
import json
import re
from pathlib import Path

import postmortem as pm

HERE = Path(__file__).parent
VARIANTS = {"facts": True, "timeline only": False}


def rubric(root_cause, keywords):
    """Passes when the root cause contains a word from each keyword list."""
    text = root_cause.lower()
    return all(any(re.search(rf"\b{re.escape(k)}\b", text) for k in group) for group in keywords)


def score(name, variant, narrative, events, facts, names, keywords):
    report = pm.check_numbers(narrative, events, facts)
    flags = pm.check_flags(report) + pm.flag_wording(narrative, names)
    return {"incident": name, "variant": variant, "report": report, "flags": flags,
            "rubric": rubric(narrative.root_cause, keywords)}


def print_row(r, hand=None):
    rep = r["report"]
    stated = "/".join(map(str, rep["impact_stated"])) or "not stated"
    extra = f" | {hand}" if hand else ""
    print(f"| {r['incident']} | {r['variant']} | {len(rep['wrong_durations'])} | "
          f"{rep['impact_minutes']} / {stated} | {'pass' if r['rubric'] else 'fail'}{extra} |")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=pm.MODEL)
    parser.add_argument("--only", help="run one incident")
    args = parser.parse_args()
    pm.MODEL = args.model

    labels = json.loads((HERE / "incidents" / "labels.json").read_text())
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    print("| Incident | Variant | Wrong durations | Impact minutes (true / stated) | Keyword rubric |")
    print("|---|---|---|---|---|")
    for name, label in labels.items():
        if args.only and name != args.only:
            continue
        events, facts, names, _ = pm.prepare(HERE / "incidents" / name)
        for variant, with_facts in VARIANTS.items():
            system, user = pm.build_prompt(name, facts, events, with_facts)
            narrative, seconds, response = pm.draft(system, user)
            r = score(name, variant, narrative, events, facts, names, label["keywords"])
            r.update(model=pm.MODEL, seconds=seconds, narrative=narrative.model_dump(),
                     output_tokens=response.eval_count)
            slug = f"{name}--{variant.replace(' ', '-')}"
            (out / f"{slug}.json").write_text(json.dumps(r, indent=2))
            (out / f"{slug}.md").write_text(pm.render(name, facts, events, narrative, r["flags"]))
            print_row(r)


if __name__ == "__main__":
    main()
