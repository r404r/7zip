# M0: archive engine boundaries

Baseline `d1fcc44`; source-informed candidates for M2, not an implemented API.
Read with [current architecture](architecture-current.md),
[platform map](win32-dependencies.md) and [risk register](migration-risks.md).

## Retained engine is larger than the C SDK

`CPP/7zip/Archive/IArchive.h` defines the central COM-like interfaces. Format
handlers implement them: for 7z, `CPP/7zip/Archive/7z/7zHandler.cpp:682`,
`CHandler::Open`; `7zExtract.cpp:229`, `CHandler::Extract`; and
`7zHandlerOut.cpp:392`, `CHandler::UpdateItems`. The decoder pipeline is in
`7zDecode.cpp:213`, `CDecoder::Decode`; encoding includes `7zEncode.cpp:312`,
`CEncoder::Encode1`. These compose coders, filters and format crypto rather than
being interchangeable with a single compression primitive.

`CPP/7zip/Archive/` includes ZIP, TAR, RAR, 7z, WIM, ISO/UDF, CAB, CHM, NSIS
and other handlers. Presence does not imply creation support for every format:
`IInArchive` and `IOutArchive` are separate capabilities. `CPP/7zip/Compress/`
and `CPP/7zip/Crypto/` remain A (retain), reached through a B (wrap) boundary.
`C/` and `Asm/` are retained primitives/optimized paths, not the whole archive API.

`C/7z.h:1` explicitly identifies its own public-domain 7z interface, with bounded
folder/coder structures at 22-51. `DOC/7zC.txt:1` describes an old 9.35 simplified
7z/LZMA decoder; its historical limitations are not an authoritative current
feature inventory. Neither its public-domain status nor its C calling convention
establishes equivalence to full multi-format C++ parsing, encryption, properties,
callbacks or creation. Do not substitute it as the universal engine to avoid FFI
or licensing work.

## Candidate seams and what each would omit

| Seam | Evidence | Assessment |
| --- | --- | --- |
| Whole CLI invocation | `CPP/7zip/UI/Console/MainAr.cpp:103`, `main`; `Main.cpp:806`, `Main2` | Good subprocess oracle; bad in-process ABI due to global streams, signals, command-line state and text output |
| C++ orchestration adapter | `CPP/7zip/UI/Common/OpenArchive.cpp:3222`, `CArchiveLink::Open`; `Extract.cpp:278`, `Extract`; `Update.cpp:1125`, `UpdateArchive` | Preferred initial B candidate for parity: retain probing, links/volumes, metadata, path and overwrite policy; isolate UI callbacks |
| Direct handler adapter | `CPP/7zip/Archive/IArchive.h:317`, `IInArchive` methods; `UI/Client7z/Client7z.cpp:1044`, factory usage | Useful narrow list prototype after reviewed prerequisites; caller must implement format selection, volumes, passwords, properties, warnings, filesystem extraction/update policy |
| DLL exports | `CPP/7zip/Archive/DllExports.cpp:48`, `CreateObject`; `ArchiveExports.cpp:14`, registration; `UI/Common/LoadCodecs.h:344`, `CreateArchiveHandler` | Native factory boundary, not a Rust-safe ownership contract; bundle/loading/calling conventions and retained module lifetime matter |
| C SDK / LZMA primitives | `C/7z.h`, `C/LzmaDec.h` | A; potentially specialized use only. Not accepted as full-engine replacement |

Provisional recommendation: put a narrow C++ facade between Rust and retained
engine/orchestration, starting with list then extract, test and creation in the
mandated sequence. M2 chooses the exact facade and capability manifest; M0 does
not freeze a new ABI. Do not expose CLI printing, HWND, arbitrary vtables or
`CPanel`/Agent proxies directly to Rust. Some `UI/Common` files are native GUI
launchers (`CompressCall.cpp:48` references `g_HWND`), so select units, not that
entire directory indiscriminately.

## Existing call contracts that constrain any facade

