# M2: target architecture

Status: design for independent review; no production implementation or compatibility
certification. Task `t_db8ffe0b`, branch `ai/migration-m2`. Source baseline is
`3aea9f8`, containing independently reviewed M0 commit `1b54c95`. The M0 source
anchors remain valid: no engine changes separate those documentation commits.

Read [current architecture](architecture-current.md), [engine evidence](archive-engine-boundaries.md),
[platform evidence](win32-dependencies.md), [risk register](migration-risks.md),
[sequencing](migration-stages.md), and the decisions:

- [ADR-0001: retained engine and facade](adr/0001-retained-engine-facade.md)
- [ADR-0002: ownership, tasks and platform boundary](adr/0002-ownership-tasks-platforms.md)
- [ADR-0003: Qt presentation and build qualification](adr/0003-qt-build-qualification.md)

All paths in the proposed workspace below are NEW design names, not existing files.
Source citations elsewhere are existing repository paths and symbol anchors.
The normative contracts here constrain subsequent cards; they do not authorize
uncharacterized behavior, a production build, distribution, or legacy removal.

## 1. Direction and dependency graph

```text
Qt 6 / QML (Qt thread)
  -> CXX-Qt presentation adapter (owned DTOs, queued notifications)
    -> archive-app (commands, tasks, settings policy)
      -> archive-domain (models and ArchiveEngine port)
        <- archive-engine (safe adapter implementing the port)
          -> archive-engine-sys (private C ABI declarations)
            -> C++ facade -> retained UI/Common orchestration
              -> mature C++ archive handlers / codecs / crypto -> C / Asm

archive-cli -> archive-app
archive-app -> archive-platform (portable ports)
archive-platform -> platform/{windows,linux,macos} implementations
```

This is dependency inversion: domain defines the port, the safe engine adapter
implements it, and executable composition roots inject the adapter into app.
Domain has no dependency on the engine implementation or platform implementations.
The Qt side does not bypass app to call C++ archive objects. CXX-Qt is ONLY the
Qt/Rust presentation bridge; the engine has its own narrow C facade.

Initial retained policy includes probing, nested archives, volumes, property
selection, scanning, extraction paths, overwrite, metadata and update planning.
`CPP/7zip/UI/Common/OpenArchive.cpp` (`CArchiveLink::Open`), `Extract.cpp`
(`Extract`), `ArchiveExtractCallback.cpp`, and `Update.cpp` (`UpdateArchive`)
are the behavioral seams, not `Console/Main2` and not just a compression SDK.
Do not compile every file in UI/Common: native launchers such as `CompressCall.cpp`
are outside the facade. Agent folder proxies, CPanel and HWND never cross it.

## 2. Proposed workspace and boundaries

Create later under `rust/`, leaving legacy build roots and executables intact:

| Proposed path / Cargo package | Responsibility | Allowed direct dependencies |
| --- | --- | --- |
| `rust/Cargo.toml` | Workspace; CLI default members, GUI opt-in | Members below |
| `rust/crates/archive-domain` | Owned values, operation requests/outcomes, ArchiveEngine port | Standard library initially; no Qt, sys or OS API dependency |
| `rust/crates/archive-app` | Use cases, task state, selection, settings and interaction routing | domain, platform portable ports |
| `rust/crates/archive-engine-sys` | Audited unsafe C ABI declarations and link/build integration | Matched facade headers/library only |
| `rust/crates/archive-engine` | Safe port implementation, validation, worker-owned handle registry | domain, engine-sys |
| `rust/crates/archive-platform` | Native paths and platform services; implementations under `src/platform/windows`, `linux`, `macos` | domain, target-specific OS dependencies only |
| `rust/crates/archive-cli` | New CLI parsing/output/exit mapping and signals | app, domain, engine, platform |
| `rust/crates/archive-qt` | CXX-Qt objects and DTO mapping; executable composition | app, domain, engine, platform, pinned Qt/CXX-Qt dependencies |
| `rust/ui/qml/` | Views, interaction and presentation only | Qt modules qualified by ADR-0003 |
| `rust/bridge/` | Versioned C header, C++ facade and dedicated build target | Selected existing engine/orchestration units |

