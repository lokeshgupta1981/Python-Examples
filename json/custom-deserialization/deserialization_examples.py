import json
from dataclasses import dataclass
from datetime import date

@dataclass
class Booking:
    guest: str
    nights: int
    check_in: date

def to_booking(d):
    return Booking(d["guest"], d["nights"], date.fromisoformat(d["check_in"]))

text = '{"guest": "Lokesh", "nights": 3, "check_in": "2026-11-02"}'
booking = json.loads(text, object_hook=to_booking)
# Booking(guest='Lokesh', nights=3, check_in=datetime.date(2026, 11, 2))

def show(d):
    print("hook got:", d)
    return d

data = json.loads('{"guest": "Ana", "room": {"no": 12}}', object_hook=show)

def hook(d):
    if {"guest", "nights", "check_in"} <= d.keys():
        return Booking(d["guest"], d["nights"], date.fromisoformat(d["check_in"]))
    return d

payload = """{"hotel": "Sea View", "bookings": [
  {"guest": "Lokesh", "nights": 3, "check_in": "2026-11-02"},
  {"guest": "Ana", "nights": 1, "check_in": "2026-11-05"}]}"""
result = json.loads(payload, object_hook=hook)
first = result["bookings"][0].guest      # 'Lokesh'
print('first', '=', repr(first))
when = result["bookings"][1].check_in    # datetime.date(2026, 11, 5)
print('when', '=', repr(when))

b = Booking(**{"guest": "Ana", "nights": 1, "check_in": "2026-11-05"})
kind = type(b.check_in)              # <class 'str'>, not a date
print('kind', '=', repr(kind))
data = {"guest": "Ana", "nights": 1, "check_in": "x", "vip": True}
try:
    extra = Booking(**data)
except Exception as e:
    print(type(e).__name__ + ':', e)

class BookingDecoder(json.JSONDecoder):
    def __init__(self, **kwargs):
        super().__init__(object_hook=hook, **kwargs)

bookings = json.loads(payload, cls=BookingDecoder)["bookings"]
count = len(bookings)                 # 2
print('count', '=', repr(count))

def no_duplicates(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError(f"duplicate keys in {keys}")
    return dict(pairs)

text2 = '{"nights": 1, "nights": 5}'
silent = json.loads(text2)                                   # {'nights': 5}
print('silent', '=', repr(silent))
try:
    strict = json.loads(text2, object_pairs_hook=no_duplicates)
except Exception as e:
    print(type(e).__name__ + ':', e)

def safe_booking(d):
    try:
        return Booking(str(d["guest"]), int(d["nights"]), date.fromisoformat(d["check_in"]))
    except (KeyError, ValueError, TypeError) as e:
        raise ValueError(f"bad booking {d}: {e}") from None

ok = json.loads('{"guest": "Ana", "nights": "2", "check_in": "2026-11-05"}', object_hook=safe_booking)
nights = ok.nights      # 2, converted from the string "2"
print('nights', '=', repr(nights))
