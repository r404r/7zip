# B05-MAN — human-executable password callback verification runbook

## Status and scope of THIS document

Task `t_5839f819`, branch `wt/t_5839f819`. This document is the runbook and
evidence template for B05 (`t_3859d918`, "Password callback states and
encrypted error characterization"). It is produced under the operator's
own-machine manual-execution authorization (Chinese original, recorded as
board comment B03#168, 2026-09-12: 「可以在个人机器上验证。若有这样的
task，请告诉我，我手工来做，但这些 task 必须标清楚验证步骤，验证方法，验证
点。」and 「我有 Windows，macOS，Linux 机器。」).

This card does **not** execute the campaign, does not pre-fill any result,
does not mark any check PASS/FAIL, and does not close or narrow B05's own
acceptance scope. B05 `t_3859d918` remains open in `todo` and continues to
block everything it currently blocks. This card's deliverable is the
harness and this runbook only.

## Qualification level this evidence can and cannot support

- **Can support:** a documented, reproducible, human-witnessed observation
  of the retained legacy password callback boundary
  (`CPP/7zip/IPassword.h`: `ICryptoGetTextPassword`,
  `ICryptoGetTextPassword2`) as exercised through the unmodified 7-Zip
  engine on one real, named machine per platform — suitable as the native
  IPassword behavioral oracle B05 requires ("not CLI -p equivalent").
- **Cannot support:** qualified CI-runner acceptance, statistically
  repeated or multi-machine coverage, release/publication readiness, or
  RAR/CAB/ISO/multi-volume password behavior (out of scope — see
  `harness/BUILD.md`, "What this harness does NOT cover"). A single manual
  pass by one human on one machine is evidence, not certification; it must
  still go through independent review before it can advance any dependent
  task, and even after review it stays scoped to the exact
  machine/build/commit recorded in the environment-capture block for that
  run.
- Every result the human records is either PASS, FAIL, or
  BLOCKED/COULD-NOT-EXECUTE with a reason. An unexpected observation is
  recorded exactly as observed and is never edited, rounded, or
  reinterpreted to make a check pass. If legacy behavior conflicts with
  what a checklist item assumed, the checklist item is wrong, not the
  observation — record it and raise it on the B05 card as a `needs_input`
  comment; do not self-correct.

## The central difficulty and how this runbook solves it

B05's own acceptance criterion states: **"native Windows/Linux/macOS
reports from actual IPassword boundary (CLI -p not equivalent)"**. A human
cannot hand-drive a C++ vtable, and the `7zz`/`7z` CLI's `-p` flag cannot
reliably distinguish "password defined and empty" from "password
undefined" (see `harness/BUILD.md`, "Why not just use the CLI"). This
runbook is driven by a small, committed, inspectable harness
(`.github/tests/migration/b05/harness/b05_password_harness.cpp`) that:

- Loads the retained 7-Zip engine (`7z.dll`/`7z.so`) exactly the way the
  repository's own retained sample client
  (`CPP/7zip/UI/Client7z/Client7z.cpp`) loads it.
- Implements the same `ICryptoGetTextPassword`/`ICryptoGetTextPassword2`
  interfaces the console/GUI/FileManager callers already implement, with
  no new archive/codec/crypto/password semantics.
- Adds a `--password-mode {undefined,defined-empty,wrong,correct,cancel,eof}`
  selector so every state B05 requires is directly, unambiguously
  selectable and its outcome is printed as plain, value-free, decidable
  text (HRESULT hex, item counts, per-item result codes).

No production/engine/GUI/codec source under `CPP/` or `C/` is modified by
this harness. Everything it links against is built unmodified from the
repository's own existing build files (`CPP/7zip/Bundles/Format7zF`,
`CPP/7zip/UI/Client7z`).

## Who can run this and what they need

A careful human unfamiliar with this codebase, operating a real desktop or
laptop they already own. No purchase, VM/guest install, or commercial
licence is required or permitted (AGENTS.md excludes VM/guest as isolation
qualification and forbids paid dependencies). Required software (all free):

