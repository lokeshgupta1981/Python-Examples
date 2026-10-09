name = input("Your name: ")    # the user types Lokesh
print('name', '=', repr(name))
print("Hello,", name)          # Hello, Lokesh


while True:
    text = input("How many pizzas? ")
    try:
        count = int(text)
        break
    except ValueError:
        print(f"'{text}' is not a whole number, try again")
print("Ordering", count, "pizzas")

w, h = map(int, input("Width and height: ").split())   # user types: 4 5
print('w', '=', repr(w))
print('h', '=', repr(h))
area = w * h                                           # 20
print('area', '=', repr(area))

answer = input("Extra cheese? ").strip().lower()   # user types: " Yes "
print('answer', '=', repr(answer))
cheese = answer in ("y", "yes")                   # True
print('cheese', '=', repr(cheese))

try:
    city = input("City: ")
except EOFError:
    city = "unknown"

cart = []
while True:
    choice = input("[a]dd, [l]ist, [q]uit: ").strip().lower()
    if choice == "q":
        break
    elif choice == "a":
        cart.append(input("Item: ").strip())
    elif choice == "l":
        print("Cart:", ", ".join(cart) or "empty")
    else:
        print("Unknown choice:", choice)

lines = []
while True:
    try:
        line = input()
    except EOFError:
        break
    if line == "":
        break
    lines.append(line)
