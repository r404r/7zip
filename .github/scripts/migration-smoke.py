#!/usr/bin/env python3
"""Smoke the existing native CLI; this is not the M1 compatibility oracle."""

import pathlib
import subprocess
import sys
import tempfile


def main():
    executable = pathlib.Path(sys.argv[1]).resolve(strict=True)
    fixtures = {
        "plain.txt": b"archive migration bootstrap\n",
        "nested/日本語.txt": "Unicode filename payload\n".encode("utf-8"),
        "nested/binary.bin": bytes(range(256)) * 4,
        "empty.txt": b"",
    }
    with tempfile.TemporaryDirectory(prefix="archive-migration-smoke-") as temp:
        root = pathlib.Path(temp)
        source = root / "source"
        for name, payload in fixtures.items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)

        def run(*args):
            result = subprocess.run(
                [str(executable), *map(str, args), "-sccUTF-8"],
                cwd=source,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                errors="replace",
                timeout=120,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"7zz {args[0]} failed ({result.returncode}):\n{result.stdout}"
                )
            return result.stdout

        for archive_format in ("7z", "zip"):
            archive = root / f"fixture.{archive_format}"
            output = root / f"extracted-{archive_format}"
            run("a", f"-t{archive_format}", archive, ".")
            listing = run("l", "-slt", archive)
            listed = {
                line.removeprefix("Path = ").replace("\\", "/")
                for line in listing.splitlines()
                if line.startswith("Path = ")
            }
            if not fixtures.keys() <= listed:
                raise RuntimeError(f"{archive_format}: listing misses fixture paths")
            run("t", archive)
            run("x", archive, f"-o{output}", "-y")
            extracted = {
                path.relative_to(output).as_posix(): path.read_bytes()
                for path in output.rglob("*")
                if path.is_file()
            }
            if extracted != fixtures:
                raise RuntimeError(f"{archive_format}: extracted paths or bytes differ")
            print(f"PASS {archive_format}: create/list/test/extract; 4 paths and bytes match")


if __name__ == "__main__":
    main()
