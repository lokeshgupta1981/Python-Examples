from collections import namedtuple

point = (3, 4)
x, y = point                 # unpacking, x = 3 and y = 4
print('x', '=', repr(x))
print('y', '=', repr(y))
first = point[0]             # 3
print('first', '=', repr(first))
size = len(point)            # 2
print('size', '=', repr(size))

tuple1 = ()                      # empty tuple
print('tuple1', '=', repr(tuple1))
tuple2 = (1, "2", 3.0)
tuple3 = 1, "2", 3.0             # same as tuple2
print('tuple3', '=', repr(tuple3))
tuple4 = tuple([1, 2, 3])        # (1, 2, 3)
print('tuple4', '=', repr(tuple4))
tuple5 = tuple("abc")            # ('a', 'b', 'c')
print('tuple5', '=', repr(tuple5))

not_a_tuple = ("hello")           # 'hello', a str
print('not_a_tuple', '=', repr(not_a_tuple))
one_element = ("hello",)          # ('hello',)
print('one_element', '=', repr(one_element))
kind = type(not_a_tuple).__name__ # 'str'
print('kind', '=', repr(kind))

nested = ("hello", ("python", "world"))
inner = nested[1][0]              # 'python'
print('inner', '=', repr(inner))

letters = ("a", "b", "c", "d", "e", "f")
a0 = letters[0]          # 'a'
print('a0', '=', repr(a0))
a1 = letters[1]          # 'b'
print('a1', '=', repr(a1))
last = letters[-1]       # 'f'
print('last', '=', repr(last))
second_last = letters[-2]  # 'e'
print('second_last', '=', repr(second_last))
head = letters[0:3]      # ('a', 'b', 'c')
print('head', '=', repr(head))
middle = letters[-3:-1]  # ('d', 'e')
print('middle', '=', repr(middle))

nested = ("a", "b", "c", ("d", "e", "f"))
inner = nested[3]        # ('d', 'e', 'f')
print('inner', '=', repr(inner))
inner_first = nested[3][0]   # 'd'
print('inner_first', '=', repr(inner_first))
inner_slice = nested[3][0:2] # ('d', 'e')
print('inner_slice', '=', repr(inner_slice))

colors = ("red", "green")
updated = colors + ("blue",)          # ('red', 'green', 'blue')
print('updated', '=', repr(updated))
replaced = (colors[0], "lime")        # ('red', 'lime')
print('replaced', '=', repr(replaced))

record = ("alex", [90, 85])
record[1].append(70)                  # allowed, the list changes
scores = record[1]                    # [90, 85, 70]
print('scores', '=', repr(scores))

letters = ("a", "b", "c")
for i, letter in enumerate(letters):
    print(i, letter)

letters = ("a", "b", "c", "d", "e", "f")
has_a = "a" in letters          # True
print('has_a', '=', repr(has_a))
no_p = "p" not in letters       # True
print('no_p', '=', repr(no_p))

letters = ("a", "c", "b", "d", "f", "e")
as_list = sorted(letters)                 # ['a', 'b', 'c', 'd', 'e', 'f']
print('as_list', '=', repr(as_list))
as_tuple = tuple(sorted(letters))         # ('a', 'b', 'c', 'd', 'e', 'f')
print('as_tuple', '=', repr(as_tuple))
descending = tuple(sorted(letters, reverse=True))   # ('f', 'e', 'd', 'c', 'b', 'a')
print('descending', '=', repr(descending))

pair = ("a", "b")
repeated = pair * 3                      # ('a', 'b', 'a', 'b', 'a', 'b')
print('repeated', '=', repr(repeated))
joined = ("a", "b", "c") + ("d", "e", "f")   # ('a', 'b', 'c', 'd', 'e', 'f')
print('joined', '=', repr(joined))

letters = ("a", "b", "c")       # packing
print('letters', '=', repr(letters))
(x, y, z) = letters             # unpacking, the brackets are optional
values = (x, y, z)              # ('a', 'b', 'c')
print('values', '=', repr(values))

first, *rest = (1, 2, 3, 4)
result = (first, rest)          # (1, [2, 3, 4])
print('result', '=', repr(result))

Record = namedtuple("Record", ["id", "name", "date"])
r1 = Record("1", "My Record", "12/12/2020")
by_index = r1[0]            # '1'
print('by_index', '=', repr(by_index))
by_name = r1.name           # 'My Record'
print('by_name', '=', repr(by_name))
changed = r1._replace(name="New")   # a new Record, r1 is unchanged
print('changed', '=', repr(changed))

nums = (4, 1, 2, 6, 9, 1)
count_1 = nums.count(1)       # 2
print('count_1', '=', repr(count_1))
pos_6 = nums.index(6)         # 3
print('pos_6', '=', repr(pos_6))
length = len(nums)            # 6
print('length', '=', repr(length))
smallest = min(nums)          # 1
print('smallest', '=', repr(smallest))
largest = max(nums)           # 9
print('largest', '=', repr(largest))
total = sum(nums)             # 23
print('total', '=', repr(total))
any_zero = any((0, "", None)) # False, no item is truthy
print('any_zero', '=', repr(any_zero))
any_one = any((0, 1))         # True
print('any_one', '=', repr(any_one))

tiles = {(0, 0): "start", (2, 3): "treasure"}
found = tiles.get((2, 3))                  # 'treasure'
print('found', '=', repr(found))

def min_max(values):
    return min(values), max(values)        # a function returns a tuple

low, high = min_max([7, 2, 9, 4])          # 2 and 9
print('low', '=', repr(low))
print('high', '=', repr(high))