No package names or ABI shapes may be independently reinvented by sibling cards.
One bridge owner owns header/build changes. Domain/app forbid unsafe code; unsafe
is restricted to engine-sys, documented safe-wrapper glue and narrowly justified
native platform modules. Every unsafe block states pointer validity, aliasing,
threading and lifetime invariants. Enforce forbidden-dependency checks in later CI.

## 3. Domain model and engine port

These are semantic API contracts, not purported compilable Rust declarations.
The first implementation must encode them as typed values, not stringly typed JSON
passed through FFI. Externally serialized formats need a separate reviewed schema.

| Value | Required fields and invariants |
| --- | --- |
| `ArchiveId` | Worker-allocated opaque identity, never an address; not persisted across process restarts |
| `Generation` | Monotonic per-session epoch; reject overflow rather than wrap; advances before any operation invalidating entries |
| `Archive` | ID, generation, native source locator, actual format/nested-chain descriptors, capabilities, owned archive properties, open diagnostics and state; no borrowed handler |
| `EntryId` | ArchiveId + Generation + handler-chain position + engine item index (`u32`); names are NOT identity |
| `ArchiveEntry` | EntryId, lossless engine name, display text, kind (including unknown/link/alternate stream), optional unpacked/packed `u64` sizes, optional encryption flag, timestamps, attributes, checksum properties and extensible typed properties |
| `EngineText` | Owned sequence of 16-bit code units representing the retained UString contract; invalid UTF-16 is preserved. `display` is explicitly lossy and never a filesystem input |
| `NativePath` | Tagged Windows UTF-16 code units or Unix bytes; platform adapter validates tag, NUL restrictions and representability without Unicode normalization. Not interchangeable with EngineText |
| `PropertyValue` | Empty/absent, bool, signed/unsigned integer with original width/type tag, EngineText, timestamp, copied bytes, or Unsupported(original type tag); retain property ID. Never coerce unknown to zero |
| `Timestamp` | Original format/units, raw value and precision/definedness; optional normalized display instant. Do not discard FILETIME or filesystem precision in a mandatory Unix-seconds conversion |
| `CapabilitySet` | Built-in handler/codec identifiers plus per-format read/test/create/update, volume and property support; distinguish built capability from qualified application feature |

Raw archive filename bytes are included only where the handler actually supplies
them, with provenance; do not reconstruct them from display text. `EngineText` is
not evidence that arbitrary code pages work on Unix (`CPP/Common/StringConvert.cpp`).
Raw properties from `IArchiveGetRawProps` are copied during the valid call interval.
Large counts/offsets stay 64-bit where the engine uses them; signed archive offsets
remain signed. Bridge counts use checked conversion, never unchecked `usize` casts.

`ArchiveEngine` defines synchronous operations invoked only by its owning worker:

- `capabilities()` returns the matched build manifest and runtime format capabilities.
- `open(OpenRequest, OperationContext)` returns Archive plus diagnostics or an
  outcome without an open session. OpenRequest carries native source, probing
  options, explicit handler-scoped properties and operation-local code-page choice.
- `entries(ArchiveId, Generation, page_range, OperationContext)` returns owned
  snapshots; a page cannot outlive its memory owner but snapshots can outlive close.
  Using their EntryIds after close/reopen/update is rejected, never dereferenced.
- `extract(Selection, ExtractRequest, OperationContext)` and `test(Selection,
  OperationContext)` return OperationOutcome. Selection is All or validated indices
  from one session/generation/handler. Sort/deduplicate indices without silently
  changing user-visible name order; only C++ emits the engine all-items sentinel.
