import math
from decimal import Decimal
from fractions import Fraction

loss = abs(-50)        # 50
print('loss', '=', repr(loss))
change = abs(-99.99)   # 99.99
print('change', '=', repr(change))

target = 21.0
reading = 19.5
off_by = abs(reading - target)     # 1.5
print('off_by', '=', repr(off_by))
same = abs(target - reading)       # 1.5
print('same', '=', repr(same))


naive = abs(0.1 + 0.2 - 0.3) < 1e-9     # True, but the threshold is a guess
print('naive', '=', repr(naive))
close = math.isclose(0.1 + 0.2, 0.3)    # True, relative tolerance
print('close', '=', repr(close))

magnitude = abs(3 - 4j)      # 5.0
print('magnitude', '=', repr(magnitude))
other = abs(5 - 9j)          # 10.295630140987
print('other', '=', repr(other))
check = math.hypot(5, -9)    # 10.295630140987, the same value
print('check', '=', repr(check))


zero = abs(-0.0)                       # 0.0
print('zero', '=', repr(zero))
sign = math.copysign(1, -0.0)          # -1.0, the sign was negative
print('sign', '=', repr(sign))
money = abs(Decimal("-10.25"))         # Decimal('10.25')
print('money', '=', repr(money))
part = abs(Fraction(-3, 4))            # Fraction(3, 4)
print('part', '=', repr(part))

fabs_int = math.fabs(-5)      # 5.0, a float
print('fabs_int', '=', repr(fabs_int))
abs_int = abs(-5)             # 5, still an int
print('abs_int', '=', repr(abs_int))

class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __abs__(self):
        return math.hypot(self.x, self.y)

length = abs(Vector(6, 8))    # 10.0
print('length', '=', repr(length))
try:
    bad = abs("5")
except Exception as e:
    print(type(e).__name__ + ':', e)

sizes = [36, 38, 40, 42, 44]
foot = 41.2
best = min(sizes, key=lambda s: abs(s - foot))     # 42
print('best', '=', repr(best))
order = sorted(sizes, key=lambda s: abs(s - foot)) # [42, 40, 44, 38, 36]
print('order', '=', repr(order))
