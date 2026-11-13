# M3-D2: second development-slice determination

Task `t_56c636a8`, branch `wt/t_56c636a8`. Status: negative determination
submitted for independent review. This is a finite scheduling result, not an
implementation authority or native qualification.

## Decision

**No second immediately actionable DEVELOPMENT slice exists in the remaining
mainline.** Do not create another coder card from this determination.

The completed and independently reviewed S2a-DEV slice exhausted the part of the
current production spine whose deferred parents were evidence-only. Every
remaining candidate either:

1. needs a semantic, ownership, safety, or licensing input from an unfinished
   parent;
2. is itself the native characterization/qualification work being deferred;
3. needs an earlier implementation, rather than merely evidence confirming an
   already reviewed contract; or
4. is on the GUI/desktop/release path, where stage ordering or the explicit
   release-path prohibition prevents a DEVELOPMENT split.

This result removes no edge and changes no live card. S2a `t_071e4cd7` retains
all eight original parents plus S2a-DEV `t_178b131f`. B01, B03, B04, B05, B06,
B07, B08 and all native obligations remain open. `qualified_operations` remains
zero and no operation becomes reachable from `archive-cli` or another product
caller.

## Authority and inspected state

The controlling test is unchanged from
[development-first-sequencing.md](development-first-sequencing.md), section 2,
and [ADR-0004](adr/0004-development-first-sequencing.md), Decision: a parent can
be omitted only when it would merely confirm implementation against an existing
reviewed contract. A parent that supplies a semantic, ownership, safety, licensing
or earlier-implementation input is input-bearing and stays in force. A split
must be a strict subset of the source card; it cannot replace real execution with
a mock or reorder the migration.

Before this determination:

- Both repository and worktree `AGENTS.md` were read. The source checkout was
  clean on `ai/migration-bootstrap-20260911`; the task worktree contained
  `AGENTS.md` and was clean on `wt/t_56c636a8` at
  `bc61a7b2aabc855e1d7559005cea1cf43ea0a2df`.
- Reviewed M3 `0706af3d714e8c2701691a19a0c663ae7b749c88`, Q1
  `5f07f21a6516e345db199d3d78a3a984118574a5`, S1
  `e809c92b2d493412882f8a623f05fbe2ee508ff2`, and S2a-DEV
  `bc61a7b2aabc855e1d7559005cea1cf43ea0a2df` were verified as ancestors.
- S2a-DEV reviewer run 93 was read, including its execution-lens PASS and
  residual risks. It independently rebuilt the retained-engine facade, ran all
  20 required checks, and approved only single-host DEVELOPMENT acceptance.
  Its remaining risks include the GNU/Itanium-only registration wrapper,
  unsolved fail-closed MSVC path, absence of ASan/UBSan/TSan and dead-strip
  qualification, and a non-canonical local toolchain. It opened no archive and
  left `qualified_operations=0`.
- The live body and complete comment thread were read for S2a. Live bodies and
  comment counts were read for every remaining M3 mainline card. Relevant live
  comments were read in full for B01, B03, B04, B05 and B06. In particular:
  B01 remains `triage`, `import_approved=false`, `qualified=false`; B03 comment
  167 is conditional on infrastructure that is not present; B04 comment 135
  freezes the card with zero native budget; and the reviewed B05/B06 preparation
  report recommends no additional preparation split.
- The later B05-MAN `t_5839f819` and B07-MAN `t_184bb07d` cards were also checked.
  Both are blocked evidence-preparation lanes. Neither is a reviewed native
  campaign result, a production slice, or authority to close B05/B07.

The existing operator decision to defer real-machine work is not being asked
again. Personal-machine manual execution authorization does not convert an
unexecuted runbook into semantic input, and does not change DEVELOPMENT into
QUALIFIED/RELEASE acceptance.

## S2a remainder: every operational part is input-bearing

S2a-DEV implemented and reviewed only `archive_bridge_v1_handshake`,
`archive_bridge_v1_create_context`, `archive_bridge_v1_destroy_context`,
`archive_bridge_v1_capabilities`, and `archive_bridge_v1_result_destroy`.
The remaining frozen revision-1 operations are `open`, `entries`, and `close`,
plus the minimal operation callback/cancellation adapters. They cannot be split
again safely.

### B01 supplies open, chain, and diagnostic semantics

