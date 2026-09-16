#!/usr/bin/env python3
"""Build the bridge-owned, non-product MSVC ABI convention probe.

This driver intentionally invokes cl/link/dumpbin directly.  It never invokes a
bridge build recipe except for the explicit fail-closed NMAKE guard check, never
links retained engine objects, and deletes all runnable probe files before its
evidence directory is uploaded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import platform
import re
import shutil
import subprocess
import sys
from typing import Iterable

FROZEN_HEADER_SHA256 = "eabe714b31e2076735b8313c06618e5dbb3db4ea924cbef244b78a8b107ee26d"
EXPORT_ARGUMENT_BYTES = {
    "archive_bridge_v1_handshake": 8,
    "archive_bridge_v1_create_context": 8,
    "archive_bridge_v1_destroy_context": 4,
    "archive_bridge_v1_capabilities": 12,
    "archive_bridge_v1_open": 20,
    "archive_bridge_v1_entries": 20,
    "archive_bridge_v1_close": 20,
    "archive_bridge_v1_result_destroy": 8,
}
CALLBACK_ARGUMENT_BYTES = {
    "probe_is_cancelled": 4,
    "probe_on_progress": 8,
    "probe_ask": 12,
}
CURRENT_EXPORTS = (
    "archive_bridge_v1_handshake",
    "archive_bridge_v1_create_context",
    "archive_bridge_v1_destroy_context",
    "archive_bridge_v1_capabilities",
    "archive_bridge_v1_result_destroy",
)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def expected_coff_symbol(arch: str, name: str) -> str:
    if arch == "amd64":
        return name
    if arch == "x86":
        return "_" + name
    raise ValueError(f"unsupported architecture: {arch}")


def contract_header_mutation_fixture() -> str:
    return """#ifndef ARCHIVE_BRIDGE_V1_H
