import heapq
import itertools
from dataclasses import dataclass, field
from queue import PriorityQueue
from typing import Any
import bisect

tasks = []
heapq.heappush(tasks, (2, "send report"))
heapq.heappush(tasks, (1, "fix outage"))
first = heapq.heappop(tasks)          # (1, 'fix outage')
print('first', '=', repr(first))

jobs = [(5, "backup"), (1, "deploy"), (3, "email")]
heapq.heapify(jobs)
order = [heapq.heappop(jobs)[1] for _ in range(3)]   # ['deploy', 'email', 'backup']
print('order', '=', repr(order))


counter = itertools.count()
heap = []
for prio, task in [(2, {"name": "a"}), (1, {"name": "b"}), (2, {"name": "c"})]:
    heapq.heappush(heap, (prio, next(counter), task))
names = [heapq.heappop(heap)[2]["name"] for _ in range(3)]   # ['b', 'a', 'c']
print('names', '=', repr(names))

scores = []
for s in [40, 95, 70]:
    heapq.heappush_max(scores, s)
best = heapq.heappop_max(scores)        # 95 (Python 3.14+)
print('best', '=', repr(best))

old_style = []
for s in [40, 95, 70]:
    heapq.heappush(old_style, -s)
best_old = -heapq.heappop(old_style)    # 95
print('best_old', '=', repr(best_old))


@dataclass(order=True)
class Job:
    priority: int
    item: Any = field(compare=False)

q = PriorityQueue()
for p, name in [(5, "how"), (4, "to"), (1, "do"), (3, "in"), (2, "java")]:
    q.put(Job(p, name))
served = [q.get().item for _ in range(5)]      # ['do', 'java', 'in', 'to', 'how']
print('served', '=', repr(served))


ordered = []
for job in [(3, "in"), (1, "do"), (2, "java")]:
    bisect.insort(ordered, job)
# ordered = [(1, 'do'), (2, 'java'), (3, 'in')]
lowest = ordered.pop(0)                 # (1, 'do')
print('lowest', '=', repr(lowest))

def run(initial):
    heap, seq = [], itertools.count()
    for prio, name in initial:
        heapq.heappush(heap, (prio, next(seq), name))
    done = []
    while heap:
        prio, _, name = heapq.heappop(heap)
        done.append(name)
        if name == "deploy":                       # deploying creates a follow-up task
            heapq.heappush(heap, (1, next(seq), "smoke test"))
    return done

log = run([(2, "deploy"), (3, "email"), (2, "backup")])
# ['deploy', 'smoke test', 'backup', 'email']
