import re
from itertools import filterfalse

numbers = [1, 2, 3, 4, 5, 6]
evens = list(filter(lambda n: n % 2 == 0, numbers))     # [2, 4, 6]
print('evens', '=', repr(evens))



result = filter(lambda n: n > 2, [1, 2, 3, 4])
kind = type(result).__name__          # 'filter'
print('kind', '=', repr(kind))
first = list(result)                  # [3, 4]
print('first', '=', repr(first))
second = list(result)                 # [], the iterator is used up
print('second', '=', repr(second))

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
filtered_numbers = list(filter(lambda x: x % 2 == 0, numbers))
print(filtered_numbers)

loop_result = []
for x in numbers:
    if x % 2 == 0:
        loop_result.append(x)          # same result as filter()

strings = ["apple", "banana", "orange", "grape", "kiwi"]
pattern = "an"
filtered_strings_list = list(filter(lambda x: pattern in x, strings))
print(filtered_strings_list)

codes = ["tea-01", "milk", "jam-22", "bread-x"]
numbered = list(filter(re.compile(r"-\d+$").search, codes))   # ['tea-01', 'jam-22']
print('numbered', '=', repr(numbered))

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

people = [Person("Alice", 30), Person("Bob", 25), Person("Charlie", 35)]
selected_people = list(filter(lambda p: p.age > 28, people))
for person in selected_people:
    print(person.name, person.age)

rows = [[1, 2], [3], [4, 5, 6]]
long_rows = list(filter(lambda r: len(r) > 1, rows))           # [[1, 2], [4, 5, 6]]
print('long_rows', '=', repr(long_rows))
odd_items = [list(filter(lambda n: n % 2, r)) for r in rows]   # [[1], [3], [5]]
print('odd_items', '=', repr(odd_items))

main_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
filter_list = [2, 4, 6, 8, 10]

allowed = set(filter_list)
kept = list(filter(lambda x: x in allowed, main_list))          # [2, 4, 6, 8, 10]
print('kept', '=', repr(kept))
removed = list(filter(lambda x: x not in allowed, main_list))   # [1, 3, 5, 7, 9]
print('removed', '=', repr(removed))

def is_wanted(pair):
    idx, num = pair
    return num > 5 and idx % 2 == 0

numbers = [3, 8, 2, 10, 6, 4, 7, 9]
pairs = filter(is_wanted, enumerate(numbers))
filtered_numbers = [num for idx, num in pairs]
print(filtered_numbers)

data = ["tea", None, "", "milk", [], "sugar"]
clean = list(filter(None, data))      # ['tea', 'milk', 'sugar']
print('clean', '=', repr(clean))

readings = [0, None, 12, None, 7]
dropped_zero = list(filter(None, readings))                    # [12, 7]
print('dropped_zero', '=', repr(dropped_zero))
kept_zero = list(filter(lambda v: v is not None, readings))    # [0, 12, 7]
print('kept_zero', '=', repr(kept_zero))

def filter_condition(value):
    return value is not None and value != "" and value % 2 == 0

data = [1, None, 3, None, "", 6, "", 8, 9, None]
filtered_data = list(filter(filter_condition, data))    # [6, 8]
print('filtered_data', '=', repr(filtered_data))

scores = [45, 82, 67, 30, 91]
passed = list(filter(lambda s: s >= 50, scores))         # [82, 67, 91]
print('passed', '=', repr(passed))
failed = list(filterfalse(lambda s: s >= 50, scores))    # [45, 30]
print('failed', '=', repr(failed))

words = ["Tea", "", "milk", "", "Sugar"]
with_filter = list(filter(None, words))           # ['Tea', 'milk', 'Sugar']
print('with_filter', '=', repr(with_filter))
with_comprehension = [w for w in words if w]      # ['Tea', 'milk', 'Sugar']
print('with_comprehension', '=', repr(with_comprehension))
capitals = list(filter(str.istitle, words))       # ['Tea', 'Sugar']
print('capitals', '=', repr(capitals))

orders = [
    {"id": 101, "status": "paid", "total": 120.0},
    {"id": 102, "status": "pending", "total": 80.0},
    {"id": 103, "status": "paid", "total": 35.5},
    {"id": 104, "status": "paid", "total": 64.0},
]

def is_large_paid(order):
    return order["status"] == "paid" and order["total"] > 50

large_paid_ids = [o["id"] for o in filter(is_large_paid, orders)]   # [101, 104]
print('large_paid_ids', '=', repr(large_paid_ids))
revenue = sum(o["total"] for o in filter(is_large_paid, orders))    # 184.0
print('revenue', '=', repr(revenue))

items = [3, 0, 5, 0]
items[:] = filter(None, items)        # items is [3, 5]

stock = {"tea": 0, "milk": 4, "sugar": 2}
in_stock = dict(filter(lambda kv: kv[1] > 0, stock.items()))   # {'milk': 4, 'sugar': 2}
print('in_stock', '=', repr(in_stock))

first_big = next(filter(lambda n: n > 10, [4, 12, 30]), None)   # 12
print('first_big', '=', repr(first_big))
no_match = next(filter(lambda n: n > 99, [4, 12, 30]), None)    # None
print('no_match', '=', repr(no_match))
