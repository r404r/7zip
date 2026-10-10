# Portable retained-facade registration seam

Status: implementation specification (P3, DEVELOPMENT scope only)

Decision owner: P3 `t_2c915e62`. A later implementation card may implement this
mechanism but must not choose a different registration identity or attachment
scheme without returning to architecture review.

## 1. Decision and boundary

Use a read-only accessor over the retained built-in registration table already
owned by `CPP/7zip/UI/Common/LoadCodecs.cpp`. Remove all linker interception from
the facade. The same source-level accessor is compiled normally by GNU C++ on
Linux, Apple Clang on macOS, and MSVC on Windows; it does not name or wrap a C++
linker symbol.

The retained table remains the single source of truth. `RegisterArc()` keeps its
existing behavior and order. The accessor exposes each stored `const CArcInfo *`
by registration index after static initialization; it neither installs a hook
nor changes the table. The facade builds a checked, call-local correspondence
between that snapshot and the sorted `CCodecs::Formats` rows. It emits the
original `CArcInfo::Id`, widened to `uint32_t`, only after proving a one-to-one
name correspondence. The separately coordinator-added `Hash` row remains the
only row with registration ID `256`.

This is the smallest portable mature-engine seam because the information is
already retained in `g_Arcs`; only its read access is missing. It avoids changing
`CArcInfoEx` layout, copying registration metadata into every `CCodecs` instance,
or intercepting static constructors. It also avoids adding any ABI symbol to
`archive_bridge_v1.h`: the accessor is an internal C++ build seam and the frozen
Q1 C ABI remains byte-for-byte unchanged.

This decision is DEVELOPMENT-only. `qualified_operations` remains the literal
`0`; the Rust workspace still has no runnable archive CLI target; and no open,
list, extract, test, create, password, overwrite, path, registry, installation,
package, signing, notarization, tag, or release operation is enabled.

## 2. Source-observed call chain and exact anchors

The design follows these source anchors in the P3 base tree
`286b12aa4b2d6312dc9058ff5658a5b9e10dee7a`:

1. `CPP/7zip/Common/RegisterArc.h:8-27` defines `CArcInfo`. Its `Byte Id` at
   line 11 and its name/factory fields have static-storage backing in handler
   translation units.
2. `CPP/7zip/Common/RegisterArc.h:44-50` makes one `static const CArcInfo`
   and one static registrar per `REGISTER_ARC_R` use. The registrar constructor
   calls `RegisterArc(&g_ArcInfo)`.
3. `CPP/7zip/Common/RegisterArc.h:73-78` has the decrement-signature variant;
   it still calls the same registrar after its deliberate signature mutation.
4. `CPP/7zip/UI/Common/LoadCodecs.cpp:112-124` owns the facade build's retained
   registration table: `g_NumArcs`, `g_Arcs[72]`, and `RegisterArc()`. The
   function appends in constructor-call order and silently retains at most 72
   pointers.
5. `CPP/7zip/UI/Common/LoadCodecs.cpp:791-895` is the built-in load path.
   `CCodecs::Load()` reads `g_Arcs` in registration order, copies the retained
   fields into `CArcInfoEx`, then sorts `Formats` by name at lines 892-894.
   `CArcInfoEx` does not contain `CArcInfo::Id` (`LoadCodecs.h:96-125`).
6. `rust/bridge/archive_bridge_v1.cpp:372-413` currently reconstructs the ID
   by name from a second table populated by link interception. This is the only
   facade consumer that must change.
7. `rust/bridge/archive_bridge_v1.cpp:485-536` creates and loads the owned
   `CCodecs` context, then adds the coordinator-only `Hash` handler through
   `Codecs_AddHashArcHandler`; `rust/bridge/archive_bridge_v1.cpp:571-630`
   publishes the immutable capability arena.
8. `rust/bridge/archive_bridge_v1.cpp:351-370,548-563,632-660` owns context and
   result lifetime. The new accessor does not transfer ownership and does not
   change these rules.
