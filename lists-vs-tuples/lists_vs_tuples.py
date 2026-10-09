import sys
from collections import namedtuple

cart = ["tea", "milk"]          # a list, can change
print('cart', '=', repr(cart))
cart.append("rice")             # ['tea', 'milk', 'rice']
point = (12.5, 7.0)             # a tuple, fixed
print('point', '=', repr(point))

nums = [1, 2, 3]
nums[0] = 10                # [10, 2, 3]
nums.append(4)              # [10, 2, 3, 4]

fixed = (1, 2, 3)
try:
    bad = fixed.append(4)
except Exception as e:
    print(type(e).__name__ + ':', e)
fixed2 = fixed + (4,)       # (1, 2, 3, 4), a new tuple
print('fixed2', '=', repr(fixed2))

record = ("Ana", [90, 85])
record[1].append(77)        # ('Ana', [90, 85, 77])

temps = {("Pune", "2026-10-09"): 31, ("Delhi", "2026-10-09"): 34}
pune = temps[("Pune", "2026-10-09")]     # 31
print('pune', '=', repr(pune))
try:
    bad_key = {[1, 2]: "x"}
except Exception as e:
    print(type(e).__name__ + ':', e)
try:
    bad_tuple = {(1, [2]): "x"}
except Exception as e:
    print(type(e).__name__ + ':', e)


t3 = sys.getsizeof((1, 2, 3))           # 72
print('t3', '=', repr(t3))
l3 = sys.getsizeof([1, 2, 3])           # 88
print('l3', '=', repr(l3))
t10 = sys.getsizeof(tuple(range(10)))   # 128
print('t10', '=', repr(t10))
l10 = sys.getsizeof(list(range(10)))    # 136
print('l10', '=', repr(l10))

not_tuple = (5)          # 5, an int
print('not_tuple', '=', repr(not_tuple))
one = (5,)               # (5,), a tuple
print('one', '=', repr(one))
also_one = 5,            # (5,), the comma is enough
print('also_one', '=', repr(also_one))
empty = ()               # (), the empty tuple
print('empty', '=', repr(empty))


Point = namedtuple("Point", ["x", "y"])
p = Point(12.5, 7.0)
x_value = p.x            # 12.5
print('x_value', '=', repr(x_value))
as_tuple = tuple(p)      # (12.5, 7.0)
print('as_tuple', '=', repr(as_tuple))
