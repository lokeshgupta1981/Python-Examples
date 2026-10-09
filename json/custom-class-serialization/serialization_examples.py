import json
from dataclasses import dataclass
from datetime import date
from enum import Enum

@dataclass
class Booking:
    guest: str
    nights: int
    check_in: date

booking = Booking("Lokesh", 3, date(2026, 11, 2))
try:
    bad = json.dumps(booking)
except Exception as e:
    print(type(e).__name__ + ':', e)


def to_json(obj):
    if isinstance(obj, Booking):
        return {"guest": obj.guest, "nights": obj.nights, "check_in": obj.check_in}
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"Cannot serialize {type(obj).__name__}")

text = json.dumps(booking, default=to_json)
# {"guest": "Lokesh", "nights": 3, "check_in": "2026-11-02"}

class BookingEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Booking):
            return {"guest": obj.guest, "nights": obj.nights, "check_in": obj.check_in}
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

text2 = json.dumps(booking, cls=BookingEncoder, indent=2)

from dataclasses import asdict

text3 = json.dumps(asdict(booking), default=str)
# {"guest": "Lokesh", "nights": 3, "check_in": "2026-11-02"}

class Guest:
    def __init__(self, name, vip):
        self.name = name
        self.vip = vip

text4 = json.dumps(Guest("Lokesh", True), default=lambda o: o.__dict__)
# {"name": "Lokesh", "vip": true}


class Room(Enum):
    SINGLE = "single"
    DOUBLE = "double"

def to_json2(obj):
    if isinstance(obj, Booking):
        return asdict(obj)
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, set):
        return sorted(obj)
    raise TypeError(f"Cannot serialize {type(obj).__name__}")

data = {"room": Room.DOUBLE, "tags": {"sea", "quiet"}, "bookings": [booking]}
text5 = json.dumps(data, default=to_json2)
# {"room": "double", "tags": ["quiet", "sea"], "bookings": [{"guest": "Lokesh", "nights": 3, "check_in": "2026-11-02"}]}
