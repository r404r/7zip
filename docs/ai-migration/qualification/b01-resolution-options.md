# B01-R: evidence-proportionate resolution options

Task `t_ec0aaad1`; branch `wt/t_ec0aaad1`; research date 2026-09-11 UTC.
Status: **proposal for independent review, not a B01 qualification or import decision**.
Companion: [structured options and evidence matrix](b01-resolution-options.json).

## Decision in brief

**No complete solution is available now. A practical route exists to stop asking
for an unavailable original writer binary while retaining a meaningful immutable
legacy oracle, but it requires an explicit evidence-policy decision.** This is
an engineering recommendation, not a finding that exact fixture rights are
already established, not legal advice, and not a native test result.

Ranked paths (all zero incremental product fees, all pending human decision):

1. **O1 — approve a two-track provenance policy and a small rights-reviewed
   existing-fixture pilot.** Distinguish replay of fixed bytes from recreation by
   a known writer. Prioritize the Debian-packaged rarfile old-volume, RAR5 solid
   and RAR5 stored-volume families. Review distribution-wide coverage plus source
   authorship instead of requiring an unattainable historical executable hash.
   Unknown generator fields remain null, not invented. Native qualification and
   full B01 coverage remain separate gates. This is the most practical corpus
   path, not an instruction to import these files now.
2. **O2 — authorize one narrow rights inquiry / voluntary fixture donation round.**
   Seek clarification for exact existing bytes first, or an explicitly licensed
   replacement contribution. Do not commission or run a commercial writer, ask
   for keys, or use a trial. Send nothing without approval. If the policy in O1
   is rejected, the donor must meet the existing generation evidence requirement;
   this substantially limits feasibility. Stop after one bounded round rather
   than repeatedly searching or waiting indefinitely.
3. **O3 — approve a separately reviewed qualification/dependency partition.**
   Keep unqualified RAR routes closed in the new application, preserve the old
   executable as a preselected alternative, and qualify only explicitly selected
   operations/formats first. This advances a smaller opt-in product surface, not
   full compatibility and not completion of B01. It is complementary to O1/O2,
   not a way to create missing RAR evidence.

No purchase, proprietary execution, upstream correspondence, payload/archive GET,
extraction, code execution from upstream, fixture import, acceptance edit, DAG edit,
production edit, or B01 state change was performed. `t_22299c6f` remains `triage`
with its existing unresolved `needs_input` escalation. A report PASS only approves
this analysis. It is not consent to any option or a qualification waiver.

## Authority and requirement archaeology

Both AGENTS.md files were read. The source checkout is on
`ai/migration-bootstrap-20260911`; task HEAD began at
`f2b1688a4c1a362bc947df98f1f85447e07e9bdc`. Reviewed B01-P
`34ba13bd440647ded178e07c6b08cd53e15b239b`, B01-W
`11ea1a217ed2fdd801346e1e0b7bd576447e9092`, B01-L
`daa88ed034ea46f6940932580339ad95c98dbcc2`, and B01-F
`8b151f71255ea26288a0926ac3306d8881122e2a` are ancestors. No integration needed.
The full current B01 comment thread was read, including the decision to retain
full acceptance and the later exclusion of paid/trial/already-owned commercial
writer execution. The new request authorizes bounded research only.

| Requirement | Actual origin | Meaning / proposed disposition |
| --- | --- | --- |
| Legacy is the oracle; no golden edits to hide drift; retained codecs; native Windows/Linux/macOS | [AGENTS.md](../../../AGENTS.md), lines 24–28, 64–78 | Product/compatibility invariants, unchanged. A new reader result cannot replace the old oracle. |
| Actual generator/version/license provenance; immutable external bytes/hashes; unsupported/CRC/truncation/volume outcomes | [M1](../characterization-baseline.md), lines 155–173, especially B01 row 166 | An explicit reviewed qualification requirement, not merely an audit invention. Allowing unknown generator/version needs human-approved amendment, even if scientifically reasonable for replay. |
| Match each changed operation to measured scope; actual legacy executable digest/toolchain; separate structured errors; no destructive fallback | [M2 stages](../migration-stages.md), lines 24–30, 71–93, 95–110 | The binary digest here identifies the **reader/oracle**, not necessarily the historical archive writer. Unchanged. |
| B01 manifest generator/version/license/provenance, per-operation reports; B01 gates S2a/S3/B05/S5 | [M3 DAG](../migration-dag.md), lines 52–58, 93–123 | Existing graph and card contracts remain binding. A report cannot bypass these edges. |
| Exact writer build/options and creator attestation for historical fixtures | [B01-P](b01-provenance.md), lines 158–182 | Evidence elaboration of M1, not a claim that copyright law universally requires compiler/build metadata. P/L rights questions are distinct from G reproducibility. |
| Package and executable digest, bundled terms/manual, exact argv, full authoring environment and repeat authoring | [B01-W](b01-writer-plan.md), lines 183–238, 290–326 | Appropriate prospective controls for an authorized **new-generation campaign**. Not named as universal historical-writer-hash requirements in AGENTS/M1/M2. Do not automatically transfer every campaign field to acquired legacy fixtures. |
| Existing-fixture audit asks for actual build/log/member binding | [B01-F](b01-existing-fixture-assessment.md), lines 74–109 | Accurate description of the stricter audit gaps. Its PASS was not a human decision to make every later field an immutable product semantic. Still no author-side relaxation. |
| No separately obtained commercial authorization; zero added fees | [B01-L](b01-writer-license-decision.md), lines 8–41, and B01 operator comments | Paid, trial and existing commercial writer routes are excluded, not waiting for another procurement request. Open-source notices still apply. |

