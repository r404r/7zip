# M2: migration stages and acceptance gates

Status: architecture sequencing for review, not the live task DAG. Task
`t_db8ffe0b`, branch `ai/migration-m2`; reviewed M0 `1b54c95` is already an ancestor
of this worktree at `3aea9f8`. [Target architecture](architecture-target.md) and
[ADR-0001](adr/0001-retained-engine-facade.md),
[ADR-0002](adr/0002-ownership-tasks-platforms.md),
[ADR-0003](adr/0003-qt-build-qualification.md) define shared decisions.

M1 (`t_f4afeee1`) owns characterization; M2 does not edit its fixtures/documents or
assume its eventual results. M3 (`t_82c76197`) must inspect BOTH independent PASS
handoffs before creating the detailed remaining DAG and must itself be reviewed
before releasing production children. M2 authors request same-card independent
review; M3 is an orchestration child, not an alternate M2 review lane.

## 1. Dependency rules for M3

- Read actual profiles and assign bounded specialist cards, not hypothetical names.
  Every card carries scope/non-scope, accepted API/model decisions, reviewed parent
  commits, isolated worktree/branch, exact tests, compatibility matrix, reviewer,
  runtime cap, two-substantive-failure limit, human-block policy and artifact paths.
- Bring reviewed required commits into each worktree before dependent edits. Verify
  source checkout remains ai/migration-bootstrap-20260911 and AGENTS.md exists.
- Scope every operation to M1's measured capabilities. PASS on M1 documentation is
  not proof that every semantic case is characterized. Make missing qualification
  an explicit prerequisite before the affected production change. Independent
  skeleton/value-model work need not wait for unrelated GUI or release credentials.
- All production descendants initially depend on reviewed M3. Native validation,
  relevant fixture/oracle gaps, package audit and toolchain pins are real graph
  dependencies, not optional checklist prose. Never archive unresolved gates.
- Serialize shared header, crate-root and make/build changes under their owner.
  Domain/API choices are those in M2; siblings may not settle competing schemas.
  Parallel work is only independent nonoverlapping evidence/platform boundaries;
  preserve the project's active-worker limits and durable operator subscriptions.
- Implementation -> verification -> reviewer -> PASS. CHANGES returns the same
  card to its implementer; two substantive failures require escalation. Only the
  reviewer serially integrates reviewed non-destructive commits into the clean
  local bootstrap. Never merge dev-main or publish releases automatically.

## 2. Ordered stages

Labels S1-S13 below are planning labels, not fabricated task IDs. Qualification
subcards can gather evidence earlier when independent, but cannot release a later
production layer before its preceding stage and relevant coverage pass.

