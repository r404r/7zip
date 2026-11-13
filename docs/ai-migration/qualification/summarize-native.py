#!/usr/bin/env python3
"""Summarize downloaded Q1 observations without treating capture as qualification."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('evidence', type=Path)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
reports = []
capabilities = {}
for manifest in sorted(args.evidence.glob('*/engine-observation.json')):
    folder = manifest.parent
    data = json.loads(manifest.read_text())
    captures = {}
    for filename in ('compiler.txt', 'driver.txt', 'runtime.txt', 'characterization.log'):
        captures[filename] = (folder / filename).read_text()
    lines = (folder / 'capabilities.txt').read_text().splitlines()
    registry = lines[lines.index('Formats:'):]
    capabilities[data['system']] = registry
    reports.append({
        'system': data['system'], 'machine': data['machine'],
        'oracle_commit': data['oracle_commit'], 'binary_sha256': data['binary_sha256'],
        'selected_count': len(data['selected_translation_units']),
        'license_counts': dict(Counter(x['license'] for x in data['selected_translation_units'])),
        'selected_paths': [x['path'] for x in data['selected_translation_units']],
        'captures': captures,
        'evidence_digests': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted(folder.iterdir()) if p.is_file()},
    })
if len(reports) != 3 or set(capabilities) != {'Linux', 'Windows', 'Darwin'}:
    raise SystemExit('Expected exactly three native OS observations')
result = {'schema_version': 1, 'status': 'native-CLI-observations-only',
          'reports': reports, 'capabilities_identical_to_linux': {
              key: value == capabilities['Linux'] for key, value in capabilities.items()}}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(result, indent=2) + '\n')
for report in reports:
    print(report['system'], report['machine'], report['selected_count'], report['license_counts'])
    print(json.dumps(report['captures'], indent=2))
print(result['capabilities_identical_to_linux'])