The unreviewed B01 implementation at
`9d01d5069f5b117aa5c69dd5cc62f090869d7650` was read via `git show` only.
Its manifest and `docs/ai-migration/qualification/b01.md` were not integrated.
It reports partial CLI/numeric evidence but explicitly excludes full list/create
numeric observation, stable item identity and full coverage. Those are reported
historical results, not independently re-run or approved by this research.

### Engineering analysis: replay is not regeneration

For a differential regression experiment, the input is a fixed byte sequence.
If the same immutable archive/volume set is presented to a pinned native legacy
reader and the replacement, differences in outputs and effects are measurable
without possessing the original writer. A writer hash helps explain creation and
reproduce the input, but is not logically necessary to replay the input. This is
an engineering inference, not evidence that a particular candidate is legal or
covers a particular method.

Two different claims must not be conflated:

- **Replay claim:** these exact bytes exercise these measured native behaviors.
  Bind source revision/package/path, all part hashes/order, full member inventory,
  rights assessment/notices, actual reader binary/build/environment, raw/numeric
  outcomes, repeat equality, unchanged controls and deliberate drift failures.
- **Generation/interoperability claim:** writer X/build Y/options Z produced these
  bytes. Require actual writer/version/build/log evidence for that claim. Unknown
  writer/version cannot be filled from unpack version, format signature, filename,
  timestamps, Git commit author, or a reader's own version. Do not advertise
  interoperability with a named writer/version that has not been established.

O1 proposes manifest `schema_version=1` with explicitly validated null unknowns
and a linked evidence-class record, not silent field/type changes. Proposed
classes are `acquired-immutable` and `generated-reproducible`. No such classes
have been implemented. Existing writer-provenance checks must be deliberately
revised, reviewed and negatively tested before using nulls. Known generator
information must still be recorded; uncertainty is not permission to discard it.
New generation retains B01-W's prospective recording discipline when a route
consistent with the operator constraint actually exists.

Rights are a separate axis. A missing exact writer hash is not itself a missing
copyright grant. Conversely, a known writer cannot grant rights to someone
else's embedded HTML, text, names, metadata or executable. Public availability,
small size and a software root LICENSE are not automatic exact-payload grants.
A distribution copyright manifest is affirmative licensing evidence, not a legal
warranty and not a new grant from a maintainer who lacks authority. A reviewer
may assess repository-wide coverage and authorship as sufficient evidence without
insisting on a newly signed per-file license; that assessment must identify
scope, exceptions and uncertainty. Unknown rights are not a finding of prohibited
use. This report neither declares a universal legal rule nor certifies rights.

## Bounded new public evidence

The search stopped at **four additional project/distribution research units**:
Debian `libarchive` 3.8.9-1; `selmf/unarr` at
`3307cd3fdcffe3b98326872c601bbf7235386441`; Debian `python-rarfile` 4.5-1
(with the already-known upstream pin for history context); Debian `unrar-free`
1:0.3.3-1. Exactly **eight candidate families** below were assessed. Unrar-free
was screened but supplied no selected family. Prior junrar leads remain solely
reviewed parent context; they were not fetched again or counted as new candidates.
No ninth family or fifth project was pursued.

### Distribution manifests are materially new evidence

Debian's copyright-format specification states that `*` matches slashes and
leading dots, unlike shell globs.[1] The libarchive 3.8.9-1 manifest has
`Files: *` and a more specific `Files: libarchive/*` BSD-2-clause stanza,
including Tim Kientzle and Andres Mejia; the inspected later exceptions name C
files, not the selected `.uu` paths.[3] Thus its declared coverage includes the
selected test-file paths; restricting that glob to top-level `.c` files would
misread the format. This is stronger than only citing a neighboring C license.
It is **distribution-maintainer attribution**, not an exact embedded-content
attestation. Its BSD notice-retention conditions must be preserved.[3]

