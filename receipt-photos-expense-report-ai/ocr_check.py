"""Count how many amounts Tesseract finds on the photos, with and without prepare_image().

Checks three amounts per receipt (amount before tax, tax and total). Makes no model calls.
Usage: python ocr_check.py photo
"""
import json
import sys
from pathlib import Path

import pytesseract
from PIL import Image

from extract import prepare_image


def main():
    image_set = sys.argv[1] if len(sys.argv) > 1 else "photo"
    labels = json.loads(Path("labels.json").read_text())
    raw_found = prepared_found = checked = 0
    for path in sorted((Path("receipts") / image_set).glob("receipt-*.*")):
        label = labels[path.stem]
        amounts = [f"{label[k]:.2f}" for k in ("amount_before_tax", "tax", "total")]
        with Image.open(path) as img:
            raw = pytesseract.image_to_string(img, config="--psm 6")
        prepared = pytesseract.image_to_string(prepare_image(path), config="--psm 6")
        raw_found += sum(a in raw for a in amounts)
        prepared_found += sum(a in prepared for a in amounts)
        checked += len(amounts)
    print(f"{checked} amounts: {raw_found} found without preparation, "
          f"{prepared_found} with prepare_image()")


if __name__ == "__main__":
    main()
