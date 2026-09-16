# M3-D3 mainline unblock reassessment

Status: research decision draft; not implementation or execution authorization

Task: `t_f9a57f84`

Evidence cutoff: `2026-09-16T01:36:30Z`, local automation base and task start at
`f6ca43ab5d370ef7a379a58e1735b45b17cd91f9`

Prior determination: [second-development-slice-determination.md](second-development-slice-determination.md)
at `f683cd35039ccb30e159f9e997097a7b3181fddb`

## Executive determination

The M3-D2 conclusion is stale in one narrow respect. It was correct at its own
cutoff, when the retained registration identity mechanism was GNU/Itanium-only
and the MSVC facade remained only a fail-closed declaration. Later reviewed work
has removed that implementation uncertainty without claiming native Windows
qualification:

- P1 `t_c4bda156` added the staged facade-probe evidence path and was integrated
  by `e17b6b1`;
- P2 `t_2abc1c2f` restricted the legacy workflow trigger and was integrated by
  `286b12a`;
- the first P3 accessor proposal (`eb2771f`, integrated by `ed6a0e0`) was rejected
  because it edited retained source and is historical only;
- P3B `t_eb67a575` replaced it with the explicit 54-translation-unit redirection
  specification at `998fcbe23b5c7b71f1dbb09f6036d12e9fc9a6c2`, integrated by `19ca3f4`;
