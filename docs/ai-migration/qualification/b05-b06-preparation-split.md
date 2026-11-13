# B05/B06-P: source-grounded preparation split assessment

Status: assessment submitted for independent review, NOT implementation authority
or native qualification. Task `t_1814209d`, branch `wt/t_1814209d`.

## Decision and finite handoff

Recommend **no useful safe split** into another preparation card for either B05
or B06 under the current constraints. Source-only advance work is useful, but its
smallest reusable outputs are the callback map and observation checklist in this
report itself. Send these to the existing tester-owned cards after independent
review; do not commission another map, speculative harness, or mock runtime.
This is a bounded scheduling judgment, not a claim that all offline test work is
impossible. It avoids extra review/implementation work with no demonstrated
critical-path reduction while B03 and the approved B01 acquisition lane proceed.

- B05 `t_3859d918` remains dependent on B01 `t_22299c6f` and M3 `t_82c76197`.
- B06 `t_83983e9c` remains dependent on B04 `t_2a64c953` and M3 `t_82c76197`.
- Neither assessment PASS nor a source/mock check releases S2a, S4–S8, B07 or Qt.
- No cards, edges, schemas, ABI declarations, golden expectations or execution
  budgets are added or changed. There is no competing implementation branch.

Coordinator action after PASS: retain both edges, deliver the exact report commit
and sections below to B05/B06, and schedule their existing tester only when their
original prerequisites permit. Do not ask for another broad research round. A
later concrete independent slice may be assessed only against an actual reviewed
input/recorder contract, not merely the existence of callback method names.

## Authority, reviewed inputs and live gate snapshot

Source and worktree `AGENTS.md` were read. Source checkout was clean on
`ai/migration-bootstrap-20260911`; task checkout was clean on `wt/t_1814209d` at
`3ccb200d73028a035e00d3ba505f88759b81541a`. Reviewed M1 `6e958b6`, M2 `29e4c6a`
and M3 `0706af3` are ancestors, so no import was required. Reviewed Q1 `5f07f21`
is also an ancestor (its reviewer run records `approved`). The reviewed B04-P
report `9c038dc` is already included; its containment decisions remain architect
owned. No unreviewed B01/B03/B04 implementation was imported.

Read the complete [M3 graph](../migration-dag.md), its
[snapshot](../migration-dag.json), [target architecture](../architecture-target.md),
[stages](../migration-stages.md) and all three referenced ADRs. Normative M2
ownership/error/task contracts apply; the existing [Q1 ABI prose](abi-v1.md)
elaborates them but is not a license to invent an extract/create callback layout
or a new observation schema here. Preserve Qt 6/QML -> CXX-Qt -> Rust -> retained
C/C++ engine, with one owner worker and no callback reentry.

Live cards and targeted read-only board queries established:

| Card | Observed state and limiting evidence |
| --- | --- |
| B05 | `todo`, direct parents exactly B01 and M3; no implementation/review run yet. |
| B06 | `todo`, direct parents exactly B04 and M3; no implementation/review run yet. |
| B01 | `triage`. Comments 96/98 distinguish reviewed O1 policy/rights preparation from the newly authorized seven-file acquisition/quarantine lane `t_d32ff791`. No extraction/list/test, official-corpus inclusion, writer or native qualification follows from acquisition authority. Remaining rights, bytes/member hashes and native behavior gates persist. |
| B04 | `triage`. Comment 72 records two failed native containment rounds and unreviewed `9728808`; comment 100 records independent B04-P PASS only. A further bounded diagnostic round still requires actual authorization and static review. No hostile extraction is authorized. |
| B03 | `running` on the tester lane. Comments 86/91 authorize offline implementation of a reviewed small-file diagnostic proposal, not new native sparse/full-volume/CI execution. Do not interrupt or duplicate this work. |

The [B04-P plan](b04-actions-recovery-plan.md) owns process-sandbox diagnosis,
runner/collector protection, logs-only execution proposal, budgets and stop rules.
This report neither reopens its alternative selection nor supplies a substitute
sandbox. The [B01 replay policy](b01-replay-policy.md) and
[bounded rights review](b01-o1-rights-review.md) do not qualify B05's encrypted
fixtures. In particular, a RAR acquisition pilot is not a ZIP/7z password oracle.

A read-only subscription comparison returned `(1, 1)`: an exact inherited M3
Telegram route exists (including delivery metadata, `default`, `notify+wake`),
and the M3 -> this-task dependency exists. No route identifiers were emitted or
changed. No subagents or extra workers were started.

## Source-established password facts

These are source facts at the starting commit, not executed observations. Paths
and line ranges below are review anchors, not claims of exhaustive format coverage.

