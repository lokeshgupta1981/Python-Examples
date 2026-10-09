import heapq

numbers = [3, 7, 1, 9, 4, 2]
max_number = max(numbers)  # 9
print('max_number', '=', repr(max_number))
min_number = min(numbers)  # 1
print('min_number', '=', repr(min_number))

largest = max(numbers)       # 9
print('largest', '=', repr(largest))
bigger = max(4, 11, 7)       # 11
print('bigger', '=', repr(bigger))

fruits = ["apple", "banana", "cherry", "date"]
alphabetical_last = max(fruits)          # 'date'
print('alphabetical_last', '=', repr(alphabetical_last))
longest_fruit = max(fruits, key=len)     # 'banana'
print('longest_fruit', '=', repr(longest_fruit))

prices = {'how': 45.23, 'to': 612.78, 'do': 205.55, 'in': 37.20, 'java': 10.75}
max_key = max(prices)                         # 'to', the largest key alphabetically
print('max_key', '=', repr(max_key))
max_value = max(prices.values())              # 612.78
print('max_value', '=', repr(max_value))
key_of_max = max(prices, key=prices.get)      # 'to'
print('key_of_max', '=', repr(key_of_max))
item = max(prices.items(), key=lambda kv: kv[1])   # ('to', 612.78)
print('item', '=', repr(item))

lowest = min(numbers)            # 1
print('lowest', '=', repr(lowest))
cheapest = min(prices, key=prices.get)   # 'java'
print('cheapest', '=', repr(cheapest))

shortest = min(fruits, key=len)   # 'date'
print('shortest', '=', repr(shortest))
first_alpha = min(fruits)         # 'apple'
print('first_alpha', '=', repr(first_alpha))

empty = []
try:
    fails = max(empty)
except Exception as e:
    print(type(e).__name__ + ':', e)
safe = max(empty, default=None)        # None
print('safe', '=', repr(safe))


index_of_max = max(range(len(numbers)), key=numbers.__getitem__)   # 3
print('index_of_max', '=', repr(index_of_max))
pos, value = max(enumerate(numbers), key=lambda p: p[1])         # (3, 9)
print('pos', '=', repr(pos))
print('value', '=', repr(value))
top3 = heapq.nlargest(3, numbers)                               # [9, 7, 4]
print('top3', '=', repr(top3))
bottom2 = heapq.nsmallest(2, numbers)                           # [1, 2]
print('bottom2', '=', repr(bottom2))

products = [("kettle", 25, 4.1), ("toaster", 20, 3.8), ("mixer", 20, 4.6)]
best = min(products, key=lambda p: (p[1], -p[2]))     # ('mixer', 20, 4.6)
print('best', '=', repr(best))
