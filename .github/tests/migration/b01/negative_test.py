#!/usr/bin/env python3
"""Negative controls alter temporary copies only, never checked-in goldens."""
import argparse
import copy
import json
from pathlib import Path
import shutil
import tempfile
import capture


def rejects(fn, label):
    try:
        fn()
    except ValueError:
        print('PASS reject ' + label)
    else:
        raise AssertionError('accepted ' + label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    real = json.loads(args.report.read_text(encoding='utf-8'))
    for key, replacement in [('exit', 123), ('diagnostics', {}), ('files', {})]:
        broken = copy.deepcopy(real)
        broken['observations']['store.zip/extract'][key] = replacement
        rejects(lambda: capture.compare(broken, real), key + ' drift')
    broken = copy.deepcopy(real)
    broken['platform']['os'] = 'not-native'
    rejects(lambda: capture.compare(broken, real), 'platform drift')
    broken = copy.deepcopy(real)
    broken['capabilities'] = ''
    rejects(lambda: capture.compare(broken, real), 'registration loss')
    manifest = json.loads((capture.HERE / 'manifest.json').read_text())
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp) / 'fixtures'
        shutil.copytree(capture.HERE / 'fixtures', directory)
        capture.verify_fixtures(manifest, directory)
        target = directory / manifest['fixtures'][0]['files'][0]['path']
        target.write_bytes(target.read_bytes() + b'drift')
        rejects(lambda: capture.verify_fixtures(manifest, directory), 'immutable byte drift')
    capture.compare(real, real)
    print('PASS unmodified control')


if __name__ == '__main__':
    main()