9. `rust/bridge/makefile.gcc:49-54` currently selects GNU `ld --wrap` and the
   private Itanium spelling `_Z11RegisterArcPK8CArcInfo`.
10. `rust/bridge/makefile:16-34` currently fails closed on Windows because MSVC
    has no corresponding reviewed mechanism.
11. `.github/workflows/rebuild-ci.yml:71-162` is the only migration workflow to
    use for three-runner evidence. P1 exact-head run `34752139022` observed a
    successful Linux facade build, the intentional Windows `!ERROR`, and the
    macOS Clang reserved-identifier compile failure. Those are build-recovery
    observations, not Windows/macOS compatibility qualification.

`CPP/7zip/Archive/ArchiveExports.cpp:13-28` owns an alternate registration table
for a different product composition. It is not linked into this facade and must
not be mixed with `LoadCodecs.cpp`'s table. `docs/ai-migration/qualification/abi-v1.md:234-261`
remains the authority for capability identity and the qualification boundary.

## 3. Exact internal API and implementation changes

### 3.1 Retained read seam

In `CPP/7zip/UI/Common/LoadCodecs.h`, forward-declare `struct CArcInfo` and add
these internal C++ declarations immediately before `CCodecs`:

    unsigned Codecs_GetNumRegisteredArcs() throw();
    const CArcInfo *Codecs_GetRegisteredArc(unsigned index) throw();

In `CPP/7zip/UI/Common/LoadCodecs.cpp`, define them next to `RegisterArc()`:

* `Codecs_GetNumRegisteredArcs()` returns `g_NumArcs`.
* `Codecs_GetRegisteredArc(index)` returns `g_Arcs[index]` when
  `index < g_NumArcs`, otherwise `NULL`.

Do not expose the array itself. Do not add mutation, callback, reset, replacement,
or test injection to this API. Do not use `extern "C"`; these names are internal
C++ link inputs, not part of Q1 `archive_bridge_v1` ABI or a public engine API.
Do not alter `RegisterArc()`, `kNumArcsMax`, `g_NumArcs`, `g_Arcs`, registration
macros, handler declarations, or `CArcInfoEx`.

### 3.2 Facade snapshot and validation

In `rust/bridge/archive_bridge_v1.cpp`:

1. Delete the private-mangling macros, `__real_`/`__wrap_` declarations and
   definitions, and the facade-owned `g_registered_arcs` table.
2. At the start of capability construction, read the accessor count once and
   copy the returned pointers into a call-local vector without taking ownership.
3. Validate the complete correspondence before publishing any row:
   * every accessor result in `[0, count)` is non-null and has a non-null,
     non-empty name;
   * registered names are unique;
   * every registered entry matches exactly one `CCodecs::Formats` row by the
     same case-sensitive name used by the current implementation;
   * every `CCodecs::Formats` row except the one exact `Hash` row matches exactly
     one registered entry;
   * exactly one `Hash` row exists, it has no registered match, and the relation
     is `format_count == registered_count + 1` after
     `Codecs_AddHashArcHandler()`;
   * no other row receives the absent sentinel `256`.
4. Preserve the sorted `CCodecs::Formats` row index and all existing effective
   flags, time flags, factory-presence, text, codec and hasher behavior. The
   snapshot order is used only to prove complete consumption; it does not reorder
   `Formats`.
5. If any check fails, return `ARCHIVE_BRIDGE_V1_ENGINE_FAILURE`. Keep `*result`
   null and all borrowed pointers in `view` null; destroy the temporary result
   and vectors exactly once. Never publish a partial capability arena.

Factor the correspondence check as a pure internal helper over an explicit
pointer span/vector plus the loaded formats. This permits negative tests without
mutating the process-global retained table. The production caller passes the
read-only accessor snapshot. Test callers pass synthetic snapshots.

