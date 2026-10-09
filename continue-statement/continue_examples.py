cart = ["milk", "", "bread", "eggs", ""]
for item in cart:
    if not item:
        continue          # skip empty entries
    print("Buying", item)

n = 0
while n < 6:
    n += 1              # update first
    if n % 2 == 0:
        continue
    print("odd", n)

for day in ["Mon", "Tue"]:
    for hour in [9, 12, 15]:
        if hour == 12:
            continue      # lunch break
        print(day, hour)

for x in [1, 0, 2]:
    try:
        if x == 0:
            continue
        print("10 /", x, "=", 10 / x)
    finally:
        print("checked", x)

lines = ["# daily steps", "4500", "", "abc", "7200"]
total = 0
for line in lines:
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    try:
        steps = int(line)
    except ValueError:
        print("Skipping bad value:", line)
        continue
    total += steps
print("Total steps:", total)

for day, hours in {"Mon": [8, 9], "Tue": [8, -1]}.items():
    for h in hours:
        if h < 0:
            break            # bad data, skip this day
    else:
        print(day, "is valid")
        continue
    print(day, "has bad data")
