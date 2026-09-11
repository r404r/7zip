#!/usr/bin/env python3
"""Mutation controls on copies of real captures; never alter frozen evidence."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('evidence', type=Path, nargs='+')
args = parser.parse_args()
failures = []
count = 0
for source in args.evidence:
    report = json.loads((source / 'engine-observation.json').read_text())
    system = report['system']
    cases: list[tuple[str, str | None, str | None, str | None]] = [('control', None, None, None)]
    for field in ('system', 'machine'):
        changed = dict(report, **{field: 'unqualified-control'})
        cases.append((field, 'engine-observation.json', json.dumps(changed), field))
    rustc = (source / 'layout/rustc.txt').read_text()
    for field in ('host', 'release'):
        cases.append(('Rust ' + field, 'layout/rustc.txt',
                      re.sub(r'^' + field + r': .*$', field + ': unqualified-control', rustc, flags=re.M),
                      'Rust ' + field))
    for name, label in [('compiler.txt', 'compiler'), ('driver.txt', 'build driver'),
                        ('layout/c-layout.txt', 'frozen ABI layout'),
                        ('layout/cargo.txt', 'cargo'), ('layout/clippy.txt', 'clippy'),
                        ('layout/rustfmt.txt', 'rustfmt')]:
        cases.append((label, name, 'unqualified-control\n', label))
    if system != 'Windows':
        cases.append(('C++ compiler', 'cxx-compiler.txt', 'unqualified-control\n', 'C++ compiler'))
    if system == 'Linux':
        versions = (source / 'runtime-packages.txt').read_text()
        for key in ('libgcc-s1:amd64', 'libstdc++6:amd64', 'libc6:amd64', 'binutils', 'make'):
            changed = re.sub(r'^' + re.escape(key) + r'\t.*$', key + '\t0.invalid-control', versions, flags=re.M)
            if changed == versions:
                raise SystemExit('Missing runtime control input: ' + key)
            cases.append((key, 'runtime-packages.txt', changed, key))
    elif system == 'Windows':
        sdk = json.loads((source / 'sdk-runtime.json').read_text())
        for key in sdk:
            cases.append((key, 'sdk-runtime.json', json.dumps(dict(sdk, **{key: 'unqualified-control'})), key))
    elif system == 'Darwin':
        for name, label in [('sdk-version.txt', 'macOS SDK'), ('xcode-version.txt', 'Xcode'),
                            ('runtime.txt', 'runtime')]:
            cases.append((label, name, 'unqualified-control\n', label))
    with tempfile.TemporaryDirectory(prefix='q1-pin-controls-') as temporary:
        target = Path(temporary)
        for name, filename, content, label in cases:
            # Restore every input before each independent mutation.
            for path in source.glob('*.txt'):
                shutil.copy2(path, target / path.name)
            for filename_json in ('engine-observation.json', 'sdk-runtime.json'):
                if (source / filename_json).exists():
                    shutil.copy2(source / filename_json, target / filename_json)
            shutil.copytree(source / 'layout', target / 'layout', dirs_exist_ok=True)
            if filename:
                assert content is not None
                (target / filename).write_text(content)
            proc = subprocess.run([sys.executable, str(HERE / 'check-pins.py'), str(target)],
                                  capture_output=True, text=True, check=False)
            good = proc.returncode == 0 if label is None else proc.returncode != 0 and label in proc.stderr
            print(json.dumps({'system': system, 'case': name, 'passed': good,
                              'exit_code': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}))
            count += 1
            if not good:
                failures.append(system + '/' + name)
if failures:
    raise SystemExit('FAIL: pin regression controls: ' + ', '.join(failures))
print(f'PASS: {count} positive/negative pin controls')
