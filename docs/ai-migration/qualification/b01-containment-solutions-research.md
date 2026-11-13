# B01-I-R: free containment solutions for bounded member inspection

Task `t_46457821`, branch `wt/t_46457821`. Author research, pending independent
review. Research date: **2026-09-12 JST / 2026-09-11 UTC**. This is an auxiliary
implementation handoff with deferred verification, **not an executable or approved
envelope and not a new prerequisite for main development**.

## 1. Decision and authority

**Recommend ending this auxiliary research at independent review and retaining
native containment validation as a low-priority TODO while the coordinator advances
the main project.** Actual user steering, read back from this card's comments at
`1789146465` and `1789146544`, supersedes the original guest-first/execution-next
research framing: prioritize main development, defer Linux/Mac/Windows machine
validation, exclude large dependencies including QEMU/guest/new virtualization
stacks, do not extend retrieval or create more research/validation cards.

Of the two previously researched envelopes, V is excluded. P (nsjail + independent
cgroup supervisor) is the only retained lightweight process-level design, **not
proven present, lightweight to provision here, or runnable**. It is a conditional
future option only if existing host facilities and already-available dependencies
meet the contract without large installations or added fees. Otherwise leave the
TODO unresolved; never trade away isolation to keep work moving. No further search,
native launch or dependency provisioning is proposed now. No third candidate.

The coordinator owns any separate development/qualification staging adjustment;
this report does not change DAG/AGENTS/main APIs, mark missing qualification PASS,
or make its deferred work a new main-development gate. B04 freeze stays intact.

Controlling local evidence:

- Reviewed parent `413120bdc321d1dba32edca4325aa17eb95a2490`, integrated as
  `0f20803188e762a11fe005e2738b1eb0dc7e6b29`, is already in this clean task's
  starting history. Both [AGENTS.md](../../../AGENTS.md) files were read; source
  is `ai/migration-bootstrap-20260911`. No integration by this author.
- [Member plan](b01-member-admission-plan.md), sections 4–7, supplies the retained
  reader trace, proposed ceilings and separate inspection/admission/CI/distribution
  authorities. Its section 6 is historical known-facility assessment, not this
  new solution research. We do not change its text or reinterpret plan PASS as
  permission to execute.
- [O1 policy](b01-replay-policy.md), normative evidence classes and acquired
  equivalence, and [O1 rights assessment](b01-o1-rights-review.md), container/member
  distinctions, remain controlling. [O1 JSON](b01-o1-rights-review.json) is an
  assessment, not an accepted manifest.
- [B01-Q](b01-quarantine-acquisition.md) and committed
  [resume.json](../../../.github/tests/migration/b01-quarantine/resume.json)
  identify exactly seven parts in DRF-OLD/DRF-SOLID/DRF-VOL, reviewed total
  423725 bytes. These are inherited measurements, not new opaque reads.
- Actual B04 comment135 was read: freeze, no additional diagnostics or native
  budget. Preserve `b1719b6d8a3b169edd696084c58921f228f41451`; no B04 code/report
  was changed or executed. B01 remains `triage`, `import_approved=false`,
  `qualified=false`; B04 `blocked`, **native budget 0**. B03 and every downstream
  gate are unchanged. Full inherited default Telegram `notify+wake` subscription
  was verified read-only without emitting route identities.

The original research authority and subsequent narrowing do not change the
freeze. No sandbox/guest/tool install, build or launch, archive
Open/list/test/extract, fixture/image/binary download, native CI, push, service
registration, correspondence, credential access, security-policy change or fee
occurred. Public documentation retrieval and offline document checks are not
native validation. The eventual Linux-only private inspection must not acquire
Windows/macOS private runners from B03 by implication; equally it cannot satisfy
O1's later three-platform replay, B03, B04, GUI, or desktop-integration obligations.

## 2. Evidence method, versions, availability and cost/license matrix

[Companion source ledger](b01-containment-solutions-research.sources.json) records
exact requested/final URLs, UTC retrieval times, fetched-text byte lengths and
SHA-256, version scopes, literal excerpts and source-line ranges. Sources 1–13 are
version-tagged first-party text/source; 14–15 are live GitHub policy pages.
Tags are named source identifiers, **not an assertion that tags cannot move**;
retained text digests detect changed evidence. No executable/image digest was
measured. These deliberately bounded reference versions are not asserted latest,
patched, installed, or approved for hostile input. Execution preparation must
select an available security-maintained package, review its release/security
changes against these cited semantics, record its full source/dependency and
binary identities, and stop on material drift. A version label is not a CVE audit.
The live QEMU master pages were also read during discovery; conclusions and
numbered claims below use the fetched v10.0.0 sources, not mixed-version options.