- `create(CreateRequest, OperationContext)` returns OperationOutcome and a native
  output locator, not a silently opened Archive. Requests retain typed format,
  method and scoped properties, input scan policy and destination policy. Opening
  the result is a later explicit operation. `UpdateArchive` stays the coordinator;
  arbitrary update/delete support is not implied by first creation support.
- `reopen(NameDecodeRequest, OperationContext)` is a later browsing capability,
  not part of initial list parity. Preserve `CAgent::CanReOpen` eligibility and
  rollback semantics when introduced. Invalidating attempts advance generation,
  including successful rollback; rollback failure makes the session unusable.
- `close(ArchiveId)` runs on the owner after active operations finish, releases
  resources and invalidates identity. Duplicate/stale commands return typed errors.

OperationContext contains task identity, cancellation observation, progress sink
and a typed interaction channel; it never contains Qt objects. Not every engine
path is interruptible. Code-page reopen currently passes a null callback in the
File Manager; do not advertise new interruptibility without characterization.

## 4. Engine facade, ABI and lifetime

ADR-0001 selects an internal versioned C ABI over a C++ orchestration facade.
`archive-engine-sys` is not a general COM binding. v1 is a source-tree-internal
matched build contract, not a stable third-party plugin API. A version/capability
handshake fails before creating a context on any mismatch.

Proposed ABI symbol prefix is `am_engine_v1_`. Operations are create_context,
destroy_context, capabilities, open, entries, extract, test, create, close and
result_destroy; introduce each operation only in the mandated stage. The future
header must declare exact widths/layouts, `struct_size`/ABI version, explicit C
calling convention (including 32-bit Windows), enum values with unknown handling,
and separate native-path/text buffers. No C++ STL, wchar_t, bool, exceptions,
PROPVARIANT or COM vtables in that header. Pointer lengths count elements of the
specified type; zero length permits null, nonzero length requires valid storage.

| Resource | Owner / valid interval | Release rule |
| --- | --- | --- |
| Opaque context/session | C++ facade; only owner worker may invoke/use | safe Rust wrapper schedules close and destroy on that worker; never `Box::from_raw` |
| CMyComPtr interfaces | C++ RAII; distinguish copied/borrowed/Attach references | matching Release, never Rust allocator |
| CCodecs, registration, loaded modules | facade runtime, longer-lived than all handlers/streams | no live reload; release dependents first, then CReleaser/CloseLibs cycle teardown |
| Input request buffers | Rust owns until synchronous ABI call returns | C++ copies any data retained after return; no stored borrowed Rust slices |
| Operation callbacks/user data | pinned stable operation allocation retained through callback quiescence | return only after all engine callbacks/codec workers have stopped using it |
| Open streams / volume chain | session-owned C++ RAII | retain after open when handlers require it; release only after handlers close |
| Output/callback streams | C++ RAII using existing callback rules | null stream retains skip/directory/link meaning; no assumed successful file write |
| Result handle and arrays | C++ owned immutable allocation; borrowed views valid until result_destroy | Rust copies needed values then destroys exactly once via facade |
| BSTR / PROPVARIANT / raw props | C++ matching allocator and RAII | initialize outputs, SysFreeString/clear even on failure; copy raw bytes before owner invalidation |
| Password | operation-private secret storage and transient C++ BSTR | no logging/persistence; minimize copies, clear controlled buffers best effort; do not promise engine-wide erasure |

If a handler retains a callback interface after an operation returns, that interface
must be a session-owned C++ adapter, not an operation-owned Rust pointer. Bind its
operation state only during a serialized active call, detach after callback
quiescence, and keep the adapter alive until the retaining handler releases it.
Prove this per interface in bridge tests; do not assume Open drops its callback.
Unexpected invocation without a bound operation returns a non-allocating failure,
never touches expired state. The facade call may not return while a callback still
uses Rust operation memory.

