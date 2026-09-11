#!/usr/bin/env python3
"""Fail closed if native observations do not match reviewed Q1 toolchain pins."""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('evidence', type=Path)
args = parser.parse_args()
pins = json.loads((HERE / 'toolchains.json').read_text())
evidence = args.evidence
report = json.loads((evidence / 'engine-observation.json').read_text())
system = report['system']
pin = pins['native'][system]
failures = []


def check(condition, label):
    if not condition:
        failures.append(label)


check((evidence / 'compiler.txt').read_text().splitlines()[0] == pin['compiler_first_line'], 'compiler')
check((evidence / 'driver.txt').read_text().strip().splitlines()[0] == pin['driver'], 'build driver')
if system == 'Linux':
    check((evidence / 'cxx-compiler.txt').read_text().splitlines()[0] ==
          pin['compiler_first_line'].replace('gcc ', 'g++ ', 1), 'C++ compiler')
    versions = dict(line.split('\t') for line in (evidence / 'runtime-packages.txt').read_text().splitlines())
    for key, value in pin['runtime_packages'].items():
        check(versions.get(key) == value, 'runtime package ' + key)
elif system == 'Windows':
    sdk = json.loads((evidence / 'sdk-runtime.json').read_text())
    for key in ('VCToolsVersion', 'WindowsSDKVersion', 'UCRTVersion'):
        check(sdk.get(key) == pin[key], key)
elif system == 'Darwin':
    check((evidence / 'cxx-compiler.txt').read_text().splitlines()[0] == pin['compiler_first_line'], 'C++ compiler')
    check((evidence / 'sdk-version.txt').read_text().strip() == pin['sdk'], 'macOS SDK')
    check((evidence / 'xcode-version.txt').read_text().splitlines()[0] == 'Xcode ' + pin['xcode'], 'Xcode')
    runtime = (evidence / 'runtime.txt').read_text()
    for name, value in pin['runtime_versions'].items():
        check(any(name in line and 'current version ' + value + ')' in line
                  for line in runtime.splitlines()), 'runtime ' + name)
else:
    failures.append('unsupported system')
check('release: ' + pins['rust']['toolchain'] + '\n' in
      (evidence / 'layout/rustc.txt').read_text(), 'Rust release')
check((evidence / 'layout/c-layout.txt').read_text() == (HERE / 'abi-layout.txt').read_text(), 'frozen ABI layout')
if failures:
    raise SystemExit('FAIL: pin/layout drift: ' + ', '.join(failures))
print('PASS: exact native/Rust pin identity and frozen ABI layout: ' + system)
