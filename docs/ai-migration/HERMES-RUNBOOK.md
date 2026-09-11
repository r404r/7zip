# Hermes migration recovery runbook

This is a recovery reference. Normal operation is performed by the persistent
gateway and dependency-aware workers, not by someone remaining at this terminal.
The bootstrap operator configures credentials and runs the verification steps.

## Runtime locations

| Item | Location |
| --- | --- |
| Source and local automation base | `/home/ding/work/github/r404r/7zip`, branch `ai/migration-bootstrap-20260911` |
| Original shared branch | `dev-main`, never automatically merged by migration workers |
| Baseline tag | `legacy-win32-pre-rust-migration` (local; not a release tag) |
| Gateway unit | `~/.config/systemd/user/hermes-gateway.service` |
| Default config/persona | `~/.hermes/config.yaml`, `~/.hermes/SOUL.md` |
| Private credentials | `~/.hermes/.env`, `~/.hermes/auth.json`; never copy into Git |
| Worker profiles | `~/.hermes/profiles/{orchestrator,architect,coder,tester,reviewer}` |
| Board database | `~/.hermes/kanban/boards/archive-rust-migration/kanban.db` |
| Worker logs | `~/.hermes/kanban/boards/archive-rust-migration/logs/` |
| Gateway logs | `~/.hermes/logs/gateway.log`, `~/.hermes/logs/agent.log`, user journal |
| Worktrees | repository `.worktrees/<task-id>`; ignored by Git |
| Configuration backup | `~/.hermes/backups/archive-migration-20260911T005519Z/` |
| Current task mapping | [task-ids.json](task-ids.json) |

Private configuration is permission-restricted. Never paste auth files, env
contents, Telegram tokens, or unredacted diagnostic dumps into a task, PR or chat.

## Service and health

Installed syntax exercised on this host:

```sh
hermes -p default gateway status
systemctl --user show hermes-gateway.service -p ActiveState -p SubState -p Restart -p UnitFileState
loginctl show-user ding -p Linger
journalctl --user -u hermes-gateway.service --since '10 minutes ago' --no-pager
hermes -p default kanban --board archive-rust-migration stats
hermes -p default kanban --board archive-rust-migration diagnostics
hermes -p default kanban --board archive-rust-migration dispatch --dry-run --json
```

Expect active/running, enabled, Restart=always and Linger=yes. The gateway owns
the singleton embedded dispatcher, every 60 seconds, maximum two active workers
and one per profile. A ready task can wait until the next tick. Review runs use
the same caps. Inspect `gateway.log` for dispatcher start/spawn/timeout events.
The total cap spans boards; the per-profile cap is board-local in this version.
Only the migration board currently has tasks.
Missing optional image/browser/media integrations are not fatal to this workflow.
The initial systemd manager's degraded state includes unrelated units; assess
the Hermes unit itself. systemd-analyze reported an unrelated spice-vdagent unit
warning; it did not invalidate Hermes's unit.

After a reviewed configuration repair use `hermes -p default gateway restart`.
The CLI drains in-flight turns; a graceful restart can take time. Use
`hermes -p default gateway start` if stopped. Never run an extra Kanban daemon or
worker gateways alongside this dispatcher. Linger is already enabled so logout
and boot do not require a manual gateway start. A physical host reboot was not
performed during bootstrap.

`hermes -p default auth status openai-codex` and the equivalent `-p architect`
check stored state. A real harmless request checks usability:

```sh
hermes -p default -t '' --reasoning low -z 'Do not use tools. Reply exactly HERMES_CODEX_BOOTSTRAP_OK'
```

Use existing valid authentication before requesting OAuth. New profiles inherit
root provider credentials via Hermes's built-in fallback. Do not duplicate or
replace refresh tokens manually. If live auth fails and supported reuse cannot
recover it, record the exact failure without secrets and request human device
authorization; unrelated work may continue.

## DAG, review, and human decisions

```text
G0 verified bootstrap/Telegram gate
  -> M0 architecture archaeology [architect -> reviewer]
       -> M1 characterization [tester -> reviewer] ---+
       -> M2 target architecture [architect -> reviewer] -> M3 detailed DAG
```

M3 depends on BOTH M1 and M2. Engineering cards request independent review through
`hermes kanban --board archive-rust-migration request-review TASK --reviewer reviewer
--summary EVIDENCE`. Reviewer PASS completes with structured evidence. Reviewer
CHANGES uses `request-changes` (inspect its current help) so the same implementer
repairs the same card; never create unlimited replacement cards. Two substantive
failures require BLOCKED. Runtime/spawn failures additionally have an enforced
two-failure circuit breaker and milestones have a two-hour runtime cap.

Inspect a card and run history using `show TASK --json`, `runs TASK`, or `log TASK`
under the explicit board. Parent results must contain commit and artifact paths.
Workers use isolated branches. Only reviewed non-destructive changes are merged
serially into the local automation base; shared branches and releases stay under
human control. AGENTS.md must be committed in the base before new worktrees start.
Check for unrelated uncommitted work before any local integration.

