# S2a-DEV evidence: retained-engine facade handshake, context and capabilities

Task: `t_178b131f`. Acceptance level: **DEVELOPMENT**, single host. This is
**not** Windows/macOS/Linux release qualification. See
[development-first-sequencing.md](../development-first-sequencing.md) section 1
for what this level does and does not mean.

Scope delivered: exactly four of the exports declared in the reviewed Q1 header
`archive_bridge_v1.h` — `handshake`, `create_context` / `destroy_context`,
`capabilities`, `result_destroy` — implemented as a C++ RAII facade over the
retained engine, plus private `repr(C)` Rust bindings and a safe adapter behind
a non-default Cargo feature.

Every other name the reviewed header reserves (`open`, `entries`, `close`,
`extract`, `test`, `create`) is **not defined**. The header was copied
byte-for-byte and nothing was deleted from it; the C++ translation unit simply
does not define the out-of-scope exports. A reserved name is not an
implementation and not permission to expose its operation.

## 1. Host, toolchain and commit

| Item | Value |
| --- | --- |
| OS | Ubuntu 26.04.1 LTS, Linux 7.0.0-28-generic |
| Architecture | x86_64 |
| Rust target | x86_64-unknown-linux-gnu (ABI target code 1) |
| C compiler | `gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0` |
| C++ compiler | `g++ (Ubuntu 15.2.0-16ubuntu1) 15.2.0` |
| Build driver | `GNU Make 4.4.1` |
| glibc | `glibc 2.43` |
| rustc | `rustc 1.97.1 (8bab26f4f 2026-07-14)` |
| cargo | `cargo 1.97.1 (c980f4866 2026-06-30)` |
| rustfmt | `rustfmt 1.9.0-stable (8bab26f4f6 2026-07-14)` |
| clippy | `clippy 0.1.97 (8bab26f4f6 2026-07-14)` |
| Python | `Python 3.11.16` |
| Task branch | `wt/t_178b131f` |
| Base commit | `9d9e72367f549f306fabeac3b2f61db949584e81` |
| Implementation commit (round 1) | `bc244efca0f4af9ba6319c0ef6c03c62e8afa155` |
| Review round 1 fix commit | `336ebd9c998fca71544f291fdc4ccaa3b0d6b4ce` |

This host toolchain is the `local_supplement` recorded in
[toolchains.json](toolchains.json) `policy`, **not** the canonical native CI
pin (`Linux` pins GCC 13.3.0 / GNU Make 4.3 / glibc 2.39 on `ubuntu-24.04`).
Requalifying against the canonical pins is part of the deferred native campaign,
not something this development slice claims.

Prerequisites verified before work: the source checkout was on
`ai/migration-bootstrap-20260911`, the task worktree contains `AGENTS.md`, and
all three reviewed parent commits are ancestors of the task branch —
M3 `0706af3d714e8c2701691a19a0c663ae7b749c88`,
Q1 `5f07f21a6516e345db199d3d78a3a984118574a5`,
S1 `e809c92b2d493412882f8a623f05fbe2ee508ff2`.

## 2. Deliverables and digests

| Path | SHA-256 |
| --- | --- |
| `rust/bridge/archive_bridge_v1.h` | `eabe714b31e2076735b8313c06618e5dbb3db4ea924cbef244b78a8b107ee26d` |
| `rust/bridge/archive_bridge_v1.cpp` | `e3d62f6cc0741668e3e18770227d475fe0e7e731ed469952fc1a99cc62d5251e` |
| `rust/bridge/makefile.gcc` | `b3741d2aa467dca0d106ca2bd21671a26db8e7d21fef7fb177a6e158279c6621` |
| `rust/bridge/makefile` | `f3027c6c729a4d2d969ffceff92ad96e2dfcfc34943fb7c854f5f0ddfb0153f0` |
| `rust/bridge/build-manifest.py` | `e4a4412204db94057f7cf72c4bd9d3c813bdf508b436ddd5504baf428888974d` |

The header digest equals the reviewed
[archive_bridge_v1.h](archive_bridge_v1.h) digest, confirming the byte-for-byte
copy.

### Matched facade build

Rebuilt from the committed tree for the record below. The build identity is
bound to the facade commit, so it changes when the facade source or its build
inputs change — which is the point of comparing it in the handshake.

