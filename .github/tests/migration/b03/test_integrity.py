#!/usr/bin/env python3
"""Regression checks against real frozen candidate bytes; mutate only temp copies."""
import base64
import contextlib
import copy
import gzip
import io
import json
from pathlib import Path
import re
import shutil
import tempfile
import tarfile
import unittest

from freeze import verify
from validate import validate, compare
from run import sparse, allocated_bytes, fs_info
from full_volume import check_mount

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
EVIDENCE = HERE / 'evidence/local-linux'


class EvidenceTests(unittest.TestCase):
    def test_native_small_sparse_proof_records_allocation(self):
        with tempfile.TemporaryDirectory(dir=HERE / 'work') as tmp:
            root = Path(tmp)
            self.assertTrue(fs_info(root)['type'])
            path = root / 'small.bin'
            observed = sparse(path, 16 << 20)
            self.assertEqual(observed['allocated_bytes'], allocated_bytes(path))
            self.assertLess(observed['allocated_bytes'], 1 << 20)
            with path.open('rb') as stream:
                self.assertEqual(stream.read(9), b'B03-BEGIN')
                stream.seek(-7, 2)
                self.assertEqual(stream.read(), b'B03-END')

    def test_new_capture_cannot_omit_native_qualification(self):
        report = json.loads(gzip.decompress((EVIDENCE / 'capture.json.gz').read_bytes()))
        report['schema'] = 2
        with self.assertRaises(AssertionError):
            validate(report)

    def test_full_volume_refuses_host_directory(self):
        with tempfile.TemporaryDirectory(dir=HERE / 'work') as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(AssertionError, 'host-sized'):
                check_mount(root, root.parent, {}, {})

    def test_large_sparse_requires_small_proof(self):
        with tempfile.TemporaryDirectory(dir=HERE / 'work') as tmp:
            path = Path(tmp) / 'unqualified.bin'
            with self.assertRaisesRegex(AssertionError, 'small sparse proof'):
                sparse(path)
            self.assertFalse(path.exists())

    def test_windows_reserved_storage_is_not_a_typed_value(self):
        # Replay actual failed native observations, never rewrite their bytes.
        with tarfile.open(HERE / 'evidence/ci-attempts/34568709582.tar.gz') as archive:
            prefix = next(n.rsplit('/', 1)[0] for n in archive.getnames()
                          if 'windows-latest' in n and n.endswith('/capture.json'))
            first = archive.extractfile(prefix + '/capture.json')
            second = archive.extractfile(prefix + '/repeat.json')
            assert first is not None and second is not None
            capture, repeat = json.load(first), json.load(second)
        compare(capture, repeat)
        # All three FILETIME precision words remain semantically significant.
        for index in range(3):
            damaged = copy.deepcopy(capture)
            prop = next(p for p in damaged['cases'][0]['properties']['observed']['items'][0]['properties']
                        if p['vt'] == 64)
            prop['reserved'][index] ^= 1
            with self.assertRaises(AssertionError):
                compare(capture, damaged)

        damaged = copy.deepcopy(capture)
        damaged['cases'][0]['properties']['observed']['items'][0]['properties'][0]['hr'] = 1
        with self.assertRaises(AssertionError):
            compare(capture, damaged)

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
