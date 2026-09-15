# Portable retained registration redirection without retained-source edits

Status: implementation specification (P3B, DEVELOPMENT scope only)

Decision owner: P3B `t_eb67a575`. This document supersedes the implementation
mechanism in `portable-retained-registration-seam.md` (P3 commit `eb2771f`, merged
locally at `ed6a0e0`). The operator rejected that mechanism because it adds an
accessor to `CPP/7zip/UI/Common/LoadCodecs.h` and `LoadCodecs.cpp`. The P3 document
remains a historical rejected-design record and is not implementation authority.

## 1. Decision and evidence level

Use per-translation-unit preprocessing to redirect the retained registration
call. Compile exactly the retained archive-registration translation units with:

- GCC and Apple Clang: `-DRegisterArc=ArchiveBridgeRegisterArc`
- MSVC: `/DRegisterArc=ArchiveBridgeRegisterArc`

Compile `CPP/7zip/UI/Common/LoadCodecs.cpp`, the bridge facade, and a new
bridge-owned registration shim **without** that definition. The shim records the
`CArcInfo` pointer and then calls the true retained `RegisterArc()` exactly once.
No retained source is edited. No linker wrapping, symbol alias, interposition,
weak reference, reserved identifier, or hard-coded C++ mangling is used.

This mechanism is viable. The declaration and each constructor call are changed
consistently within a registration translation unit, while the true declaration
remains available to the separately compiled shim. The repository's GNU make and
NMAKE rules permit exact-object recipes/flags; they do not force one flag set for
the complete build.

The following is established now:

- source archaeology identifies 54 selected registration translation units and
  60 active registrations in the retained `Format7zF` composition;
- all 54 were compiled locally with GCC 15.2.0 under the retained warning policy
  by adding a GNU make target-specific definition;
- every resulting registration object had an undefined reference to
  `ArchiveBridgeRegisterArc(const CArcInfo *)`, while an independently compiled
  shim defined that function and referred to the true `RegisterArc(const
  CArcInfo *)`;
- `LoadCodecs.o`, compiled without the definition, defined the true
  `RegisterArc(const CArcInfo *)` and did not refer to the shim.

The local experiment used scratch files under `/tmp/p3b-gcc*`; it changed no
repository source and is not qualification evidence. Apple Clang and MSVC are not
installed on this host, so their actual object files are not claimed as tested by
P3B. Their syntax and rule placement are specified below, but an implementation
must obtain exact-head native `macos-latest` and `windows-latest` evidence before
this mechanism is accepted on those platforms. A successful document review is
not that native evidence.

This remains DEVELOPMENT-only. `qualified_operations` remains the literal `0`.
No archive operation, GUI, desktop integration, installation, packaging,
signing, tag, release, or shared-branch merge is authorized.

## 2. Source-observed registration chain

The actual retained header is `CPP/7zip/Common/RegisterArc.h` (not
`CPP/7zip/Archive/Common/RegisterArc.h`). Its relevant behavior is:

1. `RegisterArc.h:8-27` defines `CArcInfo`; `Id` is the byte at line 11.
2. `RegisterArc.h:29` declares `RegisterArc(const CArcInfo *) throw()`.
3. `RegisterArc.h:44-50` creates a file-scope `static const CArcInfo` and a
   file-scope registrar whose constructor calls `RegisterArc(&g_ArcInfo)`.
4. The derived macros at lines 53-71 use that path. The decrement-signature
   variant at lines 73-78 mutates its signature and then calls the same function.
5. `LoadCodecs.cpp:112-124` owns `g_NumArcs`, `g_Arcs[72]`, and the true
   `RegisterArc()`. It currently drops registrations beyond 72 silently.
6. `LoadCodecs.cpp:791-846` copies the retained pointers into `CArcInfoEx` rows;
   it preserves the mature registration behavior but does not copy `Id`.
7. `LoadCodecs.cpp:892-894` sorts `CCodecs::Formats` by name. The interception
   must not alter construction or this sort.
8. `LoadCodecs.h:96-125` confirms that `CArcInfoEx` has no registration ID.
9. `CPP/7zip/Archive/ArchiveExports.cpp:13-28` owns a different registration
   table for a different product. It is not selected by this facade and is not a
   substitute for the `LoadCodecs.cpp` registrar.

The preprocessor operates on identifier tokens. It replaces the exact
`RegisterArc` token but does not change `CRegisterArc`, `g_RegisterArc`, or any
other longer identifier.

