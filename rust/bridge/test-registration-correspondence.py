#!/usr/bin/env python3
"""Build and execute bridge-owned correspondence negative controls."""
from pathlib import Path
import subprocess
import tempfile


BRIDGE = Path(__file__).resolve().parent
ROOT = BRIDGE.parents[1]


def compile_and_run_shim(source, binary):
    command = [
        "g++", "-std=c++11", "-Wall", "-Wextra", "-Werror",
        str(source), str(BRIDGE / "test-registration-shim.cpp"),
        "-I", str(BRIDGE), "-I", str(ROOT), "-o", str(binary),
    ]
    subprocess.run(command, check=True)
    return subprocess.run([str(binary)], check=False, text=True, capture_output=True)


def require_fault_rejected(original, old, new, label, temporary):
    if old not in original:
        raise SystemExit("shim fault-injection anchor missing: " + label)
    source = Path(temporary) / (label + ".cpp")
    source.write_text(original.replace(old, new, 1))
    completed = compile_and_run_shim(source, Path(temporary) / label)
    if completed.returncode == 0:
        raise SystemExit("shim fault injection was not rejected: " + label)
    print("PASS: shim fault injection rejected: " + label)


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

        shim_binary = Path(temporary) / "registration-shim-test"
        shim_source = BRIDGE / "archive_bridge_registration.cpp"
        shim_completed = compile_and_run_shim(shim_source, shim_binary)
        if shim_completed.returncode != 0:
            raise SystemExit(shim_completed.stdout + shim_completed.stderr)
        if "PASS: process-isolated registration shim controls" not in shim_completed.stdout:
            raise SystemExit("registration shim test did not exercise the real shim")
        print(shim_completed.stdout, end="")

        original = shim_source.read_text()
        faults = (
            ("const unsigned kRegisteredArcsMax = 72;",
             "const unsigned kRegisteredArcsMax = 73;", "capacity-73"),
            ("g_registered_arc_overflow = true;",
             "g_registered_arc_overflow = false;", "non-sticky-overflow"),
            ("  RegisterArc(arcInfo);", "  RegisterArc(arcInfo);\n  RegisterArc(arcInfo);",
             "double-forward"),
            ("  RegisterArc(arcInfo);", "  (void)arcInfo;", "zero-forward"),
        )
        for old, new, label in faults:
            require_fault_rejected(original, old, new, label, temporary)


if __name__ == "__main__":
    main()
