#!/usr/bin/env python3
"""Print a bounded human-readable index into real B03 raw reports."""
import argparse
import base64
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('report', type=Path)
a = p.parse_args()
r = json.loads(a.report.read_text())
print('Platform:', r['platform_detail'])
print('Filesystem:', r['filesystem'])
print('Capabilities:', r['capability_setup'])
for c in r['cases']:
    print('CASE', c['format'], c['zone'])
    for i in c['outputs']:
        print(' ', i['path'], 'mode', oct(i['mode']), 'mtime_ns', i['mtime_ns'], 'xattrs', i.get('xattrs'))
for c in r['probes']:
    print('PROPERTY', c['label'], 'exit', c['create']['exit'])
    print(base64.b64decode(c['create']['stderr_b64']).decode('utf-8', 'backslashreplace'))
for c in r['faults']:
    print('FAULT', c['operation'], c['mode'], 'exit', c['run']['exit'],
          'disposition', [(i['path'], i['size']) for i in c['disposition']],
          'original_unchanged', c.get('before_sha256') == c.get('after_sha256') if c['operation'] == 'update' else None)
print('LARGE', {k: v for k, v in r['large'].items() if k not in ('properties', 'seek', 'create')})
print('KERNEL_FULL', r['kernel_full'])
