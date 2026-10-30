"""Writes 6 fictional service agreements as PDF files and their expected answers.

All companies, people and contracts are invented for this example.
Run: python make_contracts.py
"""
import json
from pathlib import Path

from fpdf import FPDF

CLIENT = "Harbor Lane Studio LLC"
PAGE_BREAK = "<page>"

def preamble(provider, kind):
    return (f'The Agreement is made between {provider}, a {kind} ("Provider"), and {CLIENT}, '
            f'a limited liability company organized under the laws of Delaware ("Client"), '
            f'each a "Party".')

# Clauses that only add realistic length. None of them contains a search keyword.
FILLER = {
    "Fees": ["Client pays the monthly fee shown in the order form, invoiced in advance.",
             "Invoices are due within thirty (30) days of the invoice date."],
    "Payment": ["Late amounts bear interest at one percent per month until paid.",
                "Client pays by bank transfer to the account named on the invoice."],
    "Taxes": ["Fees exclude sales tax, which Provider adds to each invoice where required."],
    "Confidentiality": ["Each Party keeps the other Party's business information confidential.",
                        "This duty does not cover information that is already public."],
    "Data Protection": ["Provider processes Client data only to perform the services.",
                        "Provider reports any data breach to Client within seventy-two hours."],
    "Personnel": ["Provider assigns trained staff and replaces anyone Client reasonably rejects."],
    "Subcontractors": ["Provider may use subcontractors and stays responsible for their work."],
    "Insurance": ["Provider keeps general liability insurance with a limit of USD 1,000,000.",
                  "Provider shows proof of insurance when Client asks for it."],
    "Warranties": ["Provider performs the services with reasonable skill and care.",
                   "Client provides accurate information and timely access."],
    "Liability": ["Neither Party is liable for indirect or consequential losses.",
                  "Each Party's total liability is limited to the fees paid in the prior year."],
    "Indemnity": ["Provider defends Client against claims that the services infringe a third-party right."],
    "Intellectual Property": ["Each Party keeps the rights it held before signing.",
                              "Client owns the deliverables once it has paid for them."],
    "Force Majeure": ["Neither Party is liable for delays caused by events outside its control."],
    "Termination": ["Either Party may end this Agreement for material breach not cured within thirty (30) days.",
                    "Client pays for services performed up to the end date."],
    "Disputes": ["The Parties first try to settle any dispute through senior managers."],
    "Audit": ["Client may review Provider's records for the services once per calendar year."],
    "Assignment": ["Neither Party may assign this Agreement without the other Party's written consent."],
    "Notices": ["Notices must be in writing and sent to the addresses above."],
    "Entire Agreement": ["This document and its order forms are the whole agreement of the Parties."],
}

def fill(*names):
    return [(n, FILLER[n]) for n in names]

