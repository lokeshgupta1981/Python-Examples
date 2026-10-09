import re

text = "HowToDoInJava.com"
start, end = "How", "com"

s1 = text.startswith(start)                      # True
print('s1', '=', repr(s1))
e1 = text.endswith(end)                          # True
print('e1', '=', repr(e1))
s2 = re.match(re.escape(start), text) is not None   # True
print('s2', '=', repr(s2))
e2 = re.search(re.escape(end) + r"\Z", text) is not None   # True
print('e2', '=', repr(e2))
s3 = text[:len(start)] == start                  # True
print('s3', '=', repr(s3))
e3 = text[-len(end):] == end                     # True
print('e3', '=', repr(e3))

starts = bool(re.match(r"How", text))          # True
print('starts', '=', repr(starts))
ends_dollar = bool(re.search(r"com$", "site.com\n"))   # True, $ also matches before a final newline
print('ends_dollar', '=', repr(ends_dollar))
ends_z = bool(re.search(r"com\Z", "site.com\n"))       # False, \Z means the real end
print('ends_z', '=', repr(ends_z))

loose = bool(re.search(".com$", "xcom"))                 # True, wrong
print('loose', '=', repr(loose))
exact = bool(re.search(re.escape(".com") + r"\Z", "xcom"))   # False
print('exact', '=', repr(exact))

url = "https://example.com/report.pdf"
secure = url.startswith(("https://", "sftp://"))     # True
print('secure', '=', repr(secure))
document = url.endswith((".pdf", ".docx"))           # True
print('document', '=', repr(document))

prefix_ok = text[:3] == "How"         # True
print('prefix_ok', '=', repr(prefix_ok))
suffix_ok = text[-3:] == "com"        # True
print('suffix_ok', '=', repr(suffix_ok))
empty_end = text[-len(""):] == ""     # False, -0 means the whole string
print('empty_end', '=', repr(empty_end))

value = '"Lokesh"'
quoted = value.startswith('"') and value.endswith('"')     # True
print('quoted', '=', repr(quoted))
inner = value[1:-1] if quoted else value                   # 'Lokesh'
print('inner', '=', repr(inner))
tag = bool(re.fullmatch(r"\[.*\]", "[ERROR]"))             # True
print('tag', '=', repr(tag))