| Item | Value |
| --- | --- |
| Artifact | `libarchive_bridge_v1.so` |
| Artifact SHA-256 | `04a4975ebfa70e1e29eca1814a276faac33f2319d137c05cf5ee567473ff8462` |
| Build identity SHA-256 | `a280b56485ca856de12a02b105d96ebb8916730a8c10862971ad5c99401a4738` |
| Facade commit | `336ebd9c998fca71544f291fdc4ccaa3b0d6b4ce` |
| Oracle commit | `336ebd9c998fca71544f291fdc4ccaa3b0d6b4ce` |
| Selected translation units | 289 |
| Identity input records | 295 (289 units + 6 make inputs) |
| Plugin policy | `built-in-only-no-external-discovery` |
| Manifest | `.s2a-spike/manifest-final/facade-build-dev.json` (task worktree) |

Verified properties of the build identity digest:

* It is the SHA-256 of the canonical input-identity object (UTF-8, sorted keys,
  compact JSON, no trailing newline) and reproduces exactly.
* It covers `rust/bridge/archive_bridge_v1.cpp` and `rust/bridge/makefile.gcc`;
  mutating the recorded facade-source hash changes the digest, so a changed
  facade cannot claim a matched identity.
* It contains neither its own hash nor the artifact hash, avoiding a
  self-referential library hash as `abi-v1.md` requires.

Exported dynamic symbols, checked by the manifest generator and asserted to be
exactly this set:

```
archive_bridge_v1_capabilities
archive_bridge_v1_create_context
archive_bridge_v1_destroy_context
archive_bridge_v1_handshake
archive_bridge_v1_result_destroy
```

## 3. Commands run and results

Every command below exited 0 on this host. After the review round 1 fix the
whole suite was re-run against the committed tree `336ebd9` with the facade
rebuilt from scratch. Logs with the literal invocation and exit code are under
the task worktree at `.s2a-spike/evidence-r2/` (round 1 runs are preserved at
`.s2a-spike/evidence-committed/` and `.s2a-spike/evidence-final/`).

| Command | Result |
| --- | --- |
| `python3 rust/tests/check_boundaries.py` | exit 0 — PASS |
| `python3 rust/tests/test_boundaries.py` | exit 0 — 14 tests OK (was 7; 7 added) |
| `cargo +1.97.1 fmt --manifest-path rust/Cargo.toml --all -- --check` | exit 0 |
| `cargo +1.97.1 build --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt` | exit 0 (default features: facade off, no native link) |
| `cargo +1.97.1 test --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt` | exit 0 — 10 tests passed, 0 failed |
| `cargo +1.97.1 clippy --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt --all-targets -- -D warnings` | exit 0 |
| `cargo +1.97.1 build … --features archive-engine/facade` | exit 0 |
| `cargo +1.97.1 test … --features archive-engine/facade` | exit 0 — 25 tests passed, 0 failed |
| `cargo +1.97.1 clippy … --all-targets --features archive-engine/facade -- -D warnings` | exit 0 |
| `python3 docs/ai-migration/qualification/check-layout.py --output <dir>` | exit 0 — `PASS: 25 struct layouts and every field offset match C/C++/Rust on Linux/x86_64` |
| `python3 .github/tests/release_version_test.py` | exit 0 |
| `python3 .github/tests/change_notice_test.py` | exit 0 |
| `python3 .github/tests/lang_files_test.py` | exit 0 |
| `python3 .github/tests/shell_ext_identity.py` | exit 0 |
| `python3 .github/tests/shell_ext_lang_reload.py` | exit 0 |
| `bash .github/tests/release_notes_test.sh` | exit 0 |
| `git diff --check` | exit 0 |
| `python3 docs/ai-migration/validate-migration-dag.py` | exit 0 — manifest PASS 29 children / 104 edges, amendment PASS, 10 negative controls PASS |
| `python3 docs/ai-migration/qualification/validate.py` | exit 0 — schema, selected input/notice hashes, capability boundaries, links and 4 schema negative controls PASS |
| `bash .s2a-spike/run-selftest.sh <facade-build-dir> <outdir>` | exit 0 — fixed build 19/19 ok; reconstructed pre-fix build fails, see section 4.1 |

`check-layout.py` is unchanged and was run against the reviewed header, so the
implemented header still matches the frozen Q1 layout.

