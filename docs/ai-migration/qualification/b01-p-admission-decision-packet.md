# B01-P admission decision packet for quarantined external candidates

Status: decision packet pending independent review; no admission or execution authorization

Task: `t_d57469cd`

Evidence retrieval date: 2026-09-16 UTC

Reviewed basis: [M3-D3 mainline unblock reassessment](../m3-d3-mainline-unblock-reassessment.md)
at `54719ddbba262170a6aaf58cef9e5b37181c4569`, the
[O1 rights assessment](b01-o1-rights-review.md), the
[quarantine acquisition record](b01-quarantine-acquisition.md), and the
[member-admission plan](b01-member-admission-plan.md).

## Decision boundary

This packet assesses only whether the three already identified families have
sufficient public provenance and terms evidence to be considered for a future
native-oracle corpus. It is not legal advice. Independent review PASS confirms
only that this packet accurately presents the evidence and recommendation; PASS
is **not** operator admission.

No archive, opaque byte, archive member, or derivative was downloaded, opened,
listed, parsed, decoded, extracted, copied, imported, attached, or executed for
this packet. No acquisition script or archive tool was run. The seven archive
payload URLs were deliberately not requested. Only the five text/metadata URLs
listed under `External source retrieval ledger` were retrieved read-only.
Existing quarantine remains untouched and outside this worktree.

The following boundaries remain unchanged:

- `import_approved=false`, `qualified=false`, and `qualified_operations=0`;
- no product caller or CLI archive operation;
- the Windows facade remains fail-closed at `!ERROR`;
- GitHub-hosted VMs are not hostile-input containment;
- B01 `t_22299c6f` and all downstream gates remain unreleased;
- B04's freeze and the B05-MAN-WM/B07-MAN stop decisions remain controlling.

## Evidence classification

**Verified facts** below are limited to public text/metadata retrieved on the
stated date and reviewed repository records. **Unavailable evidence** means the
needed fact cannot be established without a prohibited payload/member inspection,
a new rights source, or both. **Assumptions** are not used to support any
recommendation.

The public identities are Debian source distribution `python-rarfile` version
`4.5-1`, exact `test/files/` paths and declared sizes. The Git object identifiers
are public upstream Git blob SHA-1 values exposed by the pinned tree metadata at
`d2f7df6fc843dae356fd6b0a85971dc36fd6e757`. They identify upstream Git objects
only. They do not establish that Debian's bytes equal those objects. The private
quarantine SHA-256 measurements are intentionally not repeated as public hashes:
they were not published by an authoritative public source and this card may not
reopen the quarantine to verify them.

## Candidate identities, evidence, and recommendations

