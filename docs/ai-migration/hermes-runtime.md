# Hermes migration runtime

Installed and exercised: Hermes v0.21.1 (2026.9.7), upstream `8068c094`, Codex CLI
0.154.0. Installed CLI help and source are the configuration authority for this
host; no unsupported policy keys or package upgrades were introduced.

## Provider and profiles

Default model is now `gpt-6-astra`, provider `openai-codex`, supported base URL
`https://chatgpt.com/backend-api/codex`. This matches the host's existing working
Hermes profiles. The previous default model section is backed up. Other default
settings and the existing `research-hermes` and `work-lab` profiles are preserved.

The installed `_import_codex_cli_tokens` and `_save_codex_tokens` helpers imported
valid existing CLI credentials into Hermes's private root auth store without
writing to Codex's auth file. No OAuth interaction was necessary. New profiles
use Hermes's supported global provider-state fallback rather than copied tokens.
Refresh handling remains owned by Hermes. No credential contents enter Git.

The default profile returned `HERMES_CODEX_BOOTSTRAP_OK` from a real request.
Each specialist returned its own `PROFILE_<ROLE>_OK` in a real request; all five
exited successfully. Provider testing used at most two simultaneous calls.

| Profile | Role |
| --- | --- |
| default | Single gateway/dispatcher and human-facing migration coordinator |
| orchestrator | Milestones, small dependency-aware DAGs; normally no production edits |
| architect | Archaeology, ADRs, FFI and Rust/platform boundaries |
| coder | Scoped implementation, build/test, reviewer handoff |
| tester | Characterization, fixtures, compatibility, native CI |
| reviewer | Independent behavior/FFI/unsafe/path/error/regression review |

Specialists were created through `hermes profile create NAME --clone-from default
--no-alias --description DESCRIPTION`; each has a separate SOUL.md, config and
session context under `~/.hermes/profiles/NAME`. The `kanban` toolset is explicitly
enabled for the default coordinator and specialists. No worker Telegram gateway
is installed. Worker `dispatch_in_gateway` is false; the default owns dispatch.

## Supported dispatcher configuration

The following keys are read by the installed gateway dispatcher or Kanban code:

```yaml
kanban:
  dispatch_in_gateway: true
  dispatch_interval_seconds: 60
  review_dispatch: true
  max_in_progress: 2
  max_in_progress_per_profile: 1
  failure_limit: 2
  auto_promote_children: true
  auto_decompose: false
  orchestrator_profile: orchestrator
  default_assignee: coder
  done_sub_retention_days: 0
```

Board: `archive-rust-migration`; default workspace:
`/home/ding/work/github/r404r/7zip`. Task workspaces explicitly use `worktree`;
the board's default alone does not turn a scratch card into a worktree.
The dispatcher holds `~/.hermes/kanban/.dispatcher.lock` and scans boards.
The total cap is host-wide across boards. The per-profile cap is board-local in
this version; the migration is the only populated board. Do not claim a host-wide
per-profile cap if other boards are later populated.

Milestones have `--max-retries 2` (block on the second failure, not two further
retries) and `--max-runtime 2h`. Runtime/spawn/crash/timeout failure accounting is
implemented by Hermes. Counting repeated substantive review failures additionally
relies on the reviewer role and AGENTS.md; there is no invented YAML circuit
breaker for semantic review. Use the same card and original implementer for fixes.

Review dispatch by itself can use the assignee; every implementer is instructed
to request review explicitly with `--reviewer reviewer`. Parent cards remain
incomplete until independent PASS. M3's new production children must depend on M3
so they cannot run before its review succeeds.

Important installed-version behavior: an initial `blocked` status without a typed
block event can be promoted. The bootstrap gate was picked up once, and the
orchestrator correctly recorded `needs_input` and stopped without releasing M0.
Use `kanban block --kind needs_input TASK REASON` for durable human gates.
Never archive an unresolved gate: archived parents also satisfy dependencies.
Worktrees start from the source checkout's current HEAD, so that checkout must
stay on the automation base; there is no fixed base-ref option configured here.

## Service and notifications