The Debian python-rarfile 4.5-1 manifest declares `Files: *`, Marko Kreen
2005–2026, ISC; the later `debian/*` stanza is GPL-2+ packaging, not the test
files' assigned license.[8] Pinned upstream histories for the three family
entrypoints name Marko Kreen and commit
`6ab3317c6a02c4f1082ab8570a34d4868c7baa3c`, “New test files for rar5”.[20][21][22]
This cross-check aligns the distribution's named author with contribution history,
but does not prove that this person created every member or held all output rights.
History is current-path bounded; no original-generation or exhaustive rename-history
claim is made. In particular the commit message does not turn `rar3-old` into RAR5.

Debian versioned directory metadata lists the selected files; the JSON preserves
paths and sizes. Upstream Git tree metadata also binds unarr and rarfile objects
to pinned revisions.[4][9] The unarr commit metadata binds the named commit to
tree `61c07dab16fdf88c42694c512505564adca49d4e`.[24] **No Debian archive-byte equality with the earlier
upstream pins is claimed.** Versioned distribution URLs are stable version
identities, not locally verified archive hashes. The exact Git blob identities in
the matrix refer only to the upstream objects; native archive/member SHA-256
fields remain null. After permission, acquisition must bind the actual selected
Debian bytes before any accepted fixture or rights mapping is frozen.

### Candidate matrix (leads, not accepted fixtures)

Full paths, metadata identities, literal quotes, evidence types and uncertainty
are in the JSON. All eight families are `unqualified` and `import_approved=false`.

| Family ID | Candidate / new evidence | Likely role and outstanding issue |
| --- | --- | --- |
| DLA-BASIC | Debian `libarchive/test/test_read_format_rar.rar.uu`; new distribution BSD path coverage; test expects `test text document\r\n`.[3][12] | R4-STORE lead from parent context, not measured here. Establish container/member applicability; symlink/name metadata and writer unknowns remain. |
| DLA-MULTI | Debian `test_read_format_rar_multivolume.part0001.rar.uu` through `part0004`; new path coverage, existing upstream contribution trace in B01-P.[3] Test declares a 241647978-byte member.[12] | Classic multipart behavior lead, **not B01-W's stored R4-VOL replacement**. Whole large text/HTML rights and resource bounds need resolution. Lower priority than small original-content leads. |
| U4-STORE | unarr `test/corpus/integration/lipsum_rar4_store.rar`; tree and current-path history “Add support for integration tests”.[4][14] | R4-STORE hypothesis. AUTHORS describes code LGPLv3, not a fixture-specific grant; source text's mere presence is not an authorship/license attestation.[5] |
| U4-LZ | unarr `lipsum_rar4_default.rar`; history “Add more integration tests”.[15] | R4-LZ hypothesis only; default filename does not establish the actual stream method or rights. |
| U4-PPM | unarr `lipsum_rar4_ppmd.rar`; CMake explicitly registers a text-compression integration test; history names rar4 ppmd/delta/wav tests.[6][7] | R4-PPM lead stronger than an unexplained filename, still not a measured PPM stream, writer version or member-rights grant. |
| DRF-OLD | Debian `test/files/rar3-old.rar`, `.r00`, `.r01`; new ISC package coverage and `.exp` metadata records `meth=0`, split flag and two member names.[8][16] | R4-OLDVOL lead now has stored-method evidence **as an upstream expected dump**, beyond B01-F's naming-only lead. Not native proof; exact writer/version remains unknown. |
| DRF-SOLID | Debian `test/files/rar5-solid.rar`; `.exp` has `cmp_meth=3` and second member `solid=True`.[10] | R5-LZ-SOLID lead; complete bytes, genuine member rights and fork-native solid/LZ behavior unverified. |
| DRF-VOL | Debian `test/files/rar5-vols.part1.rar` through `part3`; `.exp` records `cmp_meth=0`, split flag and members spanning through `vol=2`.[11] | R5-VOL stored lead, not assumption from names. Full part order and native missing-volume/entrypoint outcomes still needed. |

Unarr's pinned tree is complete and has source payload paths, but they were not
fetched because member payload acquisition is outside scope.[4] Its AUTHORS
explicitly frames licensing around code.[5] No fixture-specific grant or exact
writer build was found in the inspected AUTHORS/CMake/current-path histories.
This bounded negative result does not reject all unarr assets or establish that
such records do not exist elsewhere.

Debian unrar-free's manifest supplies a GPL-2+ package declaration.[17] Its
versioned top-level listing has no tests directory,[23] and the attempted `tests/`
API returns literal `{"error":404}` (structured negative in JSON, not a license
finding). The screen stopped there; nested packaging paths were not exhaustively
searched. No corpus-completeness or absence-everywhere claim follows, and no
unrar-free execution/encoder recommendation is made.

