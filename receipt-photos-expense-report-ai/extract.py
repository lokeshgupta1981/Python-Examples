"""Steps 2 to 5: prepare the photo, read it with Tesseract, let the model fill the
Receipt schema, and check the answer in code.

Usage: python extract.py clean   (or: python extract.py photo)
"""
import json
import sys
import time
from datetime import date
from pathlib import Path

import httpx
import ollama
import pytesseract
from PIL import Image, ImageChops, ImageFilter, ImageOps
from pydantic import ValidationError

from receipt_schema import Receipt

MODEL = "qwen2.5:7b"
CURRENCIES = {"EUR", "GBP", "USD"}

SYSTEM_PROMPT = """You read OCR text from a shop or restaurant receipt and fill in its fields.
Copy values exactly as printed. If a value is missing or unreadable, use null.
Never calculate a value that isn't printed.
- merchant: the business name at the top
- date: YYYY-MM-DD. UK receipts print DD/MM/YYYY, German receipts DD.MM.YYYY,
  US receipts (USD) MM/DD/YYYY
- currency: EUR, GBP or USD
- amount_before_tax: the Net or Subtotal line
- tax: the VAT, MwSt or Sales tax line
- tip: the Tip line, 0 if the receipt has no Tip line
- total: the TOTAL line
- card_last4: the last four digits of the card number
- category: meals (food and drinks), lodging (hotels), transport (taxi, train,
  flights), supplies (printing, stationery) or other"""

client = ollama.Client(timeout=1800) # seconds; a busy CPU server queues calls


def prepare_image(path):
    """Turn a photo into a clean grayscale image that Tesseract reads well."""
    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img) # apply the phone's rotation flag
        img = img.convert("L")
    scale = 1400 / img.width # small text needs more pixels
    img = img.resize((1400, round(img.height * scale)), Image.LANCZOS)
    background = img.filter(ImageFilter.GaussianBlur(25))
    img = ImageChops.invert(ImageChops.subtract(background, img)) # remove shadows
    return ImageOps.autocontrast(img, cutoff=1)


def ocr(path):
    # --psm 6 reads the image as one block of text, which suits a receipt
    return pytesseract.image_to_string(prepare_image(path), config="--psm 6").strip()


def ask_model(text, attempts=3):
    """Send the OCR text to the model; retry when the Ollama server can't be reached."""
    for attempt in range(1, attempts + 1):
        try:
            return client.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Receipt text:\n\n{text}"},
                ],
                format=Receipt.model_json_schema(), # the answer must match this
                options={"temperature": 0},
            )
        except (ConnectionError, httpx.TransportError) as e:
            if attempt == attempts:
                raise
            print(f"  model call failed ({e}), retrying in 30 s", flush=True)
            time.sleep(30)


def validate(r: Receipt, today=None):
    """Checks the schema can't express. Returns a list of problems."""
    today = today or date.today()
    if r.total is None:
        return ["unreadable: no total found"]
    problems = []
    if r.date is None:
        problems.append("no date")
    elif r.date > today:
        problems.append(f"date {r.date} is in the future")
    if r.currency not in CURRENCIES:
        problems.append(f"unknown currency {r.currency}")
    if r.amount_before_tax is None or r.tax is None or r.tip is None:
        problems.append("amount before tax, tax or tip missing")
    elif abs(r.amount_before_tax + r.tax + r.tip - r.total) > 0.01:
        problems.append(
            f"before tax + tax + tip = {r.amount_before_tax + r.tax + r.tip:.2f}, "
            f"total is {r.total:.2f}")
    if r.total <= 0:
        problems.append("total is not positive")
    return problems


def extract(path):
    started = time.time()
    text = ocr(path)
    response = ask_model(text)
    answer = response.message.content
    try:
        receipt = Receipt.model_validate_json(answer)
        problems = validate(receipt)
    except ValidationError as e:
        receipt, problems = None, [f"invalid answer: {e.errors()[0]['msg']}"]
    return {
        "file": path.stem, "ocr_chars": len(text), "answer": answer,
        "receipt": receipt.model_dump(mode="json") if receipt else None,
        "problems": problems, "seconds": round(time.time() - started, 1),
        "model_seconds": round((response.prompt_eval_duration or 0) / 1e9
                               + (response.eval_duration or 0) / 1e9, 1),
        "prompt_tokens": response.prompt_eval_count,
        "output_tokens": response.eval_count,
    }, text


def main():
    image_set = sys.argv[1] if len(sys.argv) > 1 else "photo"
    folder = Path("receipts") / image_set
    out_file = Path(f"results_{image_set}.json")
    results = json.loads(out_file.read_text()) if out_file.exists() else []
    done = {r["file"] for r in results}
    text_dir = Path("ocr") / image_set
    text_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(folder.glob("receipt-*.*")):
        if path.stem in done:
            continue
        result, text = extract(path)
        (text_dir / f"{path.stem}.txt").write_text(text)
        results.append(result)
        out_file.write_text(json.dumps(results, indent=2))
        status = "OK" if not result["problems"] else "; ".join(result["problems"])
        print(f"{image_set}/{path.name}: {result['seconds']}s, {status}", flush=True)


if __name__ == "__main__":
    main()
