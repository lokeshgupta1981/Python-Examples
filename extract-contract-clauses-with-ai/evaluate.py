"""Runs all 6 contracts twice (keyword-selected clauses and the whole contract)
and scores each field against labels.json, with and without the quote check.

Run: python evaluate.py [--model qwen2.5:7b] [--contracts C1 C3]
"""
import argparse
import json
import time
from datetime import date
from pathlib import Path

from ollama import Client

import extractor
from extractor import (deadlines, find_dates, normalize, parse_period, process,
                       current_term_end, last_notice_day)

REFERENCE_DATE = date(2026, 10, 26)   # the labels were worked out for this day
FIELDS = ["parties", "effective_date", "term", "renewal", "governing_law"]

def same_names(names, expected):
    return sorted(normalize(n).replace(",", "") for n in names) == \
           sorted(normalize(n).replace(",", "") for n in expected)

def raw_values(terms):
    """The model's values read with the same parsers, ignoring the quotes."""
    dates = find_dates(terms.effective_date.value)
    term = parse_period(terms.term.value)
    r = terms.renewal
    return {
        "parties": terms.parties.names,
        "effective_date": dates[0].isoformat() if dates else None,
        "term": term[1] if term and term[0] == "months" else None,
        "renewal": dict(auto_renews=r.auto_renews,
                        renewal_months=(parse_period(r.renewal_period) or (None, None))[1]
                        if r.auto_renews else None,
                        notice=parse_period(r.notice_period) if r.auto_renews else None),
        "governing_law": terms.governing_law.value,
    }

def correct(field, value, label):
    if value is None:
        return False
    if field == "parties":
        return same_names(value, label["parties"])
    if field == "effective_date":
        return value == label["effective_date"]
    if field == "term":
        return value == label["term_months"]
    if field == "renewal":
        notice = tuple(label["notice"]) if label["notice"] else None
        return (value["auto_renews"] == label["auto_renews"]
                and value["renewal_months"] == label["renewal_months"]
                and (tuple(value["notice"]) if value["notice"] else None) == notice)
    return label["governing_law"].lower() in (value or "").lower()

def raw_deadlines(values):
    try:
        start = date.fromisoformat(values["effective_date"])
        r = values["renewal"]
        end = current_term_end(start, values["term"], r["renewal_months"], REFERENCE_DATE)
        notice = last_notice_day(end, r["notice"]) if r["auto_renews"] else None
        return end.isoformat(), notice.isoformat() if notice else None
    except (TypeError, ValueError, KeyError):
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=extractor.MODEL)
    parser.add_argument("--contracts", nargs="*")
    args = parser.parse_args()
    extractor.MODEL = args.model
    labels = json.loads(Path("labels.json").read_text())
    ids = args.contracts or list(labels)
    client = Client(host="http://localhost:11434", timeout=600)
    results = {"model": args.model, "reference_date": REFERENCE_DATE.isoformat(), "modes": {}}
    for mode in ("keywords", "whole"):
        m = dict(fields=0, raw_correct=0, verified_correct=0, verified_wrong=0, to_person=0,
                 raw_deadlines=0, checked_deadlines=0, deadlines_to_person=0,
                 prompt_tokens=[], seconds=[], contracts={})
        for cid in ids:
            label = labels[cid]
            started = time.time()
            result = process(client, f"contracts/{cid}.pdf", REFERENCE_DATE, whole_contract=(mode == "whole"))
            m["seconds"].append(round(time.time() - started, 1))
            m["prompt_tokens"].append(result["response"].prompt_eval_count)
            raw, checked = raw_values(result["terms"]), result["checked"]
            detail = {}
            for field in FIELDS:
                m["fields"] += 1
                ok_raw = correct(field, raw[field], label)
                c = checked[field]
                value = c["value"]
                if field == "renewal" and value:
                    value = dict(value, notice=list(value["notice"]) if value["notice"] else None)
                ok_checked = c["status"] == "verified" and correct(field, value, label)
                m["raw_correct"] += ok_raw
                if c["status"] == "verified":
                    m["verified_correct" if ok_checked else "verified_wrong"] += 1
                else:
                    m["to_person"] += 1
                detail[field] = dict(raw_correct=ok_raw, status=c["status"], reason=c.get("reason", ""),
                                     quote=c["quote"])
            expected = (label["term_end"], label["notice_deadline"])
            m["raw_deadlines"] += raw_deadlines(raw) == expected
            rows, _ = deadlines(cid, checked, REFERENCE_DATE)
            if rows:
                got = {r["kind"]: r["date"].isoformat() for r in rows}
                m["checked_deadlines"] += (got.get("term-end"), got.get("notice-deadline")) == expected
            else:
                m["deadlines_to_person"] += 1
            m["contracts"][cid] = dict(clauses=[s.number for s in result["chosen"]], fields=detail,
                                       prompt_tokens=m["prompt_tokens"][-1], seconds=m["seconds"][-1])
            print(mode, cid, m["prompt_tokens"][-1], "prompt tokens", m["seconds"][-1], "s",
                  {f: (d["raw_correct"], d["status"]) for f, d in detail.items()}, flush=True)
        n = len(ids)
        print(f"\n{mode}: fields correct as returned {m['raw_correct']} of {m['fields']}, "
              f"verified and correct {m['verified_correct']}, verified but wrong {m['verified_wrong']}, "
              f"sent to a person {m['to_person']}")
        print(f"{mode}: deadlines correct as returned {m['raw_deadlines']} of {n}, after the check "
              f"{m['checked_deadlines']} of {n} ({m['deadlines_to_person']} sent to a person)")
        print(f"{mode}: average prompt tokens {sum(m['prompt_tokens']) / n:.0f}, "
              f"average seconds per contract {sum(m['seconds']) / n:.1f}\n")
        results["modes"][mode] = m
    Path("results.json").write_text(json.dumps(results, indent=2, default=str))

if __name__ == "__main__":
    main()
