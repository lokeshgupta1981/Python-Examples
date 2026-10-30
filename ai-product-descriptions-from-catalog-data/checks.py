import re

NUMBER = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?")
SPEC_TERMS = [
    "waterproof", "water-resistant", "windproof", "insulated", "breathable",
    "lifetime", "warranty", "recycled", "merino", "wool", "goose", "nylon",
    "polyester", "leather", "aluminium", "aluminum", "titanium", "carbon",
    "stainless", "silk", "fleece", "gore-tex", "ultralight", "upf", "ipx",
    "lumens", "red", "blue", "green", "black", "grey", "gray", "orange",
    "navy", "sage", "white", "yellow",
]
NEEDS_COLUMN = {"waterproof": "waterproof_rating", "warranty": "warranty_years"}


def numbers_in(text):
    return {float(n.replace(",", "")) for n in NUMBER.findall(text)}


def allowed_numbers(facts):
    allowed = numbers_in(" ".join(facts.values()))
    if "weight_g" in facts:
        allowed |= {n / 1000 for n in numbers_in(facts["weight_g"])}
    if "capacity_l" in facts:
        allowed |= {n * 1000 for n in numbers_in(facts["capacity_l"])}
    return allowed


def check_facts(copy, facts):
    text = copy_text(copy).lower()
    source = " ".join(facts.values()).lower()
    violations = []
    for number in sorted(numbers_in(text) - allowed_numbers(facts)):
        violations.append(f"invented number: {number:g}")
    for term in SPEC_TERMS:
        if not re.search(rf"\b{re.escape(term)}\b", text):
            continue
        if term in NEEDS_COLUMN:
            if NEEDS_COLUMN[term] not in facts:
                violations.append(f"invented spec: {term}")
        elif not re.search(rf"\b{re.escape(term)}\b", source):
            violations.append(f"invented spec: {term}")
    for name in copy.used_attributes:
        if name not in facts:
            violations.append(f"unknown attribute: {name}")
    return violations


def check_style(copy, banned_words):
    text = copy_text(copy)
    violations = []
    for word in banned_words:
        if re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
            violations.append(f"banned word: {word}")
    if "!" in text:
        violations.append("banned word: exclamation mark")
    return violations


def copy_text(copy):
    return " ".join([copy.title, copy.description, *copy.bullets,
                     copy.meta_title, copy.meta_description])
