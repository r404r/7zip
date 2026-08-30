#!/usr/bin/env python3
"""The shell extension of this fork must not share its identity with 7-Zip.

The official 7-zip.dll registers CLSID {23170F69-40C1-278A-1000-000100020000}
under "...\\shellex\\ContextMenuHandlers\\7-Zip". A build that keeps any of
that replaces the official context menu on the machine it is installed on.
The identity is written in three source files and in the MSI, and this
script checks that all of them agree on the fork's own values.

    python3 .github/tests/shell_ext_identity.py [repo root]
"""
import os
import re
import sys

FORK_CLSID = "{1281FA63-F95D-48AC-9342-EE333A3F71F8}"
OFFICIAL_CLSID = "{23170F69-40C1-278A-1000-000100020000}"
MENU_NAME = "7-Zip-fork"

EXPLORER = os.path.join("CPP", "7zip", "UI", "Explorer")
FILES = {
    "registry": os.path.join(EXPLORER, "RegistryContextMenu.cpp"),
    "exports": os.path.join(EXPLORER, "DllExportsExplorer.cpp"),
    "menu": os.path.join(EXPLORER, "ContextMenu.cpp"),
    "wxs": os.path.join(".github", "msi", "7zip-fork.wxs"),
}

failed = 0


def check(ok, what):
    global failed
    if not ok:
        failed += 1
    print("  %-4s %s" % ("PASS" if ok else "FAIL", what))


def guid_from_define(text):
    """Rebuild the GUID that Z7_DEFINE_GUID(CLSID_CZipContextMenu, ...) spells out.
    Returns None when an argument is not a numeric literal."""
    m = re.search(r"Z7_DEFINE_GUID\(CLSID_CZipContextMenu,(.*?)\);", text, re.S)
    if not m:
        return None
    args = [a.strip() for a in m.group(1).split(",")]
    if len(args) != 11:
        return None
    try:
        nums = [int(a, 0) for a in args]
    except ValueError:
        return None
    return "{%08X-%04X-%04X-%02X%02X-%02X%02X%02X%02X%02X%02X}" % tuple(nums)


def main(root):
    src = {}
    for key, rel in FILES.items():
        with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as f:
            src[key] = f.read()

    print("-- CLSID")
    check('k_Clsid_A "%s"' % FORK_CLSID in src["registry"],
          "RegistryContextMenu.cpp: k_Clsid_A is the fork CLSID")
    check('TEXT("%s")' % FORK_CLSID in src["exports"],
          "DllExportsExplorer.cpp: k_Clsid is the fork CLSID")
    got = guid_from_define(src["exports"])
    check(got == FORK_CLSID,
          "DllExportsExplorer.cpp: Z7_DEFINE_GUID(CLSID_CZipContextMenu) spells the fork CLSID (got %s)" % got)
    for key in ("registry", "exports", "wxs"):
        check(OFFICIAL_CLSID not in src[key],
              "%s: the official CLSID does not appear" % FILES[key])

    print("-- registry key names")
    check('"\\\\shellex\\\\ContextMenuHandlers\\\\%s"' % MENU_NAME in src["registry"],
          "RegistryContextMenu.cpp: ContextMenuHandlers key is %s" % MENU_NAME)
    check('"\\\\shellex\\\\DragDropHandlers\\\\%s"' % MENU_NAME in src["registry"],
          "RegistryContextMenu.cpp: DragDropHandlers key is %s" % MENU_NAME)
    for key in ("registry", "exports"):
        check('TEXT("%s Shell Extension")' % MENU_NAME in src[key],
              "%s: the Approved-list name says %s" % (FILES[key], MENU_NAME))

    print("-- menu caption")
    check('(UString)"%s",' % MENU_NAME in src["menu"],
          "ContextMenu.cpp: the cascaded submenu is captioned %s" % MENU_NAME)
    check('name = "%s";' % MENU_NAME in src["menu"],
          "ContextMenu.cpp: the IExplorerCommand root is named %s" % MENU_NAME)
    check('(UString)"7-Zip",' not in src["menu"] and 'name = "7-Zip";' not in src["menu"],
          "ContextMenu.cpp: no caption left that reads plain 7-Zip")

    print("-- MSI")
    check("7-zip.dll" in src["wxs"], "wxs: 7-zip.dll is installed")
    check(FORK_CLSID in src["wxs"], "wxs: the fork CLSID is registered")
    check("InprocServer32" in src["wxs"], "wxs: the class has an InprocServer32 entry")
    for kind in ("ContextMenuHandlers", "DragDropHandlers"):
        check(("shellex\\%s\\%s" % (kind, MENU_NAME)) in src["wxs"],
              "wxs: %s registered under %s" % (kind, MENU_NAME))
    check("shellex\\ContextMenuHandlers\\7-Zip\"" not in src["wxs"],
          "wxs: no handler registered under the official name 7-Zip")

    print("%d failed" % failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