## 3. Exact selected registration translation units

`rust/bridge/makefile.gcc:30` includes the retained
`CPP/7zip/Bundles/Format7zF/Arc_gcc.mak`; its `ARC_OBJS` composition is assembled
at `Arc_gcc.mak:372-393`. The MSVC declaration includes the corresponding
`Arc.mak`, whose object groups begin at `Arc.mak:1`. The selected lists agree for
registration-bearing sources. `AvbHandler.cpp` and `LvmHandler.cpp` contain
registration macros but are intentionally not selected: GCC comments them out at
`Arc_gcc.mak:145-146`, and they are absent from `Arc.mak`.

The 54 selected registration translation units are:

| Retained object group | Translation units that receive the definition |
| --- | --- |
| `AR_OBJS` | `ApfsHandler.cpp`, `ApmHandler.cpp`, `ArHandler.cpp`, `ArjHandler.cpp`, `Base64Handler.cpp`, `Bz2Handler.cpp`, `ComHandler.cpp`, `CpioHandler.cpp`, `CramfsHandler.cpp`, `DmgHandler.cpp`, `ElfHandler.cpp`, `ExtHandler.cpp`, `FatHandler.cpp`, `FlvHandler.cpp`, `GptHandler.cpp`, `GzHandler.cpp`, `HfsHandler.cpp`, `IhexHandler.cpp`, `LpHandler.cpp`, `LzhHandler.cpp`, `LzmaHandler.cpp`, `MachoHandler.cpp`, `MbrHandler.cpp`, `MslzHandler.cpp`, `MubHandler.cpp`, `NtfsHandler.cpp`, `PeHandler.cpp`, `PpmdHandler.cpp`, `QcowHandler.cpp`, `RpmHandler.cpp`, `SparseHandler.cpp`, `SplitHandler.cpp`, `SquashfsHandler.cpp`, `SwfHandler.cpp`, `UefiHandler.cpp`, `VdiHandler.cpp`, `VhdHandler.cpp`, `VhdxHandler.cpp`, `VmdkHandler.cpp`, `XarHandler.cpp`, `XzHandler.cpp`, `ZHandler.cpp`, `ZstdHandler.cpp` |
| `7Z_OBJS` | `7z/7zRegister.cpp` |
| `CAB_OBJS` | `Cab/CabRegister.cpp` |
| `CHM_OBJS` | `Chm/ChmHandler.cpp` |
| `ISO_OBJS` | `Iso/IsoRegister.cpp` |
| `NSIS_OBJS` | `Nsis/NsisRegister.cpp` |
| `RAR_OBJS` | `Rar/RarHandler.cpp`, `Rar/Rar5Handler.cpp` |
| `TAR_OBJS` | `Tar/TarRegister.cpp` |
| `UDF_OBJS` | `Udf/UdfHandler.cpp` |
| `WIM_OBJS` | `Wim/WimRegister.cpp` |
| `ZIP_OBJS` | `Zip/ZipRegister.cpp` |

These produce 60 registrations: most produce one; `ChmHandler.cpp` and
`LzmaHandler.cpp` produce two each, `PeHandler.cpp` produces three,
`SwfHandler.cpp` and `UefiHandler.cpp` produce two each, and exactly one of the
two conditional registrations in `ZstdHandler.cpp` is compiled. Both Zstd
branches are in the same listed translation unit, so configuration does not
change definition coverage.

The definition must be attached to this explicit 54-object list, not to all of
`ARC_OBJS`, `AR_OBJS`, a directory wildcard, or global `CXXFLAGS`/`CFLAGS`.
`LoadCodecs.cpp`, `ArchiveExports.cpp`, codec registration sources under
`CPP/7zip/Compress`, the shim, and the facade do not receive it.

A bridge-owned build guard must compare the GNU and NMAKE registration-object
lists by basename and fail if they differ. It must also audit the compiled
composition before link:

- each of the 54 listed objects refers to the shim registrar;
- no other selected object refers to the shim registrar;
- `LoadCodecs` defines the true registrar and does not refer to the shim;
- the shim defines the redirected registrar and refers to the true registrar;
- the final runtime capture contains exactly the 60 frozen Q1 native names and
  IDs before the coordinator `Hash` row is considered.

The audit may ask each platform's compiler/symbol tool to resolve its own C++
symbols, but neither build nor source may contain a hard-coded mangled spelling.
Any selected-object drift, new registration TU, missing redirected reference, or
unexpected redirected reference is a build failure and returns to architecture
review.

