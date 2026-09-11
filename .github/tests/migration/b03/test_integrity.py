#!/usr/bin/env python3
"""Regression checks against real frozen candidate bytes; mutate only temp copies."""
import base64
import contextlib
import gzip
import io
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest

from freeze import verify
from validate import validate

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
EVIDENCE = HERE / 'evidence/local-linux'


class EvidenceTests(unittest.TestCase):
    def test_frozen_candidate_integrity(self):
        with contextlib.redirect_stdout(io.StringIO()):
            verify(EVIDENCE)

    def test_corrupt_stored_archive_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix='b03-negative-', dir=HERE / 'work') as tmp:
            dest = Path(tmp) / 'copy'
            shutil.copytree(EVIDENCE, dest)
            manifest = json.loads((dest / 'manifest.json').read_text())
            name = next(n for n in manifest['files'] if n.endswith('.zip.gz'))
            data = bytearray((dest / name).read_bytes())
            data[len(data) // 2] ^= 1
            (dest / name).write_bytes(data)
            with self.assertRaises(AssertionError):
                verify(dest)

    def test_nonzero_exit_is_not_enospc_evidence(self):
        report = json.loads(gzip.decompress((EVIDENCE / 'capture.json.gz').read_bytes()))
        report['kernel_full']['stderr_b64'] = base64.b64encode(b'E_NOTIMPL : Not implemented').decode()
        with self.assertRaisesRegex(AssertionError, 'kernel ENOSPC'):
            validate(report)

    def test_document_relative_links_exist(self):
        doc = ROOT / 'docs/ai-migration/qualification/b03.md'
        for link in re.findall(r'\]\(([^)]+)\)', doc.read_text()):
            self.assertTrue((doc.parent / link).exists(), link)


if __name__ == '__main__':
    (HERE / 'work').mkdir(exist_ok=True)
    unittest.main()
