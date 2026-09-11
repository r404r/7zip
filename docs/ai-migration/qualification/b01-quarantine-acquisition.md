# B01-Q: bounded quarantine acquisition and reviewed-resume preparation

Task `t_d32ff791`; branch `wt/t_d32ff791`. Status: **1/7 acquired; resume
preparation awaiting independent stage review**. The MIME decision is resolved,
but no network acquisition occurred during this preparation stage. Stage PASS
must return this same card to tester, not complete it. Final acquisition and
independent acceptance remain pending.

## Authority and preflight

Original B01 `t_22299c6f` records the actual operator decision `批准方案1`
at timestamp `1789128797`, authorizing only acquisition and quarantined retention
of the seven pinned files in the [reviewed rights matrix](b01-o1-rights-review.json).
No corpus import, extraction, listing, testing, writer/upstream execution, native
CI, wider search, mirror substitution, publication or paid action is authorized.
The [replay policy](b01-replay-policy.md) and
[rights assessment](b01-o1-rights-review.md) remain controlling.

Both source and assigned worktree AGENTS.md were read. Source checkout remained
`ai/migration-bootstrap-20260911`; task worktree was clean before changes.
Reviewed parent `3cf4421d081b912763e326c47322f095211fbd47` is already an ancestor
of task HEAD `3ccb200`; no parent merge was necessary. Matrix raw SHA-256:
`0f8af166ddbd150f951a1910525c1d842275f3e20e2ff9731b24ac39b70a02a8`.
Complete parent subscription inheritance and default Telegram `notify+wake`
were checked read-only against the board database; both returned `True`. No route
identities were emitted and no subscription/configuration changes were made.

## Actual acquisition and stop

The explicit one-shot [acquisition script](../../../.github/tests/migration/b01-quarantine/acquire.py)
uses Python standard-library HTTPS with certificate/hostname verification,
no redirect following, no retries, identity encoding and fixed response-size
bounds. It requires HTTP 200, exactly the reviewed Content-Length, no transfer or
content encoding, and a binary Content-Type allowlist before reading a body.
Each read is capped to the remaining reviewed byte budget; it does not probe an
extra byte. HTTP Content-Length defines the response body boundary; this is not
inspection of trailing transport bytes. No archive signature/member parser runs.
A shared markup-looking response rejection is an error-page guard, not format
qualification; the stage-review repair below supersedes the original shallow check.

At `2026-09-11T12:31:12.828193+00:00`, the first exact URL returned HTTP 200,
`Content-Type: application/vnd.rar`, `Content-Length: 102400`, no redirect and no
transfer/content encoding. The 102400 opaque bytes were stored and reopened for
SHA-256 verification. A subsequent independent `sha256sum` and `wc -c` agreed:

- Source path: `test/files/rar3-old.rar` (Debian `python-rarfile` `4.5-1`).
- SHA-256: `57f57c2d61f4a6b437cbb38fbabecb42e6f826b5d3ce952d6e74cbbc7d5dcd71`.
- Durable path: `/home/ding/work/github/r404r/b01-quarantine-t_d32ff791/DRF-OLD/rar3-old.rar.opaque`.
- File mode `0400`; containing task quarantine root mode `0700`. Directory execute
  bits permit traversal only; files are non-executable. No noexec mount is claimed.

At `2026-09-11T12:31:13.469689+00:00`, the next exact request returned:

```text
URL: https://sources.debian.org/data/main/p/python-rarfile/4.5-1/test/files/rar3-old.r00
HTTP status: 200
Content-Type: absent (manifest null)
Content-Length: 102400
Content-Encoding: absent
Transfer-Encoding: absent
Location: absent
ValueError: unexpected Content-Type: ''
```

The header guard stopped before calling the body reader. No `.r00` payload was
saved or accepted; the transport may buffer network bytes while obtaining headers,
so this is not a claim that no body bytes reached the socket. No further URL was
requested. Missing MIME metadata is not evidence of a rights conflict or archive
corruption; it is an unexpected response under this strict acquisition guard.
The first attempt stopped as required. Its evidence is unchanged; the later
operator-authorized exception is described below and has not been used online.

