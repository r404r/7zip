#!/usr/bin/env python3
"""Validate measured relations, then compare stable semantics, never edit oracles."""
import argparse
import base64
import copy
import json
from pathlib import Path


def tree(items):
    # Native directory sizes/allocation, atime and ctime depend on run location/time.
    # Preserve them raw in the report; compare content, mtime and native modes.
    keys = ('path', 'native_name_hex', 'kind', 'mode', 'mtime_ns', 'attributes', 'sha256', 'ads_b03_sha256', 'xattrs', 'xattrs_error')
    result = []
    for i in items:
        projected = {k: v for k, v in i.items() if k in keys or (k == 'size' and i['kind'] == 'file')}
        if 'native_acl' in i:
            projected['native_acl'] = {k: v for k, v in i['native_acl'].items() if k != 'raw'}
        result.append(projected)
    return result


def properties(record):
    value = copy.deepcopy(record['observed'])
    for item in value.get('items', []):
        # kpidCTime=10 / kpidATime=11: creation/access times are measured, not pinned
        # on all native platforms. Preserve their VARTYPE/precision, omit only value.
        for prop in item['properties']:
            # Legacy schema-1 captures sampled undefined scalar reserved words.
            # Keep their raw bytes intact; only VT_FILETIME (64) defines precision
            # here (PropID.h). New samplers never read non-time reserved storage.
            if prop['vt'] != 64:
                prop.pop('reserved', None)
            elif prop['reserved'][0] == 0:
                prop['reserved'][1:] = [None, None]
            if prop['id'] in (10, 11):
                prop.pop('filetime', None)
    return value


def stable(r):
    full = r['kernel_full']
    if 'operations' in full:
        full = dict(layer=full['layer'], completed=full['completed'], operations=[
            dict(operation=c['operation'], filesystem=c['filesystem']['type'],
                 fill_error=c['fill_error'], exit=c['run']['exit'],
                 disposition=c['disposition'], before_sha256=c.get('before_sha256'),
                 after_sha256=c.get('after_sha256'), test_after=c.get('test_after', {}).get('exit'))
            for c in full['operations']])
    return dict(platform=r['platform'], filesystem=r['filesystem'].get('type'), inputs=tree(r['inputs']),
                fault_input_sha256=r['fault_input_sha256'],
                cases=[dict(format=c['format'], zone=c['zone'], create=c['create']['exit'],
                            props=properties(c['properties']), extract=c['extract']['exit'], outputs=tree(c['outputs'])) for c in r['cases']],
                probes=[dict(label=c['label'], create=c['create']['exit'],
                             props=properties(c['properties']) if 'properties' in c else None,
                             extract=c.get('extract', {}).get('exit'), outputs=tree(c.get('outputs', []))) for c in r['probes']],
                faults=[dict(operation=c['operation'], mode=c['mode'], exit=c['run']['exit'],
                             disposition=[{k: v for k, v in i.items() if k != 'mtime_ns'} for i in tree(c['disposition'])],
                             test_after=c.get('test_after', {}).get('exit')) for c in r['faults']],
                large={k: r['large'][k] for k in ('archive_size', 'archive_sha256', 'source_sha256', 'zip_central')},
                sparse_outputs=tree(r['sparse_roundtrip']['outputs']),
                seek=r['large']['seek']['observed'], large_properties=properties(r['large']['properties']),
                large_extract={k: r['large']['extract_stdout'][k] for k in ('exit', 'bytes', 'sha256')},
                kernel_full={k: v for k, v in full.items() if k not in ('stderr_b64', 'argv')})