## 4. Declaration, linkage, ODR, and static initialization

For a listed registration translation unit, preprocessing changes both the
header declaration and constructor call as if the source said:

    void ArchiveBridgeRegisterArc(const CArcInfo *arcInfo) throw();
    // ... file-scope constructor ...
    ArchiveBridgeRegisterArc(&g_ArcInfo);

This is consistent and helpful: the call has a declaration with the same C++
language linkage, parameter type, and exception specification as the shim
definition. That translation unit does not need the true registrar declaration
because it never calls the true registrar.

The new bridge-owned shim is compiled without the definition. It includes
`CPP/7zip/Common/RegisterArc.h`, which therefore declares the true
`RegisterArc()`. The shim defines ordinary C++
`ArchiveBridgeRegisterArc(const CArcInfo *) throw()` and calls the true
`RegisterArc(arcInfo)`. It needs no manual declaration of the true function and
must not use `extern "C"`; normal compiler-produced C++ linkage is used on each
platform without inspecting its spelling.

`LoadCodecs.cpp` is also compiled without the definition. Its retained include
continues to declare `RegisterArc`, and its retained definition at line 116 is
unchanged. The bridge facade and the shim's own translation unit must have a
source/build guard rejecting either command-line definition.

The mechanism does not add a second definition of `RegisterArc` and therefore
does not create an ODR conflict. It adds exactly one definition of the distinct
`ArchiveBridgeRegisterArc`. Each retained file-scope constructor remains in its
original object, with the same storage duration, link position, and constructor
body except for its callee. The shim synchronously forwards before returning, so
for every constructor invocation the true registrar observes the same pointer at
the same point in initialization. Consequently `g_Arcs` insertion order and
`CCodecs::Formats` construction are unchanged.

The shim's tracker must use only zero-initialized POD static storage: a fixed
pointer array, an unsigned count, and a sticky overflow flag. Static
zero-initialization completes before any dynamic initializer in any translation
unit, so the tracker is usable regardless of cross-translation-unit constructor
order. It must not use a global `std::vector`, lock, callback, allocator, or any
object requiring dynamic initialization.

## 5. Bridge-owned internal seam

Implementation adds these bridge-owned internal files:

- `rust/bridge/archive_bridge_registration.h`
- `rust/bridge/archive_bridge_registration.cpp`
- `rust/bridge/check-registration-seam.py`

The existing Rust facade contract test files may be extended as listed in the
owned-path section; no test-only retained source is added.

The internal header forward-declares `CArcInfo` and declares ordinary C++
functions for the shim and read-only snapshot access. These are not exported C
ABI and must not be added to frozen Q1 `archive_bridge_v1.h`.

The shim behavior is fixed:

1. For each call, if the recorded count is below 72, store the pointer and
   increment the count. Store a null pointer too; null is later a correspondence
   failure rather than an omitted observation.
2. If the count is already 72, set a sticky overflow flag. Do not write out of
   bounds and do not clear or wrap the count.
3. In both cases call the true `RegisterArc(arcInfo)` exactly once and return its
   `void` result. Tracking must never throw from a file-scope constructor.
4. Expose only read-only internal queries for count, indexed pointer, and
   overflow. They borrow module-lifetime pointers and transfer no ownership.

The old implementation at `rust/bridge/archive_bridge_v1.cpp:55-98` silently
stops recording after 72. That behavior is forbidden. If the sticky overflow
flag is set, context creation and every capability construction attempt must
fail with `ARCHIVE_BRIDGE_V1_ENGINE_FAILURE`; no result is published and all view
pointers remain null. The shim still forwards the overflow call, preserving the
retained registrar's behavior, but the facade refuses to represent an incomplete
capture. A null recorded pointer, count other than the frozen expected count, or
incomplete correspondence fails identically.

All snapshot reads occur after process static initialization and before any
handler unloading. The retained facade is built-in-only and does not enable
runtime format registration. If a future composition registers after the first
facade export, unloads handler storage, or needs concurrent mutation, stop and
return to architecture review; do not add locking or ownership by implication.
No `CArcInfo *` crosses the Q1 ABI or enters Rust ownership.

## 6. Exact build changes

### 6.1 GNU make: GCC and Apple Clang

