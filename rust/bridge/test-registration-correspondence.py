#!/usr/bin/env python3
"""Build and execute bridge-owned correspondence negative controls."""
from pathlib import Path
import subprocess
import tempfile


BRIDGE = Path(__file__).resolve().parent


def main():
    with tempfile.TemporaryDirectory(prefix="archive-bridge-correspondence-") as temporary:
        binary = Path(temporary) / "registration-correspondence-test"
        command = [
            "g++", "-std=c++11", "-Wall", "-Wextra", "-Werror",
            str(BRIDGE / "archive_bridge_registration_correspondence.cpp"),
            str(BRIDGE / "test-registration-correspondence.cpp"),
            "-I", str(BRIDGE), "-o", str(binary),
        ]
        subprocess.run(command, check=True)
        completed = subprocess.run([str(binary)], check=False, text=True,
                                 capture_output=True)
        if completed.returncode != 0:
            raise SystemExit(completed.stdout + completed.stderr)
        required = (
            "PASS: correspondence positive control",
            "PASS: correspondence negative controls",
            "PASS: 73rd-call overflow control",
            "PASS: in-range null control",
            "PASS: duplicate captured name control",
            "PASS: missing Hash control",
            "PASS: duplicate Hash control",
        )
        for marker in required:
            if marker not in completed.stdout:
                raise SystemExit("missing test marker: " + marker)


if __name__ == "__main__":
    main()
