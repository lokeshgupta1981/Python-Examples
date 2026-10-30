"""Draw 15 synthetic travel receipts and write the correct values to labels.json.

Each receipt is saved twice: receipts/clean/receipt-NN.png as printed, and
receipts/photo/receipt-NN.jpg rotated, warped, shaded and blurred like a phone photo.
The amounts, dates and traps are fixed below; Faker fills in addresses, receipt
numbers, card digits and the merchant names the data doesn't fix.
"""
import json
import random
from datetime import date
from pathlib import Path

from faker import Faker
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SEED = 48053
WIDTH = 600

# Country formats: date format, tax label, net label
FORMATS = {
    "GBP": {"date": "%d/%m/%Y", "net": "Net", "locale": "en_GB", "city": "London"},
    "EUR": {"date": "%d.%m.%Y", "net": "Net", "locale": "de_DE", "city": "Berlin"},
    "USD": {"date": "%m/%d/%Y", "net": "Subtotal", "locale": "en_US", "city": "New York, NY"},
}

# The 15 receipts of the trip (14-19 September 2026). Amounts before tax + tax + tip = total.
# hand=True means the tip and the final total are handwritten.
RECEIPTS = [
    # 1: taxi from Heathrow, three days before the trip starts
    dict(merchant="MACDONALD CARS", date="2026-09-11", currency="GBP", category="transport",
         items=[("Heathrow T5 to hotel", 43.33)], tax_label="VAT 20%", tax=8.67, tip=0.0,
         total=52.00, card="3156"),
    dict(merchant="ANDREWS KITCHEN", date="2026-09-14", currency="GBP", category="meals",
         items=[("Chicken wrap", 7.46), ("Flat white", 2.92), ("Water", 1.25)],
         tax_label="VAT 20%", tax=2.32, tip=0.0, total=13.95, card="8612"),
    # 3: hotel, photo stored sideways with an EXIF rotation flag
    dict(merchant=None, kind="HOTEL", date="2026-09-15", currency="GBP", category="lodging",
         items=[("Room 1 night 14/09", 120.83)], tax_label="VAT 20%", tax=24.17, tip=0.0,
         total=145.00, exif_rotate=True),
    dict(merchant="WELLS GRILL HOUSE", date="2026-09-15", currency="GBP", category="meals",
         items=[("Steak frites", 21.50), ("Side salad", 4.50), ("Sparkling water", 6.50)],
         tax_label="VAT 20%", tax=6.50, tip=4.00, tip_label="Service", total=43.00),
    dict(merchant=None, kind="PRINT SHOP", date="2026-09-15", currency="GBP", category="supplies",
         items=[("Colour prints A4 x60", 12.00), ("Binding x3", 3.00)],
         tax_label="VAT 20%", tax=3.00, tip=0.0, total=18.00),
    dict(merchant="CAFE RUPPERSBERGER", date="2026-09-16", currency="EUR", category="meals",
         items=[("Milchkaffee", 4.20), ("Kaesebroetchen", 5.67), ("Apfelkuchen", 5.00)],
         tax_label="MwSt 19%", tax=2.83, tip=0.0, total=17.70),
    # 7: second meal on 16 September, together with receipt 6 above the daily limit
    dict(merchant="RESTAURANT JUNITZ", date="2026-09-16", currency="EUR", category="meals",
         items=[("Wiener Schnitzel", 24.94), ("Fischplatte", 28.00)],
         tax_label="MwSt 19%", tax=10.06, tip=0.0, total=63.00, card="9418"),
    # 8: hotel over the 180 EUR limit
    dict(merchant=None, kind="HOTEL", date="2026-09-17", currency="EUR", category="lodging",
         items=[("Zimmer 1 Nacht 16.09", 205.61)], tax_label="MwSt 7%", tax=14.39, tip=0.0,
         total=220.00),
    dict(merchant=None, kind="TAXI", date="2026-09-17", currency="EUR", category="transport",
         items=[("Fahrt Mitte - BER", 32.71)], tax_label="MwSt 7%", tax=2.29, tip=0.0,
         total=35.00),
    # 10: deli with a handwritten tip and total
    dict(merchant=None, kind="DELI", date="2026-09-17", currency="USD", category="meals",
         items=[("Pastrami on rye", 16.95), ("Pickles", 1.25), ("Iced tea", 2.97)],
         tax_label="Sales tax 8.875%", tax=1.88, tip=3.00, total=26.05, hand=True),
    # 11: JFK taxi with a printed tip
    dict(merchant=None, kind="TAXI", date="2026-09-17", currency="USD", category="transport",
         items=[("JFK flat fare", 70.00), ("Tolls", 6.94)], tax_label="Sales tax 0%", tax=0.00,
         tip=15.00, total=91.94),
    # 12: dinner with a handwritten tip and total, photo stored sideways
    dict(merchant=None, kind="STEAKHOUSE", date="2026-09-18", currency="USD", category="meals",
         items=[("Ribeye", 64.00), ("Salmon", 38.00), ("Two sodas", 18.00)],
         tax_label="Sales tax 8.875%", tax=10.65, tip=25.29, total=155.94, hand=True,
         exif_rotate=True),
    # 13: coffee on Saturday
    dict(merchant=None, kind="COFFEE", date="2026-09-19", currency="USD", category="meals",
         items=[("Latte", 5.25)], tax_label="Sales tax 8.875%", tax=0.47, tip=0.0, total=5.72),
    # 14 and 15 photograph receipts 6 and 11 a second time
    dict(duplicate_of=6),
    dict(duplicate_of=11),
]


