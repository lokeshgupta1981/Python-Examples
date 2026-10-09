import keyword
import calendar as cal
import math
from math import pi, floor
import asyncio

count = len(keyword.kwlist)         # 35
print('count', '=', repr(count))
soft = keyword.softkwlist           # ['_', 'case', 'match', 'type']
print('soft', '=', repr(soft))
reserved = keyword.iskeyword("for") # True
print('reserved', '=', repr(reserved))



result = 5 < 6           # True
print('result', '=', repr(result))
as_number = True + 1      # 2
print('as_number', '=', repr(as_number))

result = 5 > 6           # False
print('result', '=', repr(result))

value = None
missing = value is None   # True
print('missing', '=', repr(missing))

both = 5 > 3 and 5 > 10     # False
print('both', '=', repr(both))
first_falsy = 0 and 99      # 0
print('first_falsy', '=', repr(first_falsy))

either = 5 > 3 or 5 > 10    # True
print('either', '=', repr(either))
name = "" or "guest"        # 'guest'
print('name', '=', repr(name))

flag = not False            # True
print('flag', '=', repr(flag))
empty = not []              # True
print('empty', '=', repr(empty))

fruits = ["apple", "banana", "cherry"]
has_banana = "banana" in fruits     # True
print('has_banana', '=', repr(has_banana))

a = ["apple", "banana"]
b = ["apple", "banana"]
c = a
same_value = a == b         # True
print('same_value', '=', repr(same_value))
same_object = a is b        # False
print('same_object', '=', repr(same_object))
alias = a is c              # True
print('alias', '=', repr(alias))

x = 5
if x > 3:
    print("x is greater than 3")

i = 0
if i > 0:
    print("Positive")
elif i == 0:
    print("Zero")
else:
    print("Negative")

try:
    n = int("42")
except ValueError:
    print("not a number")
else:
    print("parsed", n)

squares = []
for n in range(1, 4):
    squares.append(n * n)
result = squares            # [1, 4, 9]
print('result', '=', repr(result))

x = 0
while x < 3:
    x += 1
final = x                   # 3
print('final', '=', repr(final))

for i in range(1, 9):
    if i == 3:
        break
stopped_at = i              # 3
print('stopped_at', '=', repr(stopped_at))

odds = []
for i in range(6):
    if i % 2 == 0:
        continue
    odds.append(i)
result = odds               # [1, 3, 5]
print('result', '=', repr(result))

def greet(name):
    return f"Hello, {name}"

message = greet("Alex")     # 'Hello, Alex'
print('message', '=', repr(message))

class User:
    def __init__(self, name):
        self.name = name

user = User("John")
name = user.name            # 'John'
print('name', '=', repr(name))

with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("hello")
closed = f.closed           # True, the file was closed
print('closed', '=', repr(closed))

first_month = cal.month_name[1]     # 'January'
print('first_month', '=', repr(first_month))

def todo():
    pass

returned = todo()           # None
print('returned', '=', repr(returned))

double = lambda n: n * 2
result = double(4)          # 8
print('result', '=', repr(result))
by_len = sorted(["kiwi", "fig", "apple"], key=lambda w: len(w))   # ['fig', 'kiwi', 'apple']
print('by_len', '=', repr(by_len))

root = math.sqrt(16)        # 4.0
print('root', '=', repr(root))

value = floor(pi)           # 3
print('value', '=', repr(value))

items = [1, 2, 3]
del items[0]
left = items                # [2, 3]
print('left', '=', repr(left))

counter = 0

def bump():
    global counter
    counter += 1

bump()
total = counter             # 1
print('total', '=', repr(total))

def outer():
    count = 0
    def inner():
        nonlocal count
        count += 1
    inner()
    return count

result = outer()            # 1
print('result', '=', repr(result))

def area(w, h):
    return w * h

result = area(3, 4)         # 12
print('result', '=', repr(result))

def countdown(n):
    while n > 0:
        yield n
        n -= 1

values = list(countdown(3))   # [3, 2, 1]
print('values', '=', repr(values))

try:
    result = 10 / 0
except ZeroDivisionError:
    result = None

try:
    int("abc")
except ValueError as e:
    message = str(e)          # "invalid literal for int() with base 10: 'abc'"

def withdraw(balance, amount):
    if amount > balance:
        raise ValueError("insufficient funds")
    return balance - amount

steps = []
try:
    steps.append("work")
finally:
    steps.append("cleanup")
done = steps                # ['work', 'cleanup']
print('done', '=', repr(done))

def average(nums):
    assert nums, "nums must not be empty"
    return sum(nums) / len(nums)

avg = average([2, 4])       # 3.0
print('avg', '=', repr(avg))

async def ticker(n):
    for i in range(n):
        yield i                    # an async generator

async def collect():
    return [i async for i in ticker(3)]

async def fetch(n):
    await asyncio.sleep (0.01)
    return n * 10

async def main():
    return await asyncio.gather(fetch(1), fetch(2))

results = asyncio.run(main())   # [10, 20]
print('results', '=', repr(results))
ticks = asyncio.run(collect())   # [0, 1, 2]
print('ticks', '=', repr(ticks))

def http_status(code):
    match code:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case _:
            return "Other"

match = http_status(404)        # 'Not Found', match is still a valid name
print('match', '=', repr(match))

def safe_name(raw):
    name = raw.strip().replace("-", "_").replace(" ", "_")
    if keyword.iskeyword(name) or keyword.issoftkeyword(name):
        name += "_"
    if not name.isidentifier():
        name = "f_" + name
    return name

columns = ["id", "from", "class", "first name", "2nd-line", "type"]
fields = [safe_name(c) for c in columns]
# ['id', 'from_', 'class_', 'first_name', 'f_2nd_line', 'type_']
