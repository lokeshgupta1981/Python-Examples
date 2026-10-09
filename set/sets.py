

names = {"alex", "brian", "alex"}
size = len(names)                    # 2, the duplicate is dropped
print('size', '=', repr(size))
found = "brian" in names             # True
print('found', '=', repr(found))
unique = set([3, 1, 3, 2, 1])        # {1, 2, 3}
print('unique', '=', repr(unique))

names = {"alex", "brian", "charles"}               # curly braces
print('names', '=', repr(names))
names2 = set(("alex", "brian", "charles"))         # set() constructor
print('names2', '=', repr(names2))
letters = set("hello")                             # {'h', 'e', 'l', 'o'}, order may vary
print('letters', '=', repr(letters))
empty = set()                                      # {} creates an empty dict, not a set
print('empty', '=', repr(empty))

names = {"alex", "brian", "charles"}
for name in sorted(names):
    print(name)

names = {"alex", "brian", "charles"}
has_brian = "brian" in names         # True
print('has_brian', '=', repr(has_brian))
has_david = "david" in names         # False
print('has_david', '=', repr(has_david))

names = {"alex", "brian", "charles"}
names.add("david")
names.add("alex")                    # no effect, already present
names.update(["evan", "frank"], ("george",))
result = sorted(names)
# ['alex', 'brian', 'charles', 'david', 'evan', 'frank', 'george']

names = {"alex", "brian", "charles", "evan", "frank"}
names.remove("frank")
names.discard("evan")
names.discard("zoe")                 # no error
any_name = names.pop()               # one of the remaining names
print('any_name', '=', repr(any_name))
left = len(names)                    # 2
print('left', '=', repr(left))
names.clear()
after = names                        # set()
print('after', '=', repr(after))

a = {"alex", "brian", "charles"}
b = {"alex", "brian", "david"}
union = sorted(a | b)                # ['alex', 'brian', 'charles', 'david']
print('union', '=', repr(union))
common = sorted(a & b)               # ['alex', 'brian']
print('common', '=', repr(common))
only_a = sorted(a - b)               # ['charles']
print('only_a', '=', repr(only_a))
not_shared = sorted(a ^ b)           # ['charles', 'david']
print('not_shared', '=', repr(not_shared))
with_list = sorted(a.union(["zoe"])) # ['alex', 'brian', 'charles', 'zoe']
print('with_list', '=', repr(with_list))

base = {"alex", "brian", "charles"}
other = {"alex", "brian", "david"}

s1 = set(base)
s1.difference_update(other)              # s1 is {'charles'}
s2 = set(base)
s2.intersection_update(other)            # s2 has 'alex' and 'brian'
s3 = set(base)
s3.symmetric_difference_update(other)    # s3 has 'charles' and 'david'
results = (sorted(s1), sorted(s2), sorted(s3))
# (['charles'], ['alex', 'brian'], ['charles', 'david'])

small = {"alex", "brian"}
big = {"alex", "brian", "charles"}
disjoint = small.isdisjoint({"david"})   # True
print('disjoint', '=', repr(disjoint))
subset = small.issubset(big)              # True
print('subset', '=', repr(subset))
superset = small.issuperset(big)          # False
print('superset', '=', repr(superset))
proper = small < big                      # True, a proper subset
print('proper', '=', repr(proper))

frozen = frozenset({"read", "write"})
roles = {frozen: "editor"}                 # a frozenset as a dict key
print('roles', '=', repr(roles))
lengths = {len(w) for w in ["tea", "milk", "jam"]}   # {3, 4}
print('lengths', '=', repr(lengths))

user_perms = {"read", "write", "comment"}
required = {"read", "write", "delete"}

allowed = required <= user_perms                 # False
print('allowed', '=', repr(allowed))
missing = sorted(required - user_perms)          # ['delete']
print('missing', '=', repr(missing))

emails = ["a@x.com", "B@x.com", "a@x.com", "b@x.com"]
unique_emails = sorted({e.lower() for e in emails})   # ['a@x.com', 'b@x.com']
print('unique_emails', '=', repr(unique_emails))
