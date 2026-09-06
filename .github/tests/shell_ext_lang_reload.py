#!/usr/bin/env python3
"""The shell extension must re-read the language setting, under a lock.

7-zip.dll lives inside explorer.exe for as long as Explorer runs. Upstream
loads the language table once per process (LoadLangOneTime), so a language
changed in the File Manager never reaches the context menu until Explorer
reloads the DLL. The fork re-reads the setting on every QueryContextMenu
(ReloadLangIfRegChanged) - and because reloading rewrites the table that
CLang::Get reads without a lock, every reader in the DLL has to hold
Lang_CriticalSection() while it reads.

This cannot run the code (it runs inside explorer.exe on Windows); it only
pins the shape of the source, so that the one-time load cannot creep back
and no reader can be added outside the lock without this going red:

  1. nothing under UI/Explorer calls LoadLangOneTime
  2. QueryContextMenu takes the lock before its first read and calls
     ReloadLangIfRegChanged under it
  3. ShowErrorMessageHwndRes (the InvokeCommand path) reads under the lock
  4. the readers of the language table in the DLL are exactly the known
     set: QueryContextMenu and the helpers it calls, and MyMessages.cpp
  5. LangUtils declares and defines the reload, keyed on the raw registry
     value, not on g_LangID

    python3 .github/tests/shell_ext_lang_reload.py [repo root]
"""
import os
import re
import sys

EXPLORER = os.path.join("CPP", "7zip", "UI", "Explorer")
CONTEXT_MENU = os.path.join(EXPLORER, "ContextMenu.cpp")
MESSAGES = os.path.join(EXPLORER, "MyMessages.cpp")
LANG_UTILS_H = os.path.join("CPP", "7zip", "UI", "FileManager", "LangUtils.h")
LANG_UTILS_CPP = os.path.join("CPP", "7zip", "UI", "FileManager", "LangUtils.cpp")

LOCK_RE = re.compile(r"CCriticalSectionLock\s+\w+\s*\(\s*Lang_CriticalSection\(\)\s*\)")
READ_RE = re.compile(r"\b(LangString|LangString_OnlyFromLangFile|AddLangString|g_Lang)\b")
FUNC_RE = re.compile(r"^[A-Za-z_][^;{}]*\b(\w+)\s*\([^;]*$")

# readers reachable only from QueryContextMenu (call sites are checked below)
HELPERS = ("FillCommand", "LangStringAlt", "AddCommand")


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as fh:
        return fh.read().split("\n")


def functions(lines):
    """[(name, first_line, last_line)] for column-0 function headers."""
    heads = []
    for i, line in enumerate(lines):
        if not line or line[0] in " \t/#{}*":
            continue
        m = FUNC_RE.match(line)
        if m and not line.rstrip().endswith(";"):
            heads.append((m.group(1), i))
    out = []
    for k, (name, start) in enumerate(heads):
        end = heads[k + 1][1] if k + 1 < len(heads) else len(lines)
        out.append((name, start, end))
    return out


def body(lines, funcs, name):
    for n, a, b in funcs:
        if n == name:
            return a, lines[a:b]
    return None, []