| Contract | Observed evidence | Required design consequence for M2 |
| --- | --- | --- |
| Open, close, enumerate, properties, extraction | `CPP/7zip/Archive/IArchive.h:277-328` | Open archive state must be owned; sorted indices and all-items sentinel must be validated; `testMode != 0` tests without writing output |
| Detection and nested archive state | `CPP/7zip/UI/Common/OpenArchive.h:117`, `COpenOptions`; `CArcErrorInfo` (149); `OpenArchive.cpp:3222`, `CArchiveLink::Open` | Don't reduce open to extension lookup; preserve warnings, offsets, tail/error flags, nested handler chain and volume callbacks |
| Item status versus call status | `CPP/7zip/Archive/IArchive.h:132`, `NExtract::NOperationResult`; `SetOperationResult` (234) | Preserve CRC/data/header/wrong-password/unsupported-method categories independently of HRESULT and open warnings |
| Stream partial I/O | `CPP/7zip/IStream.h:23-105`, `Read`, `Write`, `Seek`, `SetSize` | Processed byte counts and partial progress are meaningful even on error; do not equate successful read with filling the buffer or reject legal seek-past-end |
| Property result ownership | `CPP/7zip/Archive/IArchive.h:20-41`; `CPP/Common/MyCom.h:14-45` | Initialize out values; clear PROPVARIANT, free BSTR and Release interfaces with the matching C++ allocator/refcount mechanism |
| Callback streams | `CPP/7zip/Archive/IArchive.h:194-208`, `GetStream`; update stream rules (427-434) | Null may mean directory/link/skip; extract and update have different rules. Preserve reference ownership and callback state until engine use ends |
| Update semantics | `CPP/7zip/Archive/IArchive.h:417-458`, `IArchiveUpdateCallback`, `IArchiveUpdateCallback2` | `newData`, `newProps`, index-in-archive, skipped inputs and volumes are not just a list of source paths |
| Password request | `CPP/7zip/IPassword.h:16-50`, `ICryptoGetTextPassword` / `ICryptoGetTextPassword2` | Undefined password and empty password are different. Caller frees even an allocated empty BSTR when undefined; no credentials in logs/events |
| Optional/raw properties | `CPP/7zip/Archive/IArchive.h:355-377`, `IArchiveGetRawProps` | Copy data while its owner is valid unless lifetime is proven; expose typed values/unknown markers, not arbitrary borrowed pointers |

### Ownership and lifetimes: proposed constraints, not current Rust guarantees

* Keep interfaces in C++ RAII ownership. `CMyComPtr` increments on copying and
  releases on destruction; `Attach`/`Detach` transfer without the same increments.
  A borrowed pointer must not be treated as a newly owned reference. Use opaque
  session identity with one explicit destroy path; no Rust `Box::from_raw` for
  C++ objects or Rust freeing BSTR/PROPVARIANT storage.
* Retain streams and open/callback state through all operations that may use them;
  keep codec modules alive until all dependent handlers and streams are released.
  `CPP/7zip/UI/Common/LoadCodecs.h:320-335`, `CCodecs::CReleaser`, explicitly
  breaks a library/codecs reference cycle. A generic shared pointer alone is not
  sufficient evidence that unload order is safe.
* Rust-visible entries should be owned snapshots with session/generation identity.
  In `CPP/7zip/UI/Agent/ArchiveFolderOut.cpp:35-80`, reopen destroys proxies,
  retries the old code page on failure and reports `folderIsUsable = false` if
  recovery also fails. Borrowed Agent entries become stale across reopen/update.
* Every FFI buffer needs explicit element type, length, ownership and valid-call
  interval; wchar_t/UString is not a Rust `String` ABI. Preserve raw/native names
  where needed alongside display text; a lossy display conversion must not become
  an extraction target or stable identity.
* Exceptions must be caught at the C++ facade and translated; Rust panics must not
  unwind into C++ callbacks. `MainAr.cpp:138-174` shows the existing distinction
  among allocation failure, user cancellation and other system failures. A future
  bridge must retain those distinctions without importing CLI exit codes as the
  entire library error model.

