# Development-first sequencing and deferred native qualification

Task `t_eb4719bf` (M3-D), branch `wt/t_eb4719bf`. Status: authored for independent
same-card review; this document is not a PASS and performs no board change.

This document implements the operator's 2026-09-12 decision recorded in
[AGENTS.md](../../AGENTS.md) "Development-first sequencing, deferred native
qualification" and in [ADR-0004](adr/0004-development-first-sequencing.md). It
does not modify the M3 graph at runtime. Every dependency and scope change below
is a proposal for the coordinator follow-up `t_f34996b9` to apply AFTER this card
receives an independent PASS.

Nothing here waives a test, changes archive semantics, enables a capability,
authorizes native execution, spends a native budget, unfreezes B04, or approves a
release.

## 1. Two acceptance levels

| Level | Meaning | What it may unlock |
| --- | --- | --- |
| DEVELOPMENT | Implementation complete; local compilation, unit tests and the card's self-owned contract tests pass on the development host. | Independent review, reviewer integration into local `ai/migration-bootstrap-20260911`, and dependent development-acceptance cards. |
| QUALIFIED / RELEASE | All originally mandated native Windows/Linux/macOS evidence, behavior characterization and licensing evidence for the changed surface are present and independently reviewed. | Capability enablement for production callers, `qualified_operations` bits, release-candidate validation. |

DEVELOPMENT acceptance is not a weaker review. It is a narrower claim: the code
is correct against contracts that are already reviewed, and nothing it produces is
reachable by a production caller.

## 2. Evidence-only versus input-bearing dependencies

A dependency `X -> Y` is EVIDENCE-ONLY when X would only confirm, on real
hardware, behavior that Y implements from an already reviewed written contract.
A dependency is INPUT-BEARING when Y cannot be written correctly without a
semantic, ownership, safety or licensing fact that only X can supply.

Only evidence-only dependencies may be deferred, and only by splitting a card;
the edge itself is never deleted from the original card.

Applying that test to the currently stalled native campaigns:

| Dependency | Consumer work | Classification | Proof |
| --- | --- | --- | --- |
| B01 `t_22299c6f` (formats/volumes/errors corpus) | Handshake, context lifetime, capability enumeration | evidence-only | Capability enumeration reads the retained registration tables (`CCodecs::Formats`, `Codecs`, `Hashers` in `CPP/7zip/UI/Common/LoadCodecs.h:357-407`) and the `GetNumberOfFormats`/`GetHandlerProperty2` exports already observed by Q1 (`docs/ai-migration/qualification/observe-formats.cpp`). It opens no archive and reads no fixture. |
| B01 | Archive open, paged entries, listing | INPUT-BEARING | Which formats, volume chains and error shapes must be represented, and which `CArcErrorInfo` states are legal, are corpus facts. Q1 explicitly records only 8 of 61 format rows as fixture-covered. |
| B02 `t_7019eca0` (name identity/property precedence) | Capability enumeration | evidence-only | B02 is already `done` and reviewed at `72631ae748e1778af65c30d39e9fe68b8c6442a5`; it is not a deferred campaign at all. |
| B03 `t_bf92ce13` (metadata, large files, partial I/O) | Handshake/context/capabilities | evidence-only | No stream is opened; no `IInStream` is created. |
| B03 | Open/entries, any stream seam | INPUT-BEARING | Short-read, seek and failure-cleanup semantics decide the stream adapter's contract. |
| B04 `t_2a64c953` (extraction safety, overwrite) | Handshake/context/capabilities | evidence-only | No path is written, no extraction callback exists in this scope. |
| B04 | S4/S8 and anything with filesystem effects | INPUT-BEARING and frozen | Overwrite and containment semantics cannot be invented. B04 stays frozen with a zero native budget. |
| B05 `t_3859d918` (password callback states) | Handshake/context/capabilities | evidence-only | The question callback is not bound in this scope; `ask` is absent, which the ABI defines as explicit interaction failure. |
| B05 | Open with encrypted input, extract, test, create | INPUT-BEARING | Undefined/empty/cancel distinctions are characterization facts. |
| B06 `t_83983e9c` (cancellation/progress/shutdown) | Handshake/context/capabilities | evidence-only | No operation runs long enough to cancel; `is_cancelled` is supplied but never polled by a codec in this scope. |
| B06 | Open/entries and every later operation | INPUT-BEARING | Staged cancellation points and quiescence are characterization facts. |

