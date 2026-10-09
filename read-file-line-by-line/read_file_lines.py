from pathlib import Path
from itertools import islice
import mmap
import fileinput
from collections import Counter

with open("data.txt", encoding="utf-8") as f:
    for line in f:
        print(line.rstrip("\n"))

try:
    with open("data.txt", encoding="utf-8") as file:
        for line in file:
            print(line.rstrip("\n"))
except FileNotFoundError:
    print("File not found.")

with open("data.txt", encoding="utf-8") as file:
    lines = file.readlines()          # ['apple\n', 'banana\n', 'cherry\n']
count = len(lines)                     # 3
print('count', '=', repr(count))
last = lines[-1].rstrip("\n")        # 'cherry'
print('last', '=', repr(last))

lines = Path("data.txt").read_text(encoding="utf-8").splitlines()   # ['apple', 'banana', 'cherry']
print('lines', '=', repr(lines))
with open("data.txt", encoding="utf-8") as file:
    long_words = [w for line in file if len(w := line.rstrip("\n")) > 5]   # ['banana', 'cherry']

with open("data.txt", encoding="utf-8") as file:
    header = file.readline().rstrip("\n")       # 'apple'
    rest = [line.rstrip("\n") for line in file]  # ['banana', 'cherry']

def read_lines(file_path):
    with open(file_path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                yield line

fruits = list(read_lines("data.txt"))      # ['apple', 'banana', 'cherry']
print('fruits', '=', repr(fruits))

with open("data.txt", encoding="utf-8") as file:
    middle = [line.rstrip("\n") for line in islice(file, 1, 3)]   # ['banana', 'cherry']

with open("data.txt", "rb") as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mm:
    lines = []
    start = 0
    while start < len(mm):
        end = mm.find(b"\n", start)
        if end == -1:
            end = len(mm)              # last line without a newline
        lines.append(mm[start:end].decode("utf-8"))
        start = end + 1
# lines = ['apple', 'banana', 'cherry']

with open("data.txt", encoding="utf-8", errors="replace") as file:
    numbered = [f"{n}: {line.rstrip()}" for n, line in enumerate(file, start=1) if line.strip()]
# ['1: apple', '2: banana', '3: cherry']

with fileinput.input(files=["data.txt", "data.txt"], encoding="utf-8") as stream:
    total = sum(1 for line in stream)        # 6, three lines from each file

with open("app.log", "w", encoding="utf-8") as f:
    f.write("INFO db started\nERROR db timeout\nERROR api 500\nINFO api ok\nERROR db timeout\n")

errors = Counter()
with open("app.log", encoding="utf-8") as log:
    for line in log:
        if not line.strip():
            continue                   # skip blank lines
        level, module, *_ = line.split()
        if level == "ERROR":
            errors[module] += 1
summary = dict(errors)              # {'db': 2, 'api': 1}
print('summary', '=', repr(summary))

with open("data.txt", "rb") as f:
    line_count = sum(1 for _ in f)      # 3