Destroying a context with active callbacks is forbidden. Public Rust ownership
exposes command handles, not transferable engine pointers; dropping a client handle
requests cleanup but cannot free live native state. Result destruction and session
cleanup remain on the worker. Raw FFI handles are neither Send nor Sync. Only
command channels and concurrency-safe interaction/progress/cancel state may cross
threads. No concurrent engine calls even across sessions initially (ADR-0002).

Catch C++ exceptions at every exported boundary AND callback adapter. Map allocation
failure separately; the error path must work without allocating a message. Rust
callbacks catch unwind when built with unwind support and return a bridge failure;
no panic or exception crosses FFI. Abort/OOM configurations cannot be caught: record
this in build qualification and never call it graceful cancellation. Bounds and
pointer validation cannot make arbitrary invalid caller pointers safe; the safe
wrapper is responsible for provenance and lifetime, the C ABI checks lengths,
nullability, tags, versions and ranges. All sizes and arithmetic must be checked.

## 5. Errors, progress, prompts and cancellation

`OperationOutcome` retains call status, open diagnostics, ordered per-item results,
warnings, completed/skipped counts and partial-effect information separately.
A successful HRESULT does not erase CRC or wrong-password item failure.

| Source | Required representation |
| --- | --- |
| HRESULT, S_FALSE, E_ABORT | Original numeric bits + category (engine failure/not recognized/cancelled as appropriate to operation); S_FALSE is contextual, not generic success |
| NExtract::NOperationResult | Preserve original numeric item result and known categories: data/CRC/header/wrong-password/unsupported-method; unknown values remain unknown |
| CArcErrorInfo | Error/warning flags, definedness, messages, tail/offset/size and nested-chain context |
| OS error | Native domain (Windows/errno), original code, operation and redacted path context; not every HRESULT is a Win32 error |
| Bridge validation / exception | StaleEntry, InvalidRequest, UnsupportedCapability, AllocationFailure, InternalFailure; keep distinct from archive corruption |
| Cancellation with writes | Cancelled plus observed completed/partial artifacts and cleanup outcomes; no rollback or latency guarantee |

Legacy CLI exit/output behavior is mapped by archive-cli after differential tests;
the library does not use exit code alone as its error model. Never label a wrong
password unless the engine reports it; data corruption is not proof of a password
error. Undefined password, defined empty password, supplied password and user
cancel are distinct replies per `CPP/7zip/IPassword.h:16-50`.

Task state is Queued -> Running <-> WaitingForReply -> Finishing -> one terminal
state (Succeeded, Failed, Cancelled). CancelRequested is an orthogonal sticky flag,
not terminal success. The first accepted terminal transition wins; a late cancel
after completion does not rewrite a successful operation's history.

ProgressEvent carries TaskId, sequence, phase, counter kind/unit (files, input bytes,
output bytes, engine-specific), optional total, optional completed and copied item
identity. Unknown remains unknown; phase changes and total corrections may reduce
a displayed percentage. Concurrent engine progress is synchronized and sequence
numbers are assigned at publication, not taken as evidence of engine causal order.
A bounded latest-progress slot may coalesce progress only. Item failures and terminal
outcomes are retained in an operation report (bounded batches/spooling for large
archives), never dropped to relieve UI backpressure. A storage failure fails the
operation explicitly; do not silently lose diagnostic evidence.

RequestReply contains TaskId, session generation, unique RequestId and one typed
question: Password, Overwrite or Volume. Replies use matching IDs and are accepted
once. Overwrite choices are only the measured legacy choices; invalid/stale replies
are rejected. The callback publishes a question, releases progress/mailbox locks
and waits on a reply-or-cancel condition. It must not hold a global initialization,
UI, or queue mutex while waiting. The single worker remains occupied, but reply
and cancel delivery run independently without needing that worker to process a
command. Engine-internal locks cannot be promised absent; replies MUST NOT reenter
the engine. An unavailable UI/CLI interaction consumer causes explicit cancellation
or interaction-unavailable failure, never a default overwrite or empty password.

