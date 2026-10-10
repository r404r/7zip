# Q1 internal ABI v1 contract

Status: Q1 contract candidate, pending independent review. Not a runtime ABI PASS.
Task: `t_f4d107ea`. The normative declaration artifact is
[archive_bridge_v1.h](archive_bridge_v1.h); it is not a production implementation.

## Public naming amendment

The operator authorized Q1 to choose a new non-secret naming rule and synchronize
all affected specifications, with independent review and uniform downstream use.
The authorization is recorded in the task comment thread; it is not a notification
wake or inferred consent. This document chooses a NEW namespace, not a recovery of
the previously obscured proposal.

- Exported C functions: `archive_bridge_v1_` followed by the operation in lower
  snake case.
- C typedefs and struct tags: `archive_bridge_v1_` followed by the type in lower
  snake case; opaque handles end in `_context`, `_session`, or `_result`.
- Preprocessor constants: `ARCHIVE_BRIDGE_V1_` followed by upper snake case.
- Header filename for the future production implementation:
  `rust/bridge/archive_bridge_v1.h`.
- ABI major is the literal integer `1`; a breaking change requires a new namespace
  and coordinated reviewed header/sys adapter, not reinterpretation of v1 memory.
- No unversioned aliases, historical aliases, compiler-mangled exports or COM
  entry points may be used by `archive-engine-sys`.

The exact reserved function names are:

| Name | Earliest exposure |
| --- | --- |
| `archive_bridge_v1_handshake` | Before any context allocation |
| `archive_bridge_v1_create_context` | S2 internal qualification |
| `archive_bridge_v1_destroy_context` | S2 internal qualification |
| `archive_bridge_v1_capabilities` | S2 internal qualification |
| `archive_bridge_v1_open` | Qualified open/list |
| `archive_bridge_v1_entries` | Qualified open/list |
| `archive_bridge_v1_close` | Qualified open/list |
| `archive_bridge_v1_result_destroy` | S2 internal qualification |
| `archive_bridge_v1_extract` | Qualified extraction only |
| `archive_bridge_v1_test` | Qualified testing only |
| `archive_bridge_v1_create` | Qualified creation only |

`reopen` is not introduced by v1 listing. A reserved name is not an implementation
or permission to expose its operation. Unsupported operations fail before effects.
S1/S2 and later workers must consume the independently reviewed Q1 commit, not
select another prefix. The new naming text takes precedence over the earlier
proposal retained as historical context in architecture-target.md and ADR-0001.

## Unchanged normative constraints

[Target architecture](../architecture-target.md) sections 2–5 and
[ADR-0001](../adr/0001-retained-engine-facade.md) continue to own domain models,
resource lifetimes, callback quiescence, serialization, error distinctions and
staging. This amendment does not substitute another schema or C++ interface.

## Declaration scope and versioning

The header fixes revision 1 for capabilities, context lifetime, open, paged entries,
close and result destruction. Extract/test/create names are RESERVED, not exports
in this revision; their request/result/callback extensions are introduced with a
new matched header revision in their mandated stages, after the corresponding
behavior gates. No opaque JSON requests or placeholder implementations may stand
in for those extensions. In particular overwrite choices must not be invented
before overwrite characterization. Reopen is separately gated. This follows the
staged operation introduction in architecture-target.md, rather than exposing
unqualified write operations early.

The C11-compatible header is the spelling/field-order/type/constant authority;
the prose below supplies semantics. Rust declarations use `repr(C)`, fixed-width
integer fields and `extern "C"`. Function pointer fields use the exact nullable
`Option<unsafe extern "C" fn(...)>` form where absence is permitted. There are no
C enums, C bools, wchar_t, STL layouts, packing pragmas, compiler bitfields, unions
with inactive borrowed pointers, or caller-selected allocators. All exported and
callback functions explicitly use `__cdecl` on Windows, overriding the retained
engine's `-Gr` default. Q1 native targets are 64-bit little-endian Linux x86_64,
Windows x64 MSVC and macOS arm64; the macro also specifies 32-bit Windows calling
convention but does not qualify or enable a 32-bit target.

`check-layout.py` parses every struct field, compiles/runs C11, C++17 and Rust 2024
probes and compares every size, alignment and field offset. The generated probes
and actual compiler logs are evidence, not a dummy engine or a substitute for S2a
ABI export/calling-convention, exception and lifetime tests. Natural platform
alignment applies; changing flags such as packing or short enums is forbidden.
No struct is serialized directly to disk or transferred between machines.

## Handshake, initialization and errors

Every outer request/view/callback envelope carries the declared `struct_size` and,
where declared, `abi_major=1`. Size must equal the matched declaration exactly;
larger sizes are not silently accepted. All reserved fields and inactive payloads
are zero. Unknown input tags, unsupported flags and out-of-range conversions fail
before effects with InvalidRequest or UnsupportedCapability; unknown output
property/native error tags remain owned Unsupported/raw values, never zero.
Boolean fields accept only 0 or 1. Undefined values are not assumed false or zero.