Conclusion: exactly one currently blocked coder card contains a self-contained
development slice whose remaining native dependencies are all evidence-only, and
that is the front half of S2a. No generic removal of B01/B03/B04 edges is
authorized, and none is proposed.

## 3. Proposed card mapping

Legend: "unchanged" means the card keeps its exact current scope, parents,
acceptance level and deferred native obligations.

| Card | Acceptance level after amendment | Change |
| --- | --- | --- |
| Q1 `t_f4d107ea`, B02 `t_7019eca0`, S1 `t_31358a3f` | qualified, already done | unchanged |
| B01 `t_22299c6f` | qualified | unchanged; stays open with its provenance/licensing gate |
| B03 `t_bf92ce13` | qualified | unchanged; stays open with its native-runner gate |
| B04 `t_2a64c953` | qualified | unchanged; stays frozen, native budget zero |
| B05 `t_3859d918`, B06 `t_83983e9c` | qualified | unchanged |
| S2a `t_071e4cd7` | qualified | scope reduced to open/entries/close and operation callbacks; ALL eight current parents retained; gains a new parent, the S2a-DEV card |
| S2a-DEV (new) | development | new card; see section 5 |
| B08 `t_0a04d8dd` | qualified | unchanged parents (S2a, M3); it qualifies the full facade, not the development slice |
| S3-S12, Q2, Q3, B07, S8L/W/M, S11W/L/M | qualified | unchanged |

Only one new card is proposed. Every other existing engineering card is reused
exactly as written.

## 4. Exact dependency and scope migration list for `t_f34996b9`

Apply only after this card's independent PASS. Each item is a complete
instruction; no other board mutation is authorized by this document.

1. CREATE one card, assignee `coder`, `workspace_kind: worktree`,
   `max_runtime_seconds: 7200`, reviewer `reviewer`, max-retries 2 including
   substantive review failures, title:
   `S2a-DEV — Retained-engine facade handshake, context and capability enumeration (development acceptance)`.
   Parents, exactly and only: `t_82c76197` (M3), `t_f4d107ea` (Q1),
   `t_31358a3f` (S1). Body: section 5 of this document, verbatim.
   Rationale for each omitted parent is the evidence-only proof in section 2.
2. LINK `S2a-DEV -> t_071e4cd7` (new card becomes a parent of S2a). S2a's
   existing eight parents are NOT touched: `t_82c76197`, `t_31358a3f`,
   `t_f4d107ea`, `t_22299c6f`, `t_7019eca0`, `t_3859d918`, `t_83983e9c`,
   `t_bf92ce13` all remain.
3. EDIT the body of `t_071e4cd7` only to narrow its scope sentence: remove
   "version/capability handshake, create_context/... close/result_destroy" from
   S2a's own deliverable list and replace it with "consume the reviewed S2a-DEV
   handshake/context/capability implementation unchanged; implement open, owned
   paged entries, close and the minimal safe callbacks/cancel". Its acceptance
   criteria, native evidence requirements, reviewer loop and block policy are
   unchanged. Because the manifest records `body_sha256`, recompute and record
   the new hash in `migration-dag.json` in the same reviewed change.
4. REMOVE nothing. Do not delete, complete, archive or re-point B01, B03, B04,
   B05, B06 or any native campaign card. Do not change B04's frozen state or any
   native budget.
