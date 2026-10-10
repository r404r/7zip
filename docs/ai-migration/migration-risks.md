# M0: migration risks and validation

Task `t_48d08249`; branch `ai/migration-m0`; inspected source baseline `d1fcc44`.
This register accompanies [current architecture](architecture-current.md),
[Win32 map](win32-dependencies.md) and [engine boundaries](archive-engine-boundaries.md).
It identifies required evidence before future changes; it does not claim those
changes or tests have been implemented. No source behavior is ambiguous in a way
that must be decided to complete this documentation-only inventory. Future
licensing, semantic and destructive-operation decisions remain gated below.

## Risk register and acceptance evidence

| ID / severity | Concrete evidence and failure mode | Mitigation / required evidence and owner |
| --- | --- | --- |
| R01 Critical: wrong engine scope | `CPP/7zip/Bundles/Alone2/makefile.gcc:9` pulls a full arc bundle; `C/7z.h:22` has a narrower model. Primitive replacement loses formats, encryption or properties | M2: explicit capability/build manifest and retained C++ adapter. M1: known-fixture list/extract/test/create per supported capability. No universal C SDK substitution |
| R02 Critical: loss or unintended write | `CPP/7zip/UI/Common/ArchiveExtractCallback.cpp:1246`, `CheckExistFile`; `SetLink` (2221); `CPP/7zip/UI/FileManager/PanelOperations.cpp:116`, `DeleteItems` | M1: overwrite variants, skip/rename, path traversal/absolute paths, symlink/hardlink/reparse, read-only and partial failure in sandbox. M2: retain old policy first. Human decision before changed delete/overwrite semantics |
| R03 High: fork name regression | `CPP/7zip/UI/Common/SetProperties.cpp:48` filters/reset properties; `CPP/7zip/Archive/Zip/ZipItem.cpp:405` decodes names | M1 native Windows: scoped/unscoped properties, EFS, valid/invalid CRC Unicode extras, CP932/936, Unix-host fallback, explicit UTF-8 and reused-handler reset; preserve `.github/tests/zip_name_encoding.py`. M2 must preserve precedence |
| R04 High: cross-platform name mismatch | `CPP/Common/StringConvert.cpp:229-272` uses surrogate representation and default UTF-8 on Unix; `ExtractingFilePath.cpp:13` has platform defaults | M1: native Windows/Linux/macOS Unicode, invalid sequences, non-BMP, reserved/long names and byte-name round trips where supported. Keep display text separate from identity/native destination. No blind UTF-8-only model |
| R05 Critical: dangling FFI state | `CPP/Common/MyCom.h:14-45`; `CPP/7zip/UI/Common/LoadCodecs.h:320-335` library cycle; `UI/Agent/ArchiveFolderOut.cpp:61-77` invalidated proxies | M2: allocator/refcount table, session lifetime, copy-out values and destruction order. Later bridge tests: repeated open/close, failed reopen/update, dropping callback/stream/module at boundary, sanitizer coverage |
| R06 High: reentrancy/races | `CPP/7zip/Archive/IArchive.h:184-192` concurrent progress, (305) no simultaneous same-archive calls; `CPP/7zip/Common/CreateCoder.cpp:15` global registration; `CPP/7zip/Crypto/Rar5Aes.cpp:189` cache lock | M2: serialize archive access and initialization; audit separate-session/global crypto state before concurrency promises. Later stress/sanitizer runs must include progress callbacks and shutdown. Don't infer thread safety from refcounts |
| R07 High: cancel deadlock or damaged partial output | `CPP/7zip/UI/FileManager/ProgressDialog2.cpp:100`, `CheckStop`; `CPP/7zip/UI/Console/ConsoleClose.cpp:18` global break; `PanelOperations.cpp:496` null reopen callback | M1: cancellation at scan/open/extract/update stages, prompt waiting, pause/resume and partial output disposition. M2: request/reply cancellation, join order, no thread termination, no unproven latency guarantee. Large archive reopen has no cancel today |
| R08 Critical: password/encryption change | `CPP/7zip/IPassword.h:31-46` undefined vs empty; `CPP/7zip/Archive/Zip/ZipHandler.cpp:1091` password callback; `CPP/7zip/Crypto/RandGen.h:35` generator | Retain crypto A. M1: empty/missing/wrong/correct/non-ASCII passwords, encrypted headers, supported ZIP/7z methods and errors. M2: redact secrets and bound callback lifetime. New credential storage/crypto behavior requires human review |
| R09 High: errors flattened | `CPP/7zip/Archive/IArchive.h:132-145` item results; `UI/Common/OpenArchive.h:149` warnings/errors; `Console/MainAr.cpp:157-174` system/cancel translation | M1: truncated/corrupt/unsupported/CRC/wrong-password/multivolume cases; assert structured outcome and legacy exit/output separately. M2: preserve item results plus call status and warnings, not bool-only success |
| R10 High: metadata/large-file mismatch | `CPP/7zip/IStream.h:89-105` 64-bit seek/size; `ArchiveExtractCallback.cpp:2795`, `SetSecurityInfo`, (3171) `SetDirsTimes` | M1: timestamps/precision/time zones, permissions, ADS/security where supported, sparse/large files, links, full disk and short I/O. Native filesystem-specific evidence required; avoid UInt64 truncation into 32-bit counts |
| R11 High: desktop mistaken for portable CLI | `CPP/7zip/UI/FileManager/FM.cpp:632`, OLE; `UI/Explorer/ContextMenu.h:29`, native shell interfaces | M2: platform adapters and Qt-thread boundary, no GUI substitution. Later native GUI + shell/drag/drop/accessibility validation separate from CLI; preserve fork CLSID/coexistence |
| R12 High: configuration/identity drift | `CPP/7zip/UI/Common/ZipRegistry.cpp:319` UTF-8 default; `UI/GUI/ExtractDialog.h:123` Auto; `UI/Explorer/DllExportsExplorer.cpp:45` fork identity | M1: saved UTF-8 setting versus transient code page, reopen position, shell language reload and install coexistence. M2: explicit settings migration, not a shared persistent code-page field |
| R13 High: licensing/package assumptions | `DOC/License.txt:8-19`, LGPL/BSD/public-domain rules; (139-149) unRAR restriction; `.github/lang/README.md` asset provenance | M2: inventory exact linked inputs and Qt/CXX-Qt licenses. Packaging owner/human resolves unclear obligations before linking/distribution choice; no public-domain claim for full engine, no RAR encoder rewrite |
| R14 Medium: bundle/toolchain drift | `CPP/7zip/Bundles/Format7zF/Arc_gcc.mak:15` ST/MT variation; `.github/workflows/migration-native-cli.yml:34` native compiler branches | M1: record oracle commit, compiler, architecture, build flags, formats/methods and fixture provenance. M2: pin bridge build inputs; native matrix and equivalent capability list before comparing results |