The facade library is located through an explicit application-supplied link
path and rpath. `PATH` and `LD_LIBRARY_PATH` are never mutated globally, and no
arbitrary system facade is searched for, per `abi-v1.md`.

## 4. Contract tests and what they prove

15 self-owned facade contract tests, all passing against the real retained
engine.

`rust/crates/archive-engine/tests/facade_capabilities.rs` (9):

* `handshake_succeeds_on_a_matched_build` — every info field matches: `abi_major=1`,
  `revision=1`, `pointer_bits=64`, `target=1`, `little_endian=1`, and both
  32-byte digests.
* `handshake_rejects_each_individually_mutated_field` — each of 5 single-field
  mutations (target, and the first and last byte of each digest) returns
  `ARCHIVE_BRIDGE_V1_MISMATCH`. No partial acceptance.
* `create_context_rejects_a_mutated_handshake` — the same mutations are refused
  inside `create_context`, so skipping the handshake cannot produce an
  incompatible context.
* `capabilities_match_the_frozen_q1_reference_exactly` — all 61 format rows
  compared against the frozen Q1 reference by name and actual registration
  identity, never by row index. Registration id, flags, effective time flags,
  writer presence, reader presence and name all match.
* `the_hash_handler_is_the_only_coordinator_added_row_and_reports_256` — `Hash`
  is the sole row reporting the literal `256` (absent), with flags `12353` and
  time flags `0`, exactly as `Codecs_AddHashArcHandler` registers it.
* `codecs_and_hashers_match_the_frozen_q1_reference_exactly` — 25 codecs and 10
  hashers compared by name, `method_id`, encoder/decoder/filter status and
  digest size. Also asserts no RAR writer and no RAR encoder ever appears,
  mirroring the reviewed Q1 boundary controls.
* `no_operation_is_reported_as_qualified` — `qualified_operations` is the
  literal 0; the adapter fails the call on any nonzero bitmask.
* `capabilities_are_stable_across_repeated_enumerations`
* `many_contexts_and_results_release_cleanly`

`rust/crates/archive-engine/tests/facade_lifetime.rs` (6):

* `destroy_context_reports_busy_while_a_result_is_live` — `ARCHIVE_BRIDGE_V1_BUSY`
  while a dependent is live, OK once released.
* `a_repeated_result_destroy_is_a_stale_entry` — exactly-once ownership; the
  second call returns `ARCHIVE_BRIDGE_V1_STALE_ENTRY`, not a double free.
* `a_result_cannot_be_destroyed_through_a_foreign_context` — owner-context
  checking.
* `a_destroyed_context_handle_is_a_stale_entry`
* `malformed_envelopes_are_rejected_without_publishing_anything` — a null
  options pointer, a zeroed envelope and an oversized view are all
  `ARCHIVE_BRIDGE_V1_INVALID_REQUEST`; output handles stay null and the
  rejected view keeps the caller-supplied size with no borrowed pointer
  published. A larger envelope is never silently accepted.
* `every_allocation_is_released_across_many_cycles` — 64 cycles × 4 arenas =
  256 arenas, all released with OK; every cycle observes the BUSY guard while
  its arenas are live and then tears down with OK. Balance is **observable**,
  not inferred: a leaked arena would keep the live set non-empty and make that
  final teardown report BUSY instead.

The `Busy` and repeated-destroy states are unreachable through the safe
adapter by design, so they are driven through raw-ABI probes in
`archive-engine-sys` (`src/probe.rs`). That keeps the assertions about the
facade's own guards rather than about the wrapper's discipline, while leaving
the contract test files free of `unsafe` and raw pointers.

### A disagreement that was investigated, not papered over

The first run of `capabilities_match_the_frozen_q1_reference_exactly` failed:

```
assertion `left == right` failed: effective time flags differ for format gzip
  left: 0
right: 134217730
```

This was a test-expectation error, not an implementation bug, and the frozen
reference was **not** edited. `abi-v1.md` "Capabilities and qualification
boundary" records the raw registered `TimeFlags` and the effective `CCodecs`
`TimeFlags` separately on purpose: the built-in `LoadCodecs` path leaves
`TimeFlags` at the `CArcInfoEx` constructor default, while the dynamic library
path obtains the exported property. Confirmed in the retained source —
`CCodecs::Load()` copies `arc.Flags` but never `arc.TimeFlags`
(`CPP/7zip/UI/Common/LoadCodecs.cpp:813-816`), whereas `CCodecs::LoadFormats()`
reads `kTimeFlags` from the library (`LoadCodecs.cpp:474-477`). The frozen
`format_registry` rows carry the raw value observed through the library's own
exports, which is a different quantity from what a built-in-path facade
reports. The test now compares against the effective value and documents why;
asserting the raw value would have demanded exactly the "repair" of retained
behavior that `abi-v1.md` forbids.

