# Q1 internal ABI v1 contract

Status: IN PROGRESS, not independently reviewed and not an implementation gate PASS.
Task: `t_f4d107ea`. No production header or bridge implementation is introduced.

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

Exact declarations, enum assignments, field layouts, size/alignment checks,
calling convention and matched build handshake remain Q1 deliverables. They are
not qualified by naming alone. No downstream bridge implementation may treat this
in-progress document as a completed exact header contract.
