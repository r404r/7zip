# B04-P: bounded GitHub Actions containment recovery plan

Status: preparation only; proposed execution is NOT authorized.
Owner/card: architect / `t_4882b482`; implementation remains on `t_2a64c953`.
Assessment date: 2026-09-11 UTC. Branch: `wt/t_4882b482`.

## Decision in brief

GitHub Actions is already the native execution environment, not an untried
alternative to the two failed experiments. Its standard fresh VMs can supply
compute at no additional runner charge for this actual public repository. They
are not, by themselves, a safe boundary between the tested process and the
runner agent, credentials, network, or evidence collector in that same VM.

Recommend ONE newly authorized, bounded **process-sandbox startup diagnosis**
phase, retaining the existing candidates and all denial expectations. Do not
adopt the whole runner VM as the security boundary. This is the smallest useful
reversible next step, not a promise that the three sandboxes can be repaired.
No demonstrated cross-platform containment solution exists in current evidence.
If that finite phase cannot produce an exact non-expanding repair, stop; do not
roll forward into successive audit/retry cards or quietly switch boundary.

This report may PASS independent preparation review without B04 qualifying.
It does not reset B04's two-failure history, authorize a third native round,
resolve its `triage` gate, or release B06/S4/S8. Human approval of acceleration
only authorized this read-only preparation. There is no existing user VM;
personal offline Windows/Mac machines remain a conditional last resort, not
approved test hosts. Offline removes neither local data loss nor credential,
mounted-volume, system integrity, and result-tampering risks.

## Authority, repository state, and evidence identity

- Read source and assigned worktree `AGENTS.md`; source was clean on
  `ai/migration-bootstrap-20260911`, assigned branch clean at
  `e580347d0b6ceebb1aec14a2d69840660258e848`.
- Reviewed M3 parent `0706af3d714e8c2701691a19a0c663ae7b749c88` is already an
  ancestor. No parent import was needed. M3 approves sequencing, not containment.
- Read the complete B04 comments and all returned runs (29, 42, 44, 45), including
  human decisions. Run 44 independently verified the first negative evidence
  and returned CHANGES on `69f869258665eeb6f55486f89732f2ebd70d95a4`.
  That was NOT a safety prerequisite PASS.
- The latest B04 worktree was clean at
  `97288080b748483b8576238d05568644ff4e8c10`. Its diagnostic implementation and
  evidence still lack independent review. It was inspected read-only, NOT
  cherry-picked, qualified, or integrated. `git show 9728808:<path>` provides
  durable access even if that worktree disappears.
