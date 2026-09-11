#!/usr/bin/env python3
"""One-shot copy of verified downloaded native capture/repeat pairs, not synthesis."""
import argparse
import json
from pathlib import Path
import shutil
from numeric_capture import compare, negative

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('download', type=Path)
    p.add_argument('destination', type=Path)
    args = p.parse_args()
    if args.destination.exists():
        raise ValueError('refusing to overwrite frozen numeric observations')
    captures = list(args.download.glob('*/numeric.json'))
    if len(captures) != 3:
        raise ValueError('requires three actual downloaded native captures')
    verified = {}
    for path in captures:
        actual = json.loads(path.read_text())
        compare(actual, json.loads(path.with_name('numeric-repeat.json').read_text()))
        negative(actual)
        name = {'Linux': 'linux', 'Windows': 'windows', 'Darwin': 'macos'}[actual['platform']]
        if name in verified:
            raise ValueError('duplicate native platform')
        verified[name] = path
    args.destination.mkdir(parents=True)
    for name, path in verified.items():
        shutil.copyfile(path, args.destination / (name + '.json'))
        print(name, 'verified native pair copied verbatim')
