# Bootstrap report — complete

Verified 2026-09-11: **bootstrap is complete and autonomous migration is active**.
G0 is DONE; M0 `t_48d08249` is RUNNING under architect in an isolated worktree.
The persistent gateway dispatches eligible descendants through independent review.
No additional bootstrap credentials, manual configuration or approval are needed.

## Discovered and preserved

Repository: `/home/ding/work/github/r404r/7zip`, a C/C++ 7-Zip 26.03 fork with
Win32 desktop/shell code and existing portable CLI makefiles. Initial working
tree was clean on `dev-main`, commit `143e2c5dd24d084614ba32017a72d822cd2bea75`.
The shared branch and legacy source baseline are preserved. Local baseline tag
`legacy-win32-pre-rust-migration` points to that commit; no tag was overwritten.

GCC/G++ 15.2 and Rust 1.97.1 are installed. Qt 6, CMake, Ninja and Clang are not
locally available; they are later architecture/build prerequisites, not blockers
for current archaeology or the retained GCC CLI. No GUI framework was changed.

## Changes and verified runtime

| Item | Actual result |
| --- | --- |
| Repository governance | AGENTS.md committed in automation base before worktrees; strangler strategy, compatibility oracle, safety, review and escalation policies |
| Git | Review branch `ai/migration-bootstrap-20260911`, [draft PR #1](https://github.com/r404r/7zip/pull/1); no shared-branch merge or release |
| Hermes version | v0.21.1 (2026.9.7), upstream `8068c094` |
| Codex version | codex-cli 0.154.0; existing ChatGPT login reused without changing Codex auth |
| Provider/model | Supported `openai-codex` / `gpt-6-astra`; real default model request passed |
| Profiles | orchestrator, architect, coder, tester, reviewer; each passed a real model request; separate roles/session contexts |
| Authentication | Private root Hermes auth imported via installed helper; new workers use supported provider-state fallback; existing profiles preserved |
| Gateway | Single default `hermes-gateway.service`, active/running, enabled, Restart=always |
| Persistence | User systemd with Linger=yes, enabled without sudo; physical reboot not performed |
| Dispatcher | Embedded singleton, 60-second loop, actual task and reviewer dispatch observed |
| Concurrency/retries | Two total workers across boards; one per profile on migration board; two-failure bounds, two-hour milestone runtime caps |
| Kanban | Dedicated archive-rust-migration board; integrity_check=ok, foreign keys clean, correct prerequisite DAG |
| Telegram | getMe/getChat/direct send/polling verified; owner accepted, unlisted sender rejected; real incoming confirmation recorded |
| Access control | Private owner/chat allowlist, public flags false, groups disabled, unknown DMs ignored; worker env files lack bot credentials |
| Notifications | Seven existing cards subscribed through durable default-owned notify+wake; blocked, completion and G0 delivery verified |
| Worktree proof | B1 executed by coder and independently repeated by reviewer; DONE without file changes |
| Production scope | No production codec/encryption/GUI rewrite started; M0 is source archaeology only |

Existing Hermes model/provider settings outside the requested default change were
preserved. Config was inspected, backed up and merged; installed validation passed.
No global or profile execution-approval setting was weakened. Comparison against
the pre-role tester config confirmed approval/security/terminal/agent sections
remain unchanged. Token, allowlist and gateway were not reconfigured after the
operator's later instruction to preserve the verified connection. A later graceful
service restart loaded only the requested presentation-language change; Telegram
credentials, routing and access controls remained unchanged.

## B2 repair and end-to-end evidence

The same B2 card `t_d905f0a0` was retained throughout. Initially the real incoming
Telegram `bootstrap-confirm` resolved its human-message gate. Its inline Python
and execute_code attempts were then rejected before execution by the installed
single-query approval policy. The existing two-cycle block guard routed it to
TRIAGE. No successful result was claimed for either rejected attempt.

The narrow repair was the committed, inspectable 14-line
`scripts/ai-migration/telegram-probe.py` at `d76f778`. It contains only an optimize
flag guard, the exact harmless arithmetic assertion and its result message. It has
no credentials, network access, archive operations or filesystem writes. The
existing policy already permitted ordinary script-file execution; no permission
change or extra approval transport was necessary.

Tester run **8** and independent reviewer run **9** each read the script and ran:

```sh
python3 -B /home/ding/work/github/r404r/7zip/scripts/ai-migration/telegram-probe.py
```

Both exited **0**, with `PASS: 2 + 2 == 4 (assertions enabled)`. Reviewer PASS
completed B2. The verified real incoming Telegram message is durable record **19**,
with a platform message ID and authorized source matching the private allowlist;
it predates the reviewer run. Synthetic notify+wake messages were explicitly
excluded from this proof. No private user ID or token is included here.

B2 completed event **60** belongs to reviewer run **9**. Both `last_event_id` and
`last_ping_event_id` covered event 60, verifying notify/wake and passive delivery.
G0 then completed as event **61**, also covered by both notification cursors.
The live systemd PID matched gateway runtime state with Telegram connected.

An independent read-only audit confirmed authorization, private permissions,
worker credential isolation, subscriptions, polling and no fatal service errors.
Possible duplicate-send warnings were observed; delivery is not claimed to be
exactly once. `kanban.done_sub_retention_days: 0` prevents a long-paused human gate
from silently losing its subscription after the installed default 30-day expiry.

## Initial DAG and actual task state

| Card | ID | Assignee | State at verification |
| --- | --- | --- | --- |
| G0 bootstrap gate | `t_5f1b2423` | orchestrator | DONE, all prerequisites verified |
| M0 archaeology | `t_48d08249` | architect | RUNNING, worker run 11 |
| M1 characterization | `t_f4afeee1` | tester | TODO, depends on reviewed M0 |
| M2 target architecture | `t_db8ffe0b` | architect | TODO, depends on reviewed M0 |
| M3 detailed migration DAG | `t_82c76197` | orchestrator | TODO, depends on BOTH reviewed M1 and M2 |
| B1 worktree/review test | `t_181faa42` | reviewer | DONE, independent PASS |
| B2 Telegram lifecycle test | `t_d905f0a0` | reviewer | DONE, independent PASS and notification verified |

First migration task: **M0 t_48d08249**, branch `ai/migration-m0`, worktree
`/home/ding/work/github/r404r/7zip/.worktrees/t_48d08249`, based on committed
bootstrap `d1fcc44`. Its log shows actual AGENTS.md/source inspection. M0's acceptance
criteria require four architecture/boundary/risk documents and independent review.
No broad production implementation is authorized before reviewed archaeology,
characterization and architecture. M3 creates actual remaining cards gated on its
own review; subsequent production work follows the existing DAG and AGENTS.md.

## Builds, tests and Git safety

The retained CLI built locally with GCC/G++ 15.2. Temporary 7z/ZIP
create/list/test/extract smoke passed, including Unicode paths and exact bytes;
six existing portable checks passed. Genuine native CI passed on Linux/macOS and
Windows at `7e4ec5a`, and again at governance/docs commit `a9a25a9`:
[Linux/macOS run 34549555370](https://github.com/r404r/7zip/actions/runs/34549555370),
[Windows run 34549555271](https://github.com/r404r/7zip/actions/runs/34549555271).
The existing Windows workflow is unchanged and its branch release job was skipped.
Later Telegram/bootstrap documentation and probe commits do not change the legacy
engine or tested build recipe; their exact CI status is available on the draft PR.
These are legacy build/smoke results, not proof of a migrated Qt/Rust desktop.

Known-secret scans passed on changed artifacts, including the supplied bot token.
Credentials and runtime state remain outside Git with restrictive permissions.
Only explicit infrastructure/docs/probe paths were committed; unrelated work was
preserved. Branch push authentication was exercised; no force push, shared merge,
legacy deletion or release occurred.

## Telegram presentation-language verification

Default and all five migration profiles now use `display.language: zh` and an
English role-policy instruction requiring concise Simplified Chinese for human-facing
Telegram prose. Repository engineering artifacts remain English. Identifiers and
raw technical evidence are preserved; existing sanitized/truncated excerpts are
explicitly labelled. AGENTS.md carries the policy for future worktrees.

This Hermes version hardcodes passive Kanban messages in English. A small local
formatter patch adds Chinese only for Telegram with the Chinese locale, leaving
other platforms, payloads, wake handoffs, routing, cursors and execution controls
unchanged. The reproducible patch and its two regression tests are preserved in
`scripts/ai-migration/hermes-telegram-zh.patch`. Revalidate this local patch after
an intentional Hermes update; it is not an upstream-supported locale extension.

The canonical Hermes runner passed **35 tests across six files**, covering language,
unchanged evidence/disclosure bounds, notification deduplication and notify+wake
routing/acceptance. A real default model response followed the Chinese policy.
One harmless Chinese test message was actually sent through `hermes send` (exit 0).
No new inbound reply was demanded: the existing genuine Telegram record 19 remains
the inbound proof. After graceful reload, systemd and gateway PID **515959** matched,
Telegram was connected, dispatcher logged its 60-second loop, and M0's existing
worker continued. All six parsed configs differ from the pre-language backups only
in display.language; model/security/execution/Telegram/Kanban settings are intact.

## Private backups

All are under `~/.hermes/backups/`, outside Git, with 0700 directories and 0600 files:

- `archive-migration-20260911T005519Z`: original default config/env/persona,
  existing profile configs and initial new-profile config/env/persona.
- `archive-migration-role-audit-20260911T010610Z`: role prompts before audit fixes.
- `archive-migration-telegram-20260911T014012Z`: config/env/coordinator before activation.
- `archive-migration-notify-retention-20260911T014535Z`: config before retention change.
- `archive-migration-active-20260911T015656Z`: coordinator before active-operation handoff.
- `archive-migration-language-policy-20260911T020245Z`: default and five profile
  config/persona files before the Chinese presentation policy.
- `archive-migration-language-20260911T020157Z`: installed notifier before localization.

## Remaining limitations and human action

No bootstrap action remains for the operator. Semantic ambiguity, encryption,
compatibility/data-loss risk, unclear licensing, major architecture changes and
release/publication still require the explicit human escalation policy. The
per-profile running cap is board-local; semantic review retry counting is
role-enforced. Keep the source checkout on the automation base because Hermes
creates worktrees from its current HEAD. Never archive an unresolved prerequisite:
Hermes treats archived parents as satisfied. An initial blocked status alone is
not a durable gate; record a real typed block event.

Recovery/reference: [HERMES-RUNBOOK.md](HERMES-RUNBOOK.md).
Environment: [environment-inventory.md](environment-inventory.md).
Runtime: [hermes-runtime.md](hermes-runtime.md).
CI coverage: [ci-validation-plan.md](ci-validation-plan.md).
