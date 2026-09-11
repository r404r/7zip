"""Explicit opt-in safety controls; synthetic bytes are not corpus evidence."""
import io
import unittest

try:
    import quarantine
except ModuleNotFoundError:
    quarantine = None


class ResponseControls(unittest.TestCase):
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
