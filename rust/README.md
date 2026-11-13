# S1 owned archive contracts

Status: implementation for independent same-card review (`t_31358a3f`).
This is a working, tested Rust **contract library**, not a new archiver. There is
no engine linkage, archive command implementation, Qt build, OS service, or GUI.
The existing executables, mature codecs, encryption and golden data are untouched.

## Boundaries

The seven package names and dependency directions follow
[architecture-target.md sections 2–5](../docs/ai-migration/architecture-target.md).
`archive-domain` has only std; `archive-app` depends on domain and the portable
platform boundary. Both explicitly forbid unsafe; S1 also inherits a workspace
unsafe prohibition for all packages. S2a must review any narrowly justified
relaxation in engine-sys/adapter, not weaken the domain/app prohibition.

`archive-cli` is the default member and currently a library composition boundary,
not an executable that fabricates success. `archive-qt` is a valid empty opt-in
library member, excluded from default and non-GUI workspace commands. Checking it
only verifies Cargo membership; Qt 6/CXX-Qt dependency selection remains Q2 and
presentation implementation remains S9a. `bridge/`, `ui/qml/` and platform OS
subdirectories reserve the architecture's paths without implementing them.

## Contract mapping and limits

- `identity.rs`: nonzero opaque IDs, monotonic non-wrapping generations, terminal
  close/exhaustion state, checked u64 page addition, single-epoch/handler selection.
  Selection retains display order (including duplicate choices), separately sorting
  and deduplicating the engine indices. `None` means All; an empty index list means
  no items. Only the future C++ adapter emits an engine sentinel.
- `lib.rs`, `properties.rs`: owned UTF-16 units, explicit lossy display, tagged
  Windows units/Unix bytes. Native paths are **unvalidated** values: the platform
  adapter checks host, NUL and representability before I/O, without normalization.
  No display-to-path conversion exists. Property IDs and Variant/Raw provenance
  survive, as do all original type tags, integer widths, unsupported values and
  empty-versus-missing records. Timestamp format/units/raw low/raw high/precision/
  definedness remain independent of optional display normalization. FILETIME's
  reserved precision fields follow the reviewed Q1 mapping, without interpretation.
- `outcomes.rs`: owned archive/entry/chain snapshots and capability identities;
  reader/writer presence is distinct from known operation support and application
  qualification. Failed open preserves chains and `non_open_error` without making
  a fake session. Call status, raw native diagnostics, ordered item results, counts,
  warnings and observed partial effects are separate; no bool-success shortcut.
- `requests.rs`: COpenType's exact retained defaults, handler-scoped properties,
  explicit operation-local code-page choice, and typed later-stage requests.
  Extract/overwrite vocabulary is traced to `CPP/7zip/UI/Common/ExtractMode.h`;
  scan/name policy vocabulary is traced to `CPP/7zip/UI/Common/Update.h`.
  These declarations do **not** enable options or choose new defaults: B04/S4 and
  B06/S6 must characterize/validate supported request subsets before dispatch.
  Creation does not expose arbitrary update/delete and never opens its output.
- `port.rs`: object-safe synchronous `ArchiveEngine` port, operation-scoped borrowed
  cancellation/progress/typed interaction endpoints, owned DTOs and redacted
  non-cloneable password storage. `NOverwriteAnswer` vocabulary comes from
  `IFileExtractCallback.h`; it must not be published before B04 measures allowed
  choices. An absent consumer is not permission to supply a default reply.

The domain types are not an externally serialized schema or another ABI. Q1's
[matched ABI v1](../docs/ai-migration/qualification/abi-v1.md) remains authoritative
for the facade. They also do not replace the live worker registry: caller-created
IDs, historical `Archive.state` or `SessionIdentity` objects cannot authorize
native access. S2a must allocate never-reused process IDs, revalidate live epoch,
chain and current bounds at every dispatch, copy views before release, ensure one
worker and callback quiescence, and reject unqualified operations before effects.
Public transport fields do not claim validation of every handler property, integer
original-type pairing, raw timestamp format or code-page combination.

General reply-once routing, cancellation wakeup/latency, report spooling, actual
filesystem conversion and rollback are later implementations, not simulated S1
behavior. Password clearing is best effort on controlled Vec storage, not a claim
of compiler/allocator/native-engine-wide erasure. Debug always redacts it.

## Reproducible checks

Q1 requires Rust/Cargo **1.97.1**, edition **2024**, `panic=unwind`, and no initial
external crates. `rust-toolchain.toml` applies inside `rust/`; explicit `+1.97.1`
also pins commands invoked from the repository root. Cargo generated the real
version-4 `Cargo.lock` with `cargo +1.97.1 generate-lockfile --manifest-path
rust/Cargo.toml`; every subsequent build/test/clippy uses `--locked`.

From the repository root:

```sh
python3 rust/tests/run_checks.py local
```

The same script runs on native `ubuntu-24.04`, `windows-2022`, and `macos-14` in
[the CI workflow](../.github/workflows/s1-native.yml), with Python 3.11. It checks
actual Rust host/release and exact Q1 Cargo/rustfmt/clippy identities, then runs:

```sh
python3 rust/tests/check_boundaries.py
python3 rust/tests/test_boundaries.py
cargo +1.97.1 fmt --manifest-path rust/Cargo.toml --all -- --check
cargo +1.97.1 build --manifest-path rust/Cargo.toml --locked
cargo +1.97.1 build --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt
cargo +1.97.1 test --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt
cargo +1.97.1 clippy --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt --all-targets -- -D warnings
cargo +1.97.1 build --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt --release
cargo +1.97.1 check --manifest-path rust/Cargo.toml --locked -p archive-qt
```

The boundary gate inspects all Cargo metadata dependency kinds/target conditions,
package sources, CLI-only defaults, native build scripts, manifest/lock pins and
unsafe inheritance. Negative controls inject renamed/target-specific/dev/build
forbidden edges, external sources, GUI defaults, native scripts and MSRV drift.
Its conservative source scan is a regression aid, not a Rust parser/sandbox;
compiler `forbid(unsafe_code)` and independent review remain mandatory.

`rust/evidence/<label>/commands.json` records the real git HEAD, host, argv,
exit codes and numbered raw logs. CI uploads that directory even on failure.
Local evidence cannot qualify Windows/macOS and Rust tests do not qualify native
archive behavior, FFI, GUI/desktop or release. Exact CI run/commit/artifact handles
are recorded in the Kanban review transition after direct verification.

## Implementation evidence

The implementation used successive RED→GREEN contract slices: text, identity/
selection, property snapshots, outcomes, and requests/port. Missing API compilation
failures were observed before introducing their types; boundary tests failed before
the checker existed. Internal read-only review identified a failed-open evidence
loss; a new failing test then drove explicit no-session chains/non-open diagnostics.
No engine result or fixture output was invented to satisfy a test.

Local full checks pass on Rust 1.97.1 x86_64-unknown-linux-gnu. Native CI is a
separate verification step, not inferred from that local result. The runtime
libraries currently contain owned contracts plus intentionally empty future
boundaries; no mature-engine compatibility or release claim is made.