In `rust/bridge/makefile.gcc`, remove
`-Wl,--wrap=_Z11RegisterArcPK8CArcInfo` and all private-mangling commentary. Add
the shim object to `BRIDGE_OBJS`. Define the exact 54-object
`REGISTER_ARC_OBJS` list and attach a GNU make target-specific variable:

    $(REGISTER_ARC_OBJS): CXXFLAGS += -DRegisterArc=ArchiveBridgeRegisterArc

The retained explicit recipes in `CPP/7zip/7zip_gcc.mak:493-711` expand
`$(CXXFLAGS)` for each archive target, so the addition reaches exactly those
objects. Other objects use unchanged flags. The explicit shim and facade recipes
at the bottom of the bridge makefile use ordinary `$(CXXFLAGS)` and must not add
the definition.

Linux continues to invoke:

    make -C CPP/7zip/Bundles/Format7zF \
      -f ../../var_gcc.mak -f ../../warn_gcc.mak \
      -f "$GITHUB_WORKSPACE/rust/bridge/makefile.gcc" \
      O="$RUNNER_TEMP/rebuild-facade"

macOS continues to invoke the same bridge makefile with Apple Clang settings:

    make -C CPP/7zip/Bundles/Format7zF \
      -f ../../var_mac_arm64.mak -f ../../warn_clang_mac.mak \
      -f "$GITHUB_WORKSPACE/rust/bridge/makefile.gcc" \
      O="$RUNNER_TEMP/rebuild-facade"

`CPP/7zip/7zip_gcc.mak:172-213` constructs per-target `CFLAGS`/`CXXFLAGS`, and
lines 221-227 establish object targets/output creation. The makefile already uses
GNU make conditionals and functions; the target-specific assignment is valid for
both retained GCC and Apple Clang invocations.

### 6.2 NMAKE: MSVC x64

Do not put `/DRegisterArc=ArchiveBridgeRegisterArc` in global `CFLAGS`.
`CPP/Build.mak:204-218` defines the per-object compile command macros, and
`CPP/7zip/7zip.mak:176-236` supplies inference rules when `MAK_SINGLE_FILE` is
not set. In `rust/bridge/makefile`, keep `MAK_SINGLE_FILE` unset and add explicit
target recipes only for the same 54 registration objects, grouped by their
retained source directory. Each recipe is the retained `$(COMPLB)` command with
the single appended option `/DRegisterArc=ArchiveBridgeRegisterArc` (equivalent
expanded form: `$(CC) $(CFLAGS_O1) -Yu"StdAfx.h" -Fp$O/a.pch $<
/DRegisterArc=ArchiveBridgeRegisterArc`); the Zip recipe also preserves
`$(ZIP_FLAGS)`. Explicit targets take precedence over the unchanged inference
rules used by every other object.

The bridge makefile must be interpreted from the retained bundle directory, not
from repository root. Correct the Windows workflow to the following shape:

    pushd CPP\7zip\Bundles\Format7zF
    nmake /NOLOGO /f "%GITHUB_WORKSPACE%\rust\bridge\makefile" \
      PLATFORM=x64 O="%RUNNER_TEMP%\rebuild-facade"
    popd

From that directory, the bridge makefile includes `Arc.mak` and
`../../7zip.mak`, exactly as the retained `Format7zF/makefile` does. Its explicit
bridge-owned source recipes add the repository-root include path and compile the
shim and facade without the registration definition. The current root invocation
at `.github/workflows/rebuild-ci.yml:121` has never passed the existing early
`!ERROR`; it must not be treated as evidence that the paths below that guard are
valid.

Removing the Windows `!ERROR` is **not** authorized by this design alone. It
requires all three of: this P3B mechanism implemented and proven in native CI;
the separate Windows `ARCHIVE_BRIDGE_V1_CALL`/retained `-Gr` calling-convention
item qualified; and a separate explicit human gate. Until then the guard remains
fail-closed.

## 7. Runtime correspondence and frozen oracle

The implementation must replace the current first-match
`RegistrationIdFor()` behavior at `archive_bridge_v1.cpp:372-385` with a checked,
all-or-nothing correspondence pass before publishing any capability row.

