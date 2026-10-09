import heapq
import numpy as np
from collections import Counter

nums = [1, 8, 2, 23, 7, -4, 18, 23, 42, 37, 2]
top3 = heapq.nlargest(3, nums)        # [42, 37, 23]
print('top3', '=', repr(top3))
bottom3 = heapq.nsmallest(3, nums)    # [-4, 1, 2]
print('bottom3', '=', repr(bottom3))



nums = [1, 8, 2, 23, 7, -4, 18, 23, 42, 37, 2]
top4 = heapq.nlargest(4, nums)         # [42, 37, 23, 23]
print('top4', '=', repr(top4))
low2 = heapq.nsmallest(2, nums)        # [-4, 1]
print('low2', '=', repr(low2))
too_many = heapq.nlargest(20, [3, 1, 2])   # [3, 2, 1], all items
print('too_many', '=', repr(too_many))
words = heapq.nsmallest(2, ["pear", "fig", "apple"])   # ['apple', 'fig']
print('words', '=', repr(words))

portfolio = [
    {"name": "IBM", "shares": 100, "price": 91.1},
    {"name": "AAPL", "shares": 50, "price": 543.22},
    {"name": "FB", "shares": 200, "price": 21.09},
    {"name": "HPQ", "shares": 35, "price": 31.75},
    {"name": "YHOO", "shares": 45, "price": 16.35},
    {"name": "ACME", "shares": 75, "price": 115.65},
]
cheap = heapq.nsmallest(3, portfolio, key=lambda s: s["price"])
expensive = heapq.nlargest(3, portfolio, key=lambda s: s["price"])
cheap_names = [s["name"] for s in cheap]          # ['YHOO', 'FB', 'HPQ']
print('cheap_names', '=', repr(cheap_names))
expensive_names = [s["name"] for s in expensive]  # ['AAPL', 'ACME', 'IBM']
print('expensive_names', '=', repr(expensive_names))

biggest = heapq.nlargest(2, portfolio, key=lambda s: s["shares"] * s["price"])
biggest_names = [s["name"] for s in biggest]      # ['AAPL', 'IBM']
print('biggest_names', '=', repr(biggest_names))

scores = [("ann", 90), ("bob", 95), ("cid", 90), ("dee", 90)]
top3 = heapq.nlargest(3, scores, key=lambda t: t[1])
# [('bob', 95), ('ann', 90), ('cid', 90)]

arr = np.array([1, 8, 2, 23, 7, -4, 18, 23, 42, 37, 2])
idx = np.argpartition(arr, -3)[-3:]       # indexes of the 3 largest, unordered
print('idx', '=', repr(idx))
top3_np = np.sort(arr[idx])[::-1]         # array([42, 37, 23])
print('top3_np', '=', repr(top3_np))

sales = [("tea", 3), ("milk", 1), ("tea", 2), ("jam", 5), ("bread", 4), ("milk", 1), ("honey", 1)]
units = Counter()
for product, qty in sales:
    units[product] += qty

best = heapq.nlargest(3, units.items(), key=lambda kv: kv[1])
# [('tea', 5), ('jam', 5), ('bread', 4)]
slowest = heapq.nsmallest(1, units.items(), key=lambda kv: kv[1])   # [('honey', 1)]
print('slowest', '=', repr(slowest))

tasks = [5, 1, 4]
heapq.heapify(tasks)
first = heapq.heappop(tasks)       # 1
print('first', '=', repr(first))
second = heapq.heappop(tasks)      # 4
print('second', '=', repr(second))

values = [10, 50, 30, 50]
top_idx = heapq.nlargest(2, range(len(values)), key=values.__getitem__)   # [1, 3]
print('top_idx', '=', repr(top_idx))