### Threading, progress and cancellation

`CPP/7zip/Archive/IArchive.h:305-307` forbids simultaneous calls on the same
`IInArchive`. At 184-192 it says extraction's GetStream/PrepareOperation/
SetOperationResult calls are not simultaneous with each other, but progress
interfaces may be called on other threads concurrently. These are different
rules; do not derive `Send`/`Sync` from COM refcounting or serialize only progress.
Initial candidate: one owning worker/serialized command queue per archive and
thread-safe progress/cancel state, with registration/loading serialized separately.
Cross-session safety still needs measurement and tests, including global state.

Progress units differ by format and whether total was reported (`IArchive.h:214-223`);
unknown total must remain unknown. A monotonically increasing percentage is not
always the actual engine contract. `CPP/7zip/UI/FileManager/ProgressDialog2.cpp:100`
uses cooperative `E_ABORT`; `CPP/7zip/UI/Console/ConsoleClose.cpp:18` uses a
process-global break counter. New per-task cancellation must not kill codec threads
or reuse a process-global flag without isolation. Cancellation latency and partial
output cleanup are M1 characterization requirements, not guarantees established here.

Engine callbacks must never directly mutate QML models. Proposed CXX-Qt boundary:
owned, queued progress/result snapshots to the Qt thread; synchronous engine
questions (password, overwrite, volumes) need an explicit request/reply protocol
with cancel and shutdown handling. Do not hold engine/global locks while waiting
for a UI reply, or require the UI thread to wait for an engine callback which is
itself waiting on that UI. M2 must settle reentrancy and join/destruction order.

## Compatibility policy lives above handlers too

`CPP/7zip/UI/Common/ArchiveExtractCallback.cpp` handles `CorrectPathParts` (1081),
`CheckExistFile` (1246), `GetExtractStream` (1380), `CloseFile` (2053), links (2221),
security (2795) and directory times (3171). `Update.cpp:1125`, `UpdateArchive`,
coordinates creation/update rather than simply calling a compressor. Retaining
only codecs while rewriting this policy blindly would not preserve compatibility.
Retain it behind B before separately characterized C/D replacements.

Fork properties must flow through `CPP/7zip/UI/Common/SetProperties.cpp:48`, or an
exactly characterized equivalent: scoped names only reach matching handlers, and
an empty filtered set resets state of reused handlers. `OpenArchive.cpp:1379` and
`3465` apply this behavior during open/reopen. ZIP encoding lives in
`Archive/Zip/ZipItem.cpp:405`; TAR has its own setter at
`Archive/Tar/TarHandler.cpp:1021`. No generic Rust text decoder should supplant it.

## Licensing evidence and release boundary

`DOC/License.txt:8-19` is the repository-wide rule: default LGPL, public-domain
only where stated, RAR decoder sources matching `CPP/7zip/Compress/Rar*` under
LGPL plus unRAR restriction,
LZFSE and ZSTD BSD-3-Clause, XXH64 BSD-2-Clause. LGPL text at 27-30 specifies 2.1
or later. The unRAR restriction at 139-149 prohibits using the source to recreate
the RAR compression algorithm and requires its stated notice. `DOC/copying.txt`
and `DOC/unRarLicense.txt` carry supporting texts; source headers and selected
object lists must accompany a distribution audit.

`C/7z.h:1` and `C/Threads.h:1` have explicit public-domain notices; that evidence
must not be generalized to `CPP/7zip` or the full linked product. `README.md:97`
identifies the fork as a modified build. This is an engineering inventory, not a
legal approval of static linking, dynamic linking, Qt distribution or third-party
plugins. Before a production packaging decision, identify every included object,
Qt/CXX-Qt version and license, notices, source/relinking obligations and language
asset provenance (`.github/lang/README.md`). Escalate unclear obligations to a human;
no new distribution or license choice is authorized in M0.