## 4.1 Review round 1 defect: the CTextArena refusal path double free

Independent review round 1 found a real double free in
`rust/bridge/archive_bridge_v1.cpp`, `CTextArena::Add`. The verdict was CHANGES
and this section records the fix and its regression.

What was wrong. The "not representable as UTF-16" branch deleted the block and
then threw `std::bad_alloc`. That throw was caught by the same function's
`catch (...)`, and because the block had never been pushed into `_blocks`, the
`_blocks.empty() || _blocks.back() != block` guard was true, so the catch
deleted the identical pointer a second time. Two code paths owned the same
allocation, which is the ownership mistake the FFI boundary must not make.

What changed. The block is now owned by a scoped `CBlockGuard` for the whole
build and released to the arena only after `push_back` has succeeded. No error
path deletes by hand, the manual `try`/`catch` is gone, and every throw —
the refusal, a `push_back` allocation failure, anything else — frees the block
exactly once through the guard's destructor.

Why no capability query exposed it. The refusal branch is unreachable through
the four exported operations: every retained format, codec and hasher name is
ASCII, so `(uint32_t)*p` never exceeds `0x10FFFF` and the branch is never taken.
That is why the 15 contract tests passed over a latent double free, and why the
regression drives the branch directly with a bounded synthetic code point rather
than opening an archive or adding a dependency.

How the regression detects it. `ARCHIVE_BRIDGE_V1_SELF_TEST` compiles a
development-only `main` into the same translation unit — the shared library
build never defines it, so the export surface is unchanged (still exactly the
four in-scope operations; `nm -D` shows no `main` and no self-test symbol).
Global `operator new`/`delete` are replaced with a tracking pair, so freeing a
pointer that is not live is *recorded* rather than corrupting the heap. This
needs no sanitizer and no external crate.

The regression is proven not vacuous. `.s2a-spike/run-selftest.sh` builds the
self-test against the fixed source, then rebuilds the **same** test against a
reconstructed pre-fix `Add` and requires that one to fail:

```
fixed exit=0 (want 0)   buggy exit=1 (want nonzero)
REGRESSION IS REAL: it passes on the fix and fails on the pre-fix code
```

The fixed build reports 19/19 `ok`. The pre-fix build fails exactly the three
double-free assertions (`Add's throw path performs no double free`, `no double
free with published blocks present`, `256 refusals perform no double free`)
while the surrounding behavioral assertions still pass — the test discriminates
the defect, not the build.

Two anti-vacuity controls are included, because an audit that observes nothing
would make every assertion above pass trivially:

* `the heap audit reports a deliberate double free (control)` — a deliberate
  double free must be reported. This control initially failed for a real reason
  worth recording: C++14 permits eliding a `new`/`delete` pair whose object
  never escapes, and GCC does elide it at `-O1`, so the control allocated
  nothing. Verified directly (`new=0 plain_delete=0 sized_delete=0` at `-O1`
  versus `new=1 sized_delete=1` with `-fno-allocation-dce`). The control now
  calls `::operator new`/`::operator delete` explicitly, which cannot be elided
  and exercises precisely the functions the audit replaces.
* `the audit observed the block allocation (test is not vacuous)` — asserts the
  arena test itself actually allocated under audit.

## 5. Retained-engine integration

The facade links the retained `ARC_OBJS` fragment the same way
`CPP/7zip/Bundles/Format7zF/makefile.gcc:8` does, and is built from the
retained bundle directory so every retained compile rule resolves its own
relative source paths unchanged. Added on top of `ARC_OBJS`: the two
`UI_COMMON_OBJS` members the card names — `LoadCodecs.o` (`CCodecs`,
`CArcInfoEx`) and `HashCalc.o` (`Codecs_AddHashArcHandler`) — plus the retained
objects those two reference for link closure (`EnumDirItems.o`, `SortUtils.o`,
`ErrorMsg.o`, `FileLink.o`, `FileStreams.o`, `MyWindows.o`). No console object
is linked. No file under `C/`, `CPP/` or `Asm/` was modified.

