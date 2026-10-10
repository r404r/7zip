# M3-D3 mainline unblock reassessment

Status: research decision draft; not implementation or execution authorization

Task: `t_f9a57f84`

Evidence cutoff: `2026-09-16T01:36:30Z`, local automation base and task start at
`f6ca43ab5d370ef7a379a58e1735b45b17cd91f9`

Prior determination: [second-development-slice-determination.md](second-development-slice-determination.md)
at `f683cd35039ccb30e159f9e997097a7b3181fddb`

## Executive determination

The M3-D2 negative determination remains controlling for archive operations.
Later reviewed work removed a registration-composition implementation
uncertainty, but it did not supply the semantic, ownership, safety, or licensing
inputs needed to implement retained-engine `open`, `entries`, or `close`:

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

P1/P2/P3B/S2a-R make the already-disabled facade composition more portable and
better tested. They do not overturn M3-D2's source-backed counterexamples for
B01 ordered-chain/error semantics, B03 stream/failure cleanup, B05 pre-parse
interaction, or B06 callback retention/quiescence. There is therefore no
immediately routable second DEVELOPMENT coder slice under the current reviewed
acceptance rules. `qualified_operations` remains `0`; no product caller or CLI
may reach an archive operation.

An operator could separately approve an architecture/acceptance amendment that
permits implementation while those inputs remain unknown, but that would change
the rule in AGENTS.md that input-bearing dependencies stay in force and would
accept rework plus FFI lifetime/semantic risk. This report does not recommend or
request that amendment. Independent review PASS would not constitute such
approval.

## Decision rule

A deferred parent is evidence-only for a proposed DEVELOPMENT slice only when its
future result can confirm or reject the implementation without supplying a
semantic choice, ownership rule, safety boundary, or licensing permission needed
to write that slice. The parent stays input-bearing when its result determines
what the code must do or whether the proposed activity may safely or legally run.
No live dependency is deleted. Disabled exposure alone is not a basis for
reclassifying an input-bearing dependency as confirming evidence.

Q1 and M2 fix transport declarations and intended ownership constraints; they
do not provide every legal retained-engine observation needed to implement those
constraints. See [archive_bridge_v1.h](qualification/archive_bridge_v1.h) and
[abi-v1.md](qualification/abi-v1.md). P3B and S2a-R fix and test portable
retained-registration composition only. A non-product feature flag limits
exposure; it does not turn unresolved implementation inputs into later
confirmation. The per-gate application of this rule appears below.

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
change `qualified_operations`. It removes uncertainty about portable,
retained-source-preserving registration composition. It does not make a real
`open`/`entries`/`close` implementation finite under the reviewed dependency
rule because none of the following input-bearing counterexamples changed:

- **B01:** Q1 requires ordered chain records, `CArcErrorInfo`, non-open errors,
  properties, volume behavior, and contextual `S_FALSE`. The retained source
  distinguishes error-field definedness (`CPP/7zip/UI/Common/OpenArchive.h:149-225`)
  and `Open_Strict` can convert nominal `S_OK` to `S_FALSE` for a nested non-open
  error (`OpenArchive.h:424-440`). Registration correspondence supplies no
  fail-closed mapping for those legal outcomes.
- **B03:** real Open owns an `IInStream`/`ISequentialInStream` and native path
  (`OpenArchive.h:117-145`), repeatedly seeks and reads while probing
  (`OpenArchive.cpp:2487-2507,3279-3297`), and consumes a Seek contract whose
  `newPosition` is undefined on failure (`CPP/7zip/IStream.h:88-100`). Rejecting
  malformed ABI envelopes does not choose short-read, seek-failure, EOF, large
  offset, or failed-open cleanup behavior.
