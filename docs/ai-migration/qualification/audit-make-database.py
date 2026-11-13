#!/usr/bin/env python3
"""Check only variable NAMES for accidental environment capture; never print values."""
import argparse
import re
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('root', type=Path)
args = parser.parse_args()
for path in sorted(args.root.rglob('make-database.txt')):
    environment_names = []
    previous = ''
    for line in path.read_text(errors='replace').splitlines():
        if previous.startswith('# environment'):
            match = re.match(r'([^\s:=]+)\s*[:+?]?=', line)
            if match:
                environment_names.append(match.group(1))
        previous = line
    sensitive_names = [name for name in environment_names if re.search(
        r'TOKEN|SECRET|PASSWORD|CREDENTIAL|API_KEY|AUTH', name, re.I)]
    print(str(path))
    print('environment variable count:', len(environment_names))
    print('sensitive-looking variable names only:', ', '.join(sensitive_names) or '(none)')
