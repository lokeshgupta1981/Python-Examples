"""Runs every step except the model call, with hand-written model answers.

It checks the parsers, the quote check, the deadline rules and the calendar
file against labels.json, so it needs no Ollama server.
Run: python check_without_model.py
"""
import json
from datetime import date
from pathlib import Path

from extractor import (ContractTerms, deadlines, load_pages, verify, write_calendar,
                       write_review)

REFERENCE_DATE = date(2026, 10, 26)

# What a perfect model would return for each contract (value as written, exact quote).
ANSWERS = {
    "C1": ("Tallpine Hosting Inc.", "1 April 2026", 'This Agreement takes effect on 1 April 2026 (the "Effective Date").',
           "twelve (12) months", "The initial term is twelve (12) months from the Effective Date.",
           (True, "twelve (12) months", "sixty (60) days",
            "This Agreement renews automatically for successive periods of twelve (12) months unless either "
            "Party gives written notice of non-renewal at least sixty (60) days before the end of the "
            "then-current term."),
           "New York", "This Agreement is governed by the laws of the State of New York."),
    "C2": ("Ledgerwise Accounting Inc.", "January 15, 2026",
           'This Agreement takes effect on January 15, 2026 (the "Effective Date").',
           "eighteen (18) months", "The initial term of this Agreement is eighteen (18) months from the Effective Date.",
           (True, "twelve (12) months", "thirty (30) days",
            "After the initial term, this Agreement renews automatically for successive twelve (12) month "
            "periods unless either Party gives notice of non-renewal at least thirty (30) days before the end "
            "of the then-current term."),
           "Massachusetts", "This Agreement is governed by the laws of the Commonwealth of Massachusetts."),
    "C3": ("Brightway Cleaning Co.", "the later of 1 March 2026 and the date on which the last Party signs it",
           "This Agreement takes effect on the later of 1 March 2026 and the date on which the last Party "
           'signs it (the "Effective Date").',
           "twenty-four (24) months", "The initial term is twenty-four (24) months from the Effective Date.",
           (True, "twelve (12) months", "ninety (90) days",
            "This Agreement renews automatically for further periods of twelve (12) months unless a Party "
            "gives written notice of non-renewal at least ninety (90) days before the end of the then-current term."),
           "Illinois", "This Agreement is governed by the laws of the State of Illinois."),
    "C4": ("Northgate Payroll Inc.", "March 1, 2025", 'This Agreement takes effect on March 1, 2025 (the "Effective Date").',
           "twelve (12) months", "The initial term is twelve (12) months from the Effective Date.",
           (True, "twelve (12) months", "two (2) months",
            "This Agreement renews automatically for successive periods of twelve (12) months unless a Party "
            "gives written notice of non-renewal at least two (2) months before the end of the then-current term."),
           "Colorado", "This Agreement is governed by the laws of the State of Colorado."),
    "C5": ("Sentry Point Security Inc.", "1 October 2024", 'This Agreement takes effect on 1 October 2024 (the "Effective Date").',
           "thirty-six (36) months", "The initial term is thirty-six (36) months from the Effective Date.",
           (False, None, None,
            "This Agreement does not renew automatically, and any extension needs a new written agreement "
            "signed by both Parties."),
           "Ohio", "This Agreement is governed by the laws of the State of Ohio."),
    "C6": ("Redline Print Partners Inc.", "July 1, 2025",
           "This Agreement is dated May 20, 2025 and, for all print orders placed under it, takes effect on "
           'July 1, 2025 (the "Effective Date").',
           "twelve (12) months", "The initial term is twelve (12) months from the Effective Date.",
           (True, "twelve (12) months", "thirty (30) days",
            "Unless a Party gives written notice of non-renewal at least thirty (30) days before the end of the "
            "then-current term, this Agreement renews automatically for successive periods of twelve (12) months."),
           "Texas", "This Agreement is governed by the laws of the State of Texas, without regard to its "
                    "conflict of law rules."),
}

def terms_for(answer):
    provider, eff, eff_q, term, term_q, (auto, period, notice, ren_q), law, law_q = answer
    return ContractTerms.model_validate(dict(
        parties=dict(names=[provider, "Harbor Lane Studio LLC"], quote=None),
        effective_date=dict(value=eff, quote=eff_q),
        term=dict(value=term, quote=term_q),
        renewal=dict(auto_renews=auto, renewal_period=period, notice_period=notice, quote=ren_q),
        governing_law=dict(value=law, quote=law_q)))

def main():
    labels = json.loads(Path("labels.json").read_text())
    rows, checked_all, failures = [], {}, 0
    for cid, answer in ANSWERS.items():
        pages = load_pages(f"contracts/{cid}.pdf")
        checked = verify(terms_for(answer), pages)
        checked_all[cid] = checked
        found, reason = deadlines(cid, checked, REFERENCE_DATE)
        rows += found
        got = {r["kind"]: r["date"].isoformat() for r in found}
        expected = labels[cid]
        ok = (all(c["status"] == "verified" for c in checked.values())
              and got.get("term-end") == expected["term_end"]
              and got.get("notice-deadline") == expected["notice_deadline"])
        failures += not ok
        print(cid, "OK " if ok else "FAIL", checked["effective_date"]["value"], got, reason)
    # Two wrong answers that the check must stop: a quote that is not in the contract,
    # and a quote that does not contain the value.
    bad = terms_for(ANSWERS["C6"]).model_copy(deep=True)
    bad.effective_date.quote = 'The Agreement is dated May 20, 2025 and takes effect on July 1, 2025 (the "Effective Date").'
    status = verify(bad, load_pages("contracts/C6.pdf"))["effective_date"]
    print("shortened quote:", status["status"], "-", status["reason"])
    failures += status["reason"] != "quote not in contract"
    bad = terms_for(ANSWERS["C1"]).model_copy(deep=True)
    bad.effective_date.quote = "The Agreement is made between Tallpine Hosting Inc., a New York corporation"
    status = verify(bad, load_pages("contracts/C1.pdf"))["effective_date"]
    print("quote without the date:", status["status"], "-", status["reason"])
    failures += status["reason"] != "date not in quote"
    write_calendar(rows, "check-deadlines.ics")
    write_review(checked_all, "check-review.csv")
    print(f"{len(rows)} events written to check-deadlines.ics; {failures} failures")
    raise SystemExit(1 if failures else 0)

if __name__ == "__main__":
    main()
