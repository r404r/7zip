# ADR-0002: worker-owned sessions, owned snapshots and platform ports

Status: proposed for independent M2 review; contracts for future staged work.

## Context

`CPP/7zip/Archive/IArchive.h:305-307` prohibits simultaneous calls on one archive.
At 184-192, progress may overlap extraction callbacks on other threads. COM-like
refcounting is not proof of Send/Sync or reentrancy. Global registration and mutable
conversion/path state are recorded in [M0](../architecture-current.md).
`CPP/7zip/UI/Agent/ArchiveFolderOut.cpp:35-80` invalidates proxies on reopen,
restores the old code page on failure and may leave the folder unusable. A borrowed
entry pointer is therefore not a stable application model.

`CPP/Common/StringConvert.cpp` uses different native conversion branches;
`CPP/Windows/FileIO.h` contains both Win32 HANDLE and POSIX descriptor versions.
Archive-decoded names, display text and native filesystem paths are distinct.
The [M0 platform map](../win32-dependencies.md) rules out both a UTF-8-only domain
and deletion of every directory named Windows.

## Decision

Start with ONE dedicated engine worker for all contexts in the process. It creates,
uses and destroys all engine/session/result objects. Commands are serialized even
across archives; queued requests are application concurrency, not simultaneous
engine execution. Registration/loading happens on that worker before requests and
is frozen until teardown. Retain codec-internal parallelism. Additional per-session
workers require a separately reviewed global-state audit and native stress evidence.

The command handle may be shared; native pointers may not. Progress/cancel/prompt
mailboxes are independently concurrency-safe because codec callbacks may arrive
on other threads. Do not hold application mailbox or initialization mutexes during
engine calls or waits. The worker does not hold a global mutex for its whole run;
its exclusive engine ownership provides serialization. Replies and cancel wakeups
must bypass the occupied command queue. No synchronous UI -> engine -> UI cycle.

Expose Archive/ArchiveEntry as owned snapshots with session/generation/item identity,
not Agent proxies or names as keys. Generation changes before invalidation and on
rollback recovery; stale commands fail without calling the engine. Snapshot data
may remain viewable after close, but cannot authorize extraction. A failed reopen
with failed rollback marks the session unusable and clears actionable selection.
Do not broaden CanReOpen eligibility or claim existing reopen cancellation.

Use engine UTF-16-code-unit text, explicit native-path tagging and lossy display
only for presentation. Copy variant/raw property values under their owner lifetime;
retain unknown/absent values. No global Unicode normalization, path sanitization
rewrite or metadata coercion. Preserve scoped handler properties, resetting reused
handlers even if the filtered property list is empty (`SetProperties.cpp:48-67`).

Define portable filesystem/settings/desktop ports with target-specific modules.
Domain/app cannot directly depend on HWND, HANDLE, Registry, COM, descriptors or
native dialogs. Existing C++ file/scan/extract/update policy implements the initial
behavior; the later Rust filesystem stage replaces only characterized services.
Native resources never acquire two owners across this transition.

## Task and lifetime protocol

The normative field/operation/allocator tables and state machine are in
[target architecture](../architecture-target.md), sections 3-6; do not maintain a
second competing schema here. Their critical guarantees are:

1. All session calls and destruction are owner-worker-only. No live callback/user
   data is freed by dropping a UI object. C++ results are copied and freed through
   the facade; Rust does not free BSTR, PROPVARIANT or COM interfaces.
2. Questions have unique request identity and reply-once validation. Undefined,
   empty and cancelled passwords differ. No secret in progress/logs/settings.
3. Cooperative cancel wakes question waiters and returns E_ABORT where supported;
   cancellation is not thread termination or guaranteed rollback. Partial outputs
   are reported according to measured retained policy. Late replies are rejected.
4. Progress may be coalesced; terminal/per-item error information may not. Units and
   unknown totals are preserved. A bounded report spool must fail explicitly if
   it cannot record outcomes, not label a partial report complete.
5. Shutdown cancels/drains, wakes interactions and keeps their state alive until
   engine quiescence; only then release sessions, module cycles and join. Qt stays
   responsive while waiting. Non-polling retained operations have unbounded latency.
6. Structured outcomes distinguish HRESULT/call status, item failures, warnings,
   bridge faults and native errors. No bool-only success or guessed wrong password.

## Alternatives and consequences

- Worker per session now: rejected until cross-session/global-state safety is
  established. Initial throughput is deliberately conservative.
- Mutex around each COM call with borrowed UI entries: rejected; it does not solve
  asynchronous progress, proxy invalidation, destruction or UI reply deadlocks.
- Zero-copy Rust views of engine properties: deferred; owned snapshots cost memory
  but allow explicit page sizing and clear lifetimes. Large archives use bounded
  enumeration pages, not one forced full-archive allocation.
- Generic UTF-8 filesystem model: rejected; invalid bytes/surrogates and platform
  name/metadata behavior must survive round trips where supported.

The bridge stage implements only safety-essential callback/cancel transport.
General task manager, pause/resume UX, richer scheduling and filesystem replacement
stay after list/extract/test/create. These contracts are not permission to skip the
mandated order.

## Required validation

Test late/duplicate replies, no interaction consumer, cancel while prompting,
shutdown during callback/progress/blocked open, stale generations after update and
reopen rollback, repeated close/drop, null streams, short I/O, partial errors and
concurrent progress. Run sanitizer/stress tests where supported and document gaps.
Native Windows tests cover code pages, UNC/long/reserved paths, ADS/security/reparse,
settings and shell/OLE separately; Linux/macOS cover their own byte names, metadata,
links and filesystem characteristics. Compare partial-output behavior to reviewed
M1 expectations in disposable sandboxes. Missing native evidence limits support;
semantic/data-loss disagreement blocks the affected card, never edits goldens.
