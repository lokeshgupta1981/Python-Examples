import re
import csv

colors = "red green  blue"
words = colors.split()            # ['red', 'green', 'blue']
print('words', '=', repr(words))
parts = "2026-10-09".split("-")   # ['2026', '10', '09']
print('parts', '=', repr(parts))

line = "red  green\tblue\n"
by_whitespace = line.split()       # ['red', 'green', 'blue']
print('by_whitespace', '=', repr(by_whitespace))
by_space = line.split(" ")         # ['red', '', 'green\tblue\n']
print('by_space', '=', repr(by_space))
empty = "".split()                 # []
print('empty', '=', repr(empty))
empty_sep = "".split(",")          # ['']
print('empty_sep', '=', repr(empty_sep))

setting = "path=/home/user=me"
key, value = setting.split("=", 1)            # 'path', '/home/user=me'
print('key', '=', repr(key))
print('value', '=', repr(value))
name, ext = "report.final.pdf".rsplit(".", 1) # 'report.final', 'pdf'
print('name', '=', repr(name))
print('ext', '=', repr(ext))

text = "first\r\nsecond\n"
with_split = text.split("\n")      # ['first\r', 'second', '']
print('with_split', '=', repr(with_split))
with_lines = text.splitlines()      # ['first', 'second']
print('with_lines', '=', repr(with_lines))


tags = "java, python;go   rust"


row = 'Lokesh,"Delhi, India",37'
naive = row.split(",")                   # ['Lokesh', '"Delhi', ' India"', '37']
print('naive', '=', repr(naive))
fields = next(csv.reader([row]))         # ['Lokesh', 'Delhi, India', '37']
print('fields', '=', repr(fields))

raw = "host = db.local; port=5432; password=a=b"
settings = {}
for pair in raw.split(";"):
    key, _, value = pair.partition("=")
    settings[key.strip()] = value.strip()
# {'host': 'db.local', 'port': '5432', 'password': 'a=b'}

nums = list(map(int, "3 14 15".split()))      # [3, 14, 15]
print('nums', '=', repr(nums))
floats = [float(p) for p in "1.5,2.25".split(",")]  # [1.5, 2.25]
print('floats', '=', repr(floats))
