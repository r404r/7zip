# ADR-0001: retain the full engine behind a versioned C facade

Status: proposed for independent M2 review. Implementation is gated by reviewed
M1/M2, M3 and the qualification steps below. No distribution approval is implied.

## Context and evidence

The mature engine is not equivalent to the public-domain C decoder SDK.
`CPP/7zip/Archive/IArchive.h:317-328` provides input archive operations;
IOutArchive and update callbacks in the same header separately define writing.
`CPP/7zip/UI/Common/OpenArchive.h:117-143` includes probing, streams, properties and
callbacks; CArcErrorInfo at 149 includes more than a success flag.
`CPP/7zip/UI/Common/Extract.cpp` and `Update.cpp` coordinate filesystem policy
above handlers. See [M0 seams and licensing](../archive-engine-boundaries.md).

`CPP/7zip/Bundles/Alone2/makefile.gcc:9` includes Format7zF/Arc_gcc.mak;
its UI_COMMON_OBJS at 48-68 are distinct from console entry/printing at 70-81.
The shared arc fragment includes C/C++, crypto, CPU/assembly options and portable
implementations under CPP/Windows. A replacement limited to C/7z.h loses semantics.

## Decision

Q1 amendment: human authorization on task `t_f4d107ea` permits a new public
namespace, `archive_bridge_v1_`, replacing the earlier proposal below. The old
spelling is neither inferred nor recovered. See [ABI v1](../qualification/abi-v1.md)
for the naming contract; downstream implementations consume its reviewed commit.
This does not approve production linkage or change the retained-engine direction.

Use an internal versioned C ABI (`am_engine_v1_`) implemented by a narrow C++ RAII
facade. Rust has a private unsafe sys crate and a safe ArchiveEngine implementation.
The ABI carries fixed-width typed values, explicit native paths and engine text,
opaque owner-bound handles and copied result snapshots, never COM vtables or
C++ standard-library layouts. [Target architecture](../architecture-target.md)
sections 3-5 define the model, entry identity, ownership and callback contract.

Retain CArchiveLink-based probing and selected UI/Common orchestration, including
SetProperties, scanning, extraction/overwrite/metadata, and UpdateArchive. Reuse
handler properties rather than decode names in Rust. Keep mature format/codec/
encryption code and its threading intact. Do not FFI into Main2, install console
signal handlers from the library, or link native GUI launchers indiscriminately.

v1 requires matched facade header/library and handshake, not permanent binary
compatibility for external consumers. Add operations in sequence: capabilities /
open / owned entries / close, then extract, test, create. Test remains retained
extraction machinery with testMode, not a separate decoder. Non-qualified operations
report UnsupportedCapability before effects; legacy products continue to supply
their existing features. Absence of qualified new-app support is not a claim that
the underlying handler lacks that feature.

### Capability and build manifest contract

The candidate local qualification target is an internal shared facade library
(`.dll`, `.so`, `.dylib` by platform), with matching C++ runtime/toolchain and
explicit loader location owned by the application build. This is a test/build
arrangement, not a final installer/linking/license decision. No production linkage
or distribution proceeds before the actual selected-input license audit. Do not
claim dynamic linking alone satisfies LGPL or Qt obligations.

The initial built-in capability reference is the full Alone2/Format7zF composition
at the reviewed oracle commit, not a hand-selected smaller codec set. Windows
qualification compares the actual native oracle product as well; differences
between products are recorded, not hidden behind a generic '7z compatible' claim.
External codec/plugin discovery is not exposed in v1. Legacy plugin-capable products
remain intact. Broadening new-app support to plugins requires its own loader trust,
module lifetime and parity work; it is not silently removed from replacement scope.

Before the bridge build, commit a machine-readable build manifest with:

- schema version, oracle and facade commit, target OS/architecture, compiler and
  runtime versions, Rust target/toolchain, ABI/header revision and build mode;
- every selected translation unit and transitive make-fragment input, defines,
  ST/MT and assembly/CPU flags, excluded UI/console objects and rationale;
- format IDs/names, read/create/update flags, codec/method and hash IDs from actual
  registration/capability enumeration, plus qualified application operations;
- plugin/loading policy, selected object/package license and notice provenance,
  artifact digest, linked-library/runtime inventory and exact reproducible commands.

Generate actual object membership from the real build rather than copying a
speculative list from this ADR. Compare manifest capabilities with native oracle
`i` output and controlled fixtures; output text alone cannot prove every handler
works. Link registration units deliberately so dead stripping does not silently
remove handlers; test the resulting registry. Freeze initialization before any
requests. Do not mutate global code-page/path options per concurrent job.

### Failure containment

C++ catches exceptions and returns structured outcomes; Rust panics cannot unwind
through C. Callback state survives all codec activity. Release handlers/streams
before codecs/modules and honor CCodecs::CReleaser's library-cycle teardown
(`CPP/7zip/UI/Common/LoadCodecs.h:320-334`). No live reload. Native names are not
lossy strings. Full ABI layout and fault-injection tests are required before a safe
Rust interface may expose operations to production callers.

## Alternatives considered

1. Direct cxx bindings to handler interfaces: attractive C++ integration but would
   expose a wider reference/COM/property ownership surface and still need the same
   policy adapter. Not selected for engine v1. CXX-Qt remains selected for Qt.
2. CLI subprocess as production engine: useful oracle and possible separately
   justified isolation strategy, but text parsing, interactive prompts, globals
   and cancellation are not the target structured in-process API. Retain for tests.
3. Universal C SDK wrapper: rejected because multi-format/orchestration equivalence
   is absent. No codec rewrite to make the FFI easier.

## Consequences and qualification

Extra marshalling and a manually reviewed header are costs. Shared ABI layouts,
explicit allocation, version checks and one semantic model isolate them. New ABI
fields need coordinated header/sys/safe-wrapper tests; no parallel unowned edits.
Performance optimization/zero-copy comes only after correctness and measured cost.

Qualification requires native Windows/Linux/macOS matched builds, registration
manifest comparison, open/list multi-format/volume/Unicode/property cases, repeated
open/close and failed-open cleanup, callback lifetime and allocation-failure tests,
partial stream I/O, ABI size/alignment/calling convention checks, and sanitizers
where supported. Production extract/create additionally need M1 overwrite, password,
metadata and partial-output evidence. A Windows cross-build or Wine is not native
compatibility evidence.

If selected licensing is unclear or the internal shared target cannot retain
necessary orchestration without semantic changes, block the affected qualification
card with actual evidence and alternatives; do not silently shrink features or
change architecture. M2 selects the seam without asserting those future checks
have passed. See [migration stages](../migration-stages.md).
