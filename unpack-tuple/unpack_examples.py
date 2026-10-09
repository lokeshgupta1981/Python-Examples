scores = (90, 85, 77, 64, 50)
first, second, *rest = scores        # first = 90, second = 85, rest = [77, 64, 50]
print('first', '=', repr(first))
print('second', '=', repr(second))
print('rest', '=', repr(rest))

*head, last = scores                 # head = [90, 85, 77, 64], last = 50
print('head', '=', repr(head))
print('last', '=', repr(last))
first, *middle, last = scores        # middle = [85, 77, 64]
print('first', '=', repr(first))
print('middle', '=', repr(middle))
print('last', '=', repr(last))
a, b, *empty = (1, 2)                # empty = []
print('a', '=', repr(a))
print('b', '=', repr(b))
print('empty', '=', repr(empty))

first, _, third, _, _ = scores        # first = 90, third = 77
print('first', '=', repr(first))
print('_', '=', repr(_))
print('third', '=', repr(third))
print('_', '=', repr(_))
print('_', '=', repr(_))
first, *_, last = scores              # first = 90, last = 50
print('first', '=', repr(first))
print('_', '=', repr(_))
print('last', '=', repr(last))

try:
    a, b = (1, 2, 3)
except Exception as e:
    print(type(e).__name__ + ':', e)
try:
    a, b, c = (1, 2)
except Exception as e:
    print(type(e).__name__ + ':', e)
try:
    a, *b, c = (1,)
except Exception as e:
    print(type(e).__name__ + ':', e)

rows = [("tea", 4, 5, 3), ("milk", 2), ("rice", 9, 8)]
for name, *ratings in rows:
    print(name, ratings)

def min_max(values):
    return min(values), max(values)

low, high = min_max(scores)          # low = 50, high = 90
print('low', '=', repr(low))
print('high', '=', repr(high))

order = ("Lokesh", ("2026-11-02", "10:30"), 3)
name, (day, hour), qty = order       # day = '2026-11-02', hour = '10:30'