| Component / candidate | Exact researched basis and cost evidence | License, separate rights and unmet conditions |
| --- | --- | --- |
| V: QEMU system emulator — excluded, not a fallback | Already-fetched `qemu/qemu` `v10.0.0` source supports CPU-emulated TCG without KVM, but expressly disclaims TCG guest isolation.[1][2] | Latest user restriction excludes new VM/guest stacks regardless of fee. GPL-v2 emulator, separately licensed firmware; TCG parts have mixed licenses.[4] No installation/image work retained. |
| P: nsjail | `google/nsjail` tag `3.4`, README/config.proto/cgroup2.cc/subproc.cc/LICENSE. Linux process isolation using namespaces, rlimits, seccomp; Apache grant says no-charge and royalty-free.[5][9] | Apache-2.0 notice/change/redistribution conditions apply; dependency licenses (including kafel, protobuf, libnl, runtime libraries) require the selected build's inventory. Not an official Google product or a commercial safety warranty. Source availability does not establish runnable host permissions. |
| Guest/image construction — excluded | Already-fetched Buildroot `2025.02` legal/COPYING text describes GPL build tooling, separately licensed outputs and incomplete `legal-info` coverage.[12][13] | Not a recommendation to build/install an image or new toolchain. No image was selected/downloaded and no image license closure is claimed. P must use a minimal allowlist of existing pinned runtime files, not introduce Buildroot. |
| Existing host kernel/runtime for P | Linux `v6.12` is only the researched cgroup/API reference; kernel COPYING identifies GPL-2.0 WITH Linux-syscall-note.[10][11] | No new kernel installation. Actual host configuration, maintained package, runtime/dependency versions and notices remain unverified. If existing facilities cannot satisfy P, defer rather than install a large replacement stack. |
| Retained C/C++ observer/reader | Repository base `0f20803188e762a11fe005e2738b1eb0dc7e6b29`; [License.txt](../../../DOC/License.txt):8–30 and [unRarLicense.txt](../../../DOC/unRarLicense.txt):13–19. Existing RAR decoding free of charge, no writer license procurement. | LGPL-2.1-or-later plus unRAR restriction for Rar decoder files; preserve source/notices and applicable relinking/source requirements if distributing a linked observer. No codec rewrite, compressor reconstruction or commercial writer. New test-only observer itself is not implemented; its license/build review remains required. |
| Original parts and eventual member reports | O1's affirmative Debian `python-rarfile` `4.5-1` ISC path assignment and Q's seven fixed identities, not software/image licenses above. | Preserve the three full existing notices. Actual member/name/metadata/source applicability still unknown. Private bounded inspection, formal admission, CI transfer and redistribution are distinct decisions. No public member logs or accepted hashes are licensed by this research. |
| Existing GitHub standard hosted Linux, deferred context only | Current billing text says public repositories using **standard** GitHub-hosted runners are free; private-repository overages are billed.[14] Published public Linux x64 standard configuration includes 4 CPUs, 16 GB RAM, 14 GB SSD, `ubuntu-24.04`.[15] | Not a recommendation to acquire a VM or dispatch now. Policy is conditional on current repository eligibility; usable cgroups/namespaces, installed dependencies and private evidence storage remain unproven. No larger runner/trial/paid storage, new service or credential setup. It may only be reconsidered as an existing environment under later explicit low-priority authority. |

GPL/Apache source grants make software fee-free use possible; they do not pay
for hardware, power, bandwidth, storage, or authorize use of somebody else's
machine. The existing hosted standard-Linux route is the concrete conditional
compute option, not a newly assumed private host. This report authorizes neither
that dispatch nor local workstation execution. A private local run would require
its own explicitly identified existing host/owner authority and operational cost
assessment; it is not the default fallback.

## 3. Common trusted protocol and retained reader boundary

The following is the **deferred implementation contract** for candidate P,
not claims that upstream tools already implement it. Plan section 4 remains the
source-backed reason a narrower CLI is insufficient: `IInArchive::Open` parses,
`Extract` decodes, property enumeration may omit data, and allocations precede
output callbacks. Use the retained RAR handlers with a small test-only observer,
not `7z l -slt`, `x -so`, a commercial writer, rarfile backend or member shell-open.