`hermes -p default gateway install --no-start-now --start-on-login` installed the
user unit; `gateway start` started it. `hermes-gateway.service` is enabled,
active/running, and uses `Restart=always`. Linger is enabled, without sudo.
Gateway logs confirm a singleton embedded dispatcher with a 60-second interval.
The gateway now has a verified Telegram polling adapter. getMe and the private
getChat succeeded; polling health and direct message delivery were observed.

`display.tool_progress: off` suppresses normal tool chatter. The installed durable
notifier handles completed, blocked, gave_up, crashed, timed_out, review_requested,
changes_requested and related state events. `notify+wake` is supported. Subscribers
inherit through parent links and creator_task_id, but subscriptions added after
children already exist must be installed on those children explicitly.

Telegram credentials supplied by the operator were merged into private `.env`.
`TELEGRAM_ALLOWED_USERS` contains only the operator; both
`TELEGRAM_ALLOW_ALL_USERS` and `GATEWAY_ALLOW_ALL_USERS` are false. Telegram policy
is allowlist-only for DMs, groups disabled, unauthorized DMs ignored, and the
allowed chat is restricted to the private operator conversation. All seven
existing cards have durable `notify+wake` subscriptions owned by default.
The actual configured adapter accepted the owner and rejected an unlisted sender;
unauthorized DMs cannot enter pairing. A blocked event was delivered and its
persistent subscription cursor advanced. The same notification woke the default
coordinator, which correctly refused to invent an incoming human reply.
The real authorized reply and unblock were recorded. B2 completed after tester
and independent reviewer executed the committed harmless script. Completion event
60 belongs to reviewer run 9 and both durable cursors advanced through it. The
actual incoming message record 19 preceded that review. Automatic notification wakes are never human decisions.

## Backups and validation

Private timestamped backup directory:
`~/.hermes/backups/archive-migration-20260911T005519Z/`.
It includes original default config, `.env`, SOUL.md and existing profile configs,
plus each newly created profile's initial config/SOUL/.env before role edits.
Directory mode is 0700; backup files and runtime secret/config files are 0600.
The original default had no auth.json. Existing Codex and profile auth stores were
not replaced. The default configuration was section-merged and checked to preserve
all unrelated parsed values. Installed `validate_config_structure` passed.

A second private role-prompt backup was created before audit safeguards:
`~/.hermes/backups/archive-migration-role-audit-20260911T010610Z/`.
Final validation passed for all six configuration structures and runtime secret
permissions. B1 t_181faa42 completed after independent reviewer PASS. A Telegram
activation backup is at `~/.hermes/backups/archive-migration-telegram-20260911T014012Z/`.
B2 and G0 are DONE after end-to-end confirmation. M0 is RUNNING under architect
in its isolated worktree at bootstrap base d1fcc44, with committed AGENTS.md.
B2 completed event 60 (review run 9) and G0 completed event 61 were both delivered
with notify+wake and confirmed through both durable cursors. Real authorized
incoming message record 19 precedes the independent review.

Independent Telegram audit verified private permissions, worker credential
isolation, all seven durable subscriptions, healthy polling, and no fatal errors.
The supported done_sub_retention_days=0 disables automatic 30-day expiry of inactive
blocked subscriptions; explicit archive cleanup is retained. Possible duplicate
send warnings were observed, so delivery is not claimed to be exactly once.

## Human-facing language

Default, orchestrator, architect, coder, tester and reviewer use `display.language:
zh`, with role instructions requiring concise Simplified Chinese on Telegram.
AGENTS.md preserves English engineering artifacts and exact technical identifiers
and evidence. The installed passive Kanban formatter required a presentation-only
local patch, recorded in `scripts/ai-migration/hermes-telegram-zh.patch` for Hermes
upstream 8068c094. Its existing redaction/truncation and durable notification logic
are preserved. The canonical runner passed 35 relevant tests; a real model response
and one actual Chinese Telegram send passed. A graceful service reload retained
M0's independent worker scope and restored connected Telegram plus the dispatcher.
No token, allowlist, model, approval, execution or task-policy change accompanied
this language update. See the runbook before updating the locally patched Hermes.
