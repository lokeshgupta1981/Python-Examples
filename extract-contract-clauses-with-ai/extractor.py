"""Extract key clauses and dates from contracts with a local Ollama model.

The model only finds values and quotes them. Plain code checks every quote
against the contract, calculates the renewal deadlines, writes them to a
calendar file and sends every failed check to review.csv.

Run: python extractor.py [contracts/C1.pdf ...] [--model qwen2.5:7b]
"""
import argparse
import calendar
import csv
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from icalendar import Alarm, Calendar, Event
from ollama import Client
from pydantic import BaseModel, Field
from pypdf import PdfReader

# ---------------------------------------------------------------------------
# Step 1: read pages and split into clauses
# ---------------------------------------------------------------------------

@dataclass
class Section:
    number: str
    title: str
    page: int
    text: str

HEADING = re.compile(r"^(\d+)\.\s+([A-Z][A-Za-z ,&-]+)$")
CLAUSE = re.compile(r"^(\d+\.\d+)\s+(.*)")

def load_pages(path):
    return [page.extract_text() or "" for page in PdfReader(path).pages]

def load_sections(pages):
    sections = [Section("0", "Preamble", 1, "")]
    title = "Preamble"
    for page_no, text in enumerate(pages, start=1):
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if heading := HEADING.match(line):
                title = heading.group(2)
            elif clause := CLAUSE.match(line):
                sections.append(Section(clause.group(1), title, page_no, clause.group(2)))
            else:
                last = sections[-1]
                last.text = f"{last.text} {line}".strip()
    return sections

# ---------------------------------------------------------------------------
# Step 2: the fields as a Pydantic model
# ---------------------------------------------------------------------------

class TextField(BaseModel):
    value: str | None = Field(description="The value as written, or null")
    quote: str | None = Field(description="The sentence that states it, copied exactly")

class Parties(BaseModel):
    names: list[str] = Field(max_length=4, description="Full legal names")
    quote: str | None

class Renewal(BaseModel):
    auto_renews: bool
    renewal_period: str | None = Field(description="Length of each renewal, or null")
    notice_period: str | None = Field(description="Notice to stop renewal, or null")
    quote: str | None

class ContractTerms(BaseModel):
    parties: Parties
    effective_date: TextField
    term: TextField
    renewal: Renewal
    governing_law: TextField

# ---------------------------------------------------------------------------
# Step 3: candidate clauses for each field
# ---------------------------------------------------------------------------

KEYWORDS = {
    "effective_date": ["effective", "takes effect", "starts on", "as of", "later of"],
    "term": ["initial term", "term of", "continues for"],
    "renewal": ["renew"],
    "governing_law": ["governed by", "govern", "laws of"],
}

def score(section, words):
    text = section.text.lower()
    return sum(text.count(w) for w in words)

def find_candidates(sections, per_field=2):
    chosen = {"0"}
    for words in KEYWORDS.values():
        ranked = sorted(sections, key=lambda s: score(s, words), reverse=True)
        chosen.update(s.number for s in ranked[:per_field] if score(s, words) > 0)
    return [s for s in sections if s.number in chosen]

def as_context(sections):
    return "\n".join(f"[{s.number}] {s.text}" for s in sections)

# ---------------------------------------------------------------------------
# Step 4: extract each field with its source quote
# ---------------------------------------------------------------------------

MODEL = "qwen2.5:7b"

SYSTEM = """You read contract clauses and extract five terms.
Rules:
- Use only the clauses given.
- For each term, copy into "quote" the one sentence that states it, word for word.
- If the clauses don't state a term, set its value and quote to null.
- effective_date: the date the agreement takes effect, as written.
- term: the length of the initial term, as written, for example "12 months".
- renewal: whether it renews automatically, the length of each renewal, and the
  notice needed to stop the renewal (not notice for other purposes).
- governing_law: the state, province or country whose laws govern the agreement."""

def extract(client, context):
    response = client.chat(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": context}],
        format=ContractTerms.model_json_schema(),
        options={"temperature": 0, "num_predict": 600, "seed": 7},
    )
    return ContractTerms.model_validate_json(response.message.content), response

# ---------------------------------------------------------------------------
# Step 5: verify quotes and values
# ---------------------------------------------------------------------------

def normalize(text):
    for mark in ("\u2018", "\u2019", "\u201c", "\u201d", '"', "'"):
        text = text.replace(mark, "")
    return " ".join(text.lower().split()).strip(" .,;:")