1. Trusted custodian fixes family/part table from committed Q metadata. On a later
   authorized run it opens no-follow regular-file handles, checks exact byte length
   and SHA-256, and creates immutable private transfer backing before exposing any
   handle. Read-only mounts alone do not prevent another host writer changing a
   backing file. Require separate custodian ownership, inaccessible original
   directory, no writable alias/handle in the child and checked before/after
   identities. Originals, notices and Q attempt evidence are never renamed/deleted.
   Logical next-volume strings map only to at most three preopened part handles;
   unknown requests stop. No path derived from a member/volume request reaches the
   host filesystem. Transfer backing creation is not authorized on this card.
2. Single retained-reader operation at a time, pinned objects/compiler/flags and
   dependencies, only selected RAR handlers/decoders; prove `Z7_EXTERNAL_CODECS`
   discovery absent. No plugins, prompts, passwords, helper exec, automatic format
   fallback or nested archive recursion. Pin raw behavior, not a name like `7zz`.
   Before the first `Open`, independent limits and final syscall restrictions must
   already be active. All parser, callback and hash code is one untrusted process.
3. Observer enumerates source indices and typed property IDs/definedness before
   accepting completion, copies `PROPVARIANT` values, retains COM references until
   last engine use, uses no concurrent archive calls, and propagates failures.
   Every decoded logical item uses a per-index streaming SHA-256/length sink;
   service/solid/link dependency work is accounted explicitly. No member file,
   link, directory, xattr or alternate stream is created. Missing raw name/link
   representation or unaccountable internal work is incomplete evidence, never
   filled from expected dumps. Hashes are not rights/content review.
4. Proposed wire format: fixed 16-byte header (ASCII `B01I`, u16 version 1, u16
   record kind, u32 source index, u32 body length, integers little-endian). A run
   header binds a parent-selected run ID, reader/config/input-set digests; indexed
   records carry bounded typed metadata followed by full digest/decoded-length
   results and explicit numeric engine outcomes; one final count/status record.
   Use length-delimited bytes for names, no implicit NUL termination/Unicode
   normalization. Define kind/body field schemas in the later test-only protocol
   file before coding producer/consumer; reject unknown fields/kinds/versions.
   No arbitrary JSON nesting, duplicate keys, executable previews or filenames as
   evidence paths. Bounds apply before allocation and before each output chunk.
5. Trusted outside validator treats **every output byte as hostile**, not merely
   names. It caps individual frame/body and aggregate output, checks ordering,
   duplicate/missing indices, overflow, definedness, family identity, digest shape,
   final record and end-of-stream. It separately records actual input hashes,
   launch identity, cgroup statistics, exit/signal/timeout and collection outcome;
   never trusts child-supplied PASS/resource/cleanup claims. A compromised parser
   can forge perfectly well-framed hashes/member reports, including the run ID:
   framing is not authentication or truth. Such reports stay provisional and need
   independent consistency/rights/native review; containment cannot prove semantic
   correctness against a fully compromised reader. Do not put a signing key in it.
6. Only bounded pipes/serial byte channels cross back. Supervisor preallocates a
   bounded private collector, drains without a terminal, never interprets ANSI,
   workflow commands, HTML or scripts; public diagnostics contain only fixed
   trusted enums and canary outcomes. Raw stderr is capped separately within the
   evidence budget. No child-created filesystem is mounted on the host to collect
   results. After all tasks are quiescent, trusted fixed-name output may be retained
   under separately authorized private custody; cleanup only known disposable
   backing, no recursive following of guest paths. If quiescence fails, do not
   collect/delete uncertain output, reuse the environment or start another family.

## 4. Candidate V: excluded large-dependency route (retained rationale only)

The later user restriction excludes QEMU, Linux guest installation, image-building
and new virtualization stacks. This supersedes the original guest-first request;
no V implementation, installation instructions, validation budget or KVM fallback
is retained. Previously fetched sources remain auditable, not recommended work.

