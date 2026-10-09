import keyword
from typing import Final

age = 25                 # int
print('age', '=', repr(age))
name = "Alice"           # str
print('name', '=', repr(name))
scores = [90, 85, 88]    # list
print('scores', '=', repr(scores))
age = "unknown"          # the same name now refers to a str
print('age', '=', repr(age))

is_kw = keyword.iskeyword("class")        # True
print('is_kw', '=', repr(is_kw))
valid = "place_2".isidentifier()          # True
print('valid', '=', repr(valid))
invalid = "2nd_place".isidentifier()      # False
print('invalid', '=', repr(invalid))

age = 25
name = "Alice"
scores = [90, 85, 88, 92]
author = 'Lokesh'
blog_name = "howtodoinjava"

i = j = k = 20
values = (i, j, k)          # (20, 20, 20)
print('values', '=', repr(values))

x, y, z = 10, 20, 30
x, y = y, x                 # swap
print('x', '=', repr(x))
print('y', '=', repr(y))
result = (x, y, z)          # (20, 10, 30)
print('result', '=', repr(result))

index = 10
index = 20
index = "NA"
current = index             # 'NA'
print('current', '=', repr(current))
kind = type(index).__name__ # 'str'
print('kind', '=', repr(kind))

a = [1, 2]
b = a                       # b refers to the same list
print('b', '=', repr(b))
b.append(3)
shared = a                  # [1, 2, 3], a changed too
print('shared', '=', repr(shared))
same = a is b               # True
print('same', '=', repr(same))

c = a.copy()                # a new list
print('c', '=', repr(c))
copied = c is a             # False
print('copied', '=', repr(copied))

x = 10
y = x
y += 1
pair = (x, y)               # (10, 11)
print('pair', '=', repr(pair))

def my_function():
    x = 10
    print("Inside the function, x =", x)

my_function()

y = 20

def my_function():
    global y
    print("Inside the function, y =", y)
    y = 30

my_function()
print("Outside the function, y =", y)

def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

counter = make_counter()
counter()
calls = counter()           # 2
print('calls', '=', repr(calls))

total = 100

def add_tax():
    total = total * 1.2     # reads the local total before it has a value
    return total

retries: int = 3
names: list[str] = ["tea", "milk"]
MAX_SIZE: Final = 100        # a checker reports any reassignment

temp = [1, 2, 3]
del temp
exists = "temp" in dir()    # False
print('exists', '=', repr(exists))

qty = "3"
price = 2.5
total = int(qty) * price        # 7.5
print('total', '=', repr(total))
label = "Total: " + str(total)  # 'Total: 7.5'
print('label', '=', repr(label))
flag = bool("")                 # False, an empty string is falsy
print('flag', '=', repr(flag))

length = 10
width = 5
area = length * width
print("The area of the rectangle is:", area)

first_name = "John"
last_name = "Doe"
full_name = f"{first_name} {last_name}"     # 'John Doe'
print('full_name', '=', repr(full_name))

TAX_RATE = 0.08
cart = [("tea", 3.50, 2), ("milk", 1.20, 1)]

subtotal = 0.0
for name, price, qty in cart:
    subtotal += price * qty

total = round(subtotal * (1 + TAX_RATE), 2)    # 8.86
print('total', '=', repr(total))
