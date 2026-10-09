temperature = 31
if temperature > 30:
    advice = "Stay indoors"
elif temperature > 20:
    advice = "Go for a walk"
else:
    advice = "Take a jacket"
# advice = 'Stay indoors'

def shipping(total):
    if total >= 100:
        return 0
    elif total >= 50:
        return 5
    else:
        return 10

prices = [shipping(t) for t in (120, 60, 20)]   # [0, 5, 10]
print('prices', '=', repr(prices))

age = 30
member = True
adult = 18 <= age < 65                  # True
print('adult', '=', repr(adult))
discount = member and age >= 60         # False
print('discount', '=', repr(discount))
allowed = age >= 18 or member           # True
print('allowed', '=', repr(allowed))

color = "green"
wrong = bool(color == "red" or "blue")    # True, always
print('wrong', '=', repr(wrong))
right = color in ("red", "blue")          # False
print('right', '=', repr(right))

cart = []
if cart:
    status = "checkout"
else:
    status = "cart is empty"           # this branch runs

stock = 0
label = "In stock" if stock > 0 else "Sold out"     # 'Sold out'
print('label', '=', repr(label))

def describe(code):
    match code:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500 | 503:
            return "Server error"
        case _:
            return "Unknown"

messages = {200: "OK", 404: "Not Found"}
m1 = describe(503)                    # 'Server error'
print('m1', '=', repr(m1))
m2 = messages.get(301, "Unknown")     # 'Unknown'
print('m2', '=', repr(m2))

def grade(score):
    if not 0 <= score <= 100:
        raise ValueError(f"score out of range: {score}")
    if score >= 90:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 50:
        return "C"
    return "F"

grades = [grade(s) for s in (95, 75, 40)]   # ['A', 'B', 'F']
print('grades', '=', repr(grades))
