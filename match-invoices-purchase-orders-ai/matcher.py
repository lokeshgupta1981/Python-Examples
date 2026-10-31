"""Two-way and three-way invoice matching with plain rules.

The model is never called from this file. A pairer (see pairers.py) may
suggest a PO line for an invoice line without an item code, and the rules
here decide whether to accept it.
"""
import json
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path

import pandas as pd
from pydantic import BaseModel

PRICE_TOLERANCE = Decimal("0.02")  # 2% above the PO price, an example value
QTY_TOLERANCE = 0                  # no extra units
SANITY_PRICE_LIMIT = Decimal("0.25")  # a suggested pair more than 25% off is rejected
CENT = Decimal("0.01")


class POLine(BaseModel):
    po_line_id: str
    sku: str
    description: str
    unit: str
    quantity: int
    unit_price: Decimal


class PurchaseOrder(BaseModel):
    po_number: str
    vendor_name: str
    currency: str
    lines: list[POLine]


class GoodsReceipt(BaseModel):
    grn_number: str
    po_number: str
    received: dict[str, int]  # po_line_id -> quantity received


class InvoiceLine(BaseModel):
    line_no: int
    item_code: str | None
    description: str
    quantity: int
    unit: str
    unit_price: Decimal
    amount: Decimal


class Invoice(BaseModel):
    vendor_name: str
    invoice_number: str
    invoice_date: date
    po_number: str
    currency: str
    line_items: list[InvoiceLine]
    subtotal: Decimal
    tax: Decimal
    total: Decimal


@dataclass
class Exception_:
    code: str
    line_no: int | None
    detail: str


@dataclass
class MatchResult:
    invoice_number: str
    decision: str = "approve"
    exceptions: list[Exception_] = field(default_factory=list)
    pairs: dict[int, str] = field(default_factory=dict)      # invoice line_no -> po_line_id
    paired_by: dict[int, str] = field(default_factory=dict)  # line_no -> "item code", "rapidfuzz", model name
    model_calls: int = 0

    def flag(self, code, line_no=None, detail=""):
        self.exceptions.append(Exception_(code, line_no, detail))
        self.decision = "hold"


def load_data(folder: Path):
    """Reads the CSV files into typed purchase orders and goods receipts."""
    lines = pd.read_csv(folder / "po_lines.csv", dtype={"unit_price": str})
    pos = {}
    for row in pd.read_csv(folder / "pos.csv").itertuples():
        po_lines = lines[lines.po_number == row.po_number]
        pos[row.po_number] = PurchaseOrder(
            po_number=row.po_number, vendor_name=row.vendor_name, currency=row.currency,
            lines=po_lines.drop(columns="po_number").to_dict("records"))

    receipts = {}
    for (grn, po_number), group in pd.read_csv(folder / "receipts.csv").groupby(["grn_number", "po_number"]):
        receipts[po_number] = GoodsReceipt(
            grn_number=grn, po_number=po_number,
            received=dict(zip(group.po_line_id, group.quantity_received)))
    return pos, receipts


def load_invoice(path: Path) -> Invoice:
    return Invoice.model_validate_json(path.read_text())


