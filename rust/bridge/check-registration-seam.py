#!/usr/bin/env python3
"""Fail-closed structural guard for the portable retained-registration seam."""
import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BRIDGE = ROOT / "rust/bridge"
EXPECTED = """ApfsHandler ApmHandler ArHandler ArjHandler Base64Handler Bz2Handler ComHandler CpioHandler CramfsHandler DmgHandler ElfHandler ExtHandler FatHandler FlvHandler GptHandler GzHandler HfsHandler IhexHandler LpHandler LzhHandler LzmaHandler MachoHandler MbrHandler MslzHandler MubHandler NtfsHandler PeHandler PpmdHandler QcowHandler RpmHandler SparseHandler SplitHandler SquashfsHandler SwfHandler UefiHandler VdiHandler VhdHandler VhdxHandler VmdkHandler XarHandler XzHandler ZHandler ZstdHandler 7zRegister CabRegister ChmHandler IsoRegister NsisRegister RarHandler Rar5Handler TarRegister UdfHandler WimRegister ZipRegister""".split()
FORBIDDEN = ("--wrap", "_Z11RegisterArcPK8CArcInfo", "__real_", "__wrap_")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_guard():
    inputs = [BRIDGE / "archive_bridge_v1.cpp", BRIDGE / "archive_bridge_registration.cpp",
              BRIDGE / "archive_bridge_registration.h", BRIDGE / "makefile.gcc", BRIDGE / "makefile"]
    text = "\n".join(path.read_text() for path in inputs)
    for token in FORBIDDEN:
        require(token not in text, "forbidden production build input: " + token)
    require("extern \"C\"" not in (BRIDGE / "archive_bridge_registration.cpp").read_text(),
            "shim must use ordinary C++ linkage")
    make = (BRIDGE / "makefile.gcc").read_text()
    selected = re.findall(r"\$O/([A-Za-z0-9]+)\.o", make[
        make.index("REGISTER_ARC_OBJS ="):make.index("$(REGISTER_ARC_OBJS):")])
    require(selected == EXPECTED, "GNU selected registration objects drift")
    require("-DRegisterArc=ArchiveBridgeRegisterArc" in make, "GNU redirection missing")
    require("archive_bridge_registration.o" in make, "shim object missing")
    require("registration-seam-check" in make and "check-registration-seam.py --object-dir" in make,
            "link preflight missing")
    require("!ERROR" in (BRIDGE / "makefile").read_text(), "Windows fail-closed guard removed")


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
    args = parser.parse_args()
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
