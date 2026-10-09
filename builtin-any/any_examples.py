mytuple = (0, 1, False)
bool_result = any(mytuple)    # True, because 1 is truthy
print('bool_result', '=', repr(bool_result))

t = any((0, 1, False))           # True
print('t', '=', repr(t))
l = any([0, False])               # False
print('l', '=', repr(l))
d1 = any({0: "False"})            # False, checks the key 0
print('d1', '=', repr(d1))
d2 = any({0: "False", 1: "True"}) # True, the key 1 is truthy
print('d2', '=', repr(d2))
values = any({"a": 0}.values())   # False, checks the values
print('values', '=', repr(values))
s1 = any("")                      # False, no characters
print('s1', '=', repr(s1))
s2 = any("  ")                    # True, a space is a non-empty string
print('s2', '=', repr(s2))

log = ["INFO start", "ERROR disk full", "INFO stop"]
has_error = any("ERROR" in line for line in log)    # True
print('has_error', '=', repr(has_error))

numbers = iter([1, 3, 4, 5, 7])
found_even = any(n % 2 == 0 for n in numbers)       # True, stops at 4
print('found_even', '=', repr(found_even))
left = list(numbers)                                # [5, 7], never checked
print('left', '=', repr(left))

first = 0 or "" or "red"          # 'red'
print('first', '=', repr(first))
flag = any([0, "", "red"])         # True
print('flag', '=', repr(flag))

password = "tea4Two"
has_digit = any(c.isdigit() for c in password)     # True
print('has_digit', '=', repr(has_digit))
has_upper = any(c.isupper() for c in password)     # True
print('has_upper', '=', repr(has_upper))
has_symbol = any(not c.isalnum() for c in password)  # False
print('has_symbol', '=', repr(has_symbol))