TCG emulates CPUs without KVM.[2] The security objection is not hardware absence:
QEMU v10.0.0 security.rst:48–50 says users of the non-virtualization use case must
not rely on guest isolation/security guarantees.[1] Read-only disks and no-network
device options do not cure that disclaimer or contain host emulator compromise.[3]
Even a supported virtualizer can have guest-to-host device vulnerabilities; it
requires least privilege and external resource/confinement supervision.[1] No
performance or resource-enforcement measurement was made, and no slowdown estimate
or perfect-security claim is warranted. Firmware/image license closure is separate
from the emulator's license.[4][12] These findings justify exclusion, not more work.

## 5. Candidate P: nsjail plus an independent Linux supervisor

### Exact platform and source trace

Research target is Linux x64 with namespaces, seccomp-BPF and cgroup v2 CPU,
memory and pids controllers. Kernel v6.12 docs define the researched interfaces;
not every host with that version enables/delegates them.[10] nsjail 3.4 exposes
ONCE vs EXECVE-without-supervisor, mount/network/user/PID namespaces, mandatory
mounts, pass_fd, no-new-privileges, limits and loopback control.[6] Its namespace
notes include cgroup namespaces requiring kernel 4.6 and optional time namespaces
5.3; this proposal does not enable time namespaces or claim those numbers alone
are sufficient for all cgroup.kill/delegation behavior.[6]

Source findings materially beyond a generic sandbox feature list:

- `cgroup2.cc`:212–271 writes memory.max/memory.swap.max, pids.max and cpu.max;
  the CPU setting is milliseconds **per second**, not lifetime CPU budget.[7]
- `subproc.cc`:185–199 waits for a parent synchronization byte before containment;
  `initParent`:420–444 sets cgroup/user state before releasing it, then
  `newProc`:216–233 installs seccomp and execs the target.[8] This provides an
  implementation point before parser execution, not proof the configuration works.
- `cgroup2.cc`:94–112 may try controller setup, retry after moving itself on
  EBUSY, and its failure diagnostic says root/host cgroup access is required.[7]
  Do **not** market default invocation as rootless/delegation-guaranteed. The
  proposed wrapper must preflight an already authorized dedicated cgroup subtree
  with controllers enabled; constrain nsjail to it and disallow unexpected
  hierarchy modification/fallback. If unavailable, fail before launching, not
  remount cgroups, disable namespaces, use privileged Docker, or alter LSM policy.
- Native time enforcement in `reapProc`:386–404 uses time(NULL), SIGCONT/SIGKILL
  for tracked PIDs; `killAndReapAll` iterates its tracked map.[8] These are not our
  independent monotonic deadline or full descendant-quiescence proof. Add an
  outside supervisor with separately owned cgroup.kill/events and bounded drain.
- Seccomp is installed before the initial exec.[8] Therefore a policy denying
  every execve would prevent launch. A reviewed static test-only observer must
  install a second irreversible restriction denying execve/execveat and all
  fork/vfork/clone/clone3 before it acknowledges READY or calls `Open`; startup
  policy permits only the pinned initial image, with no other executable files.
  The second filter is a prerequisite, not assumed provided by nsjail defaults.

### Full envelope proposal

Reuse section 3's fixed-handle transfer/protocol. Minimal immutable root contains
only pinned observer/runtime files; no host `/`, `/home`, `/proc` by default,
workspace, credential, cgroup-control or supervisor mount. Explicitly mandatory
read-only/noexec input bindings and limited writable tmpfs with nodev/nosuid/noexec;
no parser access to original directory entries, writable aliases or canary files.
No external tool or member materialization. Exact numeric volume table and
allowlisted descriptors replace normal filesystem Open callbacks.

Use ONCE, serial invocation, fresh user/mount/PID/IPC/UTS/net namespaces, dropped
capabilities, no-new-privileges, `iface_no_lo=true`, no moved/macvlan interfaces,
no network sockets in final syscall filter, empty allowlisted environment and
closed inherited FDs except input/output protocol handles. These are choices
supported by configuration fields, **not safe defaults inferred from examples**.[6]
The README's interactive shell/host-root/privileged-container examples are not
an accepted template.[5] Child cannot signal/ptrace supervisor, setns/unshare,
mount, access devices, bpf, change cgroups, regain privileges or execute another
image. Startup/final syscall lists must be derived from the exact harmless
observer/runtime, reviewed for alternate syscalls/ABIs, and fail closed; no
“allow all until it runs” adaptation.

