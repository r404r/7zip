#!/usr/bin/env python3
"""Build retained CLI and explicitly instrumented disposable test copy."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('work', type=Path)
    work = p.parse_args().work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    source = work / 'source'
    if source.exists():
        raise SystemExit('Fresh build directory required')
    names = subprocess.check_output(['git', 'ls-files', '-z', 'C', 'CPP', 'Asm'], cwd=ROOT).decode().split('\0')
    hashes = {}
    for name in filter(None, names):
        dst = source / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dst)
        hashes[name] = sha(dst)
        assert hashes[name] == sha(ROOT / name)
    report = dict(head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
                  engine_diff=subprocess.check_output(['git', 'diff', 'd9c3b65', '--', 'C', 'CPP', 'Asm'], cwd=ROOT).decode(),
                  source_sha256=hashes, platform=platform.platform(), machine=platform.machine(),
                  python=platform.python_version(), commands=[], executables={},
                  run_id=os.environ.get('GITHUB_RUN_ID'), run_attempt=os.environ.get('GITHUB_RUN_ATTEMPT'))
    assert not report['engine_diff'], 'Oracle engine changed'
    modified = {}
    for variant in ('plain', 'probe'):
        if variant == 'probe':
            main_cpp = source / 'CPP/7zip/UI/Console/Main.cpp'
            text = main_cpp.read_text()
            marker = 'int Main2(\n'
            assert text.count(marker) == 2
            text = text.replace(marker, '#include "B03Probe.inc"\n\n' + marker, 1)
            marker = ')\n{\n  #if defined(MY_CPU_SIZEOF_POINTER)'
            assert text.count(marker) == 1
            text = text.replace(marker, ')\n{\n  if (B03Mode()) return B03Probe();\n  #if defined(MY_CPU_SIZEOF_POINTER)', 1)
            main_cpp.write_text(text)
            shutil.copyfile(HERE / 'probe.inc', main_cpp.parent / 'B03Probe.inc')
            streams = source / 'CPP/7zip/Common/FileStreams.cpp'
            text = streams.read_text()
            marker = '#include "StdAfx.h"'
            assert text.count(marker) == 1
            text = text.replace(marker, marker + '\n#include "B03Fault.inc"')
            for method, direction in [('COutFileStream::Write(const void *data', 'write'), ('CInFileStream::Read(void *data', 'read')]:
                marker = f'Z7_COM7F_IMF({method}, UInt32 size, UInt32 *processedSize))\n{{'
                assert text.count(marker) == 1, marker
                text = text.replace(marker, marker + f'\n  HRESULT b03hr = B03Limit("{direction}", size);\n  if (b03hr != S_OK) {{ if (processedSize) *processedSize = 0; return b03hr; }}')
            streams.write_text(text)
            shutil.copyfile(HERE / 'fault.inc', streams.parent / 'B03Fault.inc')
            for f in (main_cpp, streams):
                modified[f.relative_to(source).as_posix()] = sha(f)
            report['instrumentation'] = dict(modified=modified, probe_sha256=sha(HERE / 'probe.inc'), fault_sha256=sha(HERE / 'fault.inc'))
        out = work / variant
        if os.name == 'nt':
            cmd = ['nmake', '/NOLOGO', 'PLATFORM=x64', f'O={out}']
            exe = out / '7zz.exe'
            compiler = ['cl']
        else:
            makefiles = ['../../cmpl_gcc.mak']
            if platform.system() == 'Darwin':
                makefiles = ['../../cmpl_mac_arm64.mak'] if platform.machine() == 'arm64' else ['../../var_mac_x64.mak', '../../warn_clang_mac.mak', 'makefile.gcc']
            cmd = ['make', '-j2']
            for name in makefiles:
                cmd += ['-f', name]
            cmd += [f'O={out}']
            exe = out / '7zz'
            compiler = ['clang' if platform.system() == 'Darwin' else 'gcc', '--version']
        cwd = source / 'CPP/7zip/Bundles/Alone2'
        report['commands'].append(dict(argv=cmd, cwd=str(cwd), compiler=compiler))
        with (work / f'{variant}-build.log').open('wb') as log:
            subprocess.run(compiler, stdout=log, stderr=subprocess.STDOUT, check=False)
            result = subprocess.run(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
        report['executables'][variant] = dict(path=str(exe), build_exit=result.returncode, sha256=sha(exe) if exe.exists() else None)
        (work / 'build.json').write_text(json.dumps(report, indent=2) + '\n')
        if result.returncode:
            raise SystemExit(f'{variant} build failed: {work / (variant + "-build.log")}')
    for name, digest in hashes.items():
        assert sha(source / name) == modified.get(name, digest), name
    print(json.dumps(report['executables'], indent=2))


if __name__ == '__main__':
    main()