def match_invoice(inv: Invoice, pos, receipts, seen: set, mode="three-way", pairer=None) -> MatchResult:
    result = MatchResult(inv.invoice_number)

    # Step 2: header checks
    key = (inv.vendor_name, inv.invoice_number)
    if key in seen:
        result.flag("DUPLICATE_INVOICE", detail=f"{inv.invoice_number} from {inv.vendor_name} was already processed")
        return result
    seen.add(key)

    po = pos.get(inv.po_number)
    if po is None:
        result.flag("PO_NOT_FOUND", detail=f"no purchase order {inv.po_number}")
        return result
    if inv.vendor_name != po.vendor_name:
        result.flag("VENDOR_MISMATCH", detail=f"invoice vendor {inv.vendor_name}, PO vendor {po.vendor_name}")
    if inv.currency != po.currency:
        result.flag("CURRENCY_MISMATCH", detail=f"invoice {inv.currency}, PO {po.currency}")
    receipt = receipts.get(po.po_number)
    if mode == "three-way" and receipt is None:
        result.flag("NO_RECEIPT", detail=f"no goods receipt for {po.po_number}")
    check_totals(inv, result)

    # Step 3: pair lines by item code
    by_id = {line.po_line_id: line for line in po.lines}
    used = set()
    unpaired = []
    for line in inv.line_items:
        po_line = next((p for p in po.lines if p.sku == line.item_code and p.po_line_id not in used), None)
        if po_line:
            result.pairs[line.line_no] = po_line.po_line_id
            result.paired_by[line.line_no] = "item code"
            used.add(po_line.po_line_id)
        else:
            unpaired.append(line)

    # Steps 4 and 5: ask the pairer, then check its suggestion
    for line in unpaired:
        free = [p for p in po.lines if p.po_line_id not in used]
        suggestion = None
        if pairer and free:
            suggestion, calls = pairer(line, free)
            result.model_calls += calls
        reason = accept_pair(line, by_id.get(suggestion), used)
        if reason is None:
            result.pairs[line.line_no] = suggestion
            result.paired_by[line.line_no] = getattr(pairer, "label", "pairer")
            used.add(suggestion)
        else:
            result.flag("UNMATCHED_LINE", line.line_no, f"'{line.description}': {reason}")

    # Step 6: price and quantity tolerances
    for line in inv.line_items:
        po_line = by_id.get(result.pairs.get(line.line_no))
        if po_line is None:
            continue
        max_price = (po_line.unit_price * (1 + PRICE_TOLERANCE)).quantize(CENT)
        if line.unit_price > max_price:
            result.flag("PRICE_VARIANCE", line.line_no,
                        f"unit price {line.unit_price} vs PO {po_line.unit_price} (max {max_price})")
        if mode == "two-way":
            allowed, what = po_line.quantity, "ordered"
        elif receipt is not None:
            allowed, what = receipt.received.get(po_line.po_line_id, 0), "received"
        else:
            continue
        if line.quantity > allowed + QTY_TOLERANCE:
            code = "QTY_OVER_RECEIVED" if what == "received" else "QTY_OVER_ORDERED"
            result.flag(code, line.line_no, f"billed {line.quantity}, {what} {allowed}")
    return result


def accept_pair(line: InvoiceLine, po_line: POLine | None, used: set) -> str | None:
    """Returns None when the suggested pair is acceptable, else the reason to reject it."""
    if po_line is None:
        return "no PO line suggested"
    if po_line.po_line_id in used:
        return f"{po_line.po_line_id} is already paired"
    if line.unit != po_line.unit:
        return f"unit '{line.unit}' differs from PO unit '{po_line.unit}'"
    if abs(line.unit_price - po_line.unit_price) > po_line.unit_price * SANITY_PRICE_LIMIT:
        return f"price {line.unit_price} is far from PO price {po_line.unit_price}"
    return None


def check_totals(inv: Invoice, result: MatchResult):
    for line in inv.line_items:
        if (line.quantity * line.unit_price).quantize(CENT) != line.amount.quantize(CENT):
            result.flag("LINE_AMOUNT_MISMATCH", line.line_no, f"{line.quantity} x {line.unit_price} != {line.amount}")
    if sum(l.amount for l in inv.line_items) != inv.subtotal or inv.subtotal + inv.tax != inv.total:
        result.flag("TOTAL_MISMATCH", detail=f"subtotal {inv.subtotal}, tax {inv.tax}, total {inv.total}")


if __name__ == "__main__":
    import sys
    data = Path(__file__).parent / "data"
    pos, receipts = load_data(data)
    seen = set()
    for path in sorted((data / "invoices").glob("*.json")):
        r = match_invoice(load_invoice(path), pos, receipts, seen, mode=(sys.argv[1] if len(sys.argv) > 1 else "three-way"))
        print(path.name, r.decision, [e.code for e in r.exceptions])