- Capture 1: `5dee62a1a526063374f332370269dcadab9c4168`,
  [run 34569823142](https://github.com/r404r/7zip/actions/runs/34569823142).
  Capture 2: `2b18c183d3a49dcef65ad1c4f4f1d507c68e7e9f`,
  [run 34572155278](https://github.com/r404r/7zip/actions/runs/34572155278).
  The four executable/workflow sources at capture 2 equal those at `9728808`.
  An evidence-freeze commit is not an exact-head CI pass.
- Both committed evidence manifests verified byte-for-byte locally. Capture 2
  run/head/failure and its three unexpired artifact IDs were re-read from GitHub:
  Ubuntu `10188190448`, Windows `10188181091`, macOS `10188177460`.
  This report did not re-download these archives or execute any captured code.
  The first round's independent byte comparison is the reviewer's prior evidence;
  the latest local hash checks and remote metadata are this author's observations.
- Read-only subscription comparison confirmed the exact M3 default Telegram
  `notify+wake` route on this task, including delivery metadata, without printing
  route identifiers. An additional TUI subscription is not a Telegram mismatch.

Durable B04 paths below are relative to commit `9728808`, not this report's tree:
`.github/tests/migration/b04/{prerequisite.py,probe.c,winlaunch.c,test_prerequisite.py}`,
`.github/tests/migration/b04/evidence/{MANIFEST.sha256,DIAGNOSTIC-MANIFEST.sha256}`,
`.github/tests/migration/b04/evidence/{34569823142,34572155278}/`,
`.github/workflows/b04-native.yml`, and
`docs/ai-migration/qualification/b04.md`.

## Where execution actually fails

Common path: `b04-native.yml` -> unit suite -> `prerequisite.py` CLI ->
`capture(destination)` -> compile fixed C probe -> independent baseline/sandbox
control envelopes -> `sandbox_command(...)` -> `run(...)` -> `parse(...)` ->
`controls_pass(...)`. The unit suite includes an end-to-end capture of its own:
its success only means safe success OR rejection produced a report. Thus each
old job contains more launches than the explicit capture alone; a new budget
must count those, not treat unittest as static inspection.

All capture-2 baselines report nine true relations, zero baseline exit status;
all sandbox maps are empty, sentinels unchanged, and `controls_pass=false`.
No launch/no records is not proof of successful containment.

| Platform observed | Exact stopping evidence | Known stage / unknown cause |
| --- | --- | --- |
| Ubuntu, Linux `6.17.0-1022-azure`, x86_64, glibc 2.39; installed bubblewrap `0.9.0-1ubuntu0.1` | `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`; startup and sandbox exit 1 | `--unshare-all` enters bwrap network setup before executing `/usr/bin/true` or `/probe`. Upstream `loopback_setup()` constructs RTM_NEWADDR and checks the netlink request. The precise host policy/capability denial has NOT been established. |
| macOS `26.6.2`, arm64 | `"startup_returncode": -6`, `"sandbox_returncode": -6`; empty stdout/stderr | `sandbox-exec -f candidate.sb` under deny-default policy fails before any record, including fixed `/usr/bin/true`. Negative POSIX subprocess status indicates signal 6, not an identified loader denial or a probe crash location. Exact process/denial remains unknown. |
| Windows Server 2025, build `10.0.26100`, x64 toolchain | `B04-launch stage=launch api=CreateProcessW error=2` | SID derivation, envelope/work DACL grants, low-integrity label and attribute setup get past their checks; `CreateProcessW` fails before child wait/exit. The missing object is not identified. |
| Windows missing-envelope negative control | `B04-launch stage=setup api=GetNamedSecurityInfoW error=2` | Deliberate ACL-read rejection, distinct from sandbox launch failure; `launcher_rejection_pass=true`. |

Windows call path: `wmain` -> `DeriveAppContainerSidFromAppContainerName` ->
`grant` (`GetNamedSecurityInfoW`, `SetEntriesInAclW`, `SetNamedSecurityInfoW`) ->
low-integrity SACL -> `InitializeProcThreadAttributeList` ->
`UpdateProcThreadAttribute(PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES)` ->
`CreateProcessW` with no capabilities, no inherited handles, and an empty
Unicode environment. SID/ACL/descriptor/attribute allocations are released;
process/thread handles close after bounded wait. No Job Object currently owns
an entire descendant tree. A timeout kill is not cancellation compatibility.

The official Microsoft launch guidance creates a profile, with per-user
folders and registry storage; `DeriveAppContainerSidFromAppContainerName` is
not profile creation. This makes the profileless design a concrete concern,
not proof that profile absence caused error 2. Creating a profile would add
writable locations outside the current work-root contract and is NOT a minimal
approved repair. Nor is replacing the AppContainer with an ordinary restricted
token automatically an equivalent network/filesystem boundary.

Linux retains read-only runtime/probe mounts and fresh tmpfs, no writable host
bind, host home, host `/tmp`, `/proc`, device tree, or host network. AppArmor's
user-namespace capability restrictions are a plausible explanation requiring
actual policy/audit evidence; neither the error text nor local success identifies
AppArmor as the proven cause. Upstream `main` was read only for call-path context,
not represented as the exact Ubuntu patched package source.

macOS currently allows execution, sysctl reads, system/envelope file reads and
work-subpath writes, with no blanket Mach lookup/network/fork grant. Runtime
loader needs, path canonicalization and sandbox OS-version support are hypotheses
for diagnosis, not permission to add broad exceptions. A path rule alone does
not establish preexisting-hardlink/race isolation.

## Exactly two approaches assessed

### A. Retain and diagnose the process sandboxes (recommended next phase)

Keep the runner/collector trusted and the fixed probe confined. Preserve mounts,
zero network capabilities, work-only grants, closed handles and minimal
environments. Reversible changes are diagnostic instrumentation, explicit image
labels, fixed-path identity checks and fail-closed report/cleanup improvements.
A path/argument/runtime-packaging correction is acceptable only when an exact
observed cause supports it and it adds no effective access. Do not guess such a
correction from the present errors. Allowlist expansion, host-policy changes,
new AppContainer storage, sharing network/IPC, privileged fallback or weakening
expected relations are outside approach A's proposed budget.

Feasible now: source review and preparation, with a clearly bounded native
observation proposal. Not established: startup repair on any hosted platform,
let alone full safety. Linux has local bounded positive evidence, but hosted
policy differs. Windows and macOS require more than a successful empty command.
This route minimizes changes to the existing implementation and trust boundary.

### B. Disposable VM as an outer boundary (not selected)

A new hosted VM per job can isolate one job from other jobs and the provider
host at the documented service boundary. It does NOT put the Actions runner
agent outside the guest. Linux/macOS jobs have passwordless sudo; Windows jobs
are administrator with UAC disabled. Treating all guest writes as disposable
would admit writes to agent/workspace/control files, credential locations,
result buffers and installed tools. Emptying the child's environment or setting
`permissions: {}` cannot remove the agent's runtime authority or separate its
memory/files. Provider-required networking also remains active. Killing the
agent or disconnecting the entire VM breaks collection and cancellation rather
than establishing an independent oracle.

A genuinely independent guest would need a trusted outer supervisor, immutable
input transfer, no credentials/runner inside the tested guest, no writable
shared mounts/device passthrough, isolated networking, and bounded non-executable
result transfer after quiescence. These are new security and operational
contracts, not a runner-label substitution. No such environment is supplied.

| Native platform | Outer-guest feasibility under zero-additional-cost constraints |
| --- | --- |
| Linux x64 | GitHub documents Android hardware acceleration, not a qualified arbitrary nested-guest containment service. Hypervisor support, storage budget, no shared mounts and supervisor separation would need proof; neither Docker nor a job container alone supplies a separate kernel or protects its socket/control plane. Not provisioned or approved. |
| Windows x64 | Standard hosted Windows supplies its own VM, not a contractual nested Hyper-V/Windows Sandbox guest with independent supervisor. Feature enablement, reboot, image licensing and isolated output paths are unverified. Do not infer rights to another Windows guest from the hosted image license. |
| macOS arm64 | Official hosted-runner reference explicitly says nested virtualization is unsupported. `macos-latest` is arm64 in the observed run. Switching to Intel is a different native/image tuple, not proof of nested support or permission to redistribute/install a guest image. No verified zero-cost three-platform route. |

No VM provisioning, paid/larger runners, self-hosted machines, or commercial
licenses are requested by this preparation. Whole-VM boundary expansion is
rejected as a shortcut, not declared impossible in all future environments.

## Provider eligibility, costs and acceptable use

Live `gh repo view r404r/7zip --json nameWithOwner,visibility,isArchived,url`
returned `PUBLIC`, `isArchived=false`. Live repository Actions permissions were
`enabled=true`, `allowed_actions=all`, `sha_pinning_required=false`. The actual
workflow uses `ubuntu-latest`, `macos-latest`, `windows-latest`; all are standard
labels listed in [GitHub's runner reference][runners]. This establishes current
free standard-runner compute eligibility, not a generic public-repo assumption
or an account-wide billing audit. Repository visibility and label eligibility
must be rechecked at any approved execution time. No private/larger runner,
custom image service, paid marketplace action, or additional VM is acceptable.

[Billing documentation][billing] distinguishes free standard compute from
artifact/cache storage accounting, with shared storage allowances. Current
account-wide remaining artifact/Packages quota was NOT accessed or proven;
small files and short retention alone cannot prove zero incremental storage
cost. Therefore the recommended bounded round uses **logs only**, no new
`upload-artifact`, cache save, package/image publication, or external storage.
The trusted controller emits size-limited encoded diagnostic bytes and hashes;
GitHub documents logs/summaries as outside artifact storage allowance. Reviewer
retrieves logs through read-only `gh run view ... --log` and freezes sanitized
raw diagnostic records in the existing B04 evidence path. Existing artifacts
are untouched. If logs cannot preserve complete bounded evidence, fail rather
than silently add billable storage. A future artifact-based round needs verified
zero-cost storage eligibility before approval, not a guessed balance.

The [Actions terms][terms] permit project development/testing and prohibit
unauthorized access/disruption and disproportionate resource use. Their Apple
software provision does not grant general nested-image redistribution rights.
The [malware/exploits policy][aup] permits dual-use research content but is not
blanket execution or provider-attack authorization. This proposal only uses
self-authored, bounded controls against harness-created files/endpoints; no
malware acquisition, exploit execution, provider penetration tests, real token
reads, scanning, denial of service, disk fill, or user data. If a later fixture
or platform requirement creates a licensing/terms ambiguity, obtain a real
human/provider resolution before execution.

## Finite proposed next phase: one diagnostic round, not qualification

Authorization delta: after this report's independent review, ask the operator
explicitly to approve ONE additional B04 diagnostic round with the limits below.
Historical two failures remain recorded. The earlier conditional VM approval
and notification wake do not approve this round. No change to the current B04
card state is made by B04-P. No new implementation card is created here.

Before any push or launch, the original tester prepares changes in the existing
isolated B04 branch and obtains an independent static review of `9728808` plus
the exact proposed delta. That review must not mark the B04 card done. Scope:

| Exact file/entrypoint | Allowed proposed work |
| --- | --- |
| `.github/tests/migration/b04/prerequisite.py`: `capture`, `sandbox_command`, `run` | Whitelisted identity/startup diagnostics, bounded output, explicit stop/cleanup accounting. Never arbitrary commands, archive execution, environment dumps or fallback. |
| `.github/tests/migration/b04/winlaunch.c`: `wmain`, `grant`, `diagnostic` | Record existence/type/final path and binary identity for generated executable and working directory, sanitized stage/error evidence. Preserve profileless/no-capability contract; do not broaden ACLs. |
| `.github/tests/migration/b04/probe.c`: fixed `main` | Keep nine existing file relations. Additional harmless controls only if explicitly enumerated/reviewed within the budget; no archive parser. |
| `.github/tests/migration/b04/test_prerequisite.py`: `GateTest` | Separate pure gate/evidence tests from `test_native_candidate_emits_fail_closed_report` for the approved CI entry; retain the test, do not remove coverage or count its hidden native launch as free. |
| `.github/workflows/b04-native.yml`: `prerequisite` job | Manual-only diagnostic dispatch on exact approved B04 ref; remove automatic push execution for this round, pin reviewed action SHAs, standard explicit OS labels, `max-parallel: 1`, retain 10-minute timeout, disable artifact upload/cache use for logs-only evidence. No other workflow changes. |
| `.github/tests/migration/b04/evidence/`, `docs/ai-migration/qualification/b04.md` | Append actual observations, run/head/image/tool identity and bounded conclusion; never replace either historical manifest or expectations. |

Proposed matrix: `ubuntu-24.04` x64, `windows-2025-vs2026` x64,
`macos-26` arm64, matching the observed major image families. Labels are not
immutable image versions: record actual image build and stop on unexpected
OS/architecture rather than claim parity. No Intel/macOS or OS-version sweep.

- Linux observation: package version/path/mode/hash; own launcher identity,
  current AppArmor label and relevant namespace-restriction values read-only;
  narrowly filtered launch-time audit diagnostics if already accessible without
  policy changes. Identify the denied setup operation before proposing a fix.
  No sudo launch of the probe, AppArmor edits, `--share-net`, profile transition
  bypass, cap addition, or package-version roulette.
- macOS observation: preserve exact `.sb`, resolved generated paths, executable
  architecture/signature identity and bounded crash/denial records for just the
  two fixed startup/probe processes. No full system log/profile dumps, SIP
  changes, broad Mach/file access or new sandbox API substitution.
- Windows observation: generated `probe.exe` and work-directory identity before
  `CreateProcessW`; sanitized immediate API error and only process-specific
  diagnostic records accessible through approved built-in tooling. Do not
  install a tracing driver, create an AppContainer profile, read real credential
  files, or retry under an unrestricted child token.

Budget: one implementation pass and one independent static review, at most one
same-card revision; two substantive review failures escalate. At most ONE
native matrix invocation, three jobs sequentially, 10 minutes per job, with no
rerun or replacement job. Per platform: one build sequence, one deliberate
unconfined fixed-file baseline, one fixed startup control on Unix (Windows uses
its existing missing-envelope rejection), and one sandbox probe. Pure tests
must not launch additional captures. Each subprocess remains capped at 60
seconds; Windows child wait 20 seconds plus at most 5 seconds termination wait.
No repeated fix/test cycle within the same job. A setup failure consumes that
platform's attempt and prohibits further sandbox launches for it.

All new control content is self-authored and finite: at most 64 files, 1 MiB
payload total, 64 MiB scratch/evidence beyond installed tools, 1 MiB emitted
encoded diagnostic log per platform; fixed probes, not adversarial exhaustion.
No arbitrary process-tree/resource stress. If descendant controls are included,
limit to one child and one grandchild and enforce a reviewed tree-kill mechanism
before launch; otherwise record descendant qualification as missing. The current
harness does not enforce all these caps; implementation/static review must do
so before authorization is exercised. More capacity is a stop, not an automatic
budget increase. Aggregate job wall-time ceiling is 30 minutes (queue excluded).

### Controls, protected assets and collection contract

The next round diagnoses startup; the following remain prerequisites before
ANY hostile extraction. Harmless controls must test rejection, not attack actual
provider assets. Existing nine relations remain mandatory and unchanged.

| Asset/boundary | Required harmless check and fail-closed condition |
| --- | --- |
| Filesystem, aliases, mounts | Baseline may change only its new sentinels. Sandbox must deny existing absolute/traversal/symlink/hardlink outside writes while inside operations work. Add preexisting-alias/reparse and bounded rename-race sentinels only within disposable envelopes; no actual host paths. A surviving sentinel after startup failure is rejection, never PASS. Windows reparse and native volume effects cannot be inferred from Linux EXDEV/tmpfs. |
| Credentials and control plane | No secrets/OIDC/PAT inputs; checkout never persists credentials; child environment/handles allowlisted. Static mount/DACL/IPC analysis excludes runner agent, workspace scripts, home, job command files, Docker socket and credentials. Controlled dummy secret/control files test denial without reading real values or probing agent memory. Their denial supplements, not replaces, the access-policy proof. |
| Network/IPC | Prove child has no route/capability to host/provider/Internet and no host IPC channel. Use only a harness-owned local listener/dummy IPC object with a harmless nonce; no request to actual metadata/token endpoints. A blocked child with a functioning trusted collector is required; whole-runner disconnection is not a substitute. No positive Internet control. |
| Resources and descendants | Controller owns launch, deadlines, byte caps and cleanup. Test capped child lifetime using self-authored helpers, not fork bombs/disk fill. Orphan or unbounded output invalidates evidence and ends the round. Provider job cleanup is defense in depth, not the sole mechanism. |
| Results and oracle | Parent owns manifest, expected relations and immutable source identity outside child write scope. Capture raw bytes to bounded parent pipes; never stream untrusted text as GitHub workflow commands or append it to `GITHUB_ENV`/`GITHUB_OUTPUT`. Child-writable Windows `probe.log` is untrusted evidence, not authority. Quiesce descendants before collecting; no following symlinks/reparse points, executing output, importing output scripts or recursive trusted extraction. Malformed/duplicate/missing/truncated records fail. External reviewer recomputes relations/hashes from exact run/head logs. |

For the finite diagnostic phase, missing broader controls are explicitly NOT
QUALIFIED; they cannot be converted to a startup PASS. A future safety verdict
requires all relevant rows implemented and observed, plus independent review
of the actual extraction/collection entrypoints, not just this probe. This
report is not an instruction to implement a general sandbox now.

Stop immediately on policy expansion, real data/credential exposure, outside
sentinel mutation in the sandbox, unknown identity, absent diagnostics, resource
cap breach, collector ambiguity, timeout or leftover descendants. Capture only
safe bounded diagnostic records, kill owned processes through reviewed handles,
verify quiescence, and remove only the parent-created disposable tree without
following links. Do not clean shared checkouts or persist modified guest images.
If cleanup cannot be proven, report failure and let the fresh hosted job end;
do not resume work in that guest. Preserve prior Git evidence untouched.

End-of-round deliverable is exactly one platform matrix with either a supported
non-expanding repair proposal or a precise blocker. No archive execution occurs
in this round, even if all bounded file controls pass. A repair requiring another
native run has no budget here. On failure, retain the original B04 gate and
present two actionable choices: (1) defer full B04 and continue independent work
(recommended when no exact safe repair exists; affected dependents stay gated),
(2) seek an explicitly supplied independent disposable-guest contract under
approach B (higher operational/licensing effort, not assumed zero-cost or
available). Personal machines are not the default implementation of choice 2.

## Compatibility and remaining risk

The retained call path remains `CPP/7zip/UI/Common/Extract.cpp:232-250` calling
`IInArchive::Extract`, closing `CArchiveExtractCallback`, then `ExtractResult`.
`ArchiveExtractCallback.cpp:1380-1408` obtains properties, corrects path parts,
creates folders and forms the destination; `CheckExistFile` at 1246-1371 routes
interactive overwrite through `AskOverwrite` and includes rename/delete effects.
It returns `E_ABORT` for cancel, and some skipped/error paths retain `S_OK` with
no output stream. A sandbox denial is not a new expected engine HRESULT or
permission to sanitize differently in Rust. No Rust sanitizer, codec, encryption,
GUI or production changes are proposed. Target Qt 6/QML -> CXX-Qt -> Rust ->
mature C/C++ engine and the reviewed M3 graph remain unchanged.

Elementary inside link checks do not prove ACL/metadata parity. Linux tmpfs is
not native persistent-filesystem semantics; macOS path rules are not alias/race
proof; Windows low integrity/AppContainer can distort permission/reparse results.
ASCII probe paths do not qualify Unicode/archive filename code-page behavior.
Tree/payload/hash/metadata, collisions, overwrite answers, EOF/cancel, null streams
and partial effects remain absent. No new Windows/Linux/macOS runtime evidence,
GUI/desktop compatibility, safe extraction or B04 PASS is claimed by this report.

## Preparation verification and review handoff

Only this Markdown file is changed. Executable builds and B04 unittests are NOT
applicable to authoring this report; notably the B04 unittest would launch a
sandbox and is prohibited here. No build, sandbox, native capture, CI dispatch,
push, provisioning, spending, secret/config change, or gate edit was performed.

Performed read-only checks:

- `git branch --show-current`, source `git -C ... branch --show-current`, both
  `git status --short`, and `git merge-base --is-ancestor 0706af3 HEAD`: correct
  branches/clean starting trees/parent present, exit 0. An initial `git status`
  mistakenly named a source-tree absolute file from the task worktree and failed
  as outside repository; corrected source-root `git -C ... status --short` passed.
- `git show 9728808:<path>` for the B04 sources/workflow/document and all three
  diagnostic reports; read-only B04 worktree HEAD/status confirmed `9728808`.
- `git diff --exit-code 2b18c18 9728808 --` the four sources named above: exit 0.
- From the B04 worktree, `sha256sum -c
  .github/tests/migration/b04/evidence/MANIFEST.sha256` and the corresponding
  `DIAGNOSTIC-MANIFEST.sha256`: both exit 0, every entry OK; no normalization.
- `gh auth status`: existing authentication valid, no setup performed; masked
  token output is not copied into the artifact. Repository query and
  `gh api repos/r404r/7zip/actions/permissions`: exit 0, eligibility above.
- `gh run view 34572155278 --repo r404r/7zip --json headSha,conclusion,jobs,url`
  and `gh api repos/r404r/7zip/actions/runs/34572155278/artifacts`: exit 0,
  exact capture head, three failed jobs and three unexpired artifacts.
  Existing logs were read (`gh run view ... --log`, line display capped at 450
  characters); runner image/package statements above use those observations,
  not a newly executed probe. Raw committed evidence remains unchanged.
- Read-only `python3.14 -m sqlite3 "$HERMES_KANBAN_DB" <SELECT>` compared M3 and
  task Telegram route fields with `IS` equality and checked the parent edge.
  Result: matching default `notify+wake` route; identifiers withheld. Initial
  all-channel comparison rejected the extra TUI subscription; narrowed exact
  Telegram comparison passed. `sqlite3` CLI was unavailable; Python's SQLite
  module performed the query. No board/config write or approval bypass occurred.

Final document checks: `git diff --cached --check` passed; `test -f` for the two
local Markdown links passed; `git diff --exit-code e580347 -- C CPP Asm .github
AGENTS.md docs/ai-migration/migration-dag.json docs/ai-migration/migration-dag.md`
passed with no changes. `python3 docs/ai-migration/validate-migration-dag.py`
passed offline: 29 children, 104 child edges, three negative controls. This is
graph preservation, not live B04 or native safety qualification. A targeted
credential-pattern search in this file returned no matches. The document commit
and clean-tree results are recorded on the same-card review transition. Reviewer
must independently inspect claims and authorization, then on preparation PASS
post the precise report commit/path/limits to B04 and read back that comment.
Do not mark B04 qualified, complete, unblocked or archived. Do not integrate its
unreviewed `9728808` as a consequence of this report's review.

## Official sources checked

All accessed read-only on 2026-09-11; live docs are descriptive, not a frozen
provider promise. Short/incomplete web extractions were supplemented by official
raw source where available; no inaccessible text is represented as read.

- [GitHub-hosted runner specifications, privilege and communication model][runners].
- [GitHub Actions billing and log/storage distinction][billing].
- [GitHub Actions product terms][terms] (Actions section also read in full from
  [official Markdown](https://raw.githubusercontent.com/github/docs/main/content/site-policy/github-terms/github-terms-for-additional-products-and-features.md)).
- [GitHub active malware/exploits policy][aup].
- [GitHub secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use),
  supplemented with [official Markdown](https://raw.githubusercontent.com/github/docs/main/content/actions/reference/security/secure-use.md)
  for token, untrusted-output and immutable action pinning context.
- [Microsoft AppContainer launch guidance](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer)
  and [CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile):
  folders/registry storage and lifecycle, not proof of the observed missing object.
- [Upstream bubblewrap network.c](https://raw.githubusercontent.com/containers/bubblewrap/main/network.c)
  and [bubblewrap.c](https://raw.githubusercontent.com/containers/bubblewrap/main/bubblewrap.c):
  loopback setup call path only, not exact Ubuntu build provenance.
- [Ubuntu AppArmor documentation](https://documentation.ubuntu.com/security/security-features/privilege-restriction/apparmor):
  official page confirms namespace capability restriction context;
  no launch-time AppArmor audit record was obtained in this preparation.
- Repository rules: [AGENTS.md](../../../AGENTS.md); reviewed sequence:
  [migration-dag.md](../migration-dag.md).

[runners]: https://docs.github.com/en/actions/reference/runners/github-hosted-runners
[billing]: https://docs.github.com/en/billing/concepts/product-billing/github-actions
[terms]: https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features#actions
[aup]: https://docs.github.com/en/site-policy/acceptable-use-policies/github-active-malware-or-exploits
