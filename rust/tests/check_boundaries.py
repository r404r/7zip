"""Fail closed on S1 dependency edges, native code and Q1 Rust pin drift.

This is an architectural regression gate, not a Rust security sandbox/parser.
Cargo's unsafe_code=forbid is the compiler-enforced safety gate. The conservative
source scan can intentionally reject comments and requires review for extensions.
"""
import json
from pathlib import Path
import re
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT.parent / "docs/ai-migration/qualification/toolchains.json").read_text())
RUST = PINS["rust"]
ALLOWED = {
    "archive-domain": set(),
    "archive-platform": {"archive-domain"},
    "archive-app": {"archive-domain", "archive-platform"},
    "archive-engine-sys": set(),
    "archive-engine": {"archive-domain", "archive-engine-sys"},
    "archive-cli": {"archive-app", "archive-domain", "archive-engine", "archive-platform"},
    "archive-qt": {"archive-app", "archive-domain", "archive-engine", "archive-platform"},
}


def metadata():
    return json.loads(subprocess.check_output([
        "cargo", "+" + RUST["toolchain"], "metadata", "--manifest-path", str(ROOT / "Cargo.toml"),
        "--locked", "--offline", "--format-version", "1",
    ], text=True))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_metadata(data):
    packages = data["packages"]
    require({p["name"] for p in packages} == set(ALLOWED), "Unexpected/missing workspace package")
    ids = {p["id"] for p in packages}
    require(set(data["workspace_members"]) == ids, "External/non-member package")
    cli = next(p["id"] for p in packages if p["name"] == "archive-cli")
    require(data["workspace_default_members"] == [cli], "CLI-only default membership required")
    for p in packages:
        name = p["name"]
        require(p["source"] is None, f"External source: {name}")
        require(p["edition"] == RUST["edition"], f"Edition drift: {name}")
        require(p["rust_version"] == RUST["msrv"], f"MSRV drift: {name}")
        require(p["publish"] == [], f"Publication enabled: {name}")
        require(all("custom-build" not in t["kind"] for t in p["targets"]), f"Native/build script in S1: {name}")
        for dep in p["dependencies"]:
            require(dep["name"] in ALLOWED[name] and dep["source"] is None,
                    f"Forbidden dependency in {name}: {dep['name']}")
        require({d["name"] for d in p["dependencies"]} == ALLOWED[name], f"Missing declared boundary: {name}")


def check_source(text):
    # Check token spelling including grouped use statements. No OS objects or
    # FFI belong in domain/app; do not confuse lossless NativePath with an OS API.
    require(not re.search(r"\bos\s*::|\bextern\b|\bunsafe\s+(?:fn|impl|trait|\{)|\b(?:HWND|HANDLE|RawFd|RawHandle)\b", text),
            "Native API or unsafe code in domain/app")


def check_files():
    toolchain = tomllib.loads((ROOT / "rust-toolchain.toml").read_text())["toolchain"]
    require(toolchain["channel"] == RUST["toolchain"], "Toolchain drift")
    require(set(toolchain["components"]) == {"rustfmt", "clippy"}, "Component drift")
    manifest = tomllib.loads((ROOT / "Cargo.toml").read_text())
    require(manifest["workspace"]["lints"]["rust"]["unsafe_code"] == "forbid", "Unsafe lint disabled")
    for profile in ("dev", "release"):
        require(manifest["profile"][profile]["panic"] == RUST["panic"], "Panic policy drift")
    lock = tomllib.loads((ROOT / "Cargo.lock").read_text())
    require(lock["version"] == RUST["cargo_lock"]["format_version"], "Lock format drift")
    require(all("source" not in p for p in lock["package"]), "External lock dependency")
    for name in ("archive-domain", "archive-app"):
        package = ROOT / "crates" / name
        require("#![forbid(unsafe_code)]" in (package / "src/lib.rs").read_text(), "Crate unsafe guard removed")
        for path in (package / "src").rglob("*.rs"):
            check_source(path.read_text())
    for name in ALLOWED:
        package = tomllib.loads((ROOT / "crates" / name / "Cargo.toml").read_text())
        require(package["lints"]["workspace"] is True, f"Lint inheritance removed: {name}")


if __name__ == "__main__":
    check_metadata(metadata())
    check_files()
    print("S1 dependency, unsafe/OS boundary, Cargo.lock and Q1 manifest pins: PASS")
