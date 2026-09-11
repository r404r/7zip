# Native CI preparation and validation

Bootstrap inspection date: 2026-09-11. This document distinguishes native CLI
smoke coverage from the characterization baseline M1 must establish.

## Existing Windows verification

`.github/workflows/build-windows.yml` is preserved unchanged. It builds with
MSVC/nmake on `windows-latest`: Alone2 (7zz), archive DLL, GUI, File Manager,
console, Explorer integration, and self-extractors. It runs ZIP filename encoding
regression checks, shell identity, release metadata, modified-file notices,
language files and shell language reload checks, then packages and validates an
MSI. The existing release job is tag-triggered. Bootstrap must push only branches,
never release tags, and must not publish releases.

The ZIP encoding test deliberately asserts only on Windows because code-page
conversion differs on POSIX. Its non-Windows output is not equivalent evidence.
Static shell source checks on Linux likewise do not prove Windows runtime behavior.
The existing workflow is useful Windows coverage, but is not yet a full archive
compatibility oracle or GUI interaction suite. Remote run status must be reported
from actual GitHub Actions results, never inferred from this workflow's presence.

## Added infrastructure

`.github/workflows/migration-native-cli.yml` uses independent native Linux and
macOS jobs, read-only repository permissions, and a 20-minute timeout. It builds
the existing `CPP/7zip/Bundles/Alone2` CLI with GNU make, writing objects and the
binary to `RUNNER_TEMP` through the existing `O` override. Linux uses the existing
generic GCC configuration without an external assembler. macOS selects the
existing arm64 configuration or x64 variables and Clang warnings according to
the runner's actual architecture. There is no Rust, FFI, Qt, or codec change.

The new `.github/scripts/migration-smoke.py` creates temporary 7z and ZIP archives,
lists and tests them, extracts them, and compares exact fixture paths and bytes.
Fixtures cover an ASCII name, a nested Japanese name, binary bytes, and an empty
file. Every CLI invocation has closed stdin and a timeout. No persistent golden
data is created. Round trips confirm that this executable works for these cases;
they cannot establish compatibility between two implementations or protect
against correlated encode/decode defects. The workflow also runs the existing
portable repository checks. It has no artifact publication or release job.

## Local evidence

On this Linux x86-64 host, GCC/G++ 15.2.0 compiled the native ELF `7zz` successfully
with the repository's warning-as-error flags. The exact build invocation was:

```sh
make -C CPP/7zip/Bundles/Alone2 -f ../../cmpl_gcc.mak -j2 O=/tmp/archive-migration-ci.t8d04p
```

Build log: `/tmp/archive-migration-ci.t8d04p/build.log`; binary:
`/tmp/archive-migration-ci.t8d04p/7zz`. These are disposable host artifacts and may
not survive reboot. No production source was edited or built into the source tree.

The following checks passed locally (exit code zero):

```sh
python3 .github/scripts/migration-smoke.py /tmp/archive-migration-ci.t8d04p/7zz
python3 .github/tests/release_version_test.py
python3 .github/tests/change_notice_test.py "$PWD"
python3 .github/tests/lang_files_test.py "$PWD"
python3 .github/tests/shell_ext_identity.py "$PWD"
python3 .github/tests/shell_ext_lang_reload.py "$PWD"
bash .github/tests/release_notes_test.sh
```

The smoke reported both formats passed create/list/test/extract with all four
file paths and byte contents matching. Existing checks reported zero failures;
language validation checked 93 files. The new workflow parsed as YAML and its
runner matrix and read-only permissions were checked. The preexisting Windows
workflow had no diff. Local validation does not execute GitHub's workflow engine.
No native macOS or Windows execution was available in this local check; CI results
remain pending until the review branch runs on their genuine runners.

## M1 and later requirements

M1 must create reviewed fixtures and observations for list/extract/create/test,
Unicode and code pages, encrypted archives and passwords, nested paths, timestamps,
permissions, corrupted archives, large files, overwrite choices, cancellation,
and CRC/hash behavior. Capture canonical Windows observations on a genuine Windows
runner, with source commit, platform, command, exit status, stdout/stderr, and
archive/fixture hashes. Do not invent expected data or update it to conceal a
disagreement. Block ambiguous behavior for human decision.

Use native Windows, Linux and macOS to compare the legacy executable and each
incremental replacement against independently retained fixtures. Cover exchanging
archives across platforms as well as local round trips; explicitly investigate
Unicode normalization, path separators, filesystem case sensitivity, permissions,
and timestamp precision. Add FFI ownership/lifetime and cancellation tests before
migrating application behavior. Qt/QML builds and desktop integration need native
GUI/platform checks later; the CLI workflow proves none of those today. Release
validation remains a separate human-authorized milestone, including licensing
review and packaging/signing requirements.
