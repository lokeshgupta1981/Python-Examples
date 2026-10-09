import string

city = "new YORK"
capitalized = city.capitalize()     # 'New york'
print('capitalized', '=', repr(capitalized))
original = city                     # 'new YORK', strings are immutable
print('original', '=', repr(original))


text = "the world's best pizza"
a = text.capitalize()          # "The world's best pizza"
print('a', '=', repr(a))
b = text.title()               # "The World'S Best Pizza"
print('b', '=', repr(b))
c = string.capwords(text)      # "The World's Best Pizza"
print('c', '=', repr(c))
d = text.upper()               # "THE WORLD'S BEST PIZZA"
print('d', '=', repr(d))

age = "25 years OLD".capitalize()      # '25 years old'
print('age', '=', repr(age))
spaced = " hello".capitalize()         # ' hello', the space is the first character
print('spaced', '=', repr(spaced))
clean = " hello".strip().capitalize()  # 'Hello'
print('clean', '=', repr(clean))

name = "mcDonald"
wrong = name.capitalize()              # 'Mcdonald'
print('wrong', '=', repr(wrong))
first_only = name[:1].upper() + name[1:]   # 'McDonald'
print('first_only', '=', repr(first_only))

a = "straße".capitalize()    # 'Straße'
print('a', '=', repr(a))
b = "ßtraße".capitalize()    # 'Sstraße', Python maps ß to 'SS' in upper and titlecase
print('b', '=', repr(b))
c = "ǆemal".capitalize()     # 'ǅemal', the two-letter character ǆ has its own titlecase form
print('c', '=', repr(c))

def tidy_name(raw):
    words = raw.strip().split()
    return " ".join(w[:1].upper() + w[1:] for w in words)

n1 = tidy_name("  lokesh gupta ")     # 'Lokesh Gupta'
print('n1', '=', repr(n1))
n2 = tidy_name("ronald mcDonald")     # 'Ronald McDonald'
print('n2', '=', repr(n2))
n3 = tidy_name("o'neil")              # "O'neil"
print('n3', '=', repr(n3))
t3 = "o'neil".title()                 # "O'Neil"
print('t3', '=', repr(t3))

text = "first line. second line. third"
fixed = ". ".join(s.capitalize() for s in text.split(". "))   # 'First line. Second line. Third'
print('fixed', '=', repr(fixed))