## Existing verification inventory and its limits

* `.github/scripts/migration-smoke.py:10` creates controlled temporary fixtures;
  for 7z and ZIP it creates, lists, tests and extracts, then compares four paths
  and payload bytes. It explicitly states it is not the M1 compatibility oracle.
  It does not cover passwords, overwrite, cancellation, native metadata or desktop.
* `.github/workflows/migration-native-cli.yml:29` builds `7zz` on Linux/macOS;
  at 55 runs the smoke and at 57 the portable source/release checks.
* `.github/workflows/build-windows.yml:21` uses native Windows, builds MSVC
  products at 46 and runs `zip_name_encoding.py` at 58. Source shell-identity and
  language guards are not Explorer activation or full File Manager automation.
* `.github/tests/release_version_test.py`, `release_notes_test.sh`,
  `change_notice_test.py`, `lang_files_test.py`, `shell_ext_identity.py`, and
  `shell_ext_lang_reload.py` protect release/version, notices, assets and fork
  source contracts. They cannot certify extraction policy just by being green.
* G0 parent `t_5f1b2423` reports native Linux/macOS/Windows CLI PASS at bootstrap
  and identifies `d1fcc44` as the delivered base. This is inherited evidence,
  not a fresh M0 native CI run. No native Windows/macOS run was performed by M0.

## M1 and M2 handoff / sequencing

M1 (`t_f4afeee1`, tester) should build its coverage matrix around R01-R14 and
preserve existing expectations. Record gaps explicitly, restrict future production
cards to their characterized behavior and block any oracle/expectation conflict;
never change golden data merely to pass a new implementation.

