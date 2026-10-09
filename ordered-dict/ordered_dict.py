from collections import OrderedDict

user = OrderedDict(name="lokesh", id=100, email="admin@gmail.com")
user.move_to_end("name")            # keys: id, email, name
first = user.popitem(last=False)    # ('id', 100)
print('first', '=', repr(first))

user = OrderedDict()
user["name"] = "lokesh"
user["id"] = 100
user["email"] = "admin@gmail.com"
user["email"] = "admin@howtodoinjava.com"   # position unchanged
user["location"] = "India"                  # added at the end
keys = list(user)                           # ['name', 'id', 'email', 'location']
print('keys', '=', repr(keys))
defaults = OrderedDict.fromkeys(["id", "name"], None)   # OrderedDict({'id': None, 'name': None})
print('defaults', '=', repr(defaults))

od = OrderedDict.fromkeys("abcde")
od.move_to_end("b")                  # a c d e b
od.move_to_end("e", last=False)      # e a c d b
last = od.popitem()                  # ('b', None)
print('last', '=', repr(last))
first = od.popitem(last=False)       # ('e', None)
print('first', '=', repr(first))
try:
    missing = od.move_to_end("z")
except Exception as e:
    print(type(e).__name__ + ':', e)

a = OrderedDict([("x", 1), ("y", 2)])
b = OrderedDict([("y", 2), ("x", 1)])
same_od = a == b                     # False, order differs
print('same_od', '=', repr(same_od))
same_dict = dict(a) == dict(b)       # True
print('same_dict', '=', repr(same_dict))
mixed = a == {"y": 2, "x": 1}        # True, a plain dict ignores order
print('mixed', '=', repr(mixed))

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = OrderedDict()

    def get(self, key):
        if key not in self.data:
            return None
        self.data.move_to_end(key)
        return self.data[key]

    def put(self, key, value):
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)

cache = LRUCache(2)
cache.put("a", 1)
cache.put("b", 2)
cache.get("a")                       # touches a, so b is now the oldest
cache.put("c", 3)                    # evicts b
keys = list(cache.data)              # ['a', 'c']
print('keys', '=', repr(keys))
