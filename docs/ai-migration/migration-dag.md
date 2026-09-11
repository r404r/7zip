# M3: executable migration task graph

Board: `archive-rust-migration`. Root: `t_82c76197`, branch `ai/migration-m3`.
Status: authored for independent same-card review; this document is not M3 PASS.
All 29 new cards have a DIRECT M3 dependency. Their initial state is `todo`;
none may run until the reviewer approves M3. This is an actual persisted board
DAG, not a list of proposed task IDs.

## Reviewed inputs and scope

Both parent cards were re-read and independently approved by `reviewer`:

- M1 `t_f4afeee1`: `6e958b65df15e1749167ef5cfa753f90482c33c1`.
- M2 `t_db8ffe0b`: `29e4c6a029604f1c49cb08646090dd5f0ba7127a`.

Both commits are already ancestors of task starting HEAD
`cab64c6c00f4796b076e28aa6d972774807ceeb2`; no import or cherry-pick was needed.
The primary checkout remains `ai/migration-bootstrap-20260911`. Both AGENTS.md
files were read. `dev-main` stays `143e2c5dd24d084614ba32017a72d822cd2bea75`.

Normative inputs: [architecture](architecture-target.md),
[stages](migration-stages.md), [M1 measured baseline](characterization-baseline.md),
[retained facade](adr/0001-retained-engine-facade.md),
[ownership/tasks](adr/0002-ownership-tasks-platforms.md), and
[Qt qualification](adr/0003-qt-build-qualification.md).
M1's native Windows/macOS/Linux CLI evidence is parent evidence, not a new M3
runtime test. It does not waive B01–B08, GUI evidence, ABI qualification or licenses.

M3 changes only this graph, its machine-readable snapshot and read-only validator.
No engine, codec, encryption, GUI, build system, oracle or existing test is edited.
No new production runtime is built here. The validator is documentation tooling.

## Fixed ownership and decisions

- Retain Qt 6/QML -> CXX-Qt -> Rust app/domain -> versioned internal C facade ->
  mature C/C++ orchestration/engine. No blind rewrite, codec replacement, direct
  QML-to-engine access or unapproved GUI substitution.
- `rust/` package names and dependency directions are exactly M2 section 2.
  `archive-domain` owns typed values and `ArchiveEngine`; `archive-app` owns use
  cases; `archive-engine-sys` owns private ABI declarations; `archive-engine`
  owns safe adaptation; `archive-platform` owns OS-private services; `archive-cli`
  and later `archive-qt` compose them. No independent sibling schema choices.
- M2 sections 3–5 define IDs/generation, lossless UTF-16 engine text, tagged native
  paths, unknown properties/timestamp precision, structured call/item/native
  errors, one worker, callback quiescence and reply/cancel protocols. Display is
  never path identity. No domain/app unsafe or Win32/Qt leakage.
- Q1 is the single evidence/contract elaboration owner before any ABI or toolchain
  consumer starts. It must encode M2's fixed semantics into exact layout and
  pinned native inputs, not propose a competing design. Q2 is the same profile's
  later extension for Qt, after CLI/filesystem qualification. Material changes
  require a human-reviewed ADR. Never reconstruct redacted identifiers from excerpts.
- Qualification JSON uses explicit `schema_version: 1`. Q1 owns the exact pin and
  engine-build schemas before downstream generation. Required build fields are
  M2 ADR-0001's oracle/facade commit, OS/arch, toolchains/runtime/mode, ABI revision,
  actual translation units/fragments/defines/CPU/assembly flags, registry/capability
  inventory, exclusions, license provenance, artifact digests and exact commands.
  B01 fixture manifests add generator/version/license/provenance, SHA-256,
  format/method, operation coverage and native oracle reports. No secret values.
- New CLI output is human-facing CLI output, not a newly serialized public JSON
  protocol. A future external serialization requires its own reviewed schema.
- S1 owns workspace manifests and pure models. S2a/S3–S7 serialize shared ABI,
  build and crate-root evolution under `coder`; no unowned parallel header edits.
  S1 must not register an invalid empty GUI Cargo package: omit it from members
  until Q2/S9a can supply a valid opt-in member. Use `--exclude archive-qt` only
  when it is actually a member; establish Cargo.lock, then use `--locked`.
- B01–B08 own separate `.github/tests/migration/bNN/` and qualification documents.
  Keep M1 harness/goldens unchanged. A shared harness/workflow change is a hotspot,
  not permission for competing sibling edits. Record `hotspot: <path>` and route
  ownership rather than silently changing a sibling's file.
