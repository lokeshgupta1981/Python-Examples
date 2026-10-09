import time
import sys
import itertools

print("Loading", end="")
print("...done")          # Loading...done

for n in [1, 2, 3]:
    print(n, end=" ")
print()                   # ends the line

print("a", "b", "c", sep="-", end="!\n")    # a-b-c!
print("a", "b", "c", sep="")               # abc

scores = [90, 85, 77]
print(*scores, sep=", ")                       # 90, 85, 77
line = ", ".join(str(s) for s in scores)       # '90, 85, 77'
print('line', '=', repr(line))


for pct in range(0, 101, 25):
    print(f"\rProgress: {pct}%", end="", flush=True)
    time.sleep (0.2)
print()


count = sys.stdout.write("no newline here")    # count = 15
print('count', '=', repr(count))
sys.stdout.write("\n")


frames = itertools.cycle("|/-\\")
for _ in range(8):
    print(f"\rWorking {next(frames)}", end="", flush=True)
    time.sleep (0.1)
print("\rWorking done")
