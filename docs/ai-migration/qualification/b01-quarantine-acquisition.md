# B01-Q: bounded acquisition stopped on an unexpected response

Task `t_d32ff791`; branch `wt/t_d32ff791`. Status: **incomplete, requires human
response-policy decision; not independently reviewed**. This is a partial handoff,
not completion of the acquisition or verification acceptance criteria.

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
A shallow HTML prefix rejection is an error-page guard, not format qualification.

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
The task requires stopping on such responses; the guard has not been weakened.

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

## Decision required before any resumption

1. Recommended bounded change: explicitly permit an absent Content-Type for the
   exact pinned `.r00`/`.r01` URLs only, retaining verified HTTPS, original/final
   identity, HTTP 200, exact declared Content-Length, no encodings/redirects,
   opaque byte caps and error-page rejection. Implement/review the narrow response
   guard change before retrying only missing files; preserve the already acquired
   original and previous failed provenance. Impact: permits progress without a
   MIME header, but does not supply a prior trusted SHA-256 or rights/format proof.
2. Keep the strict MIME guard and leave acquisition paused until the same source
   supplies the expected header. Impact: no reduced response constraints and no
   additional acquisition; six files remain missing, with no automatic retry,
   alternate source search or rights inquiry.

This is not a repeated request for the already authorized O1 policy or acquisition
scope. No decision is inferred from notify/wake. B01 remains `triage`; no B01 or
B03/B04 gates/dependencies were changed.

## Actual verification and remaining work

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

The required full manifest/local-byte verifier and its missing/extra-file,
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
