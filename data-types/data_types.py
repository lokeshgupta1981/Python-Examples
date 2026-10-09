

values = ["Alice", 30, 1.75, True, None, [1, 2], {"a": 1}]
types = [type(v).__name__ for v in values]
# ['str', 'int', 'float', 'bool', 'NoneType', 'list', 'dict']

name = "Alice"
greeting = 'Hello, World!'
message = name + ", " + greeting      # 'Alice, Hello, World!'
print('message', '=', repr(message))
substring = message[0:5]              # 'Alice'
print('substring', '=', repr(substring))
shout = f"{name.upper()}!"            # 'ALICE!'
print('shout', '=', repr(shout))

x = 2                    # int
print('x', '=', repr(x))
y = 2.5                  # float
print('y', '=', repr(y))
z = 100 + 3j             # complex
print('z', '=', repr(z))
big = 2 ** 100           # 1267650600228229401496703205376, no overflow
print('big', '=', repr(big))
imprecise = 0.1 + 0.2    # 0.30000000000000004
print('imprecise', '=', repr(imprecise))
hex_int = 0xFF           # 255, also 0b for binary and 0o for octal
print('hex_int', '=', repr(hex_int))
sci = 1.5e3              # 1500.0, scientific notation
print('sci', '=', repr(sci))

my_list = [1, "apple", 3.14, [4, 5]]
my_tuple = (1, "apple", 3.14)
my_range = range(1, 6)              # 1, 2, 3, 4, 5 (the stop value is excluded)
print('my_range', '=', repr(my_range))
as_list = list(my_range)            # [1, 2, 3, 4, 5]
print('as_list', '=', repr(as_list))

person = {"name": "Alice", "age": 30}
age = person["age"]                  # 30
print('age', '=', repr(age))
grades = {"math": 95, "history": 85}
grades["science"] = 90               # add a pair

num_set = {1, 2, 3, 2}               # {1, 2, 3}
print('num_set', '=', repr(num_set))
char_set = set("banana")              # {'b', 'a', 'n'}, order may vary
print('char_set', '=', repr(char_set))
immutable_set = frozenset([1, 2, 3])
empty = set()                         # {} creates an empty dict
print('empty', '=', repr(empty))

x = True
check = 5 > 6                # False
print('check', '=', repr(check))
total = True + True          # 2
print('total', '=', repr(total))
truthy = bool(1)             # True
print('truthy', '=', repr(truthy))
falsy = bool(0)              # False
print('falsy', '=', repr(falsy))
empty_list = bool([])        # False, empty collections are falsy
print('empty_list', '=', repr(empty_list))

my_bytes = b"Hello"
first = my_bytes[0]                       # 72, an int
print('first', '=', repr(first))
text = my_bytes.decode("utf-8")           # 'Hello'
print('text', '=', repr(text))
my_bytearray = bytearray(b"Hello")
my_bytearray[0] = 74                      # bytearray(b'Jello')
view = memoryview(my_bytearray)[1:3]
part = bytes(view)                        # b'el'
print('part', '=', repr(part))

def log(msg):
    print(msg)

result = log("saved")         # prints saved
print('result', '=', repr(result))
no_value = result is None     # True
print('no_value', '=', repr(no_value))

x = 5
kind = type(x)                          # <class 'int'>
print('kind', '=', repr(kind))
name = type("howtodoinjava.com").__name__   # 'str'
print('name', '=', repr(name))
is_num = isinstance(x, (int, float))    # True
print('is_num', '=', repr(is_num))
is_int_bool = isinstance(True, int)     # True, bool is a subclass of int
print('is_int_bool', '=', repr(is_int_bool))

s = "tea"
t = s
s += "s"
strings = (s, t)              # ('teas', 'tea'), t is unchanged
print('strings', '=', repr(strings))

a = [1, 2]
b = a
a.append(3)
lists = (a, b)                # ([1, 2, 3], [1, 2, 3]), b sees the change
print('lists', '=', repr(lists))

product = {
    "sku": "TEA-01",                # str
    "price": 3.5,                   # float
    "stock": 120,                   # int
    "active": True,                 # bool
    "sizes": ("S", "M", "L"),       # tuple, fixed options
    "tags": {"green", "organic"},   # set, unique labels
    "discount": None,               # NoneType, not set yet
    "thumbnail": b"\x89PNG",        # bytes, binary data
}
summary = {k: type(v).__name__ for k, v in product.items()}
in_stock = product["active"] and product["stock"] > 0     # True
print('in_stock', '=', repr(in_stock))
