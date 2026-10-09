import sys

nums = list(range(5))            # [0, 1, 2, 3, 4]
print('nums', '=', repr(nums))
evens = list(range(2, 10, 2))    # [2, 4, 6, 8]
print('evens', '=', repr(evens))

a = list(range(3))          # [0, 1, 2]
print('a', '=', repr(a))
b = list(range(2, 6))       # [2, 3, 4, 5]
print('b', '=', repr(b))
c = list(range(0, 10, 3))   # [0, 3, 6, 9]
print('c', '=', repr(c))
d = list(range(5, 2))       # [], start is already past stop
print('d', '=', repr(d))

down = list(range(10, 0, -3))      # [10, 7, 4, 1]
print('down', '=', repr(down))
same = list(reversed(range(4)))    # [3, 2, 1, 0]
print('same', '=', repr(same))
try:
    zero_step = range(1, 5, 0)
except Exception as e:
    print(type(e).__name__ + ':', e)


big = range(0, 10**12, 3)
count = len(big)                         # 333333333334
print('count', '=', repr(count))
size_range = sys.getsizeof(range(10**6)) # 48 bytes
print('size_range', '=', repr(size_range))
size_list = sys.getsizeof(list(range(10**6)))   # about 8 MB for the references alone
print('size_list', '=', repr(size_list))

r = range(0, 20, 3)          # 0 3 6 9 12 15 18
print('r', '=', repr(r))
first = r[0]                 # 0
print('first', '=', repr(first))
last = r[-1]                 # 18
print('last', '=', repr(last))
sub = r[2:5]                 # range(6, 15, 3)
print('sub', '=', repr(sub))
pos = r.index(9)             # 3
print('pos', '=', repr(pos))
has = 12 in r                # True
print('has', '=', repr(has))
equal = range(0) == range(5, 2)   # True, both are empty
print('equal', '=', repr(equal))

steps = [i / 10 for i in range(0, 5)]    # [0.0, 0.1, 0.2, 0.3, 0.4]
print('steps', '=', repr(steps))

items = ["tea", "milk", "rice"]
for i, item in enumerate(items, start=1):
    print(i, item)

records = list(range(1, 11))          # 10 records
print('records', '=', repr(records))
batches = [records[i:i + 4] for i in range(0, len(records), 4)]
# [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10]]
