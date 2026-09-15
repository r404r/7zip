#!/usr/bin/env python3
"""Regression entry point for bridge-owned registration seam guards."""
from pathlib import Path
import subprocess
import sys


SCRIPT = Path(__file__).with_name("check-registration-seam.py")
CORRESPONDENCE = Path(__file__).with_name("archive_bridge_registration_correspondence.cpp")
CORRESPONDENCE_HEADER = Path(__file__).with_name("archive_bridge_registration_correspondence.h")
FACADE = Path(__file__).with_name("archive_bridge_v1.cpp")


def main():
    source = CORRESPONDENCE.read_text()
    if "(wchar_t)(unsigned char)*capture_name" in source:
        raise SystemExit("correspondence helper contains an Apple Clang old-style cast")
    if CORRESPONDENCE_HEADER.read_text().count("uint32_t Reserved;") != 2:
        raise SystemExit("correspondence records must make alignment storage explicit")
    if "rows, rows, 61" in FACADE.read_text():
        raise SystemExit("production correspondence compares the runtime table to itself")
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


if __name__ == "__main__":
    main()