For human decisions use `block --kind needs_input TASK REASON`. The reason includes
the precise issue, source/test evidence, two or three options, a recommendation
and impacts. **Do not rely on `create --initial-status blocked` alone:** this
version initially promoted G0 until the worker recorded a typed needs_input block.
Ordinary dependency waits use actual parent links, not human blocks. Independent
eligible tasks continue. Never archive unresolved gates or unreviewed parents;
archived parents are treated as satisfied and can release dependent work.

The Telegram coordinator must record an authorized human reply as a task comment
before unblocking a semantic decision. A notification wake is not approval. For
credentials, the user's original setup authorization suffices once the credential
and verification evidence exist; do not ask an additional abstract permission.
After a decision is recorded use `unblock TASK`; tasks with unfinished parents
remain waiting. Emergency `hermes pause` is host/profile automation control;
inspect `hermes pause --help` before using it because it may affect other work.

## Telegram activation and end-to-end test

Telegram credentials have now been supplied and configured privately. The bot and
private chat are reachable, polling is healthy, and durable block delivery passed.
B2 passed the one-time inbound/review/completion probe. For future credential recovery,
the bootstrap operator obtains replacement values, creates a timestamped backup,
and merges them into the private default `.env` using dotenv-aware editing:
`TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS` (one numeric ID),
`TELEGRAM_HOME_CHANNEL` (the verified private conversation), and
`GATEWAY_ALLOW_ALL_USERS=false`. Do not clone these into worker profiles. Inspect
and preserve unrelated credentials; keep `.env` mode 0600 and parent mode 0700.

Verify getMe and an authorized private chat with the Telegram API without printing
the request URL/token. Check whether the user has started the bot; Telegram may
require that human action before a bot can message a private conversation. Only
request it if the API shows it is required. Restart the default gateway and check
its Telegram adapter and authorization state. Send the authorized harmless test
message. Never enable public unrestricted access to bypass an authorization error.

Subscribe G0 and every existing M0/M1/M2/M3 and test card explicitly using the
supported `notify-subscribe` options `--platform telegram --chat-id PRIVATE_CHAT
--user-id AUTHORIZED_ID --chat-type dm --notifier-profile default
--delivery-mode notify+wake`. The operator reads private identifiers securely;
these placeholders are not literal configuration values. Verify persisted rows
with `notify-list`. Existing descendants do not retroactively inherit a newly
added parent subscription; later children inherit through creator_task_id/links.

Create a harmless test card with a typed needs_input block; subscribe BEFORE
emitting the test block event. Verify actual delivered notification and persisted
delivery progress, then ask for one harmless reply in Telegram. Confirm the inbound
source ID passes the allowlist, record that reply on the card, unblock it, and
verify dispatcher execution and independent reviewer PASS. Observe completion
notification delivery as well. Do not fabricate an inbound human reply. Gateway
notifications cover blocked, gave_up, crashed, timed_out and completion; ordinary
tool chatter is off. Review notifications may also appear.

Only after these checks pass, record evidence on G0 and complete it. M0 will be
promoted and dispatched automatically on the next tick. Verify its worktree
contains AGENTS.md. Update BOOTSTRAP-REPORT.md with actual Telegram/M0 status.

## Recovery and backups

Back up existing config before every repair, then merge targeted changes and run
Hermes's installed configuration validator. The initial private backup preserves
the pre-bootstrap default model and persona as well as profile configs. Avoid
restoring stale OAuth files over current valid authentication. Restoring all old
config would also disable current migration policies; use targeted recovery.

For database trouble, stop the gateway gracefully, ensure no active workers are
writing, and take a consistent SQLite backup including WAL state through SQLite's
backup API. Run integrity_check and foreign_key_check. Inspect `hermes kanban
repair --help` before repairs; never delete the board database to fix a task.
Record unresolved errors and keep the affected work blocked.

Do not delete worktrees containing uncommitted changes or unique commits. Inspect
`git worktree list` and the task's branch/result first. Retain the legacy baseline.
Do not reset --hard, clean -fd, force-push, auto-merge shared branches, or publish
releases. Branch pushes can run the existing Windows package build; the existing
release job remains tag-only, and bootstrap pushes no release tags.

## Notification retention and delivery caveats

`kanban.done_sub_retention_days: 0` disables the installed default 30-day expiry
of inactive done/blocked subscriptions, so a long human pause does not silently
remove the remote notification route. Explicitly archiving a task still removes
its subscription; never archive an unresolved prerequisite. Transport retries can
produce a duplicate notification (observed during bootstrap); task/event IDs and
durable cursors identify the underlying event. Do not treat duplicate delivery as
a second human decision or retry a migration task because a ping repeated.

## Noninteractive probe execution

The initial inline Python command was rejected by the installed single-query
approval policy. The same B2 card now runs the inspectable, committed file
`python3 -B /home/ding/work/github/r404r/7zip/scripts/ai-migration/telegram-probe.py`.
The file has no network/filesystem writes or credentials. Tester and reviewer
execute it independently. No approval setting is weakened and no second Telegram
confirmation is needed after the actual source-verified reply is recorded.
