#!/usr/bin/env python3
"""Fail-closed structural guard for the portable retained-registration seam."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BRIDGE = ROOT / "rust/bridge"
EXPECTED = """ApfsHandler ApmHandler ArHandler ArjHandler Base64Handler Bz2Handler ComHandler CpioHandler CramfsHandler DmgHandler ElfHandler ExtHandler FatHandler FlvHandler GptHandler GzHandler HfsHandler IhexHandler LpHandler LzhHandler LzmaHandler MachoHandler MbrHandler MslzHandler MubHandler NtfsHandler PeHandler PpmdHandler QcowHandler RpmHandler SparseHandler SplitHandler SquashfsHandler SwfHandler UefiHandler VdiHandler VhdHandler VhdxHandler VmdkHandler XarHandler XzHandler ZHandler ZstdHandler 7zRegister CabRegister ChmHandler IsoRegister NsisRegister RarHandler Rar5Handler TarRegister UdfHandler WimRegister ZipRegister""".split()
FORBIDDEN = ("--wrap", "_Z11RegisterArcPK8CArcInfo", "__real_", "__wrap_")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_guard(bridge=BRIDGE):
    inputs = [bridge / "archive_bridge_v1.cpp", bridge / "archive_bridge_registration.cpp",
              bridge / "archive_bridge_registration.h",
              bridge / "archive_bridge_registration_correspondence.cpp",
              bridge / "archive_bridge_registration_correspondence.h",
              bridge / "makefile.gcc", bridge / "makefile"]
    text = "\n".join(path.read_text() for path in inputs)
    for token in FORBIDDEN:
        require(token not in text, "forbidden production build input: " + token)
    require("extern \"C\"" not in (bridge / "archive_bridge_registration.cpp").read_text(),
            "shim must use ordinary C++ linkage")
    make = (bridge / "makefile.gcc").read_text()
    selected = re.findall(r"\$O/([A-Za-z0-9]+)\.o", make[
        make.index("REGISTER_ARC_OBJS ="):make.index("$(REGISTER_ARC_OBJS):")])
    require(selected == EXPECTED, "GNU selected registration objects drift")
    require("-DRegisterArc=ArchiveBridgeRegisterArc" in make, "GNU redirection missing")
    bridge_start = make.index("BRIDGE_OBJS =")
    bridge_objects = make[bridge_start:make.index("\nOBJS =", bridge_start)]
    require("$O/archive_bridge_registration.o" in bridge_objects, "shim object missing")
    require(".PHONY: registration-seam-check" in make
            and "registration-seam-check: $(REGISTER_ARC_OBJS) $O/LoadCodecs.o $O/archive_bridge_registration.o" in make
            and "check-registration-seam.py --object-dir" in make
            and "$(PROGPATH): registration-seam-check" in make,
            "link preflight missing")
    require("!ERROR" in (bridge / "makefile").read_text(), "Windows fail-closed guard removed")


def replace_once(path, old, new):
    text = path.read_text()
    require(old in text, "self-test anchor missing: " + old)
    path.write_text(text.replace(old, new, 1))


def expect_source_guard_failure(bridge, path, old, new, label):
    replace_once(bridge / path, old, new)
    try:
        source_guard(bridge)
    except ValueError:
        return
    raise ValueError("negative control did not fail closed: " + label)


def self_test():
    # Every mutation is applied to an isolated copy. Production sources and
    # retained inputs stay immutable while the guard proves it rejects a bad
    # bridge input before link.
    mutations = (
        ("archive_bridge_v1.cpp", "#include \"archive_bridge_registration.h\"", "--wrap", "forbidden linker wrapper"),
        ("archive_bridge_registration.cpp", "#include \"archive_bridge_registration.h\"", "extern \"C\"", "C linkage shim"),
        ("makefile.gcc", "$O/ZipRegister.o", "$O/PhantomRegister.o", "selected-object drift"),
        ("makefile.gcc", "-DRegisterArc=ArchiveBridgeRegisterArc", "-DRegisterArc=WrongRegistrar", "missing redirection"),
        ("makefile.gcc", "archive_bridge_registration.o", "archive_bridge_removed.o", "missing shim object"),
        ("makefile.gcc", "registration-seam-check", "registration-seam-removed", "missing link preflight"),
        ("makefile", "!ERROR", "!MESSAGE", "removed Windows guard"),
    )
    for path, old, new, label in mutations:
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "bridge"
            shutil.copytree(BRIDGE, copied)
            expect_source_guard_failure(copied, path, old, new, label)
    print("PASS: registration seam negative controls")


def object_guard(directory):
    directory = Path(directory)
    require(directory.is_dir(), "object directory does not exist")
    for name in EXPECTED:
        path = directory / (name + ".o")
        require(path.is_file(), "missing selected object " + path.name)
        symbols = subprocess.check_output(["nm", "-C", str(path)], text=True)
        require("ArchiveBridgeRegisterArc(CArcInfo const*)" in symbols,
                "selected object lacks redirected reference: " + path.name)
    load = directory / "LoadCodecs.o"
    shim = directory / "archive_bridge_registration.o"
    for path in (load, shim):
        require(path.is_file(), "missing bridge object " + path.name)
    load_symbols = subprocess.check_output(["nm", "-C", str(load)], text=True)
    shim_symbols = subprocess.check_output(["nm", "-C", str(shim)], text=True)
    require("RegisterArc(CArcInfo const*)" in load_symbols and "ArchiveBridgeRegisterArc" not in load_symbols,
            "LoadCodecs registrar scope drift")
    require("ArchiveBridgeRegisterArc(CArcInfo const*)" in shim_symbols
            and "RegisterArc(CArcInfo const*)" in shim_symbols, "shim forwarding scope drift")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--object-dir")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    source_guard()
    if args.object_dir:
        object_guard(args.object_dir)
    elif not args.source_only:
        raise SystemExit("FAIL: --object-dir is required unless --source-only is used")
    print("PASS: portable retained registration seam guard")


if __name__ == "__main__":
    try:
        main()
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        print("FAIL:", error, file=sys.stderr)
        sys.exit(1)