Q1 fixes the transport layout, not the legal runtime observations. Its Open and
paging contract requires ordered chain records, `CArcErrorInfo`, non-open errors,
properties, volume behavior, and contextual handling of `S_FALSE`; see
[abi-v1.md](qualification/abi-v1.md), “Handshake, initialization and errors” and
“Open and paging”. The retained source has materially distinct error fields and
definedness in `CPP/7zip/UI/Common/OpenArchive.h:149-225`, and `Open_Strict`
changes a nominal `S_OK` to `S_FALSE` when a nested non-open error exists at
`OpenArchive.h:424-440`.

Those legal combinations are corpus facts, not choices a bridge author can derive
from the struct layout. The reviewed sequencing decision already classifies B01
as input-bearing for archive open, paged entries, and listing. Live B01 still has
only partial capability/corpus coverage and no formally admitted external corpus;
its recent acquisition work explicitly leaves `import_approved=false` and
`qualified=false`. Restricting a new slice to a guessed extension, one convenient
fixture, or the eight already covered format rows would silently narrow S2a rather
than implement a reviewed subset.

### B03 supplies stream and failure-cleanup semantics

Opening is real I/O. `COpenOptions` carries `IInStream`,
`ISequentialInStream`, callbacks, and a native file path
(`CPP/7zip/UI/Common/OpenArchive.h:117-145`). `CArchiveLink::Open` calls
`CArc::OpenStreamOrFile` for the initial input
(`OpenArchive.cpp:3279-3297`). Probing repeatedly seeks and reads the same stream
and treats a zero processed count as EOF (`OpenArchive.cpp:2487-2507`). The
retained `IInStream::Seek` contract permits seeking past EOF and leaves
`newPosition` undefined on failure (`CPP/7zip/IStream.h:88-100`).

Therefore short reads, seek failures, EOF, large offsets and cleanup after a
failed open determine the adapter and session contract. They are not just later
platform confirmation. B03 remains input-bearing exactly as
`development-first-sequencing.md` section 2 states. Its conditional native
permission in live comment 167 cannot run until independently verified runner,
lease, ledger, protection and preservation prerequisites exist. The later
personal-machine permission does not resolve those semantics and explicitly
requires safe bounded designs for resource-exhaustion cases.

### B05 supplies interaction and encrypted-open semantics

The ABI correctly distinguishes unavailable, cancel, undefined password,
defined-empty password, and supplied password replies
(`archive_bridge_v1.h:190-235`; `abi-v1.md`, “Callback and allocation lifetime”).
That declaration does not establish which retained handler requests which state,
or the resulting outer/item status.

`COpenCallbackImp::CryptoGetTextPassword` returns `E_NOTIMPL` without a provider
and otherwise forwards the password request
(`CPP/7zip/UI/Common/ArchiveOpenCallback.cpp:369-385`). Header-encrypted input can
request a password during Open, before a caller can classify the archive safely.
The live B05-MAN review found materially different `E_ABORT` versus `S_FALSE`
observations; one inaccurate observation was corrected and a later inaccurate
causal claim was returned for further correction. This demonstrates why
source-plausible flattening is unsafe. Its manual lane remains blocked and is
not B05 PASS.
Consequently there is no honest “unencrypted-only open” precondition the bridge
can enforce before parsing, and no safe default reply.

### B06 supplies cancellation and callback-quiescence semantics

The ABI requires `is_cancelled`, permits concurrent progress, and requires
session-retained C++ callback adapters to detach only after quiescence
(`abi-v1.md:196-232`). The retained open path does not poll uniformly:
`COpenCallbackImp::SetTotal` is a no-op while `SetCompleted` checks break only
when a UI callback exists (`ArchiveOpenCallback.cpp:389-403`). Signature scanning
calls an offset progress callback only after an 8 MiB interval
(`OpenArchive.cpp:2543-2555`). No bounded cancellation latency follows.

More importantly, multivolume streams retain the open callback object: the source
comment says `COpenCallbackImp` can exist after Open until volume objects release
their references (`ArchiveOpenCallback.h:88-95`), and each
`CInFileStreamVol` stores both a raw implementation pointer and a COM reference
(`ArchiveOpenCallback.cpp:357-363`). Thus callback lifetime, cancellation,
close, and session teardown are one ownership problem. B06 staged polling and
quiescence observations are input-bearing; a callback adapter tested only by
synthetic direct invocation cannot prove safe return from real Open.

### Entries and close are not independently exercisable

`entries` and `close` require a real live `(archive_id, generation)` session.
Q1 requires page bounds against the engine item count and owned snapshots before
result destruction; close must invalidate the session while preserving already
owned Rust copies (`abi-v1.md:165-205`). `CArchiveLink` owns the nested `CArc`
chain, retained `IInStream`, handler interfaces and raw-property interfaces
(`OpenArchive.h:267-346,390-443`); `Close` releases each archive in reverse order
before identity invalidation (`OpenArchive.cpp:3172-3191`).

