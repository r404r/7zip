#!/usr/bin/env python3
"""Render measured coverage without implying full handler qualification."""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def inventory(report):
    manifest = json.loads((HERE / 'manifest.json').read_text())
    rows = []
    for line in report['capabilities'].split('\nCodecs:', 1)[0].splitlines():
        if not line.strip():
            continue
        # Native Alone2 i rows begin with a non-whitespace flags token.
        name = line.split()[1]
        fixtures = [f['id'] for f in manifest['fixtures'] if f['format'].lower() == name.lower()]
        rows.append(dict(format=name, registration=line, status='covered' if fixtures else 'unqualified',
                         scope='Only listed fixtures/operations; not complete format/method qualification', fixtures=fixtures,
                         production_release=False))
    return dict(schema_version=1, scope='Full native Alone2 registration inventory; CLI only',
                formats=rows, unsupported=[dict(case='ZIP method 65535', evidence='unsupported.zip/test',
                                               scope='This measured method value only; not all unknown methods')],
                unqualified_required=['All other methods/format variants', 'External 7z/RAR/CAB/ISO/WIM fixtures',
                                      'RAR multivolume', 'Automatic arbitrary nested handler chains',
                                      'Numeric HRESULT/NOperationResult/CArcErrorInfo at FFI boundary',
                                      'Windows GUI 7z.dll product capability comparison'],
                policy='No full B01 closure or affected production release while required cases are unqualified')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('report', type=Path)
    parser.add_argument('--inventory', type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding='utf-8'))
    if args.inventory:
        args.inventory.write_text(json.dumps(inventory(report), indent=2) + '\n', encoding='utf-8')
    print(report['platform'])
    for key, value in report['observations'].items():
        print(key, 'exit=' + str(value['exit']), value['diagnostics']['labels'], value.get('files', ''))
    print(report['capabilities'])


if __name__ == '__main__':
    main()