## Exact incomplete set

The [manifest](../../../.github/tests/migration/b01-quarantine/manifest.json) records
all seven paths in the reviewed candidate/part order, their fixed URLs, declared
sizes, notice bindings, unknown hashes and actual retrieval outcomes:

| Candidate | Source path | Outcome | Declared / acquired bytes |
| --- | --- | --- | --- |
| DRF-OLD | `test/files/rar3-old.rar` | acquired_quarantined | 102400 / 102400 |
| DRF-OLD | `test/files/rar3-old.r00` | failed_stopped before body read | 102400 / unknown |
| DRF-OLD | `test/files/rar3-old.r01` | not_attempted | 2572 / unknown |
| DRF-SOLID | `test/files/rar5-solid.rar` | not_attempted | 169 / unknown |
| DRF-VOL | `test/files/rar5-vols.part1.rar` | not_attempted | 102400 / unknown |
| DRF-VOL | `test/files/rar5-vols.part2.rar` | not_attempted | 102400 / unknown |
| DRF-VOL | `test/files/rar5-vols.part3.rar` | not_attempted | 11384 / unknown |

Only one of seven files is acquired; six remain unavailable. Null size/hash fields
are unknown/unacquired, never fabricated zero-length evidence. `final_url` on the
failed request is the original request URL because redirects are never followed;
it does not imply a successful payload retrieval. `retrieved_at_utc` is the request
start timestamp, including the failed request.

The durable quarantine root is outside Git and outside the task worktree, not
scratch storage. It contains one opaque file, three per-family `NOTICE.txt` files,
and a copy of the manifest. Preserve it through review/retries. The downloaded
bytes must never be staged, attached, pushed, previewed, parsed or executed.
Each family notice is the exact selected stanza from the reviewed matrix plus a
final newline, retaining literal copyright, permission and full ISC disclaimer.
Tracked notice copies: [DRF-OLD](../../../.github/tests/migration/b01-quarantine/DRF-OLD-NOTICE.txt),
[DRF-SOLID](../../../.github/tests/migration/b01-quarantine/DRF-SOLID-NOTICE.txt),
[DRF-VOL](../../../.github/tests/migration/b01-quarantine/DRF-VOL-NOTICE.txt).

## Resolved decision and pre-network stage gate

Actual operator decision `按照推荐1进行`, recorded on this card at `1789130330`,
authorizes an absent Content-Type only for these two complete URLs:

```text
https://sources.debian.org/data/main/p/python-rarfile/4.5-1/test/files/rar3-old.r00
https://sources.debian.org/data/main/p/python-rarfile/4.5-1/test/files/rar3-old.r01
```

Explicit empty/wrong MIME remains rejected; this is not a suffix/domain exception.
TLS, exact original/final URL, HTTP 200, exact length, streaming byte caps,
encoding/redirect/error-page guards remain mandatory. Missing MIME is recorded
as JSON null, never synthesized. This resolves the previous human gate, not the
remaining evidence/qualification limits.

The same decision requires independent review of the exact guard/resume commit
BEFORE any more GETs. Stage PASS must be recorded and the SAME card returned to
tester for the six previously authorized files, without another MIME permission
question. Do not complete the card at stage PASS. Final review after acquisition
may complete only B01-Q; B01/B03/B04 gates remain unchanged.

This is not a repeated request for the already authorized O1 policy or acquisition
scope. No decision is inferred from notify/wake. B01 remains `triage`; no B01 or
B03/B04 gates/dependencies were changed.

## First attempt verification (historical, commit ed7950b)

Commands run from the task worktree root:

```text
python3 .github/tests/migration/b01-quarantine/check_controls.py
python3 .github/tests/migration/b01-quarantine/check_document.py
python3 -m json.tool .github/tests/migration/b01-quarantine/manifest.json /dev/null
git diff --check
python3 .github/tests/migration/b01-quarantine/acquire.py --acquire-approved-seven
sha256sum /home/ding/work/github/r404r/b01-quarantine-t_d32ff791/DRF-OLD/rar3-old.rar.opaque
wc -c /home/ding/work/github/r404r/b01-quarantine-t_d32ff791/DRF-OLD/rar3-old.rar.opaque
stat -c '%a %F %n' /home/ding/work/github/r404r/b01-quarantine-t_d32ff791 /home/ding/work/github/r404r/b01-quarantine-t_d32ff791/DRF-OLD/rar3-old.rar.opaque
cmp .github/tests/migration/b01-quarantine/manifest.json /home/ding/work/github/r404r/b01-quarantine-t_d32ff791/manifest.json
cmp .github/tests/migration/b01-quarantine/DRF-OLD-NOTICE.txt /home/ding/work/github/r404r/b01-quarantine-t_d32ff791/DRF-OLD/NOTICE.txt
```

Response controls were written in RED/GREEN slices: missing bounded-reader and
missing header-guard assertions each failed before implementation. The final two
response-control tests pass, including HTTP 302/404, wrong/missing length,
transfer/content encoding, HTML MIME and short-body rejection, and a read-position
check showing no over-cap byte request. These use harmless local `BytesIO`, not
archive golden data. Acquisition exited 1 at the literal error above. Hash/length,
mode and both `cmp` commands passed. No body/archive/native tests were run.
Partial document checks passed for JSON, matrix digest, all three exact notices
and eight local links; outcome counts are one acquired, one failed, five unattempted.
JSON parsing and whitespace checks also passed. This is not the pending full
manifest verifier or its negative-control suite.

At that stopped commit, the required full manifest/local-byte verifier and its missing/extra-file,
wrong-size/hash/source and unexpected-accepted-status negative controls are NOT
implemented or claimed to pass in this stopped attempt. All-seven byte validation,
independent review and acquisition completion remain pending. The current code is
unreviewed partial work, not a reusable approved downloader; its one-shot directory
creation deliberately refuses to overwrite this quarantine on rerun. Resume must
preserve prior evidence rather than deleting the directory to rerun.

No production builds are applicable: only quarantine bookkeeping code was added;
archive/native execution is explicitly outside this authorization. Historical
writer, actual members/rights/hashes and all native compatibility remain unknown.
Hashes identify bytes only, not legal authority, interoperability or qualification.
Top-level, family and per-file `import_approved=false`, `qualified=false` remain.
Zero extra product fees, no releases, no shared-branch integration or binary Git
publication. Independent reviewer must inspect safe byte identities and complete
scope controls after the blocker is resolved; this report does not self-approve.

## Current preparation implementation and offline evidence

Changes build on `ed7950b87b50ae305d51b7e26ccf6a0dabdc56f6`; no reviewed parent
merge was needed. Both AGENTS.md, source branch and parent ancestry were rechecked.
Current B01 comments still leave B01 `triage`. Read-only subscription verification
again returned complete parent inheritance and default Telegram `notify+wake` true.

- [Header/local verifier](../../../.github/tests/migration/b01-quarantine/quarantine.py):
  exact two-URL exception; duplicate guard headers and Location rejected; strict
  private directory, regular-file/no-link, size/hash, source/order/status/notice
  bindings and exact tree inventory checks. Existing success metadata is immutable.
- [Resume entry point](../../../.github/tests/migration/b01-quarantine/resume.py):
  authenticates matrix and stopped manifest digests before planning. Preflight
  reopens the existing opaque file; only six missing records are eligible, in the
  original reviewed order. No directory deletion, replacement or request of the
  already acquired original. The original manifest/notices are never rewritten.
- A future explicit resume creates `resume.json` exclusively before its first GET.
  That separate file retains new attempt state, while original `manifest.json`
  retains the literal failed response forever. State updates use exclusive
  `.resume.json.tmp`, fsync and replace only this attempt's state. Existing attempt
  marker, partial write, unknown extra file, corrupt evidence or interruption stops
  rather than retrying. No cleanup erases forensic evidence. Files use exclusive
  creation and mode 0400; all acquired bytes are reopened and hashed after each GET.
- [Local negative controls](../../../.github/tests/migration/b01-quarantine/check_resume.py)
  use only temporary `harmless` bytes and explicitly synthetic notices/provenance.
  They are not archive golden data or evidence of TLS/server/native compatibility.
  Injected transport tests exercise the real response guard/reader without sockets;
  the actual SSL context still requires certificates and hostname verification.

Commands executed in this preparation stage (all from this worktree):

```text
python3 .github/tests/migration/b01-quarantine/check_controls.py
python3 .github/tests/migration/b01-quarantine/check_resume.py
python3 .github/tests/migration/b01-quarantine/resume.py --preflight
python3 .github/tests/migration/b01-quarantine/check_document.py
python3 -m json.tool .github/tests/migration/b01-quarantine/manifest.json /dev/null
python3 -m py_compile .github/tests/migration/b01-quarantine/quarantine.py .github/tests/migration/b01-quarantine/resume.py .github/tests/migration/b01-quarantine/check_controls.py .github/tests/migration/b01-quarantine/check_resume.py
sha256sum .github/tests/migration/b01-quarantine/manifest.json /home/ding/work/github/r404r/b01-quarantine-t_d32ff791/manifest.json /home/ding/work/github/r404r/b01-quarantine-t_d32ff791/DRF-OLD/rar3-old.rar.opaque
wc -c /home/ding/work/github/r404r/b01-quarantine-t_d32ff791/DRF-OLD/rar3-old.rar.opaque
git diff --check
git diff --cached --check
```

RED observed: new MIME API was absent; local verifier and resume module missing;
duplicate Content-Length/Content-Type accepted. GREEN: four header/stream tests
and three local/transport/resume tests pass. Subcontrols include missing/extra
files, wrong size/hash/source/final URL, accepted/qualified status, path escape,
symlink, execute permission and changed notice; corrupt preflight makes zero
fetch calls and creates no marker. Complete synthetic six-file continuation and
first-response failure both preserve original evidence; a second invocation makes
zero further calls. Expected injected failure prints
`ValueError: synthetic response conflict`; it is not a live retrieval failure.
Offline preflight reports exactly the six missing paths in the table above.
Document/JSON/compile/whitespace checks pass. Existing manifest SHA-256 remains
`5bf0600459996c638697eb902d789670186db72197d65665b3ee881b0f59655e` in both locations;
opaque file digest and 102400-byte count remain unchanged. No acquired binaries,
notices or manifests were modified in this stage. No production build is applicable.

Only after exact-commit stage PASS, the tester may execute (NOT run in this stage):

```text
python3 .github/tests/migration/b01-quarantine/resume.py --resume-reviewed-six
python3 .github/tests/migration/b01-quarantine/resume.py --verify-complete
```

The CLI opt-in is an operational guard, not a cryptographic proof of reviewer
approval: the worker must check the actual stage verdict first. After execution,
preserve and commit the separate result JSON and update this report with real
hashes/outcomes before final review; never replace the original stopped manifest.
The complete verifier has only been exercised on harmless synthetic data so far;
no seven-file live completion is claimed. Filesystem checks assume one worker and
no concurrent same-owner tampering in the private root; this is not a malicious
local-user sandbox or crash-proof transaction. HTTP Content-Length defines the
body boundary; no over-budget probe or format validation is authorized. All rights,
historical writer, member hashes, native/GUI/desktop qualification limits remain.

## Stage CHANGES repair: wrapped error-page rejection

Independent reviewer rejected preparation commit `9a5d8e3f76e9fbe09158ca59e1abc126c3caaaed`
in comment 112: both acquisition paths accepted HTML preceded by a UTF-8 BOM or
comment. This is the first substantive review failure, not a reopened MIME gate.
No stage PASS exists yet; no real GET was made during this repair.

The root cause was duplicated checks for only two literal prefixes after whitespace.
Both paths now call `check_opaque_body` before writing any opaque file. It examines
only the already length-capped response bytes, skips leading ASCII whitespace and
one optional UTF-8 BOM, and conservatively rejects a leading `<`. Comments, HTML
doctypes and XML/XHTML declarations are therefore stopped without parsing their
contents or trusting a closing delimiter. This intentionally also rejects other
markup-looking responses; false positives require inspection, not automatic retry.
This is not a general content classifier, archive signature test, rights check or
proof that an accepted body is an archive. No extra reads/GETs, archive libraries,
MIME exceptions or source substitutions were added.

[Error-page regressions](../../../.github/tests/migration/b01-quarantine/check_error_pages.py)
exercise real `fetch_one`, real `run_resume` with its default fetch, and the initial
`acquire.main` path. Only HTTPS transport and temporary destinations are patched.
Six synthetic page variants cover bare HTML, BOM, comments, repeated comments with
doctype, XML-declared XHTML and combined BOM/XML/comments. The fetch control uses
the exact pinned `.r01` URL and 2572 bytes with missing MIME. Resume controls use
the pinned first pending `.r00` URL and 102400 bytes. Tests enforce bounded reads,
one request only, closed connections, no new opaque file, retained original
manifest/notices/synthetic prior success, saved HTTP/null MIME/final URL/error
evidence and no request on a second invocation. An ordinary synthetic binary body
is the positive control. No acquired original is mutated or parsed.

Repair commands (from task worktree):

```text
python3 .github/tests/migration/b01-quarantine/check_error_pages.py
python3 .github/tests/migration/b01-quarantine/check_controls.py
python3 .github/tests/migration/b01-quarantine/check_resume.py
python3 .github/tests/migration/b01-quarantine/resume.py --preflight
python3 .github/tests/migration/b01-quarantine/check_document.py
python3 -m json.tool .github/tests/migration/b01-quarantine/manifest.json /dev/null
python3 -m py_compile .github/tests/migration/b01-quarantine/acquire.py .github/tests/migration/b01-quarantine/quarantine.py .github/tests/migration/b01-quarantine/resume.py .github/tests/migration/b01-quarantine/check_error_pages.py
python3 .github/tests/migration/b01-quarantine/__pycache__/audit_repair.py
sha256sum .github/tests/migration/b01-quarantine/manifest.json /home/ding/work/github/r404r/b01-quarantine-t_d32ff791/manifest.json /home/ding/work/github/r404r/b01-quarantine-t_d32ff791/DRF-OLD/rar3-old.rar.opaque
wc -c /home/ding/work/github/r404r/b01-quarantine-t_d32ff791/DRF-OLD/rar3-old.rar.opaque
stat -c '%a %F %n' /home/ding/work/github/r404r/b01-quarantine-t_d32ff791 /home/ding/work/github/r404r/b01-quarantine-t_d32ff791/DRF-OLD/rar3-old.rar.opaque
git diff --check
git diff --cached --check
```

RED: new regressions failed in 15 subcases before the implementation repair:
wrapped bodies returned success or caused a second mock request. GREEN: three
new regression methods, four existing header/stream tests and three existing
resume/verifier tests pass. The latter retains the expected diagnostic
`ValueError: synthetic response conflict`. Offline preflight still reports six
pending files. Document checks cover three notices and twelve local links;
JSON/compile/diff checks pass. Original manifest hashes, opaque hash, 102400-byte
length and modes remain exactly as recorded above. Read-only audit reconfirmed
B01 `triage` and inherited default Telegram `notify+wake` without route disclosure.
The audit helper is ignored local scratch, not a deliverable or new dependency.

Changed deliverables in this repair: `acquire.py`, `quarantine.py`, `resume.py`,
`check_error_pages.py` under the owned quarantine bookkeeping directory, and this
report. No real quarantine bytes/notices/manifests changed, no production build
is applicable, and no compatibility qualification is claimed. Request same-card
stage re-review on the committed repair; PASS must return to tester without
completing or integrating the still-incomplete acquisition card.