CONTRACTS = {
    "C1": dict(
        title="HOSTING SERVICES AGREEMENT",
        preamble=preamble("Tallpine Hosting Inc.", "New York corporation"),
        body=[
            ("Services", ["Provider hosts Client's website and backups on servers that Provider manages.",
                          "Provider keeps the service available at least 99.5 percent of each month."]),
            ("Term", ['This Agreement takes effect on 1 April 2026 (the "Effective Date").',
                      "The initial term is twelve (12) months from the Effective Date."]),
            ("Renewal", ["Client may order more storage at any time through the order form.",
                         "This Agreement renews automatically for successive periods of twelve (12) months "
                         "unless either Party gives written notice of non-renewal at least sixty (60) days "
                         "before the end of the then-current term."]),
            *fill("Fees", "Confidentiality"),
            PAGE_BREAK,
            *fill("Liability", "Termination"),
            ("General", ["This Agreement is governed by the laws of the State of New York.",
                         "Notices must be in writing and sent to the addresses above."]),
        ],
        signatures=[("Provider", "Dana Whitlock", "18 March 2026"), ("Client", "Maya Ortiz", "20 March 2026")],
        labels=dict(parties=["Tallpine Hosting Inc.", CLIENT], effective_date="2026-04-01", term_months=12,
                    auto_renews=True, renewal_months=12, notice=["days", 60], governing_law="New York",
                    term_end="2027-03-31", notice_deadline="2027-01-30"),
    ),
    "C2": dict(
        title="BOOKKEEPING SERVICES AGREEMENT",
        preamble=preamble("Ledgerwise Accounting Inc.", "Massachusetts corporation"),
        body=[
            ("Services", ["Provider keeps Client's books and prepares a monthly report.",
                          "Client sends bank statements and receipts by the fifth working day of each month."]),
            ("Term", ['This Agreement takes effect on January 15, 2026 (the "Effective Date").',
                      "The initial term of this Agreement is eighteen (18) months from the Effective Date."]),
            ("Fees", ["Client pays a monthly fee of USD 650, invoiced in advance.",
                      "Provider may change its fees by giving Client ninety (90) days' written notice."]),
            *fill("Confidentiality", "Data Protection"),
            PAGE_BREAK,
            ("Renewal", ["After the initial term, this Agreement renews automatically for successive twelve (12) "
                         "month periods unless either Party gives notice of non-renewal at least thirty (30) "
                         "days before the end of the then-current term."]),
            *fill("Liability", "Termination", "Assignment"),
            ("General", ["This Agreement is governed by the laws of the Commonwealth of Massachusetts.",
                         "This document and its order forms are the whole agreement of the Parties."]),
        ],
        signatures=[("Provider", "Owen Brandt", "8 January 2026"), ("Client", "Maya Ortiz", "12 January 2026")],
        labels=dict(parties=["Ledgerwise Accounting Inc.", CLIENT], effective_date="2026-01-15", term_months=18,
                    auto_renews=True, renewal_months=12, notice=["days", 30], governing_law="Massachusetts",
                    term_end="2027-07-14", notice_deadline="2027-06-14"),
    ),
    "C3": dict(
        title="CLEANING SERVICES AGREEMENT",
        preamble=preamble("Brightway Cleaning Co.", "Illinois corporation"),
        body=[
            ("Services", ["Provider cleans Client's studio three evenings per week.",
                          "Provider brings its own equipment and supplies."]),
            ("Term", ["This Agreement takes effect on the later of 1 March 2026 and the date on which "
                      'the last Party signs it (the "Effective Date").',
                      "The initial term is twenty-four (24) months from the Effective Date."]),
            *fill("Fees", "Insurance"),
            PAGE_BREAK,
            ("Renewal", ["This Agreement renews automatically for further periods of twelve (12) months unless "
                         "a Party gives written notice of non-renewal at least ninety (90) days before the end "
                         "of the then-current term."]),
            *fill("Personnel", "Liability", "Termination"),
            ("General", ["This Agreement is governed by the laws of the State of Illinois."]),
        ],
        signatures=[("Provider", "Luis Ferreira", "4 March 2026"), ("Client", "Maya Ortiz", "9 March 2026")],
        labels=dict(parties=["Brightway Cleaning Co.", CLIENT], effective_date="2026-03-09", term_months=24,
                    auto_renews=True, renewal_months=12, notice=["days", 90], governing_law="Illinois",
                    term_end="2028-03-08", notice_deadline="2027-12-09"),
    ),
    "C4": dict(
        title="PAYROLL SERVICES AGREEMENT",
        preamble=preamble("Northgate Payroll Inc.", "Colorado corporation"),
        body=[
            ("Services", ["Provider runs Client's payroll twice per month and files payroll tax returns.",
                          "Client confirms hours and salary changes two working days before each pay date."]),
            ("Term", ['This Agreement takes effect on March 1, 2025 (the "Effective Date").',
                      "The initial term is twelve (12) months from the Effective Date."]),
            *fill("Fees", "Data Protection"),
            PAGE_BREAK,
            ("Renewal", ["This Agreement renews automatically for successive periods of twelve (12) months "
                         "unless a Party gives written notice of non-renewal at least two (2) months before "
                         "the end of the then-current term."]),
            *fill("Liability", "Termination", "Notices"),
            ("General", ["This Agreement is governed by the laws of the State of Colorado."]),
        ],
        signatures=[("Provider", "Priya Natarajan", "20 February 2025"), ("Client", "Maya Ortiz", "24 February 2025")],
        labels=dict(parties=["Northgate Payroll Inc.", CLIENT], effective_date="2025-03-01", term_months=12,
                    auto_renews=True, renewal_months=12, notice=["months", 2], governing_law="Colorado",
                    term_end="2027-02-28", notice_deadline="2026-12-28"),
    ),
    "C5": dict(
        title="ALARM MONITORING AGREEMENT",
        preamble=preamble("Sentry Point Security Inc.", "Ohio corporation"),
        body=[
            ("Services", ["Provider monitors the alarm system at Client's studio at all hours.",
                          "Provider calls the contacts on Client's list when an alarm is raised."]),
            ("Term", ['This Agreement takes effect on 1 October 2024 (the "Effective Date").',
                      "The initial term is thirty-six (36) months from the Effective Date."]),
            *fill("Fees", "Liability"),
            PAGE_BREAK,
            ("Expiry", ["This Agreement does not renew automatically, and any extension needs a new written "
                        "agreement signed by both Parties."]),
            *fill("Termination", "Assignment"),
            ("General", ["This Agreement is governed by the laws of the State of Ohio."]),
        ],
        signatures=[("Provider", "Grant Holloway", "23 September 2024"), ("Client", "Maya Ortiz", "25 September 2024")],
        labels=dict(parties=["Sentry Point Security Inc.", CLIENT], effective_date="2024-10-01", term_months=36,
                    auto_renews=False, renewal_months=None, notice=None, governing_law="Ohio",
                    term_end="2027-09-30", notice_deadline=None),
    ),
    "C6": dict(
        title="PRINT SERVICES AGREEMENT",
        preamble=preamble("Redline Print Partners Inc.", "Texas corporation"),
        body=[
            ("Services", ["Provider prints brochures, posters and business cards from Client's files.",
                          "Provider sends a proof for each order before printing."]),
            ("Term", ["This Agreement is dated May 20, 2025 and, for all print orders placed under it, "
                      'takes effect on July 1, 2025 (the "Effective Date"). The initial term is twelve (12) '
                      "months from the Effective Date."]),
            ("Orders", ["Client places orders through Provider's online portal, and Provider confirms "
                        "each order within one working day."]),
            ("Delivery", ["Provider delivers orders to Client's studio at no extra charge."]),
            *fill("Fees", "Payment"),
            PAGE_BREAK,
            *fill("Taxes", "Warranties"),
            ("Quality", ["Client reports printing defects within ten (10) working days of delivery, and "
                         "Provider reprints defective items at its own cost."]),
            ("Price Changes", ["A price change becomes effective thirty (30) days after Provider gives written "
                               "notice and applies for the rest of the term of this Agreement."]),
            *fill("Confidentiality", "Data Protection"),
            PAGE_BREAK,
            *fill("Intellectual Property", "Liability", "Indemnity", "Insurance", "Force Majeure",
                  "Subcontractors"),
            PAGE_BREAK,
            *fill("Termination", "Disputes"),
            ("General", ["Notices must be in writing and sent to the addresses above.",
                         "Neither Party may assign this Agreement without the other Party's written consent.",
                         "Unless a Party gives written notice of non-renewal at least thirty (30) days before "
                         "the end of the then-current term, this Agreement renews automatically for successive "
                         "periods of twelve (12) months.",
                         "This Agreement is governed by the laws of the State of Texas, without regard to its "
                         "conflict of law rules.",
                         "If a court finds any clause unenforceable, the other clauses stay in force.",
                         "This document and its order forms are the whole agreement of the Parties."]),
        ],
        signatures=[("Provider", "Rosa Delgado", "20 May 2025"), ("Client", "Maya Ortiz", "20 May 2025")],
        labels=dict(parties=["Redline Print Partners Inc.", CLIENT], effective_date="2025-07-01", term_months=12,
                    auto_renews=True, renewal_months=12, notice=["days", 30], governing_law="Texas",
                    term_end="2027-06-30", notice_deadline="2027-05-31"),
    ),
}

def write_pdf(contract, path):
    pdf = FPDF(format="Letter")
    pdf.set_margins(25, 25, 25)
    pdf.set_auto_page_break(True, margin=25)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.multi_cell(0, 8, contract["title"], new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 6, contract["preamble"], new_x="LMARGIN", new_y="NEXT")
    number = 0
    for item in contract["body"]:
        if item == PAGE_BREAK:
            pdf.add_page()
            continue
        title, clauses = item
        number += 1
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 6, f"{number}. {title}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        for i, text in enumerate(clauses, start=1):
            pdf.multi_cell(0, 6, f"{number}.{i} {text}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    for role, name, day in contract["signatures"]:
        pdf.multi_cell(0, 6, f"Signed for {role}: {name}, {day}", new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(path))

def main():
    out = Path("contracts")
    out.mkdir(exist_ok=True)
    labels = {}
    for cid, contract in CONTRACTS.items():
        write_pdf(contract, out / f"{cid}.pdf")
        labels[cid] = contract["labels"]
    Path("labels.json").write_text(json.dumps(labels, indent=2))
    print(f"wrote {len(CONTRACTS)} contracts to {out}/ and labels.json")

if __name__ == "__main__":
    main()
