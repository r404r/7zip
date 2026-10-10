#!/usr/bin/env python3
"""Regression entry point for bridge-owned registration seam guards."""
from pathlib import Path
import re
import subprocess
import sys


SCRIPT = Path(__file__).with_name("check-registration-seam.py")
CORRESPONDENCE = Path(__file__).with_name("archive_bridge_registration_correspondence.cpp")
CORRESPONDENCE_HEADER = Path(__file__).with_name("archive_bridge_registration_correspondence.h")
FACADE = Path(__file__).with_name("archive_bridge_v1.cpp")
NMAKE = Path(__file__).with_name("makefile")
GNU_MAKE = Path(__file__).with_name("makefile.gcc")


def main():
    source = CORRESPONDENCE.read_text()
    if "(wchar_t)(unsigned char)*capture_name" in source:
        raise SystemExit("correspondence helper contains an Apple Clang old-style cast")
    if CORRESPONDENCE_HEADER.read_text().count("uint32_t Reserved;") != 2:
        raise SystemExit("correspondence records must make alignment storage explicit")
    if "rows, rows, 61" in FACADE.read_text():
        raise SystemExit("production correspondence compares the runtime table to itself")
    nmake = NMAKE.read_text()
    recipes = re.findall(
        r"^\t\$\(COMPLB\).* /DRegisterArc=ArchiveBridgeRegisterArc$", nmake, re.MULTILINE)
    if len(recipes) != 54:
        raise SystemExit("NMAKE must contain 54 explicit redirected compile recipes")
    if "$(COMPLB) $(ZIP_FLAGS) /DRegisterArc=ArchiveBridgeRegisterArc" not in nmake:
        raise SystemExit("NMAKE Zip recipe must preserve ZIP_FLAGS")
    if '!include "Arc.mak"' not in nmake or '!include "../../7zip.mak"' not in nmake:
        raise SystemExit("NMAKE includes must resolve from the retained bundle directory")
    for bridge_source in (
        "archive_bridge_v1.cpp",
        "archive_bridge_registration.cpp",
        "archive_bridge_registration_correspondence.cpp",
    ):
        recipe = re.search(
            rf"^\$O\\{re.escape(Path(bridge_source).stem)}\.obj: "
            rf"\.\./\.\./\.\./\.\./rust/bridge/{re.escape(bridge_source)}\n"
            r"\t\$\(COMPLB_O2\) /I\"(?:\.\./){4}\"(?!.*RegisterArc)",
            nmake,
            re.MULTILINE,
        )
        if recipe is None:
            raise SystemExit(f"NMAKE must compile {bridge_source} explicitly without redirection")
    gnu_make = GNU_MAKE.read_text()
    if "registration-mis-scope-check" not in gnu_make:
        raise SystemExit("GNU build must compile and reject a real mis-scoped object")
    if "--expect-mis-scope" not in gnu_make:
        raise SystemExit("GNU object audit must inspect the real mis-scoped object")
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--self-test"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.stdout + completed.stderr)
    if "PASS: registration seam negative controls" not in completed.stdout:
        raise SystemExit("registration seam self-test did not report all negative controls")
    print(completed.stdout, end="")


if __name__ == "__main__":
    main()
