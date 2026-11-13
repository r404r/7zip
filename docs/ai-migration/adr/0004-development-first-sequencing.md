# ADR-0004: development-first sequencing with deferred native qualification

Status: proposed for independent review on task `t_eb4719bf`. This is a sequencing
and acceptance-vocabulary decision. It changes no architecture, no retained codec,
no ABI, no compatibility requirement and no release authority.

## Context

The operator decided on 2026-09-12 that real-machine Linux, Windows and macOS
verification is lowered in priority and becomes deferred follow-up work, and that
the project's mainline implementation should proceed first. The decision is
recorded in AGENTS.md, section "Development-first sequencing, deferred native
qualification", and on task `t_eb4719bf`.

The M3 graph ([migration-dag.md](../migration-dag.md)) was authored with a single
acceptance notion: every card required native Windows, Linux and macOS evidence
for its changed surface. Several native campaigns are currently not executable:
B01 `t_22299c6f` waits on verifiable fixture provenance and licensing, B03
`t_bf92ce13` and B04 `t_2a64c953` wait on authorized private native runners and a
zero native execution budget. Under one acceptance notion, the entire production
spine S1 -> S2a -> B08 -> S3 ... inherits those stalls, including the parts that
need no archive fixture, no hostile input, no password state and no platform
runner at all.

## Decision

Separate two acceptance levels and apply them per card.

- DEVELOPMENT acceptance: the card's own implementation is complete, locally
  compiled, unit tested and verified by its self-owned contract tests on the
  development host. It may be reviewed, approved and integrated into the local
  automation base.
- QUALIFIED/RELEASE acceptance: the card's mandated native Windows, Linux and
  macOS evidence, behavior characterization and licensing evidence are present.
  Only this level may enable a capability for production callers or feed release
  validation.

A card may be scheduled on development acceptance only when each remaining
dependency on a deferred native campaign is EVIDENCE-ONLY: the campaign would
confirm behavior the card already implements from an existing reviewed contract,
rather than supply a semantic, ownership, safety or licensing input the
implementation must consume in order to be written correctly. Dependencies that
supply such an input stay in force. No dependency edge is deleted to make a card
runnable; where an existing card mixes both kinds of work, the development-only
part is split into a separate, smaller card with strictly fewer parents, and the
original card keeps its scope remainder and all of its original parents.

Capability enablement stays gated. The Q1 `qualified_operations` bitmask
([abi-v1.md](../qualification/abi-v1.md)) remains 0 for every development-acceptance
deliverable; bits 0-4 may only be set by the reviewed gate that owns them. Rust
surfaces produced under development acceptance stay behind a non-default Cargo
feature or private module, and unqualified operations return
`ARCHIVE_BRIDGE_V1_UNSUPPORTED` before any effect. A capability whose native
behavior is not yet qualified is unavailable, never approximated.

Deferred native obligations keep their existing cards. They are not deleted,
completed, archived, re-pointed at a mock, or represented as passed. Every
originally mandated native evidence item is still required before S12 release
validation, and archiving an unresolved gate remains forbidden because the
dispatcher treats an archived parent as satisfied.

## Consequences

- The graph gains an explicit `acceptance_mode` per card and an explicit list of
  the native obligations each development-acceptance card defers. The machine
  manifest and [validator](../validate-migration-dag.py) enforce both, reject any
  card that drops an original M3 parent edge, reject a development claim with no
  recorded deferred obligation, reject a qualified-acceptance downgrade on the
  release path, and detect a card completed while its deferred obligations are
  still open.
- The first card enabled by this ADR is the S2a-DEV split described in
  [development-first-sequencing.md](../development-first-sequencing.md): the
  retained-engine facade handshake, context lifetime and capability enumeration,
  which consume only the reviewed Q1 ABI and S1 domain contracts. The remaining
  S2a scope (archive open, paged entries, close and the operation callbacks)
  keeps every one of its B01/B02/B03/B05/B06 parents, because those supply
  format, name/property, partial-I/O, password and cancellation semantics the
  implementation must encode, not merely confirm.
- Review load is unchanged: same-card independent review, CHANGES to the original
  implementer, human escalation after two substantive failures.
- Risk: a development-accepted implementation can still be wrong on Windows or
  macOS. Mitigation is that its exposure stays disabled, its deferred obligations
  stay listed and blocking, and the unqualified targets are refused rather than
  assumed compatible.

## Alternatives considered

1. Remove the native-campaign edges from the affected cards. Rejected: B01/B03/B05/
   B06 supply semantics, not only confirmation; removing them would let an
   implementer invent archive, password and cancellation behavior.
2. Wait for the native campaigns before any further implementation. Rejected by
   the operator decision; it also leaves contract-only work idle for reasons
   unrelated to that work.
3. Substitute mocks for native evidence. Rejected: AGENTS.md forbids mock
   qualification evidence, and it would produce a false compatibility claim.