**No fixture-specific grant for complete container and member material was
established in this bounded retrieval.** The useful positive finding is two
explicit distribution path-coverage declarations plus contributor/history
corroboration, not merely software root licenses. This supports a concrete
risk/evidence review under O1 or precise questions under O2. It does not justify
silently changing the prior `import_review_candidates=[]` decisions.

## Original eight B01-W IDs and remaining coverage

Mapping is intended coverage, not byte-equivalent replacement for B01-W's exact
ALL-member generation recipe. Any substitution must retain the case's intent
and explicitly revise recipe-specific acceptance through review/human decision.

| B01-W ID | Newly assessed lead | Current outcome |
| --- | --- | --- |
| R4-STORE | DLA-BASIC, U4-STORE | unqualified; hypotheses / expected test context only |
| R4-LZ | U4-LZ | unqualified; filename-based method hypothesis |
| R4-PPM | U4-PPM | unqualified; declared integration intent, not native decoding |
| R4-VOL | none matching stored/non-solid part-number contract | unqualified; DLA-MULTI only covers a different intended multipart behavior |
| R4-OLDVOL | DRF-OLD | unqualified; upstream expected metadata suggests store |
| R5-STORE | none newly assessed | unqualified; B01-F J5-STORE remains an unresolved prior lead |
| R5-LZ-SOLID | DRF-SOLID | unqualified; upstream expected dump, not measured |
| R5-VOL | DRF-VOL | unqualified; upstream expected dump, not measured |

O1 could enable replay-based qualification work, not automatically qualify even
one row. O2 donations could target all rows, but availability is a hypothesis.
O3 closes none of them. No stored-header synthesis substitutes for compressed,
encrypted, solid or real multipart evidence; no RAR compressor is commissioned.

Beyond these eight, keep B01-W's explicit obligations: Rar1/Rar2; Rar3 PPM/LZ
transitions and filters; classic compressed solid/multipart; levels/dictionaries;
RAR-specific unsupported and damaged compressed streams; encryption/password
callbacks (B05); Unicode/fork code pages (B02); metadata/links/permissions/large
files (B03/B04); recovery/SFX; nested/probing chains; external 7z/CAB/ISO/WIM and
other inventory rows; list/create numeric results and operation identity;
FFI ownership (B08), GUI/desktop qualification. These are not all RAR-license
problems. B01's unreviewed inventory says 8 covered/53 unqualified across 61 CLI
capability rows; this is not 61 library registration slots (Q1 distinguishes the
coordinator-added Hash entry). No partial implementation is promoted to PASS.

## O1: explicit two-track evidence decision and finite pilot

Proposed human decision: approve `acquired-immutable` replay qualification with
honest unknown historical writer metadata, while retaining actual reader identity,
rights review, exact input hashes, measured coverage and all other B01 gates.
Approve **review of** the three DRF families first; import permission is a separate
checkpoint after the exact rights/evidence assessment, not implied by O1's policy.
The decision must explicitly amend M1/B01's actual generator/version requirement
for that evidence class and B01-W recipe equivalence where applicable. A reviewer
PASS of this memo cannot do that. Keep `generated-reproducible` discipline intact.

Concrete sequence after approvals:

1. On original B01, record the policy delta and exact allowed fixture scope. Review
   Debian ISC coverage, contributor trace, all exceptions/notices and the remaining
   member/container applicability question. If the human requires a direct
   rights-holder statement, stop this pilot and use O2; do not call missing rights
   a harmless missing generator field.
2. After actual acquisition/import authorization, tester quarantines only the
   selected versioned sets, computes every volume/archive/member SHA-256, complete
   names/metadata inventory and decompression budgets. Confirm expected data/flags
   against actual bytes; discrepancies go to review, not fabricated provenance.
3. Extend/freeze new legacy native captures additively: Windows MSVC x64, Linux
   GCC x64, macOS Apple clang arm64; list/test/extract, create refusal, probing,
   missing-volume positions/entrypoints, supported corruption controls, raw plus
   actual numeric errors at available levels. Preserve original M1/B01 goldens.
4. Validate drift detection for one changed archive byte, volume order/membership,
   member hash, raw result, HRESULT/NOperationResult/CArcErrorInfo and evidence-class
   binding. Unchanged controls must pass. Review any remaining list/create numeric
   instrumentation rather than infer numbers from CLI text. Independently review
   the pilot; the rest of B01 stays open.

Planning estimate, not measured: 1–2 engineer-days for policy/rights assessment;
3–5 engineer-days for the small pilot and native additive capture if existing
harnesses are reusable. CI availability and rights response may extend elapsed
calendar time. Stop at the three named families; stop on unresolved rights,
resource violation, byte/source mismatch or legacy/expected disagreement. Do not
start another general search when a stop is reached. Cost cap is zero new fees;
no promise about existing CI quotas or free human labor.