| Boundary / call chain | Established fact and constraint on a future test |
| --- | --- |
| [IPassword.h](../../../CPP/7zip/IPassword.h):16–51, `ICryptoGetTextPassword`, `ICryptoGetTextPassword2` | Caller initializes BSTR to NULL and frees returned allocation with `SysFreeString`. The second interface separately returns `passwordIsDefined`; undefined may still return an allocated empty string. BSTR nullness or length alone cannot classify undefined. The first interface has no definedness out-parameter. M2's typed reply states must not be mistaken for identical native signatures. |
| [ArchiveOpenCallback.h](../../../CPP/7zip/UI/Common/ArchiveOpenCallback.h):25–40,89–95,141–155; [ArchiveOpenCallback.cpp](../../../CPP/7zip/UI/Common/ArchiveOpenCallback.cpp):370–385 | `COpenCallbackImp` proxies native password requests through a queried reopen interface or `IOpenCallbackUI::Open_CryptoGetTextPassword`; absent ordinary callback returns `E_NOTIMPL`. Volume objects can retain the proxy after Open. Raw UI callback pointers are documented for the Open stage: interface retention does not prove operation state may be borrowed forever. |
| [OpenArchive.cpp](../../../CPP/7zip/UI/Common/OpenArchive.cpp):1133–1173, `CArchiveOpenCallback_Offset` | Offset probing adds another queried password proxy; it forwards only when available, otherwise `E_NOTIMPL`. Direct handler-only testing misses this retained orchestration layer. |
| [7zHandler.cpp](../../../CPP/7zip/Archive/7z/7zHandler.cpp):694–720; [7zDecode.cpp](../../../CPP/7zip/Archive/7z/7zDecode.cpp):424–452 | Open queries `ICryptoGetTextPassword` and passes it into `ReadDatabase` for header decoding. A crypto decoder requests a password, reports `E_NOTIMPL` when the provider is absent, and supplies two bytes per password code unit to `CryptoSetPassword`. This is not a UTF-8 password contract. |
| [7zExtract.cpp](../../../CPP/7zip/Archive/7z/7zExtract.cpp):122,363–366; [ArchiveExtractCallback.cpp](../../../CPP/7zip/UI/Common/ArchiveExtractCallback.cpp):2924–2933 | Extraction queries the native password interface; the retained extraction proxy lazily queries and forwards to its UI callback. Item completion travels separately through `SetOperationResult`. A CLI password argument alone is not evidence that every native callback state was exercised. |
| [UpdateCallback.h](../../../CPP/7zip/UI/Common/UpdateCallback.h):33–60,85–99; [UpdateCallback.cpp](../../../CPP/7zip/UI/Common/UpdateCallback.cpp):1012–1023 | `CArchiveUpdateCallback` exposes both password interfaces and forwards them to `IUpdateCallbackUI`. Creation's definedness and existing-data password requests must be recorded as different call sites, not flattened into one mock. |
| [7zHandlerOut.cpp](../../../CPP/7zip/Archive/7z/7zHandlerOut.cpp):721–763 | Writer requests `CryptoGetTextPassword2`; existing `_passwordIsDefined` can supply password state when method state is undefined. Header-encryption properties also affect selection. A fresh-create result cannot establish existing-archive update semantics. |
| [ZipHandlerOut.cpp](../../../CPP/7zip/Archive/Zip/ZipHandlerOut.cpp):392–425 | Writer queries password2, preserves definedness and rejects a defined non-simple-ASCII password with `E_INVALIDARG`; AES length has another rejection. Preserve this branch; do not propose accepting non-ASCII ZIP passwords as a preparation convenience. |
| [ZipHandler.cpp](../../../CPP/7zip/Archive/Zip/ZipHandler.cpp):1090–1141 | Reader uses password1 and the active conversion uses `CP_ACP`. Missing provider or password-setting failure can set item `kWrongPassword` while returning `S_OK` from this helper. This is NOT a prediction of every wrong-password archive's outer result. |
| [OpenCallbackConsole.cpp](../../../CPP/7zip/UI/Console/OpenCallbackConsole.cpp):82–94; [ExtractCallbackConsole.cpp](../../../CPP/7zip/UI/Console/ExtractCallbackConsole.cpp):526–531 | Console open initializes the BSTR, checks break before prompting, caches a supplied password and returns a BSTR; extraction forwards under `MT_LOCK`. Capturing that console lock behavior does not authorize using it as the future Rust mailbox policy. |
| [UpdateCallbackConsole.cpp](../../../CPP/7zip/UI/Console/UpdateCallbackConsole.cpp):830–878; [UserInputUtils.cpp](../../../CPP/7zip/UI/Console/UserInputUtils.cpp):63–117 | Update password2 distinguishes `AskPassword` from `PasswordIsDefined`; password1 prompts when undefined. `GetPassword_HRESULT` distinguishes scan failure, stream error, and empty EOF (`E_INVALIDARG`, `E_FAIL`, `E_ABORT`). Which branch an actual terminal disconnect/signal reaches remains a native observation, not a guessed expected value. |