5. Subscriptions: create the new card with `creator_task_id` inheritance from
   this task's lineage so it inherits the same durable operator route as every
   other M3 child. Do not configure Telegram or write a chat identifier.
6. Concurrency: apply `kanban.max_in_progress=8` and
   `kanban.max_in_progress_per_profile=4` only after the AGENTS.md clause in
   section 6 has actually been written through the supported approval path, and
   only once the cards it would parallelize have verified non-overlapping owned
   paths. Section 6 also records why this run could not write that clause. With
   the S2a-DEV split there is one runnable coder slice, so raising the ceiling
   has no immediate effect and no throughput gain may be claimed from it.

Old/new summary, machine-checkable against `migration-dag.json`:

| Edge | Before | After |
| --- | --- | --- |
| `t_82c76197 -> S2a-DEV` | absent | present |
| `t_f4d107ea -> S2a-DEV` | absent | present |
| `t_31358a3f -> S2a-DEV` | absent | present |
| `S2a-DEV -> t_071e4cd7` | absent | present |
| all 8 existing `* -> t_071e4cd7` | present | present (unchanged) |
| every other edge in the graph | present | present (unchanged) |

## 5. First executable coder task specification (S2a-DEV)

This is the immediately actionable slice. It is meaningful retained-engine bridge
work, not an empty scaffold: it links the real retained engine, enumerates its
real registration tables and proves the matched-build handshake.

### Owned files

The card owns exactly these paths and no others:

- `rust/bridge/archive_bridge_v1.h` — copied byte-for-byte from the reviewed
  `docs/ai-migration/qualification/archive_bridge_v1.h`, then reduced to the four
  exported functions in scope by deleting nothing: the header is copied unchanged,
  and the C++ translation unit simply does not define the out-of-scope exports.
- `rust/bridge/archive_bridge_v1.cpp` — the C++ RAII facade implementation.
- `rust/bridge/makefile.gcc`, `rust/bridge/makefile` — build of the facade as an
  internal shared library, including the retained `ARC_OBJS` fragment the same way
  `CPP/7zip/Bundles/Format7zF/makefile.gcc:8` does, plus the `UI_COMMON_OBJS`
  members `LoadCodecs.o` and `HashCalc.o` that supply `CCodecs` and
  `Codecs_AddHashArcHandler`. Console objects are excluded.
- `rust/bridge/build-manifest.py` — emits the engine build manifest required by
  `docs/ai-migration/qualification/engine-build-schema.json`, with the real
  facade commit, the real selected translation units, flags and digests.
- `rust/crates/archive-engine-sys/src/lib.rs` and new modules under it — the
  private `repr(C)` declarations and `extern "C"` bindings. This crate's
  `#![forbid(unsafe_code)]` is replaced by scoped `unsafe` with a documented
  invariant per block; `rust/tests/check_boundaries.py` is amended accordingly.
- `rust/crates/archive-engine/src/lib.rs` and new modules — the safe adapter.
- `rust/crates/archive-engine/tests/` — the card's self-owned contract tests.
- `docs/ai-migration/qualification/s2a-dev.md` — evidence and limits.

It must not edit `rust/crates/archive-domain`, `archive-app`, `archive-cli`,
`archive-qt`, any file under `C/`, `CPP/`, `Asm/`, any `.github/tests/migration/`
directory, `AGENTS.md`, or any other card's owned files.

### Concrete behavior in scope

Implement, on the development host, exactly these four exported functions from
the reviewed Q1 ABI, with the semantics fixed in
[abi-v1.md](qualification/abi-v1.md):

1. `archive_bridge_v1_handshake` — compare every `archive_bridge_v1_info` field:
   `abi_major=1`, `revision=1`, `pointer_bits`, `target`, `little_endian=1`, the
   raw 32-byte SHA-256 of the exact header bytes, and the build identity digest
   over the canonical input-identity object. Mismatch returns
   `ARCHIVE_BRIDGE_V1_MISMATCH` without allocating. It may fill `actual` to
   describe the loaded build; that grants no fallback compatibility.
