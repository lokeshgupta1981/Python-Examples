from collections import Counter

a = {'x': 1, 'y': 2, 'z': 3}
b = {'u': 1, 'v': 2, 'w': 3, 'x': 1, 'y': 2}

common_keys = a.keys() & b.keys()      # {'x', 'y'}
print('common_keys', '=', repr(common_keys))
common_items = a.items() & b.items()   # {('x', 1), ('y', 2)}
print('common_items', '=', repr(common_items))

dictA = {'x': 1, 'y': 2, 'z': 3}
dictB = {'u': 1, 'v': 2, 'w': 3, 'x': 1, 'y': 2}

common_keys = dictA.keys() & dictB.keys()   # {'x', 'y'}
print('common_keys', '=', repr(common_keys))
setOfCommonKeys = set(dictA) & set(dictB)   # {'x', 'y'}
print('setOfCommonKeys', '=', repr(setOfCommonKeys))

setOfCommonKeys = set(dictA).intersection(dictB)   # {'x', 'y'}
print('setOfCommonKeys', '=', repr(setOfCommonKeys))


cartA = {'apple': 3, 'pear': 2, 'kiwi': 1}
cartB = {'apple': 1, 'pear': 5}
both = Counter(cartA) & Counter(cartB)     # Counter({'pear': 2, 'apple': 1})
print('both', '=', repr(both))

common = {key: dictA[key] for key in dictA if key in dictB}   # {'x': 1, 'y': 2}
print('common', '=', repr(common))

prices_jan = {'tea': 4, 'milk': 2, 'rice': 9}
prices_feb = {'tea': 4, 'milk': 3, 'rice': 9}
unchanged = dict(prices_jan.items() & prices_feb.items())   # {'tea': 4, 'rice': 9}, in any order
print('unchanged', '=', repr(unchanged))

dicts = [{'x': 1, 'y': 2}, {'x': 5, 'y': 0, 'z': 1}, {'y': 7, 'x': 2}]
in_all = set(dicts[0]).intersection(*dicts[1:])    # {'x', 'y'}
print('in_all', '=', repr(in_all))

only_a = dictA.keys() - dictB.keys()     # {'z'}
print('only_a', '=', repr(only_a))
either = dictA.keys() ^ dictB.keys()     # {'z', 'u', 'v', 'w'}, in any order
print('either', '=', repr(either))