## O2: exact inquiry and donation manifest — NOT SENT

Proposed audience: rarfile maintainers/contributors for DRF first; optionally
libarchive maintainers for DLA-BASIC if the first answer is insufficient and the
operator expressly includes that second recipient. No invented private address,
attachment, public issue, email or message has been sent.

> Subject: Clarify test-data rights for pinned RAR interoperability fixtures
>
> We are considering only the exact DRF-OLD, DRF-SOLID and DRF-VOL paths listed
> in this report, as distributed in Debian python-rarfile 4.5-1, with upstream
> history context at d2f7df6fc843dae356fd6b0a85971dc36fd6e757. We have not imported
> them. Debian declares ISC coverage under Files: * and attributes Marko Kreen.
> Does the applicable grant cover these archive containers, every embedded member,
> filenames and other member metadata for redistribution in another project's
> test corpus/CI, including modified test derivatives? What notices/exceptions
> must be retained, and what is the source of your authority for this confirmation?
>
> Please identify original member sources/authors, any borrowed material, and
> whether the distributed bytes match the referenced upstream revision. Can an
> upstream commit bind that statement to the exact paths and archive/part hashes?
> Which actual writer/version/options are known from records? Unknown is useful:
> please do not infer writer versions from decoder/header versions or timestamps.
> We do not require you to recover an old executable hash merely to answer rights
> questions; our replay-policy proposal is not yet approved.
>
> If rights cannot be confirmed, would you voluntarily contribute an already-held,
> redistributable minimal replacement corpus with an explicit grant and complete
> source/member manifest? We are not asking you to buy/install/run proprietary
> software, obtain commercial authorization on our behalf, disclose keys, or
> submit private archives. No payment or execution is commissioned. Fresh
> generation would require a separately established route consistent with our
> no-commercial-authorization/no-extra-fees constraint; none is established now.
>
> Partial confirmation will remain partial. Please identify any uncertainty rather
> than extending a software license to unidentified embedded content by assumption.

Draft donation record (all fields required as records, unknowns explicitly null
with reason; **not an accepted fixture schema or an actual license grant**):

- `schema_version=1`, `donation_id`, public contribution commit and approval record;
  public author/rights-holder attribution without personal contact details or keys.
- `files[]`: exact archive/part paths, byte lengths, full SHA-256, ordered volume
  membership, immutable retrieval URL; no writer binary or SFX executable bundled.
- `members[]`: complete source path/revision or original recipe, author, rights
  holder, license text/identifier and notice path; names/link targets/metadata,
  byte length/full digest, classification of any incorporated third-party material.
- `grant`: explicit scope for container contribution and all members/metadata to
  the extent rights exist, source/binary redistribution and permitted derivatives,
  CI/public corpus distribution, grantor authority, exceptions and obligations.
  CC0-1.0 for wholly original data is an option, not a dedication we may invent;
  an applicable existing permissive grant may suffice after review.
- `generation`: actual known writer/product/version/build/package/executable hashes,
  argv/source recipe/logs where available; `unknown_reason` for missing history.
  Record rights evidence separately; never demand keys or treat a donor's writer
  statement as an operator execution authorization.
- `coverage_intent`: original B01-W IDs, intended method/solid/volume/encryption
  observations and resource limits; `native_reports=[]`, `qualified=false` until
  our own authorized native capture. Public synthetic passwords only if separately
  scoped/approved; no secrets.

Proposed bound: one approved message, at most one clarification, two named
recipients maximum, a 14-calendar-day response window. Estimate 0.5–1 engineer-day
for preparation/review; outside response timing is unknown. Stop after that window,
unclear grantor authority, commercial-execution request or incompatible terms;
record the result and choose O1 with adequate rights evidence or O3, not an
automatic inquiry/search loop. Receiving bytes is not import authorization.

## O3: proposed dependency/qualification partition, no graph change

The current graph is **operation/card-wide**, not format-scoped: B01 directly
blocks B05, S2a, S3 and S5; S2a also requires B02/B03/B05/B06, and public S3
exposure waits for B08. Thus simply saying “RAR stays off” cannot release those
cards. The earlier operator expressly chose full B01 acceptance; O3 is a new,
explicit scope/sequence decision that may not be inferred from “research”.

