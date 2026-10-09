

total = 11 + 1.1            # 12.1, int widened to float (implicit)
print('total', '=', repr(total))
count = int("42")           # 42, str converted to int (explicit)
print('count', '=', repr(count))
label = "Total: " + str(total)   # 'Total: 12.1'
print('label', '=', repr(label))

int_val = 11
flo_val = 1.1
flo_sum = int_val + flo_val
print("datatype of flo_sum:", type(flo_sum))
print("value of flo_sum:", flo_sum)

as_int = True + 1            # 2, bool is a subclass of int
print('as_int', '=', repr(as_int))
as_complex = 1 + 2j          # (1+2j)
print('as_complex', '=', repr(as_complex))
division = 3 / 2             # 1.5, a float
print('division', '=', repr(division))
floor_float = 7 // 2.0       # 3.0, a float because one operand is float
print('floor_float', '=', repr(floor_float))

int_val = 11
str_val = "1.1"
try:
    val_sum = int_val + str_val
except TypeError as e:
    message = str(e)         # "unsupported operand type(s) for +: 'int' and 'str'"

int_val = 11
str_val = "1.1"
as_text = str(int_val) + str_val          # '111.1'
print('as_text', '=', repr(as_text))
as_number = int_val + float(str_val)      # 12.1
print('as_number', '=', repr(as_number))

letters = list("abca")                  # ['a', 'b', 'c', 'a']
print('letters', '=', repr(letters))
unique = sorted(set(letters))            # ['a', 'b', 'c']
print('unique', '=', repr(unique))
frozen = tuple([1, 2, 3])                # (1, 2, 3)
print('frozen', '=', repr(frozen))
pairs = dict([("a", 1), ("b", 2)])       # {'a': 1, 'b': 2}
print('pairs', '=', repr(pairs))
keys = list({"x": 1, "y": 2})            # ['x', 'y']
print('keys', '=', repr(keys))

truncated = int(3.99)          # 3, the fraction is dropped
print('truncated', '=', repr(truncated))
toward_zero = int(-3.99)       # -3, truncation goes toward zero
print('toward_zero', '=', repr(toward_zero))
rounded = round(3.99)          # 4
print('rounded', '=', repr(rounded))
big = 2**53 + 1 + 0.0          # 9007199254740992.0, precision lost
print('big', '=', repr(big))
true_text = bool("False")      # True, any non-empty string is truthy
print('true_text', '=', repr(true_text))
text_of_bytes = str(b"hi")     # "b'hi'", use decode() instead
print('text_of_bytes', '=', repr(text_of_bytes))

form = {"qty": "3", "price": "19.99", "gift": "on", "coupon": ""}

def parse_order(data):
    errors = []
    try:
        qty = int(data["qty"])
    except ValueError:
        qty, errors = 0, errors + ["qty must be a whole number"]
    try:
        price = float(data["price"])
    except ValueError:
        price, errors = 0.0, errors + ["price must be a number"]
    gift = data.get("gift") == "on"          # checkbox to bool
    coupon = data.get("coupon") or None      # empty string to None
    return {"qty": qty, "price": price, "gift": gift, "coupon": coupon}, errors

order, problems = parse_order(form)
# order = {'qty': 3, 'price': 19.99, 'gift': True, 'coupon': None}, problems = []
