from collections import Counter, defaultdict

person = {"name": "Lokesh", "age": 39}
name = person["name"]                   # 'Lokesh'
print('name', '=', repr(name))
person["blog"] = "howtodoinjava"        # add a new key
country = person.get("country", "India")   # 'India', a default for a missing key
print('country', '=', repr(country))

empty = {}
person = {
    "name": "Lokesh",
    "age": 39,
    "blog": "howtodoinjava"
}
print(person)

d1 = dict({1: "Python", 2: "Example"})        # {1: 'Python', 2: 'Example'}
print('d1', '=', repr(d1))
d2 = dict([(1, "Python"), (2, "Example")])    # {1: 'Python', 2: 'Example'}
print('d2', '=', repr(d2))
d3 = dict(firstName="Lokesh", lastName="Gupta", age=39)
# {'firstName': 'Lokesh', 'lastName': 'Gupta', 'age': 39}
d4 = dict(zip(["a", "b"], [1, 2]))            # {'a': 1, 'b': 2}
print('d4', '=', repr(d4))

squares = {n: n * n for n in range(4)}            # {0: 0, 1: 1, 2: 4, 3: 9}
print('squares', '=', repr(squares))

person = {"name": "Lokesh", "blog": "howtodoinjava", "age": 39}
name = person["name"]                      # 'Lokesh'
print('name', '=', repr(name))
age = person.get("age")                    # 39
print('age', '=', repr(age))
missing = person.get("country")            # None
print('missing', '=', repr(missing))
with_default = person.get("country", "India")   # 'India'
print('with_default', '=', repr(with_default))

pairs = len(person)                       # 3
print('pairs', '=', repr(pairs))

user = {"name": "Lokesh", "address": {"city": "Delhi", "zip": "110001"}}
city = user["address"]["city"]                      # 'Delhi'
print('city', '=', repr(city))
country = user.get("address", {}).get("country")    # None
print('country', '=', repr(country))
user["address"]["city"] = "Noida"                   # change an inner value

person = {"name": "Lokesh", "blog": "howtodoinjava", "age": 39}
has_name = "name" in person                # True
print('has_name', '=', repr(has_name))
has_value = "Lokesh" in person             # False, values are not checked
print('has_value', '=', repr(has_value))
in_values = "Lokesh" in person.values()    # True
print('in_values', '=', repr(in_values))

if "country" not in person:
    print("country is not present")

person = {"name": "Lokesh", "blog": "howtodoinjava", "age": 39}
person["name"] = "Alex"                    # update
person.update({"name": "Brian"})           # update with update()
person["country"] = "India"                # add a new key
person.update(city="Delhi", age=40)        # several pairs at once
snapshot = person
# {'name': 'Brian', 'blog': 'howtodoinjava', 'age': 40, 'country': 'India', 'city': 'Delhi'}

defaults = {"theme": "light", "lang": "en"}
user = {"lang": "fr"}
settings = defaults | user                 # {'theme': 'light', 'lang': 'fr'}
print('settings', '=', repr(settings))
defaults |= {"size": 12}                   # defaults changed in place

person = {"name": "Lokesh", "blog": "howtodoinjava", "age": 39}
del person["name"]
remaining = person                     # {'blog': 'howtodoinjava', 'age': 39}
print('remaining', '=', repr(remaining))

person = {"name": "Lokesh", "blog": "howtodoinjava", "age": 39}
removed = person.pop("name")           # 'Lokesh'
print('removed', '=', repr(removed))
safe = person.pop("country", None)     # None, no error
print('safe', '=', repr(safe))

person = {"name": "Lokesh", "blog": "howtodoinjava", "age": 39}
person.clear()
after = person                         # {}
print('after', '=', repr(after))

person = {"name": "Lokesh", "blog": "howtodoinjava", "age": 39}
for k in person:
    print(f"Key: {k}, Value: {person[k]}")

for v in {"name": "Lokesh", "blog": "howtodoinjava"}.values():
    print("Value:", v)

for key, value in {"name": "Lokesh", "blog": "howtodoinjava"}.items():
    print(f"Key: {key}, Value: {value}")

stock = {"tea": 0, "milk": 4, "sugar": 0}
for item in list(stock):
    if stock[item] == 0:
        del stock[item]
left = stock                           # {'milk': 4}
print('left', '=', repr(left))

d = {"name": "Lokesh", "blog": "howtodoinjava"}
keys = d.keys()
d["age"] = 39
live = list(keys)                      # ['name', 'blog', 'age']
print('live', '=', repr(live))
items_view = d.items()                 # dict_items([('name', 'Lokesh'), ('blog', 'howtodoinjava'), ('age', 39)])
print('items_view', '=', repr(items_view))

d = {"name": "Lokesh", "blog": "howtodoinjava"}
age = d.setdefault("age", 39)          # 39, inserted
print('age', '=', repr(age))
name = d.setdefault("name", "Alex")    # 'Lokesh', unchanged
print('name', '=', repr(name))

groups = {}
for word in ["tea", "toast", "milk"]:
    groups.setdefault(word[0], []).append(word)
by_letter = groups                     # {'t': ['tea', 'toast'], 'm': ['milk']}
print('by_letter', '=', repr(by_letter))

d = {"name": "Lokesh", "blog": "howtodoinjava"}
last = d.popitem()                     # ('blog', 'howtodoinjava')
print('last', '=', repr(last))

counts = dict.fromkeys(("key1", "key2", "key3"), 0)   # {'key1': 0, 'key2': 0, 'key3': 0}
print('counts', '=', repr(counts))
shared = dict.fromkeys(["a", "b"], [])
shared["a"].append(1)                  # shared is {'a': [1], 'b': [1]}
separate = {k: [] for k in ["a", "b"]} # one list per key
print('separate', '=', repr(separate))

words = "the cat and the hat and the bat".split()
counts = {}
for w in words:
    counts[w] = counts.get(w, 0) + 1
# counts is {'the': 3, 'cat': 1, 'and': 2, 'hat': 1, 'bat': 1}
top = Counter(words).most_common(2)     # [('the', 3), ('and', 2)]
print('top', '=', repr(top))

orders = [("alice", 30), ("bob", 15), ("alice", 20)]
by_customer = defaultdict(list)
for customer, amount in orders:
    by_customer[customer].append(amount)
totals = {c: sum(a) for c, a in by_customer.items()}   # {'alice': 50, 'bob': 15}
print('totals', '=', repr(totals))

scores = {"bob": 72, "alice": 91, "carl": 85}
by_score = dict(sorted(scores.items(), key=lambda kv: kv[1], reverse=True))
# {'alice': 91, 'carl': 85, 'bob': 72}
