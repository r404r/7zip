#!/usr/bin/env python3
"""Compile/run C, C++ and Rust layout probes for the normative Q1 header.

No engine implementation is substituted. These tests prove declarations/layout,
not handler behavior or lifetime safety. Generated sources and real logs persist.
"""
import argparse
import json
from pathlib import Path
import platform
import re
import subprocess

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=True)
header = HERE / 'archive_bridge_v1.h'
text = re.sub(r'/\*.*?\*/', '', header.read_text(), flags=re.S)
records = re.findall(r'typedef struct (archive_bridge_v1_\w+)\s*\{(.*?)\}\s*\1;', text, re.S)
if not records:
    raise SystemExit('No struct declarations')
c_lines = ['#include <stddef.h>', '#include <stdio.h>', '#include "archive_bridge_v1.h"',
           '#ifdef __cplusplus', '#define ALIGNOF(T) alignof(T)', '#else',
           '#define ALIGNOF(T) _Alignof(T)', '#endif', 'int main(void) {']
r_lines = ['#![allow(non_camel_case_types, dead_code)]', 'use std::ffi::c_void;',
           'enum archive_bridge_v1_context {}', 'enum archive_bridge_v1_result {}',
           'type archive_bridge_v1_is_cancelled = Option<unsafe extern "C" fn(*mut c_void) -> u32>;',
           'type archive_bridge_v1_on_progress = Option<unsafe extern "C" fn(*mut c_void, *const archive_bridge_v1_progress) -> i32>;',
           'type archive_bridge_v1_ask = Option<unsafe extern "C" fn(*mut c_void, *const archive_bridge_v1_question, *mut archive_bridge_v1_reply) -> i32>;']
r_main = ['fn main() {']
primitives = {'uint8_t': 'u8', 'uint16_t': 'u16', 'uint32_t': 'u32',
              'uint64_t': 'u64', 'int32_t': 'i32', 'int64_t': 'i64', 'void': 'c_void'}
for name, body in records:
    c_lines.append(f'printf("{name} size %zu align %zu\\n", sizeof({name}), ALIGNOF({name}));')
    r_lines += ['#[repr(C)]', f'struct {name} {{']
    r_main.append(f'println!("{name} size {{}} align {{}}", std::mem::size_of::<{name}>(), std::mem::align_of::<{name}>());')
    for field in body.split(';'):
        field = field.strip()
        if not field:
            continue
        match = re.fullmatch(r'(const\s+)?(\w+)\s*(\*)?\s*(\w+)(?:\[(\d+)\])?', field)
        if not match:
            raise SystemExit('Unsupported declaration: ' + field)
        const, ctype, pointer, member, count = match.groups()
        rtype = primitives.get(ctype, ctype)
        if pointer:
            rtype = ('*const ' if const else '*mut ') + rtype
        if count:
            rtype = f'[{rtype}; {count}]'
        r_lines.append(f'  {member}: {rtype},')
        c_lines.append(f'printf("{name}.{member} %zu\\n", offsetof({name}, {member}));')
        r_main.append(f'println!("{name}.{member} {{}}", std::mem::offset_of!({name}, {member}));')
    r_lines.append('}')
c_lines += ['return 0;', '}']
r_main += ['}']
(out / 'layout.c').write_text('\n'.join(c_lines) + '\n')
(out / 'layout.rs').write_text('\n'.join(r_lines + r_main) + '\n')
commands = []


def run(argv, log):
    proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    (out / log).write_bytes(proc.stdout)
    commands.append({'argv': argv, 'exit_code': proc.returncode, 'log': log})
    (out / 'layout-commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    if proc.returncode:
        raise RuntimeError(f'{log}: exit {proc.returncode}')
    return proc.stdout


windows = platform.system() == 'Windows'
for language in ('c', 'cpp'):
    binary = out / (language + ('.exe' if windows else ''))
    if windows:
        command = ['cl', '/nologo', '/W4', '/WX', '/std:c11' if language == 'c' else '/std:c++17',
                   '/TC' if language == 'c' else '/TP', '/I' + str(HERE),
                   '/Fo' + str(out / (language + '.obj')), '/Fe' + str(binary), str(out / 'layout.c')]
    else:
        compiler = ('gcc' if language == 'c' else 'g++') if platform.system() == 'Linux' else ('clang' if language == 'c' else 'clang++')
        command = [compiler, '-std=c11' if language == 'c' else '-std=c++17',
                   '-Wall', '-Wextra', '-Werror', '-x', 'c' if language == 'c' else 'c++',
                   '-I', str(HERE), str(out / 'layout.c'), '-o', str(binary)]
    run(command, language + '-build.log')
    run([str(binary)], language + '-layout.txt')
run(['rustc', '+1.97.1', '--version', '--verbose'], 'rustc.txt')
run(['cargo', '+1.97.1', '--version'], 'cargo.txt')
rust_binary = out / ('rust.exe' if windows else 'rust')
run(['rustc', '+1.97.1', '--edition=2024', '-Dwarnings', '-C', 'panic=unwind',
     str(out / 'layout.rs'), '-o', str(rust_binary)], 'rust-build.log')
run([str(rust_binary)], 'rust-layout.txt')
observed = [(out / (language + '-layout.txt')).read_text() for language in ('c', 'cpp', 'rust')]
if len(set(observed)) != 1:
    raise SystemExit('FAIL: C/C++/Rust layout mismatch')
print(f'PASS: {len(records)} struct layouts and every field offset match C/C++/Rust on {platform.system()}/{platform.machine()}')
