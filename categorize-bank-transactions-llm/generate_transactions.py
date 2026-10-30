"""Writes the fictional sample bank exports used by the article.

data/history.csv  July and August, already categorized (64 rows)
data/test.csv     September, the labelled test set (60 rows)
data/next.csv     October, used to measure how the rules grow (44 rows)

All names are fictional. Customer company names come from Faker with a
fixed seed, so every run writes the same files.
"""

import csv
import re
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

Faker.seed(42)
fake = Faker("en_GB")


def company() -> str:
    return re.sub(r"[^A-Z ]", "", fake.company().upper())


CUSTOMERS = [company() for _ in range(6)]   # A, B, C recurring; D, E one-off; F new
A, B, C, D, E, F = CUSTOMERS

# (description, amount, label) for merchants that appear every month
RECURRING = [
    ("DD NORTHGRID POWER {n}", -184.20, "Utilities"),
    ("DD MAILKITE {n}", -29.00, "Software"),
    ("CARD 4411 NORTHLINE TRAINS", -62.40, "Travel"),
    ("CARD 4411 BLUE CUP COFFEE LONDON", -8.70, "Meals"),
    ("CARD 4411 PAPERLY*ORDER {n}", -46.15, "Office supplies"),
    ("FPS TO L PERRY REF SALARY {m}", -2150.00, "Payroll"),
    ("FPS TO R OKAFOR REF SALARY {m}", -1980.00, "Payroll"),
    ("DD HMRC PAYE {n}", -1240.55, "Taxes"),
    ("MONTHLY ACCOUNT FEE", -12.50, "Bank fees"),
    ("DD CITYLINK BROADBAND", -38.00, "Utilities"),
    ("DD HARBOUR WORKSPACE LTD", -950.00, "Rent"),
    (f"BGC {A} REF INV {{n}}", 3200.00, "Sales income"),
    (f"BGC {B} REF INV {{n}}", 1450.00, "Sales income"),
    (f"BGC {C} REF INV {{n}}", 2780.00, "Sales income"),
    ("CARD 4411 CLOUDNEST.IO", -54.00, "Software"),
    ("CARD 4411 SWIFTCAB*TRIP {n}", -18.60, "Travel"),
    ("CARD 4411 GREENLEAF SANDWICHES", -23.40, "Meals"),
    ("DD VOXLINE MOBILE", -41.99, "Utilities"),
    ("DD TAKEPAY FEES", -15.80, "Bank fees"),
    ("DD AQUAFLOW WATER", -27.30, "Utilities"),
    ("CARD 4411 PRINTHAUS MANCHESTER", -35.90, "Office supplies"),
    ("CARD 4411 SIGNWELL.COM", -19.00, "Software"),
    ("CARD 4411 PARKRIGHT {n}", -9.50, "Travel"),
    ("CARD 4411 OFFICEBOX", -64.25, "Office supplies"),
    ("FPS TO A NOWAK REF SALARY {m}", -1875.00, "Payroll"),
]

# Second visits to recurring merchants in September and October
EXTRA = [
    ("CARD 4411 PAPERLY*ORDER {n}", -22.80, "Office supplies"),
    ("CARD 4411 BLUE CUP COFFEE LONDON", -6.90, "Meals"),
    ("CARD 4411 SWIFTCAB*TRIP {n}", -24.10, "Travel"),
    ("CARD 4411 NORTHLINE TRAINS", -48.00, "Travel"),
    ("CARD 4411 GREENLEAF SANDWICHES", -31.20, "Meals"),
    ("CARD 4411 PARKRIGHT {n}", -7.00, "Travel"),
]

JULY_ONE_OFF = [
    ("CASH WITHDRAWAL LEEDS", -200.00, "Other"),
    ("DD HMRC VAT {n}", -3120.00, "Taxes"),
    ("CARD 4411 STAYWELL HOTEL MANCHESTER", -118.00, "Travel"),
    (f"BGC {D} REF INV {{n}}", 960.00, "Sales income"),
    ("CARD 4411 TECHSTORE*ORDER {n}", -149.99, "Office supplies"),
    ("FPS TO J WARD REF EXPENSES JUL", -86.40, "Other"),
    ("CARD 4411 ROMA TRATTORIA LONDON", -74.50, "Meals"),
]

AUGUST_ONE_OFF = [
    ("CHQ {n}", -350.00, "Other"),
    ("FPS TO SAVINGS ACCT {n}", -1000.00, "Other"),
    (f"BGC {E} REF INV {{n}}", 640.00, "Sales income"),
    ("OVERDRAFT INTEREST", -3.12, "Bank fees"),
    ("BGC OFFICEBOX REFUND", 21.50, "Refunds"),
    ("CARD 4411 FUELSTOP A1", -71.80, "Travel"),
    ("CARD 4411 POSTHUB", -12.60, "Office supplies"),
]