def find_page(quote, pages):
    target = normalize(quote or "")
    if len(target) < 10:
        return None
    for page_no, text in enumerate(pages, start=1):
        if target in normalize(text):
            return page_no
    # A sentence can run over a page break: search the joined text as well.
    starts, joined = [], ""
    for text in pages:
        starts.append(len(joined))
        joined += normalize(text) + " "
    at = joined.find(target)
    if at < 0:
        return None
    return max(i for i, start in enumerate(starts, start=1) if start <= at)

MONTHS = {name.lower(): i for i, name in enumerate(calendar.month_name) if name}
MONTH_RE = "|".join(MONTHS)
DATE_US = re.compile(rf"\b({MONTH_RE})\s+(\d{{1,2}}),\s*(\d{{4}})", re.I)
DATE_UK = re.compile(rf"\b(\d{{1,2}})\s+({MONTH_RE})\s+(\d{{4}})", re.I)
PERIOD = re.compile(r"(\d+)\)?[\s-]*(day|month|year)s?\b", re.I)

def find_dates(text):
    found = [date(int(y), MONTHS[m.lower()], int(d))
             for m, d, y in DATE_US.findall(text or "")]
    found += [date(int(y), MONTHS[m.lower()], int(d))
              for d, m, y in DATE_UK.findall(text or "")]
    return found

def find_periods(text):
    periods = []
    for n, unit in PERIOD.findall(text or ""):
        n, unit = int(n), unit.lower()
        if unit == "day":
            periods.append(("days", n))
        else:
            periods.append(("months", n * 12 if unit == "year" else n))
    return periods

def parse_period(text):
    periods = find_periods(text)
    return periods[0] if periods else None

def check(value, quote, pages, derive):
    if value is None and quote is None:
        return dict(status="not found", value=None, quote=None, page=None)
    if quote is None:
        return dict(status="needs review", reason="value without a quote",
                    value=None, quote=None, page=None)
    page = find_page(quote, pages)
    if page is None:
        return dict(status="needs review", reason="quote not in contract",
                    value=None, quote=quote, page=None)
    derived, reason = derive(value, quote)
    if derived is None:
        return dict(status="needs review", reason=reason, value=None,
                    quote=quote, page=page)
    return dict(status="verified", value=derived, quote=quote, page=page)

def signature_dates(pages):
    return [d for text in pages for line in text.splitlines()
            if line.strip().lower().startswith("signed") for d in find_dates(line)]

def check_parties(parties, pages):
    """The model returns names, not a value with a quote: look for each name instead."""
    text = normalize(" ".join(pages))
    names = [n for n in parties.names if n and normalize(n) in text]
    if not parties.names:
        return dict(status="not found", value=None, quote=None, page=None)
    if len(names) < 2:
        return dict(status="needs review", reason="fewer than two names in contract",
                    value=None, quote=parties.quote, page=None)
    return dict(status="verified", value=names, quote=parties.quote or "; ".join(names),
                page=find_page(names[0], pages))

def verify(terms, pages):
    def effective_date(value, quote):
        in_quote = find_dates(quote)
        if "later of" in quote.lower():
            signed = signature_dates(pages)
            if not in_quote or not signed:
                return None, "no dates for 'later of'"
            return max(in_quote + signed).isoformat(), ""
        values = find_dates(value)
        if not values or values[0] not in in_quote:
            return None, "date not in quote"
        return values[0].isoformat(), ""

    def term(value, quote):
        period = parse_period(value)
        if period is None or period[0] != "months":
            return None, "term is not a number of months"
        if period not in find_periods(quote):
            return None, "term not in quote"
        return period[1], ""

    r = terms.renewal

    def renewal(value, quote):
        if "renew" not in quote.lower():
            return None, "quote is not about renewal"
        if not r.auto_renews:
            return dict(auto_renews=False, renewal_months=None, notice=None), ""
        in_quote = find_periods(quote)
        notice = parse_period(r.notice_period)
        period = parse_period(r.renewal_period)
        if notice not in in_quote:
            return None, "notice period not in quote"
        if period not in in_quote or period[0] != "months":
            return None, "renewal period not in quote"
        return dict(auto_renews=True, renewal_months=period[1], notice=notice), ""

    def governing_law(value, quote):
        if normalize(value or "") and normalize(value) in normalize(quote):
            return value, ""
        return None, "law not in quote"

    e, t, g = terms.effective_date, terms.term, terms.governing_law
    renewal_value = None if r.quote is None and not r.auto_renews else r.auto_renews
    return {
        "parties": check_parties(terms.parties, pages),
        "effective_date": check(e.value, e.quote, pages, effective_date),
        "term": check(t.value, t.quote, pages, term),
        "renewal": check(renewal_value, r.quote, pages, renewal),
        "governing_law": check(g.value, g.quote, pages, governing_law),
    }

