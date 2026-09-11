# Bootstrap report — Telegram credentials required

Status as of 2026-09-11: **bootstrap is not complete**. All independently feasible
repository, provider, profile, service, board and native CI setup has been executed
and checked. The remaining external blocker is the Telegram Bot token and the
operator's numeric Telegram user ID. No value for either was found securely
configured. Actual Telegram notification/inbound tests and M0 dispatch remain
gated until those values are supplied and the path is verified.

## Discovered and changed

- Clean 7-Zip 26.03 fork on `dev-main`, original commit
  `143e2c5dd24d084614ba32017a72d822cd2bea75`; source and user work preserved.
- Created local baseline tag `legacy-win32-pre-rust-migration` without overwriting
  any tag; created and pushed review branch `ai/migration-bootstrap-20260911`.
  Shared `dev-main` is unchanged. No release tags or releases were pushed.
- Installed repository AGENTS.md, ignored local worktrees/private runtime paths,
  and committed governance before the first isolated worktree task started.
- Configured Hermes `openai-codex` / `gpt-6-astra` using valid existing Codex login;
  retained unrelated configuration and existing profiles. Created five specialist
  profiles with separate role contexts and supported root credential fallback.
- Created dedicated board, real dependency links, bounded retries, independent
  review policy, single embedded dispatcher and a persistent user systemd service.
- Added native Linux/macOS retained-CLI CI and temporary smoke fixtures. Preserved
  existing Windows workflow byte-for-byte. No C/C++/Rust production file changed.

## Verified runtime

| Check | Evidence/status |
| --- | --- |
| Hermes | v0.21.1 (2026.9.7), upstream `8068c094` |
| Codex CLI | 0.154.0; authenticated with ChatGPT |
| Provider | Real default request returned HERMES_CODEX_BOOTSTRAP_OK |
| Profiles | orchestrator, architect, coder, tester, reviewer each passed its own real model request |
| Config | Installed structure validator passed; configured keys traced to installed code |
| Gateway | hermes-gateway.service active/running, enabled, Restart=always |
| Logout/boot persistence | Linger=yes; enabled without sudo; no physical reboot test performed |
| Dispatcher | Gateway logs show singleton lock, 60-second loop and actual worker/reviewer dispatch |
| Concurrency | Two total across boards; one per profile on migration board; other board empty |
| Kanban database | SQLite integrity_check=ok; foreign_key_check empty; no active diagnostics |
| Worktree/review | B1 `t_181faa42` DONE after actual coder execution and separate reviewer PASS |
| Telegram | Not configured; zero durable subscriptions; no outbound or inbound success claimed |
| Production migration | Not started; no codec or encryption rewrite |

B1 actually created an isolated worktree based on committed governance, read
AGENTS.md, ran the existing release-version regression script (zero failures),
checked clean status and diffs, and requested the reviewer. The separate reviewer
repeated those checks and completed the card. Both runs and command/result
metadata are durable in Kanban. No files were changed by this smoke.

An independent read-only bootstrap audit checked policy keys, gate behavior, DAG,
worktree base, service and database. It identified and prompted documentation of
initial-block promotion, archived-prerequisite satisfaction and current-HEAD
worktree creation. These safeguards are now explicit in AGENTS.md and role prompts.

## Initial DAG and current state

| Card | ID | Assignee | State / prerequisite |
| --- | --- | --- | --- |
| G0 bootstrap/Telegram activation | `t_5f1b2423` | orchestrator | BLOCKED, durable needs_input event |
| M0 repository archaeology | `t_48d08249` | architect | TODO, waiting only on G0 |
| M1 characterization | `t_f4afeee1` | tester | TODO, depends on reviewed M0 |
| M2 target architecture | `t_db8ffe0b` | architect | TODO, depends on reviewed M0 |
| M3 detailed migration DAG | `t_82c76197` | orchestrator | TODO, depends on BOTH reviewed M1 and M2 |
| B1 worktree/review probe | `t_181faa42` | reviewer | DONE, independent PASS |
| B2 Telegram lifecycle probe | `t_d905f0a0` | tester | BLOCKED, needs credentials and real authorized reply |

First migration task: **M0 `t_48d08249`**, fully specified and awaiting the Telegram
bootstrap gate. M0–M3 have not run. G0 was initially promoted because a bare
initial blocked status is not sticky in this installed version; its worker
correctly recorded a needs_input block without releasing migration. Subsequent
dispatcher ticks and the independent audit confirmed the gate holds. Never
archive a blocked gate or unreviewed prerequisite to bypass it.

All milestone cards use isolated Git worktrees/branches, require review, specify
non-scope/acceptance/evidence and have two-failure bounds and two-hour runtime caps.
M3 will create actual remaining cards only after reviewed M1/M2, and those cards
must depend on M3's review. Review CHANGES returns the same card to its implementer.

## Validation and Git evidence

Retained CLI built locally with GCC/G++ 15.2; 7z and ZIP create/list/test/extract
smoke passed, including nested Unicode paths and exact bytes. Six existing
portable checks passed. At infrastructure commit
`7e4ec5a0a13976ab7d5a89cc0cc43b7451a443dd`, genuine
[Linux/macOS CI](https://github.com/r404r/7zip/actions/runs/34548991963) and
[Windows MSVC/CI](https://github.com/r404r/7zip/actions/runs/34548991981) passed.
The Windows release job was skipped. This is legacy CLI/build/regression evidence,
not proof of migrated Qt/Rust desktop compatibility. See the
[CI validation plan](ci-validation-plan.md) for exact commands and coverage limits.

GitHub read and branch-push authentication were exercised successfully. The
review branch holds the committed infrastructure; the original shared branch and
legacy implementation are preserved. Final documentation changes are additive.
The changed-file scan against known local credential material passed without
printing secrets. All changed paths are governance, documentation, ignores or
the new CI/smoke infrastructure; legacy source and existing CI have zero diff.

## Private backups

- `~/.hermes/backups/archive-migration-20260911T005519Z/`: original default config,
  env and persona; existing profile configs; initial new-profile configs/env/personas.
- `~/.hermes/backups/archive-migration-role-audit-20260911T010610Z/`: role prompts
  before audit safeguards were added.

Backup directories are 0700 and files 0600. Secret-containing runtime files are
0600. The default had no auth.json before import; existing Codex and preexisting
profile credentials were not overwritten. Backups and credentials are outside Git.

## Remaining work requiring external input

Supply only the **Telegram Bot token** and **numeric Telegram user ID**. The
bootstrap operator will back up and merge private configuration, verify bot/chat
connectivity and authorization, subscribe all existing cards with notify+wake,
and run B2's real blocked-notification/reply/unblock/completion cycle. Telegram
may require the operator to start the bot before it can send a DM; request that
only if the API demonstrates it is necessary. Never fabricate an inbound reply.

After actual verification, the existing user authorization permits completing G0
without another abstract permission question. The dispatcher then starts M0 and
progresses through eligible dependencies with independent review. Update this
report with the observed Telegram and M0 statuses at that point.

Qt 6, CMake, Ninja and Clang are not installed locally; they are later build/GUI
prerequisites and do not block current archaeology or the GCC legacy CLI. Major
architecture or compatibility decisions remain human gates. The per-profile cap
is board-local, semantic review retry counting is role-enforced, and worktree
creation relies on the source checkout staying on the automation base branch.

Recovery/reference: [HERMES-RUNBOOK.md](HERMES-RUNBOOK.md).
Environment details: [environment-inventory.md](environment-inventory.md).
Runtime details: [hermes-runtime.md](hermes-runtime.md).