# September rows that no history rule matches, by their position in the month
SEPTEMBER_NEW = {
    3: ("CARD 4411 GREENFORK CATERING", -186.00, "Meals"),
    5: ("CARD 4411 ROADWAY FUEL M4 SERVICES", -68.30, "Travel"),
    7: ("CARD 4411 NORTHLINE TRAINS REFUND", 31.20, "Refunds"),
    9: ("CASH WITHDRAWAL BRISTOL", -150.00, "Other"),
    11: ("CARD 4411 STAYWELL HOTEL LEEDS", -104.00, "Travel"),
    13: (f"BGC {D} REF INV {{n}}", 1120.00, "Sales income"),
    15: ("CARD 4411 TECHSTORE*ORDER {n}", -89.00, "Office supplies"),
    17: ("CARD 4411 KEYSTONE LOCKSMITHS", -95.00, "Other"),
    19: ("OVERDRAFT INTEREST", -2.48, "Bank fees"),
    21: ("CARD 4411 POSTHUB", -9.80, "Office supplies"),
    23: ("CARD 4411 ROMA TRATTORIA LONDON", -58.00, "Meals"),
    25: ("CARD 4411 PIXELFORGE.IO", -24.00, "Software"),
    27: ("DD HMRC VAT {n}", -2890.00, "Taxes"),
    28: ("FPS TO M PATEL REF SEPT", -640.00, "Payroll"),
    30: ("CHQ {n}", -120.00, "Other"),
    32: ("CARD 4411 QUICKPRINT LTD", -43.50, "Office supplies"),
    34: ("FPS TO SAVINGS ACCT {n}", -1500.00, "Other"),
    36: ("CARD 4411 BEANHOUSE CAFE", -11.20, "Meals"),
    38: ("DD BRIGHTWAVE ENERGY {n}", -96.40, "Utilities"),
    40: ("FPS TO J WARD REF EXPENSES SEP", -54.90, "Other"),
    42: ("CARD 4411 METROPARK", -12.00, "Travel"),
    44: ("BGC TAKEPAY SETTLEMENT", 812.35, "Sales income"),
    45: (f"FPS TO {B} REF REFUND INV {{n}}", -150.00, "Refunds"),
    46: ("CARD 4411 OFFICEBOX REFUND", 18.00, "Refunds"),
    48: ("CARD 4411 LUMEN COWORK DAY PASS", -25.00, "Rent"),
    50: ("CARD 4411 MAILKITE.COM", -12.00, "Software"),
    52: ("BGC SWIFTCAB REFUND", 9.40, "Refunds"),
    54: (f"BGC {F} REF INV {{n}}", 2300.00, "Sales income"),
    56: ("CARD 4411 CLOUDNEST.IO REFUND", 54.00, "Refunds"),
}

OCTOBER_FROM_SEPTEMBER = [
    ("CARD 4411 MAILKITE.COM", -12.00, "Software"),
    ("CARD 4411 GREENFORK CATERING", -142.00, "Meals"),
    ("CARD 4411 ROADWAY FUEL M4 SERVICES", -59.90, "Travel"),
    ("FPS TO M PATEL REF OCT", -640.00, "Payroll"),
    ("DD BRIGHTWAVE ENERGY {n}", -101.20, "Utilities"),
    ("CARD 4411 METROPARK", -12.00, "Travel"),
    ("CARD 4411 PIXELFORGE.IO", -24.00, "Software"),
    ("CARD 4411 QUICKPRINT LTD", -27.00, "Office supplies"),
    ("CARD 4411 BEANHOUSE CAFE", -9.60, "Meals"),
    ("BGC TAKEPAY SETTLEMENT", 904.10, "Sales income"),
]

OCTOBER_NEW = [
    ("CARD 4411 HARBOR BAKERY", -14.30, "Meals"),
    ("CHQ {n}", -275.00, "Other"),
    ("CARD 4411 VELOCITY BIKES", -420.00, "Travel"),
]

MONTHS = {7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT"}


def month_rows(month: int, rows: list[tuple], start_id: int, balance: float):
    """Spreads the rows over the month and fills in numbers and balances."""
    first = date(2026, month, 1)
    out = []
    for i, (text, amount, label) in enumerate(rows):
        day = first + timedelta(days=i * 28 // len(rows))
        number = 1000 + month * 100 + i
        description = text.format(n=number, m=MONTHS[month])
        balance = round(balance + amount, 2)
        out.append({"id": start_id + i, "date": day.strftime("%d/%m/%Y"),
                    "description": description, "amount": f"{amount:.2f}",
                    "balance": f"{balance:.2f}", "label": label})
    return out, balance


def interleave(fixed: dict, others: list[tuple], size: int) -> list[tuple]:
    """Puts the fixed rows at their 1-based positions and fills the gaps in order."""
    rest = iter(others)
    return [fixed[p] if p in fixed else next(rest) for p in range(1, size + 1)]


def write(path: str, rows: list[dict]) -> None:
    Path(path).parent.mkdir(exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    july, balance = month_rows(7, RECURRING + JULY_ONE_OFF, 1, 18500.00)
    august, balance = month_rows(8, RECURRING + AUGUST_ONE_OFF, 1 + len(july), balance)
    write("data/history.csv", july + august)

    september_rows = interleave(SEPTEMBER_NEW, RECURRING + EXTRA, 60)
    september, balance = month_rows(9, september_rows, 1, balance)
    write("data/test.csv", september)

    october, _ = month_rows(10, RECURRING + EXTRA + OCTOBER_FROM_SEPTEMBER + OCTOBER_NEW,
                            1, balance)
    write("data/next.csv", october)
    print(f"history {len(july) + len(august)}, test {len(september)}, next {len(october)}")


if __name__ == "__main__":
    main()
