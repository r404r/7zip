# B05-MAN harness — Linux build instructions

This document is intentionally Linux-only. The task scope was narrowed by a
recorded human decision after review found that Windows and macOS instructions
had not been executed on those native platforms and could not honestly be
presented as human-executable. Windows/macOS operator-confirmed entry points
belong to separate follow-up work; this document must not be used for either
platform.

The harness is a small driver that directly implements the retained legacy C++
password callback interfaces (`CPP/7zip/IPassword.h`:
`ICryptoGetTextPassword`, `ICryptoGetTextPassword2`) and loads the unmodified
engine like `CPP/7zip/UI/Client7z/Client7z.cpp`. It is not a wrapper around the
CLI `-p` flag. It adds no archive, codec, crypto, or password semantics.

For password-bearing ZIP creation the retained ZIP handler needs its existing
`em` property. The harness exposes only `--zip-encryption zipcrypto|aes256` and
rejects a password-bearing ZIP create without it, so a plaintext ZIP cannot be
recorded as password-boundary evidence.

## Prerequisites

Linux with `gcc`, `g++`, `make`, POSIX `sh`, Python 3, and this repository
checked out at the commit the coordinator identifies. These tools are the same
Linux build family already used by this repository's `makefile.gcc` path.

## Build from a POSIX shell

Run these commands from any directory inside the intended repository checkout.
They create a disposable directory at `$HOME/b05-manual-b05`, remove only that
directory before rebuilding, and do not modify the checkout:

```
export R="$(git rev-parse --show-toplevel)"
export W="$HOME/b05-manual-b05"
rm -rf "$W"
mkdir -p "$W"
sh "$R/.github/tests/migration/b05/harness/build_linux.sh" "$R" "$W/build"
export H="$W/build/harness"
```

On success the build output is:

```
$H/b05_password_harness
$H/7z.so
```

Keep `7z.so` beside `b05_password_harness`: the driver calls `dlopen` next to
its own executable. The script builds the retained `Format7zF` and `Client7z`
support objects unmodified, compiles/links only the harness translation unit,
and ends by running `selftest-leak`.

Verify the build before any runbook check:

```
"$H/b05_password_harness" selftest-leak
```

The expected output is exactly:

```
[harness] SELFTEST: deliberately printing marker below for check_no_leak.py's own negative control.
SELFTEST_MARKER_SECRET=b05-harness-selftest-leak-marker-77219
```

If the marker is absent or different, record `BLOCKED` and stop; do not proceed
with the runbook.

## Return to a clean state

After copying out the completed evidence record, remove only the disposable
working directory created above:

```
rm -rf "$W"
```

Do not run cleanup commands inside the repository checkout.

## Deliberate coverage limits

- This Linux-only harness covers the retained 7z and ZIP password callback
  paths selected by its `a`, `l`, and `x` commands. It does not cover
  RAR/CAB/ISO, multi-volume archives, or GUI/FileManager dialogs.
- The real `ICryptoGetTextPassword` and `ICryptoGetTextPassword2` contracts
  accept only output pointers and return `HRESULT` (`CPP/7zip/IPassword.h`);
  they have no stream, terminal, or transport/disconnect parameter. The
  harness neither reads stdin nor owns a connection. Therefore it cannot
  truthfully create a distinct real IPassword "disconnect" event without
  modifying retained source or substituting an invented callback result.
  `disconnect` is explicitly excluded from this Linux-only deliverable, not
  passed: B05 needs a separate retained-console/transport harness if it needs
  that behavior characterized.
- The Linux build path was executed locally for this task. A future operator
  run is still manual evidence, not qualified CI or release evidence.