Reusable B05 observation checklist (requirements, not a new schema):

- Label interface, operation, retained proxy and handler/method, plus actual
  callback invocation/return and separately outer call/item results. No inference
  of wrong-password status merely from corrupt data or CLI exit code.
- Exercise absent provider, undefined password2 (including allocation despite
  undefinedness), defined-empty, public synthetic wrong/correct/non-ASCII values,
  explicit callback cancellation, prompt EOF and consumer disconnect distinctly.
  Do not fabricate an undefinedness output for password1.
- Keep header encryption, data encryption, fresh creation and existing-archive
  update as separate observations. Bind cases to the eventual reviewed B01
  fixture/method/provenance/native tuple; no IDs or expected archive outcomes are
  assigned by this report.
- Record allocator/cleanup and callback retention checks without password payloads
  in ordinary diagnostics. Test redaction at the actual future recorder, using
  public synthetic secrets only; a stand-alone scrubber's success is insufficient.
- Preserve M2/Q1 private secret storage and reply/cancel separation. This checklist
  does not change any ABI tag, enum, encoding, error or cancellation mapping.

## Source-established progress/cancellation facts

| Stage / source anchor | Actual path and limit |
| --- | --- |
| Scan: [EnumDirItems.cpp](../../../CPP/7zip/UI/Common/EnumDirItems.cpp):111–117,280,319,333; [UpdateCallbackConsole.cpp](../../../CPP/7zip/UI/Console/UpdateCallbackConsole.cpp):183–194 | `CDirItems::ScanProgress` calls its callback when present; callers propagate HRESULT. Console update scan returns `CheckBreak()`. These are potential observed triggers, not a guaranteed callback count or pre-write boundary on every input. |
| Open: [IArchive.h](../../../CPP/7zip/Archive/IArchive.h):177–181; [OpenCallbackConsole.cpp](../../../CPP/7zip/UI/Console/OpenCallbackConsole.cpp):10–70 | Open progress has independently nullable files/bytes counters; both console forwarding methods check the break signal. A percentage in console output is not the native progress interface. |
| Open exceptions: [ArchiveOpenCallback.cpp](../../../CPP/7zip/UI/Common/ArchiveOpenCallback.cpp):284–294,389–403; [OpenArchive.cpp](../../../CPP/7zip/UI/Common/OpenArchive.cpp):1177–1185 | Volume lookup checks break before path/open work. The one-argument `IProgress::SetTotal` is a no-op; `SetCompleted` checks break only with a UI callback. Offset proxy `SetTotal` also returns `S_OK`. Do not assert that every progress entry polls cancel or that an absent callback is interruptible. |
| Extract/test: [Extract.cpp](../../../CPP/7zip/UI/Common/Extract.cpp):225–250; [ArchiveExtractCallback.cpp](../../../CPP/7zip/UI/Common/ArchiveExtractCallback.cpp):397–448 | Retained coordinator chooses `testMode`, resets completed before non-stdin extraction, invokes `IInArchive::Extract`, closes the callback and routes `ExtractResult`. Multi-archive forwarding rescales completed and conditionally suppresses total. Capture phase/counter provenance, not monotonic percentage assumptions. Test uses this path, not a separate decoder. |
| Extract progress: [IProgress.h](../../../CPP/7zip/IProgress.h):12–17; [ExtractCallbackConsole.cpp](../../../CPP/7zip/UI/Console/ExtractCallbackConsole.cpp):238–260 | Native total is a value and completed a pointer. Console methods lock and return `CheckBreak2()` even when percent printing is off. A synthetic callback invocation cannot prove a codec will invoke it during a selected stage. |
| Create/update: [Update.cpp](../../../CPP/7zip/UI/Common/Update.cpp):855–863; [UpdateCallback.cpp](../../../CPP/7zip/UI/Common/UpdateCallback.cpp):103–114,144–148,596 | Coordinator calls `UpdateItems`. Proxy forwards progress and explicitly checks break in item-info/input-stream paths. Early HRESULT propagation precedes the success-path closed-input check. This is not proof of rollback, output deletion or all-thread join on error. |
| Unequal polling: [UpdateCallbackConsole.cpp](../../../CPP/7zip/UI/Console/UpdateCallbackConsole.cpp):595–622 | `SetTotal` returns `S_OK`; `SetCompleted` and ratio callbacks check break. A generic test that assumes all progress methods return `E_ABORT` after cancellation would encode a false oracle. |
| Console controls: [ConsoleClose.h](../../../CPP/7zip/UI/Console/ConsoleClose.h):10–22; [ConsoleClose.cpp](../../../CPP/7zip/UI/Console/ConsoleClose.cpp):18–83 | Non-CE `TestBreakSignal` tests a nonzero counter. Windows handler treats logoff specially and returns FALSE at the threshold; POSIX installs SIGINT/SIGTERM and exits at the threshold. Repeated-signal termination is not cooperative cancellation. Actual console groups, delivery and prompt wake behavior require native tests. |
| Overlap and units: [IArchive.h](../../../CPP/7zip/Archive/IArchive.h):184–229,305–307 | Extract stream/prepare/result calls are not simultaneous with each other, but progress may overlap them. Completed units depend on format/total reporting. Simultaneous calls on one archive are forbidden. A serialized mock does not qualify native overlap or callback quiescence. |
| Pause: [ProgressDialog2.cpp](../../../CPP/7zip/UI/FileManager/ProgressDialog2.cpp):91–109 | Legacy GUI `CProgressSync::CheckStop` loops while paused, sleeping between locked checks. Therefore there is no repository-wide absence-of-pause claim. The inspected CLI/native interfaces provide no universal pause protocol; unsupported CLI pause must not be broadened into a cross-platform GUI conclusion. GUI qualification remains B07/later stages. |