The caller supplies `expected` and writable `actual` to `handshake` before
`create_context`; every info field must match: major, revision, pointer width,
target (1 Linux x64, 2 Windows x64 MSVC, 3 macOS arm64), endian marker (1), raw
32-byte SHA-256 of the exact header bytes and build identity digest. Recheck in
create_context, so skipping handshake cannot create an incompatible context.
Mismatch is a non-allocating bridge status. The actual record can describe the
loaded build on mismatch, but it never grants fallback compatibility.

The build identity digest covers only the canonical input identity object from
engine-build-schema.json (UTF-8, sorted keys, compact JSON, no final newline).
Artifact hashes and this digest itself are outside that object, avoiding a
self-referential library hash. The loader receives an explicit application-owned
library location and expected identity; never mutate PATH/LD_LIBRARY_PATH globally
or search for an arbitrary system facade. No external engine plugin discovery.

Return status is int32_t with exact macros 0–10 in the header. It is NOT an
HRESULT or CLI exit status. Engine HRESULT/Win32/errno numeric bits live in ordered
diagnostics with their domain; retain S_FALSE as a contextual engine outcome,
not success. CArcErrorInfo is represented explicitly by `arc_error`, preserving
definedness, original error/warning flags, ErrorFormatIndex (-1 sentinel), tail,
unexpected end, ignore-tail, and separate error/warning messages. `chain` retains
format, item count, signed offset, property snapshots and per-chain diagnostics.
`non_open_error` survives a failed open without a session. Never infer wrong
password from a corruption message or an exit status. Later operation results
must preserve original NOperationResult values independently of call status.

All output handles initialize to null and views to zero before effects, retaining
their caller-supplied size/version. A failed open may return a result containing
diagnostics but no valid archive_id/generation. Allocation failure can return only
the non-allocating status and no result. Every exported boundary and callback
adapter must catch C++ exceptions; Rust callback unwind is caught inside Rust.
The qualified Rust policy is panic=unwind; OOM/abort cannot be promised catchable.

## Text, properties and paths

`text` is a borrowed view of uint16_t code units, including ill-formed UTF-16;
`bytes` counts uint8_t elements. Empty views permit null; nonempty require valid,
aligned, initialized storage and checked count/byte-size conversion. No view
implies a NUL terminator. A view cannot establish arbitrary-pointer validity:
safe Rust provenance and lifetime checks remain mandatory.

`path.tag=1` uses windows_units only; `tag=2` uses unix_bytes only. The inactive
view is null/zero. Reject wrong-host tags and embedded NUL, and reject a path that
the retained native path conversion cannot represent. Never normalize or use
lossy display text to recover a path. Volume paths follow the same rule.

`value` has exactly one active payload selected by the header tag. For Bool,
unsigned_value is 0 or 1. Integer widths are 8/16/32/64 and range checked. Signed
and unsigned values retain the original property type; text/bytes are copied into
the result arena. Timestamp format/precision/raw components preserve the source
representation without mandatory normalization. In revision 1, format=1 denotes
FILETIME raw low 64-bit value; precision is original wReserved1, and raw_high
preserves wReserved2 in bits 0–15 and wReserved3 in bits 16–31 (upper bits zero).
This retains sub-100ns metadata from PropVariant.h:93–110 without interpreting or
correcting Get_Ns100. Future distinct source time formats require an explicit
reviewed mapping rather than reinterpreting format=1. Undefined timestamps have
defined=0. Unsupported contains original_type and no fabricated value.

Property source_kind is 0 for PROPVARIANT and 1 for copied IArchiveGetRawProps;
raw properties use the Bytes tag and retain the original raw type in original_type.
The two property sources therefore never collapse into one ambiguous numeric tag.
Archive and entry property IDs remain the numeric engine PROPID; present Empty
differs from a missing property record. This property projection is not a new
domain schema: the safe adapter constructs the exact ArchiveEntry/PropertyValue/
Timestamp model in architecture-target.md section 3, including kind, optional
sizes/encryption, attributes and checksums. Raw IArchiveGetRawProps data must be
copied with source type/provenance before invalidation; support cannot be claimed
where the handler does not supply it.

## Open and paging

The caller allocates nonzero archive_id and generation, never reusing an identity
within the process; reject overflow, not wrap. A context checks duplicate IDs,
generation and active state. Sessions may not be guessed from names or pointers.
`open_type` projects COpenType directly: FormatIndex=-1 means the retained
automatic selection, spec flag bits 1/2/4 mean frontal/tail/mid, booleans retain
their source meaning, max_start_offset is unsigned with separate definedness.
The retained default is forced=7, main=1, wrong-extension=0, unknown-extension=7,
recursive=1, can_return_arc=1, other booleans=0. Do not zero-initialize these
defaults as a substitute. `types` and `excluded_formats` retain COpenOptions
ordering and index validation against this runtime's capability table. Initial
source input is a native file path; stdin/custom streams are not implicit support.

