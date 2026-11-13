# Environment inventory

Inspected 2026-09-11, Ubuntu 26.04.1 LTS, Linux x86-64, user `ding`, Asia/Tokyo.

| Item | Observed state before bootstrap |
| --- | --- |
| Repository | `/home/ding/work/github/r404r/7zip` |
| Git | Clean tracked and untracked working tree; branch `dev-main` |
| HEAD | `143e2c5dd24d084614ba32017a72d822cd2bea75` |
| Remote | `git@github.com:r404r/7zip.git`; GitHub |
| Authentication | `git ls-remote origin HEAD` succeeded; GitHub CLI authenticated as repository owner |
| Project | Personal 7-Zip 26.03 fork; C/C++ archive engine, Win32 desktop and shell, filename code-page customizations |
| Build | Existing MSVC/nmake Windows builds and GNU make GCC/Clang portable CLI makefiles; no Rust workspace or Qt build detected |
| C/C++ | GCC and G++ 15.2.0 installed; Clang absent from PATH |
| Rust | rustc 1.97.1; cargo 1.97.1 |
| Qt | No qmake/qmake6/qtpaths/qtpaths6 or installed qt6 packages discovered |
| Other build tools | GNU make available; CMake and Ninja absent from PATH |
| Codex | `codex-cli 0.154.0`; `codex login status`: logged in using ChatGPT |
| Hermes | v0.21.1 (2026.9.7), upstream `8068c094`; git install under `~/.hermes/hermes-agent` |
| Hermes Python | 3.11.16, `~/.hermes/hermes-agent/venv/bin/python`; OpenAI SDK 2.24.0 |
| Original default model | `anthropic/claude-opus-4.6`, provider `auto`, OpenRouter base URL |
| Existing worker profiles | `research-hermes`, `work-lab`, already configured for `openai-codex` / `gpt-6-astra`; untouched |
| Original default Hermes auth | No stored Codex credentials; reusable current Codex CLI credentials present |
| Telegram | No configured bot token or authorized numeric user ID in inspected profile env files or process environment |
| Initial gateway | Stopped; no persistent user gateway; user systemd available but overall manager degraded; linger initially disabled |
| Existing CI | `.github/workflows/build-windows.yml`; native Windows MSVC, CLI/GUI/shell builds, regression and MSI checks |

Inspected `pwd`, Git status/branch/remotes/log, both CLI versions and help, Hermes
profile/gateway/kanban/model help, auth status, compiler/build-tool versions,
package discovery, user systemd, profiles, and config structure without printing
credential values. `hermes model` is an interactive picker and refused stdin;
the installed help, source, configuration validator and real model requests were
used instead. No installed tool upgrade was required.

Hermes supports `hermes -p PROFILE`, `profile create --clone-from`, a dedicated
board with `boards create --default-workdir`, isolated `worktree:<repo>` tasks,
repeatable prerequisite `--parent`, per-card `--max-retries`, gateway-embedded
dispatch, reviewer routing and `request-changes`, and durable
`notify-subscribe --delivery-mode notify+wake`. See [runtime](hermes-runtime.md)
for exact configured values and [runbook](HERMES-RUNBOOK.md) for recovery.

The historical native Windows run on `dev-main` was observed successful:
[run 34005718363](https://github.com/r404r/7zip/actions/runs/34005718363).
This is evidence for that run, not a claim of Rust or cross-platform desktop
support. See [CI validation plan](ci-validation-plan.md) for new evidence.

Bootstrap creates local tag `legacy-win32-pre-rust-migration` at the original
HEAD and the separate automation base branch `ai/migration-bootstrap-20260911`.
No source implementation changes are needed for bootstrap. Qt/CMake/Ninja/Clang
installation remains a later architecture/build prerequisite; the retained CLI
already builds with installed GCC and make. No sudo is needed for current work.