Independent parent retains domain-cgroup handles outside the sandbox, prepares
limits before nsjail releases the child, checks child startup proof from trusted
OS observations and enforces 30-second monotonic wall limit including launch.
Use memory.max=256 MiB, memory.swap.max=0, pids.max=1 in the final parser group,
one CPU affinity and hard process CPU limit 10 seconds (soft must not exceed
hard), no process/thread creation after READY. There is no trusted running
parser child outside the bounded group. The launcher/supervisor have separate
bounded groups and cannot be killed or starved through parser budget exhaustion.
Hard CPU behavior requires both rlimit hard/soft readback and actual control
verification; `rlimit_as` alone is not aggregate resident memory.[6][10]
Kernel memory.max can temporarily overshoot; do not promise a mathematically
absolute 256 MiB host-footprint ceiling. Reserve host headroom and record peak,
OOM/event outcomes; overshoot beyond the independently agreed tolerance fails.[10]

pids.max counts tasks/threads, not just processes; migration can exceed the number
but fork/clone are denied at the limit.[10] Precreate only the trusted launcher
outside the parser group, admit the one parser, then prohibit subsequent migration
into/out of it. If the single-threaded build cannot start within one task, stop
for review rather than lift the limit; no decoder plugin/helper exception. CPU
bandwidth is a supplementary rate limit, not the 10-second lifetime enforcement.

8 MiB size-bounded private tmpfs is the only scratch; additionally bound inodes
and file descriptors, core dumps disabled. RLIMIT_FSIZE is per-file, not total
disk or pipe-output control. The trusted collector separately caps all encoded
output at 1 MiB per family. On any unexpected behavior the supervisor issues
cgroup.kill, waits at most 5 seconds for cgroup.events populated=0 and reap/EOF,
then follows section 3 collection rules. No cgroup deletion or direct PID exit is
used as a substitute for quiescence. Injected cleanup failure leaves the run
failed and storage quarantined, never “best-effort successful cleanup”.[10]

### Feasibility and residual risk

P is less image/device code and no hardware virtualization dependency, with
specific upstream setup/exec boundaries that a coder can target.[5][8] It still
shares the host Linux kernel. Kernel/namespace/seccomp bugs or a flawed allowlist
can compromise the host; trusted supervisor/validator bugs can defeat collection.
Neither success on a different local host nor B04's failed launcher proves P
works here. Published passwordless sudo on hosted Linux is administrative
capability, **not this task's authority to use it or proof namespaces work**.[15]
No sandbox invocation is recommended without the prerequisites and controls below.

## 6. Which plan limits may change, and which obligations may not

Plan section 5 explicitly labels all numerical ceilings proposals, not measured
limits or current budgets. O1 policy mandates complete identities, rights,
reader/native evidence and preserved compatibility, not those numerical values.
The distinction permits an explicit reviewed envelope adjustment; it does not
permit quietly ignoring a cap during a failed run.

| Existing proposal | Origin and disposition |
| --- | --- |
| Seven fixed inputs, maximum three handles per family, 423725 bytes | Fixed Q authority/identity, not tunable workload. Keep all seven identities/notices; no expansion/reacquisition, no original renaming or omission. |
| 16 entries, 4096-byte names/targets, 64 KiB metadata, 1 MiB/member, 4 MiB aggregate | Plan's proposed rejection budgets. Retain for first observer design; count all observable dependency work, never silently truncate. O1 requires complete accepted identity, not these sizes. If insufficient, stop with incomplete inventory and seek an exact reviewed adjustment before another authorization, not automatic growth. |
| 256 MiB, 10 CPU seconds, 30 wall seconds | Proposed parser-domain caps, retained for P. Applying the same cap to trusted supervisor/build resources is unnecessarily implementation-specific; account and bound them separately, not inside the parser domain. Temporary kernel accounting overshoot and CPU-time enforcement granularity require an explicit acceptance tolerance, not a false absolute claim.[10] No adjustment effective here. |
| One process, bounded threads, no fork/exec | Keep one final parser task for P, separate from its trusted launcher/supervisor. pids.max counts TIDs.[10] Distinguish launch-time initial exec from forbidden post-READY exec; an unconditional pre-launch exec denial would prevent the intended executable from starting.[8] No permission to introduce an unbounded helper tree. |
| Zero writable host mounts, 8 MiB scratch, 1 MiB evidence | Preserve no member materialization and no child-writable trusted host surfaces. Distinguish existing immutable tools from runtime scratch. A one-way bounded pipe is not an illicit writable host mount. Avoid shared-folder output collection; permissions for private derived evidence remain separate. |
| 5-second quiescence; serial/no retry; stop on unknown metadata/rights, format/password, drift or breach | Keep conservative operational stop. Killing may fail/delay under kernel faults; report that honestly and stop, never extend/reuse automatically. Safety cannot be inferred from an empty direct-child list. |
| Pinned retained engine/no plugin, independent supervisor, network/credentials excluded; O1 rights and full native qualification | Non-negotiable trust/rights/compatibility obligations inherited from AGENTS/O1/plan, not arbitrary performance knobs. A Linux provisional inventory changes none of them. Historical writer unknown remains allowed only as O1 defines; actual members/reader/native acceptance may not become null accepted placeholders. |