- **B05:** `CryptoGetTextPassword` returns `E_NOTIMPL` without a provider and
  otherwise forwards the request (`ArchiveOpenCallback.cpp:369-385`). A
  header-encrypted input can ask during Open before the caller can classify it
  as non-encrypted/non-interactive. Returning `INTERACTION_UNAVAILABLE` would be
  a new outcome mapping, not a source-backed fail-closed precondition.
- **B06:** Open polling is non-uniform (`ArchiveOpenCallback.cpp:389-403` and
  `OpenArchive.cpp:2543-2555`), while multivolume streams retain callback state
  after Open (`ArchiveOpenCallback.h:88-95` and
  `ArchiveOpenCallback.cpp:357-363`). A synthetic callback invocation cannot
  prove retained-handler lifetime, return-time quiescence, or safe close.

Entries and close require the real session created by Open. A synthetic session
would test a new mock rather than retained-engine item count, reverse release,
and generation invalidation (`OpenArchive.h:267-346,390-443`;
`OpenArchive.cpp:3172-3191`). No honest source-backed mapping avoids all four
unresolved inputs, so the ordinary sequencing proposal is withdrawn.

## Candidate route assessment

### A. Disabled internal open / entries / close DEVELOPMENT slice — not viable under current rules

Disabled exposure, allowlisted fixtures, and `qualified_operations=0` reduce user
risk but do not resolve the B01/B03/B05/B06 inputs above. A repository-owned
non-password fixture cannot prove before parsing that retained Open will not ask
for a password or volume. Synthetic fault or callback injection can test local
adapter validation only; it cannot establish retained Open outcomes, handler
requests, retention, or quiescence. Routing this slice would therefore require
an explicit operator-approved architecture/acceptance amendment, not an ordinary
sequencing decision. No such amendment is requested here.

### B. B08-owned lifetime/fault/concurrency harness before open/list — not yet meaningful

Some reusable fault-injection and ownership checks could be written against the
current four-export facade. However, S2a-DEV already has nine capability and six
lifetime contract tests, including mismatch, stale/foreign-context and result
ownership paths. A new B08 sub-slice today would either duplicate those tests or
invent blocked-open/session behavior before the exports exist. It becomes valuable
only after qualified S2a provides real operation/session behavior. It should
remain tester-owned and must not contain bridge fixes. A pre-operation synthetic
harness proves only its own injection surface and cannot claim B08 evidence.

### C. No-operation `archive-cli` shell — reject

The current workspace intentionally has no binary target, and the existing Linux
development artifact says `component.runnable_binary=none`. A shell that exposes
no operation would add parsing/packaging surface without testing the retained
engine or unblocking S3. It could be mistaken for a product despite having no
qualified behavior. There is no concrete downstream value that outweighs that
confusion.

### D. Resolve the input-bearing critical path — only currently valid route

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
| 1 | Critical-path evidence resolution (Route D) | Long before operation code, but shortest valid route to meaningful retained-engine implementation and product exposure | Highest when B04 remains frozen until proven containment and resource-heavy tests are redesigned | Lowest eventual product risk | Must resolve every listed input-bearing gate and native campaign; no waiver |
| 2 | Continue narrow hosted ABI/build/link/registration evidence | Short, but improves only the existing disabled facade | High when no hostile archives or product exposure are added | Low; cannot answer operation semantics | B01/B03/B04/B05/B06/S2a/B08/S3 all remain open; Windows `!ERROR` and `qualified_operations=0` remain |
| 3 | Operator-approved architecture/acceptance amendment | Potentially short to code after a separate explicit decision | Lower: implementation proceeds with known semantic/lifetime gaps | High rework and compatibility risk; may encode behavior before its oracle exists | Does not qualify or expose operations; every native, safety, licensing, B08 and product obligation remains open |

Recommendation: choose rank 1 and retain M3-D2's negative determination. Rank 2
may continue only where it has independent downstream value; it is not a bridge
operation unblock. Rank 3 is documented for completeness, but is not recommended
because it changes the input-bearing dependency rule and accepts avoidable
semantic, ownership, and compatibility risk. Reviewer PASS on this report cannot
approve rank 3.

