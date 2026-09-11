#!/usr/bin/env python3
"""Check source-backed relations and report integrity, not synthesized goldens."""
import argparse
import copy
import json
from pathlib import Path
import struct

from fixtures import corpus
from run import negative_controls, sha


def validate(report):
    obs = report['observations']
    assert all(obs['native_roundtrip'][op]['exit'] == 0 for op in ('create', 'list', 'extract'))
    assert set(obs['cases']) == set(corpus()), 'incomplete corpus'
    for label, (_, data, _) in corpus().items():
        case = obs['cases'][label]
        assert case['fixture_sha256'] == sha(data), label
        handler = case['handler']
        assert json.loads(bytes.fromhex(case['handler_raw']['stdout_hex'])) == handler
        assert handler['open_hr'] == 0
        phases = {p['phase']: p for p in handler['phases']}
        for p in phases.values():
            assert p['set_hr'] == p['close_hr'] == p['reopen_hr'] == 0, (label, p['phase'])
            for snapshot in (p, p['reopened']):
                assert snapshot['count_hr'] == 0 and snapshot['items']
                assert [item['index'] for item in snapshot['items']] == list(range(len(snapshot['items'])))
                assert all(item['hr'] == 0 and item['vt'] == 8 for item in snapshot['items'])
        def names(phase):
            return phases[phase]['reopened']['items']
        assert names('unscoped_empty') == names('cp65001'), (label, 'unscoped empty must not reset')
        for phase in ('scoped_empty', 'filtered_empty', 'direct_empty'):
            assert names(phase) == names('fresh'), (label, phase, 'must reset')
        for cp in ('932', '936', '65001'):
            a, b = (case['cli'][prefix + cp] for prefix in ('scoped', 'unscoped'))
            assert a.get('tree') == b.get('tree'), (label, cp)
            assert a['listing']['exit'] == b['listing']['exit'] == 0
        assert case['cli']['invalid_cp_type']['listing']['exit'] != 0
        assert case['cli']['other_scope'].get('tree') == case['cli']['default'].get('tree')
        assert case['cli']['ordered_override'].get('tree') == case['cli']['scoped936'].get('tree')
        assert case['cli']['reverse_override'].get('tree') == case['cli']['scoped932'].get('tree')
    cases = obs['cases']
    for label in ('unicode-bad-crc', 'unicode-bad-version', 'unicode-invalid-utf8'):
        for actual, fallback in zip(cases[label]['handler']['phases'], cases['cp932-zip']['handler']['phases']):
            assert actual['items'] == fallback['items'], (label, 'invalid extra must fall back')
    for label in ('unicode-valid', 'efs-beats-extra'):
        phases = cases[label]['handler']['phases']
        assert all(p['items'] == phases[0]['items'] for p in phases), (label, 'cp must not override declared Unicode')
    assert cases['unicode-valid']['handler']['phases'][0]['items'] != cases['efs-beats-extra']['handler']['phases'][0]['items']
    if obs['platform'] == 'Windows':
        for fmt in ('zip', 'tar'):
            for cp, text in (('932', '日本語.txt'), ('936', '中文.txt')):
                case = obs['cases'][f'cp{cp}-{fmt}']
                phase = next(p for p in case['handler']['phases'] if p['phase'] == 'cp' + cp)
                expected = list(struct.unpack('<' + 'H' * (len(text.encode('utf-16-le')) // 2), text.encode('utf-16-le')))
                assert phase['reopened']['items'][0]['wchar_units'] == expected
                assert case['cli']['scoped' + cp]['tree'][0]['path'] == {'tag': 'windows-u16', 'hex_le': text.encode('utf-16-le').hex()}
        # This UTF-8 unflagged ZIP makes reset/non-reset observable on Windows.
        phases = {p['phase']: p for p in obs['cases']['utf-8-zip']['handler']['phases']}
        assert phases['cp936']['items'] != phases['cp65001']['items']
    return negative_controls(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    controls = validate(report)
    mutant = copy.deepcopy(report)
    mutant['observations']['cases'].pop('cp932-zip')
    try:
        validate(mutant)
    except AssertionError:
        controls += 1
    else:
        raise AssertionError('missing fixture accepted')
    print(f'Integrity/source relations PASS; {controls} negative controls rejected')


if __name__ == '__main__':
    main()
