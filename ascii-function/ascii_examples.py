import json
import unicodedata

name = "José"
escaped = ascii(name)     # 'Jos\xe9'
print('escaped', '=', repr(escaped))
shown = repr(name)        # 'José'
print('shown', '=', repr(shown))

a = ascii("café")      # 'caf\xe9'        code point below 256, \x
print('a', '=', repr(a))
b = ascii("Ωmega")     # '\u03a9mega'     up to 0xFFFF, \u
print('b', '=', repr(b))
c = ascii("ok 😀")     # 'ok \U0001f600'  above 0xFFFF, \U
print('c', '=', repr(c))

names = ascii(["Zoë", "Ana"])        # ['Zo\xeb', 'Ana']
print('names', '=', repr(names))
city = ascii({"city": "Málaga"})     # {'city': 'M\xe1laga'}
print('city', '=', repr(city))

code = ord("é")        # 233
print('code', '=', repr(code))
char = chr(233)        # 'é'
print('char', '=', repr(char))
hex_code = hex(233)    # '0xe9'
print('hex_code', '=', repr(hex_code))
tab = ascii("a\tb")    # 'a\tb', repr() escapes \t as well
print('tab', '=', repr(tab))


raw = "José".encode("ascii", "backslashreplace")         # b'Jos\\xe9'
print('raw', '=', repr(raw))
as_json = json.dumps({"name": "José"})                   # '{"name": "Jos\u00e9"}'
print('as_json', '=', repr(as_json))
as_utf8 = json.dumps({"name": "José"}, ensure_ascii=False)   # '{"name": "José"}'
print('as_utf8', '=', repr(as_utf8))

price = "100\xa0USD"                # copied from a web page
print('price', '=', repr(price))
same = price == "100 USD"           # False
print('same', '=', repr(same))
shown = ascii(price)                # '100\xa0USD'
print('shown', '=', repr(shown))
fixed = price.replace("\xa0", " ") == "100 USD"   # True
print('fixed', '=', repr(fixed))

plain = "cafe".isascii()     # True
print('plain', '=', repr(plain))
accented = "café".isascii()  # False
print('accented', '=', repr(accented))


dropped = "café".encode("ascii", "ignore").decode()   # 'caf'
print('dropped', '=', repr(dropped))
plain = unicodedata.normalize("NFKD", "café").encode("ascii", "ignore").decode()   # 'cafe'
print('plain', '=', repr(plain))
