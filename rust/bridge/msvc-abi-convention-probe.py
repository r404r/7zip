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
from typing import Any, Iterable

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
GENERATED_HEADER_PREAMBLE = (
    "/* Build-time non-product probe header.  The validator requires this file to\n"
    " * equal the frozen Q1 header after removing only the eight dllexport markers. */\n"
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


def generated_probe_header(frozen: str) -> str:
    """Add direct probe-only exports without changing the frozen artifact."""
    generated = frozen
    for name in EXPORT_ARGUMENT_BYTES:
        declaration = generated.find(name + "(")
        if declaration < 0 or generated.find(name + "(", declaration + 1) >= 0:
            raise RuntimeError(f"frozen export declaration is missing or ambiguous: {name}")
        line_start = generated.rfind("\n", 0, declaration) + 1
        if not generated.startswith("int32_t ", line_start):
            raise RuntimeError(f"unexpected frozen export declaration shape: {name}")
        generated = (
            generated[:line_start]
            + "__declspec(dllexport) "
            + generated[line_start:]
        )
    result = GENERATED_HEADER_PREAMBLE + generated
    validate_generated_probe_header(frozen, result)
    return result


def validate_generated_probe_header(frozen: str, generated: str) -> None:
    """Prove the generated declaration view differs only by export attributes."""
    if not generated.startswith(GENERATED_HEADER_PREAMBLE):
        raise RuntimeError("generated probe header lacks its build-time non-product marker")
    restored = generated[len(GENERATED_HEADER_PREAMBLE):]
    for name in EXPORT_ARGUMENT_BYTES:
        declaration = restored.find(name + "(")
        if declaration < 0 or restored.find(name + "(", declaration + 1) >= 0:
            raise RuntimeError(f"generated export declaration is missing or ambiguous: {name}")
        line_start = restored.rfind("\n", 0, declaration) + 1
        marker = "__declspec(dllexport) "
        if not restored.startswith(marker, line_start):
            raise RuntimeError(f"generated export lacks direct dllexport: {name}")
        restored = restored[:line_start] + restored[line_start + len(marker):]
    if "__declspec(dllexport)" in restored:
        raise RuntimeError("generated probe header contains an unexpected dllexport")
    if restored != frozen:
        raise RuntimeError(
            "generated probe header drifted from the frozen header beyond export attributes"
        )


def contract_header_mutation_fixture() -> str:
    return """#ifndef ARCHIVE_BRIDGE_V1_H
#define ARCHIVE_BRIDGE_V1_H
#include <stdint.h>
#define ARCHIVE_BRIDGE_V1_CALL __cdecl
typedef unsigned (ARCHIVE_BRIDGE_V1_CALL *archive_bridge_v1_is_cancelled)(void *);
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_handshake(void *, void *);
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_close(void *, unsigned long long, unsigned long long);
#endif
"""


def build_mutations(source: str) -> dict[str, str]:
    without_call = source.replace(
        "int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_handshake",
        "int32_t archive_bridge_v1_handshake",
        1,
    )
    callback_stdcall = source.replace(
        "(ARCHIVE_BRIDGE_V1_CALL *archive_bridge_v1_is_cancelled)",
        "(__stdcall *archive_bridge_v1_is_cancelled)",
        1,
    )
    close_stdcall = source.replace(
        "int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_close",
        "int32_t __stdcall archive_bridge_v1_close",
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
        self.artifact_audit: dict[str, dict[str, object]] = {}
        self.acceptance_tables: dict[str, object] = {}
        self.state_path = self.evidence / "runner-state.json"
        if self.state_path.is_file():
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
            self.commands = list(state.get("commands", []))
            self.artifact_audit = dict(state.get("artifact_audit", {}))
            self.acceptance_tables = dict(state.get("acceptance_tables", {}))

    def save_state(self) -> None:
        self.state_path.write_text(
            json.dumps(
                {
                    "commands": self.commands,
                    "artifact_audit": self.artifact_audit,
                    "acceptance_tables": self.acceptance_tables,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

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
        self.save_state()
        if expected is not None and proc.returncode != expected:
            raise RuntimeError(f"{name}: expected exit {expected}, got {proc.returncode}; see {log}")
        return proc

    def write_manifest(self, extra: dict[str, object]) -> None:
        payload = dict(extra)
        payload["commands"] = self.commands
        payload["artifact_audit"] = self.artifact_audit
        payload["acceptance_tables"] = self.acceptance_tables
        (self.evidence / "manifest.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )


def definitions_source() -> str:
    return r'''#include "archive_bridge_v1_probe_exports.h"
#include <stdint.h>
extern "C" {
__declspec(dllexport) extern const char cc_probe_not_product[] = "NOT_PRODUCT";
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_handshake(const archive_bridge_v1_info *a, archive_bridge_v1_info *b) { return a==(void*)(uintptr_t)0x10101010 && b==(void*)(uintptr_t)0x20202020 ? 101 : -101; }
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_create_context(const archive_bridge_v1_context_options *a, archive_bridge_v1_context **b) { return a==(void*)(uintptr_t)0x30303030 && b==(void*)(uintptr_t)0x40404040 ? 102 : -102; }
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_destroy_context(archive_bridge_v1_context *a) { return a==(void*)(uintptr_t)0x50505050 ? 103 : -103; }
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_capabilities(archive_bridge_v1_context *a, archive_bridge_v1_result **b, archive_bridge_v1_capability_view *c) { return a==(void*)(uintptr_t)0x60606060 && b==(void*)(uintptr_t)0x70707070 && c==(void*)(uintptr_t)0x80808080 ? 104 : -104; }
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_open(archive_bridge_v1_context *a, const archive_bridge_v1_open_request *b, const archive_bridge_v1_operation *c, archive_bridge_v1_result **d, archive_bridge_v1_view *e) { return a==(void*)(uintptr_t)0x11111111 && b==(void*)(uintptr_t)0x22222222 && c==(void*)(uintptr_t)0x33333333 && d==(void*)(uintptr_t)0x44444444 && e==(void*)(uintptr_t)0x55555555 ? 105 : -105; }
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_entries(archive_bridge_v1_context *a, const archive_bridge_v1_entries_request *b, const archive_bridge_v1_operation *c, archive_bridge_v1_result **d, archive_bridge_v1_view *e) { return a==(void*)(uintptr_t)0x12121212 && b==(void*)(uintptr_t)0x23232323 && c==(void*)(uintptr_t)0x34343434 && d==(void*)(uintptr_t)0x45454545 && e==(void*)(uintptr_t)0x56565656 ? 106 : -106; }
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_close(archive_bridge_v1_context *a, uint64_t b, uint64_t c) { return a==(void*)(uintptr_t)0x67676767 && b==UINT64_C(0x1122334455667788) && c==UINT64_C(0x8877665544332211) ? 107 : -107; }
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_result_destroy(archive_bridge_v1_context *a, archive_bridge_v1_result *b) { return a==(void*)(uintptr_t)0x78787878 && b==(void*)(uintptr_t)0x89898989 ? 108 : -108; }
__declspec(dllexport) int32_t ARCHIVE_BRIDGE_V1_CALL cc_probe_invoke_callbacks(const archive_bridge_v1_operation *op) {
  archive_bridge_v1_progress progress; archive_bridge_v1_question question; archive_bridge_v1_reply reply;
  progress.counter_kind = 0x7011; question.kind = 0x7022; reply.kind = 0;
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
int __cdecl main(void) { return !(c1 && c2 && c3 && c4 && c5 && c6 && c7 && c8 && cb1 && cb2 && cb3); }
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
int __cdecl main() { return 0; }
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
int __cdecl main(int argc, char **argv) {
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
    return set(pe_exports(text))


def pe_exports(text: str) -> dict[str, str | None]:
    """Parse PE public names separately from DUMPBIN's optional internal target."""
    exports: dict[str, str | None] = {}
    for line in text.splitlines():
        match = re.match(
            r"^\s+\d+\s+[0-9A-Fa-f]+\s+[0-9A-Fa-f]+\s+(\S+)(?:\s+=\s+(\S+))?\s*$",
            line,
        )
        if match:
            name, internal = match.groups()
            if name in exports and exports[name] != internal:
                raise RuntimeError(f"duplicate PE export has conflicting targets: {name}")
            exports[name] = internal
    return exports


def machine_value(text: str) -> str:
    match = re.search(r"^\s*(8664|14C)\s+machine\s+\((x64|x86)\)\s*$", text, re.MULTILINE | re.IGNORECASE)
    if not match:
        raise RuntimeError("DUMPBIN headers lack a recognized machine field")
    return match.group(1).upper()


def assert_machine(text: str, arch: str) -> str:
    expected = "8664" if arch == "amd64" else "14C"
    actual = machine_value(text)
    if actual != expected:
        raise RuntimeError(f"DUMPBIN machine mismatch: expected {expected}, got {actual}")
    return actual


def convention_symbols(symbols: Iterable[str], names: Iterable[str]) -> set[str]:
    """Collect every ordinary/x86-decorated spelling in the controlled namespace."""
    controlled = tuple(names)
    found: set[str] = set()
    for symbol in symbols:
        for name in controlled:
            if symbol == name or symbol == "_" + name:
                found.add(symbol)
                break
            if re.fullmatch(r"@" + re.escape(name) + r"@\d+", symbol):
                found.add(symbol)
                break
            if re.fullmatch(r"_" + re.escape(name) + r"@\d+", symbol):
                found.add(symbol)
                break
    return found


def bridge_namespace_symbols(symbols: Iterable[str]) -> set[str]:
    """Collect plain and x86-decorated names in the Q1 public namespace."""
    found: set[str] = set()
    for symbol in symbols:
        if symbol.startswith("?archive_bridge_v1_"):
            found.add(symbol)
            continue
        base = symbol
        if base.startswith(("@", "_")):
            base = base[1:]
        base = re.sub(r"@\d+$", "", base)
        if base.startswith("archive_bridge_v1_"):
            found.add(symbol)
    return found


def assert_object_symbols(text: str, arch: str, names: Iterable[str]) -> dict[str, str]:
    controlled = tuple(names)
    expected = {expected_coff_symbol(arch, name) for name in controlled}
    parsed = raw_symbols(text)
    actual = convention_symbols(parsed, controlled)
    if any(name.startswith("archive_bridge_v1_") for name in controlled):
        actual |= bridge_namespace_symbols(parsed)
    if actual != expected:
        raise RuntimeError(
            "raw COFF symbol set mismatch: "
            f"missing={sorted(expected - actual)} extra={sorted(actual - expected)}"
        )
    return {
        name: expected_coff_symbol(arch, name)
        for name in controlled
    }


def audit_artifact(
    runner: EvidenceRunner,
    name: str,
    path: pathlib.Path,
    arch: str,
    *,
    symbols: bool,
) -> dict[str, object]:
    """Retain and validate headers plus, for objects, literal raw symbols."""
    headers_text = runner.run(name + "-headers", ["dumpbin", "/headers", str(path)], cwd=path.parent).stdout
    record: dict[str, object] = {
        "path": str(path),
        "kind": "object" if path.suffix.lower() == ".obj" else "dll",
        "machine": assert_machine(headers_text, arch),
        "headers_log": name + "-headers.log",
    }
    if symbols:
        symbols_text = runner.run(name + "-symbols", ["dumpbin", "/symbols", str(path)], cwd=path.parent).stdout
        record["symbols_log"] = name + "-symbols.log"
        record["defined_symbols"] = sorted(defined_symbols(symbols_text))
    runner.artifact_audit[str(path.resolve())] = record
    runner.save_state()
    return record


def assert_complete_artifact_audit(
    work_root: pathlib.Path,
    runner: EvidenceRunner,
    arch: str,
) -> None:
    expected_machine = "8664" if arch == "amd64" else "14C"
    artifacts = sorted(
        path.resolve()
        for path in work_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".obj", ".dll"}
    )
    missing = [str(path) for path in artifacts if str(path) not in runner.artifact_audit]
    if missing:
        raise RuntimeError(f"artifact audit is missing object/DLL records: {missing}")
    incomplete = []
    for path in artifacts:
        record = runner.artifact_audit[str(path)]
        headers_log = record.get("headers_log")
        symbols_log = record.get("symbols_log")
        if not headers_log or not (runner.evidence / str(headers_log)).is_file():
            incomplete.append(str(path) + ":headers")
        if path.suffix.lower() == ".obj" and (
            not symbols_log or not (runner.evidence / str(symbols_log)).is_file()
        ):
            incomplete.append(str(path) + ":symbols")
    if incomplete:
        raise RuntimeError(f"artifact audit is missing header/symbol records: {incomplete}")
    wrong = [
        str(path)
        for path in artifacts
        if runner.artifact_audit[str(path)]["machine"] != expected_machine
    ]
    if wrong:
        raise RuntimeError(f"artifact audit contains wrong machine values: {wrong}")


def assert_acceptance_tables(tables: dict[str, object], arch: str) -> None:
    expected_exports = {
        name: expected_coff_symbol(arch, name) for name in EXPORT_ARGUMENT_BYTES
    }
    expected_callbacks = {
        name: expected_coff_symbol(arch, name) for name in CALLBACK_ARGUMENT_BYTES
    }
    if tables.get("export_coff_expected") != expected_exports:
        raise RuntimeError("acceptance record export expected COFF table is incomplete")
    if tables.get("export_coff_actual") != expected_exports:
        raise RuntimeError("acceptance record export actual COFF table differs")
    if tables.get("callback_coff_expected") != expected_callbacks:
        raise RuntimeError("acceptance record callback expected COFF table is incomplete")
    if tables.get("callback_coff_actual") != expected_callbacks:
        raise RuntimeError("acceptance record callback actual COFF table differs")
    expected_pe = {
        name: {
            "public_name": name,
            "allowed_internal_targets": [None, expected_coff_symbol(arch, name)],
        }
        for name in EXPORT_ARGUMENT_BYTES
    }
    actual_pe = tables.get("export_pe_actual")
    if tables.get("export_pe_expected") != expected_pe or not isinstance(actual_pe, dict):
        raise RuntimeError("acceptance record PE export tables are incomplete")
    if set(actual_pe) != set(expected_pe):
        raise RuntimeError("acceptance record PE export actual table has missing/extra entries")
    for name, expected in expected_pe.items():
        actual = actual_pe[name]
        if not isinstance(actual, dict) or actual.get("public_name") != name:
            raise RuntimeError(f"acceptance record PE public name differs: {name}")
        if actual.get("internal_target") not in expected["allowed_internal_targets"]:
            raise RuntimeError(f"acceptance record PE internal target differs: {name}")
    callbacks_pe = tables.get("callback_pe_exports")
    if callbacks_pe != {name: "not_applicable_static_target" for name in CALLBACK_ARGUMENT_BYTES}:
        raise RuntimeError("acceptance record callback PE applicability is incomplete")


def assert_def_alias_evasion(exports_text: str, symbols_text: str) -> str:
    """Prove PE normalization hid the wrong public spelling but COFF caught it."""
    controlled_exports = {
        name: internal
        for name, internal in pe_exports(exports_text).items()
        if bridge_namespace_symbols({name})
    }
    if set(controlled_exports) != {"archive_bridge_v1_handshake"}:
        raise RuntimeError(
            ".def evasion did not hide the decorated PE name exactly: "
            f"{controlled_exports}"
        )
    alias_internal = controlled_exports["archive_bridge_v1_handshake"]
    if alias_internal not in (None, "_archive_bridge_v1_handshake@8"):
        raise RuntimeError(f".def evasion exposed an unexpected internal target: {alias_internal}")
    try:
        assert_object_symbols(
            symbols_text,
            "x86",
            {"archive_bridge_v1_handshake"},
        )
    except RuntimeError as error:
        rejection = str(error)
        if "_archive_bridge_v1_handshake@8" not in rejection:
            raise RuntimeError("raw COFF rejection omitted the wrong stdcall symbol") from error
        return rejection
    raise RuntimeError("raw COFF exact checker accepted .def alias evasion")


def write_sources(work: pathlib.Path, header: str) -> str:
    work.mkdir(parents=True, exist_ok=True)
    generated_header = generated_probe_header(header)
    # Consumers and type checks use the exact frozen declaration view.  Only the
    # probe DLL definition unit includes the build-time export-decorated view;
    # otherwise dllexport directives would leak into the dynamic C caller.
    (work / "archive_bridge_v1.h").write_text(header, encoding="utf-8")
    (work / "archive_bridge_v1_probe_exports.h").write_text(
        generated_header, encoding="utf-8"
    )
    (work / "probe.cpp").write_text(definitions_source(), encoding="utf-8")
    (work / "typecheck.c").write_text(typecheck_source(), encoding="utf-8")
    (work / "typecheck.cpp").write_text(cpp_typecheck_source(), encoding="utf-8")
    (work / "caller.c").write_text(c_caller_source(), encoding="utf-8")
    (work / "caller.rs").write_text(rust_caller_source(), encoding="utf-8")
    return generated_header


def record_generated_header_contract(
    frozen: str,
    generated: str,
    runner: EvidenceRunner,
    *,
    run_negative_controls: bool,
) -> None:
    validate_generated_probe_header(frozen, generated)
    evidence: dict[str, object] = {
        "relationship": (
            "byte-identical to the frozen Q1 header after removing the build-time "
            "marker and exactly eight direct __declspec(dllexport) attributes"
        ),
        "frozen_header_sha256": hashlib.sha256(frozen.encode("utf-8")).hexdigest(),
        "generated_header_sha256": hashlib.sha256(generated.encode("utf-8")).hexdigest(),
        "exports": list(EXPORT_ARGUMENT_BYTES),
        "callback_typedefs": [
            "archive_bridge_v1_is_cancelled",
            "archive_bridge_v1_on_progress",
            "archive_bridge_v1_ask",
        ],
        "positive_check": "PASS",
    }
    if run_negative_controls:
        marker = "__declspec(dllexport) "
        mutations = {
            "parameter_type_drift": generated.replace(
                "const archive_bridge_v1_info *expected",
                "const void *expected",
                1,
            ),
            "missing_export": generated.replace(
                marker + "int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_handshake(",
                "int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_handshake(",
                1,
            ),
            "missing_call_macro": generated.replace(
                marker + "int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_close(",
                marker + "int32_t archive_bridge_v1_close(",
                1,
            ),
        }
        results: dict[str, str] = {}
        for name, mutated in mutations.items():
            if mutated == generated:
                raise RuntimeError(f"generated-header negative control did not mutate: {name}")
            try:
                validate_generated_probe_header(frozen, mutated)
            except RuntimeError as error:
                results[name] = f"EXPECTED_REJECTION: {error}"
            else:
                raise RuntimeError(
                    f"generated-header structural validator accepted drift: {name}"
                )
        evidence["negative_controls"] = results
    (runner.evidence / "generated-probe-header-contract.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


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
            work / "current-source.obj",
        ),
        (
            "diagnostic-typecheck-c",
            ["cl", "/nologo", "/c", "/TC", "/Gr", "/W4", "/WX",
             str(work / "typecheck.c"), "/Fo" + str(work / "typecheck-c.obj")],
            work / "typecheck-c.obj",
        ),
        (
            "diagnostic-typecheck-cpp",
            ["cl", "/nologo", "/c", "/TP", "/Gr", "/W4", "/WX", "/EHsc",
             str(work / "typecheck.cpp"), "/Fo" + str(work / "typecheck-cpp.obj")],
            work / "typecheck-cpp.obj",
        ),
        (
            "diagnostic-probe",
            ["cl", "/nologo", "/c", "/TP", "/Gr", "/W4", "/WX", "/EHsc",
             str(work / "probe.cpp"), "/Fo" + str(work / "probe.obj")],
            work / "probe.obj",
        ),
        (
            "diagnostic-c-caller",
            ["cl", "/nologo", "/c", "/TC", "/Gr", "/W4", "/WX", "/Od", "/RTC1",
             str(work / "caller.c"), "/Fo" + str(work / "caller.obj")],
            work / "caller.obj",
        ),
    )
    failures: list[str] = []
    summary: list[str] = []
    for name, command, artifact in commands:
        proc = runner.run(name, command, cwd=work, expected=None)
        diagnostics = sorted(set(re.findall(r"\bC\d{4}\b", proc.stdout)))
        diagnostic_text = ",".join(diagnostics) if diagnostics else "none"
        summary.append(f"{name}: exit_code={proc.returncode}; diagnostics={diagnostic_text}")
        if proc.returncode != 0:
            failures.append(f"{name} [{diagnostic_text}]")
        elif artifact.is_file():
            audit_artifact(runner, name, artifact, arch, symbols=True)
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
    audit_artifact(runner, "current-source", obj, arch, symbols=True)
    symbols = (runner.evidence / "current-source-symbols.log").read_text(encoding="utf-8")
    assert_object_symbols(symbols, arch, CURRENT_EXPORTS)


def positive_lane(root: pathlib.Path, output: pathlib.Path, arch: str, runner: EvidenceRunner) -> None:
    work = output / "work" / arch / "positive"
    header = (root / "docs/ai-migration/qualification/archive_bridge_v1.h").read_text(encoding="utf-8")
    generated_header = write_sources(work, header)
    record_generated_header_contract(
        header,
        generated_header,
        runner,
        run_negative_controls=arch == "amd64",
    )
    compile_current_source(root, work, arch, runner)
    typecheck_c = work / "typecheck-c.obj"
    typecheck_cpp = work / "typecheck-cpp.obj"
    runner.run("typecheck-c", ["cl", "/nologo", "/c", "/TC", "/Gr", "/W4", "/WX", str(work / "typecheck.c"), "/Fo" + str(typecheck_c)], cwd=work)
    runner.run("typecheck-cpp", ["cl", "/nologo", "/c", "/TP", "/Gr", "/W4", "/WX", "/EHsc", str(work / "typecheck.cpp"), "/Fo" + str(typecheck_cpp)], cwd=work)
    for name, artifact in (("typecheck-c", typecheck_c), ("typecheck-cpp", typecheck_cpp)):
        audit_artifact(runner, name, artifact, arch, symbols=True)
    callback_dump = (runner.evidence / "typecheck-c-symbols.log").read_text(encoding="utf-8")
    callback_symbols = defined_symbols(callback_dump)
    expected_callbacks = {expected_coff_symbol(arch, name) for name in CALLBACK_ARGUMENT_BYTES}
    actual_callbacks = convention_symbols(callback_symbols, CALLBACK_ARGUMENT_BYTES)
    if actual_callbacks != expected_callbacks:
        raise RuntimeError(
            "callback target COFF symbol set mismatch: "
            f"missing={sorted(expected_callbacks - actual_callbacks)} "
            f"extra={sorted(actual_callbacks - expected_callbacks)}"
        )
    probe_obj = work / "probe.obj"
    runner.run("probe-compile", ["cl", "/nologo", "/c", "/TP", "/Gr", "/W4", "/WX", "/EHsc", str(work / "probe.cpp"), "/Fo" + str(probe_obj)], cwd=work)
    audit_artifact(runner, "probe", probe_obj, arch, symbols=True)
    symbols = (runner.evidence / "probe-symbols.log").read_text(encoding="utf-8")
    actual_export_coff = assert_object_symbols(symbols, arch, EXPORT_ARGUMENT_BYTES)
    dll = work / "archive_bridge_v1_cc_probe.dll"
    lib = work / "archive_bridge_v1_cc_probe.lib"
    runner.run("probe-link", ["link", "/nologo", "/dll", "/noentry", str(probe_obj), "/out:" + str(dll), "/implib:" + str(lib)], cwd=work)
    audit_artifact(runner, "probe-dll", dll, arch, symbols=False)
    exports = runner.run("probe-exports", ["dumpbin", "/exports", str(dll)], cwd=work).stdout
    parsed_exports = pe_exports(exports)
    controlled_pe = {
        name: internal
        for name, internal in parsed_exports.items()
        if bridge_namespace_symbols({name})
    }
    if set(controlled_pe) != set(EXPORT_ARGUMENT_BYTES):
        raise RuntimeError(
            "archive_bridge_v1 PE export set mismatch: "
            f"missing={sorted(set(EXPORT_ARGUMENT_BYTES) - set(controlled_pe))} "
            f"extra={sorted(set(controlled_pe) - set(EXPORT_ARGUMENT_BYTES))}"
        )
    runner.acceptance_tables = {
        "export_coff_expected": {
            name: expected_coff_symbol(arch, name) for name in EXPORT_ARGUMENT_BYTES
        },
        "export_coff_actual": actual_export_coff,
        "export_pe_expected": {
            name: {
                "public_name": name,
                "allowed_internal_targets": [None, expected_coff_symbol(arch, name)],
            }
            for name in EXPORT_ARGUMENT_BYTES
        },
        "export_pe_actual": {
            name: {"public_name": name, "internal_target": internal}
            for name, internal in controlled_pe.items()
        },
        "callback_coff_expected": {
            name: expected_coff_symbol(arch, name) for name in CALLBACK_ARGUMENT_BYTES
        },
        "callback_coff_actual": {
            name: expected_coff_symbol(arch, name) for name in CALLBACK_ARGUMENT_BYTES
        },
        "callback_pe_exports": {
            name: "not_applicable_static_target" for name in CALLBACK_ARGUMENT_BYTES
        },
        "machine": "8664" if arch == "amd64" else "14C",
    }
    assert_acceptance_tables(runner.acceptance_tables, arch)
    caller_obj = work / "c-caller.obj"
    runner.run("c-caller-compile", ["cl", "/nologo", "/c", "/TC", "/Gr", "/W4", "/WX", "/Od", "/RTC1", str(work / "caller.c"), "/Fo" + str(caller_obj)], cwd=work)
    audit_artifact(runner, "c-caller", caller_obj, arch, symbols=True)
    runner.run("c-caller-link", ["link", "/nologo", str(caller_obj), "/out:" + str(work / "c-caller.exe")], cwd=work)
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
            audit_artifact(
                runner,
                "amd64-nondiscriminator-" + mutation,
                case / "typecheck.obj",
                arch,
                symbols=True,
            )
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


def rtc_handler_source(exit_code: int) -> str:
    """Generate an RTC handler whose required return remains compiler-reachable."""
    return f'''#include <windows.h>
#include <rtcapi.h>
#include <stdio.h>
typedef void (WINAPI *exit_process_fn)(UINT);
static int __cdecl rtc_handler(int t,const wchar_t*f,int l,const wchar_t*m,const wchar_t*fmt,...){{
  exit_process_fn exit_process = ExitProcess;
  (void)t;(void)f;(void)l;(void)m;(void)fmt;
  puts("EXPECTED_RTC_STACK_MISMATCH"); fflush(stdout); exit_process({exit_code}); return 0;
}}
'''


def runtime_negative_compile_diagnostic_sweep(
    base: pathlib.Path, runner: EvidenceRunner, arch: str = "x86"
) -> None:
    """Compile every runtime-negative translation unit before formal execution."""
    commands = (
        ("runtime-diagnostic-fastcall-dll", ["cl", "/nologo", "/c", "/TC", "/Gr", "/W4", "/WX", str(base / "fastcall-dll.c"), "/Fo" + str(base / "diagnostic-fastcall-dll.obj")], base / "diagnostic-fastcall-dll.obj"),
        ("runtime-diagnostic-fastcall-caller", ["cl", "/nologo", "/c", "/TC", "/Gd", "/W4", "/WX", "/Od", "/RTC1", str(base / "fastcall-caller.c"), "/Fo" + str(base / "diagnostic-fastcall-caller.obj")], base / "diagnostic-fastcall-caller.obj"),
        ("runtime-diagnostic-stdcall-dll", ["cl", "/nologo", "/c", "/TC", "/Gz", "/W4", "/WX", str(base / "stdcall-dll.c"), "/Fo" + str(base / "diagnostic-stdcall-dll.obj")], base / "diagnostic-stdcall-dll.obj"),
        ("runtime-diagnostic-stdcall-caller", ["cl", "/nologo", "/c", "/TC", "/Gd", "/W4", "/WX", "/Od", "/RTC1", str(base / "stdcall-caller.c"), "/Fo" + str(base / "diagnostic-stdcall-caller.obj")], base / "diagnostic-stdcall-caller.obj"),
        ("runtime-diagnostic-callback-dll", ["cl", "/nologo", "/c", "/TC", "/Gd", "/W4", "/WX", "/Od", "/RTC1", str(base / "callback-dll.c"), "/Fo" + str(base / "diagnostic-callback-dll.obj")], base / "diagnostic-callback-dll.obj"),
        ("runtime-diagnostic-callback-caller", ["cl", "/nologo", "/c", "/TC", "/Gd", "/W4", "/WX", str(base / "callback-caller.c"), "/Fo" + str(base / "diagnostic-callback-caller.obj")], base / "diagnostic-callback-caller.obj"),
    )
    failures: list[str] = []
    summary: list[str] = []
    for name, command, artifact in commands:
        proc = runner.run(name, command, cwd=base, expected=None)
        diagnostics = sorted(set(re.findall(r"\bC\d{4}\b", proc.stdout)))
        diagnostic_text = ",".join(diagnostics) if diagnostics else "none"
        summary.append(f"{name}: exit_code={proc.returncode}; diagnostics={diagnostic_text}")
        if proc.returncode != 0:
            failures.append(f"{name} [{diagnostic_text}]")
        elif artifact.is_file():
            audit_artifact(runner, name, artifact, arch, symbols=True)
    (runner.evidence / "runtime-negative-compile-diagnostic-summary.txt").write_text(
        "\n".join(summary) + "\n", encoding="utf-8"
    )
    if failures:
        raise RuntimeError(
            "runtime negative compile diagnostic sweep failed after all translation units: "
            + "; ".join(failures)
        )


def runtime_negative_controls(output: pathlib.Path, runner: EvidenceRunner) -> None:
    base = output / "work" / "x86" / "runtime-negatives"
    base.mkdir(parents=True, exist_ok=True)

    # An omitted ARCHIVE_BRIDGE_V1_CALL inherits /Gr (__fastcall).  The caller
    # deliberately resolves the decorated name but calls through __cdecl; exact
    # argument sentinels make register/stack disagreement deterministic.
    (base / "fastcall-dll.c").write_text(
        "#include <windows.h>\n"
        "__declspec(dllexport) int __fastcall archive_bridge_v1_handshake(void *a, void *b) "
        "{ return a==(void*)0x11111111 && b==(void*)0x22222222 ? 901 : -901; }\n",
        encoding="utf-8",
    )
    (base / "fastcall-caller.c").write_text(
        rtc_handler_source(85)
        + "typedef int (__cdecl *fn)(void*,void*);\n"
        "int main(int n,char**v){ HMODULE m=n==2?LoadLibraryA(v[1]):0; "
        "union{FARPROC raw;fn typed;}u; u.raw=m?GetProcAddress(m,\"@archive_bridge_v1_handshake@8\"):0; fn f=u.typed; "
        "if(!f)return 2; _RTC_SetErrorFuncW(rtc_handler); if(f((void*)0x11111111,(void*)0x22222222)==-901){"
        "puts(\"EXPECTED_ARGUMENT_SENTINEL_MISMATCH\"); return 86;} return 3;}\n",
        encoding="utf-8",
    )
    (base / "stdcall-dll.c").write_text("#include <windows.h>\n__declspec(dllexport) int __stdcall archive_bridge_v1_close(void*a,unsigned __int64 b,unsigned __int64 c){return a!=0 && b!=0 && c!=0;}\n", encoding="utf-8")
    (base / "stdcall-caller.c").write_text(
        rtc_handler_source(87)
        + "typedef int (__cdecl *fn)(void*,unsigned __int64,unsigned __int64);\n"
          "int main(int n,char**v){ HMODULE m=n==2?LoadLibraryA(v[1]):0; union{FARPROC raw;fn typed;}u;u.raw=m?GetProcAddress(m,\"_archive_bridge_v1_close@20\"):0; if(!u.typed)return 2; _RTC_SetErrorFuncW(rtc_handler); (void)u.typed((void*)1,2,3); return 4;}\n",
        encoding="utf-8",
    )
    (base / "callback-dll.c").write_text(
        rtc_handler_source(88)
        + "typedef unsigned (__stdcall *callback_fn)(void*);\n"
          "typedef struct operation { callback_fn callback; void *user; } operation;\n"
          "__declspec(dllexport) int __cdecl cc_probe_bad_callback(const operation*op){_RTC_SetErrorFuncW(rtc_handler); (void)op->callback(op->user); return 5;}\n",
        encoding="utf-8",
    )
    (base / "callback-caller.c").write_text(
        "#include <windows.h>\n"
        "typedef unsigned (__cdecl *cdecl_cb)(void*); typedef unsigned (__stdcall *stdcall_cb)(void*); "
        "typedef struct operation{stdcall_cb callback;void*user;}operation; "
        "typedef int (__cdecl *helper)(const operation*); "
        "static unsigned __cdecl cb(void*u){return u==(void*)0x1234;} "
        "int main(int n,char**v){HMODULE m=n==2?LoadLibraryA(v[1]):0;union{FARPROC raw;helper typed;}loader;union{cdecl_cb c;stdcall_cb s;}callback;operation op;loader.raw=m?GetProcAddress(m,\"cc_probe_bad_callback\"):0;if(!loader.typed)return 2;callback.c=cb;op.callback=callback.s;op.user=(void*)0x1234;(void)loader.typed(&op);return 6;}\n",
        encoding="utf-8",
    )

    runtime_negative_compile_diagnostic_sweep(base, runner)

    runner.run("runtime-fastcall-dll", ["cl", "/nologo", "/TC", "/Gr", "/W4", "/WX", "/LD", str(base / "fastcall-dll.c"), "/Fo" + str(base / "fastcall-dll.obj"), "/Fe:" + str(base / "fastcall.dll")], cwd=base)
    audit_artifact(runner, "runtime-fastcall-dll-object", base / "fastcall-dll.obj", "x86", symbols=True)
    audit_artifact(runner, "runtime-fastcall-dll", base / "fastcall.dll", "x86", symbols=False)
    fast_exports_text = runner.run("runtime-fastcall-exports", ["dumpbin", "/exports", str(base / "fastcall.dll")], cwd=base).stdout
    fast_exports = pe_export_names(fast_exports_text)
    if "@archive_bridge_v1_handshake@8" not in fast_exports or "archive_bridge_v1_handshake" in fast_exports:
        raise RuntimeError("fastcall mutation did not expose the expected decorated PE name")
    runner.run("runtime-fastcall-caller", ["cl", "/nologo", "/TC", "/Gd", "/W4", "/WX", "/Od", "/RTC1", str(base / "fastcall-caller.c"), "/Fo" + str(base / "fastcall-caller.obj"), "/Fe:" + str(base / "fastcall-caller.exe")], cwd=base)
    audit_artifact(runner, "runtime-fastcall-caller", base / "fastcall-caller.obj", "x86", symbols=True)
    require_runtime_failure(runner, "runtime-fastcall-run", [str(base / "fastcall-caller.exe"), str(base / "fastcall.dll")], base, 86, "EXPECTED_ARGUMENT_SENTINEL_MISMATCH")

    runner.run("runtime-stdcall-dll", ["cl", "/nologo", "/TC", "/Gz", "/W4", "/WX", "/LD", str(base / "stdcall-dll.c"), "/Fo" + str(base / "stdcall-dll.obj"), "/Fe:" + str(base / "stdcall.dll")], cwd=base)
    audit_artifact(runner, "runtime-stdcall-dll-object", base / "stdcall-dll.obj", "x86", symbols=True)
    audit_artifact(runner, "runtime-stdcall-dll", base / "stdcall.dll", "x86", symbols=False)
    std_exports_text = runner.run("runtime-stdcall-exports", ["dumpbin", "/exports", str(base / "stdcall.dll")], cwd=base).stdout
    std_exports = pe_export_names(std_exports_text)
    if "_archive_bridge_v1_close@20" not in std_exports or "archive_bridge_v1_close" in std_exports:
        raise RuntimeError("stdcall mutation did not expose the expected decorated PE name")
    runner.run("runtime-stdcall-caller", ["cl", "/nologo", "/TC", "/Gd", "/W4", "/WX", "/Od", "/RTC1", str(base / "stdcall-caller.c"), "/Fo" + str(base / "stdcall-caller.obj"), "/Fe:" + str(base / "stdcall-caller.exe")], cwd=base)
    audit_artifact(runner, "runtime-stdcall-caller", base / "stdcall-caller.obj", "x86", symbols=True)
    require_runtime_failure(runner, "runtime-stdcall-run", [str(base / "stdcall-caller.exe"), str(base / "stdcall.dll")], base, 87, "EXPECTED_RTC_STACK_MISMATCH")

    runner.run("runtime-callback-dll", ["cl", "/nologo", "/TC", "/Gd", "/W4", "/WX", "/Od", "/RTC1", "/LD", str(base / "callback-dll.c"), "/Fo" + str(base / "callback-dll.obj"), "/Fe:" + str(base / "callback.dll")], cwd=base)
    audit_artifact(runner, "runtime-callback-dll-object", base / "callback-dll.obj", "x86", symbols=True)
    audit_artifact(runner, "runtime-callback-dll", base / "callback.dll", "x86", symbols=False)
    runner.run("runtime-callback-caller", ["cl", "/nologo", "/TC", "/Gd", "/W4", "/WX", str(base / "callback-caller.c"), "/Fo" + str(base / "callback-caller.obj"), "/Fe:" + str(base / "callback-caller.exe")], cwd=base)
    audit_artifact(runner, "runtime-callback-caller", base / "callback-caller.obj", "x86", symbols=True)
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
        audit_artifact(runner, name, work / "probe.obj", "x86", symbols=True)
        dump = (runner.evidence / f"{name}-symbols.log").read_text(encoding="utf-8")
        symbols = raw_symbols(dump)
        if wrong not in symbols or correct in symbols:
            raise RuntimeError(f"{name}: expected wrong symbol {wrong} and absence of {correct}")
        (runner.evidence / f"{name}-symbol-result.txt").write_text(f"EXPECTED_REJECTION: {wrong} observed; {correct} absent\n", encoding="utf-8")

    # A .def can normalize a wrong stdcall PE export, but cannot erase the raw
    # COFF evidence.  Build the evasion successfully, then reject its object.
    work = output / "work" / "x86" / "def_alias_evasion"
    work.mkdir(parents=True, exist_ok=True)
    (work / "alias.c").write_text("int __stdcall archive_bridge_v1_handshake(void *a, void *b) { return a != b; }\n", encoding="utf-8")
    (work / "alias.def").write_text("LIBRARY archive_bridge_v1_cc_probe_alias\nEXPORTS\n  archive_bridge_v1_handshake=_archive_bridge_v1_handshake@8\n", encoding="utf-8")
    runner.run("def-alias-compile", ["cl", "/nologo", "/c", "/TC", "/Gr", "/W4", "/WX", str(work / "alias.c"), "/Fo" + str(work / "alias.obj")], cwd=work)
    audit_artifact(runner, "def-alias", work / "alias.obj", "x86", symbols=True)
    runner.run("def-alias-link", ["link", "/nologo", "/dll", "/noentry", str(work / "alias.obj"), "/def:" + str(work / "alias.def"), "/out:" + str(work / "alias.dll")], cwd=work)
    audit_artifact(runner, "def-alias-dll", work / "alias.dll", "x86", symbols=False)
    exports = runner.run("def-alias-exports", ["dumpbin", "/exports", str(work / "alias.dll")], cwd=work).stdout
    symbols_text = (runner.evidence / "def-alias-symbols.log").read_text(encoding="utf-8")
    rejection = assert_def_alias_evasion(exports, symbols_text)
    (runner.evidence / "def-alias-evasion-result.txt").write_text(
        "EXPECTED_REJECTION: PE table contained only archive_bridge_v1_handshake; "
        "raw COFF exact checker rejected _archive_bridge_v1_handshake@8. "
        + rejection
        + "\n",
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
        audit_artifact(
            runner,
            "current-source-definition-mutation",
            current / "mutated.obj",
            "x86",
            symbols=True,
        )
        dump = (runner.evidence / "current-source-definition-mutation-symbols.log").read_text(encoding="utf-8")
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
    assert_complete_artifact_audit(work, runner, arch)
    assert_acceptance_tables(runner.acceptance_tables, arch)
    runner.write_manifest({"schema": 2, "target_name": "msvc-abi-convention-probe", "not_product": True,
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
    manifests: dict[str, dict[str, Any]] = {}
    for arch in ("amd64", "x86"):
        manifest = evidence / arch / "manifest.json"
        if not manifest.is_file():
            raise RuntimeError(f"missing lane manifest: {manifest}")
        manifests[arch] = json.loads(manifest.read_text(encoding="utf-8"))
        assert_acceptance_tables(manifests[arch]["acceptance_tables"], arch)
    runnable_suffixes = {".dll", ".exe", ".lib", ".exp", ".obj", ".pdb", ".ilk"}
    work = output / "work"
    if work.exists():
        for path in work.rglob("*"):
            if path.is_file() and path.suffix.lower() in runnable_suffixes:
                path.unlink()
    summary_lines = [
        "MSVC ABI convention qualification (non-product)\n"
        "AMD64 normative lane: PASS\n"
        "x86 compiler-semantic diagnostic lane (not a product target): PASS\n"
        "Failure injection: omitted call macro, callback __stdcall, export __stdcall, and .def alias evasion all rejected.\n"
        "The retained facade was not built. The fail-closed !ERROR guard remains authoritative.\n"
        "Windows facade qualification remains unauthorized and qualified_operations is 0.\n"
        "This evidence does not qualify archive semantics, codecs, encryption, passwords, filesystem behavior, lifetimes, cancellation, registration, GUI, packaging, or release behavior.\n",
    ]
    for arch in ("amd64", "x86"):
        manifest = manifests[arch]
        tables = manifest["acceptance_tables"]
        audit = manifest["artifact_audit"]
        summary_lines.append(
            f"\n{arch.upper()} acceptance record: machine={tables['machine']}; "
            f"audited objects/DLLs={len(audit)}\n"
        )
        summary_lines.append("Audited object/DLL machine values:\n")
        for path, record in sorted(audit.items()):
            summary_lines.append(
                f"  {path}: {record['kind']} machine={record['machine']}\n"
            )
        summary_lines.append("Exports (expected COFF | actual COFF | expected PE/internal | actual PE/internal):\n")
        for name in EXPORT_ARGUMENT_BYTES:
            summary_lines.append(
                f"  {name}: {tables['export_coff_expected'][name]} | "
                f"{tables['export_coff_actual'][name]} | "
                f"{tables['export_pe_expected'][name]} | "
                f"{tables['export_pe_actual'][name]}\n"
            )
        summary_lines.append("Callback targets (expected COFF | actual COFF | PE):\n")
        for name in CALLBACK_ARGUMENT_BYTES:
            summary_lines.append(
                f"  {name}: {tables['callback_coff_expected'][name]} | "
                f"{tables['callback_coff_actual'][name]} | "
                f"{tables['callback_pe_exports'][name]}\n"
            )
    (evidence / "SUMMARY.txt").write_text("".join(summary_lines), encoding="utf-8")
    digest_lines = []
    for path in sorted(evidence.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            digest_lines.append(f"{sha256(path)}  {path.relative_to(evidence).as_posix()}")
    (evidence / "SHA256SUMS.txt").write_text("\n".join(digest_lines) + "\n", encoding="utf-8")


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
