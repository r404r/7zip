#!/usr/bin/env python3
"""Capture real callback numbers and verify observer does not change CLI outcomes."""
import argparse
import base64
import copy
import json
import platform
from pathlib import Path
import shutil
import subprocess
import tempfile
from capture import HERE, REPO, sha, verify_fixtures


def split_events(raw):
    events, normal = [], []
    for line in raw.splitlines(keepends=True):
        if line.startswith(b'B01_NATIVE '):
            events.append(json.loads(line[len(b'B01_NATIVE '):]))
        else:
            normal.append(line)
    return events, b''.join(normal)


def compare(actual, expected):
    for field in ('platform', 'manifest_sha256', 'observations'):
        if actual[field] != expected[field]:
            raise ValueError('numeric drift: ' + field)


def capture(legacy, observer):
    manifest = json.loads((HERE / 'manifest.json').read_text())
    verify_fixtures(manifest, HERE / 'fixtures')
    report: dict = dict(schema_version=1, platform=platform.system(),
                  manifest_sha256=sha((HERE / 'manifest.json').read_bytes()),
                  commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO).decode().strip(),
                  legacy_sha256=sha(legacy.read_bytes()), observer_sha256=sha(observer.read_bytes()),
                  commands={}, observations={})
    with tempfile.TemporaryDirectory(prefix='b01-numeric-') as tmp:
        root = Path(tmp)
        shutil.copytree(HERE / 'fixtures', root / 'fixtures')
        for fixture in manifest['fixtures']:
            for verb in ('t', 'x'):
                key = fixture['id'] + '/' + verb
                args = [verb, str(root / 'fixtures' / fixture['id']), '-y', '-bd', '-sccUTF-8', '-o' + str(root / 'out')]
                results = []
                for exe in (legacy, observer):
                    shutil.rmtree(root / 'out', ignore_errors=True)
                    argv = [str(exe), *args]
                    p = subprocess.run(argv, cwd=root, input=b'', capture_output=True, timeout=120)
                    files = {f.relative_to(root / 'out').as_posix(): sha(f.read_bytes())
                             for f in sorted((root / 'out').rglob('*')) if f.is_file()}
                    events, stderr = split_events(p.stderr)
                    # Raw stdout/stderr are retained even when stable comparison ignores banners.
                    raw = dict(argv=argv, exit=p.returncode, stdout_base64=base64.b64encode(p.stdout).decode(),
                               stderr_base64=base64.b64encode(p.stderr).decode())
                    results.append((raw, events, stderr, files))
                a, b = results
                if a[0]['exit'] != b[0]['exit'] or a[2:] != b[2:]:
                    raise ValueError('observer changed exit/stderr/files: ' + key)
                # Only ignore executable's identifying banner path and volatile statistics.
                from capture import properties, diagnostics
                stable_out = lambda r: (properties(base64.b64decode(r[0]['stdout_base64']).decode()),
                                        diagnostics(base64.b64decode(r[0]['stdout_base64']).decode()))
                if stable_out(a) != stable_out(b):
                    raise ValueError('observer changed stdout properties: ' + key)
                if not b[1] or b[1][0]['event'] != 'open_result':
                    raise ValueError('native open observation missing: ' + key)
                report['commands'][key] = dict(legacy=a[0], observer=b[0])
                report['observations'][key] = dict(events=b[1], exit=b[0]['exit'], files=b[3])
    return report


def negative(report):
    compare(report, copy.deepcopy(report))
    for field in ('hresult_bits', 'ErrorFlags_Defined', 'NOperationResult'):
        changed = copy.deepcopy(report)
        event = next(e for o in changed['observations'].values() for e in o['events'] if field in e)
        event[field] ^= 1
        try:
            compare(changed, report)
        except ValueError:
            continue
        raise AssertionError('numeric negative control accepted: ' + field)
    print('PASS: HRESULT/definedness/item-result negative controls')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('legacy', type=Path)
    p.add_argument('observer', type=Path)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--expect', type=Path)
    args = p.parse_args()
    dest = args.report.resolve()
    if dest.is_relative_to(HERE) or (args.expect and dest == args.expect.resolve()):
        raise ValueError('refusing to overwrite corpus/expectation')
    report = capture(args.legacy.resolve(), args.observer.resolve())
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2) + '\n')
    if args.expect:
        compare(report, json.loads(args.expect.read_text()))
    negative(report)
    print('PASS:', len(report['observations']), 'native callback captures with unchanged CLI exit/stderr/files')
