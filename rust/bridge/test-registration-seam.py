#!/usr/bin/env python3
"""Regression entry point for bridge-owned registration seam guards."""
from pathlib import Path
import subprocess
import sys


SCRIPT = Path(__file__).with_name("check-registration-seam.py")


def main():
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
