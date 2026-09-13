# B05-MAN harness — build instructions (all platforms)

This directory holds `b05_password_harness.cpp`, a small driver that
exercises the retained legacy C++ password callback boundary
(`CPP/7zip/IPassword.h`: `ICryptoGetTextPassword`, `ICryptoGetTextPassword2`)
directly against the unmodified 7-Zip engine, loaded exactly the way the
repository's own retained sample client
(`CPP/7zip/UI/Client7z/Client7z.cpp`) loads it: `LoadLibrary`/`dlopen` the
engine, call its exported `CreateObject`, and implement the same COM-style
callback interfaces the console/GUI/FileManager callers already implement.

It adds **no new archive, codec, crypto, or password semantics**. It adds
one thing Client7z.cpp does not have: a `--password-mode` selector so every
state B05 needs — including states the CLI `-p` flag cannot reliably
produce, such as a password that is *defined and empty* as distinct from
*undefined* — is directly selectable and independently observable through
`ICryptoGetTextPassword2`'s explicit `passwordIsDefined` out-parameter.

For ZIP creation, the retained handler also requires its documented `em`
property to choose an encryption method. The harness exposes that retained
property only as `--zip-encryption zipcrypto|aes256` and refuses a
password-bearing ZIP create without it; this prevents a plaintext ZIP from
being recorded as password-boundary evidence.

## Why not just use the `7zz`/`7z` CLI?

B05's own acceptance criterion states this explicitly: **"native
Windows/Linux/macOS reports from actual IPassword boundary (CLI -p not
equivalent)"**. The AI's own exploration for this card confirmed why: the
CLI's `-p` flag cannot express "password is defined but is the empty
string" as distinct from "no password given" (the command-line parser
folds those together — see `CPP/7zip/UI/Common/ArchiveCommandLine.cpp`
around the `NKey::kPassword` handling). It also cannot express prompt
cancel/EOF as distinct signals separately from "wrong password" without
driving an actual interactive stdin prompt, which is fragile to automate
identically across three OSes. Driving the interfaces directly removes
both problems while still calling into the same unmodified engine through
the same interfaces the retained UI layers use.

## What gets built

1. The retained 7-Zip engine as a shared library — `7z.dll` (Windows) /
   `7z.so` (Linux) / `7z.dylib`-equivalent bundle (macOS) — built
   **unmodified** from `CPP/7zip/Bundles/Format7zF` using the repository's
   own build files. No source under `CPP/` or `C/` is changed.
2. `b05_password_harness`, this directory's own driver, compiled with the
   same flags the repository already uses for
   `CPP/7zip/UI/Client7z/Client7z.cpp` and linked against the same set of
   retained support objects (string/file/COM plumbing) Client7z.cpp itself
   links against.

## Linux

Prerequisites: `gcc`/`g++` (already used by this repository's own
`makefile.gcc` build path), `make`.

```
cd <repo-root>
sh .github/tests/migration/b05/harness/build_linux.sh <repo-root> <build-dir>
```

`<build-dir>` is created if missing; anywhere writable is fine (does not
need to be inside the repository). On success:

```
<build-dir>/harness/b05_password_harness   # the driver binary
<build-dir>/harness/7z.so                  # the retained engine, must stay
                                            # beside the binary (dlopen looks
                                            # next to argv[0])
```

The script ends by running `b05_password_harness selftest-leak`, which
prints one line containing a fixed, clearly-labeled marker string (never a
real or synthetic archive password) so you can immediately confirm
`check_no_leak.py` catches a genuine leak before trusting its PASS verdicts
on real transcripts — see the runbook, Section 0 and Section 7.

This exact script was run end-to-end against this task's Linux host by
the AI while preparing this card; see the task's completion evidence for
the transcript. **A human's own Linux run in the runbook is still required**
— this repository's compatibility policy does not accept AI-only execution
as native platform evidence.

## Windows