def main(root):
    fails = []

    def fail(msg):
        fails.append(msg)
        print("  FAIL " + msg)

    # 1. the one-time load is gone from the DLL
    for name in sorted(os.listdir(os.path.join(root, EXPLORER))):
        if not name.endswith(".cpp"):
            continue
        rel = os.path.join(EXPLORER, name)
        for i, line in enumerate(read(root, rel), start=1):
            if "LoadLangOneTime" in line and not line.lstrip().startswith("//"):
                fail("%s:%d still uses LoadLangOneTime - the language would"
                     " stick for the life of explorer.exe" % (rel, i))

    # 2. QueryContextMenu: lock first, reload under it, then the reads
    cm = read(root, CONTEXT_MENU)
    funcs = functions(cm)
    start, qcm = body(cm, funcs, "QueryContextMenu")
    if start is None:
        fail("%s: QueryContextMenu not found" % CONTEXT_MENU)
    else:
        lock = next((i for i, l in enumerate(qcm) if LOCK_RE.search(l)), None)
        reload = next((i for i, l in enumerate(qcm) if "ReloadLangIfRegChanged()" in l), None)
        first_read = next((i for i, l in enumerate(qcm)
                           if READ_RE.search(l) or re.search(r"\b(%s)\s*\(" % "|".join(HELPERS), l)), None)
        if lock is None:
            fail("QueryContextMenu does not take Lang_CriticalSection()")
        if reload is None:
            fail("QueryContextMenu does not call ReloadLangIfRegChanged()")
        if lock is not None and reload is not None and reload < lock:
            fail("QueryContextMenu reloads the language before taking the lock")
        if lock is not None and first_read is not None and first_read < lock:
            fail("QueryContextMenu reads the language table (line %d) before the lock (line %d)"
                 % (start + first_read + 1, start + lock + 1))

    # 3. the InvokeCommand path reads under the lock too
    mm = read(root, MESSAGES)
    mfuncs = functions(mm)
    mstart, sem = body(mm, mfuncs, "ShowErrorMessageHwndRes")
    if mstart is None:
        fail("%s: ShowErrorMessageHwndRes not found" % MESSAGES)
    else:
        lock = next((i for i, l in enumerate(sem) if LOCK_RE.search(l)), None)
        rd = next((i for i, l in enumerate(sem) if READ_RE.search(l)), None)
        if lock is None or rd is None or rd < lock:
            fail("ShowErrorMessageHwndRes reads the language table outside Lang_CriticalSection()")

    # 4. the set of readers is closed
    for name in sorted(os.listdir(os.path.join(root, EXPLORER))):
        if not name.endswith(".cpp") or name in ("ContextMenu.cpp", "MyMessages.cpp"):
            continue
        rel = os.path.join(EXPLORER, name)
        for i, line in enumerate(read(root, rel), start=1):
            if READ_RE.search(line) and not line.lstrip().startswith("//"):
                fail("%s:%d reads the language table - a reader outside the lock" % (rel, i))
    readers = set()
    for n, a, b in funcs:
        if any(READ_RE.search(l) for l in cm[a:b] if not l.lstrip().startswith("//")):
            readers.add(n)
    expected = {"QueryContextMenu", "FillCommand", "LangStringAlt"}
    if readers != expected:
        fail("%s: language table readers are %s, expected %s"
             % (CONTEXT_MENU, sorted(readers), sorted(expected)))
    # the helpers must only be reached from inside QueryContextMenu
    callers = {}
    for n, a, b in funcs:
        for h in HELPERS:
            if any(re.search(r"\b%s\s*\(" % h, l) and not l.lstrip().startswith("//")
                   for l in cm[a + 1:b]):
                callers.setdefault(h, set()).add(n)
    allowed = {"FillCommand": {"AddCommand", "QueryContextMenu"},
               "LangStringAlt": {"QueryContextMenu"},
               "AddCommand": {"QueryContextMenu"}}
    for h, want in allowed.items():
        got = callers.get(h, set())
        if got != want:
            fail("%s is called from %s, expected only %s" % (h, sorted(got), sorted(want)))

    # 5. LangUtils: declared under Z7_LANG, defined, keyed on the registry value
    h = "\n".join(read(root, LANG_UTILS_H))
    for sym in ("Lang_CriticalSection", "ReloadLangIfRegChanged"):
        if sym not in h:
            fail("%s does not declare %s" % (LANG_UTILS_H, sym))
    c = read(root, LANG_UTILS_CPP)
    cfuncs = functions(c)
    rstart, rbody = body(c, cfuncs, "ReloadLangIfRegChanged")
    if rstart is None:
        fail("%s does not define ReloadLangIfRegChanged" % LANG_UTILS_CPP)
    else:
        text = "\n".join(rbody)
        if "ReadRegLang(" not in text:
            fail("ReloadLangIfRegChanged does not read the registry value")
        if "g_LangID" in text:
            fail("ReloadLangIfRegChanged compares g_LangID - that is the resolved name,"
                 " not the setting (OpenDefaultLang rewrites it when the setting is empty)")
        if "ReloadLang()" not in text:
            fail("ReloadLangIfRegChanged never reloads")

    print("%d problem(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