Creating a synthetic session merely to test page arithmetic or stale IDs would
exercise a new mock, not the retained engine. Defining `entries`/`close` while
leaving `open` undefined would create no reachable meaningful operation. Defining
a placeholder `open` that always reports Unsupported is likewise not a retained-
engine slice; S2a-DEV already correctly leaves the symbol undefined and the safe
surface disabled.

## Determination for every remaining mainline card

The table applies the same test to all unfinished cards in the M3 graph. “No”
means no immediately actionable DEVELOPMENT subset is proved; it does not say
that the original card should be deleted or can never run.

| Card | Candidate considered | Decisive input-bearing fact | DEVELOPMENT slice now? |
| --- | --- | --- | --- |
| B01 `t_22299c6f` | More corpus tooling or a reduced corpus | Rights/admission, actual members, format/volume/error observations and native oracle runs are the deliverable itself. Existing research does not set `import_approved` or `qualified`. | No |
| B03 `t_bf92ce13` | Offline stream tests or a smaller native run | Actual short-I/O/seek/large-file/cleanup semantics are the required input. Live execution authorization remains conditional; hazardous exhaustion design needs a separately approved bounded mechanism. | No |
| B04 `t_2a64c953` | Another containment preparation | Safety containment and overwrite/partial-effect observations are the deliverable itself. Live comment 135 freezes B04 with zero native budget. | No |
| B05 `t_3859d918` | Synthetic reply recorder or manual harness | Actual `IPassword` state/call/item outcomes are semantic input. The reviewed [B05/B06-P report](qualification/b05-b06-preparation-split.md) says another recorder would invent a competing observation schema; B05-MAN is blocked and not campaign PASS. | No |
| B06 `t_83983e9c` | Synthetic cancel controller | Actual polling, overlap, prompt wake and quiescence are semantic/ownership input. The [B05/B06-P report](qualification/b05-b06-preparation-split.md) says a fake controller proves only itself and can duplicate B04 supervision. | No |
| S2a `t_071e4cd7` | Open, entries, close, or callback-only second split | B01/B03/B05/B06 inputs are inseparable at real Open and retained-session lifetime, as proved above. | No |
| B08 `t_0a04d8dd` | Pre-write fault/lifetime tests | B08 qualifies the complete S2a facade. A nonexistent `open`/session/callback path cannot be stress-tested, and mocks are not qualification evidence. | No |
| S3 `t_481c87b0` | CLI parser/output shell without an engine | B08-qualified open/list surface and B01/B02/B05 output/error behavior are inputs. A no-op CLI would be scaffold, not the opt-in retained-engine listing operation. | No |
| S4 `t_e398de63` | Extract request types or disabled command | S3 selection plus B03/B04/B05/B06 semantics determine writes, null streams, overwrite, secrets, cancellation and partial effects. Data-loss semantics cannot be guessed. | No |
| S5 `t_9ca14b05` | Test-mode command shell | It consumes the real S4 extraction/testMode path and B01/B05/B06 call/item/cancel semantics. Implementing before them would invent the outcome mapping. | No |
| S6 `t_425adbdd` | Fresh-create request shell | S5 plus B02/B03/B05/B06 supply property, scanner, partial-write, password and cancellation semantics. Destination effects and generated-archive compatibility are inputs. | No |
| S7 `t_61c84597` | Pure task/progress state machine | S3-S6 command/outcome types, B06 polling/shutdown behavior and B08 ownership are implementation inputs. A detached synthetic controller is the rejected mock pattern, not integration with the one engine worker. | No |
| S8 `t_49ccd799` | Portable trait skeleton or read-only seam | S7 owns the command/lifetime integration and B03 defines partial I/O; B02 defines native path identity. Even a read-only stream contract cannot choose EOF/error/seek behavior without them. | No |
| S8L `t_be89f382` | Linux module early | The fixed S8 port contract and selector do not exist; native Linux behavior is this card's acceptance, not later confirmation of a completed target module. | No |
| S8W `t_595610a4` | Windows module early | The fixed S8 port contract does not exist, and Windows native path/handle semantics are core inputs. Cross-building would not qualify them. | No |
| S8M `t_600ba1b2` | macOS module early | The fixed S8 port contract does not exist, and macOS byte-path/filesystem semantics are core inputs. Linux evidence cannot supply them. | No |
| B07 `t_2e00825a` | Source-only GUI/runbook work | Native desktop behavior is the card's deliverable. B07-MAN is blocked evidence preparation and explicitly cannot close B07. It is not a production mainline slice. | No |
| Q2 `t_7ac2c6d5` | Early Qt/CXX-Qt pin or lifetime spike | Q2 is sequenced after qualified CLI/filesystem work and consumes the actual S8L/W/M composition. Omitting those parents would skip directly to GUI qualification, contrary to `migration-stages.md:65-69` and ADR-0003 timing. | No |
| S9a `t_bedc9b95` | Empty Qt/QML shell | Q2 exact pins/lifetime result, B07 desktop semantics, and all platform stream implementations are inputs. An early shell would violate the mandated Qt 6/QML -> CXX-Qt -> Rust order and GUI gate. | No |
| S9b `t_ce984818` | Browser DTO/model without reopen | It requires S9a plus B07 measured reopen/rollback and B02 name/property behavior. Removing reopen would not deliver the owned browser contract, and fake entries would bypass S2a/S3. | No |
| S10 `t_d3f76753` | Dialog-only QML | Actual S4/S6/S7 commands and B04/B05/B06/B07 interaction/effect semantics are inputs; QML may not invent archive policy. | No |
| S11W `t_1f366758` | Windows package skeleton | S10 UI and B07 identity/coexistence/OLE behavior are inputs; native activation is the card's core deliverable. | No |
| S11L `t_f757c611` | Linux launcher/package skeleton | S10 and B07 desktop contract are inputs; native desktop/session evidence is the card's core deliverable. | No |
| S11M `t_7b347d4f` | macOS bundle skeleton | S10 and B07 desktop contract are inputs; native bundle/Finder behavior is the card's core deliverable. | No |
| Q3 `t_8342040b` | Early license inventory | It must audit the actual selected S11 packages and obtain a precise human validation/signing scope. The amendment validator explicitly forbids DEVELOPMENT acceptance on the release path. | No |
| S12 `t_11923d05` | Build-only candidate | Exact-head native release validation, reviewed package inputs and human scope are the deliverable. DEVELOPMENT acceptance is forbidden on the release path and could not authorize publication. | No |

