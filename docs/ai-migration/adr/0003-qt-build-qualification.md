# ADR-0003: Qt 6/QML via CXX-Qt, with explicit qualification gates

Status: proposed for independent M2 review. Confirms the prescribed direction;
not a toolchain, licensing, GUI parity or release certification.

## Context

[M0 architecture](../architecture-current.md) identifies Win32 File Manager and
archive GUI presentation, portable CLI machinery, and a separate Explorer COM DLL.
The retained engine can sit behind an application boundary; CPanel and HWND cannot
become portable Rust domain objects. AGENTS.md requires Qt 6/QML -> CXX-Qt -> Rust
-> mature C/C++ and forbids silent GUI substitution or skipping straight to GUI.
[M0 risks](../migration-risks.md) R11-R14 identify native desktop, configuration,
licensing and toolchain uncertainties; they have not been experimentally settled
by this documentation task.

## Decision

Keep Qt 6/QML for presentation and CXX-Qt between Qt objects and Rust app services.
Use the separate C engine facade from [ADR-0001](0001-retained-engine-facade.md).
The CLI and engine must build/test without Qt; GUI members are opt-in. Do not
replace Qt with Slint, embed the Win32 UI as the cross-platform solution, or expose
engine pointers through QML to avoid designing application services.

Qt owns its thread-affine objects and models. Rust worker outputs are owned DTOs
queued through the CXX-Qt-supported thread dispatch mechanism of the eventually
pinned version. This ADR deliberately does not invent a version-specific CXX-Qt
method name. Check receiver lifetime and task generation before model changes.
Commands are asynchronous; no Qt-thread blocking join or synchronous engine call.
Prompts use request/reply IDs with cancellation/disconnect behavior from
[ADR-0002](0002-ownership-tasks-platforms.md). Password input is ephemeral and does
not enter model history. Numeric IDs/sizes wider than JavaScript's exact integer
range use lossless adapters; keep domain arithmetic in Rust.

Qt archive browsing, extraction and creation UI each require separate native
acceptance. Preserve per-operation Auto code page, ZIP UTF-8 creation preference,
explicit property precedence and reopen eligibility/rollback. Native Explorer COM,
OLE/drag-drop, associations, language reload and fork installer identities remain
platform responsibilities; successful QML rendering is not shell parity.

## Build/toolchain and licensing qualification contract

No Rust/Qt/CXX-Qt version is asserted tested in M2. Version selection is a bounded
qualification deliverable, not an open choice left to several implementers. M3
assigns one toolchain owner to produce a reviewed pin manifest consumed unchanged
by workspace/bridge/GUI cards. It has two ordered parts:

1. Before production bridge linkage: choose an exact Rust toolchain/MSRV policy,
   Rust edition, supported targets, Cargo.lock policy, C/C++ compiler/runtime and
   build-driver versions; resolve the actual retained-input license obligations
   and reproduce an isolated local engine build with a capability manifest. Check
   ABI, exception mode, ST/MT, registration/link retention and native library
   loading without global search-path hacks. Pin reproducible inputs rather than
   'latest' or an unbounded dependency version.
2. Before GUI implementation (after eligible CLI/filesystem stages): qualify exact
   Qt 6, CXX-Qt and transitive cxx versions together with those Rust/C++ toolchains.
   Use a disposable non-product spike: create/destroy a Qt object, send worker
   snapshots, test queued receiver destruction, request/cancel shutdown, and run
   QML smoke on native Windows/Linux/macOS. Record commands, logs, version output,
   dependency lockfiles and machine/architecture. The spike may establish a valid
   configuration, not bypass CLI-first migration or count as GUI delivery.

Select only modules actually needed; record every Qt runtime/plugin shipped and
its version/license. Audit repository License.txt, source headers and modified
notices, LGPL source/relinking obligations as applicable, unRAR restriction, BSD
components, language assets and selected Rust/Qt/CXX-Qt package licenses. Dynamic
linking is not automatic legal approval; no static-linking/release choice is
approved here. Unclear selected obligations require a real human needs_input gate
before the affected linking/distribution decision. Native signing/notarization and
installer distribution are later release tasks, never implied by a local build.

A valid pin manifest lets later cards proceed without asking humans to choose
minor compatible version details. A failed qualification must include real logs
and attempt count. Do not label Windows cross-compilation or Wine native PASS.
Do not invent credentials or require duplicate authorization after authorized
credential setup has actually been supplied and verified.

## Alternatives and consequences

- CXX-Qt all the way to COM/engine: rejected; presentation ownership and engine
  lifetime are different problems, with different thread and error contracts.
- Alternate GUI framework: not selected. If qualification demonstrates a material
  blocker, prepare an evidence-backed ADR and request human approval before change.
- Qt migration now: rejected; it would conceal missing characterization and force
  UI-driven policy rewrites before the engine/application seam exists.

Version pins remain pending qualification, but framework, crate ownership, model
boundary and event protocol are fixed by M2. No semantic/licensing decision is
needed to write these architecture documents because no new package is installed,
linked or distributed here. Future unresolved facts are explicit prerequisites,
not presumed approvals.

## Escalation and exit evidence

For a real Qt/toolchain blocker offer: (1) recommended, qualify another supported
Qt/CXX-Qt pin while retaining direction, costing investigation only; (2) defer GUI
and continue eligible CLI work, delaying desktop replacement; (3) propose a major
alternative ADR for human review, with parity/rework impacts. Record a typed
needs_input block and wait for actual decision when architecture must change.

Native GUI exit evidence includes archive browse/selection with stale updates,
password/overwrite/volume dialogs, cancel/shutdown, keyboard/accessibility,
localization, invalid/non-BMP names, large sizes and each supported OS's desktop
integration separately. Neither this ADR nor the qualification spike satisfies
those product acceptance tests. See [migration stages](../migration-stages.md).