- S8 deliberately replaces ONE seam first: read-only native input streams
  (open/read/seek/size/close). It fixes the portable port before S8L/W/M implement
  only their own target modules. Output, scanner, metadata application, links,
  rename/replace and overwrite remain C++ owned. This is a bounded strangler
  increment, not complete Rust filesystem parity. Further service replacement
  needs separately scoped, reviewed work against B02–B04, not implicit authority.
- S9/S10 own shared Qt models/dialogs serially. S11W/L/M own platform-specific
  integration subtrees and consume the same app command contract. Desktop
  activation is opt-in; no association takeover or legacy uninstall. Common
  package changes require an owner/hotspot check, not divergent schemas.
- Existing CLI, Win32 GUI, Explorer DLL, FAR/SFX and specialized bundles remain.
  No automatic fallback/double execution after partial writes. No substantial
  retirement, plugin expansion, release publication or optional codec migration
  is authorized by this DAG. Optional codec work is a later separate human decision;
  there is intentionally no runnable codec or publication card.

## Actual cards and direct dependencies

Every listed parent is a persisted dependency edge. Transitive dependencies are
not repeated in every row. M3 is shown explicitly to make the review gate auditable.
The full snapshot includes original assignees, body hashes and exact IDs:
[migration-dag.json](migration-dag.json).

| Stage | Task ID | Implementer | Direct parents | Deliverable |
| --- | --- | --- | --- | --- |
| Q1 | t_f4d107ea | architect | M3 | Rust/native pins, retained-input audit, exact ABI contract |
| B01 | t_22299c6f | tester | M3 | Immutable format/volume/error interoperability corpus |
| B02 | t_7019eca0 | tester | M3 | Native name identity/code-page/property precedence |
| B03 | t_bf92ce13 | tester | M3 | Native metadata, large-file, input scan and partial I/O |
| B04 | t_2a64c953 | tester | M3 | Sandboxed extraction/overwrite/partial effects |
| B05 | t_3859d918 | tester | M3, B01 | Native password callback states and encrypted errors |
| B06 | t_83983e9c | tester | M3, B04 | Native staged cancel/progress/shutdown oracle |
| S1 | t_31358a3f | coder | M3, Q1 | Workspace and owned Archive/ArchiveEntry/domain contracts |
| S2a | t_071e4cd7 | coder | M3, S1, Q1, B01, B02, B03, B05, B06 | Internal non-product facade and safe-wrapper qualification build |
| B08 | t_0a04d8dd | tester | M3, S2a | Additional native ABI/lifetime/fault/stress qualification suite |
| S3 | t_481c87b0 | coder | M3, B08, B01, B02 | Qualified safe engine exposure and CLI listing |
| S4 | t_e398de63 | coder | M3, S3, B03, B04, B05, B06 | CLI extraction through retained policy |
| S5 | t_9ca14b05 | coder | M3, S4, B01, B05, B06 | CLI testing via retained testMode |
| S6 | t_425adbdd | coder | M3, S5, B03, B02, B05, B06 | Fresh archive creation via retained UpdateArchive |
| S7 | t_61c84597 | coder | M3, S6, B06, B08 | General task/progress/lossless outcomes/cancellation |
| S8 | t_49ccd799 | coder | M3, S7, B02, B03, B04 | Portable ports and retained read-only stream seam |
| S8L | t_be89f382 | coder | M3, S8 | Linux stream module and native CLI compatibility |
| S8W | t_595610a4 | coder | M3, S8 | Windows stream module and native fork compatibility |
| S8M | t_600ba1b2 | coder | M3, S8 | macOS stream module and native CLI compatibility |
| B07 | t_2e00825a | tester | M3, S7, B02, B05 | Native legacy GUI/settings/reopen/desktop characterization |
| Q2 | t_7ac2c6d5 | architect | M3, Q1, S8L, S8W, S8M | Native Qt/CXX-Qt pins/licenses/lifetime spike |
| S9a | t_bedc9b95 | coder | M3, Q2, B07, S8L, S8W, S8M | Qt 6/QML shell and CXX-Qt adapter |
| S9b | t_ce984818 | coder | M3, S9a, B07, B02 | Owned browser/selection and characterized reopen |
| S10 | t_d3f76753 | coder | M3, S9b, S4, S6, S7, B07 | Extraction/create dialogs and async task UI |
| S11W | t_1f366758 | coder | M3, S10, B07, S8W | Windows Explorer/OLE/settings/coexistence |
| S11L | t_f757c611 | coder | M3, S10, B07, S8L | Additive Linux desktop/package integration |
| S11M | t_7b347d4f | coder | M3, S10, B07, S8M | Additive macOS bundle/Finder integration |
| Q3 | t_8342040b | architect | M3, S11W, S11L, S11M, Q2 | Actual selected-package audit and human validation-scope gate |
| S12 | t_11923d05 | tester | M3, Q3, S11W, S11L, S11M | Exact-head native candidate validation, no publication |

