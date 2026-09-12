# Autonomous archive migration engineering

## Human-facing language

Telegram-facing explanations, status notifications, BLOCKED/TRIAGE details,
approval requests, progress/review reports, failures, recommendations and human
decision questions default to concise, professional Simplified Chinese. Use that
language for human-facing Kanban summaries and reasons as well.

Preserve task IDs, branch/profile names, filenames/paths, Rust/C/C++ identifiers,
API/command names, enum values, Kanban state tokens and CI job names exactly.
Use Chinese plus the original technical term where useful. Never translate raw
compiler/shell errors, CI output, stack traces or important log excerpts: present
the explanation under `中文解释:` and unchanged evidence under `原始信息:`. Label
existing redacted/truncated excerpts honestly; do not duplicate or alter evidence.

Keep repository artifacts primarily English: this file, source/comments,
architecture documents, ADRs, CI configuration and commit messages. This is only
a presentation policy; migration semantics, acceptance criteria, Kanban behavior,
security and execution policies are unchanged.

## Principle and direction

This is an incremental **strangler migration**, never a whole-repository rewrite
or mechanical C++ to Rust translation. Legacy behavior is the behavioral oracle
until characterized by tests. First establish automation, archaeology, and tests;
only then begin production migration. Retain mature C/C++ archive formats,
compression algorithms, encryption, and compatibility-sensitive codec logic.

Target platforms: Windows, Linux, macOS. Provisional architecture:

```text
Qt 6 / QML
    |
CXX-Qt
    |
Rust application core
    |
existing mature C/C++ archive engine
```

Validate this direction through archaeology and ADRs. Do not silently substitute
Slint or another GUI framework. A material architecture change requires an ADR
with evidence and human review before implementation.

## Migration order

1. Repository archaeology.
2. Characterization and regression tests.
3. Architecture definition.
4. Rust workspace skeleton.
5. C/C++ to Rust bridge.
6. Rust CLI archive listing.
7. Rust CLI extraction.
8. Rust CLI archive testing.
9. Rust CLI archive creation.
10. Task, progress, cancellation infrastructure.
11. Cross-platform filesystem abstraction.
12. Qt/QML GUI.
13. Windows/Linux/macOS desktop integration.
14. Native cross-platform release validation.
15. Optional, separately justified codec migration.

Do not skip directly to GUI migration. M3 may begin only after reviewed M1 and M2.

### Development-first sequencing, deferred native qualification

Human decision (2026-09-12): Linux, Windows and macOS real-machine verification
is deferred to later work; mainline development proceeds first. Development
acceptance and qualified/release acceptance are separate.

A card may proceed on development acceptance when its remaining dependency on a
deferred platform campaign is evidence-only, meaning the campaign supplies
confirming platform evidence rather than a semantic, ownership, safety or
licensing input the implementation needs. Dependencies that supply such inputs
stay in force and are not removed to make a card runnable.

Deferral changes ordering only. It does not waive ordinary local compilation,
unit tests or self-owned contract tests, does not authorize mocks as
qualification evidence, and does not relax the compatibility, safety, licensing
or independent-review requirements in this file. Deferred native obligations
remain open on their existing cards and must never be deleted, completed,
archived or represented as passed. Capabilities whose native behavior is not yet
qualified stay unavailable or disabled by default rather than given invented
behavior. Release still requires every originally mandated native evidence item.

## Compatibility and test oracle

Preserve archive-format semantics, compression, encryption, password handling,
Unicode filenames, path handling, timestamps, permissions, CRC/hash semantics,
corrupted archive handling, overwrite behavior, cancellation, and large files
unless explicitly approved. Preserve this fork's filename code-page features.

Never edit golden/expected regression data merely to make an implementation pass.
Investigate disagreements; fix new code when legacy behavior is known. Otherwise
BLOCK the relevant card for a human decision. Native Windows is the canonical
environment for Win32 behavior; Wine and Linux cross-compilation do not establish
Windows compatibility. Require native Linux, Windows, and macOS CI evidence;
distinguish CLI coverage from GUI and desktop integration coverage.

## Rust and boundaries

