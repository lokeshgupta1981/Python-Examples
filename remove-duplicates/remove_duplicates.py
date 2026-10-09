from collections import OrderedDict
import numpy as np
import pandas as pd

original_list = [5, 1, 2, 4, 2, 3, 1]
unique = list(dict.fromkeys(original_list))     # [5, 1, 2, 4, 3]
print('unique', '=', repr(unique))
unordered = list(set(original_list))            # [1, 2, 3, 4, 5], order lost
print('unordered', '=', repr(unordered))

def remove_duplicates_seen(lst):
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

result = remove_duplicates_seen(original_list)    # [5, 1, 2, 4, 3]
print('result', '=', repr(result))


with_dict = list(dict.fromkeys(original_list))           # [5, 1, 2, 4, 3]
print('with_dict', '=', repr(with_dict))
with_ordered = list(OrderedDict.fromkeys(original_list)) # [5, 1, 2, 4, 3]
print('with_ordered', '=', repr(with_ordered))


arr = np.array(original_list)
sorted_unique = np.unique(arr)                          # array([1, 2, 3, 4, 5])
print('sorted_unique', '=', repr(sorted_unique))
_, idx = np.unique(arr, return_index=True)
ordered_unique = arr[np.sort(idx)]                       # array([5, 1, 2, 4, 3])
print('ordered_unique', '=', repr(ordered_unique))


s = pd.Series(original_list)
unique_series = s.drop_duplicates().tolist()            # [5, 1, 2, 4, 3]
print('unique_series', '=', repr(unique_series))
df = pd.DataFrame({"email": ["a@x.com", "b@x.com", "a@x.com"], "visit": [1, 2, 3]})
first_visits = df.drop_duplicates(subset="email")["visit"].tolist()   # [1, 2]
print('first_visits', '=', repr(first_visits))

emails = ["Ana@x.com", "bob@x.com", "ana@X.com"]
seen, unique_emails = set(), []
for e in emails:
    key = e.lower()
    if key not in seen:
        seen.add(key)
        unique_emails.append(e)
# unique_emails = ['Ana@x.com', 'bob@x.com']

rows = [{"id": 1}, {"id": 2}, {"id": 1}]
seen, unique_rows = set(), []
for r in rows:
    key = tuple(sorted(r.items()))
    if key not in seen:
        seen.add(key)
        unique_rows.append(r)
# unique_rows = [{'id': 1}, {'id': 2}]
