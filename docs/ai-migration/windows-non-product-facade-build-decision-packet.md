# Decision packet: non-product Windows retained-facade build

Status: operator decision requested; no build authorization is in force

Task: `t_0cf7533c`

Reviewed inputs:

- S2a-R `t_13a346c7`, commit
  `f6ca43ab5d370ef7a379a58e1735b45b17cd91f9`
- P4-I `t_acdf81b3`, commit
  `5249961fb6b71b80ce9a63d59a25f324a684acf5`

This packet does not change the Windows guard, authorize a build, qualify an
archive operation, or promote an artifact. Independent review of this document
is required before it reaches the operator, but reviewer PASS is not the human
gate and is not operator approval.

## Operator question

After the reviewed S2a-R registration-redirection work and P4-I MSVC
calling-convention probe, may a later, independently reviewed implementation
replace the unconditional Windows `!ERROR` with a fail-closed opt-in that permits
one exact-head CI build/link/registration evidence run of the retained facade into
a scratch directory, while `qualified_operations == 0`, every archive operation,
every consumer, and every artifact-promotion path remain disabled?

Recommended answer: **keep the unconditional guard unless the operator explicitly
authorizes disposition 2, the narrowly bounded non-product evidence build.**
Disposition 3, unconditional guard removal, should be rejected.

The operator should record exactly one of:

- `KEEP`: disposition 1; make no build-enablement card.
- `AUTHORIZE_NON_PRODUCT_EXACT_HEAD_BUILD`: disposition 2 only; create the one
  constrained implementation card described below.
- Any broader intent requires a new architecture decision. It is not an answer to
  this packet.

## Three decisions that must remain separate

### 1. Build authorization — the only ripe question

This asks only whether the five-definition Windows facade may be compiled and
linked once under controlled, non-product, exact-head CI conditions to collect
compiler, linker, PE export, registration-composition, and runtime contract
evidence. Authorization would permit later implementation of the control, not
this document and not an immediate build.

### 2. Operation qualification — not ripe

No archive operation may be implemented, enabled, invoked, or consumed under this
decision. B01, B03, B05, and B06 remain direct input-bearing S2a gates. B04 is
relevant indirectly through B06 and later filesystem-effect work. Those unresolved
inputs include licensing/admission, filesystem semantics, password behavior, and
callback/lifetime behavior. A build authorization answer cannot resolve them.

`archive_bridge_v1_open`, `archive_bridge_v1_entries`, and
`archive_bridge_v1_close` are declarations in the frozen Q1 header, not current
facade definitions and not qualified operations
([`qualification/archive_bridge_v1.h:293-312`](qualification/archive_bridge_v1.h),
[`msvc-calling-convention-qualification-design.md:62-68`](msvc-calling-convention-qualification-design.md)).
They must remain absent from the retained facade's PE export table.

### 3. Artifact promotion — not ripe

No resulting DLL may be uploaded as a normal artifact, packaged, signed,
installed, registered, placed on a release path, handed to an operator as a
product, tagged, or published. Build authorization would not imply any of these
actions.

The Kanban dependency graph coordinates policy; it is not access control. Once a
build path exists, a developer, local script, or modified CI job could invoke it
without traversing the intended card graph. Disposition 2 therefore requires
technical fail-closed controls in the build and workflow themselves.

## What the reviewed evidence establishes

### S2a-R: registration redirection

S2a-R `t_13a346c7` at reviewed commit `f6ca43ab` implemented the explicit
54-translation-unit registration redirection and correspondence checks. It
established the retained registration composition under GCC and Apple Clang,
including the real shim, 72-slot/73rd-call overflow controls, one-to-one frozen
registration correspondence, and the five-symbol POSIX facade surface. The exact
mechanism and 54-source inventory are documented in
[`portable-retained-registration-redirection.md:11-54,82-135`](portable-retained-registration-redirection.md).
The implementation record says the NMAKE file declares the corresponding 54
explicit `/DRegisterArc=ArchiveBridgeRegisterArc` recipes, but its top-level
`!ERROR` remains active and MSVC remains unverified
([`qualification/s2a-dev.md:347-368`](qualification/s2a-dev.md)).