| Candidate | Stable public identity and public immutable identifiers | Verified provenance and terms facts | Unavailable evidence | Assumptions not accepted | Recommendation and reason | What this recommendation does not prove |
| --- | --- | --- | --- | --- | --- | --- |
| `DRF-OLD` | Debian `python-rarfile` `4.5-1`: `test/files/rar3-old.rar` (102400 bytes; upstream blob `962d8b6f4b9d7e60396c1b5366f8962868c71fe1`), `rar3-old.r00` (102400; `0ba628367eaae36c92a648217e9baf96125c2acb`), `rar3-old.r01` (2572; `9bc19dde8cb2e46d3e064b83074c7fc4e7e5c3da`). | Debian's versioned `debian/copyright` assigns `Files: *` to Marko Kreen under ISC. DEP-5 says `*` matches slashes and the last matching stanza applies; the only later stanza is `debian/*`, so it does not match these paths. The pinned upstream commit is authored by Marko Kreen and has message `New test files for rar5` / `Move away from shell scripts to tox+nose`; this corroborates distribution attribution but is not a complete creation history. | Actual member identities, member authors/sources, member and metadata rights, contrary embedded notices, historical writer/build/invocation, Debian-to-upstream byte equality, and native behavior remain unavailable. | Do not assume `Files: *` proves a complete rights chain for every embedded member. Do not infer archive generation details from the commit message or filename. | **`defer`**. Container-path terms are affirmative, but complete member provenance/terms are unavailable and the current freeze forbids the inspection that might reveal contrary embedded evidence. If the operator requires proven member-level authority, choose `reject` instead. | It does not admit the family, establish member rights, prove RAR3/RAR4 behavior, verify volume order, authorize inspection, or qualify B01. |
| `DRF-SOLID` | Debian `python-rarfile` `4.5-1`: `test/files/rar5-solid.rar` (169 bytes; upstream blob `277cfe7206417067faf2fbd7c3f0bd7a1bf878a2`). | The same versioned `Files: *` ISC assignment applies. The pinned upstream commit attribution corroborates that the file is a project test asset. Public directory metadata confirms the exact path and size. | Actual member identities, member authors/sources, member and metadata rights, contrary embedded notices, historical writer/build/invocation, Debian-to-upstream byte equality, and actual solid/compression/native behavior remain unavailable. | Do not treat small size, expected test-data names, or project placement as a member-rights grant. Do not infer decoder behavior from public metadata. | **`defer`**. The path-level ISC evidence supports preservation in quarantine, but it does not resolve the rights of actual embedded members and no authorized safe inspection route exists. If complete member-level authority is mandatory now, choose `reject`. | It does not admit the family, establish member rights, prove compressed-solid interoperability, authorize decoding, or qualify B01. |
| `DRF-VOL` | Debian `python-rarfile` `4.5-1`: `test/files/rar5-vols.part1.rar` (102400 bytes; upstream blob `0926f2f8f6d74bd1a7e8c4c1ebe74432c0b8d4e2`), `part2` (102400; `d4f55a2f859d0c7b422b99e111db4fc5e8b7e34f`), `part3` (11384; `ba6e9924a6db984d321364b8788301cda8c3bfba`). | The same versioned `Files: *` ISC assignment applies. The pinned upstream commit attribution corroborates that the entrypoint is a project test asset. Public directory metadata confirms all three exact paths and sizes. | Actual member identities, member authors/sources, member and metadata rights, contrary embedded notices, historical writer/build/invocation, Debian-to-upstream byte equality, actual volume membership/order, and missing-volume/native behavior remain unavailable. | Do not infer a complete volume set or rights chain from numbered filenames. Do not equate public upstream blob IDs with Debian payload identity. | **`defer`**. Public container-path terms exist, but member rights and the actual multipart relationship cannot be established within the no-execution boundary. If the operator requires complete member-level authority, choose `reject`. | It does not admit the family, establish member rights, prove multipart semantics, authorize listing/testing, or qualify B01. |

### Common terms and obligations if admission is later approved

The retrieved Debian copyright file grants permission to use, copy, modify,
and/or distribute under ISC, provided the copyright and permission notice appear
in all copies. Any later authorized copy or derivative must preserve the full
copyright, permission, and disclaimer text and retain the exact
source/version/path and rights-review binding. It must not be relicensed as CC0
or MIT. The separate `debian/*` GPL-2+ stanza applies to Debian packaging files,
not these selected `test/files/` paths; copying packaging material would require
a separate obligations review.

These are engineering evidence findings, not a legal conclusion. Absence of a
selected-path exception is not proof that no embedded third-party rights exist.

## Fact, unavailable-evidence, and assumption summary

Verified facts:

1. All seven exact paths and sizes are present in the versioned Debian directory
   metadata.
2. Debian's versioned copyright file has a general `Files: *` ISC stanza and one
   later `debian/*` GPL-2+ stanza.
3. Under the retrieved DEP-5 rules, `*` matches slashes and the last matching
   stanza applies. The selected `test/files/` paths therefore match the ISC
   stanza and not the `debian/*` override.
4. The pinned upstream tree publishes the seven Git blob SHA-1 identifiers in the
   candidate table.
5. Pinned commit `6ab3317c6a02c4f1082ab8570a34d4868c7baa3c` names Marko Kreen as author and
   contains the message `New test files for rar5` / `Move away from shell scripts
   to tox+nose`.

Unavailable evidence:

- complete actual member inventory and hashes;
- original source, author, and applicable terms for every embedded member and its
  names/metadata;
