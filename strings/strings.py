

s = "hello world"
first = s[0]               # 'h'
print('first', '=', repr(first))
word = s[6:]               # 'world'
print('word', '=', repr(word))
loud = s.upper()           # 'HELLO WORLD', s is unchanged
print('loud', '=', repr(loud))
size = len(s)              # 11
print('size', '=', repr(size))

s1 = 'hello world'
s2 = "hello world"
same = s1 == s2                  # True
print('same', '=', repr(same))
multi = """Say hello
to python"""
lines = multi.splitlines()       # ['Say hello', 'to python']
print('lines', '=', repr(lines))

tabbed = "a\tb"                     # 'a', a tab, 'b'
print('tabbed', '=', repr(tabbed))
quote = 'It\'s fine'                  # "It's fine"
print('quote', '=', repr(quote))
path = r"C:\Users\new"               # backslashes kept, no newline
print('path', '=', repr(path))
length = len(path)                    # 12
print('length', '=', repr(length))

s = "hello world"
middle = s[2:5]            # 'llo'
print('middle', '=', repr(middle))
tail_part = s[-5:-2]       # 'wor'
print('tail_part', '=', repr(tail_part))
last3 = s[-3:]             # 'rld'
print('last3', '=', repr(last3))
every_2nd = s[::2]         # 'hlowrd'
print('every_2nd', '=', repr(every_2nd))
backwards = s[::-1]        # 'dlrow olleh'
print('backwards', '=', repr(backwards))
safe = s[20:30]            # '', no error
print('safe', '=', repr(safe))

s = "hello world"
h = s[0]                   # 'h'
print('h', '=', repr(h))
e = s[1]                   # 'e'
print('e', '=', repr(e))
chars = [c for c in "abc"] # ['a', 'b', 'c']
print('chars', '=', repr(chars))

s = "hello"
fixed = "j" + s[1:]        # 'jello'
print('fixed', '=', repr(fixed))
replaced = s.replace("h", "y")   # 'yello', s is still 'hello'
print('replaced', '=', repr(replaced))

length = len("hello world")             # 11
print('length', '=', repr(length))
accented = "caf\u00e9"                   # 'cafe' with an accented e
print('accented', '=', repr(accented))
chars = len(accented)                     # 4
print('chars', '=', repr(chars))
utf8_bytes = len(accented.encode("utf-8"))   # 5
print('utf8_bytes', '=', repr(utf8_bytes))

age = 36
name = "Lokesh"
f1 = f"My name is {name} and my age is {age}"     # 'My name is Lokesh and my age is 36'
print('f1', '=', repr(f1))
f2 = "My age is {1} and the name is {0}".format(name, age)   # 'My age is 36 and the name is Lokesh'
print('f2', '=', repr(f2))
price = f"{1234.5:,.2f}"                          # '1,234.50'
print('price', '=', repr(price))
padded = f"[{name:>10}]"                          # '[    Lokesh]'
print('padded', '=', repr(padded))
debug = f"{age=}"                                 # 'age=36'
print('debug', '=', repr(debug))

full = "hello" + " " + "world"           # 'hello world'
print('full', '=', repr(full))
line = "-" * 10                           # '----------'
print('line', '=', repr(line))
csv_row = ",".join(["tea", "milk", "jam"])   # 'tea,milk,jam'
print('csv_row', '=', repr(csv_row))
numbers = " ".join(str(n) for n in [1, 2, 3])   # '1 2 3'
print('numbers', '=', repr(numbers))

a = "lokesh GUPTA".capitalize()        # 'Lokesh gupta'
print('a', '=', repr(a))
b = "38 yrs old lokesh".capitalize()   # '38 yrs old lokesh'
print('b', '=', repr(b))

a = "My Name is Lokesh".casefold()      # 'my name is lokesh'
print('a', '=', repr(a))
same = "STRASSE".casefold() == "Stra\u00dfe".casefold()   # True
print('same', '=', repr(same))

a = "hello world".center(20)          # '    hello world     '
print('a', '=', repr(a))
b = "hi".center(6, "*")               # '**hi**'
print('b', '=', repr(b))

n = "hello world".count("o")          # 2
print('n', '=', repr(n))
m = "aaaa".count("aa")                # 2, not 3
print('m', '=', repr(m))

b = "hello".encode()                  # b'hello'
print('b', '=', repr(b))
c = "caf\u00e9".encode("ascii", errors="replace")   # b'caf?'
print('c', '=', repr(c))

a = "report.pdf".endswith(".pdf")     # True
print('a', '=', repr(a))
b = "img.PNG".lower().endswith((".png", ".jpg"))   # True
print('b', '=', repr(b))

a = "a\tb".expandtabs(4)               # 'a   b'
print('a', '=', repr(a))

i = "hello world".find("o")           # 4
print('i', '=', repr(i))
j = "hello world".find("z")           # -1
print('j', '=', repr(j))

a = "{} is {} years".format("Alex", 30)   # 'Alex is 30 years'
print('a', '=', repr(a))
b = "{n:.1f}%".format(n=12.345)            # '12.3%'
print('b', '=', repr(b))

data = {"name": "Alex", "age": 30}
a = "{name} is {age}".format_map(data)     # 'Alex is 30'
print('a', '=', repr(a))

i = "hello world".index("w")          # 6
print('i', '=', repr(i))

a = "abc123".isalnum()                # True
print('a', '=', repr(a))
b = "abc 123".isalnum()               # False, the space
print('b', '=', repr(b))