Scoped properties carry separate scope/name/typed value. Apply via SetProperties,
including the empty reset behavior, never global concurrent mutation. The
operation-local filename code-page selection is encoded as the characterized
handler-scoped property with explicit-option precedence in the safe adapter;
Auto omits the override. No generic Rust decoder or implicit ACP substitution.
Only characterized property names/types can be enabled by the application; the
transport does not authorize every possible retained handler option.

Page requests validate archive_id, generation, chain_position and checked
first+count against the engine item count before any indexing; engine item_index
remains uint32_t. Count=0 yields an empty result, not the all-items sentinel.
Returned entries retain full identity and owned property/name snapshots. Close
invalidates the session and later entries requests, not already owned Rust copies.
Stale and duplicate close commands return StaleEntry. Initial global execution is
serialized even across contexts; only one owning worker invokes context, result
and session operations. Context/result handles are neither Send nor Sync.

## Callback and allocation lifetime

Rust owns requests and the operation allocation through the synchronous call and
callback quiescence. The facade must copy anything needed after return. C++ owns
contexts, sessions, retained streams/handler callback adapters and immutable result
arenas. Rust copies result views before result_destroy on the owner worker; never
use Box::from_raw, free/delete or Rust allocators on a native handle. Result
destruction checks owner context and exactly-once ownership. Context destruction
returns Busy while sessions, results or callbacks are live; wrapper cleanup closes
and destroys dependents first. Invalid arbitrary pointers remain unsafe caller
misuse, not something status checks can make safe.

The cancellation callback is required and returns only 0/1; its user data may be
null only if the function does not dereference it. Progress callback absence means
no progress consumer, not missing cancellation. Progress can arrive concurrently
from engine threads, carries actual optional files/bytes/engine counters and must
be synchronized by the Rust adapter. Phase/sequence assignment and coalescing
remain the app protocol, not a fabricated engine total.

The question callback is optional; absent consumers explicitly fail interaction,
never supply an empty password or an overwrite default. Its output echoes the
request_id and exact reply kind. Defined empty password (kind=3, length=0),
undefined password (kind=2), cancellation (kind=1), unavailable (kind=0), and a
native volume locator (kind=4) are distinct. Question task/archive/generation IDs
bind the Rust request/reply routing. The callback's returned views point into
operation-owned storage retained until the enclosing ABI call returns; the C++
adapter copies them immediately. Password storage is private, never in diagnostic
or progress logs; clear controlled buffers best effort, not an engine-wide erasure
claim. Release mailbox/progress locks while waiting; delivery/cancel must not
depend on the engine worker processing another command or reentering the engine.

Session-retained callback interfaces are C++ adapters, not expired Rust pointers.
Bind operation state only while an operation is active and detach after all codec
activity is quiescent. Unexpected callbacks when unbound return a non-allocating
failure. Shutdown requests cooperative cancel, wakes questions, waits without
terminating codec threads, releases handlers/streams/results, then tears down the
runtime. No bounded cancellation/shutdown guarantee is introduced by the ABI.

## Capabilities and qualification boundary

Capability formats preserve runtime index, CArcInfo's registration byte widened
to uint32_t (256 explicitly means absent, not a fabricated native ID), effective
CCodecs flags/time flags, actual reader/writer factory presence, names and
extensions. Writer presence is not proof of every create/update property. Methods
and hashers retain uint64_t IDs and factory availability, filter status and digest
size. These are built capabilities, distinct from qualified_operations: initial
Q1 is 0; bit 0 capabilities, 1 open/list, 2 extraction, 3 testing, 4 creation may
only be enabled by the later reviewed application gates. Unknown bits are rejected.

The Hash archive handler is added by Codecs_AddHashArcHandler in HashCalc.cpp,
not exported as a CArcInfo slot by Format7zF. Preserve it; the matched reference
manifest distinguishes the raw library registry from coordinator-added formats.
Indices are local to the matched CCodecs table, not stable across products, sort
orders or builds. Match comparison records by name/actual registration identity,
not coincidentally equal row indices. Raw registered TimeFlags from the library
observer and effective CCodecs TimeFlags are separately recorded: the built-in
LoadCodecs path leaves TimeFlags at its constructor default, while the dynamic
path obtains the exported property. Do not repair that retained behavior or use
the raw metadata to change timestamp policy in Q1/S2a; future write/GUI policy
remains subject to native characterization and the relevant behavior gates.

S2a must produce the actual matched facade build manifest, verify exported symbols,
explicit library loading/handshake failure, registration retention after linkage,
and exercise failure injection, lifetime/allocator boundaries and callbacks on
native platforms. Q1 declaration and CLI evidence do not stand in for those tests,
nor for B01–B08 feature characterization, Qt qualification or distribution approval.