Reusable B06 observation checklist (not instrumentation authorization):

1. Identify scan/open/extract/test/create/update by actual callback/call-site
   observation. Distinguish request time, first observed polling boundary and
   return/cleanup; timed sleeps alone do not establish the stage reached.
2. Preserve optional totals, units, null completed pointers, total suppression,
   progress resets and possible overlap. Do not interpret UI coalescing as an
   engine event log. Keep per-item results lossless and separate from progress.
3. Separate cooperative E_ABORT, prompt EOF/unavailable, ordinary engine error,
   timeout and forced process termination. A timeout collector may protect a
   harness, but its kill is never a cancellation oracle PASS.
4. Observe pending prompts, callback entry/exit overlap, retained adapters and
   post-call activity before claiming quiescence or safe join. Do not implement
   M2's sticky CancelRequested/worker-independent reply channel here: that is
   later bridge/task implementation, not observed legacy behavior.
5. For all write stages retain preexisting archive identity and post-operation
   tree/payload/metadata/partial-output evidence. B04 owns safe containment and
   overwrite effects; B03 owns metadata/scan/partial-I/O qualification. No blind
   deletion, simulated rollback, sandbox substitution or guessed shutdown bound.

## Candidate decisions, ownership and critical-path value

The following exact paths are **proposed, uncreated paths**, not existing files,
assigned work or permission to implement. All candidates would consume reviewed
M1/M2/M3 and this report; execution candidates also need their original gate PASS.
There is no recommendation to create any of them now.

| Candidate and reusable output | Exact proposed owned paths; future assignee | Verification and dependency boundary | Decision / critical-path effect |
| --- | --- | --- | --- |
| B05 source-only callback/observation specification | `docs/ai-migration/qualification/b05-callback-observations.md`; `tester` | Source/interface/path review only; consume M2 ownership/error contracts. No bytes, native execution or schema decisions. Independent of B03/B04 only while limited to static password paths. Native fixture binding still waits for reviewed B01. | Safe but no useful additional split: this report already supplies that finite map/checklist. Creating another documentation card duplicates evidence and review. Reuse here saves rediscovery on B05. |
| B05 offline password/reply recorder tests | `.github/tests/migration/b05/test_password_records.py`, `.github/tests/migration/b05/password_records.py`; `tester` | Synthetic undefined/empty/cancel/error and redaction negative controls could test a recorder without archives. But M2/Q1 describe native/app contracts, not this harness's serialized observation representation. A concrete recorder contract/owner decision must precede implementation; later native B01/B05 binding is mandatory. No touching B03/B04 or shared harness/workflow. | Not selected. Inventing a new recorder here risks a competing schema or testing only its own fabricated outcomes. Stand-alone redaction does not establish actual log non-disclosure. No demonstrated reusable implementation saving without that contract. Refer any required shared schema choice to architect, not parallel workers. |
| B06 source-only stage/polling observation specification | `docs/ai-migration/qualification/b06-stage-observations.md`; `tester` | Review actual polling/forwarding/non-polling sites against M2; no event enum or measured latency assertions. Source work is independent of B04 execution and B03 I/O, but runtime stage selection is not. | Safe but no useful additional split: the stage map/checklist above is the reusable output. Another map card creates research churn, not a new prerequisite solution. |
| B06 synthetic stage/cancel controller | `.github/tests/migration/b06/stage_controller.py`, `.github/tests/migration/b06/test_stage_controller.py`; `tester` | Fake event tests could prove only their own state machine. Real process identity, controlled signaling, deadlines, trusted collection and cleanup depend on the reviewed B04 containment contract; filesystem-effect observations must consume B03/B04 evidence. M2 task model is not a harness supervisor specification. | Not selected. Implementing now either duplicates B04's controller/security work or defers its essential interfaces and yields a throwaway mock. Moving it to a separate path does not establish independence. |