M2 (`t_db8ffe0b`, architect) owns the architecture decisions, not production code:
engine capability set, facade/ABI, ownership and exception boundary, archive and
entry identity, per-task progress/cancel, platform filesystem abstraction,
configuration boundary and Qt 6/QML -> CXX-Qt -> Rust separation. It must not edit
M1 fixtures or silently decide their semantics. Both children depend on independently
reviewed M0; their existing operator subscriptions are reported by G0.

Reviewed M1 and M2 are both prerequisites to M3. Subsequent order stays: Rust
workspace, bridge, list, extract, test, create, tasks/progress/cancel infrastructure,
filesystem abstraction, Qt/QML GUI, native desktop integration, native release
validation. Any codec migration is an optional separate human-reviewed justification.
Identifying cancellation constraints now does not authorize skipping ahead in that
implementation sequence.

## Human escalation protocol for subsequent work

For a real unresolved gate record a typed `needs_input` blocked event on the
relevant card, with exact evidence and these context-specific alternatives:

* Semantic ambiguity/oracle disagreement: (1) recommended, retain measured legacy
  behavior and characterize missing cases, delaying only the affected rewrite;
  (2) approve a precisely documented behavior change with fixture provenance and
  compatibility impact; (3) defer the feature, explicitly narrowing release scope.
* Unclear license/linking/distribution obligations: (1) recommended, retain current
  engine/source boundary while a human resolves the selected package obligations;
  (2) approve a reviewed alternative linking/package arrangement, adding validation
  and notice work; (3) defer that distribution feature without claiming parity.
* Material Qt direction/toolchain failure: (1) recommended, investigate/pin a
  supported Qt/CXX-Qt configuration while preserving direction; (2) propose an
  evidence-backed alternative ADR for human approval, with rework/parity cost;
  (3) defer GUI while independent eligible CLI work continues.

A notification/wake is not approval. Missing native evidence is not permission to
claim portability. Never archive unresolved gates/unreviewed prerequisites; never
merge shared `dev-main` or publish a release. Two substantive failures return the
same card then escalate rather than creating repeated repair cards.

## Validation performed for this documentation card

Worktree: `/home/ding/work/github/r404r/7zip/.worktrees/t_48d08249`.
Source checkout branch verified as `ai/migration-bootstrap-20260911`; worktree
branch `ai/migration-m0`, clean at start, with committed `AGENTS.md` read first.
`git merge-base --is-ancestor d1fcc44 HEAD` returned 0: no parent import necessary.

Executed from the worktree, all succeeded (exit 0):

```sh
python3 .github/tests/release_version_test.py
python3 .github/tests/change_notice_test.py "$PWD"
python3 .github/tests/lang_files_test.py "$PWD"
python3 .github/tests/shell_ext_identity.py "$PWD"
python3 .github/tests/shell_ext_lang_reload.py "$PWD"
bash .github/tests/release_notes_test.sh
```

Observed summaries: release-version and release-notes checks `0 failed`;
change-notice check `34 modified upstream files, 0 without a notice`;
language check `93 language files checked, 0 problem(s)`; identity `0 failed`;
language reload `0 problem(s)`. These are actual local source/check executions,
not generated compatibility outcomes.

Documentation verification used source reads and definition/caller searches for
paths and line anchors; companion Markdown link targets were enumerated with
`search_files` and checked against the four existing files.
`git diff --cached --check` passed. An attempted automated citation checker did not execute: the
runtime rejected a helper write under protected `.hermes/` and rejected inline
Python execution in headless mode. Neither restriction was bypassed; no validator
file was created and no automated citation-check PASS is claimed. Exact final
results and commit are recorded in the review transition metadata. Source-based
manual verification does not replace independent review of semantic claims.
No new executable tests or C/C++ builds are applicable to changing only these four
Markdown files; M0 did not rebuild or run archive binaries. The unchanged portable
checks above provide preservation evidence, not full archive regression coverage.

Only the four required documents are deliverables. No production changes, expected
fixture changes, dependency installation, framework substitution, shared-branch
integration or release publication occurred. Independent reviewer must confirm
source claims and scope before PASS; this author does not self-complete M0.
