#!/usr/bin/env python3
"""Q1 evidence capture for a real native Alone2 build; no production changes.

Run from the repository root. Windows requires an initialized x64 MSVC prompt.
This collects observations, not an assertion of ABI or license qualification.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = ROOT / 'CPP/7zip/Bundles/Alone2'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    records = []

    def run(argv, name, cwd=ROOT, accepted=(0,)):
        proc = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, check=False)
        (out / name).write_bytes(proc.stdout)
        records.append({'argv': argv, 'cwd': str(cwd), 'exit_code': proc.returncode,
                        'log': name, 'sha256': digest(out / name)})
        (out / 'commands.json').write_text(json.dumps(records, indent=2) + '\n')
        if proc.returncode not in accepted:
            raise RuntimeError(f'{name}: exit {proc.returncode}; see {out / name}')
        return proc.stdout.decode('utf-8', errors='replace')

    system = platform.system()
    machine = platform.machine()
    commit = run(['git', 'rev-parse', 'HEAD'], 'source-commit.txt').strip()
    if system == 'Windows':
        run(['cl'], 'compiler.txt', accepted=(0, 2))
        run(['nmake', '/?'], 'driver.txt')
        # The legacy makefile owns the platform output directory.
        build = ['nmake', '/G', '/NOLOGO', 'PLATFORM=x64']
        binary = BUNDLE / 'x64/7zz.exe'
        run(build, 'build.log', BUNDLE)
        run(['dumpbin', '/DEPENDENTS', str(binary)], 'runtime.txt')
        run(['dumpbin', '/HEADERS', str(binary)], 'binary-headers.txt')
        (out / 'sdk-runtime.json').write_text(json.dumps({key: os.environ.get(key)
            for key in ('VCToolsVersion', 'WindowsSDKVersion', 'UCRTVersion')}, indent=2) + '\n')
        for product, directory in [('Format7zF', ROOT / 'CPP/7zip/Bundles/Format7zF'),
                                   ('Console', ROOT / 'CPP/7zip/UI/Console')]:
            run(build, product + '-build.log', directory)
        product_dir = out / 'native-product'
        product_dir.mkdir()
        shutil.copy2(ROOT / 'CPP/7zip/UI/Console/x64/7z.exe', product_dir / '7z.exe')
        shutil.copy2(ROOT / 'CPP/7zip/Bundles/Format7zF/x64/7z.dll', product_dir / '7z.dll')
        run([str(product_dir / '7z.exe'), 'i'], 'native-product-capabilities.txt', product_dir)
        run(['dumpbin', '/DEPENDENTS', str(product_dir / '7z.dll')], 'native-product-runtime.txt')
    else:
        compiler = 'gcc' if system == 'Linux' else 'clang'
        run([compiler, '--version'], 'compiler.txt')
        run(['make', '--version'], 'driver.txt')
        if system == 'Linux':
            run(['getconf', 'GNU_LIBC_VERSION'], 'libc-version.txt')
            run(['dpkg-query', '-W', 'gcc', 'g++', 'libstdc++6', 'libc6', 'binutils', 'make'], 'runtime-packages.txt')
            fragments = ['../../cmpl_gcc.mak']
        elif system == 'Darwin' and machine == 'arm64':
            run(['sw_vers'], 'os-version.txt')
            run(['xcrun', '--show-sdk-version'], 'sdk-version.txt')
            run(['xcodebuild', '-version'], 'xcode-version.txt')
            fragments = ['../../cmpl_mac_arm64.mak']
        elif system == 'Darwin' and machine == 'x86_64':
            fragments = ['../../var_mac_x64.mak', '../../warn_clang_mac.mak', 'makefile.gcc']
        else:
            raise RuntimeError(f'Unsupported native host: {system}/{machine}')
        build = ['make', '-j2']
        for fragment in fragments:
            build += ['-f', fragment]
        build += ['O=' + str(out / 'build')]
        if (out / 'build').exists():
            raise RuntimeError('Fresh output required: do not claim cached objects as new compilation')
        run(build, 'build.log', BUNDLE)

        run(build + ['-f', str(Path(__file__).with_name('native-inputs.mak')),
                     'q1-inputs'], 'selected-make-inputs.txt', BUNDLE)
        binary = out / 'build/7zz'
        run((['ldd'] if system == 'Linux' else ['otool', '-L']) + [str(binary)], 'runtime.txt')
        for product, directory in [('Format7zF', ROOT / 'CPP/7zip/Bundles/Format7zF'),
                                   ('Console', ROOT / 'CPP/7zip/UI/Console')]:
            product_build = build[:-1] + ['O=' + str(out / product)]
            run(product_build, product + '-build.log', directory)
            run(product_build + ['-f', str(Path(__file__).with_name('native-inputs.mak')),
                                 'q1-inputs'], product + '-make-inputs.txt', directory)
        product_dir = out / 'native-product'
        product_dir.mkdir()
        shutil.copy2(out / 'Console/7z', product_dir / '7z')
        shutil.copy2(out / 'Format7zF/7z.so', product_dir / '7z.so')
        run([str(product_dir / '7z'), 'i'], 'native-product-capabilities.txt', product_dir)
        run((['ldd'] if system == 'Linux' else ['otool', '-L']) +
            [str(product_dir / '7z.so')], 'native-product-runtime.txt')
    observer = product_dir / ('observe-formats.exe' if system == 'Windows' else 'observe-formats')
    observer_source = str(Path(__file__).with_name('observe-formats.cpp'))
    if system == 'Windows':
        run(['cl', '/nologo', '/EHsc', '/W4', '/WX', '/std:c++17', '/I' + str(ROOT),
             '/Fo' + str(product_dir / 'observe-formats.obj'), '/Fe' + str(observer),
             observer_source, str(ROOT / 'CPP/7zip/Bundles/Format7zF/x64/7z.lib'),
             'oleaut32.lib'], 'format-observer-build.log')
    else:
        run(['g++' if system == 'Linux' else 'clang++', '-std=c++17', '-Wall', '-Wextra',
             '-Werror', '-I', str(ROOT), observer_source, str(product_dir / '7z.so'),
             '-o', str(observer)], 'format-observer-build.log')
    run([str(observer)], 'format-registry.tsv', product_dir)
    run([str(binary), 'i'], 'capabilities.txt')
    run(['python3' if system != 'Windows' else 'python',
         '.github/tests/archive_characterization.py', str(binary),
         '--report', str(out / 'core.json'), '--expect',
         '.github/tests/oracles/' + {'Linux': 'linux-x86_64', 'Darwin': 'macos-arm64',
                                   'Windows': 'windows-amd64'}[system] + '-core.json'],
        'characterization.log')
    # Preserve every command. Selected source inventory is derived from emitted
    # compile commands, never from a hand-maintained format/object list.
    sources = set()
    for line in (out / 'build.log').read_text(errors='replace').splitlines():
        for token in shlex.split(line, posix=system != 'Windows'):
            token = token.strip('"')
            if token.endswith(('.c', '.cpp', '.asm', '.S')):
                path = (BUNDLE / token.replace('\\', '/')).resolve()
                if path.is_file() and path.is_relative_to(ROOT):
                    sources.add(path)
    if not sources:
        raise RuntimeError('No selected sources recovered; inventory cannot pass')
    inventory = []
    for path in sorted(sources):
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(errors='replace')
        header = '\n'.join(text.splitlines()[:35])
        if relative.startswith('CPP/7zip/Compress/Rar'):
            license_id = 'LGPL-2.1-or-later AND LicenseRef-unRAR-restriction'
        elif relative in ('CPP/7zip/Compress/LzfseDecoder.cpp', 'C/ZstdDec.c'):
            license_id = 'BSD-3-Clause'
        elif relative == 'C/Xxh64.c':
            license_id = 'BSD-2-Clause'
        elif re.search(r'public domain', header, re.I):
            license_id = 'LicenseRef-Public-Domain'
        else:
            license_id = 'LGPL-2.1-or-later'
        inventory.append({'path': relative, 'sha256': digest(path),
                          'license': license_id, 'license_basis': 'DOC/License.txt:8-30 and source header',
                          'header': header})
    manifest = {'schema_version': 1, 'status': 'observed-not-ABI-qualified',
                'oracle_commit': commit, 'system': system, 'machine': machine,
                'binary_sha256': digest(binary), 'binary': str(binary),
                'selected_translation_units': inventory,
                'license_review': 'requires independent selected-input review',
                'facade_commit': None, 'qualified_application_operations': [],
                'limits': ['Native CLI only; no shared facade, Rust ABI, GUI or desktop evidence',
                           'Header and transitive include audit remains separate',
                           'Capability enumeration is not per-handler behavior qualification']}
    (out / 'engine-observation.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Captured native {system}/{machine}: {len(inventory)} translation units; {out}')


if __name__ == '__main__':
    main()
