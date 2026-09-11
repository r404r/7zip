#!/usr/bin/env python3
"""Build unchanged and test-entry-point CLIs; never edit the source checkout."""
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
    parser = argparse.ArgumentParser()
    parser.add_argument('work', type=Path)
    args = parser.parse_args()
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    source = work / 'source'
    if source.exists():
        raise SystemExit('Use a fresh work directory; source already exists')
    files = subprocess.check_output(['git', 'ls-files', '-z', 'C', 'CPP', 'Asm'], cwd=ROOT).decode().split('\0')
    hashes = {}
    for name in filter(None, files):
        dest = source / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
        hashes[name] = sha(dest)
        assert hashes[name] == sha(ROOT / name)
    provenance = {
        'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
        'engine_diff_from_reviewed_base': subprocess.check_output(['git', 'diff', 'd9c3b65', '--', 'C', 'CPP', 'Asm'], cwd=ROOT).decode(),
        'platform': platform.platform(), 'machine': platform.machine(),
        'python': platform.python_version(), 'source_sha256': hashes,
        'commands': [], 'executables': {},
        'run_id': os.environ.get('GITHUB_RUN_ID'), 'run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT'),
        'repository': os.environ.get('GITHUB_REPOSITORY'),
    }
    assert not provenance['engine_diff_from_reviewed_base'], 'Legacy oracle changed'
    bundle = source / 'CPP/7zip/Bundles/Alone2'
    for variant in ('plain', 'probe'):
        if variant == 'probe':
            main_cpp = source / 'CPP/7zip/UI/Console/Main.cpp'
            text = main_cpp.read_text()
            marker = 'int Main2(\n'
            assert text.count(marker) == 2
            text = text.replace(marker, '#include "B02Probe.inc"\n\n' + marker, 1)
            marker = ')\n{\n  #if defined(MY_CPU_SIZEOF_POINTER)'
            assert text.count(marker) == 1
            text = text.replace(marker, ')\n{\n  if (getenv("B02_FORMAT")) {\n#ifdef ENV_HAVE_LOCALE\n    MY_SetLocale();\n#endif\n    return B02Probe();\n  }\n  #if defined(MY_CPU_SIZEOF_POINTER)', 1)
            main_cpp.write_text(text)
            shutil.copyfile(HERE / 'probe.inc', main_cpp.parent / 'B02Probe.inc')
            provenance['instrumentation'] = {'Main.cpp_sha256': sha(main_cpp), 'probe.inc_sha256': sha(HERE / 'probe.inc')}
        out = work / variant
        if os.name == 'nt':
            # Run from a vcvars64 environment; each variant has independent objects.
            cmd = ['nmake', '/NOLOGO', 'PLATFORM=x64', f'O={out}']
            exe = out / '7zz.exe'
        else:
            makefiles = ['../../cmpl_gcc.mak']
            if platform.system() == 'Darwin':
                makefiles = ['../../cmpl_mac_arm64.mak'] if platform.machine() == 'arm64' else ['../../var_mac_x64.mak', '../../warn_clang_mac.mak', 'makefile.gcc']
            cmd = ['make', '-j2']
            for name in makefiles:
                cmd += ['-f', name]
            cmd += [f'O={out}']
            exe = out / '7zz'
        provenance['commands'].append({'cwd': str(bundle), 'argv': cmd})
        with (work / f'{variant}-build.log').open('wb') as log:
            if os.name == 'nt':
                subprocess.run(['cl'], stdout=log, stderr=subprocess.STDOUT, check=False)
            else:
                subprocess.run(['clang' if platform.system() == 'Darwin' else 'gcc', '--version'], stdout=log, stderr=subprocess.STDOUT, check=True)
            result = subprocess.run(cmd, cwd=bundle, stdout=log, stderr=subprocess.STDOUT)
        provenance['executables'][variant] = {'path': str(exe), 'build_exit': result.returncode, 'sha256': sha(exe) if exe.exists() else None}
        (work / 'build.json').write_text(json.dumps(provenance, indent=2) + '\n')
        if result.returncode:
            raise SystemExit(f'{variant} build failed: {work / (variant + "-build.log")}')
    for name, digest in hashes.items():
        if name != 'CPP/7zip/UI/Console/Main.cpp':
            assert sha(source / name) == digest, name
    print(json.dumps(provenance['executables'], indent=2))


if __name__ == '__main__':
    main()
