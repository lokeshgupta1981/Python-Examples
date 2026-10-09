import os
from contextlib import suppress

def send_invoice(order):
    pass

result = send_invoice(42)    # None
print('result', '=', repr(result))

class PaymentError(Exception):
    pass

for n in [1, 2, 3]:
    if n == 2:
        pass
    print("pass loop", n)        # prints 1, 2, 3

for n in [1, 2, 3]:
    if n == 2:
        continue
    print("continue loop", n)    # prints 1, 3

def refund(order): ...           # Ellipsis, same effect as pass

def ship(order):
    raise NotImplementedError("ship() is not written yet")

r = refund(42)                    # None
print('r', '=', repr(r))
try:
    s = ship(42)
except Exception as e:
    print(type(e).__name__ + ':', e)


with suppress(FileNotFoundError):
    os.remove("old-cache.tmp")    # no error if the file does not exist

class OrderError(Exception):
    pass


class OutOfStock(OrderError):
    pass


try:
    raise OutOfStock("tea is sold out")
except OrderError as e:
    caught = type(e).__name__        # 'OutOfStock'