Its exact-head Windows facade job stopped at the guard by design. Therefore S2a-R
does **not** establish a successful Windows facade compilation or link.

### P4-I: MSVC calling convention

P4-I `t_acdf81b3` at reviewed commit `5249961` qualified MSVC treatment of the Q1
ABI boundary with an AMD64 normative lane and an x86 diagnostic lane. The probe
covers eight frozen declarations, the five current bridge definitions, three
callback types, object and PE names, C and Rust callers, and mandatory failure
injection. Its design deliberately forbids invoking the retained facade makefile,
compiling retained engine translation units into the probe, linking
`archive_bridge_v1.dll`, or producing a facade package
([`msvc-calling-convention-qualification-design.md:26-37`](msvc-calling-convention-qualification-design.md)).

P4-I is a bridge-owned non-product probe, not the retained facade. It does **not**
establish a successful Windows retained-facade build or any archive-operation
semantics.

### Combined limit

Neither reviewed commit built the Windows facade through `rust/bridge/makefile`.
That path has still never passed its first directive. Neither commit establishes
archive open/list/close, extraction, testing, creation, encryption, password,
filesystem-effect, overwrite, cancellation, or error semantics on Windows.

The exact current *defined facade function set* is five C ABI names:

1. `archive_bridge_v1_handshake`
2. `archive_bridge_v1_create_context`
3. `archive_bridge_v1_destroy_context`
4. `archive_bridge_v1_capabilities`
5. `archive_bridge_v1_result_destroy`

The source states this at [`rust/bridge/archive_bridge_v1.cpp:1-11`](../../rust/bridge/archive_bridge_v1.cpp),
and the P4 inventory independently records it at
[`msvc-calling-convention-qualification-design.md:62-68`](msvc-calling-convention-qualification-design.md).
This is not yet a verified Windows PE export set: no retained Windows facade DLL
exists, so there is no `dumpbin /exports` evidence for it.

One implementation hazard must be resolved under review rather than assumed away.
The guarded NMAKE declaration sets `PROG = archive_bridge_v1.dll` but does not set
`DEF_FILE`, and the matched header has no `__declspec(dllexport)`. The retained
`Build.mak` selects `/DLL -DEF:` only when `DEF_FILE` is defined
([`CPP/Build.mak:154-176`](../../CPP/Build.mak)). Consequently the current text is
an input declaration, not proof that an unguarded invocation can produce a DLL
with the five required exports. Disposition 2 authorizes investigation and a
reviewed non-product link/export mechanism; it does not pre-approve a specific
mechanism or permit changing the frozen Q1 header.

## Mandatory audit 1: guard-dependent checks

The current guard is the unconditional `!ERROR` at
[`rust/bridge/makefile:24-27`](../../rust/bridge/makefile). It precedes the output
name, every target, and every include.

Two existing checks depend on that exact safety property:

- `rust/bridge/check-registration-seam.py` explicitly requires `!ERROR` and its
  self-test mutates it to `!MESSAGE` to prove removal is rejected
  ([`check-registration-seam.py:70-86,105-133`](../../rust/bridge/check-registration-seam.py)).
- `rust/bridge/msvc-abi-convention-probe.py` requires the guard to exist before
  `PROG` and before the first `!include`; otherwise source validation fails
  ([`msvc-abi-convention-probe.py:147-191`](../../rust/bridge/msvc-abi-convention-probe.py)).

Removing the guard without equivalent replacement weakens both reviewed safety
checks. A disposition-2 implementation must update their positive and negative
controls without weakening the default refusal. The replacement must, at minimum:

1. refuse before every include and target when the opt-in is absent, misspelled,
   locally supplied, stale, or inconsistent with CI context;