2. `archive_bridge_v1_create_context` / `archive_bridge_v1_destroy_context` —
   allocate the C++ context, re-check the handshake inside create so skipping
   handshake cannot produce an incompatible context, construct `CCodecs` with the
   retained `CREATE_CODECS_OBJECT` pattern and `CCodecs::Load()`, honor
   `CCodecs::CReleaser`'s library-cycle teardown on destroy, and return
   `ARCHIVE_BRIDGE_V1_BUSY` from destroy while any result handle is live.
3. `archive_bridge_v1_capabilities` — return an owned, immutable result arena
   containing `archive_bridge_v1_capability_view`: every `CCodecs::Formats` row
   with its runtime index, the `CArcInfo` registration byte widened to `uint32_t`
   with the literal `256` for the coordinator-added Hash handler, effective
   `Flags`/`TimeFlags`, actual reader/writer factory presence, name and
   extensions; every codec and hasher with its `uint64_t` id, encoder/decoder/
   filter status and digest size. `qualified_operations` is the literal `0`.
4. `archive_bridge_v1_result_destroy` — free exactly one result, checking owner
   context and exactly-once ownership; a repeat returns
   `ARCHIVE_BRIDGE_V1_STALE_ENTRY`.

Every other export named in the reviewed header, including `open`, `entries`,
`close`, `extract`, `test` and `create`, is NOT defined by this card. The safe
Rust adapter exposes these four operations only behind a non-default Cargo
feature; `archive-cli` gains no new command and no new dependency, so the default
workspace build is byte-for-byte unaffected in behavior.

C++ catches all exceptions at every exported boundary and converts them to a
bridge status. Rust never unwinds into C. No Rust allocator touches a native
handle. Context and result handles are neither `Send` nor `Sync`.

### Exact tests the card must run and record

- `python3 rust/tests/check_boundaries.py` and `python3 rust/tests/test_boundaries.py`
  after amending them to allow scoped `unsafe` in `archive-engine-sys` only, and
  to assert that `archive-domain`, `archive-app`, `archive-cli` and `archive-qt`
  still contain no `unsafe`, no `extern`, and no OS handle types.
- `cargo +1.97.1 fmt --manifest-path rust/Cargo.toml --all -- --check`
- `cargo +1.97.1 build --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt`
  (default features: the facade feature off, so no native link)
- `cargo +1.97.1 test --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt`
- `cargo +1.97.1 clippy --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt --all-targets -- -D warnings`
- The same build/test/clippy triple again with the facade feature enabled, on the
  development host only.
- `python3 docs/ai-migration/qualification/check-layout.py` unchanged, to confirm
  the implemented header still matches the frozen Q1 layout.
- Self-owned contract tests, which must include at least: handshake success on a
  matched build; handshake rejection for each individually mutated info field;
  create_context rejection after a mutated handshake; capability count and every
  format name/registration id compared against the frozen Q1
  `native-observations.json` for this host, including the Hash row's `256`;
  double `result_destroy` returning `STALE_ENTRY`; `destroy_context` returning
  `BUSY` with a live result; and a leak check that every allocation is released.
- `python3 .github/tests/release_version_test.py`,
  `change_notice_test.py`, `lang_files_test.py`, `shell_ext_identity.py`,
  `shell_ext_lang_reload.py`, `bash .github/tests/release_notes_test.sh`,
  `git diff --check`, and
  `python3 docs/ai-migration/validate-migration-dag.py`.

### Acceptance

DEVELOPMENT acceptance. All commands above exit 0 on the development host, the
build manifest validates against the Q1 schema, and the evidence document records
the exact commands, outputs, host OS/arch/toolchain versions and digests.

### Retained evidence and unresolved limits the card MUST state

- This is a single-host development build. It is not Windows, macOS or Linux
  release qualification. `-Gr`/`__cdecl` behavior, MSVC and Apple toolchain
  layout, dead-strip retention of the registration units under each native
  linker, and sanitizer runs remain S2a/B08 native obligations.
