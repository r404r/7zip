#!/usr/bin/env python3
"""Audit actual Q1 compile logs and assemble committed input/capability evidence."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shlex

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRODUCTS = {'Alone2': ROOT / 'CPP/7zip/Bundles/Alone2',
            'Format7zF': ROOT / 'CPP/7zip/Bundles/Format7zF',
            'Console': ROOT / 'CPP/7zip/UI/Console'}
parser = argparse.ArgumentParser()
parser.add_argument('evidence', type=Path)
args = parser.parse_args()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    relative = path.relative_to(ROOT).as_posix()
    header = '\n'.join(path.read_text(errors='replace').splitlines()[:35])
    if relative.startswith('CPP/7zip/Compress/Rar'):
        license_id = 'LGPL-2.1-or-later AND LicenseRef-unRAR-restriction'
    elif relative in ('CPP/7zip/Compress/LzfseDecoder.cpp', 'C/ZstdDec.c'):
        license_id = 'BSD-3-Clause'
    elif relative == 'C/Xxh64.c':
        license_id = 'BSD-2-Clause'
    elif re.search(r'public domain', header, re.I):
        license_id = 'LicenseRef-Public-Domain'
    else:
        license_id = 'LGPL-2.1-or-later'
    return {'path': relative, 'sha256': sha(path), 'license': license_id,
            'basis': 'DOC/License.txt:8-30 and selected source header'}


def registry(path):
    section = None
    result = {'formats': [], 'codecs': [], 'hashers': []}
    for raw in path.read_text().splitlines():
        if raw in ('Formats:', 'Codecs:', 'Hashers:'):
            section = raw[:-1].lower()
            continue
        if section is None or not raw.strip():
            continue
        tokens = raw.split()
        if section == 'formats':
            if tokens[0].isdigit():
                tokens.pop(0)  # explicit legacy product library index, not format ID
            flags = tokens.pop(0)
            time_flags = None
            if re.fullmatch(r'[wudn.]{4}\d+', tokens[0]):
                time_flags = tokens.pop(0)
            name = tokens.pop(0)
            result[section].append({'name': name, 'flags_text': flags,
                                    'time_flags_text': time_flags, 'raw': raw})
        elif section == 'codecs':
            result[section].append({'name': tokens[-1], 'method_id': int(tokens[-2], 16),
                                    'flags_text': tokens[-3], 'raw': raw})
        else:
            result[section].append({'name': tokens[-1], 'method_id': int(tokens[-2], 16),
                                    'digest_size': int(tokens[-3]), 'raw': raw})
    if not all(result.values()):
        raise ValueError('Incomplete registry ' + str(path))
    return result


builds = []
licenses = {}
for observation in sorted(args.evidence.glob('*/engine-observation.json')):
    folder = observation.parent
    native = json.loads(observation.read_text())
    system = native['system']
    selected_products = {}
    for product, cwd in PRODUCTS.items():
        logfile = folder / ('build.log' if product == 'Alone2' else product + '-build.log')
        units = set()
        fragments = {cwd / ('makefile' if system == 'Windows' else 'makefile.gcc')}
        for line in logfile.read_text(errors='replace').splitlines():
            if line.startswith('Included: '):
                fragments.add((cwd / line.removeprefix('Included: ').replace('\\', '/')).resolve())
            try:
                tokens = shlex.split(line, posix=system != 'Windows')
            except ValueError:
                # A non-command diagnostic may contain an unmatched quote;
                # fail rather than accidentally omit a compilation command.
                if re.match(r'\s*(?:cl|gcc|g\+\+|clang|clang\+\+|ml64|rc)\s', line):
                    raise
                continue
            for token in tokens:
                token = token.strip('"').replace('\\', '/')
                if token.endswith(('.c', '.cpp', '.asm', '.S', '.rc')):
                    source = (cwd / token).resolve()
                    if source.is_file() and source.is_relative_to(ROOT):
                        units.add(source)
        if system != 'Windows':
            makefile = folder / ('selected-make-inputs.txt' if product == 'Alone2' else product + '-make-inputs.txt')
            for line in makefile.read_text().splitlines():
                if line.startswith('Q1_MAKEFILE_LIST='):
                    for name in line.split('=', 1)[1].split():
                        if name.endswith('/native-inputs.mak'):
                            continue  # observation-only target, not retained engine input
                        fragments.add((cwd / name).resolve())
        if not units or not all(path.is_file() and path.is_relative_to(ROOT) for path in fragments):
            raise ValueError('Incomplete selected input audit: ' + product + '/' + system)
        selected = [record(path) for path in sorted(units)]
        make_inputs = [record(path) for path in sorted(fragments)]
        for item in selected + make_inputs:
            old = licenses.setdefault(item['path'], item)
            if old != item:
                raise ValueError('Input identity mismatch ' + item['path'])
        selected_products[product] = {'units_and_resources': selected, 'make_inputs': make_inputs,
                                      'build_log_sha256': sha(logfile)}
    standalone = registry(folder / 'capabilities.txt')
    loaded = registry(folder / 'native-product-capabilities.txt')
    with (folder / 'format-registry.tsv').open(newline='') as stream:
        numeric = list(csv.DictReader(stream, delimiter='\t'))
    for item in numeric:
        for key in ('index', 'registration_id', 'flags', 'time_flags', 'writer'):
            item[key] = int(item[key])
    numerical_names = {r['name'] for r in numeric}
    cli_names = {r['name'] for r in loaded['formats']}
    coordinator = [r for r in loaded['formats'] if r['name'] == 'Hash']
    hash_source = 'CPP/7zip/UI/Common/HashCalc.cpp'
    if len(coordinator) != 1 or 'Hash' in numerical_names or not all(
            hash_source in {r['path'] for r in selected_products[p]['units_and_resources']}
            for p in ('Alone2', 'Console')):
        raise ValueError('Missing/changed separately retained Hash coordinator evidence')
    if numerical_names | {'Hash'} != cli_names:
        raise ValueError('Numerical observer/loaded CLI format registry mismatch: '
                         + repr({'system': system, 'observer_only': sorted(numerical_names - cli_names),
                                 'cli_only': sorted(cli_names - numerical_names)}))
    if {r['name'] for r in standalone['formats']} != {r['name'] for r in loaded['formats']}:
        raise ValueError('Standalone/loaded registry lost formats')
    time_differences = []
    standalone_by_name = {r['name']: r for r in standalone['formats']}
    for row in loaded['formats']:
        other = standalone_by_name[row['name']]
        if row['flags_text'] != other['flags_text'] or row['time_flags_text'] != other['time_flags_text']:
            time_differences.append({'name': row['name'], 'standalone': other, 'loaded': row})
    builds.append({'system': system, 'machine': native['machine'],
                   'oracle_commit': native['oracle_commit'], 'products': selected_products,
                   'standalone': standalone, 'loaded': loaded, 'format_registry': numeric,
                   'coordinator_formats': [{'name': 'Hash', 'registration_id': None,
                       'source': hash_source, 'source_symbol': 'Codecs_AddHashArcHandler',
                       'observed': coordinator[0]}],
                   'standalone_loaded_differences': time_differences,
                   'binary_sha256': native['binary_sha256'],
                   'evidence': {path.relative_to(folder).as_posix(): sha(path)
                                for path in sorted(folder.rglob('*')) if path.is_file()}})
if {b['system'] for b in builds} != {'Linux', 'Windows', 'Darwin'} or len(builds) != 3:
    raise ValueError('Expected three native builds')
result = {'schema_version': 1, 'status': 'retained-native-reference',
          'facade_commit': None, 'qualified_application_operations': [], 'builds': builds}
(HERE / 'engine-build.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'license-inventory.json').write_text(json.dumps({
    'schema_version': 1, 'status': 'engineering-inventory-not-distribution-approval',
    'inputs': sorted(licenses.values(), key=lambda item: item['path']),
    'notices': [{'path': 'DOC/' + name, 'sha256': sha(ROOT / 'DOC' / name)}
                for name in ('License.txt', 'copying.txt', 'unRarLicense.txt')]
}, indent=2) + '\n')
for build in builds:
    print(build['system'], {name: len(p['units_and_resources']) for name, p in build['products'].items()},
          'formats', len(build['format_registry']), 'product differences', len(build['standalone_loaded_differences']))
print('Audited unique selected inputs:', len(licenses))