## 7. Finite implementation handoff and options (nothing dispatched)

### Low-priority TODO: P only if existing facilities suffice

No follow-up research/validation card is requested or created. Stop this task at
independent review using already retrieved evidence. The following finite contract
is retained solely to avoid rediscovery if the coordinator later schedules this
low-priority TODO under explicit authority. It is not a request to delay main
development, change B04, install dependencies or run anything now.

Exact unmet prerequisites and owners:

1. Coordinator: identify an explicitly permitted existing Linux environment and
   visibility/retention scope with zero added fees; no new machine/service/private
   runner or large installation. Current native budget is still 0. Host ownership,
   permissions and private evidence collection are unproven, so leave this TODO
   unresolved unless supplied by an independently authorized later activity.
2. Coder: if nsjail and its maintained kernel/runtime/build prerequisites already
   exist, pin sources/build/binary hashes, dependency license/notices, build config,
   syscall policy and the allowlist of existing root files. nsjail 3.4 is a source
   reference, not an unchecked package mandate. Availability/size of this exact
   dependency set was not measured; do not claim installation is lightweight.
   Missing facilities mean defer, not Buildroot/new VM/new kernel/toolchain.
   Dedicated cgroup controllers and namespaces/seccomp must already be permitted;
   no host/global policy relaxation to manufacture feasibility.
3. Coder: implement only supervisor + bounded validator + synthetic no-archive
   probe executable. Resolve startup-to-final seccomp transition, cgroup ownership,
   hard CPU limit/timer semantics, output frame schema, separate supervisor caps,
   no-follow collection, and fail-closed process-tree shutdown. Do not compile or
   invoke retained archive parsers for this validation. Fake probes must be clearly
   labeled synthetic, not manufactured compatibility evidence.
4. Tester/reviewer: examine exact code/config/license artifacts and run approved
   controls once. Preflight failures stop before probes. Source claims and mock
   results do not establish native containment. Only after native controls PASS
   can a **different** exact observer implementation plus private seven-input
   inspection permission be considered. Member rights/admission remain later.

Retained finite **future TODO** validation ceiling (not a dispatch recommendation
or current authorization): one existing Linux x64 environment, 15-minute total
wall ceiling including bounded harness compilation/preflight with existing tools,
no automatic rerun, maximum 12 synthetic probe invocations, serial; each at most
30 seconds plus 5 seconds quiescence, 256 MiB parser group, one final task,
10 CPU seconds, 8 MiB scratch, 1 MiB output. Launcher/supervisor proposal:
128 MiB, 8 tasks, bounded drains and independent monotonic watchdog. No dependency
installation/build campaign in this TODO; existing-tool harness compilation must
fit 512 MiB memory, 8 tasks and 64 MiB disposable workspace or stop. These are
ceilings, not measured feasibility or permission; no automatic increase, paid
fallback, large dependency substitution or fixture exposure.

Preflight may read only system capability/config and self-owned test data; it
must check cgroup domain/control/kill ownership and namespace/seccomp enforcement
without remounting or changing global security settings. Actual host build/CPU
availability and legal inventory are acceptance prerequisites. If a necessary
preflight action needs unavailable authority, return that exact issue, not a
weakened isolation profile.

