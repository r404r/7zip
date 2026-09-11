#!/usr/bin/env python3
"""Print bounded summaries from actual observations, without rewriting reports."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('report', type=Path)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    r = json.loads(args.report.read_text())
    print('bytes:', args.report.stat().st_size)
    print('platform:', r['observations']['platform'], r['observations']['machine'])
    print('head:', r['provenance']['head'])
    print('run_id:', r['provenance']['run_id'])
    print('filesystem:', json.dumps(r['observations']['filesystem'], ensure_ascii=True))
    for name, case in r['observations']['cases'].items():
        if args.case and name not in args.case:
            continue
        print(name, 'sha256:', case['fixture_sha256'])
        phases = case['handler']['phases']
        for phase in phases:
            print(' ', phase['phase'], phase['set_hr'], [item['wchar_units'] for item in phase['items']],
                  'reopened:', phase.get('reopened'), 'reopen_hr:', phase.get('reopen_hr'))
        print(' cli exits:', {mode: (v['listing']['exit'], v.get('extraction', {}).get('exit')) for mode, v in case['cli'].items()})


if __name__ == '__main__':
    main()