### 3.3 Build files

In `rust/bridge/makefile.gcc`, remove only the `-Wl,--wrap=...` addition and its
private-mangling explanation. Keep the retained `ARC_OBJS`, built-in-only policy,
shared-library mode, exact header/build digests and object composition.

The same file remains the GNU/Linux and Apple Clang build description. Select the
existing platform variable/warning makefiles at invocation time; do not add
Apple-specific symbol aliases, `-undefined dynamic_lookup`, weak references, or
linker interposition.

In `rust/bridge/makefile`, remove the intentional `!ERROR`, complete the existing
MSVC x64 retained-object build, and compile `archive_bridge_v1.cpp` with the same
header and build identity defines as the POSIX build. Ensure the bridge compile
uses the Q1 `ARCHIVE_BRIDGE_V1_CALL` declarations, which explicitly select
`__cdecl` despite the retained make system's `-Gr`. Export exactly the five
currently defined C ABI symbols (handshake, create/destroy context,
capabilities, result destroy), using a bridge-owned `.def` file if and only if
MSVC does not export that exact set from the existing declarations. Any `.def`
file belongs under `rust/bridge/`; never reuse `Archive2.def` or expose retained
C++ accessor names.

In `.github/workflows/rebuild-ci.yml`, preserve the three Rust workspace jobs and
the DEVELOPMENT manifest wording. Make each facade build outcome required while
keeping `if: always()` evidence upload. Do not route this work through or loosen
`.github/workflows/build-windows.yml`. Use `workflow_dispatch` at the exact coder
branch/ref unless the implementation card explicitly owns a narrower temporary
rebuild-workflow branch filter; never re-enable the legacy workflow on migration
branches.

### 3.4 Tests owned by the implementation

Add checked correspondence tests beside the bridge, not in codec/handler files.
The implementation may add one bridge-only C++ test translation unit or extend
the existing `ARCHIVE_BRIDGE_V1_SELF_TEST` section. Tests must call the factored
helper with explicit snapshots; they must not overwrite `g_Arcs` or
`g_NumArcs`.

Required positive controls:

* the real retained snapshot is completely consumed;
* all Q1 format names and registration IDs match the applicable frozen native
  observation, while `Hash` alone is `256`;
* repeated capability enumeration is stable and leaves registration order and
  `CCodecs::Formats` unchanged;
* the five-symbol Q1 export surface is exact on each platform;
* `qualified_operations == 0` and no reserved archive operation is exported.

Required negative controls, each independently expecting
`ARCHIVE_BRIDGE_V1_ENGINE_FAILURE`, a null result, and no published view pointers:

1. remove one retained entry;
2. duplicate one retained name (even if the IDs are equal);
3. substitute an unknown registered name;
4. add an unexpected unregistered non-`Hash` format;
5. remove or duplicate the coordinator `Hash` row;
6. return null for an in-range accessor slot.

A control that deliberately reintroduces the old `--wrap`, `_Z11...`,
`__real_...`, or `__wrap_...` strings must make the source/build guard fail. This
proves the guard is active rather than merely reporting an empty search.

## 4. Ownership, lifetime, threading, error and cleanup invariants

* Each handler translation unit owns its `static const CArcInfo` for module
  lifetime. `LoadCodecs.cpp` owns only borrowed pointers in its static table.
  The accessor lends those pointers; callers never delete, alter, retain beyond
  module lifetime, or convert them into Rust ownership.
* Dynamic initialization is complete before a successfully loaded facade can be
  called. The production accessor is read-only after that point. No callback or
  mutable process-global observer is installed, so there is no restoration path
  to forget and no cross-context observer state.
* A capability call copies only the pointer list into call-local C++ storage.
  It copies scalar IDs and text into the existing C++ result arena before return.
  No `CArcInfo *` crosses Q1 ABI or enters Rust.