- `qualified_operations` stays `0`. No capability is enabled for any production
  caller. `archive-cli` behavior is unchanged.
- No archive is opened, no fixture is read, no password is requested, no path is
  written, no hostile input is processed, no CI is run and nothing is pushed to a
  shared branch.
- B01, B03, B04, B05, B06, B08, Q2, Q3 and S12 obligations are untouched and
  still block everything they blocked before.

## 6. Pending AGENTS.md concurrency clause (not yet written)

The operator additionally decided on 2026-09-12: 「按照你的建议，后续进行修改，修改
内容也按照你的建议，但我想稍稍提高，全局是 8，per-profile 是 4」. This revises the
existing AGENTS.md clause "Maximum two active workers globally, one per profile
initially." to a global maximum of 8 and a per-profile maximum of 4, corresponding
to runtime `kanban.max_in_progress=8` and
`kanban.max_in_progress_per_profile=4`.

This architect run could NOT write it: the protected agent-instruction file
approval prompt timed out with no response, and the tool forbids retrying or
using another path. The clause is therefore recorded here verbatim so it can be
applied through the same supported approval path that landed the
"Development-first sequencing" section, without any agent reconstructing it from
memory. It is a DEFERRED authorization, not an immediate configuration change.

Replace, in AGENTS.md section "Autonomy and escalation":

> Parallelize only independent boundaries without competing architecture
> decisions or strongly overlapping edits. Maximum two active workers globally,
> one per profile initially.

with:

> Parallelize only independent boundaries without competing architecture
> decisions or strongly overlapping edits. Maximum eight active workers globally,
> maximum four per profile (human decision 2026-09-12, runtime
> `kanban.max_in_progress=8` and `kanban.max_in_progress_per_profile=4`). The
> raised ceiling is permission to run more genuinely independent cards, nothing
> else. Every card still has exactly one owned path set and one decision owner;
> two cards must never edit the same file concurrently; and the raise does not
> relax independent review, qualification gates, conflict handling, the B04
> freeze or the zero native budget. Apply the runtime change only after the cards
> it would parallelize actually have non-overlapping boundaries.

Sequencing constraints that come with this authorization:

1. The runtime `kanban` configuration is NOT changed by this card. The
   coordinator follow-up `t_f34996b9` applies it only after this card's
   independent PASS and only once the mainline slices it would parallelize have
   demonstrably non-overlapping owned paths.
2. At the time of writing the board has zero `ready` cards, so the higher ceiling
   changes nothing observable. No throughput improvement may be claimed from it.
3. A higher ceiling is not permission to relax review, to auto-resolve merge
   conflicts, or to let two cards edit one file. The hotspot rule in
   [migration-dag.md](migration-dag.md) ("Fixed ownership and decisions") still
   governs shared-file contention.
4. B04 stays frozen and every native budget stays zero regardless of the ceiling.

Under the S2a-DEV split in section 5 there is exactly one runnable coder slice,
so the raised ceiling has no immediate parallelization target either. It becomes
useful only when several independent boundaries exist at once.

## 7. Invariants the amended validator enforces

- Release-path cards (`s12` and its prerequisites `q3`, `s11w`, `s11l`, `s11m`)
  can never carry development acceptance.
- A development-acceptance card must list at least one deferred native obligation
  and must name an existing qualified card that still owns it.
- A development-acceptance card's parents must be a strict subset of its source
  card's parents, and the source card must retain every original parent, so the
  amendment cannot smuggle in an edge deletion.
- No card may claim qualified acceptance while still listing deferred obligations.
- Cards named as obligation owners must exist in the graph and must be
  qualified-acceptance cards.

Negative controls in `validate-migration-dag.py` exercise each of these plus the
three original graph controls. See section "Reproducible validation" in
[migration-dag.md](migration-dag.md).