- **Windows**: MSVC (Visual Studio 2019+ Build Tools, "Desktop development
  with C++" workload) — same toolchain `.github/workflows/build-windows.yml`
  already uses.
- **Linux**: `gcc`/`g++`, `make` (same toolchain this repository's own
  `makefile.gcc` build path already uses).
- **macOS**: Xcode Command Line Tools (`clang`/`clang++`, `make`).
- A source checkout of this repository at the exact commit the coordinator
  states.
- Python 3 (already required elsewhere in this repository's own test
  scripts, e.g. `.github/tests/zip_name_encoding.py`) to run
  `check_no_leak.py`.

Full build instructions per platform: `harness/BUILD.md`. **Only the Linux
path in that document has been executed by the AI** while preparing this
card (see this task's completion evidence). Windows and macOS instructions
are derived from this repository's own existing build files but are
otherwise unverified until the human's own run.

## Machine / environment capture block

Use `harness/evidence-template.md` for the actual recorded run. Copy it to
`evidence-<platform>-<date>.md` before starting Section 1; fill in the
environment-capture block first, once, before touching any check. If any
field cannot be observed, write "not observed" and why — never leave blank
and never guess.

## Ordering

1. **Section 0 — Build and selftest** (once per platform run). Build per
   `harness/BUILD.md`; the build ends with `selftest-leak`, whose output
   must match exactly. Do not proceed if it does not match.
2. **Section 1 — Open/list password states (7z)**. Independent of the
   other sections; run first because later sections' archives are built
   here.
3. **Section 2 — Extract password states (7z)**. Depends on the
   non-header-encrypted multi-file archive created in Section 1's fixture
   step (see per-check steps below); run after Section 1.
4. **Section 3 — Create (update) password states, 7z and ZIP**.
   Independent of Sections 1–2; can run before or after them, but must run
   before Section 5 (Section 5 reuses Section 3's ZIP non-ASCII-password
   observation).
5. **Section 4 — Redaction/no-leak**. Depends on transcripts captured
   during Sections 1 and 3 (run those first and save their stdout to
   files).
6. **Section 5 — Legacy non-ASCII ZIP rejection**. Depends on Section 3.6's
   observation; run last.

Between checks: no shared mutable state carries over except the archive
files each check explicitly names, so checks within a section may be
re-run individually if one fails without needing to redo the whole
section. Delete `t1.7z`/`t2.7z`/etc. working files between full re-runs of
a section to guarantee `a` (create) does not fail on "already exists"
(the harness deliberately never overwrites — see BUILD.md).

## Time estimate

| Section | Estimate |
| --- | --- |
| 0. Build + selftest | 15–30 min (first time; toolchain install not included) |
| 1. Open/list password states | 30 min |
| 2. Extract password states | 20 min |
| 3. Create password states | 25 min |
| 4. Redaction/no-leak | 15 min |
| 5. Legacy non-ASCII ZIP rejection | 10 min |
| Total (after toolchain already installed) | ~2 hours |

## Standing instructions (apply to every check below)

1. Follow "Exact steps" literally, including the stated working directory.
2. Follow "Method" to observe and copy the literal value asked for
   (HRESULT hex, exit code, stdout lines) into the evidence record —
   do not paraphrase.
3. Apply "Verification point" mechanically: if the observed value does not
   exactly match, the result is FAIL, full stop. "Close enough" is never a
   basis for PASS.
4. Run "Negative control" for every check that has one. If the negative
   control does NOT show the expected different/absent state, the check is
   inconclusive — record it as BLOCKED with the reason, not PASS or FAIL.
5. Record the observed result immediately, exactly as observed. Never
   "correct" an earlier entry to match what a later step implies should
   have happened.
6. **Never paste a real password anywhere in this process.** Only the
   synthetic values below (`B05Synth-Correct-9f2a`,
   `B05Synth-WRONG-1234`, `B05Synth-注重-éèü-テスト`) are used. These are
   public test data, not secrets — they may be committed and shared freely.
7. Return the working directory to clean before the next full section (new
   archive filenames, or delete-and-recreate) so failures don't mask each
   other.

## Fixture setup (run once, before Section 1)

Working directory: `<any writable dir>`, referred to below as `$W`. All
commands assume the harness binary and `7z.dll`/`7z.so`/equivalent are in
`$H` (the build output directory from Section 0), and are run as
`$H/b05_password_harness` (Linux/macOS) or `$H\b05_password_harness.exe`
(Windows) — substitute your actual build path.

Create two plaintext input files (any content is fine; these are not
secrets), and pre-create the extraction output directories Section 2 uses
(the harness does not create its own top-level output directory — see
Section 2.1):

```
echo "line one" > $W/a.txt
echo "line two" > $W/b.txt
mkdir $W/out_correct $W/out_wrong $W/out_undef $W/out_cancel
```

## Section 1 — Open/list password states (7z)

### 1.1 undefined password, header not encrypted

**Exact steps** (working directory `$W`):
```
<H>/b05_password_harness a 7z t1_plain.7z a.txt --password-mode undefined
<H>/b05_password_harness l t1_plain.7z --password-mode undefined
```
**Method**: capture combined stdout of both commands and the second
command's process exit code.

**Verification point**: create succeeds (`UpdateItems HRESULT=0x00000000`,
exit 0). List succeeds and prints `item count=1` and the file's path,
exit 0 — because header encryption was never requested, the archive's
directory is plaintext and readable without any password regardless of
`--password-mode`.

**Negative control**: re-run the list command with `--password-mode wrong
--password anything` — it must produce the SAME successful listing (proves
the check is actually exercising "no encryption", not accidentally
succeeding for an unrelated reason).

### 1.2 undefined password, header encrypted

**Exact steps**:
```
<H>/b05_password_harness a 7z t1_he.7z a.txt --password-mode correct --password B05Synth-Correct-9f2a --header-encrypt
<H>/b05_password_harness l t1_he.7z --password-mode undefined
```
**Method**: capture stdout + exit code of the `l` command.

**Verification point**: `l` fails. Observed on the AI's own Linux run:
`Open() with format candidate 0/1 returned HRESULT=0x00000001`, final
`Cannot open file as archive (tried 7z, zip)`, exit code 2. Record the
EXACT HRESULT/exit code your platform produces — if it differs from
`0x00000001`/exit 2, record the actual value; do not silently expect it to
match.

**Negative control**: repeat with `--password-mode correct --password
B05Synth-Correct-9f2a` — must now succeed and print `item count=1`,
proving the FAIL above was the header encryption being live, not a broken
harness/archive.

### 1.3 defined-empty password, header encrypted

**Exact steps**:
```
<H>/b05_password_harness a 7z t1_empty.7z a.txt --password-mode defined-empty --header-encrypt
<H>/b05_password_harness l t1_empty.7z --password-mode defined-empty
```
**Method**: capture stdout + exit code of both commands.

**Verification point**: BOTH succeed — an archive can legitimately be
created and reopened with a defined-but-empty password. This is the state
CLI `-p` (empty argument) cannot reliably produce; this check exists
specifically to prove the harness reaches it. Exit 0 for both, `l` prints
`item count=1`.

**Negative control**: re-run `l` with `--password-mode undefined` (not
defined-empty) — this MUST behave like 1.2 (fail to open), proving
"defined-empty" and "undefined" are genuinely different states to the
engine, not the harness silently treating them the same.

### 1.4 wrong password, header encrypted

**Exact steps**:
```
<H>/b05_password_harness l t1_he.7z --password-mode wrong --password B05Synth-WRONG-1234
```
(reuses the `t1_he.7z` archive from 1.2, correct password
`B05Synth-Correct-9f2a`)

**Method**: capture stdout + exit code.

**Verification point**: fails. AI's own Linux observation:
`Open()` returns HRESULT != 0 for both format candidates, final message
`Cannot open file as archive`, exit 2 — same shape as "undefined" (1.2),
because a wrong password and no password are indistinguishable to header
decryption (both fail AES-GCM/HMAC verification the same way). Record
whatever your platform actually shows.

**Negative control**: same archive with `--password-mode correct
--password B05Synth-Correct-9f2a` succeeds (already proven in 1.2's
negative control; re-confirm here to bind it to this exact check run).

### 1.5 correct password, header encrypted

**Exact steps**:
```
<H>/b05_password_harness l t1_he.7z --password-mode correct --password B05Synth-Correct-9f2a > list_correct_transcript.txt 2>&1
```
**Method**: capture the transcript to a FILE (needed later for Section 4's
redaction check) and the exit code.

**Verification point**: exit 0, transcript contains `item count=1` and the
archived file's path.

**Negative control**: 1.2's FAIL with the same archive and no password is
the negative control (already run).

### 1.6 correct non-ASCII password, header encrypted

**Exact steps**:
```
<H>/b05_password_harness a 7z t1_nonascii.7z a.txt --password-mode correct --password "B05Synth-注重-éèü-テスト" --header-encrypt
<H>/b05_password_harness l t1_nonascii.7z --password-mode correct --password "B05Synth-注重-éèü-テスト" > list_nonascii_transcript.txt 2>&1
```
(quote the password exactly as shown, including the non-ASCII characters,
so the shell passes it through as one argument)

**Method**: capture both commands' exit codes and the second transcript to
a file (needed for Section 4).

**Verification point**: BOTH succeed, exit 0, proving the 7z (not ZIP)
password path round-trips non-ASCII characters correctly through
`ICryptoGetTextPassword2` end to end.

**Negative control**: re-run `l` with `--password-mode wrong --password
"WrongNonAsciiVälue"` (any different non-ASCII string) — must fail, proving
the check is discriminating on the actual password value, not merely
"any non-ASCII string works".

### 1.7 prompt cancel

**Exact steps**:
```
<H>/b05_password_harness l t1_he.7z --password-mode cancel
```
**Method**: capture stdout + exit code.

**Verification point**: AI's own Linux observation: prints `[harness]
password prompt aborted (open)`, then `Open() ... HRESULT=0x80004004`
(E_ABORT), then `treating Open() failure as the expected abort outcome`,
exit 2. Record your platform's actual HRESULT.

**Negative control**: the `[harness] password prompt aborted (open)` line
itself is the negative control marker — its PRESENCE (not just the
failure) proves the abort branch specifically fired, as distinct from an
ordinary wrong-password failure (1.4), which does NOT print that line.
Compare your 1.4 and 1.7 transcripts side by side and confirm only 1.7 has
it.

### 1.8 prompt EOF

**Exact steps**:
```
<H>/b05_password_harness l t1_he.7z --password-mode eof
```
**Method**: capture stdout + exit code.

**Verification point**: same HRESULT/exit code shape as 1.7 (by this
harness's own construction — see `b05_password_harness.cpp`'s `PwMode`
enum comment: this harness cannot give EOF a different HRESULT than cancel
through the `ICryptoGetTextPassword` interface alone, since it has no
distinct EOF signal in its single-return-value contract). This is a
**known, documented limitation of this harness**, not a legacy-code
observation — record it as such rather than treating "same as cancel" as
a discovery about the retained engine.

**Negative control**: the log line differs textually (`mode=eof` vs
`mode=cancel` in the `[harness] password-callback #1 fired: ...` line) —
this proves the MODE selection is live and reaching the harness correctly,
even though the engine-visible outcome (HRESULT) is identical by harness
design. If you want an engine-level EOF/cancel distinction, see "Known gap"
below.

**Known gap — flag for B05 card, do not fabricate a fix here**: the
retained CONSOLE path (`GetPassword_HRESULT` in
`CPP/7zip/UI/Console/UserInputUtils.cpp:109-118`) DOES distinguish these
three outcomes at the source level: `E_INVALIDARG` (scan failure),
`E_FAIL` (stream error), `E_ABORT` (clean EOF with no characters typed).
This harness exercises the interface boundary, not the console's own
stdin-scanning code, so it cannot reproduce that finer distinction. If B05
needs console-level EOF-vs-cancel-vs-stream-error evidence specifically,
that requires a DIFFERENT harness that drives the actual console binary's
stdin, which is a distinct future card — comment this gap on B05's own
card (`t_3859d918`) rather than silently declaring it covered here.

## Section 2 — Extract password states (7z, header NOT encrypted)

Setup (uses the plaintext-header archive style from 1.1, but with two
files so per-item behavior is visible):
```
<H>/b05_password_harness a 7z t2.7z a.txt b.txt --password-mode correct --password B05Synth-Correct-9f2a
```
(no `--header-encrypt`: names are visible, item DATA is encrypted)

### 2.1 correct password

**Exact steps**:
```
mkdir out_correct
<H>/b05_password_harness x t2.7z out_correct/ --password-mode correct --password B05Synth-Correct-9f2a
```
(the output directory must already exist — like the repository's own
`Client7z.cpp`, this harness does not create the top-level extraction
target directory itself, only subdirectories implied by paths inside the
archive; AI's own Linux run hit exactly this and confirms the fix below)
**Method**: capture stdout, exit code, and check `out_correct/` for the
two extracted files with correct content.

**Verification point**: exit 0, `Extract() HRESULT=0x00000000
items_ok=2 items_error=0`, both files present with their original content.

**Negative control**: `diff` the extracted files against the originals
(`a.txt`/`b.txt`) — byte-identical is required for PASS, not merely
"files exist".

### 2.2 wrong password (per-item error, whole call still S_OK)

**Exact steps** (fresh output dir):
```
mkdir out_wrong
<H>/b05_password_harness x t2.7z out_wrong/ --password-mode wrong --password B05Synth-WRONG-1234
```
**Method**: capture stdout + exit code.

**Verification point**: AI's own Linux observation:
`item result CODE=2 for: a.txt`, `item result CODE=2 for: b.txt`
(CODE=2 is `NArchive::NExtract::NOperationResult::kCRCError`, i.e. wrong
password/data corruption manifests as a per-item CRC failure, NOT an
Open()-level failure, because the header was not encrypted), THEN
`Extract() HRESULT=0x00000000 items_ok=0 items_error=2` — the outer call
HRESULT is S_OK even though every item failed. Exit code from the harness
is 1 (it treats any items_error>0 as a nonzero process exit, but the
engine's own `Extract()` HRESULT is 0). **This is the specific
"per-item versus per-call errors" distinction B05's scope requires** —
record both numbers exactly.

**Negative control**: 2.1's `items_error=0` with the correct password is
the negative control — same archive, only the password differs, proving
the distinction is caused by the password and not by the archive/file.

### 2.3 undefined password

**Exact steps**:
```
mkdir out_undef
<H>/b05_password_harness x t2.7z out_undef/ --password-mode undefined
```
**Verification point**: AI's own Linux observation: this does NOT mirror
2.2's per-item CRC errors. Instead the callback itself reports failure
(`[harness] password not defined (extract) -- reporting failure per
legacy ICryptoGetTextPassword contract`) and the WHOLE call aborts:
`Extract() HRESULT=0x80004004 items_ok=0 items_error=0`, exit 1 — same
outer shape as 2.4 (cancel), because this harness's "undefined" state
returns E_ABORT from `CryptoGetTextPassword` exactly like its "cancel"
state does (see `b05_password_harness.cpp`'s `CryptoGetTextPassword`
implementations: both the `!defined` branch and the cancel/eof
`ResolvePassword()` branches return E_ABORT). This mirrors Client7z.cpp's
own "password not defined" branches, which take the identical
`PrintError()+E_ABORT` path. Record whatever your platform actually shows;
do not assume it matches this Linux observation without checking your own
transcript.

**Negative control**: contrast directly against 2.2 (wrong password):
2.2 has `items_error=2` (the loop tried and failed each item because a
password value, even a wrong one, was supplied), while 2.3 has
`items_error=0` (the loop never started because no password value was
ever supplied). This items_error=0-vs-2 contrast is the actual
discriminator, not the "per-item CRC vs per-call abort" HRESULT shape
alone — record both counts.

### 2.4 cancel

**Exact steps**:
```
mkdir out_cancel
<H>/b05_password_harness x t2.7z out_cancel/ --password-mode cancel
```
**Verification point**: AI's own Linux observation:
`[harness] password prompt aborted (extract)`, then
`Extract() HRESULT=0x80004004 items_ok=0 items_error=0`, exit 1 — the
WHOLE call aborts (E_ABORT), unlike 2.2's per-item CRC failures, because a
genuine cancel stops the extraction loop rather than letting it try (and
fail) each item.

**Negative control**: contrast directly with 2.2 — cancel produces
`items_error=0` (loop never tried), wrong-password produces
`items_error=2` (loop tried and failed each item). If your platform shows
the same items_error count for both, that is a genuine, reportable
discrepancy — record it as an unexpected observation, do not adjust either
result to force the expected contrast.

## Section 3 — Create (update) password states, 7z and ZIP

### 3.1 undefined password (7z)
```
<H>/b05_password_harness a 7z t3_undef.7z a.txt --password-mode undefined
```
**Verification point**: succeeds, exit 0 (creating an unencrypted archive
needs no password) — AI's own observation: `UpdateItems HRESULT=0x00000000`.

### 3.2 defined-empty password, header-encrypt (7z)
```
<H>/b05_password_harness a 7z t3_empty.7z a.txt --password-mode defined-empty --header-encrypt
```
**Verification point**: succeeds, exit 0 — an archive CAN be created with
an explicitly-empty-but-defined password (distinguishing this from
`undefined`, where no encryption is requested at all — cross-check against
3.1: 3.1's archive should be openable with `--password-mode undefined`,
3.2's archive should NOT (behaves like a real, if weak, encrypted archive).

**Negative control**: `<H>/b05_password_harness l t3_empty.7z
--password-mode undefined` must FAIL (mirrors Section 1.2/1.3's contrast).

### 3.3 correct password, header-encrypt (7z)
```
<H>/b05_password_harness a 7z t3_correct.7z a.txt --password-mode correct --password B05Synth-Correct-9f2a --header-encrypt > create_correct_transcript.txt 2>&1
```
**Method**: save transcript to a file (needed for Section 4).

**Verification point**: exit 0.

### 3.4 correct non-ASCII password, header-encrypt (7z)
```
<H>/b05_password_harness a 7z t3_nonascii.7z a.txt --password-mode correct --password "B05Synth-注重-éèü-テスト" --header-encrypt
```
**Verification point**: exit 0 — 7z accepts non-ASCII passwords on create
(contrast with 3.6 below).

### 3.5 correct ASCII password (ZIP)
```
<H>/b05_password_harness a zip t3_zip_ascii.zip a.txt --password-mode correct --password B05Synth-Correct-9f2a
```
**Verification point**: exit 0.

### 3.6 correct non-ASCII password (ZIP) — expect rejection
```
<H>/b05_password_harness a zip t3_zip_nonascii.zip a.txt --password-mode correct --password "B05Synth-注重-éèü-テスト"
```
**Verification point**: AI's own Linux observation: FAILS with
`UpdateItems HRESULT=0x80070057` (E_INVALIDARG), exit 1. This matches the
source at `CPP/7zip/Archive/Zip/ZipHandlerOut.cpp:415-416`
(`if (!IsSimpleAsciiString(password)) return E_INVALIDARG;`) — the legacy
ZIP writer rejects non-simple-ASCII passwords outright. **Record the
EXACT HRESULT your platform shows; if it differs from `0x80070057`, that
is the more important fact — do not silently expect the source-code
prediction to hold on your platform without checking.**

**Negative control**: 3.4's SUCCESS with the identical non-ASCII password
against the 7z format (not ZIP) proves the rejection is ZIP-format-specific
behavior, not a harness bug that rejects all non-ASCII input.

## Section 4 — Redaction / no-leak

### 4.0 selftest (negative control for the checker itself)

**Exact steps**:
```
python3 .github/tests/migration/b05/harness/check_no_leak.py --selftest
```
**Verification point**: prints `SELFTEST PASS: checker correctly detected
the planted secret...`, exit 0. If this does not print PASS, the checker
itself is broken — STOP, do not trust any other Section 4 result until
this is fixed.

### 4.1 — 4.3: real transcripts do not contain the password

**Exact steps** (repeat per transcript captured in earlier sections):
```
python3 .github/tests/migration/b05/harness/check_no_leak.py --secret "B05Synth-Correct-9f2a" list_correct_transcript.txt
python3 .github/tests/migration/b05/harness/check_no_leak.py --secret "B05Synth-注重-éèü-テスト" list_nonascii_transcript.txt
python3 .github/tests/migration/b05/harness/check_no_leak.py --secret "B05Synth-Correct-9f2a" create_correct_transcript.txt
```
**Method**: run each, capture stdout + exit code.

**Verification point**: each prints `PASS: none of 1 secret(s) found...`,
exit 0. AI's own Linux observation for the equivalent transcripts:
confirmed PASS in all cases (see this task's completion evidence).

**Negative control**: 4.0 is the negative control for the checker script
itself. As an ADDITIONAL live negative control specific to these
transcripts, deliberately create one contaminated copy and confirm FAIL:
```
echo "test-leak: B05Synth-Correct-9f2a" >> list_correct_transcript_CONTAMINATED_COPY.txt
python3 .github/tests/migration/b05/harness/check_no_leak.py --secret "B05Synth-Correct-9f2a" list_correct_transcript_CONTAMINATED_COPY.txt
```
Must print `FAIL: secret material found...`, exit 1. Delete the
contaminated copy afterward — do not leave it in the evidence directory.

## Section 5 — Legacy non-ASCII ZIP rejection (recorded as observed)

This section is a pointer, not a new check: Section 3.6 IS this repository
fork's currently-observed legacy non-ASCII ZIP password rejection. Copy
its exact HRESULT and exit code into the evidence template's Section 5
table, and explicitly confirm: "this matches/does not match
`E_INVALIDARG` (0x80070057) as predicted from
`CPP/7zip/Archive/Zip/ZipHandlerOut.cpp:415-416`". If it does not match,
this is a compatibility-relevant finding — comment it on B05's card
verbatim; do not silently normalize it to match the prediction.

## What to do when you finish

1. Fill in every field of your `evidence-<platform>-<date>.md` copy,
   including the mandatory "any unexpected observation" section (write
   "none" if genuinely none).
2. Do NOT edit `.github/tests/migration/b05/` or this runbook to make a
   result look better.
3. Send the completed evidence file to the coordinator/operator; do not
   mark B05 (`t_3859d918`) itself PASS or closed — that decision belongs to
   B05's own reviewed implementation card, informed by, but not equal to,
   this evidence.
