from contextlib import redirect_stdout
import sys

with open("demo.txt", "w", encoding="utf-8") as f:
    print("Hello, Python!", file=f)
    print("Total:", 42, file=f)

for run in (1, 2):
    with open("runs.txt", "a", encoding="utf-8") as f:
        print("run", run, "finished", file=f)


def report():
    print("Sales: 120")
    print("Returns: 4")

with open("report.txt", "w", encoding="utf-8") as f, redirect_stdout(f):
    report()
print("This message will be written to the screen.")


original_stdout = sys.stdout
with open("demo2.txt", "w", encoding="utf-8") as f:
    sys.stdout = f
    try:
        print("This message will be written to a file.")
    finally:
        sys.stdout = original_stdout
print("Back on the screen.")

rows = [("tea", 4, 5.0), ("milk", 2, 2.25)]
with open("sales.csv", "w", encoding="utf-8") as f:
    print("item", "qty", "price", sep=",", file=f)
    for row in rows:
        print(*row, sep=",", file=f)
