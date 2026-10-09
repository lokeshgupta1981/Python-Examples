

x = 5
y = -10
total = x + y            # -5
print('total', '=', repr(total))
product = x * y          # -50
print('product', '=', repr(product))
quotient = x / y         # -0.5, always a float
print('quotient', '=', repr(quotient))
floor_q = x // 2         # 2
print('floor_q', '=', repr(floor_q))
remainder = x % 3        # 2
print('remainder', '=', repr(remainder))
power = x ** 2           # 25
print('power', '=', repr(power))
big = 2 ** 100           # 1267650600228229401496703205376
print('big', '=', repr(big))

x = 10
y = 12345678987654321
z = 12_34_56              # 123456
print('z', '=', repr(z))
million = 1_000_000       # 1000000
print('million', '=', repr(million))

binary_int = 0b1010      # 10
print('binary_int', '=', repr(binary_int))
octal_int = 0o22         # 18
print('octal_int', '=', repr(octal_int))
hex_int = 0xAA           # 170
print('hex_int', '=', repr(hex_int))

x = 22
y = 5
add = x + y              # 27
print('add', '=', repr(add))
sub = x - y              # 17
print('sub', '=', repr(sub))
mul = x * y              # 110
print('mul', '=', repr(mul))
div = x / y              # 4.4
print('div', '=', repr(div))
exact = 10 / 2           # 5.0, still a float
print('exact', '=', repr(exact))
floor_div = x // y       # 4
print('floor_div', '=', repr(floor_div))
mod = x % y              # 2
print('mod', '=', repr(mod))
both = divmod(x, y)      # (4, 2)
print('both', '=', repr(both))

neg_floor = -7 // 2      # -4
print('neg_floor', '=', repr(neg_floor))
neg_mod = -7 % 2         # 1
print('neg_mod', '=', repr(neg_mod))
toward_zero = int(-7 / 2)    # -3
print('toward_zero', '=', repr(toward_zero))

x = 10
x += 1                   # 11
x += 5                   # 16
y = 10
y -= 1                   # 9
y -= 5                   # 4
count = x                # 16
print('count', '=', repr(count))

square = 10 ** 2           # 100
print('square', '=', repr(square))
half = 2 ** -1             # 0.5
print('half', '=', repr(half))
mod_pow = pow(3, 200, 7)   # 2, without building the full number
print('mod_pow', '=', repr(mod_pow))

value = 42
check1 = isinstance(value, int)     # True
print('check1', '=', repr(check1))
check2 = type(value) is int         # True
print('check2', '=', repr(check2))
flag = isinstance(True, int)        # True, bool is a subclass of int
print('flag', '=', repr(flag))
strict = type(True) is int          # False
print('strict', '=', repr(strict))

n = 1234567
text = str(n)                 # '1234567'
print('text', '=', repr(text))
grouped = f"{n:,}"            # '1,234,567'
print('grouped', '=', repr(grouped))
padded = f"{42:05d}"          # '00042'
print('padded', '=', repr(padded))
as_bin = f"{10:#b}"           # '0b1010'
print('as_bin', '=', repr(as_bin))
as_hex = f"{255:x}"           # 'ff'
print('as_hex', '=', repr(as_hex))

plain = int("10")              # 10
print('plain', '=', repr(plain))
spaces = int(" 42 ")           # 42
print('spaces', '=', repr(spaces))
from_hex = int("ff", 16)       # 255
print('from_hex', '=', repr(from_hex))
from_bin = int("1010", 2)      # 10
print('from_bin', '=', repr(from_bin))
auto = int("0x1A", 0)          # 26, base taken from the prefix
print('auto', '=', repr(auto))

raw = "4.5"
try:
    value = int(raw)
except ValueError as e:
    message = str(e)           # "invalid literal for int() with base 10: '4.5'"
value = int(float(raw))        # 4
print('value', '=', repr(value))

huge = 10 ** 5000               # arithmetic works
bits = huge.bit_length()        # 16610
print('bits', '=', repr(bits))
digits = len(str(2 ** 1000))   # 302
print('digits', '=', repr(digits))

a, b = 12, 10              # 0b1100 and 0b1010
print('a', '=', repr(a))
print('b', '=', repr(b))
and_ = a & b               # 8
print('and_', '=', repr(and_))
or_ = a | b                # 14
print('or_', '=', repr(or_))
xor = a ^ b                # 6
print('xor', '=', repr(xor))
shifted = 1 << 4           # 16
print('shifted', '=', repr(shifted))
halved = 40 >> 2           # 10
print('halved', '=', repr(halved))
inverted = ~5              # -6
print('inverted', '=', repr(inverted))

prices_cents = [1999, 450, 1]          # 19.99, 4.50 and 0.01
print('prices_cents', '=', repr(prices_cents))
total_cents = sum(prices_cents)         # 2450
print('total_cents', '=', repr(total_cents))
euros, cents = divmod(total_cents, 100)
label = f"{euros}.{cents:02d}"          # '24.50'
print('label', '=', repr(label))

items, per_page = 23, 10
pages = -(-items // per_page)           # 3, ceiling division without math.ceil
print('pages', '=', repr(pages))