| Stage | Depends on | Scope / retained boundary | Exit evidence |
| --- | --- | --- | --- |
| M0 archaeology | Bootstrap verification | Reviewed current architecture, platform map, engine seams and risks | Existing reviewed parent commit and source citations |
| M1 characterization; M2 architecture | Reviewed M0 | Concurrent tests versus design; no M2 production edits | Independent PASS on both, explicit remaining coverage gaps |
| M3 DAG orchestration | Reviewed M1 + M2 | Real cards and links only; no production implementation | Independent review, real assignees, acyclic gated graph, inherited subscriptions |
| S1 Rust workspace and domain values | Reviewed M3; Rust toolchain pin | Proposed rust/ packages, domain models, CLI-only defaults and dependency checks; legacy engine untouched | Native cargo build/test/fmt/clippy using recorded exact commands; owned text/IDs/unknown-property round trips, no OS/Qt leakage |
| S2 minimal engine bridge | S1; retained-input license/build audit; ABI/header review; relevant M1 open/list coverage | C facade and safe worker wrapper, capabilities/open/pages/close, minimal safe callbacks/cancel; retain CArchiveLink and codec scope | Native matched ABI/build manifests; open/close/failure/ownership tests, sanitizers where available, no registry loss from linking |
| S3 Rust CLI listing | S2; list/probing/name/property characterization | CLI parsing/output/domain selection; retain handler decoding/probing and old CLI oracle | Differential formats/properties/Unicode/volumes/corruption/exit-output cases; session and paging stress |
| S4 Rust CLI extraction | S3; write/overwrite/path/link/password/metadata/cancel coverage | Retained Extract and ArchiveExtractCallback policy, no new delete/overwrite semantics | Sandboxed differential tree/payload/metadata/partial-output comparison, prompt cancel/disconnect, native platform cases |
| S5 Rust CLI testing | S4; corrupt/encrypted/test-mode characterization | Retained extraction testMode; no second decoder | Correct per-item + call errors, no output files, password/CRC/header/unsupported methods and cancellation |
| S6 Rust CLI creation | S5; creation/update-planner/property/partial-write coverage | Retained UpdateArchive and input scan; no implicit broad delete/update feature | Native format/method capability cases, metadata/property/password precedence, full disk/cancel outputs and fresh-open validation |
| S7 task/progress/cancellation infrastructure | S6; callback and shutdown coverage | General task manager, scheduling and UX beyond minimal bridge safety; initially one engine worker | Stress concurrent progress, unknown totals, stale/duplicate replies, lossless outcomes, cancel/shutdown and partial effects; any pause support separately characterized |
| S8 filesystem abstraction replacement | S7; service-specific native oracle | Replace one retained app/platform I/O service at a time under portable ports; not codecs | Differential short I/O/seek/large-file, path/native-name, link/security/time/replace behavior on each supported filesystem |
| S9 Qt/QML shell then browser | S8; reviewed Qt/CXX-Qt pin/license/spike; browsing/reopen characterization | Qt shell, CXX-Qt adapter then owned archive model and navigation | Native Qt-thread/lifetime/shutdown tests, lossless IDs/sizes, stale-generation invalidation, eligible code-page reopen rollback and localization |
| S10 extraction/create UI | S9; corresponding CLI/task parity | Typed dialogs, selection and async task views; no QML engine policy | Native password/overwrite/volume prompts, cancel, settings precedence, accessibility/keyboard and partial-effect reports |
| S11 desktop integration | S10; per-platform native integration coverage | Windows Explorer/OLE/settings/coexistence; separately scoped Linux/macOS desktop services | Native shell activation, associations, drag/drop temp lifetime, fork identity/language, packaging integration evidence; CLI green is insufficient |
| S12 native release validation | S11; complete selected-input audit and actual signing/packaging prerequisites | Build/install/upgrade/uninstall artifacts and compatibility report only; no automatic publication | Exact-head native Windows/Linux/macOS release matrix, reproducible capability/license inventory, approved release scope and explicit human publication gate |
| S13 optional codec work | Separate later evidence-backed human decision | No codec migration planned by this DAG | Separate justification, compatibility/performance/security evidence and review; never implied by S12 |

S1 may define models and contracts without linking Qt or the engine. Toolchain pin
selection is an engineering qualification subcard, not permission to install an
unreviewed production dependency arbitrarily. ABI review precedes writing mutually
dependent C/Rust layouts. Qt spike timing remains before GUI but after eligible
CLI/filesystem work, as ADR-0003 specifies.

## 3. Compatibility evidence matrix

For every changed surface record legacy executable commit/digest, product/bundle,
compiler/target/flags, filesystem/locale, fixture provenance and native test runner.
Compare structured outcomes as well as CLI output/exit status. Ignore only explicitly
reviewed nondeterministic differences; never normalize away name/order/time/error
semantics to make tests pass. Known unsupported cases remain visible.

| Risk / behavior | Evidence before affected implementation | Canonical environment |
| --- | --- | --- |
| R01/R14 format and bundle scope | Actual capability enumeration, object manifest, known good and damaged archives by read/test/create capability | Native Windows, Linux, macOS with matched product scope |
| R03/R04/R12 filename code pages | ZIP EFS/Unicode extras including CRC validity, explicit/scoped/unscoped CP932/936/UTF-8, Unix-host heuristic, TAR properties, reused-handler reset, invalid/non-BMP names | Windows is canonical for Win32 conversions; Unix results separately measured, never assumed equivalent |
| R02 overwrite/containment | Existing targets, skip/rename/all choices, absolute/traversal names, links/reparse/races, permission errors and partial output in disposable sandbox | Native each target filesystem; human decision on semantic/data-loss ambiguity |
| R05/R06/R07 FFI/thread/cancel | Allocation failure, open/close/reopen rollback, module teardown, callback overlap, prompt shutdown, stale IDs, report backpressure and no use-after-free | Native builds plus ASan/UBSan/TSan or platform tools where supported; log exclusions |
| R08/R09 encrypted/errors | Missing/empty/wrong/correct/non-ASCII passwords, encrypted headers, supported ZIP/7z crypto, CRC/data/header errors, warnings, truncated and multivolume archives | Native each target; preserve engine result distinctions and secret redaction |
| R10 metadata/large files | Sizes beyond 32-bit, sparse/short I/O/full disk, timestamp precision/zones, modes/attributes, links, ADS/security where supported | Native Windows plus distinct Linux/macOS filesystems |
| R11/R12 GUI and desktop | Browse/reopen eligibility/restoration, saved UTF-8 versus transient Auto, QML lifecycle, prompts, OLE/drag-drop, Explorer language/CLSID and coexistence | Native desktop sessions per OS; not headless CLI-only results |
| R13 packaging/licenses | Selected objects and transitive crates/Qt modules, notices/source/relink obligations, unRAR restriction, assets, installer/signing scope | Reviewed inventory plus human resolution where obligations remain unclear |