- S2a-R `t_13a346c7` implemented and independently reviewed that mechanism through
  `f6ca43ab5d370ef7a379a58e1735b45b17cd91f9`. Exact-head CI run
  [34980048480](https://github.com/r404r/7zip/actions/runs/34980048480) passed the
  Linux/macOS facade jobs and all three Rust-workspace jobs. The Windows facade
  probe stopped at the retained `!ERROR` by design.

A finite second DEVELOPMENT slice now exists: implement the already-reviewed Q1
`open` / owned paged `entries` / `close` ABI behind the non-default internal
facade, keep every product caller unable to reach it, and keep
`qualified_operations=0`. This is implementation staging, not S2a qualification.
It does not satisfy or remove B01, B03, B05, B06, S2a, B08, or S3.

Because this changes migration sequencing and scopes a new implementation card,
the recommendation below is a **draft requiring explicit operator approval after
independent review of this report**. Reviewer PASS on this report is not that
approval.

## Decision rule

A deferred parent is evidence-only for a proposed DEVELOPMENT slice only when its
future result can confirm or reject the implementation without supplying a
semantic choice, ownership rule, safety boundary, or licensing permission needed
to write that slice. The parent stays input-bearing when its result determines
what the code must do or whether the proposed activity may safely or legally run.
No live dependency is deleted merely because a separate disabled slice can be
staged.

The reviewed Q1 declaration and M2 ownership model already fix the ABI, native
path representation, arena ownership, context/session generations, result
destruction, error domains, callback lifetimes, and fail-before-effects rules.
See [archive_bridge_v1.h](qualification/archive_bridge_v1.h) and
[abi-v1.md](qualification/abi-v1.md). P3B and S2a-R now also fix and prove the
portable retained-registration mechanism used to construct the matched facade.
The unresolved native campaigns remain necessary before qualification and
exposure, but they no longer prevent writing a disabled implementation that
makes no compatibility claim.

## Live gate map

The table distinguishes the current technical role from the Kanban status. A
status can be mechanically accurate while its old explanatory text is stale.

| Gate | Live state at cutoff | Input-bearing semantic / ownership / safety / licensing matter | Confirming qualification evidence still required | Answered stop/freeze or future human gate | Stale or obsolete state |
| --- | --- | --- | --- | --- | --- |
| B01 `t_22299c6f` | `triage`; `import_approved=false`, `qualified=false` | External RAR/multipart members still lack complete provenance, actual member rights, and approved admission. Those are licensing/admission inputs for using that corpus, not merely missing CI logs. | Complete required-format/interoperability corpus, native Windows/Linux/macOS oracle results, structured errors, multivolume/probing and drift controls. | Reviewed B01-I-P says current facilities do not safely support member inspection; retain quarantine/freeze until material new evidence or a changed decision. Any import requires a future explicit admission decision. | Earlier claims that machine availability alone was the blocker are obsolete. The operator now permits personal machines, but that does not grant corpus rights or `import_approved`.
| B03 `t_bf92ce13` | `triage` | Native NTFS/APFS semantics, short/partial I/O, seek behavior, failed-output disposition and deterministic ENOSPC design affect implementation behavior. The original “nearly fill the host disk” design is rejected as unsafe. | Real Windows/NTFS and macOS/APFS runs with bounded leases/evidence; large-file, sparse, metadata and fault controls. | Operator allows personal Windows/macOS/Linux machines, but full-volume/disk-fill and other host-wide resource effects require a new explicit design review and confirmation. The earlier small-diagnostic authorization was conditional on infrastructure that was not then present. | “Personal machines prohibited” is stale. “Job Objects/ledger/storage already verified” is also stale; the card explicitly corrected that claim.
| B04 `t_2a64c953` | `blocked` | Proven containment outside the disposable root is a safety input before any hostile traversal/symlink/reparse/race archive may execute. Offline analysis did not establish Linux/Windows launch containment; macOS native failure remains unresolved. | Native containment enforcement and negative escape controls on each affected platform, before hostile archive execution. | Operator chose the recommended freeze. Reopen only after a changed decision or material containment evidence; native budget is zero. | None material: `blocked` reflects the current stop. The reviewed offline findings are useful evidence but are not containment PASS.
| B05 `t_3859d918` | `todo`, gated by B01 and B05-MAN-WM | Undefined versus defined-empty password, wrong/correct/non-ASCII behavior, actual `IPassword` callback, per-item/call error distinction, prompt EOF/cancel and redaction are semantic/security inputs. CLI `-p` is not equivalent. | Actual native Windows/Linux/macOS callback observations using public synthetic secrets and negative controls. | B05-MAN-WM `t_3acd4f76` was stopped by user choice C after repeated unsafe/incorrect runbook attempts. Future human redefinition or cancellation is required; quarantined `6fbf0fe` is not executable or integrable. | B05 itself has never run, so `todo` is accurate. Any older suggestion that the Windows/macOS bootstrap is deliverable is obsolete.
| B05-MAN-WM `t_3acd4f76` | `triage`, typed stop recorded | Safe operator instructions and platform-verified commands would be input to the native campaign. | None from the quarantined branch. A replacement would need independent review before operator use. | Answered stop: choice C. Do not integrate, execute, complete, or archive. | Its unreviewed runbook/checker content is superseded and dangerous; only the stop record is authoritative.
| B06 `t_83983e9c` | `todo`, gated by B04 | Exact polling/non-polling stages, cooperative cancellation, overlap/quiescence, partial outputs and shutdown behavior are semantic and safety inputs. Kill is not cancellation. | Real stage-triggered Windows console-control and Linux/macOS evidence, including prompt wait and integrity effects. | No separate execution approval exists. B04's freeze remains a hard predecessor. Any host-wide effect needs operator confirmation. | The preparation report is current but only an observation checklist; it is not an executable controller or qualification.
| B07 `t_2e00825a` | `todo`, gated by B07-MAN, B05 and other reviewed parents | Windows GUI reopen/settings/prompt/OLE/temp-lifetime and interaction semantics are inputs for Qt/desktop behavior. | Human desktop observations, screenshots/logs and preservation controls; source/CLI-only evidence cannot pass B07. | B07-MAN was stopped after round 10. Restart requires a newly reviewed, materially smaller safe boundary; the recorded possible direction is pure GUI observation with no registry mutation/deletion, but it is not authorized. | Older runbook commits, including `ddbf941`, are quarantined and not operator deliverables.
| B07-MAN `t_184bb07d` | `triage`, typed stop recorded | Safe executable instructions were themselves a safety/data input because prior drafts touched HKCU and personal paths. | None from the quarantined drafts. | Answered stop: retain quarantine; do not integrate or deliver. Future redesign needs a new decision. | The mechanical `triage` label should not be read as “awaiting routine specification”; the comment thread records a deliberate stop.
| S2a `t_071e4cd7` | `todo`; nine live parents | B01/B03/B05/B06 results remain input-bearing for full qualified open/list behavior, callbacks, errors and native stream handling. B08-style safety evidence is not a substitute. | Matched native Windows/Linux/macOS facade/runtime, differential fixtures, ABI/calling convention, sanitizers/stress, callbacks, teardown and dead-strip retention. | Future semantic conflicts still require human input. No operation may be exposed before S2a and B08 PASS. | The body is stale where it says S2a must implement handshake/context/capabilities: S2a-DEV already did so, and S2a-R fixed registration. Its live edges and qualification obligations are not stale.
| B08 `t_0a04d8dd` | `todo`, parents S2a and M3 | It is primarily independent safety qualification, but test design for blocked-open shutdown, prompt disconnect and copied results depends on the completed S2a operation behavior. It must not become the bridge-fix owner. | Native ABI/lifetime/fault/concurrency/sanitizer/stress evidence with explicit exclusions. | Defects return to the bridge owner; repeated safety ambiguity requires a future human gate. | No stale status. Existing facade lifetime tests are DEVELOPMENT contract tests, not B08 PASS.
| S3 `t_481c87b0` | `todo`, parents B08, B01, B02 and M3 | Product CLI output/error behavior depends on qualified B01/B02/B05-era oracle results and a B08-qualified safe engine. Product exposure is therefore input-bearing, not a mere CI confirmation. | Native Windows/Linux/macOS CLI differential and paging/stale/close stress after B08. | Any attempt to expose unqualified operations would require an explicit architecture/safety decision and is not recommended. | No stale status. A no-operation shell would not satisfy this card.

## What changed after M3-D2

M3-D2's negative determination explicitly cited the GNU/Itanium-only registration
wrapper, the unsolved MSVC path, missing sanitizer/dead-strip evidence, and
`qualified_operations=0`. It correctly rejected calling the existing four-export
facade an archive-operation slice.

The later work changes only the first two implementation facts:

1. P1 made the hosted facade probe and evidence packaging explicit.
2. P2 prevented the legacy Windows build workflow from being used as an
   accidental migration-branch qualification path.
3. P3B replaced private symbol wrapping and retained-source accessors with a
   per-object source-level rename applied to exactly 54 registration-bearing
   translation units. `LoadCodecs.cpp`, codec registration, the shim and the
   facade are outside that define.
4. S2a-R proves 60 captured registrations map one-to-one to the pre-`Hash` loaded
   rows and the complete 61-row frozen table, with process-isolated negative
   controls and fail-closed correspondence. Linux and macOS development builds
   passed. Windows recipes and guards are audited but the actual facade build is
   still deliberately refused.

This does **not** make Windows qualified, add sanitizers, qualify open/list, or
change `qualified_operations`. It does remove the uncertainty about whether a
portable, retained-source-preserving facade composition can be implemented at
all. That makes a disabled open/list/close implementation finite and reversible.

## Candidate route assessment

### A. Disabled internal open / entries / close DEVELOPMENT slice — viable

This is the only recommended immediate implementation route. Q1 already fixes the
revision-1 declarations and ownership rules. The implementation can be compiled
and contract-tested behind the existing non-default `facade` feature while every
product crate remains unable to call it. Tests can use repository-owned, public,
non-password, non-hostile fixtures and synthetic fault controls. Native campaigns
then qualify or correct it before exposure.

This route must not claim that deferred semantic inputs are irrelevant. Instead,
it creates a separate DEVELOPMENT card and leaves the existing S2a card and all
its parents unchanged. Any disagreement with a later oracle is fixed in the
implementation; it is not resolved by rewriting goldens or declaring the oracle
“evidence-only” retroactively.

### B. B08-owned lifetime/fault/concurrency harness before open/list — bounded but not first

Some reusable fault-injection and ownership checks could be written against the
current four-export facade. However, S2a-DEV already has nine capability and six
lifetime contract tests, including mismatch, stale/foreign-context and result
ownership paths. A new B08 sub-slice today would either duplicate those tests or
invent blocked-open/session behavior before the exports exist. It becomes valuable
immediately after Route A, when it can independently attack real session/result
lifetimes. It should remain tester-owned and must not contain bridge fixes.

### C. No-operation `archive-cli` shell — reject

The current workspace intentionally has no binary target, and the existing Linux
development artifact says `component.runnable_binary=none`. A shell that exposes
no operation would add parsing/packaging surface without testing the retained
engine or unblocking S3. It could be mistaken for a product despite having no
qualified behavior. There is no concrete downstream value that outweighs that
confusion.

### D. Resolve all input-bearing critical-path gates first — safest product path, slowest first code

The shortest path to **product** listing remains B01 plus bounded B03 and B05
native evidence; resolve B04 containment or formally redesign the B06 dependency;
then B06; then full S2a; then B08; then S3. This is the only route to qualified
product exposure. It is not the fastest route to meaningful implementation because
B01 has licensing/admission work, B04 is intentionally frozen, and the Windows/
macOS manual runbook attempts are stopped.

### E. Existing GitHub-hosted runners — useful for narrow ABI/build/link evidence only

GitHub documents that `runs-on` selects Linux, Windows and macOS hosted runners,
that a new VM is provisioned for a job, and that it is decommissioned afterward.[1]
The hosted-runner reference lists standard Windows, Linux and macOS images; public
repository standard runners are currently described as free and unlimited.[2]
Those runners are suitable for the exact questions P1/P2/P3B/S2a-R already ask:
compile flags, object composition, export/calling-convention checks, link closure,
frozen table correspondence, Rust tests and bounded synthetic fault injection.

Disposable VM lifetime is **not** containment evidence for hostile archives. It
does not prove that a path-traversal or reparse attack cannot leave the intended
root during the job, nor does it establish the operator's required safety boundary.
Hosted runners must not be used to bypass B04, execute unreviewed hostile inputs,
or reinterpret VM teardown as containment PASS.

## Ranked project-level paths

| Rank | Path | Time to first meaningful implementation | Safety | Compatibility risk | Retained obligations |
| --- | --- | --- | --- | --- | --- |
| 1 | Draft Route A: disabled internal open/list/close DEVELOPMENT slice | Short: one focused coder card after report review and explicit operator approval | High if fixture allowlist, no hostile/password inputs, no product reachability and fail-closed controls are enforced | Medium: real native/semantic differences are expected and must be corrected later; no user is exposed | All B01/B03/B04/B05/B06/S2a/B08/S3 obligations remain open; Windows facade remains fail-closed; `qualified_operations=0` |
| 2 | Critical-path evidence resolution (Route D) | Long before code, but shortest to real product exposure | Highest when B04 remains frozen until proven containment and resource-heavy tests are redesigned | Lowest eventual product risk | Must resolve every listed input-bearing gate and native campaign; no waiver |
| 3 | Independent B08 harness staging after Route A | Medium; useful as soon as real sessions exist | High; tester-owned and non-product | Low-to-medium, because it finds defects rather than selecting behavior | Does not pass B08 without native sanitizers/stress or release S3 |

Recommendation: choose rank 1 as a draft sequencing change, then immediately
follow it with rank 3 while continuing rank 2 in parallel where safe. This is not
permission to implement yet. After independent review, the operator must explicitly
approve or reject the new DEVELOPMENT scope. No recommendation here changes safety,
license, data-handling, qualification, or release policy.

## One routable coder slice (draft; approval required)

Proposed title: `S2a-DEV2 — Disabled retained facade open/list/close implementation`

Proposed assignee: `coder`; same-card independent reviewer: `reviewer`.

### Parent set

Use only reviewed, completed design/development inputs:

- Q1 `t_f4d107ea` (`5f07f21a6516e345db199d3d78a3a984118574a5`);
- S1 `t_31358a3f` (`e809c92b2d493412882f8a623f05fbe2ee508ff2`);
- B02 `t_7019eca0` (`72631ae748e1778af65c30d39e9fe68b8c6442a5`);
- S2a-DEV `t_178b131f` (reviewed head `bc61a7b`);
- S2a-R `t_13a346c7` (`f6ca43ab5d370ef7a379a58e1735b45b17cd91f9`);
- the independently reviewed M3-D3 decision artifact, plus explicit operator
  approval of this sequencing change.

Do not remove, relink, complete or archive any parent of S2a `t_071e4cd7`.
The new card is a sibling staging slice; S2a remains the qualification card.

### Fixed API and behavior

Implement exactly the existing revision-1 C declarations:

- `archive_bridge_v1_open`;
- `archive_bridge_v1_entries`;
- `archive_bridge_v1_close`;
- the ABI structs needed by those functions in `archive-engine-sys`;
- a safe owned internal adapter that copies all result views before
  `archive_bridge_v1_result_destroy` and remains `!Send`/`!Sync`.

Reuse the existing handshake, context, capability and result ownership. Use
retained `CArchiveLink` / `SetProperties`; never decode native names in Rust.
Archive IDs are never reused in a context. Generations reject stale requests.
`entries` is bounded by `first/count`; all caller envelopes, tags, reserved fields,
counts and pointer/count pairs fail closed before effects. `close` is idempotent
only where Q1 says so; otherwise return the fixed stale/invalid status rather than
inventing behavior. Exceptions and Rust unwind are contained at their respective
boundaries.

The callback posture is deliberately narrow:

- cancellation callback is present and uses a deterministic non-cancelled test
  adapter plus a synthetic cancellation control;
- progress may be absent;
- question callback is absent, and any password or volume interaction returns
  `INTERACTION_UNAVAILABLE` without supplying empty data;
- no password, encrypted-header, multivolume, external-plugin, hostile-path,
  extract, test, create, update or reopen fixture is used.

If implementing even this narrow posture requires deciding behavior not fixed by
Q1/M2, stop and block; do not infer it from CLI output.

### Owned paths

- `rust/bridge/archive_bridge_v1.cpp` and bridge-owned helpers/tests;
- `rust/bridge/build-manifest.py`, `makefile.gcc`, and `makefile` only as needed
  to compile/test these already-reserved exports;
- `rust/crates/archive-engine-sys/**`;
- `rust/crates/archive-engine/**`;
- focused DEVELOPMENT documentation under `docs/ai-migration/qualification/`;
- focused test wiring in `.github/workflows/rebuild-ci.yml` only if a separately
  reviewed workflow edit is included in the same isolated card.

### Forbidden paths and exposure

No edits to `C/`, `CPP/`, `Asm/`, codecs, crypto, format handlers, frozen Q1/B01/B02
records, fixtures/goldens, `archive_bridge_v1.h`, `archive-domain`, `archive-app`,
`archive-cli`, Qt/QML, installers, registry/services, packaging/signing/release,
legacy workflows, `AGENTS.md`, migration DAG, `dev-main`, or board edges/status.
No public safe-engine port, command, binary or GUI route may call the new exports.

### Exact dependency map

Old product/qualification path (unchanged):

`B01 + B03 + B05 + B06 + Q1 + S1 + S2a-DEV -> S2a -> B08 -> S3`

New DEVELOPMENT-only staging path:

`Q1 + S1 + B02 + S2a-DEV + S2a-R + reviewed M3-D3 + operator approval -> S2a-DEV2`

Then S2a consumes S2a-DEV2 implementation while retaining every original live
parent. B08 and S3 retain their current parents. No old edge is removed.

### Required negative controls

1. Restore `qualified_operations=0` as an exact assertion; any nonzero bit fails.
2. Build/export audit must show exactly the intended current plus three new
   operation exports and no CLI entry point.
3. Feature-off workspace build must contain no facade link or callable operation.
4. Link a mismatched header/manifest and prove handshake/context/open fail before
   effects.
5. Corrupt struct size, ABI major, tag, reserved field, pointer/count pair and
   page bounds independently; each must fail closed with null result/zero view.
6. Inject allocation failure and C++ exception at each arena/session construction
   phase; no leak, double-free or live session on failure.
7. Repeated result destruction, foreign-context result destruction, stale
   generation, repeated close and context destroy with live session/result must
   exercise their fixed status contracts.
8. Remove or mis-scope one of the 54 registration redirects and prove the existing
   correspondence guard fails.
9. Attempt a password/volume interaction with no `ask` callback and prove
   `INTERACTION_UNAVAILABLE`, never defined-empty password.
10. Repository boundary test must prove `archive-app`, `archive-cli` and Qt have
    no dependency or symbol reference to the operation adapter.

### Build, test and CI requirements

Run formatting, locked build/test and clippy for the default workspace and for the
non-default facade feature. Build the matched facade on Linux and macOS hosted CI,
run the new contract/lifetime/fault tests, layout checks, registration seam and
correspondence tests, boundary tests, warning-as-error audit and existing frozen
reference checks. The Windows job must continue to prove the retained `!ERROR`
fail-closed state unless a separate future gate authorizes its removal. Preserve
exact-head manifests, logs, digests and downloadable evidence artifacts.

Runtime tests are applicable to that future coder card because it changes FFI and
session ownership. They are not applicable to this research-only report, which
changes no executable code.

### Disabled exposure and deferred obligations

`qualified_operations` remains literal zero in C++ and Rust. The safe adapter is
internal, feature-gated, non-product and unreachable from all binaries. No artifact
is described as an archive tool. B01, B03, B04, B05, B06, S2a, B08 and S3 remain
open; native Windows facade, hostile-input containment, password semantics,
cancellation/progress, sanitizer/stress, native differential and release evidence
remain deferred but mandatory.

## Bounded remedies for the actual gates

- **B01:** continue only with rights/provenance evidence that can support an
  explicit import decision. Do not repeat acquisition or inspect opaque members
  without reviewed containment. Zero-cost synthetic/public fixtures may cover
  additional independent cases but cannot be represented as the missing RAR
  writer provenance.
- **B03:** redesign ENOSPC around a separately approved, bounded disposable object;
  never fill a shared/system disk. Use hosted CI for harmless compile/link and
  small-file metadata questions, but use actual operator filesystems only through
  an independently reviewed manual procedure.
- **B04:** retain freeze. The bounded remedy is proof of containment first, not a
  cheaper hostile run. No current repository or hosted-runner evidence meets it.
- **B05:** replace the stopped cross-platform runbook only if the operator reopens
  it. A new plan should be platform-authored/verified and start from read-only
  environment capture plus public synthetic secrets; do not reuse `6fbf0fe`.
- **B06:** reuse the reviewed observation checklist, but wait for B04's safety
  resolution and use stage instrumentation rather than sleep/kill.
- **B07:** if reopened, redesign to pure GUI observation with no registry mutation,
  deletion or custom checker. That scope needs independent safety review before
  operator use.
- **B08:** after S2a-DEV2, add independent tests rather than bridge fixes. Use
  sanitizers only where supported and record exclusions instead of inventing
  parity.

All remedies preserve zero additional payment and avoid VM/guest installation,
commercial tools, registry/services/mount mutation, shared-disk exhaustion and
hostile archive execution without proven containment.

## Delivery and continuity risks

The local automation base `ai/migration-bootstrap-20260911` and this worktree both
start at `f6ca43a`. The shared `dev-main` remains
`143e2c5dd24d084614ba32017a72d822cd2bea75` and must not be merged automatically.
The remote `origin/ai/migration-bootstrap-20260911` is stale at `44ba9df`, while
`origin/wt/t_13a346c7` contains exact reviewed head `f6ca43a`. Thus the current work
is remotely recoverable through a task branch, but the named long-lived automation
base is not itself backed up at the current head. This is a delivery continuity
risk, not permission to push or change branch policy.

The migration workflow emits evidence, not an operator-runnable archive product.
Its Linux development artifact explicitly records no binary target and
`qualified_operations=0`. Facade-probe artifacts contain manifests, logs and a
non-product development library for contract verification; the Windows facade is
absent by design. The legacy `7zip-win-x64` artifact belongs to the retained
legacy workflow, not the Rust migration product. No current migration artifact
should be handed to an operator as a new archive application.

## Validation of this documentation card

This card changes one English Markdown report only. It modifies no runtime,
workflow, fixture, golden, DAG, board edge/status, credential or production path;
therefore native archive execution and runtime tests are not applicable. The
required validation is document scope, links/paths, citation integrity, Git
whitespace, reviewed-parent ancestry and preservation checks. Exact commands and
results are recorded in the task handoff after execution.

## Residual risks

- The proposed slice can still expose incorrect retained-engine behavior to its
  tests; disabled reachability limits user risk but does not make defects harmless
  inside CI. Fault and lifetime controls remain mandatory.
- Windows implementation remains compile-declared and fail-closed, not built.
- Later native oracle evidence may require implementation changes. That is expected
  and must not be recast as a reason to alter goldens.
- B01 licensing/admission and B04 containment can still block the product path
  indefinitely.
- Local-only integration plus a stale named remote base risks loss or confusion;
  remote backup policy remains a human decision.

## Sources

[1] https://docs.github.com/en/enterprise-cloud@latest/actions/how-tos/manage-runners/github-hosted-runners/use-github-hosted-runners — Using GitHub-hosted runners
[2] https://docs.github.com/en/actions/reference/runners/github-hosted-runners — GitHub-hosted runners reference