| Stage / lane | Current permission and proposed partition |
| --- | --- |
| Q1/S1 | Pure pins/contracts and workspace/domain work do not depend on B01 in the reviewed DAG. May proceed only with their existing own reviewed prerequisites; this memo does not assert their live completion. |
| B03/B04; B06 after B04; B02 | Existing independent eligible characterization continues under its own gates. No edges or acceptance touched, no competing edits here. |
| B05 | Currently waits for B01. Proposal could separate a qualified 7z/ZIP callback subset from RAR password cases; still needs native empty/undefined/cancel semantics. Cannot simply delete B01 dependency or mark all B05 PASS. |
| S2a | Currently blocked by full relevant parents. A reviewed bounded non-product facade pilot could use approved non-RAR open/list corpus plus qualified stream/password/cancel evidence. Requires explicit scope and new dependency representation; unreviewed B01 observer cannot be integrated as a shortcut. |
| B08 / S3 | B08 must test an actual reviewed bridge. Only then may a qualified **allowlisted** non-RAR listing surface be proposed. Opening/probing must fail closed before dispatch for unqualified RAR, including renamed files and nested layers; extension filtering is insufficient. Gate enforcement itself requires tests. |
| S4 / S5 / S6 | No automatic release. Respect S3 -> extraction -> test -> creation order and B02–B06/B08. A selected 7z/ZIP surface could later advance after native path/overwrite/metadata/password/cancel/error qualification. RAR read/test remains closed and RAR creation must preserve retained refusal, never add a writer. |
| S7 / S8 | General task and filesystem work still follows the CLI spine and relevant native coverage. No jumping ahead because one format is deferred. |
| Q2 / B07 / S9–S11 | Qt/QML and desktop remain after eligible CLI/filesystem qualification and native GUI/settings prerequisites. No GUI substitution or early Qt migration authorized. |
| Q3 / S12 | Full selected release qualification, package/legal/signing scope and human gates remain. A narrower opt-in preview cannot claim full parity or replace the existing product by default. No release publication. |

Architectural direction remains Qt 6/QML -> CXX-Qt -> Rust -> mature C/C++.
Qualification topology and promised **new-surface** coverage would change, not the
engine or codec architecture. Legacy formats remain available in the existing
executable; new application format selection must be explicit before work starts.
“Fallback” means a preselected, documented legacy route, **not** catching a partial
extract/update error and running the legacy command again. No double writes,
automatic retry, legacy uninstall, silent capability loss or codec removal.

Proposed next action: orchestrator/architect submit a separate bounded partition
spec with operation-format-platform allowlist, which exact prerequisites remain,
unchanged legacy route, gate-enforcement tests and review ownership. Do not archive
B01 or an unreviewed parent to satisfy dependencies. Estimate 1–2 engineer-days for
spec/DAG review, then implementation effort remains unknown. Stop if the requested
preview cannot enforce exclusion before probing/writing, or the operator needs
full replacement parity now: keep the existing graph and choose corpus work.

## Reproduction, limitations and review handoff

Only this Markdown and its JSON are deliverables. No production/native archive
build is applicable: no runtime edits or authorized archive acquisition occurred;
compilation cannot prove rights and native reader execution would exceed scope.
All runtime commands above are future obligations, not execution claims.

Research used bounded text/metadata HTTPS GETs with 40-second timeouts and no
upstream execution. The JSON carries each successfully used source URL, literal
quotes, snapshot digest and pin type. Git revision URLs bind source objects;
Debian version URLs bind the declared distribution version, not an acquired
archive digest. API envelopes can vary; validation compares decoded values and
whitespace-normalized quotes, not JSON formatting. The Debian specification text
snapshot is normalized HTML text; its digest is not a raw HTML digest.

Reproduce source/schema/matrix/path checks without scratch by saving the single
Python block below as a new temporary checker and running it from repository root.
It GETs only the allowlisted text/metadata sources from the matrix, never fixtures.
Snapshot hashes record this research; byte equality is checked locally during
author validation, not demanded for changing server serialization. Validation of
links/quotes is not legal analysis or independent review of the reasoning.
The matrix separates exact `retrieval_url` (including directory trailing slashes)
from citation-ledger canonical `url`. Debian's negative directory API responds
with JSON at the slash-terminated URL but HTTP 404 without that slash.