Existing .github/tests source guards and migration-smoke.py are preservation/smoke
checks, not proof of this entire matrix. Cross-compilation and Wine are supplemental
only. Lack of native infrastructure creates an actual dependency/capability gate
on affected qualification; do not claim PASS or manufacture logs.

## 4. Strangler replacement and rollback policy

Keep the old CLI, Win32 File Manager/GUI, Explorer DLL, FAR/SFX, handlers/codecs and
legacy build targets available. Introduce a new CLI/app beside them, opt-in until
its declared surface is proven. Replacement scope is explicit per operation and
platform, not all formats because one ZIP passed.

For each application helper retirement: identify all call sites, freeze legacy
oracle evidence, add the Rust implementation behind the owned port, compare effects
in a sandbox, independently review and retain a documented route back to the legacy
implementation. Switching implementations must not double-run destructive commands;
no transparent retry using the old engine after partial extraction or update.
Future feature flags may select the path before execution, never infer safe retry.
No existing user data, expected fixtures or shared history is deleted to simplify
rollback. Substantial legacy removal requires human approval and separate evidence.
Mature codecs/encryption have no retirement authorization here.

## 5. Human gates versus ordinary work

M2 needs no new human decision merely to document the prescribed architecture.
Future selected-package uncertainties and unmeasured semantics cannot be treated as
resolved by this statement. When actually encountered, block the affected card with
kind needs_input and exact issue, original evidence, options and impacts:

- Semantics/data loss: recommended retain measured behavior and extend characterization
  (delays affected rewrite); approve a precisely scoped behavior-change ADR (changes
  compatibility expectations); defer that feature explicitly (narrows release scope).
- License/package uncertainty: recommended hold affected linkage/distribution while
  a human resolves selected obligations (independent code/design may continue);
  approve another audited arrangement (build/relink/retest cost); defer package
  feature (no claim of replacement parity).
- Material Qt/toolchain failure: recommended qualify a supported pinned combination
  (investigation cost); defer GUI while eligible CLI work continues (desktop delay);
  propose an alternative ADR for human review (architecture/parity rework).

An authorized credential setup is resolved only by supplied credentials plus real
verification, not another approval request or a notify+wake event. Do not print
secrets in evidence. Ordinary dependency waits are not invented semantic gates.
Never archive gates/unreviewed prerequisites, invent approvals or unblock without
resolution. Record all operator-facing explanations in Simplified Chinese while
preserving technical identifiers and literal raw errors.

## 6. M2 documentation verification record

Only architecture-target.md, this file and the three linked ADRs are changed.
No source/build/fixture edits, installations, native GUI runs, archive binary runs,
shared-branch integration or release publication were performed by M2. Executable
build tests for a new implementation are not applicable: there is no implementation
in this card. Downstream qualification is required, not falsely reported complete.

Executed in `/home/ding/work/github/r404r/7zip/.worktrees/t_db8ffe0b`:

```sh
python3 .github/tests/release_version_test.py
python3 .github/tests/change_notice_test.py "$PWD"
python3 .github/tests/lang_files_test.py "$PWD"
python3 .github/tests/shell_ext_identity.py "$PWD"
python3 .github/tests/shell_ext_lang_reload.py "$PWD"
bash .github/tests/release_notes_test.sh
```

All returned exit 0: release/version, identity and notes report 0 failed;
notices report 34 modified upstream files, 0 without a notice; languages report
93 language files checked, 0 problem(s); reload reports 0 problem(s).
Source reads checked IArchive/IStream/IPassword, CMyComPtr/CCodecs, COpenOptions,
SetProperties, reopen rollback, native text conversion and retained bundle inputs.
M0 supplies broader source context. Proposed new paths are explicitly marked as
new; companion links are checked against actual files. Final whitespace/scope and
commit checks are recorded in the review handoff. An execute_code read helper was
blocked by headless approval policy before execution; normal read_file calls were
used instead, with no bypass and no automated citation-check claim.

Review must independently confirm source-informed boundaries, ownership and task
lifecycle coherence, stage order, native coverage gates, license/toolchain limits,
link targets and documentation-only scope. PASS is a reviewer decision, not this
author's status declaration. Branch/commit and absolute deliverable paths accompany
the request-review transition so M3 need not rely on a surviving worktree.