2. permit only an allowlisted exact commit, with checked-out `HEAD`, workflow
   event SHA, and requested evidence SHA all equal;
3. permit only the dedicated non-product Windows evidence job;
4. force a newly created scratch output directory outside every normal artifact,
   package, installer, and release staging tree;
5. verify the final PE architecture and exact five-name export set, and reject
   `open`, `entries`, `close`, extra bridge names, or a missing current name;
6. execute matched identity, registration correspondence, and facade contract
   checks while asserting the literal `qualified_operations == 0`;
7. emit a machine-readable and human-readable `NOT_PRODUCT` manifest/marker tied
   to the exact commit and binary digest;
8. fail if any consumer is built, staged, or run other than the dedicated contract
   harness; and
9. delete or quarantine the DLL before evidence upload, uploading logs, manifests,
   hashes, and symbol/export records only—not the DLL, import library, executable,
   package, or installer.

The default path must continue to fail at the top of the makefile. A conditional
`!ERROR` is acceptable only if these controls and their failure injections are
independently reviewed and the default branch remains fail-closed.

## Mandatory audit 2: reachability behind the guard

If the unconditional refusal no longer stops evaluation, the following becomes
reachable:

- `PROG = archive_bridge_v1.dll`, so `PROGPATH` later resolves to
  `$O\archive_bridge_v1.dll` (`rust/bridge/makefile:32`,
  [`CPP/Build.mak:202`](../../CPP/Build.mak));
- `!include "Arc.mak"`, which brings in the retained common, Windows, archive,
  compression, crypto, C, and nested retained object groups
  ([`CPP/7zip/Bundles/Format7zF/Arc.mak`](../../CPP/7zip/Bundles/Format7zF/Arc.mak));
- the bridge's `UI_COMMON_OBJS`, `WIN_OBJS`, `7ZIP_COMMON_OBJS`, and three
  bridge-owned `CURRENT_OBJS` additions (`rust/bridge/makefile:39-65`);
- `!include "../../7zip.mak"`, which aggregates all object groups, includes
  `../../../Build.mak`, exposes the `all`, `clean`, output-directory, object,
  resource, precompiled-header, link, retained C/C++, and assembly rules, and
  includes `Asm.mak`
  ([`CPP/7zip/7zip.mak:1-33,176-240`](../../CPP/7zip/7zip.mak));
- explicit recipes for the three bridge-owned objects and all 54 selected
  registration objects, the latter with per-object
  `/DRegisterArc=ArchiveBridgeRegisterArc` (`rust/bridge/makefile:68-206`); and
