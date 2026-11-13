"""Offline synthetic controls. No network, archive bytes or golden data."""
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import quarantine


class ResumeControls(unittest.TestCase):
    def test_fetch_transport_guards_without_network(self):
        import resume
        from email.message import Message
        base = 'https://sources.debian.org/data/main/p/python-rarfile/4.5-1/test/files/'
        cases = [
            ('rar3-old.r00', None, 200, '8', b'harmless', True),
            ('rar3-old.r01', None, 200, '8', b'harmless', True),
            ('rar5-solid.rar', None, 200, '8', b'harmless', False),
            ('rar3-old.r00', 'text/html', 200, '8', b'harmless', False),
            ('rar3-old.r00', None, 302, '8', b'harmless', False),
            ('rar3-old.r00', None, 200, '9', b'harmless!', False),
            ('rar3-old.r00', None, 200, '8', b'short', False),
            ('rar3-old.r00', None, 200, '8', b'<html>xx', False),
        ]
        for name, mime, status, length, body, success in cases:
            with self.subTest(name=name, mime=mime, status=status, length=length, body=body):
                headers = Message()
                headers['Content-Length'] = length
                if mime is not None:
                    headers['Content-Type'] = mime
                stream = io.BytesIO(body)

                class Response:
                    def __init__(self, status, headers, assert_bounded):
                        self.status = status
                        self.headers = headers
                        self.assert_bounded = assert_bounded

                    def getheader(self, key):
                        return headers.get(key)

                    def read(self, count):
                        self.assert_bounded(count)
                        return stream.read(count)

                response = Response(status, headers, lambda n: self.assertLessEqual(n, 8 - stream.tell()))
                with patch('http.client.HTTPSConnection') as transport:
                    connection = transport.return_value
                    connection.getresponse.return_value = response
                    item = {'original_url': base + name, 'declared_size': 8}
                    if success:
                        self.assertEqual(resume.fetch_one(item), body)
                        self.assertIsNone(item['response_headers']['Content-Type'])
                    else:
                        with self.assertRaises(ValueError):
                            resume.fetch_one(item)
                    connection.close.assert_called_once()
                    self.assertEqual(connection.request.call_count, 1)
                    self.assertEqual(connection.request.call_args.args[:2], ('GET', '/data/main/p/python-rarfile/4.5-1/test/files/' + name))
                    context = transport.call_args.kwargs['context']
                    self.assertTrue(context.check_hostname)
                    self.assertEqual(context.verify_mode, resume.ssl.CERT_REQUIRED)
                    if status != 200 or length != '8' or mime == 'text/html' or name == 'rar5-solid.rar':
                        self.assertEqual(stream.tell(), 0)

    def test_resume_once_preserves_original_and_stops_on_failure(self):
        import importlib.util
        self.assertIsNotNone(importlib.util.find_spec('resume'), 'resume implementation missing')
        import resume
        template = json.loads((Path(__file__).parent / 'manifest.json').read_text())
        for fail_at in (None, 1):
            with self.subTest(fail_at=fail_at), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                root.chmod(0o700)
                baseline = copy.deepcopy(template)
                baseline['quarantine_root'] = str(root)
                notice = b'SYNTHETIC NOTICE - not rights evidence\n'
                for cid, family in baseline['candidates'].items():
                    directory = root / cid
                    directory.mkdir(mode=0o700)
                    (directory / 'NOTICE.txt').write_bytes(notice)
                    for item in family['files']:
                        item['local_opaque_path'] = str(directory / (Path(item['path']).name + '.opaque'))
                        item['local_notice_path'] = str(directory / 'NOTICE.txt')
                        item['notice_sha256'] = hashlib.sha256(notice).hexdigest()
                        item['declared_size'] = 8
                        if item['retrieval_outcome'] == 'acquired_quarantined':
                            item['actual_size'] = 8
                            item['sha256'] = hashlib.sha256(b'harmless').hexdigest()
                            Path(item['local_opaque_path']).write_bytes(b'harmless')
                            Path(item['local_opaque_path']).chmod(0o400)
                original = json.dumps(baseline).encode()
                (root / 'manifest.json').write_bytes(original)
                calls = []

                def fetch(item):
                    calls.append(item['original_url'])
                    if fail_at == len(calls):
                        raise ValueError('synthetic response conflict')
                    item.update(final_url=item['original_url'], http_status=200,
                                retrieved_at_utc='synthetic-not-a-real-retrieval',
                                response_headers={'Content-Length': '8',
                                                  'Content-Type': 'application/octet-stream'},
                                tls_validation='ssl.create_default_context; certificate and hostname verified')
                    return b'harmless'

                with patch('http.client.HTTPSConnection', side_effect=AssertionError('network forbidden')):
                    (root / 'extra').write_bytes(b'harmless')
                    with self.assertRaises(ValueError):
                        resume.run_resume(baseline, root, notice, fetch=fetch)
                    self.assertEqual(calls, [])
                    self.assertFalse((root / 'resume.json').exists())
                    (root / 'extra').unlink()
                    result = resume.run_resume(baseline, root, notice, fetch=fetch)
                    self.assertEqual(result, 0 if fail_at is None else 1)
                    expected = [f['original_url'] for c in baseline['candidates'].values()
                                for f in c['files'] if f['retrieval_outcome'] != 'acquired_quarantined']
                    self.assertEqual(calls, expected if fail_at is None else expected[:1])
                    self.assertEqual((root / 'manifest.json').read_bytes(), original)
                    self.assertEqual(Path(baseline['candidates']['DRF-OLD']['files'][0]['local_opaque_path']).read_bytes(), b'harmless')
                    saved = json.loads((root / 'resume.json').read_text())
                    self.assertEqual(saved['candidates']['DRF-OLD']['files'][0], baseline['candidates']['DRF-OLD']['files'][0])
                    quarantine.verify_local(saved, baseline, root, notice, require_complete=fail_at is None)
                    if fail_at is None:
                        with (patch.object(resume, 'ROOT', root),
                              patch.object(resume, 'BASELINE_SHA256', hashlib.sha256(original).hexdigest()),
                              patch.object(resume, 'load_evidence', return_value=(baseline, notice)),
                              patch('sys.argv', ['resume.py', '--verify-complete']),
                              patch('sys.stdout', new_callable=io.StringIO)):
                            self.assertEqual(resume.main(), 0)
                    before = list(calls)
                    with self.assertRaises(ValueError):
                        resume.run_resume(baseline, root, notice, fetch=fetch)
                    self.assertEqual(calls, before)

    def test_existing_bytes_verified_and_only_missing_planned(self):
        self.assertTrue(hasattr(quarantine, 'verify_local'), 'local verifier missing')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            root.chmod(0o700)
            family = root / 'DRF-OLD'
            family.mkdir(mode=0o700)
            notice = b'Harmless synthetic notice, not rights evidence\n'
            (family / 'NOTICE.txt').write_bytes(notice)
            data = b'harmless'
            opaque = family / 'first.opaque'
            opaque.write_bytes(data)
            opaque.chmod(0o400)
            first = {'path': 'first', 'original_url': 'https://example.invalid/first',
                     'final_url': 'https://example.invalid/first', 'declared_size': 8,
                     'actual_size': 8, 'sha256': hashlib.sha256(data).hexdigest(),
                     'local_opaque_path': str(opaque), 'local_notice_path': str(family / 'NOTICE.txt'),
                     'notice_sha256': hashlib.sha256(notice).hexdigest(),
                     'status': 'quarantine', 'import_approved': False, 'qualified': False,
                     'retrieval_outcome': 'acquired_quarantined'}
            second = {**first, 'path': 'second', 'original_url': 'https://example.invalid/second',
                      'final_url': None, 'actual_size': None, 'sha256': None,
                      'local_opaque_path': str(family / 'second.opaque'),
                      'retrieval_outcome': 'not_attempted'}
            manifest = {'schema_version': 1, 'status': 'quarantine_incomplete',
                        'import_approved': False, 'qualified': False,
                        'quarantine_root': str(root), 'accepted_fixtures': [],
                        'candidates': {'DRF-OLD': {'status': 'quarantine',
                            'import_approved': False, 'qualified': False, 'files': [first, second]}}}
            (root / 'manifest.json').write_text(json.dumps(manifest))
            baseline = copy.deepcopy(manifest)
            self.assertEqual(quarantine.verify_local(manifest, baseline, root, notice), [second])
            for key, value in [('actual_size', 9), ('sha256', '0' * 64),
                               ('original_url', 'https://else.invalid/first'),
                               ('final_url', 'https://else.invalid/first'),
                               ('status', 'accepted'), ('import_approved', True),
                               ('qualified', True), ('declared_size', 9),
                               ('local_opaque_path', str(root / 'escape'))]:
                changed = copy.deepcopy(manifest)
                changed['candidates']['DRF-OLD']['files'][0][key] = value
                with self.subTest(key=key), self.assertRaises(ValueError):
                    quarantine.verify_local(changed, baseline, root, notice)
            for key, value in [('status', 'accepted'), ('qualified', True),
                               ('accepted_fixtures', ['first'])]:
                with self.subTest(top=key), self.assertRaises(ValueError):
                    quarantine.verify_local({**manifest, key: value}, baseline, root, notice)
            for op in ('missing', 'extra', 'size', 'hash', 'symlink', 'mode', 'notice'):
                with self.subTest(disk=op):
                    if op == 'missing':
                        opaque.rename(family / 'hidden')
                    elif op == 'extra':
                        (family / 'extra').write_bytes(b'harmless')
                    elif op in ('size', 'hash'):
                        opaque.chmod(0o600)
                        opaque.write_bytes(b'wrong' if op == 'size' else b'changed!')
                        opaque.chmod(0o400)
                    elif op == 'symlink':
                        opaque.rename(family / 'hidden')
                        opaque.symlink_to(family / 'hidden')
                    elif op == 'mode':
                        opaque.chmod(0o500)
                    else:
                        (family / 'NOTICE.txt').write_bytes(b'changed notice')
                    with self.assertRaises(ValueError):
                        quarantine.verify_local(manifest, baseline, root, notice)
                    if op in ('missing', 'symlink'):
                        if op == 'symlink':
                            opaque.unlink()
                        (family / 'hidden').rename(opaque)
                    elif op == 'extra':
                        (family / 'extra').unlink()
                    elif op in ('size', 'hash', 'mode'):
                        opaque.chmod(0o600)
                        opaque.write_bytes(data)
                        opaque.chmod(0o400)
                    else:
                        (family / 'NOTICE.txt').write_bytes(notice)
            with self.assertRaises(ValueError):
                quarantine.verify_local(manifest, baseline, root, notice, require_complete=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
