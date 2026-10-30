"""Step 7: write the expense report as CSV and PDF.

Usage: python report.py photo   (or: python report.py clean)
"""
import json
import sys
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from policy import apply_policy, load_yaml

COLUMNS = ["file", "date", "merchant", "category", "currency", "total", "total_eur",
           "card", "status", "reason"]
ROW_COLORS = {"flagged": colors.HexColor("#fff3c4"), "review": colors.HexColor("#f9d6d5")}


def text(value):
    return "" if value is None or pd.isna(value) else str(value)


def build_report(lines, trip, csv_path, pdf_path):
    df = pd.DataFrame(lines)
    df["card"] = df["card_last4"].map(lambda d: f"**** {d}" if isinstance(d, str) else "")
    df = df[COLUMNS]
    df.to_csv(csv_path, index=False)

    approved = df[df["status"] == "approved"]
    summary = approved.groupby("category")["total_eur"].agg(["count", "sum"])
    # The PDF part of the function follows here in report.py
    styles = getSampleStyleSheet()
    small = styles["BodyText"].clone("small", fontSize=8, leading=10)
    story = [
        Paragraph(f"Expense report: {trip['employee']}", styles["Title"]),
        Paragraph(f"{trip['purpose']}, {trip['start']} to {trip['end']}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Approved amounts per category (EUR)", styles["Heading2"]),
    ]
    rows = [["Category", "Receipts", "EUR"]]
    rows += [[c, int(s["count"]), f"{s['sum']:.2f}"] for c, s in summary.iterrows()]
    rows.append(["Total", int(summary["count"].sum()), f"{summary['sum'].sum():.2f}"])
    t = Table(rows, hAlign="LEFT")
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef7")),
                           ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold")]))
    story += [t, Spacer(1, 12), Paragraph("Receipts", styles["Heading2"])]

    header = ["File", "Date", "Merchant", "Category", "Total", "EUR", "Card", "Status", "Reason"]
    rows = [header]
    for _, line in df.iterrows():
        eur = "" if pd.isna(line["total_eur"]) else f"{line['total_eur']:.2f}"
        total = "" if pd.isna(line["total"]) else f"{line['total']:.2f} {line['currency']}"
        rows.append([line["file"], text(line["date"]), Paragraph(text(line["merchant"]), small),
                     text(line["category"]), total, eur, line["card"], line["status"],
                     Paragraph(text(line["reason"]), small)])
    t = Table(rows, colWidths=[62, 62, 120, 58, 78, 52, 62, 52, 220], repeatRows=1)
    style = [("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 8),
             ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef7")),
             ("VALIGN", (0, 0), (-1, -1), "TOP")]
    for i, status in enumerate(df["status"], start=1):
        if status in ROW_COLORS:
            style.append(("BACKGROUND", (0, i), (-1, i), ROW_COLORS[status]))
    t.setStyle(TableStyle(style))
    story.append(t)
    SimpleDocTemplate(str(pdf_path), pagesize=landscape(A4)).build(story)
    return df


def main():
    image_set = sys.argv[1] if len(sys.argv) > 1 else "photo"
    results = json.loads(Path(f"results_{image_set}.json").read_text())
    lines = apply_policy(results, load_yaml("policy.yaml"), load_yaml("trip.yaml"))
    df = build_report(lines, load_yaml("trip.yaml"),
                      "expense_report.csv", "expense_report.pdf")
    print(df["status"].value_counts().to_string())


if __name__ == "__main__":
    main()