`Z7_EXTERNAL_CODECS` is deliberately **not** defined, because the frozen Q1
identity pins `plugin_policy` to `built-in-only-no-external-discovery`. The
facade therefore reads only the built-in registration tables and loads no
external module. The retained `CREATE_CODECS_OBJECT` pattern is followed for
whichever branch is compiled: both hold one COM reference, and the external
branch additionally arms `CCodecs::CReleaser` and publishes the
`CExternalCodecs` links. In the non-external configuration `CCodecs::Libs` does
not exist, so there is no library cycle for `CReleaser` to break and the
reference drop alone is the retained teardown.

### Registration-byte recovery

`CArcInfoEx` does not retain `CArcInfo::Id`, so the registration byte the card
requires cannot be read back from `CCodecs::Formats`. Rather than edit a
retained source file, the facade captures it at its source: the link wraps the
retained registrar with GNU ld's `--wrap`, keyed on the Itanium C++ ABI
mangling of `RegisterArc(const CArcInfo *)`. The wrapper records each built-in
`CArcInfo` pointer and then calls `__real_`, so `CCodecs::Formats` is built
exactly as before and no registration is dropped. Observed: 60 wrapped
registrations and 61 format rows, the 61st being the coordinator-added `Hash`
handler, which correctly reports the literal `256`.

This mechanism is GNU-linker specific. MSVC's `link.exe` has no `--wrap` and a
different mangling, so Windows needs its own reviewed mechanism. That is
recorded in `rust/bridge/makefile`, which **fails closed** with an `!ERROR` so
no unqualified Windows binary can be produced by accident.

## 6. Rust boundary and safety posture

`archive-engine-sys` is the single FFI boundary crate. Its
`#![forbid(unsafe_code)]` was replaced with crate-level
`unsafe_code = "deny"` — deliberately `deny`, not `allow`, so every unsafe site
must carry an explicit `#[allow(unsafe_code)]` next to its documented invariant
and none can appear by accident. Every other workspace crate still inherits the
workspace `forbid`.

`archive-engine`, the safe adapter, keeps `#![forbid(unsafe_code)]` and
contains no `unsafe`, no foreign-function declaration and no raw pointer. All
pointer work — including the owned-snapshot layer that copies capability rows
and text out of the facade arena — lives in `archive-engine-sys`.

`rust/tests/check_boundaries.py` was amended to enforce exactly that split, and
now additionally asserts:

* the scoped-unsafe relaxation exists on `archive-engine-sys` only, at `deny`,
  and that crate does not inherit the workspace lint table;
* every other crate inherits the workspace table and does not override it;
* `archive-domain`, `archive-app`, `archive-cli` and `archive-qt` still contain
  no unsafe, no foreign-function declaration and no OS handle type, and
  `archive-engine`'s sources and the contract tests are now scanned too;
* library dependency edges remain exactly as declared, with a dev-only edge
  permitted only where explicitly declared, so a test dependency cannot smuggle
  in a production edge;
* the `facade` feature stays off by default on both crates and cannot appear on
  any other crate, and `archive-engine/facade` must forward to
  `archive-engine-sys/facade`.

`rust/tests/test_boundaries.py` gained 7 negative controls for those rules
(14 tests total, all passing), including proof that unsafe outside the FFI
crate is still rejected and that a production edge cannot hide as a dev
dependency.

Boundary properties implemented: C++ catches all exceptions at every exported
boundary and converts them to an `int32_t` bridge status; Rust never unwinds
into C (no callback is defined and none of the four operations takes a function
pointer); no Rust allocator touches a native handle; context and result handles
are neither `Send` nor `Sync`; a mismatching handshake allocates nothing;
output handles initialize to null and views are zeroed, retaining the
caller-supplied size, before any effect.

## 7. Default build is unaffected

The safe adapter exposes the four operations only behind the non-default
`facade` Cargo feature. `archive-cli` gains no new command and no new
dependency. The default workspace build links no native code: the entire
`abi`/`link`/`owned`/`probe` module set is `#[cfg(feature = "facade")]`, and
`check_boundaries.py` asserts the feature is off by default. The default-feature
build, test and clippy triple passes with no native library present at all.

