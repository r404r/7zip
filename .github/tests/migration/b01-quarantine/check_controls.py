"""Explicit opt-in safety controls; synthetic bytes are not corpus evidence."""
import io
import unittest

import quarantine


class ResponseControls(unittest.TestCase):
    def test_duplicate_guard_headers_rejected(self):
        from email.message import Message
        for key, value in (('Content-Length', '8'), ('Content-Type', 'text/html')):
            headers = Message()
            headers['Content-Length'] = '8'
            headers['Content-Type'] = 'application/octet-stream'
            headers[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                quarantine.check_headers(200, headers, 8)

    def test_exact_missing_mime_exception(self):
        base = 'https://sources.debian.org/data/main/p/python-rarfile/4.5-1/test/files/'
        for name in ('rar3-old.r00', 'rar3-old.r01'):
            quarantine.check_headers(200, {'Content-Length': '8'}, 8, base + name)
            for status, headers in ((302, {'Content-Length': '8'}),
                                    (200, {'Content-Length': '9'}),
                                    (200, {'Content-Length': '8', 'Content-Encoding': 'gzip'}),
                                    (200, {'Content-Length': '8', 'Transfer-Encoding': 'chunked'}),
                                    (200, {'Content-Length': '8', 'Location': base + name})):
                with self.subTest(name=name, headers=headers), self.assertRaises(ValueError):
                    quarantine.check_headers(status, headers, 8, base + name)
        for url in ('', base + 'rar3-old.rar', base + 'rar5-solid.rar',
                    base.replace('4.5-1', '4.4-1') + 'rar3-old.r00',
                    base + 'rar3-old.r00?x=1', base + 'other.r00'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                quarantine.check_headers(200, {'Content-Length': '8'}, 8, url)
        for mime in ('', 'text/html', 'text/plain'):
            with self.subTest(mime=mime), self.assertRaises(ValueError):
                quarantine.check_headers(200, {'Content-Length': '8', 'Content-Type': mime},
                                         8, base + 'rar3-old.r00')

    def test_header_and_stream_bounds(self):
        self.assertTrue(hasattr(quarantine, 'check_headers'), 'header guard missing')
        headers = {'Content-Length': '8', 'Content-Type': 'application/octet-stream'}
        quarantine.check_headers(200, headers, 8)
        for status, changes in [(302, {}), (404, {}), (200, {'Content-Length': '9'}),
                                (200, {'Content-Length': '7'}),
                                (200, {'Content-Length': None}),
                                (200, {'Transfer-Encoding': 'chunked'}),
                                (200, {'Content-Encoding': 'gzip'}),
                                (200, {'Content-Type': 'text/html'})]:
            with self.subTest(status=status, changes=changes):
                with self.assertRaises(ValueError):
                    quarantine.check_headers(status, {**headers, **changes}, 8)
        with self.assertRaises(ValueError):
            quarantine.read_bounded(io.BytesIO(b'short'), 8)
        data = io.BytesIO(b'harmless-excess')
        self.assertEqual(quarantine.read_bounded(data, 8), b'harmless')
        self.assertEqual(data.tell(), 8)  # no over-cap probe; length guard required

    def test_exact_response(self):
        self.assertIsNotNone(quarantine, 'bounded acquisition implementation missing')
        data = io.BytesIO(b'harmless')
        self.assertEqual(quarantine.read_bounded(data, 8), b'harmless')


if __name__ == '__main__':
    unittest.main(verbosity=2)
