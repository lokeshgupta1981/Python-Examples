import json
from pathlib import Path

with open("recipes.json", encoding="utf-8") as f:
    recipes = json.load(f)

kind = type(recipes)           # <class 'list'>
print('kind', '=', repr(kind))
first = recipes[0]["name"]     # 'Pancakes'
print('first', '=', repr(first))
vegan = recipes[1]["vegan"]    # True, JSON true becomes Python True
print('vegan', '=', repr(vegan))
tag = recipes[0]["tags"][1]    # 'sweet'
print('tag', '=', repr(tag))
servings = recipes[0].get("servings", 2)   # 2, the key is missing
print('servings', '=', repr(servings))


text = Path("recipes.json").read_text(encoding="utf-8")
same = json.loads(text) == recipes    # True
print('same', '=', repr(same))

def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("No such file:", path)
    except json.JSONDecodeError as e:
        print(f"Bad JSON in {path}: {e.msg} at line {e.lineno}, column {e.colno}")
    return None

load_json("missing.json")
load_json("broken.json")

with open("recipes.jsonl", encoding="utf-8") as f:
    rows = [json.loads(line) for line in f if line.strip()]
names = [r["name"] for r in rows]    # ['Pancakes', 'Lentil soup']
print('names', '=', repr(names))

DEFAULTS = {"port": 8080, "debug": False, "theme": "light"}

def load_config(path):
    try:
        with open(path, encoding="utf-8") as f:
            return DEFAULTS | json.load(f)
    except FileNotFoundError:
        return dict(DEFAULTS)

config = load_config("settings.json")    # {'port': 9000, 'debug': False, 'theme': 'dark'}
print('config', '=', repr(config))