- the default `all` target and link command. With `O=<scratch>`, reachable files
  include `$O\archive_bridge_v1.dll`, retained and bridge `.obj` files,
  `$O\resource.res`, `$O\a.pch`, and `$O\asm\` intermediates. A reviewed DLL
  export mechanism may also cause MSVC linker sidecars such as an import `.lib`
  and `.exp`; those must be treated as prohibited runnable/promotable products and
  kept in the same scratch containment.

This composition includes mature archive handlers, compression, and crypto
objects because it mirrors retained `Format7zF`; that makes the output
production-shaped even though no archive operation is exported. It is why an
opt-in must be narrower than merely changing `!ERROR` to a comment.

## Mandatory audit 3: consumer enforcement

Universal enforcement of `qualified_operations == 0` is **unproven**.

Verified repository facts:

- No tracked production code dynamically loads a retained
  `archive_bridge_v1.dll` by that name. The repository search found dynamic
  bridge loading only in the P4-I generated probe callers, which load the
  separately named `archive_bridge_v1_cc_probe.dll` for test sentinels
  ([`msvc-calling-convention-qualification-design.md:175-210`](msvc-calling-convention-qualification-design.md)).
- The current Rust FFI consumer is link-time, not a Windows `LoadLibrary` policy.
  `archive-engine-sys` declares the five current symbols directly
  ([`rust/crates/archive-engine-sys/src/link.rs:19-59`](../../rust/crates/archive-engine-sys/src/link.rs)).
- The safe adapter rejects a capability snapshot whose
  `qualified_operations` differs from zero
  ([`rust/crates/archive-engine/src/facade.rs:191-249`](../../rust/crates/archive-engine/src/facade.rs)).
- The `facade` feature is off by default and there is no build script or arbitrary
  system-facade search
  ([`rust/crates/archive-engine-sys/Cargo.toml:17-28`](../../rust/crates/archive-engine-sys/Cargo.toml)).

Limits:

- Loading/linking and handshake/context creation occur before the safe adapter
  observes the capability bitmask. The lower-level sys crate exposes those calls;
  it does not make DLL load contingent on first checking `qualified_operations`.
- An external C/C++ or Rust consumer is not forced by the DLL to call
  `capabilities` or enforce the bitmask.
- There are currently no operation definitions to invoke, which is a real
  containment property, but it is not proof that every present or future consumer
  enforces the bitmask.

Disposition 2 must therefore require **no consumer** outside the dedicated
contract harness. `qualified_operations == 0` is a required assertion, not the
sole access control.

## Mandatory audit 4: artifact identity and collision

The declared output is `archive_bridge_v1.dll`, not `7z.dll` or `7z.exe`. The
legacy package names and sources are explicit in
[`.github/workflows/build-windows.yml:85-109`](../../.github/workflows/build-windows.yml).
There is no source-backed filename collision with either legacy product name, and
this packet makes no such claim.

The real collision hazards are:

- a stale or future `archive_bridge_v1.dll` already in the chosen output directory;
- a same-named DLL found through the consumer's DLL-search path rather than the
  intended exact-head scratch path;
- a new binary overwriting prior evidence at a reused `$O` path; and
- a binary containing the retained `Format7zF` composition being mistaken for the
  sanctioned migration facade despite being unqualified and non-product.

The matched-build handshake and build digest reduce mistaken acceptance only for
consumers that actually perform and enforce them. They do not prevent copying,
renaming, uploading, signing, or loading by another consumer. Disposition 2 must
use a fresh absolute scratch path, reject pre-existing outputs, verify the loaded
module's canonical path in the harness, include commit and binary digests in the
non-product manifest, and destroy/quarantine runnable outputs after evidence
capture.

## Mandatory audit 5: artifact, package, installer, signing, and release paths

The tracked workflows contain eight artifact-upload actions across six files:

- Q1 evidence only: `.github/workflows/q1-native.yml:49-65`;
- B02 evidence only: `.github/workflows/b02-native.yml:54-63`;
- S1 logs only: `.github/workflows/s1-native.yml:34-40`;
- characterization evidence only:
  `.github/workflows/characterization-native.yml:113-119`;
- P4-I evidence, Linux development output, and facade-probe directory:
  `.github/workflows/rebuild-ci.yml:123-129,176-182,377-383`; and
- the legacy Windows product artifact:
  `.github/workflows/build-windows.yml:249-278`.

The current Windows facade attempt uses
`O=%RUNNER_TEMP%\rebuild-facade`, while the current facade-probe upload reads
`%RUNNER_TEMP%\rebuild-facade-probe`; therefore the guarded DLL output is not in
the upload tree today (`rebuild-ci.yml:295-310,311-383`). That separation is a
verified current fact, not a durable control against a future workflow edit.

The only tracked package/installer/release chain is the legacy Windows workflow:

1. an explicit source allowlist is copied into `msi-stage`;
2. WiX consumes that stage to create `7zip-fork.msi`;
3. `msi-stage\*` is copied into `artifact\portable` and the MSI into `artifact`;
4. `artifact` is uploaded as `7zip-win-x64`;
5. a tag-triggered job downloads it, creates an MSI asset, portable ZIP, and
   checksums; and
6. `gh release create` publishes `out/*`
   ([`.github/workflows/build-windows.yml:85-155,249-278,280-389`](../../.github/workflows/build-windows.yml)).

The WiX source itself allowlists legacy filenames and does not mention
`archive_bridge_v1.dll`
([`.github/msi/7zip-fork.wxs:49-107`](../../.github/msi/7zip-fork.wxs)). Thus the
facade is not currently staged into the MSI, portable ZIP, `7zip-win-x64`, or
release assets. A future copy into `msi-stage`, `artifact`, `artifact/portable`,
`out`, any evidence directory, or any current upload path would bypass that
separation and must fail disposition-2 checks.

No tracked Authenticode, `signtool`, `codesign`, or other product-signing command
was found. This is unavailable capability, not evidence that signing can never be
added. Disposition 2 forbids adding or invoking one.

## Dispositions

### Disposition 1 — keep the unconditional guard

Decision: retain the current `!ERROR` exactly. This is the default and the
recommendation unless disposition 2 is explicitly authorized.

Later card permitted: no Windows facade build-enablement implementation card. A
documentation-only evidence-refresh/audit card may be created if source facts
change, and the existing B01/B03/B04/B05/B06/S2a/B08 work may continue under its
own gates.

Still forbidden: guard edits, Windows facade compilation/linking, operation work,
consumer work, DLL upload, packaging, signing, install, release, and product
claims.

Impact: preserves the strongest accidental-build protection and both existing
guard checks, but obtains no Windows facade build/link/registration evidence.

### Disposition 2 — later fail-closed exact-head non-product opt-in

Decision: only after explicit operator approval, create one implementation card
to replace the unconditional refusal with the technical controls in this packet.
That card must be independently reviewed before any exact-head run.

Later card permitted: one narrowly scoped “Windows retained facade non-product
exact-head evidence build” card. It may edit the NMAKE guard/control, a dedicated
non-product workflow job, and bridge-owned verification/evidence scripts as
needed to:

- implement the fail-closed opt-in;
- solve the currently unproven DLL link/export mechanism without changing the
  frozen Q1 header;
- build only on Windows AMD64 at the exact reviewed head into a fresh scratch
  directory;
- inspect every object and the final PE machine/export/registration composition;
- run only the dedicated matched contract harness;
- assert the five-name export set and `qualified_operations == 0`; and
- upload only non-runnable evidence after deleting/quarantining all binary outputs.

The later card must carry a changed-path allowlist, failure injection for every
control, exact build/test commands and results, and a second independent review.
If implementation requires a broader boundary, it must stop for a new operator
decision rather than expanding this authorization.

Still forbidden: `open`, `entries`, `close` definitions or exports; any other
archive operation; operation or product qualification; any general/local build
switch; any consumer outside the harness; normal artifact upload; package,
installer, registration, signing, install, tag, release, publication, or
`dev-main` merge.

Impact: obtains the missing Windows compilation/link/registration evidence with a
larger but bounded attack surface. It replaces one simple unconditional barrier
with a more complex control, so control failure injection and independent review
are mandatory.

### Disposition 3 — remove the guard unconditionally (reject)

Decision: delete/bypass the refusal and make the retained NMAKE path ordinarily
reachable.

Later card permitted: **none under this packet.** If the operator nevertheless
wants this outcome, a new architecture decision and human gate must first define
product intent, consumers, export/link policy, operation prerequisites, artifact
identity, packaging, and release controls.

Still forbidden under the present migration: all implementation implied by this
disposition.

Impact: weakens two reviewed safety checks, lets local scripts or modified CI
produce a production-shaped retained-engine binary without graph enforcement,
leaves universal consumer enforcement unproven, and exposes stale-DLL and
promotion risks. It provides no operation semantics. Reject.

## Expiry and mandatory re-decision

Whichever answer the operator gives expires before use if any of the following
changes after this packet's reviewed commit:

- a facade definition or PE export is added, removed, or renamed;
- `open`, `entries`, `close`, or any other operation becomes defined or exported;
- the output name, `$O` handling, DLL/import-library location, or DLL-search policy
  changes;
- any workflow artifact path, package stage, WiX input, installer, signing path,
  tag trigger, or release path changes in a way that could reach the facade;
- `qualified_operations` changes from literal zero, its bit assignments change,
  or a consumer begins treating any bit as enabled;
- a new consumer, loader, build script, runtime search path, or package dependency
  is introduced;
- B01, B03, B04, B05, B06, S2a, or B08 dependencies resolve or are re-scoped such
  that operation qualification becomes a different ripe question; or
- either reviewed input commit is replaced, reverted, or contradicted by later
  native evidence.

Expiry does not silently select disposition 1 or 2. It restores the unconditional
fail-closed posture pending a fresh audit and operator decision.

## Evidence classification

### Verified facts

- Both reviewed commits resolve in this repository and are ancestors of the
  packet's starting head `5249961fb6b71b80ce9a63d59a25f324a684acf5`.
- The Windows facade guard remains before every target/include.
- S2a-R's Windows job stopped at that guard; P4-I did not build the retained
  facade.
- Five facade functions are defined; eight are declared; `open`, `entries`, and
  `close` have no retained-facade definitions.
- `qualified_operations` is assigned literal zero by the facade
  (`rust/bridge/archive_bridge_v1.cpp:642-645`).
- The safe Rust capability adapter rejects nonzero bits, but no universal loader
  or external-consumer enforcement exists.
- The declared Windows output name is `archive_bridge_v1.dll` and the current
  legacy package/release allowlists do not contain it.
- No tracked product-signing command exists.

### Unavailable evidence

- A successful retained Windows facade compile or link.
- The retained Windows facade's actual PE machine, five-name export table, import
  library, registration table, loaded module identity, or runtime contract result.
- Proof that the current guarded NMAKE declaration links correctly once reached.
- Proof that every external or future consumer checks `qualified_operations`.
- Native archive-operation semantics on Windows.

### Assumptions that an implementation must not promote to facts

- That an `.dll` filename alone makes the current link a valid exported DLL.
- That the Kanban graph prevents an out-of-graph build.
- That `qualified_operations == 0` prevents loading or misuse by itself.
- That separation of today's scratch/upload paths survives workflow edits.
- That no stale same-named DLL exists on an output or search path.

## Validation of this documentation card

This card changes one English Markdown decision packet only. It intentionally does
not edit or execute `rust/bridge/makefile`, build the facade, change an operation,
or touch a workflow. Runtime and native build tests are therefore not applicable;
running them would violate this card's scope. Required validation is limited to
ancestry, source/path/citation checks, Markdown whitespace, the one-file allowlist,
and preservation hashes for forbidden paths.

Executed from the isolated task worktree:

- `python3 /tmp/t_0cf7533c_validate_packet.py docs/ai-migration/windows-non-product-facade-build-decision-packet.md`
  — PASS: all 21 local Markdown links and source citations resolve.
- `git diff --check` — PASS.
- `git status --short` plus an exact one-file assertion — PASS: only
  `docs/ai-migration/windows-non-product-facade-build-decision-packet.md` changed.
- `git cat-file -e <sha>^{commit}` and `git merge-base --is-ancestor <sha> HEAD`
  for both reviewed inputs — PASS.
- `git diff --exit-code -- C CPP Asm rust .github docs/ai-migration/qualification AGENTS.md`
  — PASS: every forbidden path is unchanged.
- `sha256sum docs/ai-migration/qualification/archive_bridge_v1.h rust/bridge/archive_bridge_v1.h rust/bridge/makefile`
  — PASS: the two Q1 headers remain byte-identical at
  `eabe714b31e2076735b8313c06618e5dbb3db4ea924cbef244b78a8b107ee26d`; the
  guarded makefile remains
  `9f51ba2b54926d4af01f26d6da04553774f21e2bf58e17c70093f614820f31f7`.
