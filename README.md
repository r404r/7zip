# 7-Zip-fork

A personal fork of [7-Zip](https://7-zip.org) by Igor Pavlov, focused on one everyday
problem: **file names inside zip archives that travel between systems with different
languages** — a zip made on a Chinese Windows shows garbled names on a Japanese or
English one, and vice versa.

Why a fork: the upstream GitHub repository does not appear to take pull requests —
at the time of writing none of the PRs opened there had been merged (the maintainer
is active in the issue tracker instead). So instead of sending patches upstream,
this fork carries them on top of each upstream release.

Upstream: [ip7z/7zip](https://github.com/ip7z/7zip) · current base: **7-Zip 26.03**

## What is different from 7-Zip

**Reading archives with the wrong names ("receiving side")**
- The **Extract dialog** has a *Name code page* drop-down: pick `936 (Chinese Simplified)`
  and the names of a legacy zip decode correctly. It always starts at *Auto* (today's
  behavior) and is not remembered — a code page fixes one archive.
- The **File Manager** can switch the code page *while browsing* an archive:
  View → *Name Code Page…* reopens a zip or tar in place and keeps your position.
  It applies only to a plain zip or uncompressed tar backed by one real file;
  `.tar.gz` and other multi-handler chains, archives opened directly from a parent
  archive's memory stream, and paths shortened by the File Manager are disabled. Reopening is
  currently synchronous, without progress or cancellation; see the detailed DOC.
- On the command line: `7z l "-mzip.cp=936" archive.zip` — the `zip.` prefix sends the
  property only to the zip handler, so `.7z`, `.gz` and everything else stay untouched.
  `tar.cp` works the same way. See `DOC/zip-name-encoding.txt` for the details and
  for two PowerShell/terminal pitfalls.

**Writing archives that decode everywhere ("sending side")**
- The **Add to Archive dialog** has *Use UTF-8 for file names* for zip (on by default):
  names are written as UTF-8 with the UTF-8 flag (bit 11), so any compliant tool
  decodes them, no guessing involved.

**Packaging and coexistence**
- A small **MSI installer** that lives next to an official 7-Zip installation: its own
  product identity, its own folder (`7-Zip-fork`), and a context menu registered as
  **7-Zip-fork** with its own CLSID — installing or removing it never touches the
  official 7-Zip.
- A **portable** set: unzip and run, nothing to install.
- The **language files** are included, which a build from the upstream sources
  alone cannot be: they ship only with the official binary release. The
  interface follows the system language on first run, and Options → Language
  lists all 90-odd of them. The fork's own strings are translated into
  Japanese, Simplified and Traditional Chinese; the other languages show them
  in English.

## Install

Take either from the latest [Release](https://github.com/r404r/7zip/releases):

| Asset | What it is |
| --- | --- |
| `7zip-fork-<version>-x64.msi` | Installer, coexists with official 7-Zip |
| `7zip-fork-<version>-portable-x64.zip` | `7zFM.exe`, `7zG.exe`, `7z.exe`, `7zz.exe`, `7z.dll`, `7-zip.dll`, SFX modules, `Lang\`, docs — run from anywhere |
| `SHA256SUMS.txt` | Checksums of both |

Version scheme: `26.03-fork.3` is the third fork release on top of 7-Zip 26.03; the MSI
carries it as `26.3.3`. Release candidates end in `-rc.N`. Windows x64 only.
There is no help file, so the Help buttons do nothing.

## How this fork is maintained

- `main` mirrors upstream exactly and is never written to; every change lives in a
  reviewed, tested branch that is merged into `dev-main`, the branch you are looking at.
- New upstream releases are **merged** into `dev-main` (never rebased), so every
  release tag stays in the history.
- Every push builds all targets on CI, runs behavior tests for the encoding features,
  and checks the MSI down to its registry entries. Releases are cut by tagging.
- `Lang/` is vendored from the official binary release and pinned to a sha256
  manifest, so it can be shown to be the official files plus this fork's own
  strings. See [`.github/lang/README.md`](.github/lang/README.md).

## Roadmap

- Finish the in-manager code page switching: add progress and cancellation while
  a large zip or tar is reopened.
- Measure reopen times on large and solid archives (drives whether the switch stays).
- Possibly show the fork release number in the About box.

## License

The same terms as 7-Zip: **LGPL 2.1 or later**, with the unRAR restriction for the RAR
decompression code and BSD-licensed pieces as listed in [`DOC/License.txt`](DOC/License.txt).
This is a modified build, not the official 7-Zip; the full change history is this
repository. 7-Zip is Copyright (C) 1999-2026 Igor Pavlov.
