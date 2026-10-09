names = ["alex", "brian", "charles"]
for name in names:
    print("Current name is:", name)

for e in ("item1", "item2"):
    print("tuple:", e)
for c in "hey":
    print("char:", c)
total = 0
for price in {4, 2, 9}:
    total += price        # total = 15, the order does not matter for a sum

stock = {"tea": 4, "milk": 0, "rice": 9}
for item, qty in stock.items():
    print(f"{item}: {qty}")

for i in range(3):
    print("lap", i)

for pos, name in enumerate(names, start=1):
    print(pos, name)

for name, score in zip(names, [90, 85, 77]):
    print(name, score)

for name in names:
    if name.startswith("z"):
        print("found", name)
        break
else:
    print("no name starts with z")     # this line runs

nums = [1, 2, 2, 3]
for n in nums:
    if n == 2:
        nums.remove(n)
wrong = nums                           # [1, 2, 3], one 2 survived
print('wrong', '=', repr(wrong))

nums = [1, 2, 2, 3]
right = [n for n in nums if n != 2]    # [1, 3]
print('right', '=', repr(right))

order = [{"item": "tea", "qty": 2, "price": 4.5}, {"item": "rice", "qty": 1, "price": 12.0}]
total = 0
for line in order:
    total += line["qty"] * line["price"]
# total = 21.0
