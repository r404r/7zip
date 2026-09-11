"""Execute S1 native Rust checks and preserve actual commands/output as evidence."""
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "rust/evidence" / (sys.argv[1] if len(sys.argv) > 1 else "local")
PINS = json.loads((ROOT / "docs/ai-migration/qualification/toolchains.json").read_text())
RUST = PINS["rust"]
CARGO = ["cargo", "+" + RUST["toolchain"]]
COMMON = ["--manifest-path", "rust/Cargo.toml", "--locked"]
WORKSPACE = ["--workspace", "--exclude", "archive-qt"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    report = {
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "os": platform.system(), "machine": platform.machine(),
        "scope": "S1 owned contracts only; no facade/CLI operations/Qt/desktop qualification",
        "commands": records,
    }

    def run(command):
        result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        log = f"{len(records):02d}.log"
        (OUT / log).write_text(result.stdout, encoding="utf-8")
        records.append({"argv": command, "exit_code": result.returncode, "log": log})
        (OUT / "commands.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("+ " + " ".join(command), flush=True)
        print(result.stdout, end="", flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)
        return result.stdout.strip()

    rustc = run(["rustc", "+" + RUST["toolchain"], "-vV"])
    fields = dict(line.split(": ", 1) for line in rustc.splitlines() if ": " in line)
    expected = PINS["native"].get(platform.system())
    if expected is None or fields.get("host") != expected["target"] or fields.get("release") != RUST["toolchain"]:
        raise SystemExit("Unqualified Rust host/compiler; requalification required")
    for command, key in ((["--version"], "cargo"), (["fmt", "--version"], "rustfmt"), (["clippy", "--version"], "clippy")):
        if run(CARGO + command) != RUST["component_versions"][key]:
            raise SystemExit(f"Q1 component drift: {key}")
    run([sys.executable, "rust/tests/check_boundaries.py"])
    run([sys.executable, "rust/tests/test_boundaries.py"])
    run(CARGO + ["fmt", "--manifest-path", "rust/Cargo.toml", "--all", "--", "--check"])
    run(CARGO + ["build"] + COMMON)
    run(CARGO + ["build"] + COMMON + WORKSPACE)
    run(CARGO + ["test"] + COMMON + WORKSPACE)
    run(CARGO + ["clippy"] + COMMON + WORKSPACE + ["--all-targets", "--", "-D", "warnings"])
    run(CARGO + ["build"] + COMMON + WORKSPACE + ["--release"])
    # Parseable opt-in member, still no Qt dependencies or runtime.
    run(CARGO + ["check"] + COMMON + ["-p", "archive-qt"])
    report["result"] = "PASS"
    (OUT / "commands.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
