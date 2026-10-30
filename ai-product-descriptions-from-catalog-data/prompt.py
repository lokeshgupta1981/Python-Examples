import json

from schema import ProductCopy

PROMPT_VERSION = "v1"

SYSTEM = """You write product copy for TrailGear, an outdoor gear shop.

Brand voice:
{voice}

Rules:
- Use only the facts the user lists. Never add a material, number, rating, color or feature that is not listed.
- If only a few facts are listed, write less. A short description is better than an invented one.
- title: at most 60 characters.
- description: 2 to 4 sentences, at most 600 characters.
- bullets: 3 to 5 short features, each based on one listed fact.
- meta_title: at most 60 characters. meta_description: at most 155 characters.
- used_attributes: the names of the facts you used, for example "material".

Answer with JSON that matches this schema:
{schema}"""


def build_messages(facts, voice):
    schema = json.dumps(ProductCopy.model_json_schema())
    lines = "\n".join(f"{name}: {value}" for name, value in facts.items())
    return [
        {"role": "system", "content": SYSTEM.format(voice=voice, schema=schema)},
        {"role": "user", "content": f"Product facts:\n{lines}"},
    ]
