# Q1 qualification handoff

Task `t_f4d107ea`, isolated branch `wt/t_f4d107ea`. Status: candidate for independent
review. No production bridge, Rust application workspace, Qt, codec change, shared
branch merge or release is included.

## Deliverables

- [toolchains.json](toolchains.json): exact Rust/MSRV/edition/targets, Cargo.lock
  policy and native compiler/build-driver/runtime pins. Runner labels are selectors,
  NOT immutable pins; [check-pins.py](check-pins.py) rejects observed version drift.
- [ABI v1](abi-v1.md), [normative header](archive_bridge_v1.h) and
  [frozen layout](abi-layout.txt): public namespace authorized by the human, exact
  initial declarations, widths/tags/calling convention and lifetime contract.
- [engine-build-schema.json](engine-build-schema.json): version 1 manifest contract,
  including the non-self-referential input-only identity for later facade handshake.
- [engine-build.json](engine-build.json): actual retained native product inputs,
  flags evidence references, registration/codec/hash capability observations and
  preserved product differences. It intentionally has facade_commit=null and no
  qualified application operations.
- [license inventory](license-inventory.md), [machine inventory](license-inventory.json)
  and [native observations](native-observations.json): auditable evidence and limits.

The prior obscured naming proposal is superseded, not reconstructed. The Q1
namespace is archive_bridge_v1_; architecture-target.md and ADR-0001 contain the
same amendment and precedence. Only the independently reviewed Q1 commit may be
consumed by S1/S2a and other downstream tasks.

## Actual native qualification

The dedicated `.github/workflows/q1-native.yml` runs on native ubuntu-24.04,
windows-2022 and macos-14. It builds Alone2, Format7zF and Console from the same
source checkout, executes the retained products, calls the original library's
registration exports, compares the existing native M1 baselines and compiles/runs
C11/C++17/Rust 2024 declaration-layout probes. It does not use Wine or a Linux
cross-build as Windows evidence.

The captured native reference at commit
`66bad6556690003f83568b97e597f7c95e957d6f` passed all three native jobs in
https://github.com/r404r/7zip/actions/runs/34561288314 . Exact-head confirmation for
the final review commit and final artifact handles are recorded on the task card,
so a document does not claim a self-referential final commit hash.

Each native Alone2 run passed the existing 41-operation baseline comparison.
C/C++/Rust probes matched 25 struct sizes/alignments and every field offset on each
native target. The Linux local supplement also built with GCC 15.2.0 and GNU Make
4.4.1; it is not substituted for the canonical GCC 13.3.0 CI pin.

## Capability findings that must not be erased

All three native Alone2 `i` capability sections matched exactly in the captured
reference: 61 CLI format rows, 25 codecs and 10 hashers. This is NOT a claim that
all handlers have full fixture coverage or that all format rows are CArcInfo slots.
The direct Format7zF observer reports 60 library registration records; the extra
Hash handler is added by UI/Common/HashCalc.cpp's Codecs_AddHashArcHandler. The
manifest retains both categories, and the ABI explicitly represents an absent
native registration ID rather than inventing one for Hash.

Standalone and loaded products differ in TimeFlags presentation for 7z, gzip,
tar, wim and zip. Source evidence: CArcInfoEx initializes TimeFlags to zero in
LoadCodecs.h; LoadCodecs.cpp:808-845 populates built-in formats without copying
arc.TimeFlags, while the dynamic path at 474-477 obtains kTimeFlags. The direct
ArchiveExports.cpp:118-119 query returns registered flags/time flags. Preserve
both observations. The ABI reports effective CCodecs capabilities while the
manifest also retains raw registered metadata. Q1 does not patch retained policy
or silently use richer metadata to change creation/timestamp defaults.

## Reproduction and verification commands

From the isolated repository root, with the exact native tools in toolchains.json:

    rustup toolchain install 1.97.1 --profile minimal --component rustfmt --component clippy
    python3 docs/ai-migration/qualification/collect-native.py --output .q1-evidence/fresh-native
    python3 docs/ai-migration/qualification/check-layout.py --output .q1-evidence/fresh-native/layout
    python3 docs/ai-migration/qualification/check-pins.py .q1-evidence/fresh-native

On Windows use `python`, initialize the exact x64 MSVC environment first, and use
a fresh isolated checkout/output. The collector refuses reused Unix object output;
NMAKE uses the retained x64 product directories, so a fresh worktree is required
for an auditable Windows compilation capture. No environment or global loader
search-path dump is needed. Actual compiler/make/link/observer commands and exit
codes are in each artifact's commands.json; emitted compilation/link commands
remain in build.log, Format7zF-build.log and Console-build.log.

