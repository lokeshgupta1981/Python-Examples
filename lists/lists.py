import copy

fruits = ["apple", "banana"]
fruits.append("cherry")        # ['apple', 'banana', 'cherry']
first = fruits[0]              # 'apple'
print('first', '=', repr(first))
fruits.remove("banana")        # ['apple', 'cherry']
size = len(fruits)             # 2
print('size', '=', repr(size))

empty = []
subjects = ["physics", "chemistry", "mathematics"]
ids = [0, 1, 2, 3, 4]
mixed = [0, "one", 2, "three"]
nested = [["A", "B", "C"], ["D", "E", "F"]]
from_range = list(range(5))      # [0, 1, 2, 3, 4]
print('from_range', '=', repr(from_range))
from_string = list("abc")        # ['a', 'b', 'c']
print('from_string', '=', repr(from_string))

wrong = [[0] * 3] * 3
wrong[0][0] = 1                  # [[1, 0, 0], [1, 0, 0], [1, 0, 0]]
right = [[0] * 3 for _ in range(3)]
right[0][0] = 1                  # [[1, 0, 0], [0, 0, 0], [0, 0, 0]]

chars = []
chars.append("a")
chars.append("b")                # ['a', 'b']
chars.insert(3, "c")             # ['a', 'b', 'c']
chars.insert(10, "d")            # ['a', 'b', 'c', 'd'], no error
chars.insert(0, "z")             # ['z', 'a', 'b', 'c', 'd']
chars.extend(["e", "f"])         # ['z', 'a', 'b', 'c', 'd', 'e', 'f']

nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
first = nums[0]          # 0
print('first', '=', repr(first))
last = nums[-1]          # 9
print('last', '=', repr(last))
part = nums[1:5]         # [1, 2, 3, 4]
print('part', '=', repr(part))
head = nums[:3]          # [0, 1, 2]
print('head', '=', repr(head))
tail = nums[7:]          # [7, 8, 9]
print('tail', '=', repr(tail))
back = nums[-8:-5]       # [2, 3, 4]
print('back', '=', repr(back))
evens = nums[::2]        # [0, 2, 4, 6, 8]
print('evens', '=', repr(evens))
reversed_copy = nums[::-1]   # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
print('reversed_copy', '=', repr(reversed_copy))

chars = ["a", "b", "c"]
chars[2] = "d"                   # ['a', 'b', 'd']
chars[0:2] = ["x", "y", "z"]     # ['x', 'y', 'z', 'd']

chars = ["a", "b", "c"]
for i, ch in enumerate(chars):
    print(i, ch)

chars = ["a", "b", "c"]
has_a = "a" in chars             # True
print('has_a', '=', repr(has_a))
has_d = "d" in chars             # False
print('has_d', '=', repr(has_d))

chars = ["a", "b", "c"]
size = len(chars)                # 3
print('size', '=', repr(size))
is_empty = not []                # True
print('is_empty', '=', repr(is_empty))

chars = ["a", "b", "c", "b"]
chars.remove("b")                # ['a', 'c', 'b']

chars = ["a", "b", "c", "d"]
last = chars.pop()               # 'd', chars is ['a', 'b', 'c']
print('last', '=', repr(last))
second = chars.pop(1)            # 'b', chars is ['a', 'c']
print('second', '=', repr(second))

chars = ["a", "b", "c", "d"]
chars.clear()                    # []

chars = ["a", "b", "c", "d"]
del chars[0]                     # ['b', 'c', 'd']
del chars[:2]                    # ['d']

chars = ["a", "b", "c"]
nums = [1, 2, 3]
joined = chars + nums            # ['a', 'b', 'c', 1, 2, 3]
print('joined', '=', repr(joined))
merged = [*chars, *nums, "z"]    # ['a', 'b', 'c', 1, 2, 3, 'z']
print('merged', '=', repr(merged))
chars.extend(nums)               # chars is ['a', 'b', 'c', 1, 2, 3]

chars = ["a", "c", "B", "d"]
result = chars.sort()                    # None, chars is ['B', 'a', 'c', 'd']
print('result', '=', repr(result))
by_lower = sorted(chars, key=str.lower)  # ['a', 'B', 'c', 'd']
print('by_lower', '=', repr(by_lower))
newest_first = sorted([3, 1, 2], reverse=True)   # [3, 2, 1]
print('newest_first', '=', repr(newest_first))

chars = ["a", "b", "c", "d"]
chars.reverse()                  # ['d', 'c', 'b', 'a']

grid = [[1, 2], [3, 4]]
shallow = grid.copy()
deep = copy.deepcopy(grid)
grid[0][0] = 99
shallow_sees = shallow[0][0]     # 99, the inner list is shared
print('shallow_sees', '=', repr(shallow_sees))
deep_sees = deep[0][0]           # 1
print('deep_sees', '=', repr(deep_sees))

letters = ["a", "b", "a", "c", "a"]
times = letters.count("a")       # 3
print('times', '=', repr(times))
first_a = letters.index("a")     # 0
print('first_a', '=', repr(first_a))
next_a = letters.index("a", 1)   # 2
print('next_a', '=', repr(next_a))

scores = [3, 9, 2]
count = len(scores)              # 3
print('count', '=', repr(count))
lowest = min(scores)             # 2
print('lowest', '=', repr(lowest))
highest = max(scores)            # 9
print('highest', '=', repr(highest))
total = sum(scores)              # 14
print('total', '=', repr(total))
safe = max([], default=0)        # 0
print('safe', '=', repr(safe))
longest = max(["tea", "sugar"], key=len)   # 'sugar'
print('longest', '=', repr(longest))

history = []
text = ""
for word in ["Hello", " World", "!"]:
    history.append(text)         # save the state before the change
    text += word

text = history.pop()             # undo the last change
print('text', '=', repr(text))
undone = text                    # 'Hello World'
print('undone', '=', repr(undone))
remaining = len(history)         # 2
print('remaining', '=', repr(remaining))

nums = [1, 2, 1, 3, 1]
without_ones = [n for n in nums if n != 1]    # [2, 3]
print('without_ones', '=', repr(without_ones))
