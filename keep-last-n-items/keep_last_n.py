from collections import deque
import numpy as np

q = deque(maxlen=3)
for n in [1, 2, 3, 4, 5]:
    q.append(n)
last_three = list(q)        # [3, 4, 5]
print('last_three', '=', repr(last_three))
size = q.maxlen             # 3
print('size', '=', repr(size))

my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
last_n_items_list = my_list[-3:]     # [7, 8, 9]
print('last_n_items_list', '=', repr(last_n_items_list))
more_than_len = my_list[-20:]        # the whole list
print('more_than_len', '=', repr(more_than_len))

def last_n(seq, n):
    return seq[-n:] if n > 0 else seq[:0]

zero_wrong = my_list[-0:]            # [1, 2, ... 9], the whole list
print('zero_wrong', '=', repr(zero_wrong))
zero_right = last_n(my_list, 0)      # []
print('zero_right', '=', repr(zero_right))


my_array = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
last_n_items_array = my_array[-3:]        # array([7, 8, 9])
print('last_n_items_array', '=', repr(last_n_items_array))
independent = my_array[-3:].copy()

card = "4111111111111234"
masked = "*" * 12 + card[-4:]        # '************1234'
print('masked', '=', repr(masked))

def tail(path, n=3):
    with open(path, encoding="utf-8") as f:
        return [line.rstrip("\n") for line in deque(f, maxlen=n)]

last_lines = tail("app.log", 2)      # ['INFO saved order 7', 'ERROR payment timeout']
print('last_lines', '=', repr(last_lines))

window = deque(maxlen=3)
averages = []
for reading in [10, 20, 30, 40, 50]:
    window.append(reading)
    averages.append(sum(window) / len(window))
# averages = [10.0, 15.0, 20.0, 30.0, 40.0]