Prerequisites: MSVC (Visual Studio 2019+ Build Tools, "Desktop development
with C++" workload) — the same toolchain `.github/workflows/build-windows.yml`
already uses for this repository's Windows CI.

Open a "Developer Command Prompt for VS" (or run `vcvars64.bat` in a plain
`cmd.exe`), then:

```
cd <repo-root>\CPP\7zip\Bundles\Format7zF
nmake /NOLOGO PLATFORM=x64
```

This produces `x64\7z.dll` — the unmodified retained engine, built the same
way the repository's own Windows CI builds it.

```
cd <repo-root>\CPP\7zip\UI\Client7z
nmake /NOLOGO PLATFORM=x64
```

This produces `x64\7zcl.exe` and, as a side effect, the object files this
harness reuses (`Client7z`'s makefile pulls in `../../7zip.mak`, which is
the same makefile chain `Format7zF`/every other bundle target uses).

Then compile and link the harness's own translation unit against those
same object files. From `CPP\7zip\UI\Client7z`, with the Client7z nmake
build's `x64\` object directory already populated from the step above:

```
cl /nologo /O2 /EHsc /D "NDEBUG" /D "_UNICODE" /D "UNICODE" ^
   /I . ^
   /c ..\..\..\..\..\.github\tests\migration\b05\harness\b05_password_harness.cpp ^
   /Fo:x64\b05_password_harness.obj

link /nologo /OUT:x64\b05_password_harness.exe ^
   x64\b05_password_harness.obj ^
   x64\Alloc.obj x64\IntToString.obj x64\MyString.obj x64\MyVector.obj ^
   x64\NewHandler.obj x64\StringConvert.obj x64\StringToInt.obj ^
   x64\UTFConvert.obj x64\Wildcard.obj x64\DLL.obj x64\FileDir.obj ^
   x64\FileFind.obj x64\FileIO.obj x64\FileName.obj x64\PropVariant.obj ^
   x64\PropVariantConv.obj x64\TimeUtils.obj x64\FileStreams.obj ^
   ole32.lib oleaut32.lib user32.lib advapi32.lib
```

(Adjust the relative path to this harness's `.cpp` if your checkout layout
differs — it is the same repo-root-relative path used elsewhere in this
document.) Then copy `x64\7z.dll` (from the Format7zF build) beside
`x64\b05_password_harness.exe` — `LoadLibrary` in the harness looks next to
the executable's own directory, exactly like Client7z.cpp does.

**This exact Windows sequence has NOT been executed by the AI** (no
Windows host is available in this task's environment) — it is derived
directly from `CPP/7zip/UI/Client7z/makefile` (the `!include
"../../7zip.mak"` chain) and `.github/workflows/build-windows.yml`'s own
`nmake`/`vcvars64.bat` invocation, but it is unverified until the human's
own Windows run in the runbook exercises it. If any step fails exactly as
written, record the literal compiler/linker error in the runbook's
evidence template and treat the whole platform run as BLOCKED — do not
improvise undocumented flags to force it through.

## macOS

Prerequisites: Xcode Command Line Tools (`clang`/`clang++`, `make`) — this
repository does not currently have a macOS CI job to mirror, so this
sequence is derived from the Linux `makefile.gcc` path (which is
clang-compatible on macOS, as evidenced by
`CPP/7zip/var_mac_x64.mak`/`var_mac_arm64.mak`/`cmpl_mac_x64.mak` already
present in this tree) rather than from any repository-verified macOS build:

```
cd <repo-root>
sh .github/tests/migration/b05/harness/build_linux.sh <repo-root> <build-dir>
```

The same script works unchanged on macOS because `makefile.gcc`'s rules
already branch correctly on the Mac clang toolchain when invoked with
`make` — the script only calls `make -f makefile.gcc` and `g++`/`gcc` from
`PATH`, which on macOS resolve to the Xcode clang/clang++ shims. **This has
NOT been executed by the AI or verified on a real Mac** — no macOS host is
available in this task's environment. If `g++`/`gcc`/`make` resolve to
something unexpected (check with `g++ --version` — it should print a
`clang` banner on macOS, not a `gcc` banner) or the build fails, record the
exact error and BLOCK the check rather than improvising.

## Verifying the build before running any check

Every platform's build ends (or should be immediately followed) by:

```
<harness-binary> selftest-leak
```

Expected output (exact, byte-for-byte apart from platform path
separators):

```
[harness] SELFTEST: deliberately printing marker below for check_no_leak.py's own negative control.
SELFTEST_MARKER_SECRET=b05-harness-selftest-leak-marker-77219
```

If this does not print exactly that marker, the build did not succeed
correctly — do not proceed to the runbook's checks.

## What this harness does NOT cover

- RAR/CAB/ISO/other formats: B05's scope is "supported ZIP and 7z methods"
  only; the harness's `a`/`l`/`x` commands only ever request the 7z or zip
  class objects (see `CLSID_Format7z`/`CLSID_FormatZip` in the `.cpp`).
- GUI/FileManager password dialogs: those are B07's scope, not B05's; this
  harness only exercises the console-shaped `ICryptoGetTextPassword(2)`
  boundary, matching B05's own body text ("native legacy callback harness").
- Multi-volume/split archives and RAR5 AES: out of scope for the same
  reason RAR is out of scope.
