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
  2. QueryContextMenu takes the lock before its first read, in a brace scope
     that is still open at every read (the body sits in a try block, so
     "the function's own scope" is that block), and reloads under it
  3. every reader in MyMessages.cpp (the InvokeCommand path) reads in the
     scope of the lock
  4. the readers of the language table linked into the DLL are exactly the
     known set - ContextMenu.cpp, MyMessages.cpp and the two File Manager
     helpers FormatUtils.cpp / PropertyName.cpp - and the helpers are only
     reached from inside QueryContextMenu
  5. LangUtils: the reload compares the raw registry value with the one the
     table was loaded for (not g_LangID) and loads that same value; it is a
     one-time load unless g_LangFollowsRegistry is set, which only the DLL's
     DllMain does - the File Manager compiles the same ContextMenu.cpp and
     must keep reloading on its own terms

    python3 .github/tests/shell_ext_lang_reload.py [repo root]
"""
import os
import re
import sys

EXPLORER = os.path.join("CPP", "7zip", "UI", "Explorer")
FM = os.path.join("CPP", "7zip", "UI", "FileManager")
CONTEXT_MENU = os.path.join(EXPLORER, "ContextMenu.cpp")
MESSAGES = os.path.join(EXPLORER, "MyMessages.cpp")
DLL_EXPORTS = os.path.join(EXPLORER, "DllExportsExplorer.cpp")
DLL_MAKEFILE = os.path.join(EXPLORER, "makefile")
LANG_UTILS_H = os.path.join(FM, "LangUtils.h")
LANG_UTILS_CPP = os.path.join(FM, "LangUtils.cpp")

LOCK_RE = re.compile(r"CCriticalSectionLock\s+\w+\s*\(\s*Lang_CriticalSection\(\)\s*\)")
# direct readers of the table, and the linked helpers that read it for the caller
READ_RE = re.compile(r"\b(LangString|LangString_OnlyFromLangFile|AddLangString|g_Lang"
                     r"|MyFormatNew|GetNameOfProperty)\b")
FUNC_RE = re.compile(r"^[A-Za-z_][^;{}]*\b(\w+)\s*\([^;]*$")

# files linked into the DLL that read the table; anything else reading it is new
READER_FILES = {"ContextMenu.cpp", "MyMessages.cpp", "FormatUtils.cpp", "PropertyName.cpp",
                "LangUtils.cpp"}
# in ContextMenu.cpp: who may read, and who may call whom (the closure under the lock)
READERS = {"QueryContextMenu", "FillCommand", "LangStringAlt", "MyFormatNew_ReducedName"}
CALLERS = {"FillCommand": {"AddCommand", "QueryContextMenu"},
           "LangStringAlt": {"QueryContextMenu"},
           "AddCommand": {"QueryContextMenu"},
           "MyFormatNew_ReducedName": {"QueryContextMenu"}}


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as fh:
        return fh.read().split("\n")


def code(line):
    """The line without its // comment and string literals."""
    line = re.sub(r'"(\\.|[^"\\])*"', '""', line)
    return line.split("//", 1)[0]


def functions(lines):
    """[(name, first_line, last_line)] for column-0 function headers."""
    heads = []
    for i, line in enumerate(lines):
        if not line or line[0] in " \t/#{}*":
            continue
        m = FUNC_RE.match(line)
        if m and not line.rstrip().endswith(";"):
            heads.append((m.group(1), i))
    return [(n, a, heads[k + 1][1] if k + 1 < len(heads) else len(lines))
            for k, (n, a) in enumerate(heads)]


def body(lines, funcs, name):
    for n, a, b in funcs:
        if n == name:
            return a, lines[a:b]
    return None, []


def reads_at(lines):
    return [i for i, l in enumerate(lines) if READ_RE.search(code(l))]


def lock_covers(lines, lock, target):
    """True when the brace scope the lock lives in is still open at target."""
    depth = 0
    depth_after = []
    for l in lines:
        c = code(l)
        depth += c.count("{") - c.count("}")
        depth_after.append(depth)
    at_lock = depth_after[lock]
    return all(d >= at_lock for d in depth_after[lock:target])