a = "hello".isalpha()                 # True
print('a', '=', repr(a))
b = "hello1".isalpha()                # False
print('b', '=', repr(b))

a = "hello".isascii()                  # True
print('a', '=', repr(a))
b = "caf\u00e9".isascii()              # False
print('b', '=', repr(b))

a = "123".isdecimal()                 # True
print('a', '=', repr(a))
b = "\u00b2".isdecimal()              # False, superscript two
print('b', '=', repr(b))

a = "123".isdigit()                   # True
print('a', '=', repr(a))
b = "\u00b2".isdigit()                # True
print('b', '=', repr(b))
c = "-5".isdigit()                    # False, the minus sign
print('c', '=', repr(c))

a = "total_2".isidentifier()          # True
print('a', '=', repr(a))
b = "2total".isidentifier()           # False
print('b', '=', repr(b))

a = "hello 1".islower()               # True
print('a', '=', repr(a))
b = "Hello".islower()                 # False
print('b', '=', repr(b))

a = "\u00bd".isnumeric()              # True, the one-half character
print('a', '=', repr(a))
b = "1.5".isnumeric()                 # False, the dot
print('b', '=', repr(b))

a = "hello".isprintable()             # True
print('a', '=', repr(a))
b = "hello\n".isprintable()           # False
print('b', '=', repr(b))

a = " \t\n".isspace()                 # True
print('a', '=', repr(a))
b = "".isspace()                      # False
print('b', '=', repr(b))

a = "Hello World".istitle()           # True
print('a', '=', repr(a))
b = "Hello world".istitle()           # False
print('b', '=', repr(b))

a = "HELLO 1".isupper()               # True
print('a', '=', repr(a))

a = ", ".join(["tea", "milk"])        # 'tea, milk'
print('a', '=', repr(a))
b = "".join(reversed("abc"))          # 'cba'
print('b', '=', repr(b))

a = "tea".ljust(6, ".") + "3.50"     # 'tea...3.50'
print('a', '=', repr(a))

a = "Hello World".lower()             # 'hello world'
print('a', '=', repr(a))

a = "   hi".lstrip()                  # 'hi'
print('a', '=', repr(a))
b = "www.site.com".lstrip("w.")       # 'site.com'
print('b', '=', repr(b))

table = str.maketrans("ae", "43", "!")
leet = "hate!".translate(table)        # 'h4t3'
print('leet', '=', repr(leet))

a = "key=value=x".partition("=")      # ('key', '=', 'value=x')
print('a', '=', repr(a))
b = "novalue".partition("=")          # ('novalue', '', '')
print('b', '=', repr(b))

a = "www.site.com".removeprefix("www.")   # 'site.com'
print('a', '=', repr(a))
b = "report.csv".removesuffix(".csv")     # 'report'
print('b', '=', repr(b))
wrong = "docs.csv".rstrip(".csv")         # 'do', strips any of the characters c, s, v and .
print('wrong', '=', repr(wrong))

a = "a-b-c".replace("-", "+")         # 'a+b+c'
print('a', '=', repr(a))
b = "a-b-c".replace("-", "+", 1)      # 'a+b-c'
print('b', '=', repr(b))

i = "hello world".rfind("o")          # 7
print('i', '=', repr(i))

i = "a/b/c".rindex("/")               # 3
print('i', '=', repr(i))

a = "42".rjust(5)                     # '   42'
print('a', '=', repr(a))

a = "archive.tar.gz".rpartition(".")  # ('archive.tar', '.', 'gz')
print('a', '=', repr(a))

a = "a,b,c".rsplit(",", 1)            # ['a,b', 'c']
print('a', '=', repr(a))

a = "line\n".rstrip("\n")              # 'line'
print('a', '=', repr(a))
b = "3.1400".rstrip("0")              # '3.14'
print('b', '=', repr(b))

a = "a  b c".split()                  # ['a', 'b', 'c']
print('a', '=', repr(a))
b = "a,,b".split(",")                 # ['a', '', 'b']
print('b', '=', repr(b))

a = "one\ntwo\r\nthree".splitlines()   # ['one', 'two', 'three']
print('a', '=', repr(a))

a = "https://x.com".startswith(("http://", "https://"))   # True
print('a', '=', repr(a))

a = "  hello  ".strip()               # 'hello'
print('a', '=', repr(a))
b = "##title##".strip("#")            # 'title'
print('b', '=', repr(b))

a = "Hello World".swapcase()          # 'hELLO wORLD'
print('a', '=', repr(a))

a = "hello world".title()             # 'Hello World'
print('a', '=', repr(a))
b = "they're here".title()            # "They'Re Here"
print('b', '=', repr(b))

no_digits = "a1b2c3".translate(str.maketrans("", "", "0123456789"))   # 'abc'
print('no_digits', '=', repr(no_digits))

a = "hello world".upper()             # 'HELLO WORLD'
print('a', '=', repr(a))

a = "42".zfill(5)                     # '00042'
print('a', '=', repr(a))
b = "-42".zfill(5)                    # '-0042'
print('b', '=', repr(b))

def normalize_email(raw):
    email = raw.strip().casefold()
    local, _, domain = email.partition("@")
    local = local.split("+")[0]               # drop +tags
    return f"{local}@{domain}" if local and domain else None

emails = ["  Alex@Example.COM ", "alex+news@example.com", "bad-address"]
clean = [normalize_email(e) for e in emails]
# ['alex@example.com', 'alex@example.com', None]
