# M1: characterization and regression baseline

Task `t_f4afeee1`, branch `ai/migration-m1`. This is a bounded legacy CLI
baseline, not full archive-format, FFI, GUI or desktop parity. No C/C++, Rust,
codec, encryption or GUI implementation is changed. M3 must enforce the evidence
prerequisites below before creating affected production work.

## Provenance and reproducibility

The oracle is this fork's `CPP/7zip/Bundles/Alone2` (`7zz`), built from
`3aea9f861807d6f9af1bc1ab0ef489030233ec59`, including reviewed M0 commit
`1b54c95dd0a49324d963b9516996fdd0a7f09601`. Both were already ancestors of the
isolated task branch. The source checkout was verified on
`ai/migration-bootstrap-20260911`; both AGENTS.md and a clean task branch were
checked before work. No parent cherry-pick was needed.

Local execution: Linux `7.0.0-28-generic x86_64`, GCC/G++
`15.2.0 (Ubuntu 15.2.0-16ubuntu1)`, GNU Make `4.4.1`, Python `3.11.16`.
The actual CLI identifies itself as 7-Zip (z) `26.03`, dated `2026-09-03`.
The JSON reports include the executable and harness SHA-256, engine source diff,
commit, platform, architecture, Python, argv, stdout/stderr, exit codes, fixture
hashes and observed metadata. `commands.capabilities` preserves actual `7zz i`
formats/codecs/hashers output, not a guessed supported-format list.

Checked-in reports, copied directly from successful local executions (not typed
or synthesized expected data):

* [Linux core oracle](../../.github/tests/oracles/linux-x86_64-core.json):
  41 observed operations; an independent second invocation matched observations.
* [Linux extended oracle](../../.github/tests/oracles/linux-x86_64-extended.json):
  46 observed operations; another full invocation matched observations.

