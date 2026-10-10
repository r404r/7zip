#!/usr/bin/env python3
"""Capture real legacy CLI observations; compare only reviewed same-platform baselines.

No auto-update: --report never writes --expect. Fixtures are generated locally,
not downloaded. Passwords below are public synthetic test data, never credentials.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import stat
import subprocess
import tempfile
import time
import zlib

REPO = Path(__file__).resolve().parents[2]
STAMP = 1700000000
FIXTURES = {
    "plain.txt": b"archive characterization\n",
    "nested/日本語-😀.txt": "Unicode payload\n".encode(),
    "nested/binary.bin": bytes(range(256)) * 4,
    "empty.txt": b"",
}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def tree(root):
    result = {}
    if root.exists():
        for path in sorted(root.rglob("*")):
            if path.is_file():
                info = path.stat()
                result[path.relative_to(root).as_posix()] = {
                    "size": info.st_size, "sha256": digest(path),
                    "mtime_ns": info.st_mtime_ns,
                    "mode": stat.S_IMODE(info.st_mode),
                }
    return result


def entries(output):
    """Select stable per-entry fields from -slt -ba, excluding archive headers."""
    result = []
    for block in output.strip().split("\n\n"):
        fields = dict(line.split(" = ", 1) for line in block.splitlines() if " = " in line)
        if "Path" in fields:
            result.append({key: (value.replace("\\", "/") if key == "Path" else value)
                           for key, value in fields.items()
                           if key in ("Path", "Size", "CRC", "Encrypted", "Folder")})
    return sorted(result, key=lambda item: item["Path"])


class Capture:
    def __init__(self, exe, root, report):
        self.exe, self.root, self.report = exe, root, report
        self.source = root / "source"
        self.source.mkdir()
        for name, data in FIXTURES.items():
            path = self.source / name
            path.parent.mkdir(exist_ok=True, parents=True)
            path.write_bytes(data)
            path.chmod(0o644)
            os.utime(path, (STAMP, STAMP))
        self.report["fixtures"] = tree(self.source)

    def run(self, key, *args, success=False):
        command = [str(self.exe), *map(str, args), "-sccUTF-8", "-bd"]
        proc = subprocess.run(command, cwd=self.source, input=b"", capture_output=True, timeout=600)
        out = proc.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n")
        err = proc.stderr.decode("utf-8", errors="replace").replace("\r\n", "\n")
        self.report["commands"][key] = {
            "argv": [arg.replace(str(self.root), "<TEMP>") for arg in command],
            "exit": proc.returncode,
            "stdout": out.replace(str(self.root), "<TEMP>"),
            "stderr": err.replace(str(self.root), "<TEMP>"),
        }
        self.report["observations"][key] = {"exit": proc.returncode}
        if success and proc.returncode != 0:
            raise AssertionError(f"{key}: exit {proc.returncode}: {out}\n{err}")
        return out

    def basic(self):
        for fmt in ("7z", "zip"):
            archive = self.root / f"fixture.{fmt}"
            self.run(f"{fmt}/create", "a", f"-t{fmt}", archive, ".", success=True)
            listing = self.run(f"{fmt}/list", "l", "-slt", "-ba", archive, success=True)
            self.report["observations"][f"{fmt}/list"]["entries"] = entries(listing)
            listed = {item["Path"]: item for item in entries(listing)}
            for name, data in FIXTURES.items():
                assert listed[name]["Size"] == str(len(data)), (fmt, name, listed)
                if data:
                    assert listed[name]["CRC"] == f"{zlib.crc32(data):08X}", (fmt, name)
            self.run(f"{fmt}/test", "t", archive, success=True)
            output = self.root / f"out-{fmt}"
            self.run(f"{fmt}/extract", "x", archive, f"-o{output}", "-y", success=True)
            got = tree(output)
            assert set(got) == set(FIXTURES), (fmt, got)
            for name, data in FIXTURES.items():
                assert got[name]["sha256"] == hashlib.sha256(data).hexdigest(), (fmt, name)
            self.report["observations"][f"{fmt}/extract"]["files"] = got
            for policy in ("-aoa", "-aos", "-aou", "-aot"):
                dest = self.root / f"overwrite-{fmt}-{policy}"
                dest.mkdir()
                victim = dest / "plain.txt"
                victim.write_bytes(b"existing destination\n")
                victim.chmod(0o644)
                os.utime(victim, (STAMP - 100, STAMP - 100))
                key = f"{fmt}/overwrite/{policy}"
                self.run(key, "x", archive, "plain.txt", f"-o{dest}", policy, success=True)
                self.report["observations"][key]["files"] = tree(dest)
            # Truncate an actually produced archive; no synthetic expected error.
            broken = self.root / f"truncated.{fmt}"
            broken.write_bytes(archive.read_bytes()[:16])
            self.run(f"{fmt}/truncated", "t", broken)
        # ZIP Store payload damage leaves headers/declared CRC untouched.
        stored = self.root / "crc.zip"
        self.run("crc/create", "a", "-tzip", "-mm=Copy", stored, "plain.txt", success=True)
        raw = stored.read_bytes()
        data = FIXTURES["plain.txt"]
        assert raw.count(data) == 1, "Cannot locate unique stored payload"
        stored.write_bytes(raw.replace(data, b"X" + data[1:], 1))
        self.run("crc/test", "t", stored)

    def passwords(self):
        for label, fmt, options in (("7z-headers", "7z", ["-mhe=on"]),
                                    ("zip-aes", "zip", ["-mem=AES256"]),
                                    ("zip-crypto", "zip", ["-mem=ZipCrypto"])):
            archive = self.root / f"{label}.{fmt}"
            # ZIP's legacy writer rejects non-ASCII (ZipHandlerOut.cpp:415).
            # Record that operation separately, without inventing a golden exit.
            if fmt == "zip":
                self.run(f"{label}/non-ascii-create", "a", f"-t{fmt}", *options,
                         "-pfixture-only-日本語", self.root / f"unicode-{label}.zip", "plain.txt")
            password = "fixture-only-日本語" if fmt == "7z" else "fixture-only-ascii"
            self.run(f"{label}/create", "a", f"-t{fmt}", *options, f"-p{password}",
                     archive, "plain.txt", success=True)
            self.run(f"{label}/correct", "t", f"-p{password}", archive, success=True)
            self.run(f"{label}/wrong", "t", "-pwrong-fixture", archive)
            self.run(f"{label}/missing-eof", "t", archive)
            self.run(f"{label}/empty-eof", "t", "-p", archive)
            output = self.root / f"decrypt-{label}"
            key = f"{label}/extract"
            self.run(key, "x", f"-p{password}", archive, f"-o{output}", success=True)
            assert (output / "plain.txt").read_bytes() == FIXTURES["plain.txt"]
            self.report["observations"][key]["files"] = tree(output)

    def large(self):
        path = self.source / "large.bin"
        size = (1 << 32) + 17
        with path.open("wb") as stream:
            stream.seek(size - 1)
            stream.write(b"Z")
        path.chmod(0o644)
        os.utime(path, (STAMP, STAMP))
        archive = self.root / "large.7z"
        self.run("large/create", "a", "-t7z", "-mx=1", "-mmt=2", archive, path.name, success=True)
        listing = self.run("large/list", "l", "-slt", "-ba", archive, success=True)
        values = entries(listing)
        assert len(values) == 1 and values[0]["Size"] == str(size), values
        self.report["observations"]["large/list"]["entries"] = values
        self.run("large/test", "t", archive, success=True)
        dest = self.root / "large-out"
        self.run("large/extract", "x", archive, f"-o{dest}", success=True)
        assert (dest / path.name).stat().st_size == size
        assert digest(dest / path.name) == digest(path)
        self.report["observations"]["large/extract"]["files"] = tree(dest)

    def cancel(self):
        if os.name != "posix":
            raise RuntimeError("POSIX SIGINT probe is not a native Windows cancellation oracle")
        path = self.source / "cancel.bin"
        # Deterministic, bounded workload: repeated incompressible-ish block.
        block = b"".join(hashlib.sha256(str(n).encode()).digest() for n in range(32768))
        with path.open("wb") as stream:
            for _ in range(256):
                stream.write(block)
        archive = self.root / "cancel.7z"
        args = [str(self.exe), "a", "-t7z", "-mx=9", "-mmt=1", str(archive), path.name,
                "-sccUTF-8", "-bd"]
        with tempfile.TemporaryFile() as log:
            proc = subprocess.Popen(args, cwd=self.source, stdin=subprocess.DEVNULL,
                                    stdout=log, stderr=subprocess.STDOUT)
            try:
                deadline = time.monotonic() + 30
                while not archive.exists():
                    if proc.poll() is not None or time.monotonic() >= deadline:
                        raise AssertionError("No live create operation to cancel")
                    time.sleep(0.01)
                # Archive creation is an observable milestone, not an arbitrary sleep.
                proc.send_signal(signal.SIGINT)
                rc = proc.wait(timeout=30)
                log.seek(0)
                output = log.read().decode("utf-8", errors="replace")
                self.report["commands"]["cancel/create"] = {
                    "argv": [arg.replace(str(self.root), "<TEMP>") for arg in args],
                    "signal": "SIGINT after output archive exists", "exit": rc,
                    "stdout": output.replace(str(self.root), "<TEMP>"),
                }
                self.report["observations"]["cancel/create"] = {
                    "exit": rc, "archive_remains": archive.exists(),
                    "break_message": "Break signaled" in output,
                }
                assert rc != 0, "Operation completed before cancellation; no cancellation evidence"
            finally:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expect", type=Path)
    parser.add_argument("--large", action="store_true")
    parser.add_argument("--cancel", action="store_true")
    args = parser.parse_args()
    if args.expect and args.expect.resolve() == args.report.resolve():
        parser.error("--report must not overwrite --expect")
    exe = args.executable.resolve(strict=True)
    report = {
        "schema": 1,
        "provenance": {
            "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
            "platform": platform.platform(), "system": platform.system(),
            "machine": platform.machine(), "python": platform.python_version(),
            "executable_sha256": digest(exe), "harness_sha256": digest(Path(__file__)),
            "source_diff": subprocess.check_output(["git", "diff", "HEAD", "--", "C", "CPP"], cwd=REPO, text=True),
            "large": args.large, "cancel": args.cancel,
        },
        "commands": {}, "observations": {}, "result": "FAILED",
    }
    try:
        with tempfile.TemporaryDirectory(prefix="archive-characterization-") as temp:
            capture = Capture(exe, Path(temp), report)
            capture.run("capabilities", "i", success=True)
            capture.basic()
            capture.passwords()
            if args.large:
                capture.large()
            if args.cancel:
                capture.cancel()
        if args.expect:
            expected = json.loads(args.expect.read_text(encoding="utf-8"))
            for field in ("system", "machine", "large", "cancel"):
                assert report["provenance"][field] == expected["provenance"][field], f"Baseline scope mismatch: {field}"
            assert expected["result"] == "PASS", "Baseline is not a successful capture"
            assert report["observations"] == expected["observations"], "Oracle disagreement: inspect reports; never auto-update expectations"
        report["result"] = "PASS"
    finally:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: {len(report['observations'])} observed operations; report={args.report}")


if __name__ == "__main__":
    main()
