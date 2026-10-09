import sys
from pprint import pp

i = 100
print("The value of i is:", i)    # The value of i is: 100

result = print("hi")      # prints hi, result = None
print('result', '=', repr(result))

print("A", "B", "C", sep=" # ", end=" Done\n")   # A # B # C Done
print(*["red", "green"], sep=", ")             # red, green


print("Disk almost full", file=sys.stderr)

with open("report.txt", "w", encoding="utf-8") as f:
    print("Total:", 42, file=f)       # report.txt contains: Total: 42

name = "Lokesh "
print(f"{name=}")          # name='Lokesh '
print(f"[{name!r}]")       # ['Lokesh ']


config = {"db": {"host": "localhost", "ports": [5432, 5433]}, "debug": True, "name": "shop"}
pp(config, width=40)

items = [("Tea", 4.5), ("Milk", 2.25), ("Rice", 12.0)]
print(f"{'Item':<8}{'Price':>8}")
for name, price in items:
    print(f"{name:<8}{price:>8.2f}")
