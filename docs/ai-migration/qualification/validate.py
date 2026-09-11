#!/usr/bin/env python3
"""Validate Q1 schemas, selected input identities and qualification boundaries."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from jsonschema import Draft202012Validator, ValidationError

if not __debug__:
    raise RuntimeError('Run qualification validation without Python optimization')

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--evidence', type=Path)
args = parser.parse_args()
schema = json.loads((HERE / 'engine-build-schema.json').read_text())
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema)
manifest = json.loads((HERE / 'engine-build.json').read_text())
validator.validate(manifest)
assert manifest['status'] == 'retained-native-reference'
assert manifest['facade_commit'] is None
assert manifest['qualified_application_operations'] == []
assert {b['system'] for b in manifest['builds']} == {'Linux', 'Windows', 'Darwin'}
licenses = json.loads((HERE / 'license-inventory.json').read_text())
assert licenses['schema_version'] == 1
inputs = {row['path']: row for row in licenses['inputs']}
assert len(inputs) == len(licenses['inputs'])
for row in licenses['inputs'] + licenses['notices']:
    path = (ROOT / row['path']).resolve()
    assert path.is_relative_to(ROOT) and path.is_file(), row['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], row['path']
for build in manifest['builds']:
    for product in build['products'].values():
        for row in product['units_and_resources'] + product['make_inputs']:
            assert inputs[row['path']] == row
    numeric_names = {row['name'] for row in build['format_registry']}
    assert len(numeric_names) == len(build['format_registry'])
    assert {row['index'] for row in build['format_registry']} == set(range(len(numeric_names)))
    for key in ('standalone', 'loaded'):
        assert {row['name'] for row in build[key]['formats']} == numeric_names | {'Hash'}
        for row in build[key]['codecs'] + build[key]['hashers']:
            assert 0 <= row['method_id'] < 2 ** 64
        assert all('E' not in row['flags_text'] for row in build[key]['codecs']
                   if row['name'].startswith('Rar'))
    for row in build['format_registry']:
        assert 0 <= row['flags'] < 2 ** 32 and 0 <= row['time_flags'] < 2 ** 32
        if row['name'].startswith('Rar'):
            assert row['writer'] == 0
    print(build['system'], 'registered formats:', len(numeric_names),
          'CLI format rows:', len(build['standalone']['formats']),
          'codecs:', len(build['standalone']['codecs']), 'hashers:', len(build['standalone']['hashers']),
          'product metadata differences:', [row['name'] for row in build['standalone_loaded_differences']])
# Schema negative controls must fail, without changing any committed oracle.
negative = []
changed = copy.deepcopy(manifest)
changed['schema_version'] = 2
negative.append(changed)
changed = copy.deepcopy(manifest)
changed['qualified_application_operations'] = ['extract']
negative.append(changed)
changed = copy.deepcopy(manifest)
changed['builds'][0]['binary_sha256'] = 'not-a-digest'
negative.append(changed)
changed = copy.deepcopy(manifest)
changed['status'] = 'facade-qualified'
negative.append(changed)
for changed in negative:
    try:
        validator.validate(changed)
    except ValidationError:
        continue
    raise AssertionError('Schema accepted negative control')
# Verify relative Markdown links resolve; ignore headings and external URLs.
for doc in HERE.glob('*.md'):
    for link in re.findall(r'\]\(([^)]+)\)', doc.read_text()):
        if '://' in link or link.startswith('#'):
            continue
        assert (doc.parent / link.split('#', 1)[0]).exists(), (doc.name, link)
if args.evidence:
    folders = {}
    for report in args.evidence.glob('*/engine-observation.json'):
        system = json.loads(report.read_text())['system']
        assert system not in folders
        folders[system] = report.parent
    for build in manifest['builds']:
        folder = folders[build['system']]
        for name, expected in build['evidence'].items():
            assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == expected, name
        subprocess.run([sys.executable, str(HERE / 'check-pins.py'), str(folder)], check=True)
        observed = [(folder / 'layout' / (lang + '-layout.txt')).read_text()
                    for lang in ('c', 'cpp', 'rust')]
        assert len(set(observed)) == 1
        assert observed[0] == (HERE / 'abi-layout.txt').read_text()
    # Pin guard negative controls use isolated copies of captured text only.
    source = folders['Linux']
    with tempfile.TemporaryDirectory(prefix='q1-negative-', dir=HERE) as directory:
        target = Path(directory)
        for name in ('engine-observation.json', 'compiler.txt', 'cxx-compiler.txt',
                     'driver.txt', 'runtime-packages.txt', 'layout/rustc.txt', 'layout/c-layout.txt'):
            dest = target / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((source / name).read_bytes())
        (target / 'compiler.txt').write_text('intentional negative-control version drift\n')
        proc = subprocess.run([sys.executable, str(HERE / 'check-pins.py'), str(target)],
                              capture_output=True, text=True, check=False)
        assert proc.returncode != 0 and 'compiler' in proc.stderr
        (target / 'compiler.txt').write_bytes((source / 'compiler.txt').read_bytes())
        (target / 'layout/c-layout.txt').write_text('intentional negative-control layout drift\n')
        proc = subprocess.run([sys.executable, str(HERE / 'check-pins.py'), str(target)],
                              capture_output=True, text=True, check=False)
        assert proc.returncode != 0 and 'frozen ABI layout' in proc.stderr
    print('PASS: artifact digests, three native pin/layout comparisons and two pin negative controls')
print('Selected input license categories:', dict(Counter(row['license'] for row in inputs.values())))
print('PASS: schema, selected input/notice hashes, capability boundaries, links and four schema negative controls')
