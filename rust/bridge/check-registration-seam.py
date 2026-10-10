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
EXPECTED_NMAKE_SOURCES = [
    "../../Archive/" + name + ".cpp" for name in EXPECTED[:43]
] + [
    "../../Archive/7z/7zRegister.cpp",
    "../../Archive/Cab/CabRegister.cpp",
    "../../Archive/Chm/ChmHandler.cpp",
    "../../Archive/Iso/IsoRegister.cpp",
    "../../Archive/Nsis/NsisRegister.cpp",
    "../../Archive/Rar/RarHandler.cpp",
    "../../Archive/Rar/Rar5Handler.cpp",
    "../../Archive/Tar/TarRegister.cpp",
    "../../Archive/Udf/UdfHandler.cpp",
    "../../Archive/Wim/WimRegister.cpp",
    "../../Archive/Zip/ZipRegister.cpp",
]
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
    correspondence = (bridge / "archive_bridge_registration_correspondence.h").read_text() + "\n" \
        + (bridge / "archive_bridge_registration_correspondence.cpp").read_text()
    require("noexcept" not in correspondence and "throw()" not in correspondence,
            "correspondence helper must not add an exception specification")
    make = (bridge / "makefile.gcc").read_text()
    selected = re.findall(r"\$O/([A-Za-z0-9]+)\.o", make[
        make.index("REGISTER_ARC_OBJS ="):make.index("$(REGISTER_ARC_OBJS):")])
    require(selected == EXPECTED, "GNU selected registration objects drift")
    definition = "-DRegisterArc=ArchiveBridgeRegisterArc"
    require(make.count("$(REGISTER_ARC_OBJS): CXXFLAGS += " + definition) == 1,
            "GNU redirection is missing or mis-scoped")
    require(make.count(definition) == 2
            and "--expect-mis-scope $$bad" in make,
            "GNU deliberate mis-scope control is missing or not isolated")
    bridge_start = make.index("BRIDGE_OBJS =")
    bridge_objects = make[bridge_start:make.index("\nOBJS =", bridge_start)]
    require("$O/archive_bridge_registration.o" in bridge_objects, "shim object missing")
    require(".PHONY: registration-seam-check" in make
            and "registration-seam-check: $(REGISTER_ARC_OBJS) $O/LoadCodecs.o $O/archive_bridge_registration.o" in make
            and "check-registration-seam.py --object-dir" in make
            and "$(PROGPATH): registration-seam-check" in make,
            "link preflight missing")
    nmake = (bridge / "makefile").read_text()
    require("!ERROR" in nmake, "Windows fail-closed guard removed")
    nmake_start = nmake.index("REGISTER_ARC_OBJS =")
    nmake_end = nmake.index("# These explicit recipes", nmake_start)
    nmake_selected = re.findall(r"\$O\\([A-Za-z0-9]+)\.obj", nmake[nmake_start:nmake_end])
    require(nmake_selected == EXPECTED, "NMAKE selected registration objects drift")
    recipes = re.findall(
        r"^\$O\\([A-Za-z0-9]+)\.obj: ([^\r\n]+)\r?\n"
        r"\t(\$\(COMPLB\)(?: \$\(ZIP_FLAGS\))? /DRegisterArc=ArchiveBridgeRegisterArc)$",
        nmake, re.MULTILINE)
    require([name for name, _, _ in recipes] == EXPECTED,
            "NMAKE explicit recipe targets drift")
    require([source for _, source, _ in recipes] == EXPECTED_NMAKE_SOURCES,
            "NMAKE explicit recipe source pairing drift")
    require(all("$(ZIP_FLAGS)" not in command for _, _, command in recipes[:-1])
            and "$(ZIP_FLAGS)" in recipes[-1][2],
            "NMAKE Zip flags are missing or mis-scoped")


def replace_once(path, old, new):
    text = path.read_text()
    require(old in text, "self-test anchor missing: " + old)
    path.write_text(text.replace(old, new, 1))


def expect_source_guard_failure(bridge, path, old, new, label):
    replace_once(bridge / path, old, new)
    try:
        source_guard(bridge)
    except ValueError:
        print("PASS: source fault injection rejected: " + label)
        return
    raise ValueError("negative control did not fail closed: " + label)


def self_test():
    # Every mutation is applied to an isolated copy. Production sources and
    # retained inputs stay immutable while the guard proves it rejects a bad
    # bridge input before link.
    mutations = (
        ("archive_bridge_v1.cpp", "#include \"archive_bridge_registration.h\"", "--wrap", "forbidden linker wrapper"),
        ("archive_bridge_registration.cpp", "#include \"archive_bridge_registration.h\"", "extern \"C\"", "C linkage shim"),
        ("archive_bridge_registration_correspondence.h", "bool ArchiveBridgeValidateRegistrationCorrespondence(", "noexcept bool ArchiveBridgeValidateRegistrationCorrespondence(", "correspondence exception specification"),
        ("makefile.gcc", "$O/ZipRegister.o", "$O/PhantomRegister.o", "selected-object drift"),
        ("makefile.gcc", "-DRegisterArc=ArchiveBridgeRegisterArc", "-DRegisterArc=WrongRegistrar", "missing redirection"),
        ("makefile.gcc", "$(REGISTER_ARC_OBJS): CXXFLAGS += -DRegisterArc=ArchiveBridgeRegisterArc",
         "$(REGISTER_ARC_OBJS) $O/LoadCodecs.o: CXXFLAGS += -DRegisterArc=ArchiveBridgeRegisterArc",
         "mis-scoped redirection"),
        ("makefile.gcc", "archive_bridge_registration.o", "archive_bridge_removed.o", "missing shim object"),
        ("makefile.gcc", "registration-seam-check", "registration-seam-removed", "missing link preflight"),
        ("makefile", "!ERROR", "!MESSAGE", "removed Windows guard"),
        ("makefile", "$O\\ApfsHandler.obj: ../../Archive/ApfsHandler.cpp\n\t$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc",
         "$O\\ApfsHandler.obj: ../../Archive/ApfsHandler.cpp\n\t$(COMPLB)",
         "missing NMAKE per-object define"),
        ("makefile", "$O\\ApfsHandler.obj: ../../Archive/ApfsHandler.cpp\n\t$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc",
         "# $(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc",
         "comment-only NMAKE declaration"),
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
    selected_names = set(EXPECTED) | {"archive_bridge_registration"}
    for path in directory.glob("*.o"):
        symbols = subprocess.check_output(["nm", "-C", str(path)], text=True)
        if path.stem not in selected_names:
            reject_unexpected_redirect(path, symbols)


def reject_unexpected_redirect(path, symbols):
    require("ArchiveBridgeRegisterArc(CArcInfo const*)" not in symbols,
            "unexpected redirected reference: " + path.name)


def expect_mis_scope_rejection(path):
    path = Path(path)
    require(path.is_file(), "missing deliberately mis-scoped object")
    symbols = subprocess.check_output(["nm", "-C", str(path)], text=True)
    require("ArchiveBridgeRegisterArc(CArcInfo const*)" in symbols,
            "deliberately mis-scoped object did not contain redirected registrar")
    try:
        reject_unexpected_redirect(path, symbols)
    except ValueError as error:
        require("unexpected redirected reference" in str(error),
                "object-scope audit failed for the wrong reason")
        print("PASS: object-scope audit rejected deliberately mis-scoped object")
        return
    raise ValueError("object-scope audit accepted deliberately mis-scoped object")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--object-dir")
    parser.add_argument("--expect-mis-scope")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    source_guard()
    if args.expect_mis_scope:
        expect_mis_scope_rejection(args.expect_mis_scope)
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