| Probe invocation | Required harmless outcome / evidence |
| --- | --- |
| 1 | Known fixed byte buffer emits valid framed digest/metadata; trusted validator and clean exit/quiescence pass. No archive format or parser. |
| 2 | Attempt input write/rename/substitute and out-of-set volume token; denial, unchanged custodian digest and identity. |
| 3 | Traversal/link/device/control-path attempts against synthetic tree; no access, no host materialization, no-follow collector behavior. |
| 4 | AF_INET/AF_INET6/AF_UNIX socket/DNS/loopback attempts with self-owned endpoints only; exact denied syscall outcome, not merely unreachable network. |
| 5 | Self-owned fake credential/env/FD/agent-socket canaries; child cannot obtain them or signal/ptrace parent. Never real credentials. |
| 6 | Fork/exec/namespace escape attempts denied after READY. Separate trusted pre-parser helper variant within this invocation verifies killing a harmless reparented descendant under the supervisor group; it is not the final parser policy and must be labeled separately. |
| 7 | Thread creation attempt denied by final filter/pids ceiling; retained task accounting never treated as process-only. |
| 8 | Memory pressure from bounded synthetic allocator triggers enforced failure without starving parent; record current/peak/events and agreed overshoot tolerance. |
| 9 | CPU spin reaches independently enforced hard CPU outcome, not just cpu.max throttling; record hard/soft limits and trusted CPU/wall samples. |
| 10 | Fill private scratch/inodes with synthetic bytes; enforced full condition, no host disk growth beyond separately bounded workspace. |
| 11 | Oversized/late output from synthetic emitter; bounded drain terminates and no raw stream reaches terminal/public log. |
| 12 | Hang with forced supervisor termination and simulated cleanup uncertainty; deadline/whole group empty proof or explicit failed quarantine, never false success. |

Expected resource kills/denials are PASS only for their named controls. The first
unexpected outcome, drift, missing denial proof, malformed collection, supervisor
starvation or unproved quiescence stops the entire job; no reruns. Host loss during
cleanup is a failed experiment even if no output remains. These controls exercise
specific invariants, not an exhaustive exploit or kernel-fuzzing campaign.

Before any native probes, offline validator controls must reject malformed,
truncated, oversized, forged-PASS, duplicate/out-of-order/missing-index, wrong-run,
wrong-input and trailing frames while the unchanged synthetic record passes.
A well-formed false hash cannot generally be identified without independent
expected bytes: demonstrate that limitation rather than claim authenticity.

Required evidence artifacts, in the eventual authorized card's private evidence
root: source/dependency/license manifest and notices; executable/root/config
SHA-256; exact argv/environment allowlist and platform/package metadata; immutable
synthetic input manifest; preflight ownership/control readbacks; per-probe trusted
OS observations and bounded sanitized raw results; cgroup memory/pids/CPU events,
monotonic timing/kill/reap/EOF record; collector negative controls; fixed-name
cleanup inventory; summary with every expected denial matched to observation.
Public hosted logs may contain only approved synthetic diagnostics. No acquired
member data, tokens or private route identity. An artifact path without a tested
private retention/collection route is not a completed handoff.

### Actionable operator options and impacts

1. **Recommended now: review and retain this auxiliary handoff; prioritize main
   development.** Keep containment/native verification as a low-priority TODO,
   with no new research/validation cards or large dependencies. No new execution,
   fees or disclosure exposure; unresolved qualification is recorded honestly.
   Coordinator handles development/qualification staging separately, not this card.
2. **Later only: reuse P on an already suitable environment under explicit
   bounded authority.** The contract above is concrete enough to scope a small
   supervisor/validator effort without restarting research. It is conditional on
   existing facilities, license/zero-cost proof and independent controls; otherwise
   remain deferred. No VM/new virtualization stack, installation campaign, lowered
   safety standard, automatic opaque inspection or B04 thaw.

No claim that all free solutions are impossible. The finite result is a deferred
lightweight design with explicit unmet prerequisites and exclusion of the large
dependency route. There is **no currently verified usable envelope** in this
report. Research completion is neither containment PASS nor a new main-development
prerequisite; do not open qualification gates or invent human approval.

## 8. Verification, limitations and review handoff

Only this report and same-stem `.sources.json` are tracked deliverables. Temporary
text/metadata retrieval and check scripts live in ignored
`.github/tests/migration/b01-quarantine/__pycache__/`; no opaque path is opened.
All substantive upstream capability/license/cost statements above point to fetched
first-party text; proposals are explicitly distinguished from observed features.
Exact excerpts with source ranges/digests are in the ledger; sources below are
rendered mechanically. No production builds are applicable: this card changes no
executable code, and tool/guest/native/archive execution is prohibited. No runtime,
compatibility, vulnerability-completeness, legal-warranty or three-platform PASS.

Executed documentation checks (all exit 0):