After downloading the three artifacts from the same Q1 run into an evidence root:

    python3 docs/ai-migration/qualification/audit-inputs.py .q1-evidence/downloaded-run
    python3 docs/ai-migration/qualification/summarize-native.py .q1-evidence/downloaded-run --output docs/ai-migration/qualification/native-observations.json
    python3 docs/ai-migration/qualification/validate.py --evidence .q1-evidence/downloaded-run

`validate.py` uses jsonschema 4.26.0 (observed installed validation tool, not a
native or Rust runtime dependency). Use an isolated validation environment if
needed; native capture and layout scripts otherwise use Python standard library
only. Validation checks JSON schema, all selected source/notice hashes, three OS
coverage, numeric ranges, absent RAR writers/encoders, relative document links,
artifact digests, frozen layout and native pins. Four invalid-schema controls and
two pin/layout-drift controls plus [test-pins.py](test-pins.py) use in-memory data
or isolated temporary copies; no committed expected regression data is modified.
Run `python3 docs/ai-migration/qualification/test-pins.py <capture> [<capture> ...]`
to replay the controls independently. CI runs these controls on each native capture.

### Pin enforcement audit (R1)

The allowed native identity mapping is explicit: Linux/x86_64 maps to
x86_64-unknown-linux-gnu, Windows/AMD64 to x86_64-pc-windows-msvc, and Darwin/arm64
to aarch64-apple-darwin. `check-pins.py` requires the exact observed machine and
Rust host equal to the mapped native target, which must also be in Rust's target
allowlist. Equal 64-bit struct layouts are not evidence of target identity.
These are native builds using the collector's fixed commands, not authorization
for arbitrary cross-compilation or compiler target overrides.

Enforced observed identities: C/C++ compiler banners, build-driver banner, Linux
binutils/glibc/libgcc/libstdc++/make package versions, Windows VCTools/SDK/UCRT,
macOS SDK/Xcode and linked runtime versions, Rust release/host, and exact captured
Cargo/clippy/rustfmt versions. R1 adds the previously omitted libgcc-s1 pin without
changing its captured version. Independent mutation controls reject every such
version category, machine, unknown system and layout drift with field diagnostics;
unchanged real captures must pass first. The original captured evidence stays intact.

Other toolchains.json fields are not independent observed version pins:
compiler_family/compiler_version summarize the checked banner; runner_selector
is workflow placement, observed_os is historical context, and make_fragments,
build_command, mode and runtime_policy describe the fixed collector/build-log
contract and ownership policy. Selected flags/inputs remain audited in
engine-build.json, not inferred from a successful pin check. Edition=2024 and
panic=unwind are explicit check-layout.py compiler arguments, and rust-std is
exercised by the compiled native Rust probe. MSRV equals the checked release.
Cargo.lock fields are S1 obligations, not a claim that Q1 built a Rust workspace.

The existing preservation checks remain applicable:

    python3 .github/tests/release_version_test.py
    python3 .github/tests/change_notice_test.py .
    python3 .github/tests/lang_files_test.py .
    python3 .github/tests/shell_ext_lang_reload.py .
    git diff --check
    git diff d9c3b65 --exit-code -- C CPP Asm AGENTS.md .github/tests

## Investigation corrections and limits

- The first whole GNU make database capture unnecessarily included unrelated
  environment variables. A name-only audit found no token/password/API-key-named
  variables (only SSH_AUTH_SOCK on local/macOS); this is not a general secret-leak
  certification. The two uploaded Unix artifacts from run 34557825987 were deleted
  and their removal verified, local database copies were replaced with removal
  markers, and subsequent captures use an explicit variable whitelist. Do not use
  those superseded database digests as current evidence.
- Native run 34559458796 exposed a real Windows observer link failure: Archive2.def
  uses PRIVATE exports, so the generated import library cannot satisfy these calls.
  The observer now uses the original typed GetProcAddress pattern and an explicit
  absolute library path. Run 34559865983 verified the fix on native Windows; no
  retained export definitions or tool policies were weakened.
- An initial inventory equality assertion exposed Hash's coordinator provenance.
  The corrected comparison requires all raw library formats PLUS the separately
  sourced Hash row and its actual selected HashCalc.cpp input. It does not drop a
  golden row or permit arbitrary missing/extra formats.
- A matched declaration layout does not exercise a real Rust facade. S2a still
  owns actual exports, version mismatch, loading, failure injection, callback
  quiescence, allocator/handle lifetime, sanitized native tests and no-dead-strip
  proof for its own selected library. Later extract/test/create ABI revisions
  remain staged, not enabled by reserved names.
- This is native CLI/reference evidence, not complete archive-format behavior,
  code-page, malicious-path, password, overwrite, metadata, cancellation, GUI,
  desktop, licensing-distribution or release certification. B01–B08 and Q2/Q3 gates
  remain intact. No shared branch was merged and no release was published.
