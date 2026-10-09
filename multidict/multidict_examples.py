from multidict import MultiDict
from multidict import MultiDict, CIMultiDict, MultiDictProxy
from multidict import CIMultiDict, MultiDict, MultiDictProxy
from collections import defaultdict
from urllib.parse import parse_qsl, urlencode

md = MultiDict()
md["key"] = "value"
md.add("key", "another_value")         # a second value for the same key
first = md["key"]                      # 'value'
print('first', '=', repr(first))
values = md.getall("key")              # ['value', 'another_value']
print('values', '=', repr(values))
md.update({"new_key": "new_value"})    # adds or replaces new_key
del md["key"]                          # removes every value of key
popped = md.popall("new_key")          # ['new_value']
print('popped', '=', repr(popped))
md.clear()

colors = {"Monday": "Blue", "Tuesday": "Red"}
colors["Monday"] = "Yellow"            # replaces Blue
plain = colors                         # {'Monday': 'Yellow', 'Tuesday': 'Red'}
print('plain', '=', repr(plain))

colors = MultiDict()
colors.add("Monday", "Blue")
colors.add("Monday", "Yellow")
colors.add("Tuesday", "Red")
monday = colors.getall("Monday")       # ['Blue', 'Yellow']
print('monday', '=', repr(monday))
keys = list(colors.keys())             # ['Monday', 'Monday', 'Tuesday']
print('keys', '=', repr(keys))
count = len(colors)                    # 3, the number of pairs
print('count', '=', repr(count))



empty = MultiDict()
with_items = MultiDict([("key", "value1"), ("key", "value2"), ("new_key", "value3")])
from_kwargs = MultiDict(page="2", sort="date")
pairs = list(with_items.items())
# [('key', 'value1'), ('key', 'value2'), ('new_key', 'value3')]

md = MultiDict()
md["key"] = "value"
md.add("key", "another_value")
md.extend([("key", "third"), ("tag", "x")])
first = md.setdefault("key", "default")         # 'value', key exists
print('first', '=', repr(first))
inserted = md.setdefault("key_default", "d")    # 'd', inserted
print('inserted', '=', repr(inserted))
all_values = md.getall("key")                   # ['value', 'another_value', 'third']
print('all_values', '=', repr(all_values))
md["key"] = "only"
after_assign = md.getall("key")                 # ['only']
print('after_assign', '=', repr(after_assign))

md = MultiDict()
md.add("fruit", "apple")
md.add("fruit", "banana")
md.add("fruit", "orange")
by_index = md["fruit"]                          # 'apple'
print('by_index', '=', repr(by_index))
by_get = md.get("fruit", "No fruit")            # 'apple'
print('by_get', '=', repr(by_get))
by_getone = md.getone("fruit", "No fruit")      # 'apple'
print('by_getone', '=', repr(by_getone))
by_getall = md.getall("fruit")                  # ['apple', 'banana', 'orange']
print('by_getall', '=', repr(by_getall))
missing = md.getall("veg", [])                  # []
print('missing', '=', repr(missing))

md = MultiDict([("a", 1), ("b", 2), ("a", 3)])
md.update({"a": 9})
updated = list(md.items())          # [('a', 9), ('b', 2)]
print('updated', '=', repr(updated))

md2 = MultiDict([("a", 1)])
md2.merge({"a": 2, "z": 3})
merged = list(md2.items())          # [('a', 1), ('z', 3)]
print('merged', '=', repr(merged))

md = MultiDict([("key", "value"), ("key", "another_value")])
values = md.popall("key")
values[values.index("another_value")] = "new_value"
md.extend(("key", v) for v in values)
result = md.getall("key")           # ['value', 'new_value']
print('result', '=', repr(result))

md = MultiDict([("a", 1), ("b", 2), ("a", 3)])
first_a = md.popone("a")            # 1, md has b=2 and a=3
print('first_a', '=', repr(first_a))
last_pair = md.popitem()            # ('a', 3)
print('last_pair', '=', repr(last_pair))
fallback = md.pop("x", "default")   # 'default'
print('fallback', '=', repr(fallback))
md.add("c", 4)
del md["c"]
left = list(md.items())             # [('b', 2)]
print('left', '=', repr(left))

headers = CIMultiDict()
headers.add("Set-Cookie", "a=1")
headers.add("set-cookie", "b=2")
cookies = headers.getall("SET-COOKIE")      # ['a=1', 'b=2']
print('cookies', '=', repr(cookies))

read_only = MultiDictProxy(MultiDict(page="2"))

groups = defaultdict(list)
for day, color in [("Monday", "Blue"), ("Tuesday", "Red"), ("Monday", "Yellow")]:
    groups[day].append(color)
grouped = dict(groups)        # {'Monday': ['Blue', 'Yellow'], 'Tuesday': ['Red']}
print('grouped', '=', repr(grouped))

params = MultiDict(parse_qsl("tag=py&tag=web&page=2"))
tags = params.getall("tag")                 # ['py', 'web']
print('tags', '=', repr(tags))
page = int(params.get("page", "1"))         # 2
print('page', '=', repr(page))
params["page"] = "3"
next_query = urlencode(list(params.items()))   # 'tag=py&tag=web&page=3'
print('next_query', '=', repr(next_query))

md = MultiDict([("tag", "a"), ("tag", "b")])
first_only = dict(md)                                   # {'tag': 'a'}
print('first_only', '=', repr(first_only))
all_values = {k: md.getall(k) for k in set(md.keys())}  # {'tag': ['a', 'b']}
print('all_values', '=', repr(all_values))