Cancel sets an atomic flag, wakes pending questions and is checked at supported
callback/adapter boundaries, mapping to E_ABORT. Never terminate codec threads.
Shutdown stops accepting commands, requests cancel, resolves/wakes pending requests,
keeps callback state alive, waits for engine/codec quiescence, releases sessions and
results, tears down runtime, then joins the worker off the Qt thread. Qt destruction
must not synchronously wait on a callback waiting for Qt. If a retained path never
polls, report pending shutdown and wait; no fabricated bounded shutdown guarantee.
Minimal safe callback/cancel plumbing is necessary in the bridge; generalized task
scheduling/pause/UI infrastructure remains a later stage, not scope creep.

## 6. Filesystem and platform services

Initially the existing C++ scanner and extraction/update callbacks perform archive
I/O. The Rust filesystem port defines a future seam, not a second path-sanitizer
running ahead of and changing retained policy. Replace one characterized service
at a time; avoid two independent owners of output file closure or metadata.

Portable service operations include native path validation/conversion, enumeration,
metadata query (follow/no-follow explicitly), open/read/write/seek/size with partial
I/O, directory creation, metadata application, links, rename/replace, temp outputs,
settings and desktop invocation. Return capability/unsupported explicitly. Do not
promise transactional extraction or portable ACL semantics. OS resources live in
platform implementations or retained C++ until the service is replaced; domain
values never carry HWND/HANDLE, file descriptors, Registry keys or COM pointers.

- `platform/windows`: lossless UTF-16 native paths, long/UNC/device/reserved-name
  behavior, reparse/ADS/security/attributes/times and replace semantics; isolate
  Registry, console control and shell/OLE integration. Native Windows is canonical.
- `platform/linux`: byte paths, POSIX modes/links/timestamps and errno; validate
  actual filesystem features instead of inferring them from Linux alone.
- `platform/macos`: byte paths plus measured filesystem normalization/case and
  metadata behavior; native application/desktop integration separate from Linux.

Extraction safety tests use sandboxed malicious absolute/traversal/link/race inputs.
If legacy behavior conflicts with desired containment, block the affected card for
human decision; neither silently reproduce dangerous writes nor silently alter the
compatibility contract. No whole CPP/Windows deletion: FileIO and other units
already contain POSIX implementations. See M0 R02, R04 and R10.

Settings separate persistent ZIP UTF-8 creation preference (legacy default true)
from transient extraction/browsing code-page choice (Auto initially). Preserve
explicit parameter precedence and scoped property reset via SetProperties. No
password persistence. Settings migration must retain old values and require native
tests before changing storage; shell identities remain fork-specific.

## 7. Qt and retirement

Qt objects/models are constructed, updated and destroyed on the Qt thread. CXX-Qt
adapts owned snapshots, not engine references. Never pass a u64 identity/size through
QML JavaScript Number without a lossless adapter: use opaque string IDs and
lossless formatted/typed values, keeping arithmetic in Rust. Reject stale queued
updates by TaskId/generation; invalidate models on reopen and disconnect receivers
safely on shutdown. Password text stays in a short-lived interaction control, not
a shared observable history or general event stream.

Retire CLI printing/parsing first only after parity; retain the old executable as
oracle. Later retire one application policy helper at a time with differential
coverage. Qt replaces Win32 presentation only after browsing and operation parity;
Explorer COM remains a separate native integration product. FAR/SFX and specialized
bundles are retained and are not implicitly in replacement scope. Mature handlers,
codecs, crypto, C and assembly have no retirement milestone here. Any substantial
removal, GUI direction change or codec proposal requires its own human gate.

## 8. Evidence and limits

M2 is documentation only. No Rust workspace, facade, GUI, new license arrangement,
archive compatibility result or native CI pass is claimed. Existing source checks
and document/path review are recorded in the review handoff. M1 owns fixtures and
characterization; its reviewed coverage controls eligibility even where this
architecture names a future operation. Toolchain/package qualification and native
runtime validation remain explicit prerequisites in migration-stages.md.