Additional reports were downloaded from native CI run
[34554685505](https://github.com/r404r/7zip/actions/runs/34554685505), exact head
`adcf6ed719c07b89cc1d4f93af65b81e84582a4a` (no engine diff from the local oracle).
Git normalizes JSON container CRLF to LF via the oracle directory's attributes;
all captured JSON values are unchanged:

* [Windows AMD64 core](../../.github/tests/oracles/windows-amd64-core.json):
  Windows `10.0.26100`, MSVC `19.51.36256`, Python `3.11.9`.
* [macOS arm64 core](../../.github/tests/oracles/macos-arm64-core.json):
  Darwin `25.6.0`, Apple clang `21.0.0`, Python `3.11.9`.

Both native jobs passed 41-operation capture/repeat and all three negative
controls; Windows also passed existing filename code-page assertions. Ubuntu's
job passed the checked-in Linux comparison. These are CLI-only results, not GUI
or desktop evidence. Each platform now has its own frozen core comparison in CI;
runner architecture drift fails closed rather than borrowing another oracle.

These captures become approved baselines only after independent reviewer PASS.
`commands` retain raw execution context apart from temporary-root substitution
with `<TEMP>` and CRLF-to-LF conversion. Stable comparison uses `observations`,
not volatile console banners, compression sizes, salts or temporary paths.
Listings compare sorted entry path/size/CRC/encryption/folder fields. Extraction
compares full regular-file path sets, SHA-256, byte count, mtime nanoseconds and
mode. This does not compare directory metadata or native ACLs. Reports are never
an instruction to change legacy behavior.

## Commands

From repository/worktree root (Python >=3.11, no third-party Python packages):

```sh
mkdir -p .m1-artifacts/build
make -j2 -C CPP/7zip/Bundles/Alone2 -f ../../cmpl_gcc.mak \
  O="$PWD/.m1-artifacts/build" > .m1-artifacts/build.log 2>&1
python3 .github/tests/archive_characterization.py .m1-artifacts/build/7zz \
  --report .m1-artifacts/linux-core-repeat.json \
  --expect .github/tests/oracles/linux-x86_64-core.json
python3 .github/tests/archive_characterization.py .m1-artifacts/build/7zz \
  --large --cancel --report .m1-artifacts/linux-full-repeat.json \
  --expect .github/tests/oracles/linux-x86_64-extended.json
python3 .github/tests/archive_characterization_test.py .m1-artifacts/build/7zz \
  .github/tests/oracles/linux-x86_64-core.json
```

Omitting `--expect` records real observations and checks basic round-trip/CRC
invariants; it does NOT establish agreement with a reviewed golden. `--expect`
requires equal OS, architecture and optional-case selection. Native macOS and
Windows must first capture their own reports; Linux modes/exits are not their
canonical oracle. Never point `--report` at a checked-in oracle for routine runs.
The harness rejects a report path equal to `--expect`. Oracle replacement is a
separate provenance-backed reviewed change, never an automatic failure remedy.

`--large` creates a sparse logical input of 4,294,967,313 bytes (zeros with final
`Z`), compresses it with 7z `-mx=1 -mmt=2`, lists/tests/extracts it, and checks
streaming SHA-256 and full size. Budget at least 10 GiB temporary free space and
600 seconds per command; extraction may allocate the full file. It is opt-in.
`--cancel` is explicitly POSIX-only: 256 MiB of repeated deterministically
SHA-256-derived data, single-threaded create, SIGINT after the output archive
exists, 30-second bounded wait, cleanup on failure. Existence is a limited create
milestone, NOT evidence of cancellation at every internal stage or a latency SLA.
No kill is counted as successful cancellation; kill is only harness cleanup.
All test inputs/output destinations live in controlled TemporaryDirectory roots.

## Fixture origin and measured coverage

Fixtures are local public test data defined in
[archive_characterization.py](../../.github/tests/archive_characterization.py):
ASCII text, empty file, nested Japanese/non-BMP filename, bytes 0..255 repeated.
Files use fixed Unix timestamp `1700000000`, mode `0644`; the overwrite victim
has distinct bytes and timestamp `1699999900`. Public synthetic passwords are
embedded solely for tests. Never pass real user passwords or archives here.
Truncation keeps the first 16 bytes of a real oracle-created archive. CRC damage
flips one byte in a unique ZIP Store payload while retaining declared headers/CRC.
Archive bytes are generated on each invocation, not frozen interoperability
fixtures; encrypted byte identity is intentionally not an assertion.

| Area | Runnable probe and local measured result | Limit / prerequisite for expansion |
| --- | --- | --- |
| Create/list/test/extract | 7z and ZIP; all exit 0; exact payload/name round trip and listing CRC | Other formats/methods, multivolume, external archives: B01 |
| Unicode/nesting | Japanese plus non-BMP filename, nested path; both formats retained names and bytes | Invalid byte names, normalization/case collisions, reserved/long paths: B02 |
| Metadata | Fixed whole-second mtime and 0644 survived local extraction | Directory/precision/timezone/permissions matrix, ADS/ACL: B03 |
| Overwrite | `-aoa` replaces; `-aos` preserves victim; `-aou` adds incoming `plain_1.txt`; `-aot` moves victim to `plain_1.txt`; both formats exit 0, hashes/mtime recorded | Interactive, multiple collisions, readonly and unsafe paths: B04 |
| Encryption | 7z encrypted headers + non-ASCII password; ZIP AES256 and ZipCrypto with ASCII; correct test/extract exit 0 | Empty-password archive creation, boundary callbacks, external encrypted fixtures: B05 |
| Password failures | Wrong and explicit `-p` with empty stdin: exit 2; missing password with EOF: exit 255 for all three methods | These are noninteractive CLI observations, not undefined-vs-empty callback equivalence |
| Non-ASCII ZIP creation | AES/ZipCrypto exit 2; raw `E_INVALIDARG` preserved | Legacy `ZipHandlerOut.cpp:415-416` rejects non-simple-ASCII; do not silently make it succeed |
| Corruption | 16-byte truncated ZIP/7z exit 2; stored ZIP payload flip exit 2 with `CRC Failed` diagnostic | Other damage locations, unsupported methods, partial extraction: B01/B04 |
| Large | >4 GiB 7z create/list/test/extract exit 0; size and streaming digest match | ZIP64, sparse allocation semantics, overflow/short I/O/full disk: B03 |
| Cancellation | POSIX create SIGINT exit 255, `Break signaled`, output archive absent; repeated run matched | Windows console control event, extract/update/scan/open stages: B06 |
| Fork filename code pages | Existing `zip_name_encoding.py` preserved; Linux execution explicitly REPORT ONLY | Native Windows assertions in CI; broader precedence/reused-handler corpus: B02 |

Initial exploration mistakenly required non-ASCII ZIP creation to succeed.
The actual execution returned `E_INVALIDARG`; source inspection above explained
why. The harness now records that rejected operation separately and tests ASCII
ZIP success. No prior golden was edited and no engine fix/semantic change was
made. This is characterization of a discovered constraint, not approval to change
password handling. The initial failed capture remains in local `.m1-artifacts/`.

## Existing checks and CI

All existing files and expectations are preserved:

* `.github/scripts/migration-smoke.py`: 7z/ZIP four-file round trip, still passes.
* `.github/tests/zip_name_encoding.py`: native Windows code-page expectations;
  on Linux it reports observations only, which is not code-page certification.
* `release_version_test.py`, `release_notes_test.sh`: release/tag/history guards.
* `change_notice_test.py`: upstream notice guard.
* `lang_files_test.py`: assets/resource references; `shell_ext_identity.py` and
  `shell_ext_lang_reload.py`: source guards, not live Explorer behavior.
* Existing `migration-native-cli.yml` and `build-windows.yml` are unchanged.

New [characterization-native.yml](../../.github/workflows/characterization-native.yml)
builds native CLI on Ubuntu, macOS and Windows (MSVC x64, not Wine/cross-compile),
runs capture and independent repeat, harness negative controls, Linux frozen
and native Windows/macOS frozen baseline comparisons, and native Windows encoding
assertions. Artifacts retain
reports and build/toolchain logs even on failure. Extended Linux comparison is
available via `workflow_dispatch` with `extended=true`. Capture and repeat alone
are not frozen regression approval; reviewer must inspect the committed native
reports before approving their baselines. Native run URLs and exact heads are
recorded in the task review handoff when available. Do not infer CI success merely
from the existence of workflow YAML.

## Explicit evidence blockers for M3 (not waived by M1 PASS)

M3 must create reviewed characterization prerequisites and dependency edges for
these gaps before affected production cards become runnable. A gap is not itself
a request to invent policy; routine additional fixture work remains engineering.
Any oracle conflict or proposed semantics change must become a typed
`needs_input` human gate, with retain/approve-change/defer options and impacts.
Never archive an unresolved prerequisite to release its child.

| Blocker | Required characterization before changing this behavior |
| --- | --- |
| B01 format/error interoperability | Retained-format corpus with actual generator/version/license provenance, immutable archive bytes and hashes, unsupported/CRC/truncation/volume outcomes. Current self-round-trip cannot detect coordinated writer/reader drift. Blocks claims of full engine/format/error parity. |
| B02 native path/name identity | Native Windows CP932/936, EFS and valid/invalid Unicode-extra CRC precedence, scoped/unscoped properties and reused-handler reset; Linux byte names; macOS normalization; reserved/long paths and collisions. Blocks filename conversion/property rewrites and UTF-8-only identity. |
| B03 filesystem fidelity | Native Windows/Linux/macOS timestamps/precision/time zones, directory metadata, executable/readonly permissions, ACL/ADS/security, sparse/ZIP64, short I/O/full disk. Blocks filesystem and broad large-file parity. |
| B04 extraction safety | Sandboxed traversal/absolute paths, symlink/hardlink/reparse attacks, readonly, repeated collision names, interactive overwrite and partial failure disposition. Blocks extraction policy/path/link/delete/overwrite rewrites beyond measured cases. |
| B05 password boundary | Native empty/undefined/wrong/non-ASCII callback state matrix, header encryption errors, supported-method corpus and password prompt lifecycle. Blocks password/crypto changes and flattened error mapping. CLI `-p` is not proof of an FFI contract. |
| B06 cancel/progress | Native Windows console control event harness, cancellation at scan/open/create/update/extract, prompt/pause/resume, existing archive integrity and partial output, join/reentrancy tests. Blocks cancellation infrastructure parity claims; POSIX create-only is insufficient. |
| B07 GUI/desktop/settings | Native File Manager/Explorer, saved-vs-transient settings, reopen positions, drag/drop, coexistence/install, language reload and accessibility. Blocks desktop/GUI parity, regardless of CLI CI PASS. |
| B08 FFI ownership/concurrency | Bridge-specific lifetime/failure/exception/allocator/drop-order/sanitizer/stress tests after M2 settles facade. No bridge implementation exists in this card; CLI cannot prove FFI safety. |

These map to [M0 risks R01-R14](migration-risks.md). Retain the mature C/C++
engine and Qt 6/QML -> CXX-Qt -> Rust direction. M1 and M2 independent PASS remain
prerequisites for M3; this document does not authorize skipping to GUI or codecs.

## Validation and handoff

Actual local commands: build and both baseline/repeat commands above exit 0;
core reports 41 operations, extended reports 46. Existing smoke passes for both
formats. Also executed, all exit 0:

```sh
python3 .github/tests/release_version_test.py
python3 .github/tests/change_notice_test.py "$PWD"
python3 .github/tests/lang_files_test.py "$PWD"
python3 .github/tests/shell_ext_identity.py "$PWD"
python3 .github/tests/shell_ext_lang_reload.py "$PWD"
bash .github/tests/release_notes_test.sh
python3 .github/tests/zip_name_encoding.py .m1-artifacts/build/7zz
```

Observed existing summaries: `0 failed`; `34 modified upstream files, 0 without a
notice`; `93 language files checked, 0 problem(s)`; reload `0 problem(s)`.
Harness negative controls deliberately damage only temporary copies of a real
capture and verify mismatch rejection, wrong-platform rejection, and refusal to
overwrite the expected file. These are test inputs, never golden evidence.

Local build/report directory:
`/home/ding/work/github/r404r/7zip/.worktrees/t_f4afeee1/.m1-artifacts/` (ignored).
Durable evidence is the four checked-in JSON reports, workflow artifacts and this document;
review handoff records final commits and CI handles. Exact source checks/diff,
negative-control results and remaining native risks belong in that handoff.
No shared branch integration or release publication is performed by the author.