No file under `C/`, `CPP/`, `Asm/`, `.github/`, `AGENTS.md`, or any other
card's owned paths was modified; verified with `git status`. The reviewed
`docs/ai-migration/qualification/engine-build.json` is untouched and still
records `status: retained-native-reference`. No golden or reference data was
edited.

## 8. Build manifest and the schema gap, stated plainly

`rust/bridge/build-manifest.py` performs a real two-pass matched build. Pass 1
builds with an all-zero identity — which no caller can match, so a pass-1
artifact can never be mistaken for a matched build — and recovers the real
compile commands, link command and selected translation units from the emitted
build log, never from a hand-maintained object list. Pass 2 rebuilds the facade
translation unit and relinks with the real identity digest embedded. It refuses
to run against a pre-existing output directory, so cached objects cannot be
claimed as a new compilation.

`engine-build-schema.json` describes the **three-platform qualification**
manifest. Its `builds` array requires exactly three native systems, and
`status: facade-qualified` additionally requires `identity`, `identity_sha256`,
`facade_artifacts` and `qualification_evidence` on every one of them.
Separately, `#/$defs/build` requires `products` (Alone2/Format7zF/Console),
`standalone`, `loaded`, `format_registry`, `coordinator_formats` and
`standalone_loaded_differences` — retained-reference observations owned by the
reviewed Q1 manifest, not outputs of a facade build.

S2a-DEV is a single-host development build. Emitting a three-element `builds`
array from one host, or copying retained-reference observation blocks into a
facade build record, would mean fabricating platform and qualification data.
`AGENTS.md` forbids that: deferred native obligations "must never be deleted,
completed, archived or represented as passed."

So the generator:

* writes a separate `facade-build-dev.json` with
  `status: facade-development-single-host`, never `facade-qualified`, and never
  touches the reviewed `engine-build.json`;
* validates the `identity` object in full against `#/$defs/identity`, the exact
  definition the handshake digest is computed over;
* validates the facade build record field-by-field against the schema's own
  `commit`, `sha256` and `input` definitions, which do apply;
* records each unmet requirement explicitly in
  `unmet_qualification_requirements`;
* proves the schema still **rejects** a one-platform `facade-qualified` claim
  assembled from this host, as a negative control.

## 9. Deferred native obligations — open, not satisfied

None of the following is satisfied, weakened or closed by this card. Each
remains open on its own card and must not be represented as passed.

| Card | Obligation |
| --- | --- |
| B01 `t_22299c6f` | Format/volume/error corpus confirmation of the enumerated capabilities. |
| B03 `t_bf92ce13` | Native metadata, large-file and partial-I/O behavior. |
| B05 `t_3859d918` | Native password callback state behavior. |
| B06 `t_83983e9c` | Native staged cancellation, progress and shutdown behavior. |
| S2a `t_071e4cd7` | Native Windows/Linux/macOS matched facade build, ABI widths, calling convention, sanitizers, dead-strip retention. |
| B08 `t_0a04d8dd` | Independent native FFI lifetime, fault and concurrency qualification. |

Additional limits of this evidence:

* Single-host Linux development build. **Not** Windows/macOS/Linux release
  qualification. No Windows or macOS facade binary exists.
* No CI run; nothing pushed to a shared branch; no merge into `dev-main`; no
  release.
* `qualified_operations` stays the literal 0. No capability is enabled for any
  production caller. `archive-cli` behavior is unchanged.
* No archive was opened, no fixture read, no password requested, no path
  written, no hostile input processed.
* No sanitizer (ASan/UBSan/TSan) or dead-strip retention run was performed;
  those are part of the deferred native campaign.
* The leak check is allocation-balance accounting observable through the
  facade's own BUSY/OK guards, not an external allocator or sanitizer audit.
* The `CTextArena` regression's heap audit replaces global
  `operator new`/`delete` inside one development-only test binary. It detects
  double and foreign frees on the paths it exercises; it is not a general
  allocator audit, does not track the retained engine's own allocations, and
  does not substitute for the deferred sanitizer work. The defect it covers was
  found by independent review, not by the contract tests, which is itself
  evidence that enumeration-level tests do not cover error-path ownership.
* Registration-byte recovery is proven only for the GNU-linker Itanium C++ ABI
  toolchain on this host. The Windows mechanism is unsolved and fails closed.
* Enumerating a capability is not qualifying an operation, and a writer factory
  is not proof of any create or update property.