```python
import json, pathlib, re, urllib.request, urllib.parse
from html.parser import HTMLParser
q = pathlib.Path('docs/ai-migration/qualification')
m = json.loads((q / 'b01-resolution-options.json').read_text())
doc = (q / 'b01-resolution-options.md').read_text()
assert m['schema_version'] == 1 and not m['complete_solution_now']
assert set(m['options']) == {'O1', 'O2', 'O3'}
assert len(m['scope']['research_units']) == 4 and len(m['candidates']) == 8
cases = ['R4-STORE', 'R4-LZ', 'R4-PPM', 'R4-VOL', 'R4-OLDVOL',
         'R5-STORE', 'R5-LZ-SOLID', 'R5-VOL']
assert list(m['case_mapping']) == cases
assert not m['imports_authorized'] and not m['native_results_produced']
cache = {}
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts = []
    def handle_data(self, data): self.parts.append(data)
for s in m['sources']:
    url = s['retrieval_url']; u = urllib.parse.urlparse(url)
    print('Checking source', s['id'], url, flush=True)
    assert u.scheme == 'https'
    assert u.netloc in {'api.github.com', 'raw.githubusercontent.com',
                       'sources.debian.org', 'www.debian.org'}
    # No encoded or binary fixture, payload member or patch retrieval.
    assert not u.path.endswith(('.rar', '.r00', '.r01', '.uu', '.zip', '.7z', '.wav'))
    if u.netloc == 'api.github.com':
        assert '/git/trees/' in u.path or '/git/commits/' in u.path or u.path.endswith('/commits')
        if u.path.endswith('/commits'):
            assert re.fullmatch('[0-9a-f]{40}', urllib.parse.parse_qs(u.query)['sha'][0])
    if u.netloc == 'raw.githubusercontent.com':
        assert re.search(r'/[0-9a-f]{40}/', u.path)
        assert u.path.endswith(('AUTHORS', 'CMakeLists.txt'))
    with urllib.request.urlopen(url, timeout=40) as r:
        assert not r.headers.get('Link')
        text = r.read().decode('utf-8')
    if s['kind'] == 'html_text':
        p = Text(); p.feed(text); text = ' '.join(p.parts)
    elif s['kind'] == 'history':
        text = '\n'.join(x['commit']['message'] for x in json.loads(text))
    elif s['kind'] == 'tree':
        data = json.loads(text)
        if 'truncated' in data: assert data['truncated'] is False
        text = json.dumps(data, indent=2, ensure_ascii=False)
    elif s['kind'] == 'structured_negative':
        assert json.loads(text) == {'error': 404}
    for quote in s['quotes']:
        assert ' '.join(quote.split()) in ' '.join(text.split()), (s['id'], quote)
    cache[s['id']] = text
assert json.loads(cache[24])['sha'] == '3307cd3fdcffe3b98326872c601bbf7235386441'
assert json.loads(cache[24])['tree']['sha'] == json.loads(cache[4])['sha']
for cid, c in m['candidates'].items():
    assert cid in doc and c['qualified'] is False and c['import_approved'] is False
    assert c['archive_sha256'] is None and c['writer_version'] is None
    assert set(c['proposed_case_ids']) <= set(cases)
    for obj in c['objects']:
        data = json.loads(cache[obj['metadata_source']])
        if obj['kind'] == 'git-blob-sha1':
            entry = next(e for e in data['tree'] if e['path'] == obj['path'])
            assert entry['sha'] == obj['value'] and entry['size'] == obj['size']
        else:
            entry = next(e for e in data['content'] if e['name'] == pathlib.PurePosixPath(obj['path']).name)
            assert entry['stat']['size'] == obj['size'] and obj['value'] is None
for case, row in m['case_mapping'].items():
    assert '| ' + case + ' |' in doc and row['qualified'] is False
    assert row['candidate_ids'] == [k for k,v in m['candidates'].items()
                                    if case in v['proposed_case_ids']]
for oid, o in m['options'].items():
    assert o['rank'] in {1,2,3} and o['incremental_product_fees'] == 0
    assert o['approved'] is False and set(o['coverage_by_case']) == set(cases)
    for key in ['verified_facts','hypotheses','proposed_policy_changes','effort',
                'risks','human_decision_needed','next_action','stop_condition']:
        assert o[key]
    assert all(v['qualified_now'] is False for v in o['coverage_by_case'].values())
for target in re.findall(r'\]\(([^)]+)\)', doc):
    if '://' not in target:
        assert (q / target.split('#')[0]).is_file(), target
source_section = doc.split('\n## Sources\n', 1)[1]
rendered = {int(n): url for n,url in re.findall(r'^\[(\d+)\] (https://\S+)', source_section, re.M)}
prose = re.sub(r'```.*?```', '', doc.split('\n## Sources\n',1)[0], flags=re.S)
cited = {int(n) for n in re.findall(r'\[(\d+)\]', prose)}
assert set(rendered) == cited
assert all(rendered[s['id']] == s['url'] for s in m['sources'] if s['id'] in cited)
print('PASS: source GETs/quotes, schema, 4 units, 8 families, 8 case IDs, 3 options, local links; no archive acquisition/native qualification')
```

