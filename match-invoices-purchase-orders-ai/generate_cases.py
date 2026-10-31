"""Writes 40 synthetic accounts-payable cases with planted problems.

Output (in data/):
  pos.csv          one row per purchase order (header)
  po_lines.csv     one row per ordered line
  receipts.csv     one row per received line (goods receipt notes)
  invoices/*.json  one extracted invoice per file
  labels.csv       expected decision and exception codes per invoice
  line_labels.csv  expected PO line for every invoice line without an item code
"""
import csv
import json
import random
import shutil
from pathlib import Path

from faker import Faker

SEED = 42
OUT = Path(__file__).parent / "data"

# sku, PO wording, supplier wording, unit, unit price
CATALOG = [
    ("TN-26A", "Toner 26A Black, 2-pack", "Black toner cartridge 26A (pack of 2)", "pack", 164.00),
    ("PAP-A4-80", "Copy paper A4 80gsm, box of 5 reams", "A4 multipurpose paper 80 g/m2, 5 x 500 sheets", "box", 27.50),
    ("PEN-BLK-50", "Ballpoint pen black, box of 50", "Black ballpoint pens (50 pcs)", "box", 12.90),
    ("BAT-AA-24", "Batteries AA alkaline, 24-pack", "Alkaline AA cells x24", "pack", 15.80),
    ("TN-410A-K", "Toner 410A Black", "410A black LaserJet toner", "each", 96.00),
    ("STP-HD", "Stapler, heavy duty", "Heavy-duty desk stapler", "each", 21.40),
    ("ENV-C4", "Envelopes C4 white, box of 250", "C4 white envelopes 250/box", "box", 31.20),
    ("NB-A5", "Notebook A5 ruled, pack of 10", "Ruled A5 notebooks (10)", "pack", 18.60),
    ("CHR-ERG", "Ergonomic office chair", "Office chair, ergonomic mesh back", "each", 189.00),
    ("MON-24", "Monitor 24 inch IPS", "24in IPS display", "each", 139.00),
    ("HDMI-2M", "HDMI cable 2 m", "2m HDMI lead", "each", 7.90),
    ("MOU-WL", "Wireless mouse", "Cordless optical mouse", "each", 14.50),
    ("WBM-4", "Whiteboard markers, assorted 4-pack", "Dry-erase markers x4, assorted colours", "pack", 6.80),
    ("WIPE-100", "Screen cleaning wipes, tub of 100", "Monitor wipes, tub of 100", "each", 5.40),
]
# Same wording style, different product: the invoice line must NOT be paired.
NEAR_MISSES = {
    "PEN-BLK-50": "Blue ballpoint pens (50 pcs)",
    "BAT-AA-24": "Alkaline AAA cells x24",
    "TN-410A-K": "410A cyan LaserJet toner",
}

# How many cases of each kind, and the expected outcome.
PLAN = [
    ("clean_codes", 9, "approve", ""),
    ("clean_wording", 8, "approve", ""),
    ("partial_billed_received", 3, "approve", ""),
    ("price_within_tolerance", 2, "approve", ""),
    ("price_over", 4, "hold", "PRICE_VARIANCE"),
    ("price_over_wording", 2, "hold", "PRICE_VARIANCE"),
    ("qty_over_received", 3, "hold", "QTY_OVER_RECEIVED"),
    ("missing_receipt", 2, "hold", "NO_RECEIPT"),
    ("wrong_po", 2, "hold", "PO_NOT_FOUND"),
    ("line_not_on_po", 3, "hold", "UNMATCHED_LINE"),
]
DUPLICATES = 2  # copies of earlier clean invoices, expected DUPLICATE_INVOICE