Native B05 harness construction belongs later under its already-owned
`.github/tests/migration/b05/` and `docs/ai-migration/qualification/b05.md`;
B06 construction belongs under `.github/tests/migration/b06/` and
`docs/ai-migration/qualification/b06.md`. Those existing card ownership allocations
are unchanged. Production callback adaptation remains staged S2a/S4–S7 ownership,
not an alternative candidate in this assessment.

## Verification, compatibility limits and review instructions

This is one Markdown addition. There is no executable implementation to build,
so no native build/test or B03/B04 unittest is appropriate; some existing harness
tests themselves launch native probes. No archive bytes were acquired, generated,
opened, listed, tested, extracted or downloaded. No CI/push/rerun, host/VM changes,
credential access, codec/encryption/overwrite/cancel changes or releases occurred.
Only local documentation/graph preservation checks are applicable.

Executed checks and final commit identity are also recorded in the same-card review
handoff. Source citations were read with `read_file`/`search_files` and compared to
actual declarations/usages, not generated from method-name guesses. The SQLite
reads used only selected task/comments/edge/routing fields; no routing values were
printed. Initial convenience tools (`execute_code` and Python `-c`) were rejected
before execution by headless policy; no approval settings or bypass were used.
A combined SQLite statement was rejected and split into individual read queries;
an invalid JSON path query was not counted as successful review evidence.

Executed verification (all successful checks below returned exit 0):

- `git merge-base --is-ancestor <commit> HEAD` for `6e958b6`, `29e4c6a`,
  `0706af3`, `5f07f21` and `9c038dc`: all required reviewed inputs present.
- `python3 docs/ai-migration/validate-migration-dag.py`: `Manifest PASS: 29
  children, 104 child edges, acyclic, complete prerequisites`; three negative
  controls PASS. This is offline preservation, not the pre-M3 live validator.
- `git diff --exit-code 3ccb200 -- C CPP Asm .github AGENTS.md
  docs/ai-migration/migration-dag.md docs/ai-migration/migration-dag.json`: no
  differences. `git diff --check`: no errors.
- Explicit shell `for p in <each linked source/document path>; do test -f "$p"
  || exit 1; done`: every link/source target exists. Relative links were manually
  resolved from this report's qualification directory; no automatic Markdown
  anchor-parser test is claimed. All links use file targets, not generated anchors.
- Targeted added-document credential-assignment pattern search: no matches.
- `python3.14 -m sqlite3 "$HERMES_KANBAN_DB" <SELECT>`: exact reviewed M3/Q1/
  B04-P commit/verdict fields confirmed; repeated B05/B06 state/parent query
  again returned `todo` with precisely the two original parents for each.

Staged whitespace, complete changed-file scope and clean post-commit status are
recorded in the review transition, alongside the immutable report commit. These
checks establish report/graph consistency only. All native Windows/Linux/macOS password, error,
prompt, cancellation, partial-effect and lifetime behavior remains unqualified by
this task. Source branches do not prove actual callback reachability for a fixture,
signal delivery, shutdown latency, byte conversion parity or engine-wide erasure.

Reviewer must independently check source claims, candidate independence and live
DAG/authorization before PASS. PASS means this assessment is accepted, not that
B01/B04/B05/B06 are complete or that future candidate paths may be implemented.
After PASS, reviewer posts the exact reviewed commit/path and the no-new-split
recommendation to both `t_3859d918` and `t_83983e9c`, then reads both comments back.
The implementer must not post a fabricated reviewed outcome before that verdict.
CHANGES returns this same card; two substantive failures require a real
`needs_input` gate. Only reviewer may perform any serial reviewed local integration;
no shared `dev-main` merge or publication is authorized.