def main(root):
    fails = []

    def fail(msg):
        fails.append(msg)
        print("  FAIL " + msg)

    # 1. the one-time load is gone from the DLL
    for name in sorted(os.listdir(os.path.join(root, EXPLORER))):
        if name.endswith(".cpp"):
            for i, l in enumerate(read(root, os.path.join(EXPLORER, name)), start=1):
                if "LoadLangOneTime" in code(l):
                    fail("%s:%d still uses LoadLangOneTime" % (os.path.join(EXPLORER, name), i))

    # 2. QueryContextMenu: lock first, in a scope that lasts to the end, reload under it
    cm = read(root, CONTEXT_MENU)
    funcs = functions(cm)
    start, qcm = body(cm, funcs, "QueryContextMenu")
    if start is None:
        fail("%s: QueryContextMenu not found" % CONTEXT_MENU)
    else:
        lock = next((i for i, l in enumerate(qcm) if LOCK_RE.search(l)), None)
        reload = next((i for i, l in enumerate(qcm) if "ReloadLangIfRegChanged()" in code(l)), None)
        reads = reads_at(qcm)
        if lock is None:
            fail("QueryContextMenu does not take Lang_CriticalSection()")
        else:
            if reload is None:
                fail("QueryContextMenu does not call ReloadLangIfRegChanged()")
            elif reload < lock or not lock_covers(qcm, lock, reload):
                fail("QueryContextMenu reloads the language outside the lock")
            for r in reads:
                if r < lock or not lock_covers(qcm, lock, r):
                    fail("QueryContextMenu reads the language table at line %d outside the lock's scope"
                         % (start + r + 1))

    # 3. every reader in MyMessages.cpp reads in the scope of the lock
    mm = read(root, MESSAGES)
    for n, a, b in functions(mm):
        fn = mm[a:b]
        reads = reads_at(fn)
        if not reads:
            continue
        lock = next((i for i, l in enumerate(fn) if LOCK_RE.search(l)), None)
        for r in reads:
            if lock is None or r < lock or not lock_covers(fn, lock, r):
                fail("%s: %s reads the language table at line %d outside Lang_CriticalSection()"
                     % (MESSAGES, n, a + r + 1))

    # 4. the readers linked into the DLL are a closed set, reached only under the lock
    objs = re.findall(r"\$O\\(\w+)\.obj", "\n".join(read(root, DLL_MAKEFILE)))
    linked_readers = set()
    for o in objs:
        for d in (EXPLORER, FM, os.path.join("CPP", "7zip", "UI", "Common")):
            rel = os.path.join(d, o + ".cpp")
            if os.path.isfile(os.path.join(root, rel)):
                if any(READ_RE.search(code(l)) for l in read(root, rel)):
                    linked_readers.add(o + ".cpp")
    if linked_readers != READER_FILES:
        fail("files linked into the DLL that read the language table are %s, expected %s"
             % (sorted(linked_readers), sorted(READER_FILES)))
    readers = {n for n, a, b in funcs if reads_at(cm[a:b])}
    if readers != READERS:
        fail("%s: language table readers are %s, expected %s"
             % (CONTEXT_MENU, sorted(readers), sorted(READERS)))
    callers = {}
    for n, a, b in funcs:
        for h in CALLERS:
            if any(re.search(r"\b%s\s*\(" % h, code(l)) for l in cm[a + 1:b]):
                callers.setdefault(h, set()).add(n)
    for h, want in CALLERS.items():
        got = callers.get(h, set())
        if got != want:
            fail("%s is called from %s, expected only %s" % (h, sorted(got), sorted(want)))

    # 5. LangUtils: compare the raw value, load that value, and only in the DLL
    h = "\n".join(read(root, LANG_UTILS_H))
    for sym in ("Lang_CriticalSection", "ReloadLangIfRegChanged", "g_LangFollowsRegistry"):
        if sym not in h:
            fail("%s does not declare %s" % (LANG_UTILS_H, sym))
    c = read(root, LANG_UTILS_CPP)
    rstart, rbody = body(c, functions(c), "ReloadLangIfRegChanged")
    if rstart is None:
        fail("%s does not define ReloadLangIfRegChanged" % LANG_UTILS_CPP)
    else:
        text = "\n".join(code(l) for l in rbody)
        m = re.search(r"ReadRegLang\s*\(\s*(\w+)\s*\)", text)
        if not m:
            fail("ReloadLangIfRegChanged does not read the registry value")
        else:
            v = m.group(1)
            if not re.search(r"if\s*\(\s*g_Loaded\s*&&\s*%s\s*==\s*g_RegLangLoaded\s*\)" % v, text):
                fail("ReloadLangIfRegChanged does not compare the value it read with g_RegLangLoaded")
            if not re.search(r"g_RegLangLoaded\s*=\s*%s\s*;" % v, text):
                fail("ReloadLangIfRegChanged does not remember the value it loaded")
            if not re.search(r"ReloadLang_From\s*\(\s*%s\s*\)" % v, text):
                fail("ReloadLangIfRegChanged loads something other than the value it compared"
                     " (a second registry read can differ from the first)")
        if "g_LangID" in text:
            fail("ReloadLangIfRegChanged compares g_LangID - the resolved name, not the setting")
        if not re.search(r"if\s*\(\s*g_Loaded\s*&&\s*!\s*g_LangFollowsRegistry\s*\)", text):
            fail("ReloadLangIfRegChanged does not fall back to a one-time load when"
                 " g_LangFollowsRegistry is off - the File Manager would reload without refreshing")
    dll = "\n".join(code(l) for l in read(root, DLL_EXPORTS))
    if not re.search(r"g_LangFollowsRegistry\s*=\s*true\s*;", dll):
        fail("%s does not set g_LangFollowsRegistry - the DLL would never reload" % DLL_EXPORTS)
    for name in sorted(os.listdir(os.path.join(root, FM))):
        if name.endswith(".cpp") and name != "LangUtils.cpp":
            for i, l in enumerate(read(root, os.path.join(FM, name)), start=1):
                if "g_LangFollowsRegistry" in code(l):
                    fail("%s:%d touches g_LangFollowsRegistry - only the DLL may" % (os.path.join(FM, name), i))

    print("%d problem(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