* Context/result ownership, `BUSY`, exactly-once result destruction, COM release,
  exception translation, and no-cross-ABI-allocation rules remain unchanged.
* A malformed registration snapshot is an engine/build identity failure, not an
  absent capability. It fails closed as `ARCHIVE_BRIDGE_V1_ENGINE_FAILURE` with
  no partial result. Allocation failures remain
  `ARCHIVE_BRIDGE_V1_ALLOCATION_FAILURE`; exceptions never cross the C ABI.
* The accessor count is sampled once per capability call. The implementation
  must not assume a stable read if any future build permits runtime registration;
  such a build hits a stop condition below rather than adding locking or global
  mutation without a new reviewed design.

## 5. Owned and forbidden paths for one later coder card

One coder card can safely implement all three platforms. The semantic change is
one coupled accessor/correspondence invariant, while the build differences are
small consumers of that same decision. Splitting by platform would make multiple
cards edit `archive_bridge_v1.cpp`, both makefiles and the same workflow, and
could let them choose incompatible failure behavior. The single card therefore
owns only:

* `CPP/7zip/UI/Common/LoadCodecs.h`
* `CPP/7zip/UI/Common/LoadCodecs.cpp`
* `rust/bridge/archive_bridge_v1.cpp`
* `rust/bridge/makefile.gcc`
* `rust/bridge/makefile`
* optional new bridge-owned `.def` and bridge-only registration test files
* `rust/bridge/build-manifest.py` only for portable evidence recording, never to
  fabricate missing platform records
* `.github/workflows/rebuild-ci.yml`
* the directly corresponding DEVELOPMENT evidence document under
  `docs/ai-migration/`

The coder must not edit `CPP/7zip/Common/RegisterArc.h`,
`CPP/7zip/Archive/ArchiveExports.cpp`, any handler/codec/encryption source under
`C/`, `CPP/7zip/Archive/`, `CPP/7zip/Compress/`, `CPP/7zip/Crypto/` or `Asm/`,
Q1 golden/native observations, fixtures, `archive_bridge_v1.h`, Rust public ABI
bindings, CLI/Qt/QML code, legacy workflow triggers, installer/registry/service
code, package/signing/release configuration, tags, `dev-main`, or shared history.
If an implementation proves one of those edits necessary, stop and return to
architecture review; do not widen the card silently.

## 6. Exact implementation verification

### 6.1 Local Linux checks

Run from a fresh committed implementation tree and record each command, exit
status, compiler/version output, artifact path and digest:

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

Also run the committed bridge registration self-test/negative-control command
documented by the implementation and the exact-symbol check produced by
`build-manifest.py`. A repository guard must report no production occurrence in
`rust/bridge/archive_bridge_v1.cpp`, `rust/bridge/makefile.gcc`, or
`rust/bridge/makefile` of `--wrap`, `_Z11RegisterArcPK8CArcInfo`, `__real_`, or
`__wrap_`; then run its deliberate bad-input control and record that it fails.

Documentation-only P3 does not execute these future implementation commands.
P3 itself runs repository documentation/preservation checks in section 8.

### 6.2 Required exact-head GitHub Actions evidence

Run `.github/workflows/rebuild-ci.yml` at the coder's exact reviewed candidate
SHA on its isolated branch, using native `ubuntu-latest`, `windows-latest`, and
`macos-latest`. Acceptance requires all six matrix jobs to finish with
`conclusion=success`, not a green job that masks a failed facade step:

* `Rust workspace / ubuntu-latest`
* `Rust workspace / windows-latest`
* `Rust workspace / macos-latest`
* `Retained facade probe / ubuntu-latest`
* `Retained facade probe / windows-latest`
* `Retained facade probe / macos-latest`

