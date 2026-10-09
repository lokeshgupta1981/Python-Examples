playlist = ["Intro", "Sunrise", "Rain", "Outro"]
for song in playlist:
    if song == "Rain":
        print("Found", song)
        break
    print("Skipping", song)

for song in playlist:
    if song == "Thunder":
        print("Found", song)
        break
else:
    print("Thunder is not in the playlist")

attempts = 0
while True:
    attempts += 1
    if attempts == 3:
        break
print("attempts =", attempts)    # attempts = 3

shelves = [["salt", "rice"], ["sugar", "tea"]]
for shelf in shelves:
    for jar in shelf:
        if jar == "rice":
            break
        print("Checked", jar)

def find(shelves, wanted):
    for row, shelf in enumerate(shelves):
        for col, jar in enumerate(shelf):
            if jar == wanted:
                return row, col
    return None

position = find(shelves, "tea")    # (1, 1)
print('position', '=', repr(position))

first_long = next((s for s in playlist if len(s) > 5), None)   # 'Sunrise'
print('first_long', '=', repr(first_long))
has_rain = any(s == "Rain" for s in playlist)                  # True
print('has_rain', '=', repr(has_rain))

def connect(attempt):
    return attempt == 2          # pretend the second try succeeds

for attempt in range(1, 4):
    if connect(attempt):
        print("Connected on attempt", attempt)
        break
    print("Attempt", attempt, "failed")
else:
    print("Gave up after 3 attempts")
