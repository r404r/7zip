#!/usr/bin/env python3
"""Review-gated small native probes only; never full capture or ZIP64."""
import argparse
import hashlib
import json
import locale
import os
from pathlib import Path
import platform
import re
import subprocess
import tempfile
import time
from typing import Any

from full_volume import observe
from run import HERE, STAMP, command, digest, fs_info, inventory, sparse


def check_gate(env, system):
    assert system in ('Windows', 'Darwin'), 'Windows/macOS preflight only'
    assert env.get('GITHUB_EVENT_NAME') == 'push', 'Controlled task-branch push required'
    assert env.get('GITHUB_REPOSITORY') == 'r404r/7zip', 'Original repository required'
    assert env.get('GITHUB_REF') == 'refs/heads/wt/t_bf92ce13', 'Original task branch required'
    assert env.get('GITHUB_RUN_NUMBER') == '4', 'Only the fixed first preflight slot is allowed'
    assert env.get('B03_PUSH_BEFORE') == '500eecdb435d03580ca8f640f72becfb617bff02', 'Unexpected push predecessor'
    assert env.get('GITHUB_RUN_ATTEMPT') == '1', 'Native preflight rerun forbidden'
    sha = env.get('B03_REVIEWED_SHA', '')
    assert re.fullmatch('[0-9a-f]{40}', sha), 'Exact reviewed commit required'
    assert sha == env.get('GITHUB_SHA'), 'Reviewed commit differs from checkout'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('work', type=Path)
    args = parser.parse_args()
    check_gate(os.environ, platform.system())
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
    assert head == os.environ['B03_REVIEWED_SHA']
    work = args.work.resolve()
    report = work / 'preflight.json'
    assert not report.exists(), 'Preflight report must be new'
    build = json.loads((work / 'build.json').read_text())
    assert build['head'] == head
    plain = Path(build['executables']['plain']['path'])
    assert digest(plain) == build['executables']['plain']['sha256']
    sandbox = Path(tempfile.mkdtemp(prefix='b03-preflight-', dir=work))
    result: dict[str, Any] = dict(kind='B03-directed-preflight-not-qualification', completed=False,
                  head=head, build_sha256=digest(work / 'build.json'),
                  platform=platform.platform(), locale=locale.setlocale(locale.LC_ALL, None),
                  timezone=list(time.tzname), sandbox=str(sandbox),
                  run_id=os.environ.get('GITHUB_RUN_ID'), run_attempt=os.environ.get('GITHUB_RUN_ATTEMPT'),
                  run_number=os.environ.get('GITHUB_RUN_NUMBER'), push_before=os.environ.get('B03_PUSH_BEFORE'),
                  harness_sha256={p.name: digest(p) for p in HERE.glob('*.py')})
    try:
        result['filesystem'] = fs_info(sandbox)
        # This path has no large-input call. A failed small allocation guard stops.
        small = sandbox / 'small-sparse.bin'
        result['sparse'] = dict(source={})
        sparse(small, 16 << 20, observation=result['sparse']['source'])
        archive = sandbox / 'small.7z'
        result['sparse']['create'] = command([plain, 'a', '-t7z', '-mx=1', '-mmt=off', archive, small], sandbox)
        assert result['sparse']['create']['exit'] == 0
        assert archive.stat().st_size < 1 << 20
        out = sandbox / 'sparse-out'
        out.mkdir()
        result['sparse']['extract'] = command([plain, 'x', '-aos', '-y', archive, f'-o{out}'], sandbox)
        assert result['sparse']['extract']['exit'] == 0
        result['sparse']['outputs'] = inventory(out)
        result['sparse']['source_sha256'] = digest(small)
        assert digest(out / small.name) == result['sparse']['source_sha256']
        inputs = sandbox / 'fault-input'
        inputs.mkdir()
        source = inputs / 'payload.bin'
        source.write_bytes(b'original\n')
        os.utime(source, ns=(STAMP, STAMP))
        seed = sandbox / 'update-write-full'
        seed.mkdir()
        result['seed'] = command([plain, 'a', '-tzip', '-mx=0', '-mtc=off', '-mta=off', seed / 'out.zip', source], sandbox)
        assert result['seed']['exit'] == 0
        source.write_bytes(b''.join(hashlib.sha256(str(i).encode('ascii')).digest() for i in range(2048)))
        os.utime(source, ns=(STAMP + 10000000000, STAMP + 10000000000))
        result['input_sha256'] = digest(source)
        result['kernel_full'] = {}
        observe(plain, sandbox, result['kernel_full'], command, fs_info, digest)
        result['completed'] = True
    finally:
        # Keep partial observations and detached images. Never recurse-delete mounts.
        report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