- any contrary notice embedded in a candidate;
- original writer identity, version, build, and invocation;
- proof that Debian's bytes equal the pinned upstream Git objects;
- safe inspection containment and current execution authority;
- native Windows/Linux/macOS oracle behavior and all B01 compatibility results.

Assumptions:

- None are relied upon. In particular, this packet does not assume that a
  container-level distribution declaration necessarily covers every embedded
  member, that absence of a discovered exception means permission, or that
  filenames/expected metadata prove archive semantics.

## Recommendation and exact future operator decision

Recommended disposition: **`defer` all three candidates and retain quarantine**.
This is conservative because public path-level ISC evidence is affirmative, but
member-level provenance and terms remain unavailable and cannot be resolved under
the current no-inspection/freeze boundary. `defer` permits a later decision if
material new public rights evidence or separately authorized, independently
reviewed inspection evidence becomes available. If the operator's threshold is
complete demonstrated member-level authority before any corpus admission, the
appropriate disposition is `reject`, not a policy exception.

After independent review of this packet, ask the operator exactly:

> Under the evidence currently recorded in this packet, for each of `DRF-OLD`,
> `DRF-SOLID`, and `DRF-VOL`, do you choose `reject` or `defer` for future
> native-oracle corpus consideration? The recommended choice is `defer` for all
> three because actual-member provenance/rights, Debian-to-upstream identity, and
> an authorized safe inspection path remain unresolved. Neither choice authorizes
> import, inspection, execution, native-oracle use, or B01 qualification.

`admit` is not an available disposition under the current evidence. It may be
considered only after material new evidence resolves the listed actual-member
rights/provenance and identity gaps, that evidence is documented in a revised
packet and independently reviewed, and the operator then makes a new explicit
admission decision. Merely accepting the current evidence limits cannot substitute
for that evidence or create an admission path.

No candidate may be imported, inspected, or used in a native oracle under this
packet or the operator's `reject`/`defer` answer. A notification, reviewer PASS,
prior quarantine-acquisition approval, or acceptance of unresolved risk is not an
admission decision or safety authority.

## External source retrieval ledger

Every external URL cited by this packet was retrieved read-only on 2026-09-16
UTC. `curl -L --fail --max-time 30` returned HTTP 200 for each URL. The GitHub
tree and commit metadata were additionally filtered read-only with `jq` to record
only the identifiers and attribution above. No archive payload URL was requested.

| Source | URL | Result and use |
| --- | --- | --- |
| DEP-5 copyright format 1.0 | https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/ | HTTP 200; verified wildcard slash matching and last-matching-stanza precedence. |
| Debian `python-rarfile` `4.5-1` copyright | https://sources.debian.org/data/main/p/python-rarfile/4.5-1/debian/copyright | HTTP 200; verified `Files: *`, Marko Kreen, ISC text, and `debian/*` GPL-2+ exception. |
| Debian versioned directory metadata | https://sources.debian.org/api/src/python-rarfile/4.5-1/test/files/ | HTTP 200; verified exact seven public paths and declared sizes. |
| Pinned upstream tree metadata | https://api.github.com/repos/markokr/rarfile/git/trees/d2f7df6fc843dae356fd6b0a85971dc36fd6e757?recursive=1 | HTTP 200; verified seven public Git blob SHA-1 identifiers and sizes. |
| Pinned upstream commit metadata | https://api.github.com/repos/markokr/rarfile/commits/6ab3317c6a02c4f1082ab8570a34d4868c7baa3c | HTTP 200; verified commit identity, author, and message. |

## Validation scope

This is a documentation-only decision packet. Runtime/archive tests are
inapplicable because no executable behavior, fixture, golden, workflow, gate,
or archive payload changes. Running an archive tool would violate the scope and
could not establish rights. Validation is therefore limited to reviewed-parent
ancestry, external text/metadata retrieval, local-link/path resolution, exact
single-file diff scope, Markdown whitespace, and the unchanged migration DAG.

Compatibility remains unmeasured: this packet does not characterize archive,
volume, error, password, filesystem, cancellation, GUI, or desktop behavior on
Windows, Linux, or macOS. Licensing remains bounded to the cited public evidence;
actual embedded-member applicability is unresolved.