def main():
    rng = random.Random(SEED)
    fake = Faker("en_US")
    Faker.seed(SEED)
    vendors = [(f"V{100 + i}", fake.company()) for i in range(6)]

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "invoices").mkdir(parents=True)

    kinds = [(k, d, c) for k, n, d, c in PLAN for _ in range(n)]
    rng.shuffle(kinds)

    pos, po_lines, receipts, labels, line_labels = [], [], [], [], []
    invoices = []  # (file name, dict)
    po_seq, inv_seq = 24001, 7101

    for kind, decision, code in kinds:
        vendor_id, vendor_name = rng.choice(vendors)
        po_number = f"PO-{po_seq}"
        po_seq += 1
        need = 3 if kind == "line_not_on_po" else rng.randint(2, 4)
        pool = [c for c in CATALOG if kind != "line_not_on_po" or c[0] in NEAR_MISSES]
        items = rng.sample(pool if kind != "line_not_on_po" else pool, min(need, len(pool)))
        if kind == "line_not_on_po":
            # one near-miss product plus two ordinary lines
            trap = items[0]
            others = rng.sample([c for c in CATALOG if c[0] not in NEAR_MISSES], 2)
            items = [trap] + others

        pos.append({"po_number": po_number, "vendor_id": vendor_id,
                    "vendor_name": vendor_name, "currency": "USD"})
        lines = []
        for n, (sku, po_desc, sup_desc, unit, price) in enumerate(items, start=1):
            qty = rng.choice([2, 4, 5, 6, 10, 12, 20])
            po_line_id = f"{po_number}-{n}"
            po_lines.append({"po_line_id": po_line_id, "po_number": po_number,
                             "sku": sku, "description": po_desc, "unit": unit,
                             "quantity": qty, "unit_price": f"{price:.2f}"})
            lines.append(dict(po_line_id=po_line_id, sku=sku, po_desc=po_desc,
                              sup_desc=sup_desc, unit=unit, qty=qty, price=price,
                              received=qty, billed_qty=qty, billed_price=price,
                              code=sku, desc=sup_desc))

        # plant the problem
        target = rng.choice(lines)
        if kind in ("clean_wording", "price_over_wording"):
            for ln in lines:
                if rng.random() < 0.7 or ln is target:
                    ln["code"] = None
        if kind in ("partial_billed_received", "qty_over_received"):
            target["received"] = target["qty"] - rng.choice([1, 2])
        if kind == "partial_billed_received":
            target["billed_qty"] = target["received"]
        if kind == "price_within_tolerance":
            target["billed_price"] = round(target["price"] * 1.01, 2)
        if kind in ("price_over", "price_over_wording"):
            target["billed_price"] = round(target["price"] * rng.choice([1.05, 1.08, 1.12]), 2)
        if kind == "line_not_on_po":
            trap = lines[0]
            trap["code"] = None
            trap["desc"] = NEAR_MISSES[trap["sku"]]
            for ln in lines[1:]:
                ln["code"] = None if rng.random() < 0.5 else ln["code"]

        if kind != "missing_receipt":
            for ln in lines:
                receipts.append({"grn_number": f"GRN-{po_number[3:]}", "po_number": po_number,
                                 "po_line_id": ln["po_line_id"], "quantity_received": ln["received"]})

        inv_lines, subtotal = [], 0.0
        for n, ln in enumerate(lines, start=1):
            amount = round(ln["billed_qty"] * ln["billed_price"], 2)
            subtotal += amount
            inv_lines.append({"line_no": n, "item_code": ln["code"], "description": ln["desc"],
                              "quantity": ln["billed_qty"], "unit": ln["unit"],
                              "unit_price": ln["billed_price"], "amount": amount})
            if ln["code"] is None:
                expected = "" if (kind == "line_not_on_po" and n == 1) else ln["po_line_id"]
                line_labels.append({"invoice_file": None, "line_no": n, "expected_po_line": expected})
        subtotal = round(subtotal, 2)
        tax = round(subtotal * 0.08, 2)
        inv_po = po_number
        if kind == "wrong_po":
            inv_po = f"PO-{po_number[3:5]}{po_number[6]}{po_number[5]}{po_number[7]}"  # a typing error: swap two digits
            if inv_po == po_number:
                inv_po = po_number + "1"  # or add a digit when the swap changes nothing
        invoice = {"vendor_name": vendor_name, "invoice_number": f"INV-{inv_seq}",
                   "invoice_date": fake.date_between("-30d", "today").isoformat(),
                   "po_number": inv_po, "currency": "USD", "line_items": inv_lines,
                   "subtotal": subtotal, "tax": tax, "total": round(subtotal + tax, 2)}
        inv_seq += rng.randint(1, 9)
        invoices.append((kind, decision, code, invoice, len(line_labels)))

    # add duplicates: re-sent copies of earlier clean invoices, placed later in the run
    clean_idx = [i for i, x in enumerate(invoices) if x[0] == "clean_codes"][:DUPLICATES]
    for k, i in enumerate(clean_idx):
        kind, _, _, invoice, _ = invoices[i]
        pos_at = min(len(invoices), i + 12 + 5 * k)
        invoices.insert(pos_at, ("duplicate", "hold", "DUPLICATE_INVOICE", dict(invoice), -1))

    # write invoices in processing order and bind line labels to file names
    pending = list(line_labels)
    li = 0
    for case_no, (kind, decision, code, invoice, _) in enumerate(invoices, start=1):
        name = f"case-{case_no:02d}.json"
        (OUT / "invoices" / name).write_text(json.dumps(invoice, indent=2))
        labels.append({"invoice_file": name, "planted": kind,
                       "expected_decision": decision, "expected_codes": code})
        if kind != "duplicate":
            for ln in invoice["line_items"]:
                if ln["item_code"] is None:
                    pending[li]["invoice_file"] = name
                    li += 1

    write_csv("pos.csv", pos)
    write_csv("po_lines.csv", po_lines)
    write_csv("receipts.csv", receipts)
    write_csv("labels.csv", labels)
    write_csv("line_labels.csv", pending)
    print(f"{len(labels)} invoices, {len(po_lines)} PO lines, "
          f"{len(receipts)} receipt lines, {len(pending)} invoice lines without item code")


def write_csv(name, rows):
    with open(OUT / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