## Rejected fabricated slices

The following were considered because they can look runnable while the native
campaigns are deferred. None passes the reviewed test:

- **Session registry plus `entries`/`close` stubs:** no real session can exist
  without Open. Synthetic sessions prove only arithmetic and risk locking a fake
  lifetime into the ABI.
- **Directly invoked callback adapters:** do not prove handler retention,
  cross-thread overlap, polling reachability or post-call quiescence. The reviewed
  B05/B06-P report already rejects a competing recorder/controller without an
  actual reviewed native observation contract.
- **A pure S7 scheduler detached from archive commands:** S3-S6 do not yet supply
  the operation/outcome integration points. It would test its own state machine,
  not the one-worker retained-engine protocol.
- **An opt-in CLI command that always returns Unsupported:** it is not meaningful
  retained-engine work and would duplicate the current safe disabled state.
- **An early Qt/CXX-Qt spike:** Q2's stage edge is not merely native confirming
  evidence; it preserves the deliberate “CLI/filesystem before GUI” architecture
  sequence. Reordering it requires a reviewed architecture change, not a split.

## Consequences and compatibility limits

There is no parent set or coder specification to route because no slice qualifies.
The coordinator should make no new DEVELOPMENT card from this document. Existing
manual runbook, research and qualification cards may continue only under their own
reviewed authority; this result neither restarts nor cancels them.

No product, Rust, C, C++, codec, crypto, fixture, golden, CI, GUI, dependency or
board artifact is changed. No archive was opened, listed, tested, extracted,
created, downloaded or inspected. No native job, install, push, shared-branch
merge or release was performed. This documentation decision establishes no
Windows/Linux/macOS compatibility and does not close any deferred obligation.

A future second slice may be reconsidered only after a real input-bearing parent
is independently reviewed (for example B01/B03/B05/B06 sufficient for a precisely
bounded Open surface), or after a separately reviewed architecture/acceptance
amendment changes the required boundary. New activity alone, a manual runbook,
or a notification is not that evidence.

## Verification record

This task changes only this Markdown file, so product/native builds are not
applicable. Verification checks the existing DAG/amendment, unresolved-obligation
state, repository preservation, linked paths and document whitespace. Exact
commands and final commit identity are recorded in the same-card review handoff.
Independent review must re-check the negative conclusion against the live card
states and source anchors; PASS approves only this determination, not any native
campaign or production operation.
