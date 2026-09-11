"""Offline response-page regressions; synthetic bodies only, never archive parsing."""
import copy
from email.message import Message
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import acquire
import resume


PAGES = (
    b'<html>proxy error</html>',
    b'\xef\xbb\xbf<html>proxy error</html>',
    b'<!-- proxy error -->\n<html>error</html>',
    b'\xef\xbb\xbf \n<!-- first --><!-- second -->\n<!DOCTYPE HTML><html>error</html>',
    b'<?xml version="1.0"?><html xmlns="http://www.w3.org/1999/xhtml">error</html>',
    b'\xef\xbb\xbf\n<?xml version="1.0"?>\n<!-- proxy --><html>error</html>',
)


class ErrorPageControls(unittest.TestCase):
    def response(self, body, mime=None):
        headers = Message()
        headers['Content-Length'] = str(len(body))
        if mime is not None:
            headers['Content-Type'] = mime
        stream = io.BytesIO(body)
        test = self

        class Response:
            status = 200

            def __init__(self):
                self.headers = headers

            def getheader(self, key):
                return headers.get(key)

            def read(self, count):
                test.assertGreater(count, 0)
                test.assertLessEqual(count, len(body) - stream.tell())
                return stream.read(count)

        response = Response()
        return response, stream

    def test_real_fetch_rejects_wrapped_pages_and_accepts_opaque_binary(self):
        baseline, _ = resume.load_evidence()
        original = baseline['candidates']['DRF-OLD']['files'][2]
        for prefix in PAGES + (b'\x00\xffharmless binary',):
            with self.subTest(prefix=prefix):
                item = copy.deepcopy(original)
                body = prefix.ljust(item['declared_size'], b' ')
                response, stream = self.response(body)
                with patch('http.client.HTTPSConnection') as transport:
                    connection = transport.return_value
                    connection.getresponse.return_value = response
                    if prefix in PAGES:
                        with self.assertRaisesRegex(ValueError, 'unexpected .*body'):
                            resume.fetch_one(item)
                    else:
                        self.assertEqual(resume.fetch_one(item), body)
                    connection.request.assert_called_once()
                    connection.close.assert_called_once()
                self.assertEqual(stream.tell(), len(body))
                self.assertIsNone(item['response_headers']['Content-Type'])

    def test_real_fetch_resume_stops_preserves_evidence_and_never_retries(self):
        template, notice = resume.load_evidence()
        for prefix in PAGES:
            with self.subTest(prefix=prefix), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                root.chmod(0o700)
                baseline = copy.deepcopy(template)
                baseline['quarantine_root'] = str(root)
                for cid, family in baseline['candidates'].items():
                    directory = root / cid
                    directory.mkdir(mode=0o700)
                    (directory / 'NOTICE.txt').write_bytes(notice)
                    for item in family['files']:
                        item['local_opaque_path'] = str(directory / (Path(item['path']).name + '.opaque'))
                        item['local_notice_path'] = str(directory / 'NOTICE.txt')
                        if item['retrieval_outcome'] == 'acquired_quarantined':
                            data = b'\x00harmless synthetic original'.ljust(item['declared_size'], b' ')
                            item['sha256'] = hashlib.sha256(data).hexdigest()
                            Path(item['local_opaque_path']).write_bytes(data)
                            Path(item['local_opaque_path']).chmod(0o400)
                raw = json.dumps(baseline).encode()
                (root / 'manifest.json').write_bytes(raw)
                before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                first_pending = baseline['candidates']['DRF-OLD']['files'][1]
                body = prefix.ljust(first_pending['declared_size'], b' ')
                response, _ = self.response(body)
                with patch('http.client.HTTPSConnection') as transport, patch('sys.stderr', new_callable=io.StringIO) as errors:
                    connection = transport.return_value
                    connection.getresponse.return_value = response
                    self.assertEqual(resume.run_resume(baseline, root, notice), 1)
                    self.assertIn('unexpected', errors.getvalue())
                    connection.request.assert_called_once()
                    self.assertEqual(connection.request.call_args.args[:2],
                                     ('GET', '/data/main/p/python-rarfile/4.5-1/test/files/rar3-old.r00'))
                    connection.close.assert_called_once()
                    with self.assertRaisesRegex(ValueError, 'already attempted'):
                        resume.run_resume(baseline, root, notice)
                    connection.request.assert_called_once()
                after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                self.assertEqual(set(after), set(before) | {'resume.json'})
                for name, data in before.items():
                    self.assertEqual(after[name], data)
                saved = json.loads(after['resume.json'])
                stopped = saved['candidates']['DRF-OLD']['files'][1]
                self.assertEqual(stopped['retrieval_outcome'], 'failed_stopped')
                self.assertIsNone(stopped['actual_size'])
                self.assertIsNone(stopped['sha256'])
                self.assertIsNone(stopped['response_headers']['Content-Type'])
                self.assertEqual(stopped['http_status'], 200)
                self.assertEqual(stopped['final_url'], first_pending['original_url'])
                self.assertEqual(stopped['response_headers']['Content-Length'], str(len(body)))
                self.assertIn('unexpected', stopped['error'])
                self.assertEqual(len(resume.verify_local(saved, baseline, root, notice)), 6)

    def test_initial_acquisition_also_rejects_wrapped_pages(self):
        # Patch only local destinations and HTTPS transport, not the acquisition path.
        for prefix in PAGES:
            with self.subTest(prefix=prefix), tempfile.TemporaryDirectory() as tmp:
                here = Path(tmp) / 'bookkeeping'
                here.mkdir()
                root = Path(tmp) / 'quarantine'
                body = prefix.ljust(102400, b' ')
                response, _ = self.response(body, 'application/octet-stream')
                with (patch.object(acquire, 'ROOT', root), patch.object(acquire, 'HERE', here),
                      patch('sys.argv', ['acquire.py', '--acquire-approved-seven']),
                      patch('http.client.HTTPSConnection') as transport,
                      patch('sys.stderr', new_callable=io.StringIO)):
                    connection = transport.return_value
                    connection.getresponse.return_value = response
                    self.assertEqual(acquire.main(), 1)
                    connection.request.assert_called_once()
                    connection.close.assert_called_once()
                self.assertEqual(list(root.rglob('*.opaque')), [])
                saved = json.loads((root / 'manifest.json').read_text())
                first = saved['candidates']['DRF-OLD']['files'][0]
                self.assertEqual(first['retrieval_outcome'], 'failed_stopped')
                self.assertIn('unexpected', first['error'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