Actual final source/schema/matrix checker returned PASS for 23 source records,
four research units, eight families, 15 metadata objects, eight original case IDs
and three options. The unchanged offline DAG validator passed its 29-child,
104-edge checks and three negative controls. Citation evidence validation passed;
uncited discovery/structured metadata entries are intentional, and no automated
prose-coverage certification is claimed. No native compatibility result follows.
Exact final commands, snapshot/preservation checks and commit are recorded on the
review transition. Research
scratch `.b01-resolution/` contains only this task's fetched public text/metadata,
read-only local context and authored checkers. It is not a durable prerequisite.
Initial guessed unarr tree/ref and Debian version/README URLs returned HTTP 404;
repo commit/package API discovery supplied valid pins. One Debian directory GET
returned HTTP 503; the later exact versioned files directory GET succeeded. An
initial route-equality check failed because this card has an extra subscription;
checking that every complete parent tuple is inherited passed, without printing
routing identities or changing subscriptions. One draft evidence quote incorrectly
reused another unarr commit's title; literal matching rejected it and the actual
“Add more integration tests” title was used. The first reproduction checker used
the ledger-normalized negative-directory URL and failed; preserving the original
trailing slash fixed retrieval. A later citation-set check mistook Python array
indexes inside the checker block for citations; excluding fenced code fixed the
checker, without changing evidence or citation IDs. No source fact or golden was
altered.

Independent reviewer must cold-read both artifacts, recheck source meanings and
policy ancestry, all eight case mappings, rights versus replay distinction,
non-RAR residual work, and the current B01 comments/gates. Commit before same-card
`reviewer` handoff. PASS may complete **only this report**, then reviewer posts the
reviewed commit/paths/options to B01 and reads back that comment. The author does
not label this draft a reviewed handoff. CHANGES returns this card; two substantive
failures require an actual `needs_input` block with evidence/options/impacts.
No B01 unblock/archive/import, shared-branch merge or release is authorized.

## Sources

[1] https://www.debian.org/doc/packaging-manuals/copyright-format/1.0
[3] https://sources.debian.org/data/main/liba/libarchive/3.8.9-1/debian/copyright
[4] https://api.github.com/repos/selmf/unarr/git/trees/61c07dab16fdf88c42694c512505564adca49d4e?recursive=1
[5] https://raw.githubusercontent.com/selmf/unarr/3307cd3fdcffe3b98326872c601bbf7235386441/AUTHORS
[6] https://raw.githubusercontent.com/selmf/unarr/3307cd3fdcffe3b98326872c601bbf7235386441/test/CMakeLists.txt
[7] https://api.github.com/repos/selmf/unarr/commits?sha=3307cd3fdcffe3b98326872c601bbf7235386441&path=test%2Fcorpus%2Fintegration%2Flipsum_rar4_ppmd.rar&per_page=100
[8] https://sources.debian.org/data/main/p/python-rarfile/4.5-1/debian/copyright
[9] https://api.github.com/repos/markokr/rarfile/git/trees/d2f7df6fc843dae356fd6b0a85971dc36fd6e757?recursive=1
[10] https://sources.debian.org/data/main/p/python-rarfile/4.5-1/test/files/rar5-solid.rar.exp
[11] https://sources.debian.org/data/main/p/python-rarfile/4.5-1/test/files/rar5-vols.part1.rar.exp
[12] https://sources.debian.org/data/main/liba/libarchive/3.8.9-1/libarchive/test/test_read_format_rar.c
[14] https://api.github.com/repos/selmf/unarr/commits?sha=3307cd3fdcffe3b98326872c601bbf7235386441&path=test%2Fcorpus%2Fintegration%2Flipsum_rar4_store.rar&per_page=100
[15] https://api.github.com/repos/selmf/unarr/commits?sha=3307cd3fdcffe3b98326872c601bbf7235386441&path=test%2Fcorpus%2Fintegration%2Flipsum_rar4_default.rar&per_page=100
[16] https://sources.debian.org/data/main/p/python-rarfile/4.5-1/test/files/rar3-old.rar.exp
[17] https://sources.debian.org/data/main/u/unrar-free/1%3A0.3.3-1/debian/copyright
[20] https://api.github.com/repos/markokr/rarfile/commits?sha=d2f7df6fc843dae356fd6b0a85971dc36fd6e757&path=test%2Ffiles%2Frar5-solid.rar&per_page=100
[21] https://api.github.com/repos/markokr/rarfile/commits?sha=d2f7df6fc843dae356fd6b0a85971dc36fd6e757&path=test%2Ffiles%2Frar5-vols.part1.rar&per_page=100
[22] https://api.github.com/repos/markokr/rarfile/commits?sha=d2f7df6fc843dae356fd6b0a85971dc36fd6e757&path=test%2Ffiles%2Frar3-old.rar&per_page=100
[23] https://sources.debian.org/api/src/unrar-free/1%3A0.3.3-1
[24] https://api.github.com/repos/selmf/unarr/git/commits/3307cd3fdcffe3b98326872c601bbf7235386441