```text
python3 .github/tests/migration/b01-quarantine/__pycache__/research_sources.py
python3 .github/tests/migration/b01-quarantine/__pycache__/research_evidence.py
python3 .github/tests/migration/b01-quarantine/__pycache__/research_quotes.py
python3 /home/ding/.hermes/profiles/architect/skills/research/grounded-citations/scripts/sources.py --ledger docs/ai-migration/qualification/b01-containment-solutions-research.sources.json render --replace-in docs/ai-migration/qualification/b01-containment-solutions-research.md
python3 /home/ding/.hermes/profiles/architect/skills/research/grounded-citations/scripts/sources.py --ledger docs/ai-migration/qualification/b01-containment-solutions-research.sources.json verify docs/ai-migration/qualification/b01-containment-solutions-research.md --strict --evidence
python3 .github/tests/migration/b01-quarantine/__pycache__/check_containment_research.py
python3 docs/ai-migration/validate-migration-dag.py
python3 -m json.tool docs/ai-migration/qualification/b01-containment-solutions-research.sources.json /dev/null
git diff --cached --check
```

Results: 15 fetched source digests/lengths, 49 literal excerpts and evidence range
bounds passed; 10 relative links passed; seven inherited identities and 423725
bytes matched the reviewed plan using committed metadata only. Branch, parent
ancestry, unchanged AGENTS/dev-main, report-only scope, full route inheritance,
B01/B04 statuses and latest user scope readback passed. DAG: 29 children, 104 child
edges, acyclic with complete prerequisites and 3 negative controls PASS. Citation
verification passed all 15 source IDs with evidence; its sentence-coverage statistic
is not substantive review (most prose here specifies a proposal/local authority).
No new retrieval occurred after scope narrowing.

Operational limitations: execute_code and a Python `-c` metadata probe were denied
before execution; explicit harmless file-based scripts were used instead without
changing approval settings. An initial read-only environment-selected database
had no relevant tables; the exact named board database was then resolved and
read-only inheritance/status checks passed. No board/database writes by scripts.
One ambiguous temporary-script patch was rejected without edits and fixed using
unique context. These are document-tool issues, not native candidate diagnostics.
Full commit SHA and absolute artifact paths accompany the review transition.

Review must independently challenge feasibility, resource/termination assumptions,
image/dependency license gaps, zero-cost conditions, TCG policy implications and
forged-report limitations, not merely click links. Request `reviewer`; CHANGES
returns the same card to architect; two substantive failures require a typed
`needs_input` block with evidence/options/impacts. PASS completes **only research**;
reviewer may serially integrate on a clean automation base and post/read back
commit/path/limitations to B01 `t_22299c6f`. Author never merges shared branches,
pushes, releases, creates implementation cards, or completes this card directly.

## Sources

[1] https://raw.githubusercontent.com/qemu/qemu/v10.0.0/docs/system/security.rst — qemu-security
[2] https://raw.githubusercontent.com/qemu/qemu/v10.0.0/docs/system/introduction.rst — qemu-intro
[3] https://raw.githubusercontent.com/qemu/qemu/v10.0.0/qemu-options.hx — qemu-options
[4] https://raw.githubusercontent.com/qemu/qemu/v10.0.0/LICENSE — qemu-license
[5] https://raw.githubusercontent.com/google/nsjail/3.4/README.md — nsjail-readme
[6] https://raw.githubusercontent.com/google/nsjail/3.4/config.proto — nsjail-config
[7] https://raw.githubusercontent.com/google/nsjail/3.4/cgroup2.cc — nsjail-cgroup
[8] https://raw.githubusercontent.com/google/nsjail/3.4/subproc.cc — nsjail-subproc
[9] https://raw.githubusercontent.com/google/nsjail/3.4/LICENSE — nsjail-license
[10] https://raw.githubusercontent.com/torvalds/linux/v6.12/Documentation/admin-guide/cgroup-v2.rst — linux-cgroup
[11] https://raw.githubusercontent.com/torvalds/linux/v6.12/COPYING — linux-license
[12] https://raw.githubusercontent.com/buildroot/buildroot/2025.02/docs/manual/legal-notice.adoc — buildroot-legal
[13] https://raw.githubusercontent.com/buildroot/buildroot/2025.02/COPYING — buildroot-license
[14] https://docs.github.com/en/billing/concepts/product-billing/github-actions — github-cost
[15] https://docs.github.com/en/actions/reference/runners/github-hosted-runners — github-runners
