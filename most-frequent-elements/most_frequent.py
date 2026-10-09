from collections import Counter
import statistics
import pandas as pd
import numpy as np
import re

sequence = [1, 2, 3, 4, 1, 2, 1, 2, 1]
counter = Counter(sequence)
top_two = counter.most_common(2)        # [(1, 4), (2, 3)]
print('top_two', '=', repr(top_two))
top, count = counter.most_common(1)[0]  # top = 1, count = 4
print('top', '=', repr(top))
print('count', '=', repr(count))
missing = counter[9]                    # 0
print('missing', '=', repr(missing))

nested = [[1], [2], [1], [2], [1]]
counts = Counter(tuple(x) for x in nested)
most = counts.most_common(1)            # [((1,), 3)]
print('most', '=', repr(most))


votes = ["tea", "coffee", "coffee", "tea", "juice"]
first_mode = statistics.mode(votes)          # 'tea'
print('first_mode', '=', repr(first_mode))
all_modes = statistics.multimode(votes)      # ['tea', 'coffee']
print('all_modes', '=', repr(all_modes))
counted = Counter(votes).most_common(2)      # [('tea', 2), ('coffee', 2)]
print('counted', '=', repr(counted))


s = pd.Series(sequence)
top_value = s.value_counts().idxmax()        # 1
print('top_value', '=', repr(top_value))
modes = s.mode().tolist()                    # [1]
print('modes', '=', repr(modes))


arr = np.array(sequence)
by_bincount = np.bincount(arr).argmax()            # np.int64(1)
print('by_bincount', '=', repr(by_bincount))
values, counts = np.unique(arr, return_counts=True)
by_unique = values[counts.argmax()]                # np.int64(1)
print('by_unique', '=', repr(by_unique))

empty_counter = Counter([]).most_common(1)     # []
print('empty_counter', '=', repr(empty_counter))
try:
    empty_mode = statistics.mode([])
except Exception as e:
    print(type(e).__name__ + ':', e)
empty_multi = statistics.multimode([])         # []
print('empty_multi', '=', repr(empty_multi))


text = "Tea, then more tea. Coffee? No, tea!"
words = re.findall(r"[a-z]+", text.lower())
top_words = Counter(words).most_common(2)      # [('tea', 3), ('then', 1)]
print('top_words', '=', repr(top_words))
