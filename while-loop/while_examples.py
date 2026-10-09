import time

attempt = 1
while attempt <= 3:
    print("Attempt", attempt)
    attempt += 1

count = 10
while count < 3:
    print("never printed")
print("after the loop")          # the only line printed

checks = [False, False, True]          # pretend status results
print('checks', '=', repr(checks))
tries = 0
while True:
    ready = checks[tries]
    tries += 1
    if ready:
        break
print("Ready after", tries, "checks")    # Ready after 3 checks

n = 0
while n < 6:
    n += 1
    if n % 2 == 0:
        continue
    print("odd", n)
else:
    print("loop finished without break")

items = []
while (line := input("Item (blank to stop): ").strip()) != "":
    items.append(line)
print("Items:", items)

guesses = iter([7, 3, 5])                # pretend user guesses
print('guesses', '=', repr(guesses))
secret = 5
while True:
    guess = next(guesses)
    print("Guess:", guess)
    if guess == secret:
        break


results = iter([False, False, True])     # pretend call results
print('results', '=', repr(results))
attempt, delay = 1, 0.1
while not next(results):
    print(f"attempt {attempt} failed, waiting {delay:.1f}s")
    time.sleep (delay)
    attempt += 1
    delay *= 2
print("succeeded on attempt", attempt)