The normative expected values come from
`docs/ai-migration/qualification/engine-build.json`, status
`retained-native-reference`, SHA-256
`4e9a98a95daced0f0b20f4db9011793c934a51328a63780a473685808195704b`.
It contains 60 `format_registry` rows and 61 loaded/standalone format rows for
each of Darwin/arm64, Linux/x86_64, and Windows/AMD64. The companion frozen
summary is `native-observations.json`, SHA-256
`acc6a5c18c7dedcbf0d8ce51d4b31169114375aa23c4f169915267e58cadbb28`.
The Q1 normative header remains byte-identical at both committed locations,
SHA-256 `eabe714b31e2076735b8313c06618e5dbb3db4ea924cbef244b78a8b107ee26d`.
Tests read these files; they never rewrite or regenerate expected values from a
new facade.

Before any row is published, prove:

- tracker overflow is false, the captured count is 60, every pointer/name is
  non-null/non-empty, and captured names are unique;
- every captured `CArcInfo` matches exactly one pre-`Hash` `CCodecs::Formats` row
  by case-sensitive name, and every such format consumes exactly one capture;
- each emitted native registration ID is the matched `CArcInfo::Id` widened to
  `uint32_t`, never a fallback;
- after `Codecs_AddHashArcHandler`, exactly one additional row named `Hash`
  exists and it alone reports the absent sentinel `256`;
- no native row reports 256 and `Hash` reports no native byte;
- format count and row order, runtime indices, names/extensions, flags, effective
  time flags, reader/writer presence, codec metadata, and hasher metadata equal
  the applicable frozen Q1 record;
- the before/after table comparison shows the candidate has exactly the same 61
  ordered format tuples as the current accepted Linux facade/frozen reference.

Registration order is used only to prove complete capture and forwarding. It
must not reorder `CCodecs::Formats`; the retained name sort and coordinator-added
`Hash` placement remain the observable table order.

Any correspondence error returns `ARCHIVE_BRIDGE_V1_ENGINE_FAILURE`, leaves
`*result` null, leaves all borrowed view pointers null, and destroys temporary
storage exactly once. Never publish a partial arena.

## 8. Required positive and negative controls

Factor two testable layers: a C++ structural correspondence helper over explicit
captured pointers and format rows, and a Rust/reference verifier that compares
the complete emitted table with frozen Q1 JSON. Production passes the real
read-only capture. Tests pass in-memory copies; they never mutate retained
statics or committed evidence.

Positive controls must prove:

1. all 54 intended objects were compiled with the definition and only those;
2. the real capture contains 60 unique native registrations and consumes every
   pre-`Hash` format exactly once;
3. the emitted ordered 61-row table, all IDs and reader/writer metadata match the
   applicable frozen Q1 record;
4. repeated enumeration is stable and does not change capture or format order;
5. exactly `Hash` reports 256;
6. the Q1 C export surface remains exact and `qualified_operations == 0`.

Each negative control operates on an in-memory copy and must make verification
fail, with no partial result:

1. change one native registration ID (`wrong id`);
2. delete one native row (`missing row`);
3. duplicate one native row/name (`duplicate row`);
4. swap two rows while keeping their indices internally plausible (`reordered rows`);
5. change a native row to 256 (`false 256`);
6. assign a native byte to `Hash` (`native id on Hash`);
7. append an unknown non-`Hash` row (`phantom format`).

Also test tracker overflow at the 73rd call, an in-range null pointer, duplicate
captured names, missing/duplicate `Hash`, and a deliberately mis-scoped compile
flag. The old strings `--wrap`, `_Z11RegisterArcPK8CArcInfo`, `__real_`, and
`__wrap_` must be absent from production bridge/build inputs; a deliberate
bad-input source-guard control containing each must fail.

## 9. Owned and forbidden paths

One later coder card owns only:

- `rust/bridge/archive_bridge_v1.cpp`;
- `rust/bridge/makefile.gcc` and `rust/bridge/makefile`;
- new bridge-owned shim, internal header, verification scripts, and bridge-only
  tests under `rust/bridge/`;
- existing Rust facade contract tests/support only as needed for frozen-reference
  and negative controls;
- `rust/bridge/build-manifest.py` only for truthful portable evidence;
- `.github/workflows/rebuild-ci.yml` only for migration exact-head evidence;
- a directly corresponding DEVELOPMENT evidence document under
  `docs/ai-migration/`.

Forbidden paths include all of `C/`, `CPP/`, and `Asm/`; every golden, fixture,
and Q1 evidence file; `docs/ai-migration/qualification/archive_bridge_v1.h` and
`rust/bridge/archive_bridge_v1.h`; codec/encryption/handler logic; Rust public ABI
bindings; CLI and Qt/QML code; legacy workflows; installer/registry/service,
packaging/signing/release configuration; tags; `dev-main`; and shared history.
Build commands may compile retained files but may not edit them.