#define ARCHIVE_BRIDGE_V1_H
#define ARCHIVE_BRIDGE_V1_CALL __cdecl
typedef unsigned (ARCHIVE_BRIDGE_V1_CALL *archive_bridge_v1_is_cancelled)(void *);
int ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_handshake(void *, void *);
int ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_close(void *, unsigned long long, unsigned long long);
#endif
"""


def build_mutations(source: str) -> dict[str, str]:
    without_call = source.replace(
        "int ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_handshake",
        "int archive_bridge_v1_handshake",
        1,
    )
    callback_stdcall = source.replace(
        "(ARCHIVE_BRIDGE_V1_CALL *archive_bridge_v1_is_cancelled)",
        "(__stdcall *archive_bridge_v1_is_cancelled)",
        1,
    )
    close_stdcall = source.replace(
        "int ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_close",
        "int __stdcall archive_bridge_v1_close",
        1,
    )
    return {
        "export_without_call": without_call,
        "callback_stdcall": callback_stdcall,
        "export_stdcall": close_stdcall,
        "def_alias_evasion": close_stdcall,
    }


def validate_source_inputs(root: pathlib.Path, expected_hash: str | None = FROZEN_HEADER_SHA256) -> dict[str, str]:
    frozen = root / "docs/ai-migration/qualification/archive_bridge_v1.h"
    production = root / "rust/bridge/archive_bridge_v1.h"
    makefile = root / "rust/bridge/makefile"
    for path in (frozen, production, makefile):
        if not path.is_file():
            raise RuntimeError(f"required input is missing: {path}")
    frozen_worktree_hash = sha256(frozen)
    production_worktree_hash = sha256(production)
    if frozen_worktree_hash != production_worktree_hash:
        raise RuntimeError("frozen and production header hashes differ")
    # actions/checkout can materialize CRLF on Windows.  The reviewed identity
    # is the canonical Git blob, not a checkout's platform line ending.  Still
    # require both materialized copies to be byte-identical before compiling.
    try:
        frozen_blob = subprocess.run(
            ["git", "-C", str(root), "show", "HEAD:docs/ai-migration/qualification/archive_bridge_v1.h"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
        ).stdout
        production_blob = subprocess.run(
            ["git", "-C", str(root), "show", "HEAD:rust/bridge/archive_bridge_v1.h"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
        ).stdout
        frozen_hash = hashlib.sha256(frozen_blob).hexdigest()
        production_hash = hashlib.sha256(production_blob).hexdigest()
    except (subprocess.CalledProcessError, FileNotFoundError):
        frozen_hash = frozen_worktree_hash
        production_hash = production_worktree_hash
    if frozen_hash != production_hash:
        raise RuntimeError("canonical frozen and production header hashes differ")
    if expected_hash is not None and frozen_hash != expected_hash:
        raise RuntimeError(f"canonical frozen header hash drift: {frozen_hash}")
    text = makefile.read_text(encoding="utf-8")
    guard = text.find("!ERROR S2a-DEV performs no Windows facade build.")
    target = text.find("PROG = archive_bridge_v1.dll")
    include = text.find("!include")
    if guard < 0 or (target >= 0 and guard > target) or (include >= 0 and guard > include):
        raise RuntimeError("retained makefile fail-closed guard is missing or no longer precedes targets/includes")
    return {
        "frozen_header_sha256": frozen_hash,
        "production_header_sha256": production_hash,
        "frozen_header_worktree_sha256": frozen_worktree_hash,
        "production_header_worktree_sha256": production_worktree_hash,
        "makefile_sha256": sha256(makefile),
    }


class EvidenceRunner:
    def __init__(self, evidence: pathlib.Path):
        self.evidence = evidence
        self.evidence.mkdir(parents=True, exist_ok=True)
        self.commands: list[dict[str, object]] = []

    def run(
        self,
        name: str,
        command: list[str],
        *,
        cwd: pathlib.Path,
        expected: int | None = 0,
    ) -> subprocess.CompletedProcess[str]:
        log = self.evidence / f"{name}.log"
        display = subprocess.list2cmdline(command)
        proc = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, encoding="utf-8", errors="replace")
        log.write_text(f"> {display}\nexit_code={proc.returncode}\n{proc.stdout}", encoding="utf-8")
        self.commands.append({"name": name, "command": display, "exit_code": proc.returncode,
                              "log": log.name})
        if expected is not None and proc.returncode != expected:
            raise RuntimeError(f"{name}: expected exit {expected}, got {proc.returncode}; see {log}")
        return proc

    def write_manifest(self, extra: dict[str, object]) -> None:
        payload = dict(extra)
        payload["commands"] = self.commands
        (self.evidence / "manifest.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )


def definitions_source() -> str:
    return r'''#include "archive_bridge_v1.h"
#include <stdint.h>
extern "C" {
#define PROBE_EXPORT __declspec(dllexport)
PROBE_EXPORT extern const char cc_probe_not_product[] = "NOT_PRODUCT";
PROBE_EXPORT int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_handshake(const archive_bridge_v1_info *a, archive_bridge_v1_info *b) { return a==(void*)(uintptr_t)0x10101010 && b==(void*)(uintptr_t)0x20202020 ? 101 : -101; }
PROBE_EXPORT int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_create_context(const archive_bridge_v1_context_options *a, archive_bridge_v1_context **b) { return a==(void*)(uintptr_t)0x30303030 && b==(void*)(uintptr_t)0x40404040 ? 102 : -102; }
PROBE_EXPORT int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_destroy_context(archive_bridge_v1_context *a) { return a==(void*)(uintptr_t)0x50505050 ? 103 : -103; }
PROBE_EXPORT int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_capabilities(archive_bridge_v1_context *a, archive_bridge_v1_result **b, archive_bridge_v1_capability_view *c) { return a==(void*)(uintptr_t)0x60606060 && b==(void*)(uintptr_t)0x70707070 && c==(void*)(uintptr_t)0x80808080 ? 104 : -104; }
PROBE_EXPORT int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_open(archive_bridge_v1_context *a, const archive_bridge_v1_open_request *b, const archive_bridge_v1_operation *c, archive_bridge_v1_result **d, archive_bridge_v1_view *e) { return a==(void*)(uintptr_t)0x11111111 && b==(void*)(uintptr_t)0x22222222 && c==(void*)(uintptr_t)0x33333333 && d==(void*)(uintptr_t)0x44444444 && e==(void*)(uintptr_t)0x55555555 ? 105 : -105; }
PROBE_EXPORT int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_entries(archive_bridge_v1_context *a, const archive_bridge_v1_entries_request *b, const archive_bridge_v1_operation *c, archive_bridge_v1_result **d, archive_bridge_v1_view *e) { return a==(void*)(uintptr_t)0x12121212 && b==(void*)(uintptr_t)0x23232323 && c==(void*)(uintptr_t)0x34343434 && d==(void*)(uintptr_t)0x45454545 && e==(void*)(uintptr_t)0x56565656 ? 106 : -106; }
PROBE_EXPORT int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_close(archive_bridge_v1_context *a, uint64_t b, uint64_t c) { return a==(void*)(uintptr_t)0x67676767 && b==UINT64_C(0x1122334455667788) && c==UINT64_C(0x8877665544332211) ? 107 : -107; }
PROBE_EXPORT int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_result_destroy(archive_bridge_v1_context *a, archive_bridge_v1_result *b) { return a==(void*)(uintptr_t)0x78787878 && b==(void*)(uintptr_t)0x89898989 ? 108 : -108; }
PROBE_EXPORT int32_t ARCHIVE_BRIDGE_V1_CALL cc_probe_invoke_callbacks(const archive_bridge_v1_operation *op) {
  archive_bridge_v1_progress progress = {0}; archive_bridge_v1_question question = {0}; archive_bridge_v1_reply reply = {0};
  progress.counter_kind = 0x7011; question.kind = 0x7022;
  if (!op || !op->is_cancelled || !op->on_progress || !op->ask) return -1;
  if (op->is_cancelled(op->user) != 0xCA11u) return -2;
  if (op->on_progress(op->user, &progress) != 0x701) return -3;
  if (op->ask(op->user, &question, &reply) != 0x702 || reply.kind != 0x7033) return -4;
  return 109;
}
}
'''


def typecheck_source() -> str:
    exports = r'''#include "archive_bridge_v1.h"
#include <stdint.h>
typedef int32_t (__cdecl *handshake_fn)(const archive_bridge_v1_info*, archive_bridge_v1_info*);
typedef int32_t (__cdecl *create_fn)(const archive_bridge_v1_context_options*, archive_bridge_v1_context**);
typedef int32_t (__cdecl *destroy_fn)(archive_bridge_v1_context*);
typedef int32_t (__cdecl *caps_fn)(archive_bridge_v1_context*, archive_bridge_v1_result**, archive_bridge_v1_capability_view*);
typedef int32_t (__cdecl *open_fn)(archive_bridge_v1_context*, const archive_bridge_v1_open_request*, const archive_bridge_v1_operation*, archive_bridge_v1_result**, archive_bridge_v1_view*);
typedef int32_t (__cdecl *entries_fn)(archive_bridge_v1_context*, const archive_bridge_v1_entries_request*, const archive_bridge_v1_operation*, archive_bridge_v1_result**, archive_bridge_v1_view*);
typedef int32_t (__cdecl *close_fn)(archive_bridge_v1_context*, uint64_t, uint64_t);
typedef int32_t (__cdecl *result_destroy_fn)(archive_bridge_v1_context*, archive_bridge_v1_result*);
static handshake_fn const c1 = &archive_bridge_v1_handshake;
static create_fn const c2 = &archive_bridge_v1_create_context;
static destroy_fn const c3 = &archive_bridge_v1_destroy_context;
static caps_fn const c4 = &archive_bridge_v1_capabilities;
static open_fn const c5 = &archive_bridge_v1_open;
static entries_fn const c6 = &archive_bridge_v1_entries;
static close_fn const c7 = &archive_bridge_v1_close;
static result_destroy_fn const c8 = &archive_bridge_v1_result_destroy;
static uint32_t __cdecl probe_is_cancelled(void *p) { return p != 0; }
static int32_t __cdecl probe_on_progress(void *p, const archive_bridge_v1_progress *e) { return p != 0 && e != 0; }
static int32_t __cdecl probe_ask(void *p, const archive_bridge_v1_question *q, archive_bridge_v1_reply *r) { return p != 0 && q != 0 && r != 0; }
static archive_bridge_v1_is_cancelled const cb1 = &probe_is_cancelled;
static archive_bridge_v1_on_progress const cb2 = &probe_on_progress;
static archive_bridge_v1_ask const cb3 = &probe_ask;
int main(void) { return !(c1 && c2 && c3 && c4 && c5 && c6 && c7 && c8 && cb1 && cb2 && cb3); }
'''
    return exports


def cpp_typecheck_source() -> str:
    return r'''#include "archive_bridge_v1.h"
#include <type_traits>
static_assert(std::is_same<decltype(&archive_bridge_v1_handshake), int32_t (__cdecl *)(const archive_bridge_v1_info*, archive_bridge_v1_info*)>::value, "handshake convention");
static_assert(std::is_same<decltype(&archive_bridge_v1_create_context), int32_t (__cdecl *)(const archive_bridge_v1_context_options*, archive_bridge_v1_context**)>::value, "create convention");
static_assert(std::is_same<decltype(&archive_bridge_v1_destroy_context), int32_t (__cdecl *)(archive_bridge_v1_context*)>::value, "destroy convention");
static_assert(std::is_same<decltype(&archive_bridge_v1_capabilities), int32_t (__cdecl *)(archive_bridge_v1_context*, archive_bridge_v1_result**, archive_bridge_v1_capability_view*)>::value, "capabilities convention");
static_assert(std::is_same<decltype(&archive_bridge_v1_open), int32_t (__cdecl *)(archive_bridge_v1_context*, const archive_bridge_v1_open_request*, const archive_bridge_v1_operation*, archive_bridge_v1_result**, archive_bridge_v1_view*)>::value, "open convention");
static_assert(std::is_same<decltype(&archive_bridge_v1_entries), int32_t (__cdecl *)(archive_bridge_v1_context*, const archive_bridge_v1_entries_request*, const archive_bridge_v1_operation*, archive_bridge_v1_result**, archive_bridge_v1_view*)>::value, "entries convention");
static_assert(std::is_same<decltype(&archive_bridge_v1_close), int32_t (__cdecl *)(archive_bridge_v1_context*, uint64_t, uint64_t)>::value, "close convention");
static_assert(std::is_same<decltype(&archive_bridge_v1_result_destroy), int32_t (__cdecl *)(archive_bridge_v1_context*, archive_bridge_v1_result*)>::value, "result convention");
static_assert(std::is_same<archive_bridge_v1_is_cancelled, uint32_t (__cdecl *)(void*)>::value, "cancel callback convention");
static_assert(std::is_same<archive_bridge_v1_on_progress, int32_t (__cdecl *)(void*, const archive_bridge_v1_progress*)>::value, "progress callback convention");
static_assert(std::is_same<archive_bridge_v1_ask, int32_t (__cdecl *)(void*, const archive_bridge_v1_question*, archive_bridge_v1_reply*)>::value, "ask callback convention");
int main() { return 0; }
'''


def c_caller_source() -> str:
    return r'''#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include "archive_bridge_v1.h"
#define LOAD(name, type) union { FARPROC raw; type typed; } name##_loader; name##_loader.raw=GetProcAddress(module,#name); type name=name##_loader.typed; if(!name)return 20
typedef int32_t (__cdecl *handshake_fn)(const archive_bridge_v1_info*, archive_bridge_v1_info*);
typedef int32_t (__cdecl *create_fn)(const archive_bridge_v1_context_options*, archive_bridge_v1_context**);
typedef int32_t (__cdecl *destroy_fn)(archive_bridge_v1_context*);
typedef int32_t (__cdecl *caps_fn)(archive_bridge_v1_context*, archive_bridge_v1_result**, archive_bridge_v1_capability_view*);
typedef int32_t (__cdecl *open_fn)(archive_bridge_v1_context*, const archive_bridge_v1_open_request*, const archive_bridge_v1_operation*, archive_bridge_v1_result**, archive_bridge_v1_view*);
typedef int32_t (__cdecl *entries_fn)(archive_bridge_v1_context*, const archive_bridge_v1_entries_request*, const archive_bridge_v1_operation*, archive_bridge_v1_result**, archive_bridge_v1_view*);
typedef int32_t (__cdecl *close_fn)(archive_bridge_v1_context*, uint64_t, uint64_t);
typedef int32_t (__cdecl *result_destroy_fn)(archive_bridge_v1_context*, archive_bridge_v1_result*);
static unsigned cancel_count, progress_count, ask_count;
static uint32_t __cdecl cancelled(void *u) { if (u != (void*)(uintptr_t)0x1234) return 0; ++cancel_count; return 0xCA11u; }
static int32_t __cdecl progress(void *u, const archive_bridge_v1_progress *e) { if (u != (void*)(uintptr_t)0x1234 || !e || e->counter_kind != 0x7011) return -1; ++progress_count; return 0x701; }
static int32_t __cdecl ask(void *u, const archive_bridge_v1_question *q, archive_bridge_v1_reply *r) { if (u != (void*)(uintptr_t)0x1234 || !q || q->kind != 0x7022 || !r) return -1; r->kind=0x7033; ++ask_count; return 0x702; }
typedef int32_t (__cdecl *helper_fn)(const archive_bridge_v1_operation*);
int main(int argc, char **argv) {
  if (argc != 2) return 10; char full[MAX_PATH]; if (!_fullpath(full, argv[1], MAX_PATH)) return 11;
  HMODULE module = LoadLibraryA(full); if (!module) return 12;
  LOAD(archive_bridge_v1_handshake, handshake_fn);
  LOAD(archive_bridge_v1_create_context, create_fn);
  LOAD(archive_bridge_v1_destroy_context, destroy_fn);
  LOAD(archive_bridge_v1_capabilities, caps_fn);
  LOAD(archive_bridge_v1_open, open_fn);
  LOAD(archive_bridge_v1_entries, entries_fn);
  LOAD(archive_bridge_v1_close, close_fn);
  LOAD(archive_bridge_v1_result_destroy, result_destroy_fn);
  union { FARPROC raw; helper_fn typed; } helper_loader; helper_loader.raw=GetProcAddress(module,"cc_probe_invoke_callbacks"); helper_fn helper=helper_loader.typed; if (!helper) return 21;
  if (archive_bridge_v1_handshake((void*)(uintptr_t)0x10101010,(void*)(uintptr_t)0x20202020)!=101 || archive_bridge_v1_create_context((void*)(uintptr_t)0x30303030,(void*)(uintptr_t)0x40404040)!=102 || archive_bridge_v1_destroy_context((void*)(uintptr_t)0x50505050)!=103 || archive_bridge_v1_capabilities((void*)(uintptr_t)0x60606060,(void*)(uintptr_t)0x70707070,(void*)(uintptr_t)0x80808080)!=104 || archive_bridge_v1_open((void*)(uintptr_t)0x11111111,(void*)(uintptr_t)0x22222222,(void*)(uintptr_t)0x33333333,(void*)(uintptr_t)0x44444444,(void*)(uintptr_t)0x55555555)!=105 || archive_bridge_v1_entries((void*)(uintptr_t)0x12121212,(void*)(uintptr_t)0x23232323,(void*)(uintptr_t)0x34343434,(void*)(uintptr_t)0x45454545,(void*)(uintptr_t)0x56565656)!=106 || archive_bridge_v1_close((void*)(uintptr_t)0x67676767,UINT64_C(0x1122334455667788),UINT64_C(0x8877665544332211))!=107 || archive_bridge_v1_result_destroy((void*)(uintptr_t)0x78787878,(void*)(uintptr_t)0x89898989)!=108) return 30;
  archive_bridge_v1_operation op = {0}; op.user=(void*)(uintptr_t)0x1234; op.is_cancelled=cancelled; op.on_progress=progress; op.ask=ask;
  if (helper(&op)!=109 || cancel_count!=1 || progress_count!=1 || ask_count!=1) return 31;
  puts("PASS: all 8 cdecl exports and all 3 cdecl callbacks executed exactly"); FreeLibrary(module); return 0;
}
'''


def rust_caller_source() -> str:
    return r'''#![allow(non_camel_case_types)]
use std::{ffi::c_void, path::PathBuf};
#[repr(C)] struct Info { bytes:[u8;88] }
#[repr(C)] struct ContextOptions { bytes:[u8;96] }
#[repr(C)] struct CapabilityView { bytes:[u8;64] }
#[repr(C)] struct Context { _private:[u8;0] }
#[repr(C)] struct ResultHandle { _private:[u8;0] }
#[repr(C)] struct Progress { struct_size:u32, counter_kind:u32, rest:[u8;32] }
#[repr(C)] struct Question { struct_size:u32, kind:u32, rest:[u8;64] }
#[repr(C)] struct Reply { struct_size:u32, kind:u32, rest:[u8;56] }
#[repr(C)] struct Operation { struct_size:u32, abi_major:u32, task_id:u64, user:*mut c_void, cancelled:Option<unsafe extern "C" fn(*mut c_void)->u32>, progress:Option<unsafe extern "C" fn(*mut c_void,*const Progress)->i32>, ask:Option<unsafe extern "C" fn(*mut c_void,*const Question,*mut Reply)->i32> }
#[link(name="archive_bridge_v1_cc_probe")]
extern "C" { fn archive_bridge_v1_handshake(a:*const Info,b:*mut Info)->i32; fn archive_bridge_v1_create_context(a:*const ContextOptions,b:*mut *mut Context)->i32; fn archive_bridge_v1_destroy_context(a:*mut Context)->i32; fn archive_bridge_v1_capabilities(a:*mut Context,b:*mut *mut ResultHandle,c:*mut CapabilityView)->i32; fn archive_bridge_v1_result_destroy(a:*mut Context,b:*mut ResultHandle)->i32; fn cc_probe_invoke_callbacks(op:*const Operation)->i32; }
#[link(name="kernel32")] extern "system" { fn GetModuleHandleExW(flags:u32,addr:*const u16,module:*mut *mut c_void)->i32; fn GetModuleFileNameW(module:*mut c_void,path:*mut u16,size:u32)->u32; }
static mut COUNTS:[u32;3]=[0;3];
unsafe extern "C" fn cancelled(user: *mut c_void)->u32 { if user as usize != 0x1234 { return 0; } COUNTS[0]+=1; 0xCA11 }
unsafe extern "C" fn progress(user: *mut c_void,event:*const Progress)->i32 { if user as usize != 0x1234 || event.is_null() || (*event).counter_kind != 0x7011 { return -1; } COUNTS[1]+=1; 0x701 }
unsafe extern "C" fn ask(user: *mut c_void,q:*const Question,r:*mut Reply)->i32 { if user as usize != 0x1234 || q.is_null() || (*q).kind != 0x7022 || r.is_null() { return -1; } (*r).kind=0x7033; COUNTS[2]+=1; 0x702 }
fn main(){ unsafe {
 let mut module=std::ptr::null_mut(); if GetModuleHandleExW(6,archive_bridge_v1_handshake as usize as *const u16,&mut module)==0 { std::process::exit(40); }
 let mut buf=[0u16;32768]; let n=GetModuleFileNameW(module,buf.as_mut_ptr(),buf.len() as u32); if n==0 { std::process::exit(41); }
 let loaded=PathBuf::from(String::from_utf16_lossy(&buf[..n as usize])).canonicalize().unwrap(); let expected=std::env::current_exe().unwrap().parent().unwrap().join("archive_bridge_v1_cc_probe.dll").canonicalize().unwrap(); if loaded!=expected { std::process::exit(42); }
 if archive_bridge_v1_handshake(0x10101010usize as *const Info,0x20202020usize as *mut Info)!=101 || archive_bridge_v1_create_context(0x30303030usize as *const ContextOptions,0x40404040usize as *mut *mut Context)!=102 || archive_bridge_v1_destroy_context(0x50505050usize as *mut Context)!=103 || archive_bridge_v1_capabilities(0x60606060usize as *mut Context,0x70707070usize as *mut *mut ResultHandle,0x80808080usize as *mut CapabilityView)!=104 || archive_bridge_v1_result_destroy(0x78787878usize as *mut Context,0x89898989usize as *mut ResultHandle)!=108 { std::process::exit(43); }
 let op=Operation{struct_size:0,abi_major:0,task_id:0,user:0x1234usize as *mut c_void,cancelled:Some(cancelled),progress:Some(progress),ask:Some(ask)}; if cc_probe_invoke_callbacks(&op)!=109 || COUNTS != [1,1,1] { std::process::exit(44); }
 println!("PASS: Rust extern C imports and three contract-probe callbacks executed; loaded={}",loaded.display()); }}
'''


def raw_symbols(text: str) -> set[str]:
    found: set[str] = set()
    for line in text.splitlines():
        if "|" in line and "External" in line and "UNDEF" not in line:
            token = line.split("|", 1)[1].strip().split()[0]
            found.add(token)
    return found


def defined_symbols(text: str) -> set[str]:
    found: set[str] = set()
    for line in text.splitlines():
        if "|" in line and "UNDEF" not in line:
            found.add(line.split("|", 1)[1].strip().split()[0])
    return found


def pe_export_names(text: str) -> set[str]:
    names: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"^\s+\d+\s+[0-9A-Fa-f]+\s+[0-9A-Fa-f]+\s+(\S+)", line)
        if match:
            names.add(match.group(1))
    return names


def assert_machine(text: str, arch: str) -> None:
    needle = "8664 machine (x64)" if arch == "amd64" else "14C machine (x86)"
    if needle.lower() not in text.lower():
        raise RuntimeError(f"DUMPBIN machine mismatch: expected {needle}")


def assert_object_symbols(text: str, arch: str, names: Iterable[str]) -> None:
    symbols = raw_symbols(text)
    missing = [expected_coff_symbol(arch, name) for name in names if expected_coff_symbol(arch, name) not in symbols]
    if missing:
        raise RuntimeError(f"missing exact raw COFF symbols: {missing}")


def write_sources(work: pathlib.Path, header: str) -> None:
    work.mkdir(parents=True, exist_ok=True)
    (work / "archive_bridge_v1.h").write_text(header, encoding="utf-8")
    (work / "probe.cpp").write_text(definitions_source(), encoding="utf-8")
    (work / "typecheck.c").write_text(typecheck_source(), encoding="utf-8")
    (work / "typecheck.cpp").write_text(cpp_typecheck_source(), encoding="utf-8")
    (work / "caller.c").write_text(c_caller_source(), encoding="utf-8")
    (work / "caller.rs").write_text(rust_caller_source(), encoding="utf-8")


def compile_diagnostic_sweep(
    root: pathlib.Path,
    output: pathlib.Path,
    arch: str,
    runner: EvidenceRunner,
) -> None:
    """Compile every independent positive MSVC translation unit before failing.

    This sweep prevents a hosted run from revealing only the first probe-owned
    compiler problem.  It intentionally does not link or execute anything; the
    formal lane below repeats these compiles and performs all artifact checks.
    """
    work = output / "work" / arch / "compile-diagnostic-sweep"
    header = (root / "docs/ai-migration/qualification/archive_bridge_v1.h").read_text(
        encoding="utf-8"
    )
    write_sources(work, header)
    commands = (
        (
            "diagnostic-current-source",
            [
                "cl", "/nologo", "/c", "/TP", "/Gr", "/W4", "/WX", "/EHsc",
                "/DARCHIVE_BRIDGE_V1_HEADER_SHA256_HEX=\"" + FROZEN_HEADER_SHA256 + "\"",
                "/DARCHIVE_BRIDGE_V1_BUILD_SHA256_HEX=\"" + ("0" * 64) + "\"",
                "/I", str(root), "/I", str(root / "rust/bridge"),
                str(root / "rust/bridge/archive_bridge_v1.cpp"),
                "/Fo" + str(work / "current-source.obj"),
            ],
        ),
        (
            "diagnostic-typecheck-c",
            ["cl", "/nologo", "/c", "/TC", "/Gr", "/W4", "/WX",
             str(work / "typecheck.c"), "/Fo" + str(work / "typecheck-c.obj")],
        ),
        (
            "diagnostic-typecheck-cpp",
            ["cl", "/nologo", "/c", "/TP", "/Gr", "/W4", "/WX", "/EHsc",
             str(work / "typecheck.cpp"), "/Fo" + str(work / "typecheck-cpp.obj")],
        ),
        (
            "diagnostic-probe",
            ["cl", "/nologo", "/c", "/TP", "/Gr", "/W4", "/WX", "/EHsc",
             str(work / "probe.cpp"), "/Fo" + str(work / "probe.obj")],
        ),
        (
            "diagnostic-c-caller",
            ["cl", "/nologo", "/c", "/TC", "/Gr", "/W4", "/WX", "/Od", "/RTC1",
             str(work / "caller.c"), "/Fo" + str(work / "caller.obj")],
        ),
    )
    failures: list[str] = []
    summary: list[str] = []
    for name, command in commands:
        proc = runner.run(name, command, cwd=work, expected=None)
        diagnostics = sorted(set(re.findall(r"\bC\d{4}\b", proc.stdout)))
        diagnostic_text = ",".join(diagnostics) if diagnostics else "none"
        summary.append(f"{name}: exit_code={proc.returncode}; diagnostics={diagnostic_text}")
        if proc.returncode != 0:
            failures.append(f"{name} [{diagnostic_text}]")
    (runner.evidence / "compile-diagnostic-summary.txt").write_text(
        "\n".join(summary) + "\n", encoding="utf-8"
    )
    (runner.evidence / "compile-diagnostic-commands.json").write_text(
        json.dumps(
            {
                "architecture": arch,
                "commands": [
                    command
                    for command in runner.commands
                    if str(command.get("name", "")).startswith("diagnostic-")
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    if failures:
        raise RuntimeError("MSVC compile diagnostic sweep failed: " + "; ".join(failures))


def compile_current_source(root: pathlib.Path, work: pathlib.Path, arch: str, runner: EvidenceRunner) -> None:
    obj = work / "current-source.obj"
    runner.run("current-source-compile", ["cl", "/nologo", "/c", "/TP", "/Gr", "/W4", "/WX", "/EHsc",
        "/DARCHIVE_BRIDGE_V1_HEADER_SHA256_HEX=\"" + FROZEN_HEADER_SHA256 + "\"",
        "/DARCHIVE_BRIDGE_V1_BUILD_SHA256_HEX=\"" + ("0" * 64) + "\"", "/I", str(root), "/I", str(root / "rust/bridge"),
        str(root / "rust/bridge/archive_bridge_v1.cpp"), "/Fo" + str(obj)], cwd=work)
    symbols = runner.run("current-source-symbols", ["dumpbin", "/symbols", str(obj)], cwd=work).stdout
    headers = runner.run("current-source-headers", ["dumpbin", "/headers", str(obj)], cwd=work).stdout
    assert_machine(headers, arch)
    assert_object_symbols(symbols, arch, CURRENT_EXPORTS)


def positive_lane(root: pathlib.Path, output: pathlib.Path, arch: str, runner: EvidenceRunner) -> None:
    work = output / "work" / arch / "positive"
    header = (root / "docs/ai-migration/qualification/archive_bridge_v1.h").read_text(encoding="utf-8")
    write_sources(work, header)
    compile_current_source(root, work, arch, runner)
    typecheck_c = work / "typecheck-c.obj"
    typecheck_cpp = work / "typecheck-cpp.obj"
    runner.run("typecheck-c", ["cl", "/nologo", "/c", "/TC", "/Gr", "/W4", "/WX", str(work / "typecheck.c"), "/Fo" + str(typecheck_c)], cwd=work)
    runner.run("typecheck-cpp", ["cl", "/nologo", "/c", "/TP", "/Gr", "/W4", "/WX", "/EHsc", str(work / "typecheck.cpp"), "/Fo" + str(typecheck_cpp)], cwd=work)
    for name, artifact in (("typecheck-c", typecheck_c), ("typecheck-cpp", typecheck_cpp)):
        headers = runner.run(name + "-headers", ["dumpbin", "/headers", str(artifact)], cwd=work).stdout
        assert_machine(headers, arch)
        runner.run(name + "-symbols", ["dumpbin", "/symbols", str(artifact)], cwd=work)
    callback_dump = runner.run("callback-target-symbols", ["dumpbin", "/symbols", str(typecheck_c)], cwd=work).stdout
    callback_symbols = defined_symbols(callback_dump)
    expected_callbacks = {expected_coff_symbol(arch, name) for name in CALLBACK_ARGUMENT_BYTES}
    if not expected_callbacks.issubset(callback_symbols):
        raise RuntimeError(f"missing callback target symbols: {sorted(expected_callbacks - callback_symbols)}")
    probe_obj = work / "probe.obj"
    runner.run("probe-compile", ["cl", "/nologo", "/c", "/TP", "/Gr", "/W4", "/WX", "/EHsc", str(work / "probe.cpp"), "/Fo" + str(probe_obj)], cwd=work)
    symbols = runner.run("probe-symbols", ["dumpbin", "/symbols", str(probe_obj)], cwd=work).stdout
    assert_object_symbols(symbols, arch, EXPORT_ARGUMENT_BYTES)
    dll = work / "archive_bridge_v1_cc_probe.dll"
    lib = work / "archive_bridge_v1_cc_probe.lib"
    runner.run("probe-link", ["link", "/nologo", "/dll", "/noentry", str(probe_obj), "/out:" + str(dll), "/implib:" + str(lib)], cwd=work)
    headers = runner.run("probe-dll-headers", ["dumpbin", "/headers", str(dll)], cwd=work).stdout
    assert_machine(headers, arch)
    exports = runner.run("probe-exports", ["dumpbin", "/exports", str(dll)], cwd=work).stdout
    export_names = pe_export_names(exports)
    for name in EXPORT_ARGUMENT_BYTES:
        if name not in export_names:
            raise RuntimeError(f"missing PE export {name}")
    public = {name for name in export_names if name.startswith("archive_bridge_v1_")}
    if public != set(EXPORT_ARGUMENT_BYTES):
        raise RuntimeError(f"unexpected archive_bridge_v1 PE exports: {sorted(public)}")
    runner.run("c-caller-compile", ["cl", "/nologo", "/TC", "/Gr", "/W4", "/WX", "/Od", "/RTC1", str(work / "caller.c"), "/Fe:" + str(work / "c-caller.exe")], cwd=work)
    runner.run("c-caller-run", [str(work / "c-caller.exe"), str(dll.resolve())], cwd=work)
    target = "x86_64-pc-windows-msvc" if arch == "amd64" else "i686-pc-windows-msvc"
    runner.run("rust-caller-compile", ["rustc", "+1.97.1", "--target", target, str(work / "caller.rs"), "-L", "native=" + str(work), "-o", str(work / "rust-caller.exe")], cwd=work)
    runner.run("rust-caller-run", [str(work / "rust-caller.exe")], cwd=work)

    if arch == "amd64":
        mutations = {
            "export-without-call": header.replace("int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_handshake(", "int32_t archive_bridge_v1_handshake(", 1),
            "callback-stdcall": header.replace("(ARCHIVE_BRIDGE_V1_CALL *archive_bridge_v1_is_cancelled)", "(__stdcall *archive_bridge_v1_is_cancelled)", 1),
            "export-stdcall": header.replace("int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_close(", "int32_t __stdcall archive_bridge_v1_close(", 1),
        }
        for mutation, mutated_header in mutations.items():
            case = output / "work" / "amd64" / ("non-discriminator-" + mutation)
            write_sources(case, mutated_header)
            runner.run("amd64-nondiscriminator-" + mutation, ["cl", "/nologo", "/c", "/TC", "/Gr", "/W4", "/WX",
                str(case / "typecheck.c"), "/Fo" + str(case / "typecheck.obj")], cwd=case)
        (runner.evidence / "amd64-convention-collapse.txt").write_text(
            "PLATFORM_FACT: AMD64 accepted omitted/default, __stdcall, and __cdecl ordinary conventions; this is not negative-control evidence.\n",
            encoding="utf-8",
        )


def require_compile_failure(runner: EvidenceRunner, name: str, command: list[str], cwd: pathlib.Path) -> None:
    proc = runner.run(name, command, cwd=cwd, expected=None)
    if proc.returncode == 0:
        raise RuntimeError(f"negative control unexpectedly passed: {name}")
    if not re.search(r"\b(C2040|C2373|C2440|C4113|C4190)\b", proc.stdout):
        raise RuntimeError(f"negative control failed for an unrecognized reason: {name}")
    (runner.evidence / f"{name}-result.txt").write_text(
        f"EXPECTED_REJECTION: exit_code={proc.returncode}; incompatible calling convention diagnostic observed\n",
        encoding="utf-8",
    )


def require_runtime_failure(
    runner: EvidenceRunner,
    name: str,
    command: list[str],
    cwd: pathlib.Path,
    expected_exit: int,
    marker: str,
) -> None:
    proc = runner.run(name, command, cwd=cwd, expected=None)
    if proc.returncode != expected_exit or marker not in proc.stdout:
        raise RuntimeError(
            f"{name}: expected exit {expected_exit} and marker {marker!r}, "
            f"got exit {proc.returncode}"
        )
    (runner.evidence / f"{name}-result.txt").write_text(
        f"EXPECTED_RUNTIME_REJECTION: exit_code={expected_exit}; marker={marker}\n",
        encoding="utf-8",
    )


def runtime_negative_controls(output: pathlib.Path, runner: EvidenceRunner) -> None:
    base = output / "work" / "x86" / "runtime-negatives"
    base.mkdir(parents=True, exist_ok=True)

    # An omitted ARCHIVE_BRIDGE_V1_CALL inherits /Gr (__fastcall).  The caller
    # deliberately resolves the decorated name but calls through __cdecl; exact
    # argument sentinels make register/stack disagreement deterministic.
    fast_dll = base / "fastcall-dll.c"
    fast_caller = base / "fastcall-caller.c"
    fast_dll.write_text(
        "#include <windows.h>\n"
        "__declspec(dllexport) int __fastcall archive_bridge_v1_handshake(void *a, void *b) "
        "{ return a==(void*)0x11111111 && b==(void*)0x22222222 ? 901 : -901; }\n",
        encoding="utf-8",
    )
    fast_caller.write_text(
        "#include <windows.h>\n#include <rtcapi.h>\n#include <stdio.h>\n"
        "static int __cdecl rtc_handler(int t,const wchar_t*f,int l,const wchar_t*m,const wchar_t*fmt,...){(void)t;(void)f;(void)l;(void)m;(void)fmt;puts(\"EXPECTED_RTC_STACK_MISMATCH\");fflush(stdout);ExitProcess(85);return 0;}\n"
        "typedef int (__cdecl *fn)(void*,void*);\n"
        "int main(int n,char**v){ HMODULE m=n==2?LoadLibraryA(v[1]):0; "
        "union{FARPROC raw;fn typed;}u; u.raw=m?GetProcAddress(m,\"@archive_bridge_v1_handshake@8\"):0; fn f=u.typed; "
        "if(!f)return 2; _RTC_SetErrorFuncW(rtc_handler); if(f((void*)0x11111111,(void*)0x22222222)==-901){"
        "puts(\"EXPECTED_ARGUMENT_SENTINEL_MISMATCH\"); return 86;} return 3;}\n",
        encoding="utf-8",
    )
    runner.run("runtime-fastcall-dll", ["cl", "/nologo", "/TC", "/Gr", "/W4", "/WX", "/LD", str(fast_dll), "/Fe:" + str(base / "fastcall.dll")], cwd=base)
    fast_exports_text = runner.run("runtime-fastcall-exports", ["dumpbin", "/exports", str(base / "fastcall.dll")], cwd=base).stdout
    fast_exports = pe_export_names(fast_exports_text)
    if "@archive_bridge_v1_handshake@8" not in fast_exports or "archive_bridge_v1_handshake" in fast_exports:
        raise RuntimeError("fastcall mutation did not expose the expected decorated PE name")
    runner.run("runtime-fastcall-caller", ["cl", "/nologo", "/TC", "/Gd", "/W4", "/WX", "/Od", "/RTC1", str(fast_caller), "/Fe:" + str(base / "fastcall-caller.exe")], cwd=base)
    require_runtime_failure(runner, "runtime-fastcall-run", [str(base / "fastcall-caller.exe"), str(base / "fastcall.dll")], base, 86, "EXPECTED_ARGUMENT_SENTINEL_MISMATCH")

    rtc_handler = r'''
#include <windows.h>
#include <rtcapi.h>
#include <stdio.h>
static int __cdecl rtc_handler(int t,const wchar_t*f,int l,const wchar_t*m,const wchar_t*fmt,...){
  (void)t;(void)f;(void)l;(void)m;(void)fmt;
  puts("EXPECTED_RTC_STACK_MISMATCH"); fflush(stdout); ExitProcess(RTC_EXIT); return 0;
}
'''
    std_dll = base / "stdcall-dll.c"
    std_caller = base / "stdcall-caller.c"
    std_dll.write_text("#include <windows.h>\n__declspec(dllexport) int __stdcall archive_bridge_v1_close(void*a,unsigned __int64 b,unsigned __int64 c){return a!=0 && b!=0 && c!=0;}\n", encoding="utf-8")
    std_caller.write_text(
        rtc_handler.replace("RTC_EXIT", "87")
        + "typedef int (__cdecl *fn)(void*,unsigned __int64,unsigned __int64);\n"
          "int main(int n,char**v){ HMODULE m=n==2?LoadLibraryA(v[1]):0; union{FARPROC raw;fn typed;}u;u.raw=m?GetProcAddress(m,\"_archive_bridge_v1_close@20\"):0; if(!u.typed)return 2; _RTC_SetErrorFuncW(rtc_handler); (void)u.typed((void*)1,2,3); return 4;}\n",
        encoding="utf-8",
    )
    runner.run("runtime-stdcall-dll", ["cl", "/nologo", "/TC", "/Gz", "/W4", "/WX", "/LD", str(std_dll), "/Fe:" + str(base / "stdcall.dll")], cwd=base)
    std_exports_text = runner.run("runtime-stdcall-exports", ["dumpbin", "/exports", str(base / "stdcall.dll")], cwd=base).stdout
    std_exports = pe_export_names(std_exports_text)
    if "_archive_bridge_v1_close@20" not in std_exports or "archive_bridge_v1_close" in std_exports:
        raise RuntimeError("stdcall mutation did not expose the expected decorated PE name")
    runner.run("runtime-stdcall-caller", ["cl", "/nologo", "/TC", "/Gd", "/W4", "/WX", "/Od", "/RTC1", str(std_caller), "/Fe:" + str(base / "stdcall-caller.exe")], cwd=base)
    require_runtime_failure(runner, "runtime-stdcall-run", [str(base / "stdcall-caller.exe"), str(base / "stdcall.dll")], base, 87, "EXPECTED_RTC_STACK_MISMATCH")

    callback_dll = base / "callback-dll.c"
    callback_caller = base / "callback-caller.c"
    callback_dll.write_text(
        rtc_handler.replace("RTC_EXIT", "88")
        + "typedef unsigned (__stdcall *callback_fn)(void*);\n"
          "typedef struct operation { callback_fn callback; void *user; } operation;\n"
          "__declspec(dllexport) int __cdecl cc_probe_bad_callback(const operation*op){_RTC_SetErrorFuncW(rtc_handler); (void)op->callback(op->user); return 5;}\n",
        encoding="utf-8",
    )
    callback_caller.write_text(
        "#include <windows.h>\n"
        "typedef unsigned (__cdecl *cdecl_cb)(void*); typedef unsigned (__stdcall *stdcall_cb)(void*); "
        "typedef struct operation{stdcall_cb callback;void*user;}operation; "
        "typedef int (__cdecl *helper)(const operation*); "
        "static unsigned __cdecl cb(void*u){return u==(void*)0x1234;} "
        "int main(int n,char**v){HMODULE m=n==2?LoadLibraryA(v[1]):0;union{FARPROC raw;helper typed;}loader;union{cdecl_cb c;stdcall_cb s;}callback;operation op;loader.raw=m?GetProcAddress(m,\"cc_probe_bad_callback\"):0;if(!loader.typed)return 2;callback.c=cb;op.callback=callback.s;op.user=(void*)0x1234;(void)loader.typed(&op);return 6;}\n",
        encoding="utf-8",
    )
    runner.run("runtime-callback-dll", ["cl", "/nologo", "/TC", "/Gd", "/W4", "/WX", "/Od", "/RTC1", "/LD", str(callback_dll), "/Fe:" + str(base / "callback.dll")], cwd=base)
    runner.run("runtime-callback-caller", ["cl", "/nologo", "/TC", "/Gd", "/W4", "/WX", str(callback_caller), "/Fe:" + str(base / "callback-caller.exe")], cwd=base)
    require_runtime_failure(runner, "runtime-callback-run", [str(base / "callback-caller.exe"), str(base / "callback.dll")], base, 88, "EXPECTED_RTC_STACK_MISMATCH")


def negative_controls(root: pathlib.Path, output: pathlib.Path, runner: EvidenceRunner) -> None:
    original = (root / "docs/ai-migration/qualification/archive_bridge_v1.h").read_text(encoding="utf-8")
    mutations = {
        "export_without_call": original.replace("int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_handshake(", "int32_t archive_bridge_v1_handshake(", 1),
        "callback_stdcall": original.replace("(ARCHIVE_BRIDGE_V1_CALL *archive_bridge_v1_is_cancelled)", "(__stdcall *archive_bridge_v1_is_cancelled)", 1),
        "export_stdcall": original.replace("int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_close(", "int32_t __stdcall archive_bridge_v1_close(", 1),
    }
    for name, header in mutations.items():
        work = output / "work" / "x86" / name
        write_sources(work, header)
        require_compile_failure(runner, name + "-typecheck", ["cl", "/nologo", "/c", "/TC", "/Gr", "/W4", "/WX", str(work / "typecheck.c"), "/Fo" + str(work / "typecheck.obj")], work)
        source = definitions_source()
        if name == "export_without_call":
            source = source.replace("int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_handshake", "int32_t archive_bridge_v1_handshake", 1)
            wrong = "@archive_bridge_v1_handshake@8"
            correct = "_archive_bridge_v1_handshake"
        elif name == "export_stdcall":
            source = source.replace("int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_close", "int32_t __stdcall archive_bridge_v1_close", 1)
            wrong = "_archive_bridge_v1_close@20"
            correct = "_archive_bridge_v1_close"
        else:
            continue
        (work / "probe.cpp").write_text(source, encoding="utf-8")
        runner.run(name + "-compile", ["cl", "/nologo", "/c", "/TP", "/Gr", "/W4", "/WX", "/EHsc", str(work / "probe.cpp"), "/Fo" + str(work / "probe.obj")], cwd=work)
        dump = runner.run(name + "-symbols", ["dumpbin", "/symbols", str(work / "probe.obj")], cwd=work).stdout
        symbols = raw_symbols(dump)
        if wrong not in symbols or correct in symbols:
            raise RuntimeError(f"{name}: expected wrong symbol {wrong} and absence of {correct}")
        (runner.evidence / f"{name}-symbol-result.txt").write_text(f"EXPECTED_REJECTION: {wrong} observed; {correct} absent\n", encoding="utf-8")

    # A .def can normalize a wrong stdcall PE export, but cannot erase the raw
    # COFF evidence.  Build the evasion successfully, then reject its object.
    work = output / "work" / "x86" / "def_alias_evasion"
    work.mkdir(parents=True, exist_ok=True)
    (work / "alias.c").write_text("__declspec(dllexport) int __stdcall archive_bridge_v1_handshake(void *a, void *b) { return a != b; }\n", encoding="utf-8")
    (work / "alias.def").write_text("LIBRARY archive_bridge_v1_cc_probe_alias\nEXPORTS\n  archive_bridge_v1_handshake=_archive_bridge_v1_handshake@8\n", encoding="utf-8")
    runner.run("def-alias-compile", ["cl", "/nologo", "/c", "/TC", "/Gr", "/W4", "/WX", str(work / "alias.c"), "/Fo" + str(work / "alias.obj")], cwd=work)
    runner.run("def-alias-link", ["link", "/nologo", "/dll", "/noentry", str(work / "alias.obj"), "/def:" + str(work / "alias.def"), "/out:" + str(work / "alias.dll")], cwd=work)
    exports = runner.run("def-alias-exports", ["dumpbin", "/exports", str(work / "alias.dll")], cwd=work).stdout
    symbols_text = runner.run("def-alias-symbols", ["dumpbin", "/symbols", str(work / "alias.obj")], cwd=work).stdout
    symbols = raw_symbols(symbols_text)
    if "archive_bridge_v1_handshake" not in pe_export_names(exports):
        raise RuntimeError(".def evasion did not normalize the PE export as intended")
    if "_archive_bridge_v1_handshake@8" not in symbols or "_archive_bridge_v1_handshake" in symbols:
        raise RuntimeError("raw COFF validator did not reject .def alias evasion")
    (runner.evidence / "def-alias-evasion-result.txt").write_text(
        "EXPECTED_REJECTION: .def produced the public PE spelling, but raw COFF retained _archive_bridge_v1_handshake@8 and the cdecl object check rejected it.\n",
        encoding="utf-8",
    )

    # Mutate one real bridge-owned definition in a temporary copy only.  The
    # unchanged included production header should reject the conflicting
    # convention; if a compiler accepts it, the raw symbol must still expose
    # the inherited __fastcall spelling.
    current = output / "work" / "x86" / "current-source-mutation"
    current.mkdir(parents=True, exist_ok=True)
    source = (root / "rust/bridge/archive_bridge_v1.cpp").read_text(encoding="utf-8")
    needle = "int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_handshake("
    if source.count(needle) != 1:
        raise RuntimeError("current-source mutation anchor is not unique")
    (current / "archive_bridge_v1-mutated.cpp").write_text(
        source.replace(needle, "int32_t archive_bridge_v1_handshake(", 1), encoding="utf-8"
    )
    command = ["cl", "/nologo", "/c", "/TP", "/Gr", "/W4", "/WX", "/EHsc",
        "/DARCHIVE_BRIDGE_V1_HEADER_SHA256_HEX=\"" + FROZEN_HEADER_SHA256 + "\"",
        "/DARCHIVE_BRIDGE_V1_BUILD_SHA256_HEX=\"" + ("0" * 64) + "\"", "/I", str(root),
        "/I", str(root / "rust/bridge"), str(current / "archive_bridge_v1-mutated.cpp"),
        "/Fo" + str(current / "mutated.obj")]
    proc = runner.run("current-source-definition-mutation", command, cwd=current, expected=None)
    if proc.returncode == 0:
        dump = runner.run("current-source-definition-mutation-symbols", ["dumpbin", "/symbols", str(current / "mutated.obj")], cwd=current).stdout
        if "@archive_bridge_v1_handshake@8" not in raw_symbols(dump):
            raise RuntimeError("current-source definition mutation passed silently")
        outcome = "compiler accepted generated copy; raw COFF exposed @archive_bridge_v1_handshake@8"
    elif not re.search(r"\b(C2040|C2373|C2440|C4113|C4190)\b", proc.stdout):
        raise RuntimeError("current-source definition mutation failed for an unrecognized reason")
    else:
        outcome = f"compiler rejected conflicting convention; exit={proc.returncode}"
    (runner.evidence / "current-source-definition-mutation-result.txt").write_text(
        "EXPECTED_REJECTION: " + outcome + "\n", encoding="utf-8"
    )

    # Rust's i686 extern "system" is stdcall.  It must not link to the cdecl
    # import-library symbol generated by the positive probe.
    positive = output / "work" / "x86" / "positive"
    rust_bad = current / "rust-system-mutation.rs"
    rust_bad.write_text(
        '#[link(name="archive_bridge_v1_cc_probe")] extern "system" { '
        'fn archive_bridge_v1_handshake(a:*const u8,b:*mut u8)->i32; } '
        'fn main(){unsafe{let _=archive_bridge_v1_handshake(core::ptr::null(),core::ptr::null_mut());}}\n',
        encoding="utf-8",
    )
    proc = runner.run("rust-i686-system-mutation", ["rustc", "+1.97.1", "--target", "i686-pc-windows-msvc",
        str(rust_bad), "-L", "native=" + str(positive), "-o", str(current / "rust-system.exe")],
        cwd=current, expected=None)
    if proc.returncode == 0 or not re.search(r"LNK2019|unresolved external|undefined symbol", proc.stdout, re.IGNORECASE):
        raise RuntimeError("i686 Rust extern-system mutation was not rejected by static import/name resolution")
    (runner.evidence / "rust-i686-system-mutation-result.txt").write_text(
        f"EXPECTED_REJECTION: extern system could not link to cdecl import; exit={proc.returncode}\n",
        encoding="utf-8",
    )

    runtime_negative_controls(output, runner)


def guard_probe(root: pathlib.Path, output: pathlib.Path, runner: EvidenceRunner) -> None:
    cwd = root / "CPP/7zip/Bundles/Format7zF"
    command = ["nmake", "/NOLOGO", "/f", str(root / "rust/bridge/makefile"), "PLATFORM=x64", "O=" + str(output / "forbidden-facade-output")]
    proc = runner.run("retained-guard-probe", command, cwd=cwd, expected=None)
    if proc.returncode == 0 or "U1050" not in proc.stdout or "S2a-DEV performs no Windows facade build" not in proc.stdout:
        raise RuntimeError("retained facade guard did not fail closed with its exact U1050 outcome")
    if (output / "forbidden-facade-output").exists():
        raise RuntimeError("guard probe unexpectedly created facade output")


def tool_versions(runner: EvidenceRunner, work: pathlib.Path) -> None:
    for name, command in (("cl-version", ["cl"]), ("link-version", ["link"]), ("dumpbin-version", ["dumpbin"]),
                          ("rustc-version", ["rustc", "+1.97.1", "-vV"]), ("rust-targets", ["rustup", "target", "list", "--installed", "--toolchain", "1.97.1"])):
        proc = runner.run(name, command, cwd=work, expected=None)
        if name in ("rustc-version", "rust-targets") and proc.returncode != 0:
            raise RuntimeError(f"{name} failed")


def run_diagnostics_only(root: pathlib.Path, output: pathlib.Path, arch: str) -> None:
    """Collect every compile diagnostic for one architecture without running a lane."""
    evidence = output / "evidence" / arch
    runner = EvidenceRunner(evidence)
    validate_source_inputs(root)
    status = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    ).stdout
    if status:
        raise RuntimeError("qualification source checkout is not clean")
    machine = platform.machine().upper()
    processor = os.environ.get("PROCESSOR_ARCHITECTURE", "").upper()
    if machine not in ("AMD64", "X86_64") or processor != "AMD64":
        raise RuntimeError(
            f"runner must be AMD64: platform.machine={machine}, "
            f"PROCESSOR_ARCHITECTURE={processor}"
        )
    work = output / "work" / arch
    work.mkdir(parents=True, exist_ok=True)
    tool_versions(runner, work)
    compile_diagnostic_sweep(root, output, arch, runner)


def run_lane(root: pathlib.Path, output: pathlib.Path, arch: str) -> None:
    evidence = output / "evidence" / arch
    runner = EvidenceRunner(evidence)
    hashes = validate_source_inputs(root)
    status = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True).stdout
    if status:
        raise RuntimeError("qualification source checkout is not clean")
    source_commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True).stdout.strip()
    machine = platform.machine().upper()
    processor = os.environ.get("PROCESSOR_ARCHITECTURE", "").upper()
    if machine not in ("AMD64", "X86_64") or processor != "AMD64":
        raise RuntimeError(f"runner must be AMD64: platform.machine={machine}, PROCESSOR_ARCHITECTURE={processor}")
    work = output / "work" / arch
    work.mkdir(parents=True, exist_ok=True)
    tool_versions(runner, work)
    if arch == "amd64":
        guard_probe(root, output, runner)
    positive_lane(root, output, arch, runner)
    if arch == "x86":
        negative_controls(root, output, runner)
    runner.write_manifest({"schema": 1, "target_name": "msvc-abi-convention-probe", "not_product": True,
                           "architecture": arch, "runner_machine": machine, "processor_architecture": processor,
                           "source_commit": source_commit, "source_tree_clean": True, "hashes": hashes,
                           "target_inputs": ["docs/ai-migration/qualification/archive_bridge_v1.h",
                                             "rust/bridge/archive_bridge_v1.h",
                                             "rust/bridge/archive_bridge_v1.cpp",
                                             "rust/bridge/msvc-abi-convention-probe.py"],
                           "expected_export_argument_bytes": EXPORT_ARGUMENT_BYTES,
                           "expected_callback_argument_bytes": CALLBACK_ARGUMENT_BYTES,
                           "qualified_operations": 0,
                           "scope": "Calling-convention probe only; no retained facade build, archive operation, product artifact, package, signing, installation, registration, tag, release, or Windows qualification."})


def finalize(output: pathlib.Path) -> None:
    evidence = output / "evidence"
    for arch in ("amd64", "x86"):
        manifest = evidence / arch / "manifest.json"
        if not manifest.is_file():
            raise RuntimeError(f"missing lane manifest: {manifest}")
    runnable_suffixes = {".dll", ".exe", ".lib", ".exp", ".obj", ".pdb", ".ilk"}
    work = output / "work"
    if work.exists():
        for path in work.rglob("*"):
            if path.is_file() and path.suffix.lower() in runnable_suffixes:
                path.unlink()
    digest_lines = []
    for path in sorted(evidence.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            digest_lines.append(f"{sha256(path)}  {path.relative_to(evidence).as_posix()}")
    (evidence / "SHA256SUMS.txt").write_text("\n".join(digest_lines) + "\n", encoding="utf-8")
    summary = (
        "MSVC ABI convention qualification (non-product)\n"
        "AMD64 normative lane: PASS\n"
        "x86 compiler-semantic diagnostic lane (not a product target): PASS\n"
        "Failure injection: omitted call macro, callback __stdcall, export __stdcall, and .def alias evasion all rejected.\n"
        "The retained facade was not built. The fail-closed !ERROR guard remains authoritative.\n"
        "Windows facade qualification remains unauthorized and qualified_operations is 0.\n"
        "This evidence does not qualify archive semantics, codecs, encryption, passwords, filesystem behavior, lifetimes, cancellation, registration, GUI, packaging, or release behavior.\n"
    )
    (evidence / "SUMMARY.txt").write_text(summary, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=pathlib.Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--arch", choices=("amd64", "x86"))
    group.add_argument("--diagnostics-only", choices=("amd64", "x86"))
    group.add_argument("--finalize", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    if args.finalize:
        finalize(output)
    elif args.diagnostics_only:
        run_diagnostics_only(root, output, args.diagnostics_only)
    else:
        run_lane(root, output, args.arch)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise
