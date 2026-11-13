# B05 manual evidence record — one copy per Linux run

Copy this file to `evidence-linux-<YYYYMMDD>.md` (do not edit this
template in place) and fill in every field. Never leave a result blank;
write `BLOCKED: <reason>` if a check could not run. Never edit a filled-in
result after the fact to make it match a different check's outcome.

## Environment capture (fill in ONCE per run, before Section 1)

```
Run date/time (local, with UTC offset):
Operator name (human executing, not the AI):
Platform: Linux
OS version/build (uname -a):
Filesystem of the working directory:
Locale / code page (locale):
Compiler and version (g++ --version):
Repository commit under test (git rev-parse HEAD):
Harness binary path:
Harness binary SHA-256 (sha256sum):
Engine library path (7z.so):
Engine library SHA-256:
selftest-leak output (paste verbatim, must match BUILD.md exactly):
```

## Section 1 — Open/list password states (7z)

| # | Check | Command / mode | Observed HRESULT / exit | Observed stdout (key lines) | Negative-control result (PASS/FAIL/not run; verbatim key line) | PASS/FAIL/BLOCKED |
|---|---|---|---|---|---|---|
| 1.1 | undefined, no header-encrypt | `l ... --password-mode undefined` | | | | |
| 1.2 | undefined, header-encrypt=on | `l ... --password-mode undefined` | | | | |
| 1.3 | defined-empty, header-encrypt=on | `l ... --password-mode defined-empty` | | | | |
| 1.4 | wrong, header-encrypt=on | `l ... --password-mode wrong --password ...` | | | | |
| 1.5 | correct, header-encrypt=on | `l ... --password-mode correct --password ...` | | | | |
| 1.6 | correct, non-ASCII, header-encrypt=on | `l ... --password-mode correct --password "B05Synth-注重-éèü-テスト"` | | | | |
| 1.7 | cancel | `l ... --password-mode cancel` | | | | |
| 1.8 | eof | `l ... --password-mode eof` | | | | |

## Disconnect boundary — explicitly excluded, not a PASS

`ICryptoGetTextPassword`/`ICryptoGetTextPassword2` have only output-pointer
arguments and an `HRESULT` return (`CPP/7zip/IPassword.h`). This direct
callback harness reads no stdin and owns no transport, so it cannot generate a
real disconnect without modifying retained code or inventing a result. Record
the following statement verbatim; do not mark it PASS:

```
EXCLUDED: disconnect is not reachable at this direct IPassword callback boundary;
no stream or transport exists in the interface/harness. Separate retained-console
or transport characterization is required by B05 if disconnect evidence is needed.
```

## Section 2 — Extract password states (7z, no header encryption: names visible, data encrypted)

| # | Check | Observed HRESULT | items_ok / items_error | Negative-control result (PASS/FAIL/not run; verbatim key line) | PASS/FAIL/BLOCKED |
|---|---|---|---|---|---|
| 2.1 | correct | | | | |
| 2.2 | wrong (per-item error, call succeeds) | | | | |
| 2.3 | undefined | | | | |
| 2.4 | cancel | | | | |

## Section 3 — Create (update) password states, 7z and ZIP

| # | Check | Format | Observed HRESULT | Negative-control result (PASS/FAIL/not run; verbatim key line) | PASS/FAIL/BLOCKED |
|---|---|---|---|---|---|
| 3.1 | undefined | 7z | | | |
| 3.2 | defined-empty, header-encrypt | 7z | | | |
| 3.3 | correct, header-encrypt | 7z | | | |
| 3.4 | correct non-ASCII, header-encrypt | 7z | | | |
| 3.5a | correct ASCII | zip / ZipCrypto | | | |
| 3.5b | correct ASCII | zip / AES256 | | | |
| 3.6a | correct non-ASCII (expect E_INVALIDARG / rejection) | zip / ZipCrypto | | | |
| 3.6b | correct non-ASCII (expect E_INVALIDARG / rejection) | zip / AES256 | | | |

## Section 4 — Redaction / no-leak

| # | Check | Transcript file | check_no_leak.py verdict | Negative-control result (PASS/FAIL/not run; verbatim key line) | PASS/FAIL/BLOCKED |
|---|---|---|---|---|---|
| 4.0 | selftest (negative control for the checker itself) | n/a | | | |
| 4.1 | Section 1.5 transcript does not contain the correct password | | | | |
| 4.2 | Section 1.6 transcript does not contain the non-ASCII password | | | | |
| 4.3 | Section 3.3 transcript does not contain the correct password | | | | |

## Section 5 — Legacy non-ASCII ZIP rejection (recorded as observed, not normalized)

| # | Observation | Result |
|---|---|---|
| 5.1 | ZIP create with non-ASCII password: HRESULT observed | |
| 5.2 | Does this match E_INVALIDARG (0x80070057)? If not, record the ACTUAL value and do not "correct" it. | |

## Any unexpected observation (mandatory section, write "none" if truly none)

Record here, verbatim, anything that did not match what a check assumed --
do not silently adjust the check's PASS/FAIL to match an assumption instead
of the observation.

```

```

## Signature

Operator: ______________________   Date: ______________________
