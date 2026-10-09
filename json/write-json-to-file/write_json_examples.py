import json
from datetime import date

py_dict = {"id": 1}

with open("users.json", "w", encoding="utf-8") as json_file:
    json.dump(py_dict, json_file, indent=4, sort_keys=True)

py_dictionary = {"Name": "Lokesh", "Age": 39, "Blog": "howtodoinjava"}

with open("users.json", "w", encoding="utf-8") as json_file:
    json.dump(py_dictionary, json_file)

with open("users.json", "w", encoding="utf-8") as json_file:
    json.dump(py_dictionary, json_file, indent=4, sort_keys=True)

city = {"City": "Málaga"}
escaped = json.dumps(city)                       # '{"City": "M\u00e1laga"}'
print('escaped', '=', repr(escaped))
readable = json.dumps(city, ensure_ascii=False)  # '{"City": "Málaga"}'
print('readable', '=', repr(readable))


event = {"name": "Launch", "on": date(2026, 11, 2)}
try:
    bad = json.dumps(event)
except Exception as e:
    print(type(e).__name__ + ':', e)
good = json.dumps(event, default=str)     # '{"name": "Launch", "on": "2026-11-02"}'
print('good', '=', repr(good))

orders = [{"id": 1, "items": ("tea", "milk")}, {"id": 2, "items": ("rice",)}]

with open("orders.json", "w", encoding="utf-8") as f:
    json.dump(orders, f, indent=2)

with open("orders.json", encoding="utf-8") as f:
    loaded = json.load(f)

items = loaded[0]["items"]      # ['tea', 'milk'], a list after loading
print('items', '=', repr(items))
equal = loaded == orders        # False, tuples became lists
print('equal', '=', repr(equal))

compact = json.dumps({"id": 1, "ok": True}, separators=(",", ":"))   # '{"id":1,"ok":true}'
print('compact', '=', repr(compact))
