mytuple = (0, 1, False)
result = all(mytuple)          # False, because 0 is falsy
print('result', '=', repr(result))

t1 = all((1, 2, True))            # True
print('t1', '=', repr(t1))
t2 = all((0, 1, False))           # False
print('t2', '=', repr(t2))
l = all([1, 2, 3])                # True
print('l', '=', repr(l))
d1 = all({0: "False"})            # False, the key 0 is falsy
print('d1', '=', repr(d1))
d2 = all({1: "True", 2: "True"})  # True
print('d2', '=', repr(d2))
s1 = all("abc")                   # True
print('s1', '=', repr(s1))
s2 = all("")                      # True, an empty string has no characters
print('s2', '=', repr(s2))

def all_like(iterable):
    for element in iterable:
        if not element:
            return False
    return True

empty_result = all_like([])       # True
print('empty_result', '=', repr(empty_result))

prices = []
valid = bool(prices) and all(p > 0 for p in prices)   # False
print('valid', '=', repr(valid))

order = {"id": 7, "qty": 2, "price": 9.5}
required = {"id", "qty", "price"}
has_keys = all(k in order for k in required)   # True
print('has_keys', '=', repr(has_keys))
has_keys2 = required <= order.keys()           # True
print('has_keys2', '=', repr(has_keys2))

qtys = [2, 1, 0, 4]
all_positive = all(q > 0 for q in qtys)        # False, stops at 0
print('all_positive', '=', repr(all_positive))

rows = [["tea", "4"], ["milk", "2"], ["rice", "x"]]
names_ok = all(name.isalpha() for name, qty in rows)     # True
print('names_ok', '=', repr(names_ok))
qty_ok = all(qty.isdigit() for name, qty in rows)        # False
print('qty_ok', '=', repr(qty_ok))
bad = [row for row in rows if not row[1].isdigit()]      # [['rice', 'x']]
print('bad', '=', repr(bad))

values = [3, 3, 3]
same1 = all(v == values[0] for v in values)   # True
print('same1', '=', repr(same1))
same2 = len(set(values)) <= 1                 # True
print('same2', '=', repr(same2))