# ---------------------------------------------------------------------------
# Step 6: renewal and notice deadlines
# ---------------------------------------------------------------------------

def add_months(day, months):
    index = day.month - 1 + months
    year, month = day.year + index // 12, index % 12 + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))

def current_term_end(start, term_months, renewal_months, today):
    end = add_months(start, term_months) - timedelta(days=1)
    while renewal_months and end < today:
        end = add_months(end + timedelta(days=1), renewal_months) - timedelta(days=1)
    return end

def last_notice_day(term_end, notice):
    unit, n = notice
    if unit == "days":
        return term_end - timedelta(days=n)
    return add_months(term_end, -n)

def deadlines(contract, checked, today):
    needed = [checked[f] for f in ("effective_date", "term", "renewal")]
    if any(f["status"] != "verified" for f in needed):
        return [], "needs review: a date field is not verified"
    start = date.fromisoformat(checked["effective_date"]["value"])
    renewal = checked["renewal"]["value"]
    end = current_term_end(start, checked["term"]["value"],
                           renewal["renewal_months"], today)
    rows = [dict(contract=contract, kind="term-end", date=end,
                 summary=f"{contract}: term ends",
                 quote=checked["term"]["quote"], page=checked["term"]["page"])]
    if renewal["auto_renews"]:
        rows.append(dict(contract=contract, kind="notice-deadline",
                         date=last_notice_day(end, renewal["notice"]),
                         summary=f"{contract}: last day to send non-renewal notice",
                         quote=checked["renewal"]["quote"],
                         page=checked["renewal"]["page"]))
    return rows, ""

# ---------------------------------------------------------------------------
# Step 7: calendar and review list
# ---------------------------------------------------------------------------

def write_calendar(rows, path):
    cal = Calendar()
    cal.add("prodid", "-//VendorDesk//contract deadlines//EN")
    cal.add("version", "2.0")
    for row in rows:
        event = Event()
        event.add("uid", f"{row['contract']}-{row['kind']}@vendordesk.example")
        event.add("dtstamp", datetime.now(timezone.utc))
        event.add("dtstart", row["date"])
        event.add("summary", row["summary"])
        event.add("description", f"Page {row['page']}: {row['quote']}")
        alarm = Alarm()
        alarm.add("action", "DISPLAY")
        alarm.add("description", row["summary"])
        alarm.add("trigger", timedelta(days=-14))
        event.add_component(alarm)
        cal.add_component(event)
    Path(path).write_bytes(cal.to_ical())

def write_review(checked_by_contract, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        out = csv.writer(f)
        out.writerow(["contract", "field", "status", "reason", "page", "quote"])
        for contract, checked in checked_by_contract.items():
            for field, result in checked.items():
                if result["status"] != "verified":
                    out.writerow([contract, field, result["status"], result.get("reason", ""),
                                  result["page"] or "", result["quote"] or ""])

# ---------------------------------------------------------------------------
# Putting it together
# ---------------------------------------------------------------------------

def process(client, path, today, whole_contract=False):
    pages = load_pages(path)
    sections = load_sections(pages)
    chosen = sections if whole_contract else find_candidates(sections)
    terms, response = extract(client, as_context(chosen))
    checked = verify(terms, pages)
    return dict(pages=pages, chosen=chosen, terms=terms, response=response, checked=checked)

def main():
    global MODEL
    parser = argparse.ArgumentParser()
    parser.add_argument("pdfs", nargs="*")
    parser.add_argument("--model", default=MODEL)
    args = parser.parse_args()
    MODEL = args.model
    paths = args.pdfs or sorted(str(p) for p in Path("contracts").glob("*.pdf"))
    client = Client(host="http://localhost:11434", timeout=600)
    today = date.today()
    rows, checked_by_contract = [], {}
    for path in paths:
        contract = Path(path).stem
        result = process(client, path, today)
        checked_by_contract[contract] = result["checked"]
        found, reason = deadlines(contract, result["checked"], today)
        rows += found
        print(contract, "clauses sent:", [s.number for s in result["chosen"]])
        for field, r in result["checked"].items():
            print(f"  {field:15} {r['status']:13} {r['value']!r:.70} {r.get('reason', '')}")
        for row in found:
            print(f"  {row['kind']:15} {row['date']}")
        if reason:
            print(" ", reason)
        sys.stdout.flush()
    write_calendar(rows, "contract-deadlines.ics")
    write_review(checked_by_contract, "review.csv")
    print(f"{len(rows)} deadlines in contract-deadlines.ics, review list in review.csv")

if __name__ == "__main__":
    main()