def font(size, bold=False, hand=False):
    names = (["DejaVuSans-Oblique.ttf", "FreeSansOblique.ttf"] if hand else
             ["DejaVuSansMono-Bold.ttf", "FreeMonoBold.ttf"] if bold else
             ["DejaVuSansMono.ttf", "FreeMono.ttf"])
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def money(x):
    return f"{x:.2f}"


def draw_receipt(r):
    fmt = FORMATS[r["currency"]]
    img = Image.new("RGB", (WIDTH, 1100), "white")
    d = ImageDraw.Draw(img)
    regular, bold, hand = font(22), font(26, bold=True), font(30, hand=True)
    y = 30

    def center(text, f):
        nonlocal y
        w = d.textlength(text, font=f)
        d.text(((WIDTH - w) / 2, y), text, fill="black", font=f)
        y += f.size + 10

    def row(left, right="", f=regular, right_font=None, color="black"):
        nonlocal y
        d.text((40, y), left, fill="black", font=f)
        if right:
            rf = right_font or f
            w = d.textlength(right, font=rf)
            d.text((WIDTH - 40 - w, y - (6 if rf is hand else 0)), right, fill=color, font=rf)
        y += f.size + 12

    center(r["merchant"], bold)
    center(r["address"], regular)
    center(fmt["city"], regular)
    y += 10
    row(r["printed_date"], r["time"])
    row(f"Receipt {r['number']}")
    y += 10
    for name, price in r["items"]:
        row(name, money(price))
    y += 8
    net = round(sum(p for _, p in r["items"]), 2)
    row(fmt["net"], money(net))
    row(r["tax_label"], money(r["tax"]))
    if r.get("hand"):
        row("Amount", money(round(net + r["tax"], 2)))
        y += 6
        row("Tip", money(r["tip"]), right_font=hand, color="#1b2a8a")
        y += 4
        row(f"TOTAL {r['currency']}", money(r["total"]), f=bold, right_font=hand, color="#1b2a8a")
    else:
        if r["tip"]:
            row(r.get("tip_label", "Tip"), money(r["tip"]))
        row(f"TOTAL {r['currency']}", money(r["total"]), f=bold)
    y += 10
    row(f"{r['card_brand']} **** {r['card']}")
    y += 20
    center("Thank you!", regular)
    return img.crop((0, 0, WIDTH, y + 20))


def phone_photo(img, rng):
    """Make a clean receipt look like a quick phone photo."""
    w, h = img.size
    canvas = Image.new("RGB", (w + 160, h + 160), (92, 84, 74))  # a wooden desk
    canvas.paste(img, (80, 80))
    canvas = canvas.rotate(rng.uniform(-4, 4), resample=Image.BICUBIC, fillcolor=(92, 84, 74))
    cw, ch = canvas.size
    j = lambda: rng.uniform(0, 18)
    quad = (j(), j(), j(), ch - j(), cw - j(), ch - j(), cw - j(), j())  # perspective warp
    canvas = canvas.transform((cw, ch), Image.QUAD, quad, resample=Image.BICUBIC)
    shade = Image.linear_gradient("L").resize((cw, ch)).rotate(rng.choice([0, 90, 180, 270]))
    shade = shade.point(lambda v: 255 - int(v * 0.45))  # a shadow across one side
    canvas = Image.composite(canvas, Image.new("RGB", canvas.size, "black"), shade)
    canvas = canvas.filter(ImageFilter.GaussianBlur(1.1))
    return canvas.resize((round(cw * 0.75), round(ch * 0.75)), Image.BILINEAR)


def main():
    rng = random.Random(SEED)
    fakers = {c: Faker(f["locale"]) for c, f in FORMATS.items()}
    for f in fakers.values():
        f.seed_instance(SEED)
    for folder in ("receipts/clean", "receipts/photo"):
        Path(folder).mkdir(parents=True, exist_ok=True)

    labels, drawn = {}, {}
    for n, spec in enumerate(RECEIPTS, start=1):
        name = f"receipt-{n:02d}"
        if "duplicate_of" in spec:
            r, img = drawn[spec["duplicate_of"]]
        else:
            r = dict(spec)
            fake = fakers[r["currency"]]
            if not r.get("merchant"):
                r["merchant"] = f"{fake.last_name().upper()} {r['kind']}"
            r["address"] = fake.street_address().replace("\n", ", ")[:34]
            r["number"] = fake.bothify("####-###")
            r["time"] = f"{rng.randint(7, 22):02d}:{rng.randint(0, 59):02d}"
            r.setdefault("card", fake.numerify("####"))
            r["card_brand"] = rng.choice(["VISA", "Mastercard"])
            r["printed_date"] = date.fromisoformat(r["date"]).strftime(
                FORMATS[r["currency"]]["date"])
            net = round(sum(p for _, p in r["items"]), 2)
            assert abs(net + r["tax"] + r["tip"] - r["total"]) < 0.005, name
            img = draw_receipt(r)
            drawn[n] = (r, img)
        img.save(f"receipts/clean/{name}.png")

        photo = phone_photo(img, rng)
        exif = Image.Exif()
        if spec.get("exif_rotate"):
            photo = photo.transpose(Image.ROTATE_90)  # stored sideways ...
            exif[0x0112] = 6  # ... and the Orientation tag says "rotate 90 degrees to view"
        photo.save(f"receipts/photo/{name}.jpg", quality=72, exif=exif)

        labels[name] = {
            "merchant": r["merchant"], "date": r["date"], "currency": r["currency"],
            "amount_before_tax": round(sum(p for _, p in r["items"]), 2), "tax": r["tax"],
            "tip": r["tip"], "total": r["total"], "card_last4": r["card"],
            "category": r["category"],
        }
        print(name, r["merchant"], r["printed_date"], r["currency"], money(r["total"]))
    Path("labels.json").write_text(json.dumps(labels, indent=2))


if __name__ == "__main__":
    main()
