import random

# A new list of even numbers from 0-9
even_numbers = [x for x in range(10) if x % 2 == 0]                # [0, 2, 4, 6, 8]
print('even_numbers', '=', repr(even_numbers))

# if-else inside a list comprehension
labels = ["Even" if x % 2 == 0 else "Odd" for x in range(4)]      # ['Even', 'Odd', 'Even', 'Odd']
print('labels', '=', repr(labels))

# Two lists in one comprehension
combined = [(x, y) for x in [1, 2, 3] for y in [3, 2, 1] if x != y]
# [(1, 3), (1, 2), (2, 3), (2, 1), (3, 2), (3, 1)]



even_numbers = []
for x in range(10):
    if x % 2 == 0:
        even_numbers.append(x)
loop_result = even_numbers                                       # [0, 2, 4, 6, 8]
print('loop_result', '=', repr(loop_result))
comprehension_result = [x for x in range(10) if x % 2 == 0]       # [0, 2, 4, 6, 8]
print('comprehension_result', '=', repr(comprehension_result))

squares = [x**2 for x in range(5)]          # [0, 1, 4, 9, 16]
print('squares', '=', repr(squares))

words = ["List", "COMPREHENSIONS", "Are", "COOL"]
lower_words = [word.lower() for word in words]    # ['list', 'comprehensions', 'are', 'cool']
print('lower_words', '=', repr(lower_words))

string = "Hello 12345 World"
numbers = [int(s) for s in string if s.isdigit()]   # [1, 2, 3, 4, 5]
print('numbers', '=', repr(numbers))

matrix = [[1, 2], [3, 4], [5, 6]]
flattened = [num for row in matrix for num in row]   # [1, 2, 3, 4, 5, 6]
print('flattened', '=', repr(flattened))

random.seed(7)
numbers = [round(random.random(), 2) for _ in range(10)]
randoms = [x for x in numbers if x >= 0.5]     # [0.65, 0.54, 0.51]
print('randoms', '=', repr(randoms))



labels = ["Even" if x % 2 == 0 else "Odd" for x in range(10)]
print(labels)

prices = [12, 0, 7, 0]
paid = [p for p in prices if p > 0]                 # [12, 7], filter
print('paid', '=', repr(paid))
shown = [p if p > 0 else "free" for p in prices]    # [12, 'free', 7, 'free'], choose
print('shown', '=', repr(shown))

list1 = [1, 2, 3]
list2 = [3, 2, 1]
combined = [(x, y) for x in list1 for y in list2 if x != y]
print(combined)

names = ["tea", "milk", "sugar"]
prices = [3, 2, 1]
labels = [f"{n}: {p}" for n, p in zip(names, prices)]    # ['tea: 3', 'milk: 2', 'sugar: 1']
print('labels', '=', repr(labels))
totals = [a + b for a, b in zip([1, 2], [10, 20], strict=True)]   # [11, 22]
print('totals', '=', repr(totals))

matrix = [[1, 2, 3], [4, 5, 6]]
transposed = [[row[i] for row in matrix] for i in range(3)]   # [[1, 4], [2, 5], [3, 6]]
print('transposed', '=', repr(transposed))

words = ["apple", "kiwi", "apple", "fig"]
lengths = {w: len(w) for w in words}        # {'apple': 5, 'kiwi': 4, 'fig': 3}
print('lengths', '=', repr(lengths))
unique = {w[0] for w in words}              # {'a', 'k', 'f'}, order may vary
print('unique', '=', repr(unique))
total = sum(len(w) for w in words)          # 17, no list is built
print('total', '=', repr(total))

lines = [
    "tea,3.50,10",
    "# discontinued",
    "milk,1.20,0",
    "",
    "sugar,2.00,4",
]
rows = [line.split(",") for line in lines if line and not line.startswith("#")]
in_stock = [(name, float(price)) for name, price, qty in rows if int(qty) > 0]
# [('tea', 3.5), ('sugar', 2.0)]
values = [v for name, price, qty in rows if (v := float(price) * int(qty)) > 0]
# [35.0, 8.0]

x = "outer"
squares = [x * x for x in range(3)]
after = x                                   # 'outer'
print('after', '=', repr(after))