Prefer safe Rust. Unsafe is limited to justified FFI, low-level platform
integration, or narrowly justified low-level implementation. Every unsafe block
documents its invariant. Explicitly document ownership, lifetimes, threading,
errors, and cancellation across FFI. Application/domain Rust must not depend
directly on HWND, HANDLE, Registry, COM, or other Win32 objects.

## Autonomy and escalation

Proceed without human questions for minor reversible decisions when tests define
behavior, architecture defines the boundary, or a failure has an engineering
cause. Use isolated worktrees and small dependency-aware cards. Separate the
orchestrator, architect, coder, tester, and independent reviewer roles. The
orchestrator normally creates and links work rather than implementing production
code. Parallelize only independent boundaries without competing architecture
decisions or strongly overlapping edits. Maximum two active workers globally,
one per profile initially.

BLOCK instead of guessing when archive semantics are ambiguous, encryption or
password behavior may change, data loss is possible, overwrite/delete behavior is
ambiguous, licensing is unclear, major architecture must change, legacy behavior
conflicts with regression expectations, compatibility could break, substantial
legacy removal is proposed, or the same substantive problem survives two failed
attempts. Explain the exact issue, evidence, two or three options, a recommendation,
and each option's impact. Record the decision on the card; resume only after the
required human answer. Independent eligible cards continue.

For human gates use `hermes kanban block --kind needs_input TASK REASON`.
This Hermes version can promote an initially blocked card without a typed block
event; `create --initial-status blocked` alone is not a durable human gate.
Credential activation requires the credential and verification evidence, not an
additional permission request after the user has already authorized setup.
Never archive an unresolved gate or unreviewed prerequisite: Hermes treats an
archived parent as satisfied and can release dependent work.

Use durable Telegram subscriptions owned by the default gateway, preferably
notify+wake. Children must inherit subscriptions (creator_task_id and dependency
links), or subscribe them explicitly. BLOCKED, gave_up, crash, timeout, and
milestone completion must reach the operator. Keep notifications concise and tool
chatter off. A notification wake is not human approval. Never invent approval or
unblock a semantic, credential, or bootstrap gate without evidence resolving it.

## Engineering and review loop

Every production card specifies scope, non-scope, acceptance criteria, isolated
worktree/branch, tests, compatibility checks, reviewer, two-failure retry bound,
and human-block policy. Read this file in the worktree before working.

Implement -> build/test -> request review with `--reviewer reviewer` -> independent
PASS -> done. CHANGES uses Kanban request-changes to return the SAME card to its
original implementer; repair and re-review. Do not generate endless repair cards.
Count repeated substantive review failures as well as runtime failures; block
after two failed attempts. A reviewer must not rubber-stamp or become the author.

Code generation is not completion. Record changed files, exact build and test
commands, their results, compatibility evidence, commit/branch and artifact paths,
and remaining risks. Documentation-only cards state why executable tests are not
applicable and check links, paths, and evidence. Commit deliverables before review.

## Git, integration, and secrets

Preserve existing work and the legacy baseline. Never reset --hard user work,
clean -fd, force push, rewrite shared history, discard uncommitted changes, delete
legacy sources, merge destructive changes automatically, or publish releases.
Never commit tokens, keys, OAuth credentials, auth.json, or secret environment
files. Back up and inspect existing Hermes config before merging changes; preserve
unrelated provider/auth settings and validate the result.

The bootstrap branch `ai/migration-bootstrap-20260911` is the local automation
base, initially descended from `dev-main`; it must contain AGENTS.md before
workers are dispatched. Never auto-merge into dev-main or another shared branch.
Hermes creates worktrees from the source checkout's current HEAD. Keep that
checkout on the automation base; verify its branch and the worktree's AGENTS.md
before each task. Block a base mismatch rather than starting migration from an
unverified branch.
Each task starts an isolated branch from the automation base. Before work, bring
required reviewed parent commits into that task's branch with ordinary Git merges
or cherry-picks; inspect parent card results and paths. Resolve routine conflicts
without discarding work. Only independently reviewed, non-destructive changes may
be integrated locally into the automation base, serially by the reviewer; check
cleanliness, record integration evidence, and rerun relevant checks first.
Push reviewable task branches when useful; no shared-branch merge or release.
Parent results must identify commits and artifact locations so dependent tasks
can consume them even before local integration. Never rely solely on a parent
worktree persisting after completion.
