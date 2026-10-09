import json
import os

filename = "users.json"

with open(filename, encoding="utf-8") as fp:
    list_obj = json.load(fp)              # list with 2 dicts

list_obj.append({"Name": "Person_3", "Age": 33, "Email": "33@gmail.com"})

with open(filename, "w", encoding="utf-8") as fp:
    json.dump(list_obj, fp, indent=4)

with open("user.json", encoding="utf-8") as fp:
    dict_obj = json.load(fp)              # dict

dict_obj.update({"Age": 12, "Role": "Developer"})

with open("user.json", "w", encoding="utf-8") as fp:
    json.dump(dict_obj, fp, indent=4)

with open("user.json", encoding="utf-8") as fp:
    data = json.load(fp)

if isinstance(data, list):
    data.append({"Name": "Person_4"})     # a new element in the array
else:
    data.update({"Role": "Lead"})         # a new key in the object


def append_record(filename, record):
    try:
        with open(filename, encoding="utf-8") as fp:
            records = json.load(fp)
    except FileNotFoundError:
        records = []
    records.append(record)
    tmp = filename + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fp:
        json.dump(records, fp, indent=4)
    os.replace(tmp, filename)             # replaces the old file in one step

append_record("events.json", {"event": "login"})

with open("events.jsonl", "a", encoding="utf-8") as fp:
    fp.write(json.dumps({"event": "login"}) + "\n")
    fp.write(json.dumps({"event": "logout"}) + "\n")

team = {"name": "core", "members": ["Ana"]}
team["members"].append("Lokesh")
text = json.dumps(team)      # '{"name": "core", "members": ["Ana", "Lokesh"]}'
print('text', '=', repr(text))