## Exact live dependency map and next bounded evidence

No new sibling or coder card is proposed. The old and new dependency maps are
identical; the explicit edges are:

- S2a `t_071e4cd7` has exactly these nine parents:
  `t_178b131f` (S2a-DEV), `t_22299c6f` (B01), `t_31358a3f` (S1),
  `t_3859d918` (B05), `t_7019eca0` (B02), `t_82c76197` (M3),
  `t_83983e9c` (B06), `t_bf92ce13` (B03), and `t_f4d107ea` (Q1).
- B08 `t_0a04d8dd` has exactly `t_071e4cd7` (S2a) and `t_82c76197`
  (M3) as parents.
- S3 `t_481c87b0` has exactly `t_0a04d8dd` (B08), `t_22299c6f`
  (B01), `t_7019eca0` (B02), and `t_82c76197` (M3) as parents.
- Proposed new edges: none. Removed edges: none. There is no S2a-DEV2 sibling,
  so there is no sibling-to-S2a, sibling-to-B08, or sibling-to-S3 connection.

The shortest critical path remains: resolve sufficient B01 ordered-chain/error
and admission evidence, bounded B03 stream/failure-cleanup behavior, and actual
B05 password/interaction behavior; resolve B04 containment before B06 native
cancellation/quiescence work; then S2a, B08, and S3.

Exactly one bounded next evidence task is recommended: produce an independently
reviewed **B01 admission decision packet** for the already-identified external
RAR/multipart candidates, containing member-level provenance, redistribution/use
terms, immutable hashes, and an explicit admit/reject recommendation, without
opening or executing the archives. This converts the current licensing/admission
unknown into a decision and determines whether those candidates may participate
in later native oracle work. It does not itself supply Open semantics, qualify
B01, or release any downstream card; if rights cannot be established, reject the
candidates and retain quarantine rather than broadening policy.

Runtime tests would be required for any future operation implementation because
it changes FFI/session ownership. They are not applicable to this research-only
report, which changes no executable code.

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
- **B08:** after qualified S2a supplies real operations and sessions, add
  independent tests rather than bridge fixes. Use sanitizers only where supported
  and record exclusions instead of inventing parity.

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
whitespace, reviewed-parent ancestry and preservation checks. External citation
verification is ledger-independent: retrieve the two literal URLs in `## Sources`
with `curl -L --fail --max-time 30` and require HTTP success. The optional
`sources.py` ledger is not part of this artifact, and no profile-local cache or
credential is required. Validation executed for the corrected report:

- `python3 -m json.tool docs/ai-migration/migration-dag.json >/dev/null && python3 docs/ai-migration/validate-migration-dag.py` — PASS: 29 children, 104 edges, acyclic; amendment PASS; 10 negative controls PASS.
- `git diff --check` — PASS.
- `git diff --name-only` — PASS: only
  `docs/ai-migration/m3-d3-mainline-unblock-reassessment.md`.
- `git diff --exit-code -- C CPP Asm rust .github AGENTS.md docs/ai-migration/migration-dag.md docs/ai-migration/migration-dag.json docs/ai-migration/validate-migration-dag.py` — PASS: forbidden and graph paths unchanged.
- `test -f AGENTS.md` and `git merge-base --is-ancestor` for `f6ca43ab5d370ef7a379a58e1735b45b17cd91f9` and `a01d9034a4ae0228a61bb5765e10cb1d9e0329dc` — PASS.
- `test -f` for all three local Markdown targets and five cited retained-source
  files — PASS.
- `curl -L --fail --max-time 30` for both GitHub Docs sources and CI run
  `34980048480` — PASS, HTTP 200 for all three URLs.

## Residual risks

- The negative determination leaves operation implementation blocked until its
  input-bearing gates resolve or a separately reviewed and explicitly approved
  architecture/acceptance amendment changes the rule.
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