For each facade job, upload even on failure: the exact commit/ref, OS and
architecture, compiler/linker/driver versions, full build and self-test logs,
exact five-symbol export listing, binary/header/build-identity SHA-256 values,
registration count and checked correspondence result, every negative-control
result, and the unchanged DEVELOPMENT statements. The reviewer must download the
artifacts independently, verify their platform and exact-head identity, and
record artifact IDs and digests. Windows evidence must be from native MSVC on
`windows-latest`; Wine or cross-compilation is not a substitute. macOS evidence
must be from Apple Clang on `macos-latest`.

This run establishes portable build and self-owned contract behavior only. It
does not satisfy deferred S2a/B08 native qualification, sanitizer, dead-strip,
archive behavior, GUI/desktop integration, installer, signing, or release gates.

## 7. Rejected alternatives

* GNU `ld --wrap`, MSVC `/alternatename`, weak aliases, interpose libraries, or
  any spelling of a private C++ mangled symbol: toolchain-specific and already
  disproved as portable by P1.
* A process-global observer callback set by the facade before registration:
  registrations occur during static initialization, before a caller can attach;
  making it replaceable introduces ordering, concurrency and deterministic
  restoration hazards.
* Preprocessor renaming of `RegisterArc` across all handler translation units:
  it silently changes the mature engine's internal link contract and is another
  form of interception.
* Editing every `REGISTER_ARC` use or generated handler table: broad, collision
  prone, and effectively rewrites mature format registration.
* Adding `Id` to `CArcInfoEx`: it changes a widely used retained structure merely
  for one facade observation. The narrow read accessor exposes data already
  retained without changing each context's layout.
* Matching by sorted row index: Q1 explicitly says indices are local to the
  sorted runtime table. Registration order and sorted capability order differ.
* Treating every unmatched row as `256`: Q1 reserves absence for the separately
  added `Hash` row; silently accepting another mismatch fabricates identity.
* Reusing `ArchiveExports.cpp` or its table: that is a different product
  registration owner and can duplicate or change the facade's retained set.

## 8. P3 documentation checks and evidence limits

P3 changes documentation only; executable product/bridge tests are not
applicable because this card is forbidden to implement the seam. Before review,
P3 must run and record:

    git diff --check
    python3 docs/ai-migration/validate-migration-dag.py
    python3 docs/ai-migration/qualification/validate.py
    python3 .github/tests/release_version_test.py
    python3 .github/tests/change_notice_test.py
    python3 .github/tests/lang_files_test.py
    python3 .github/tests/shell_ext_identity.py
    python3 .github/tests/shell_ext_lang_reload.py
    bash .github/tests/release_notes_test.sh

It must also verify every cited path exists and the listed source anchors still
contain the described symbols. P3 claims no Windows/macOS facade success beyond
P1 run `34752139022`; that run's Windows and macOS failures remain the evidence
that motivates this design.

## 9. Rollback and stop conditions

Rollback is deletion of the two retained accessor declarations/definitions and
restoration of the previous facade/build files from the implementation parent.
No archive data or persistent state is migrated, and no installer identity or
public ABI revision is changed.

Stop implementation and return to architecture review if any of these occurs:

* native registration is not complete before the first facade export can run;
* a supported build performs runtime registration or unloads handler storage;
* registered names are not unique or cannot establish a one-to-one relation to
  the loaded built-in formats;
* a non-`Hash` row legitimately has no `CArcInfo`, or `Hash` is registered through
  `CArcInfo` on a supported platform;
* preserving behavior requires changing registration order, `CArcInfoEx`, Q1 ABI,
  handler/codec/encryption sources, external-plugin policy, or archive semantics;
* exact-head native CI cannot prove the required build, symbol and negative
  controls on all three runners;
* the same substantive implementation/review problem survives two attempts.

Do not convert one of these conditions into a fallback ID, skipped test,
`continue-on-error` success, weakened warning policy, or qualification claim.
Use a typed `needs_input` gate only when the evidence exposes a real semantic,
ownership, security, licensing, or material architecture decision; ordinary
compiler/build defects return to the same implementation card for repair.
