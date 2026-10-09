import sys

v1 = (3, 12, 4)
v2 = (3, 13, 0)
older = v1 < v2        # True, decided by 12 < 13
print('older', '=', repr(older))
equal = v1 == (3, 12, 4)   # True
print('equal', '=', repr(equal))

a = (1, 2, 3) < (1, 2, 4)      # True, the third elements decide
print('a', '=', repr(a))
b = (1, 9, 9) < (2, 0, 0)      # True, the first elements decide
print('b', '=', repr(b))
c = (1, 2) < (1, 2, 0)         # True, the shorter tuple is smaller
print('c', '=', repr(c))
d = (1,) == (1.0,)             # True, 1 == 1.0
print('d', '=', repr(d))

same = (1, 2, 3) == (1, 2, "3")      # False, no error
print('same', '=', repr(same))
early = (1, "a") < (2, 2)            # True, decided before the string is reached
print('early', '=', repr(early))
try:
    bad = (1, "a") < (1, 2)
except Exception as e:
    print(type(e).__name__ + ':', e)

t1, t2 = (1, 5), (2, 0)
lexical = t1 < t2                                   # True
print('lexical', '=', repr(lexical))
every = all(x < y for x, y in zip(t1, t2))          # False, 5 is not < 0
print('every', '=', repr(every))

players = [("Ana", 90), ("Lokesh", 95), ("Bea", 90)]
ranked = sorted(players, key=lambda p: (-p[1], p[0]))
# [('Lokesh', 95), ('Ana', 90), ('Bea', 90)]


def version(text):
    return tuple(int(part) for part in text.split("."))

text_order = "3.9" > "3.10"                    # True, wrong
print('text_order', '=', repr(text_order))
tuple_order = version("3.9") > version("3.10")  # False, right
print('tuple_order', '=', repr(tuple_order))
new_enough = sys.version_info >= (3, 11)       # True on Python 3.14
print('new_enough', '=', repr(new_enough))
