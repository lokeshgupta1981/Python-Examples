from pprint import pp

num_list = [1, 2, 3, 4, 5]
fruits = ["apple", "kiwi", "fig"]

print(*num_list)          # 1 2 3 4 5
print(*fruits)            # apple kiwi fig

print(*num_list, sep=", ")              # 1, 2, 3, 4, 5
line = ", ".join(map(str, num_list))    # '1, 2, 3, 4, 5'
print('line', '=', repr(line))
try:
    bad = ", ".join(num_list)
except Exception as e:
    print(type(e).__name__ + ':', e)

print(num_list)                              # [1, 2, 3, 4, 5]
print(num_list, sep=" | ")                   # [1, 2, 3, 4, 5], sep is not used
print(f"[{'; '.join(map(str, num_list))}]")  # [1; 2; 3; 4; 5]

print(f"{{{', '.join(map(str, num_list))}}}")    # {1, 2, 3, 4, 5}
print(f"Numbers: {', '.join(map(str, num_list))}")  # Numbers: 1, 2, 3, 4, 5
print(f"{fruits!r}")                               # ['apple', 'kiwi', 'fig']

print(*fruits, sep="\n")
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}. {fruit}")


orders = [{"id": 1, "items": ["tea", "milk"]}, {"id": 2, "items": ["rice"]}, {"id": 3, "items": []}]
pp(orders, width=40)
for o in orders:
    print(f"{o['id']:<3}{', '.join(o['items']) or '-'}")