The production spine is S1 -> S2a -> B08 -> S3 -> S4 -> S5 -> S6 -> S7 -> S8
-> native stream modules -> Q2/S9a -> S9b -> S10 -> native desktop modules
-> Q3 -> S12. B07 can gather legacy evidence alongside late CLI/platform work;
it cannot authorize early Qt implementation.

B08 cannot test a nonexistent bridge. S2a therefore delivers an INTERNAL,
non-product, independently reviewed qualification implementation first, with its
own ABI/failure/lifetime self-tests. B08 then authors additional qualification
artifacts; only its independently reviewed PASS releases S3 production exposure.
It is not a substitute review lane for S2a. All cards, including documentation,
evidence and qualification cards, retain their own same-card reviewer loop.
Likewise, downstream B cards and S12 are later engineering stages, not M3 review
children: M3 must request review, never self-complete to start them.

## Evidence blockers and native matrix

| Missing evidence | First affected gate in this graph | Ongoing acceptance |
| --- | --- | --- |
| B01 formats/errors/interoperability | S2a then S3 | S4–S6/S12 preserve immutable external corpus and actual capability inventory |
| B02 names/properties | S2a then S3 | Native Windows canonical code pages, byte paths and platform identity through GUI |
| B03 metadata/I/O/large files | S2a stream qualification, then S4 | S6 input scan/partial writes; S8/platform streams; retained output metadata parity |
| B04 extraction safety | B06 and S4 | S8, UI and release sandbox effects; no guessed containment/overwrite semantics |
| B05 password boundary | S2a | Extract/test/create/UI keep undefined/empty/cancel and item/call errors distinct |
| B06 cancel/progress | S2a minimum transport | S4–S7 and UI/native shutdown; no pause/latency guarantees without evidence |
| B07 GUI/settings/desktop | S9a | S9b/S10/S11 native desktop evidence, not source guards or CLI CI alone |
| B08 ownership/concurrency | S3 public exposure | Every added operation reruns/extends ABI/fault/quiescence tests |
| Q1 pins/licenses/ABI | S1 and S2a | Actual selected objects/runtime/registration, not assumed dynamic-link legality |
| Q2 Qt/native spike/licenses | S9a | Exact pinned native GUI builds and lifecycle tests |
| Q3 scope/signing/package audit | S12 | Actual human scope and supplied/verified credentials, or explicit narrowed unsigned validation |

Each card requires actual native Windows, Linux and macOS evidence for its changed
surface; target-specific cards require their named OS. Record OS/arch/filesystem,
locale, compiler/runtime/flags, oracle commit/binary digest, fixture provenance,
commands, raw outcomes and artifact digests. Wine/cross-compilation is supplemental.
Unsupported and unqualified differ; required unqualified cases cannot be silently
excluded to pass a card. New Linux/macOS desktop integration is additive, not a
fictional legacy GUI parity claim.

B04 hostile archives run only with independently enforced disposable containment;
block before execution when isolation is insufficient. Real oracle/desired-safety
conflicts require human resolution, not reproducing dangerous writes and not
silently changing behavior. Never edit goldens to make new code pass.

## Execution, subscriptions and review contract

Actual `hermes profile list` returned `architect`, `coder`, `tester`, `reviewer`,
`orchestrator` (and unrelated profiles). Only discovered specialists are assigned.
The gateway configuration read shows `max_in_progress: 2`,
`max_in_progress_per_profile: 1`, `failure_limit: 2`, `review_dispatch: true`.
No configuration was changed. Every new card sets `max_runtime_seconds: 7200` and
states `max-retries=2`, including substantive review failures. The create tool has
no max_retries parameter: rows inherit the verified dispatcher failure limit of 2;
reviewer/implementer must additionally count substantive CHANGES rounds and escalate
at two, since a runtime counter alone does not measure review failures.

These are board-local profile limits, not a cross-board global mutex. No additional
active cards were found in the other discovered board databases during this run.
Do not duplicate migration work on other boards. Preserve the project-wide maximum
of two workers; independent evidence/pin work may run concurrently, but each coder
subtree is scheduled under one coder profile. Reviewer integration is serial.

All created events record `creator_task_id: t_82c76197`. Exact durable operator
subscription tuples were compared read-only against M3, without printing or
committing chat/user IDs: every child inherits Telegram, owner `default`, mode
`notify+wake`, including delivery metadata. The tool's `subscribed: false` response
means no extra current-session subscription was added; it does not negate the
persisted creator/dependency inheritance. Do not reconfigure Telegram or invent IDs.

Every card must:

1. Read its assigned AGENTS.md and check source branch before migration. Use its
   own dispatcher-created worktree/branch, not the common source path stored as
   the worktree origin. Record the actual allocated branch/path after dispatch;
   do not guess the fallback branch name. Bring required reviewed parent commits
   by ordinary merge/cherry-pick after inspecting handoffs; mere parent completion
   or a surviving worktree is not a sufficient import mechanism.
2. Implement only its scope, run exact relevant native builds/tests, commit
   deliverables, and record changed files, commands/results, compatibility evidence,
   limits/risks, branch/commit and durable artifact paths. Cargo checks use the
   actual qualified manifests/pins, not an assumed future member list. Docs require
   link/path/evidence checks and an explanation if executable builds do not apply.
3. Request same-card review with `reviewer`; never self-complete. Reviewer PASS
   may complete; CHANGES returns the SAME card to its original implementer. Never
   generate infinite repair cards or use a needs_input block as a review queue.
   Two substantive failures require human escalation, not a fresh counter/card.
4. Reviewer alone may serially integrate reviewed non-destructive commits into
   clean local `ai/migration-bootstrap-20260911`, with preservation checks, parent
   ancestry and integration evidence. Never merge shared `dev-main`, rewrite user
   history, remove secrets/changes, or publish a release.
5. Use concise Simplified Chinese for operator summaries/gates while preserving
   identifiers and literal errors. Engineering artifacts stay English.

A future genuine human gate uses an actual `kanban_block(kind="needs_input")`
event, not just an initially blocked status. Record exact issue/evidence, 2–3
options, recommendation and impacts. Typical choices: retain measured behavior
and gather missing evidence (recommended, delays affected scope); approve a narrow
behavior-change ADR (compatibility cost); defer the feature explicitly (reduced
scope). License/toolchain failure can instead retain/qualify another compatible
pin, defer affected linkage, or seek a human-reviewed architecture change.
Never archive unresolved gates/unreviewed prerequisites, treat notify+wake as
approval, or unblock credentials without provision and real verification.

Q3 gathers concrete late-stage selected-package evidence before requesting the
precise human validation/signing scope. It is a dependency-gated engineering card
now, not a fabricated already-resolved human gate. It MUST emit needs_input when
that required decision is absent. An explicit unsigned validation-only choice may
narrow S12, but cannot yield a signed/notarized or release-ready claim. Publication
still has no authorization or runnable card. Independent eligible work continues.

## Reproducible validation

Run from the repository/worktree root with ordinary Python 3 (no dependencies):

```sh
python3 docs/ai-migration/validate-migration-dag.py
python3 docs/ai-migration/validate-migration-dag.py --board-db "$HERMES_KANBAN_DB"
python3 .github/tests/release_version_test.py
python3 .github/tests/change_notice_test.py "$PWD"
python3 .github/tests/lang_files_test.py "$PWD"
python3 .github/tests/shell_ext_identity.py "$PWD"
python3 .github/tests/shell_ext_lang_reload.py "$PWD"
bash .github/tests/release_notes_test.sh
git diff --check
```

The offline validator checks all stage IDs, exact independently specified
prerequisite sets, acyclicity, isolation/review/runtime policy, document card
coverage and local links. Its three negative controls reject a missing M3 edge,
a cycle and a dangling edge. The optional live pre-review check reads SQLite with
`mode=ro`, validates the entire board DAG, M1/M2 reviewer PASS/commit metadata,
exact live child bodies/fields/edges, creator lineage, unclaimed `todo` states and
full inherited routing tuples without emitting identities. It deliberately fails
after M3 release; use the offline check for later repository regression. Never
regenerate a snapshot to conceal an unreviewed live dependency change.

Actual execution: offline and live validators returned exit 0: 29 children,
104 child edges; the complete live board had 36 tasks and 109 edges. All children
were `todo`/unclaimed, both parent review commits and exact inherited routes
matched, and all three negative controls passed. The six existing checks above
all returned exit 0: version/identity/notes reported 0 failed; notices reported
34 modified upstream files, 0 without a notice; languages reported 93 files and
0 problems; reload reported 0 problems. No native archive/Qt runtime test is
claimed for M3's documentation-only change.

Final commit and artifact paths accompany M3's structured review handoff. Three
temporary read-only board inspection/snapshot scripts remain untracked under
`.m3-artifacts/`; they are not deliverables. The headless security guard rejected
their batch deletion before execution, so cleanup was not retried or bypassed.
No source change or verification is blocked by retaining those local scratch files.
The committed graph/validator are durable and do not rely on a worktree remaining
after completion. Review must independently re-read live cards and confirm the
gate and subscription evidence before completing M3.
