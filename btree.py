import collections
import csv
import itertools
import re

class BTree:
    def __init__(self, label='BTree', hiearchy_separator='/'):
        self.data = BTree.__make_btree()
        self.num_elements = 0
        self.label = label
        self.hierarchy_separator = hiearchy_separator
        self.hdepth = 0

    def rollup_by_hierarchy(self, pattern, rollup_func):
        rolled_up = BTree(f"{self.label}_hierarchy_rolled_up")
        BTree.__hrollup(self.data, rolled_up, pattern, rollup_func, [], self.hierarchy_separator)
        return rolled_up
    
    def to_csv(self, file_name):
        with open(file_name, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            for k, v in BTree.recursive_collect(self.data, preserve_key=True):
                depth = k.count(self.hierarchy_separator)
                _additions = ('.'*(self.hdepth-depth)).split('.')
                if _additions:
                    _k = k.split(self.hierarchy_separator) + _additions + [v]
                else:
                    _k = k.split(self.hierarchy_separator) + [v]
                print(_k)
                csvwriter.writerow(_k)

    def __setitem__(self, key, value):
        self.num_elements += 1
        BTree.__insert(key, value, self.data, self.hierarchy_separator)
        hdepth = key.count(self.hierarchy_separator)
        if hdepth > self.hdepth:
            self.hdepth = hdepth

    def __getitem__(self, key):
        return BTree.__get(key, self.data, self.hierarchy_separator)
    
    def __repr__(self):
        return f"{self.label}({self.num_elements})"
    
    @staticmethod
    def __hrollup(data, ru, pattern, rf, ksf, hs):
        match = [k for k in data.keys() if re.search(pattern, hs.join(ksf + [k]))]
        for matched_key in match:
            result = BTree.recursive_collect(data[matched_key])
            ru[hs.join(ksf + [matched_key])] = rf(result)
        if not match:
            for k, v in data.items():
                if is_dict(v):
                    BTree.__hrollup(v, ru, pattern, rf, ksf + [k], hs)

    @staticmethod
    def __make_btree():
        return collections.defaultdict(BTree.__make_btree)
    
    @staticmethod
    def __insert(key, value, loc, separator):
        try:
            m, n = key.split(separator, 1)
            BTree.__insert(n, value, loc[m], separator)
        except ValueError:
            loc[key] = value

    @staticmethod
    def __get(key, loc, separator):
        try:
            m, n = key.split(separator, 1)
            return BTree.__get(n, loc[m], separator)
        except ValueError:
            return loc[key]

    @staticmethod    
    def recursive_collect(dd, preserve_key=False, pk=''):
        result = []
        for k, v in dd.items():
            _pk = '/'.join([x for x in [pk, k] if x]) if preserve_key else ''
            if is_dict(v):
                result.extend(BTree.recursive_collect(v, preserve_key, _pk))
            else:
                if preserve_key:
                    result.extend([(_pk, v)])
                else:
                    result.extend([v])
        return result

def is_dict(v):
    return isinstance(v, dict) or isinstance(v, collections.defaultdict)

def ddict2dict(ddict):
    result = dict()
    for k, v in ddict.items():
        if isinstance(v, collections.defaultdict):
            result[k] = ddict2dict(v)
        else:
            result[k] = v
    return result

animals = BTree('Animals')
total = 0.0

with open("test", "r") as fp:
    for line in fp:
        data = line.strip().split()
        strength = float(data[-1])
        total += strength
        animals[data[0]] = strength

print(f"Total: {total:.2f}")

import json

pattern = ".*mammal.*"
cc = animals.rollup_by_hierarchy(re.compile(pattern), sum)
print(json.dumps(cc.data, indent=4))
print(cc.hdepth)
print(animals.hdepth)
animals.to_csv('animals.csv')