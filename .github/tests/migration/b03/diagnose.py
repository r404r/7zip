#!/usr/bin/env python3
"""Print differing stable fields from two captured reports without changing them."""
import argparse
import json
from pathlib import Path
from validate import stable


def differences(a, b, path=''):
    if type(a) is not type(b):
        print(path, repr(a), repr(b))
    elif isinstance(a, dict):
        for key in sorted(a.keys() | b.keys()):
            if key not in a or key not in b:
                print(path, key, 'missing')
            else:
                differences(a[key], b[key], path + '/' + key)
    elif isinstance(a, list):
        if len(a) != len(b):
            print(path, 'length', len(a), len(b))
        for index, (x, y) in enumerate(zip(a, b)):
            differences(x, y, path + '/' + str(index))
    elif a != b:
        print(path, repr(a), repr(b))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('repeat', type=Path)
    args = parser.parse_args()
    differences(stable(json.loads(args.capture.read_text())),
                stable(json.loads(args.repeat.read_text())))