def validate(r):
    assert r['completed'] is True
    if r['schema'] >= 2:
        assert r['filesystem'].get('type'), 'Native filesystem identity required'
        for source in (r['sparse_roundtrip']['source'], r['large']['source']):
            assert source.get('allocated_bytes', 1 << 20) < 1 << 20, 'Sparse allocation proof required'
            assert source['free_before'] > source['size'] + (512 << 20)
        if r['platform'] in ('Windows', 'Darwin'):
            groups = [r['inputs']] + [c['outputs'] for c in r['cases']] + [c.get('outputs', []) for c in r['probes']]
            for group in groups:
                for item in group:
                    assert item.get('native_acl') is not None, 'Native file/directory ACL evidence required'
            full = r['kernel_full']
            assert full.get('completed') is True, 'Native kernel-full-volume qualification required'
            assert [c['operation'] for c in full['operations']] == ['create', 'update']
            for c in full['operations']:
                assert 1 << 20 < c['capacity']['total'] <= 64 << 20
                assert c['control']['exit'] == c['control_test']['exit'] == c['cleanup']['exit'] == 0
                assert c['fill_error']['errno'] == 28 or c['fill_error']['winerror'] == 112
                assert c['run']['exit'] != 0
                message = base64.b64decode(c['run']['stderr_b64'])
                assert b'No space left on device' in message or b'There is not enough space on the disk' in message, 'Must observe kernel-full diagnostic'
    assert len(r['cases']) == 6 and len(r['probes']) == 5 and len(r['faults']) == 12
    sparse = r['sparse_roundtrip']
    assert sparse['create']['exit'] == sparse['extract']['exit'] == 0
    assert len(sparse['outputs']) == 1 and sparse['outputs'][0]['sha256'] == sparse['source_sha256']
    for c in r['cases']:
        assert c['create']['exit'] == c['extract']['exit'] == 0
        assert c['properties']['observed']['open_hr'] == 0
        assert c['list_plain']['stdout_b64'] == c['list_probe']['stdout_b64']
        assert c['list_plain']['stderr_b64'] == c['list_probe']['stderr_b64']
        wanted = {i['path']: i['sha256'] for i in r['inputs'] if i['kind'] == 'file'}
        got = {i['path']: i['sha256'] for i in c['outputs'] if i['kind'] == 'file'}
        assert all(got.get(k) == v for k, v in wanted.items()), (c['format'], c['zone'])
    for operation in ('create', 'update'):
        cases = {c['mode']: c for c in r['faults'] if c['operation'] == operation}
        base = cases['none']
        assert base['run']['exit'] == base['test_after']['exit'] == 0
        for mode in ('write-short', 'read-short'):
            c = cases[mode]
            assert c['run']['exit'] == c['test_after']['exit'] == 0
            assert c['after_sha256'] == base['after_sha256'], (operation, mode)
            assert b'B03_FAULT active=' in base64.b64decode(c['run']['stderr_b64'])
        for mode in ('write-full', 'read-error'):
            c = cases[mode]
            assert c['run']['exit'] != 0
            assert b'B03_FAULT triggered=' in base64.b64decode(c['run']['stderr_b64']), (operation, mode)
        assert cases['missing-input']['run']['exit'] != 0
    large = r['large']
    assert large['source']['size'] == large['zip_central']['file_size'] == (1 << 32) + 33
    assert large['zip_central']['extract_version'] >= 45
    assert bytes.fromhex(large['zip_central']['extra_hex'])[:2] == b'\x01\x00'
    assert large['extract_stdout']['sha256'] == large['source_sha256']
    assert large['extract_stdout']['bytes'] == large['source']['size']
    assert large['extract_stdout']['exit'] == 0
    ops = large['seek']['observed']['operations']
    assert ops[1]['seek_hr'] != 0 and not ops[1]['position_defined']
    assert ops[2]['seek_hr'] == 0 and ops[2]['position'] == 4294967313
    assert ops[3]['processed'] == ops[4]['processed'] == 0
    assert ops[5]['seek_hr'] != 0
    if r['platform'] == 'Linux':
        assert r['kernel_full']['exit'] != 0
        assert b'No space left on device' in base64.b64decode(r['kernel_full']['stderr_b64']), 'Must observe kernel ENOSPC, not an unrelated nonzero exit'


def compare(a, b):
    validate(a)
    validate(b)
    x, y = stable(a), stable(b)
    if x != y:
        changed = [k for k in x if x[k] != y[k]]
        raise AssertionError(f'Stable native observations differ: {changed}')


def negative_controls(r):
    mutations = [lambda x: x['inputs'][0].update(mtime_ns=0),
                 lambda x: x['faults'][0]['run'].update(exit=99),
                 lambda x: x['large']['zip_central'].update(file_size=42),
                 lambda x: x['cases'][0]['properties']['observed']['items'][0]['properties'][0].update(vt=999)]
    if r['schema'] >= 2:
        mutations += [lambda x: x['filesystem'].update(type=''),
                      lambda x: x['sparse_roundtrip']['source'].update(allocated_bytes=16 << 20)]
        if r['platform'] in ('Windows', 'Darwin'):
            mutations += [lambda x: x['cases'][0]['outputs'][0].pop('native_acl'),
                          lambda x: x['kernel_full']['operations'][0]['run'].update(stderr_b64=base64.b64encode(b'E_NOTIMPL').decode())]
    for mutation in mutations:
        altered = copy.deepcopy(r)
        mutation(altered)
        try:
            compare(r, altered)
        except AssertionError:
            continue
        raise AssertionError('Negative control was not rejected')
    print(f'PASS: {len(mutations)} independent report mutations rejected')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('report', type=Path)
    args = p.parse_args()
    report = json.loads(args.report.read_text())
    validate(report)
    negative_controls(report)
    print('PASS: completeness and measured relations')
