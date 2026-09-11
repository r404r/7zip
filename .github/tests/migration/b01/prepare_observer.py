#!/usr/bin/env python3
"""Build-tree-only numeric observer. Never edits the checkout's C/CPP sources."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def prepare(dest):
    dest = dest.resolve()
    if dest.exists():
        raise ValueError('observer destination must not exist')
    dest.mkdir(parents=True)
    for name in ('C', 'CPP'):
        shutil.copytree(REPO / name, dest / name,
                        ignore=shutil.ignore_patterns('*.o', '*.obj', 'x64', '_o'))
    path = dest / 'CPP/7zip/UI/Console/ExtractCallbackConsole.cpp'
    source = path.read_text()
    original = hashlib.sha256(path.read_bytes()).hexdigest()
    hooks = [
        ('#include "UserInputUtils.h"', '#include "UserInputUtils.h"\n#include "B01Observer.h"'),
        ('Z7_COM7F_IMF(CExtractCallbackConsole::SetOperationResult(Int32 opRes, Int32 encrypted))\n{\n  MT_LOCK',
         'Z7_COM7F_IMF(CExtractCallbackConsole::SetOperationResult(Int32 opRes, Int32 encrypted))\n{\n  MT_LOCK\n  B01Item(opRes, encrypted);'),
        ('    const wchar_t *name, HRESULT result)\n{\n  _currentArchivePath = name;',
         '    const wchar_t *name, HRESULT result)\n{\n  B01Open(arcLink, result);\n  _currentArchivePath = name;'),
        ('HRESULT CExtractCallbackConsole::ExtractResult(HRESULT result)\n{\n  MT_LOCK',
         'HRESULT CExtractCallbackConsole::ExtractResult(HRESULT result)\n{\n  MT_LOCK\n  B01Result(result);'),
    ]
    for old, new in hooks:
        if source.count(old) != 1:
            raise ValueError('observer source anchor changed: ' + old)
        source = source.replace(old, new)
    path.write_text(source)
    shutil.copyfile(HERE / 'B01Observer.h', path.with_name('B01Observer.h'))
    (dest / 'observer-provenance.json').write_text(json.dumps({
        'schema_version': 1, 'source': str(REPO), 'original_sha256': original,
        'instrumented_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'scope': 'test/extract console callback arguments only; not list/create or an FFI'}, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    prepare(parser.parse_args().destination)
