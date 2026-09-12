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
# S2a amendment: archive-engine-sys is the single FFI boundary crate, so it
# opts out of the workspace unsafe_code=forbid in favour of crate-level
# unsafe_code="deny" plus a per-site #[allow(unsafe_code)] next to each
# documented invariant. "deny" (not "allow") is what keeps every unsafe site
# explicit; an accidental one still fails the build.
#
# Every other crate keeps the workspace forbid, and the source scan below still
# rejects unsafe/extern/OS handle types in archive-domain, archive-app,
# archive-cli and archive-qt.
SCOPED_UNSAFE_CRATE = "archive-engine-sys"
SCOPED_UNSAFE_LEVEL = "deny"
UNSAFE_FREE_CRATES = ("archive-domain", "archive-app", "archive-cli", "archive-qt")
# archive-engine's contract tests drive the raw-ABI lifetime probes that live in
# archive-engine-sys, so a dev-only edge to that crate is expected. Library
# dependency edges are still exactly ALLOWED.
DEV_ONLY_ALLOWED = {"archive-engine": {"archive-engine-sys"}}
# Non-default features the facade slice introduces. They must stay off by
# default so the default workspace build links nothing native.
FACADE_FEATURE_CRATES = {
    "archive-engine-sys": {"facade": []},
    "archive-engine": {"facade": ["archive-engine-sys/facade"]},
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
        # Library edges stay exactly ALLOWED. A dev-only edge is permitted only
        # where DEV_ONLY_ALLOWED declares it, so a test dependency can never
        # smuggle in a production edge.
        library_deps = set()
        for dep in p["dependencies"]:
            require(dep["source"] is None, f"External dependency in {name}: {dep['name']}")
            if dep.get("kind") == "dev":
                permitted = ALLOWED[name] | DEV_ONLY_ALLOWED.get(name, set())
                require(dep["name"] in permitted,
                        f"Forbidden dev dependency in {name}: {dep['name']}")
                continue
            require(dep["name"] in ALLOWED[name],
                    f"Forbidden dependency in {name}: {dep['name']}")
            library_deps.add(dep["name"])
        require(library_deps == ALLOWED[name], f"Missing declared boundary: {name}")
        # The facade must stay a non-default feature: enabling it is what links
        # native code, and the default workspace build must link none.
        features = p.get("features", {})
        expected_features = FACADE_FEATURE_CRATES.get(name)
        if expected_features is None:
            require("facade" not in features, f"Unexpected facade feature on {name}")
        else:
            for feature, enables in expected_features.items():
                require(features.get(feature) == enables,
                        f"Facade feature drift on {name}: {features.get(feature)}")
            require(features.get("default", []) == [],
                    f"Facade enabled by default on {name}")


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
    # The unsafe-free crates keep their crate-level guard AND stay free of
    # unsafe, extern and OS handle types in every source file.
    for name in UNSAFE_FREE_CRATES:
        package = ROOT / "crates" / name
        require("#![forbid(unsafe_code)]" in (package / "src/lib.rs").read_text(), "Crate unsafe guard removed")
        for path in (package / "src").rglob("*.rs"):
            check_source(path.read_text())
    # archive-engine is the safe adapter: it must contain no unsafe at all, so
    # its own sources are scanned too even though it links to the FFI crate.
    for path in (ROOT / "crates/archive-engine/src").rglob("*.rs"):
        check_source(path.read_text())
    # The card's own contract tests must not reintroduce unsafe either.
    tests = ROOT / "crates/archive-engine/tests"
    if tests.is_dir():
        for path in tests.rglob("*.rs"):
            check_source(path.read_text())
    for name in ALLOWED:
        package = tomllib.loads((ROOT / "crates" / name / "Cargo.toml").read_text())
        if name == SCOPED_UNSAFE_CRATE:
            # The single FFI boundary crate: scoped unsafe at "deny", and
            # therefore deliberately NOT inheriting the workspace lint table.
            require("lints" not in package or "workspace" not in package.get("lints", {}),
                    f"{name} must not inherit the workspace forbid it needs to relax")
            require(package["lints"]["rust"]["unsafe_code"] == SCOPED_UNSAFE_LEVEL,
                    f"Scoped unsafe level drift: {name}")
            # Every unsafe site is individually opted in next to its invariant.
            for path in (ROOT / "crates" / name / "src").rglob("*.rs"):
                text = path.read_text()
                allows = text.count("#[allow(unsafe_code)]")
                blocks = len(re.findall(r"\bunsafe\s*(?:\{|fn\b|extern\b|impl\b|trait\b)", text))
                require(allows >= 1 or blocks == 0,
                        f"Unsafe without an explicit per-site allow: {path.name}")
        else:
            require(package["lints"]["workspace"] is True, f"Lint inheritance removed: {name}")
            require("rust" not in package.get("lints", {}),
                    f"{name} must not override the workspace lint table")


if __name__ == "__main__":
    check_metadata(metadata())
    check_files()
    print("S1 dependency, unsafe/OS boundary, Cargo.lock and Q1 manifest pins: PASS")
    print("S2a scoped unsafe confined to archive-engine-sys; facade feature off by default")