## 10. Verification and evidence required from implementation

Local Linux implementation verification must run and record these commands from
a fresh committed tree:

    git diff --check
    python3 rust/tests/check_boundaries.py
    python3 rust/tests/test_boundaries.py
    cargo +1.97.1 fmt --manifest-path rust/Cargo.toml --all -- --check
    cargo +1.97.1 build --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt
    cargo +1.97.1 test --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt
    cargo +1.97.1 clippy --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt --all-targets -- -D warnings
    cargo +1.97.1 build --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt --features archive-engine/facade
    cargo +1.97.1 test --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt --features archive-engine/facade
    cargo +1.97.1 clippy --manifest-path rust/Cargo.toml --locked --workspace --exclude archive-qt --all-targets --features archive-engine/facade -- -D warnings
    python3 docs/ai-migration/qualification/check-layout.py --output <fresh-layout-dir>
    python3 rust/bridge/build-manifest.py --output <fresh-facade-manifest-dir>
    python3 docs/ai-migration/qualification/validate.py
    python3 .github/tests/release_version_test.py
    python3 .github/tests/change_notice_test.py
    python3 .github/tests/lang_files_test.py
    python3 .github/tests/shell_ext_identity.py
    python3 .github/tests/shell_ext_lang_reload.py
    bash .github/tests/release_notes_test.sh

The makefile facade target must invoke
`python3 rust/bridge/check-registration-seam.py` with the selected object
directory and platform symbol-tool mode before link. Its positive object-scope
audit, deliberate mis-scope failure, overflow test, seven correspondence
mutations, source guard, and bad-input guard are mandatory parts of the recorded
facade self-test. Documentation-only P3B does not claim those future
implementation tests.

Run `.github/workflows/rebuild-ci.yml` at the exact candidate SHA. Acceptance
requires all six jobs to conclude `success`:

- `Rust workspace / ubuntu-latest`
- `Rust workspace / windows-latest`
- `Rust workspace / macos-latest`
- `Retained facade probe / ubuntu-latest`
- `Retained facade probe / windows-latest`
- `Retained facade probe / macos-latest`

Facade steps must no longer use `continue-on-error` to turn a failed build into a
green acceptance. Evidence upload remains `if: always()`. Each facade artifact
must include exact commit/ref, platform/architecture, compiler/build/linker
versions, full commands and logs, compiled-object scope audit, runtime registration
count/correspondence, all negative controls, ordered before/after format tables,
exact export listing, binary/header/build-input digests, and unchanged DEVELOPMENT
notices. The reviewer independently downloads and hashes artifacts.

Native Windows evidence must use MSVC/link.exe on `windows-latest`; Wine, MinGW,
or Linux cross-compilation is not Windows evidence. macOS evidence must use Apple
Clang on `macos-latest`. These runs establish build portability and self-owned
contract behavior only, not deferred S2a/B08 qualification or archive semantics.

Preservation evidence must record a changed-file allowlist and before/after hashes
showing no change under `C/`, `CPP/`, `Asm/`, frozen Q1 artifacts, codec or
encryption logic, or legacy workflows.

## 11. Stop and rollback conditions

Stop implementation and return to architecture review if:

- the explicit 54-TU set cannot be reproduced from the selected retained object
  composition, or GNU/NMAKE sets differ;
- any registration constructor bypasses the shim or any non-registration object
  receives the definition;
- forwarding changes constructor order, pointer identity, `g_Arcs`, format count,
  sorted order, metadata, or reader/writer factories;
- native registration exceeds 72, contains null/duplicate names, or does not map
  one-to-one to exactly 60 non-`Hash` rows;
- `Hash` is natively registered, another row legitimately lacks a native ID, or
  frozen Q1 disagrees with the candidate;
- Apple Clang or MSVC cannot express the exact per-object build without editing
  retained source, or native exact-head CI does not pass;
- correctness requires a retained-source/header/golden edit, a fallback ID,
  mangled symbol, linker interposition, weakened warning/failure policy, or
  architecture change;
- the same substantive implementation/review problem survives two attempts.

Do not weaken a guard, update a golden, generate expectations from the candidate,
or map an unmatched row to 256. Rollback is deletion of bridge-owned seam files
and restoration of the four migration-owned facade/two-build/workflow files; no
retained file or persistent archive state is migrated.
