# B01-F: bounded existing RAR fixture assessment

Task `t_c46854b9`; branch `wt/t_c46854b9`; research date 2026-09-11 UTC.
Status: **assessment for independent review; no import-review candidate established**.

## Decision and scope

The operator approved option 1: assess free existing fixtures read-only, rather
than acquiring a writer or generating new archives. This authorizes neither
import nor extraction, writer execution, upstream correspondence, proprietary
terms, spending, a qualification waiver, nor release. Original B01 `t_22299c6f`
retains its existing `needs_input` gate and `triage` state; this card does not
change it. Notify+wake is not approval.

The result is bounded: **three public projects screened, five candidate archive
sets assessed, zero evidence-complete import-review candidates**. This is not a
claim that no suitable fixture exists elsewhere, nor that redistribution of the
inspected fixtures is prohibited. The strongest new leads are junrar's documented
RAR5 store, solid and stored-volume sets: its committed recipes explicitly name
`rar 7.23`, instead of leaving the writer/version entirely unknown.[8][9]
Exact container and payload grants remain unestablished in the material inspected;
this is an evidence gap, not a legal conclusion. Do not resolve it by assuming
trivial payloads are public domain or software licenses automatically cover them.

Consumed reviewed [B01-P](b01-provenance.md), [B01-W](b01-writer-plan.md), and
[B01-L](b01-writer-license-decision.md). Parent
`daa88ed034ea46f6940932580339ad95c98dbcc2` and its B01-P/W ancestors are already
in starting HEAD `158fef1bfde44303dfa3d0033cac51cd95c8aa81`; no merge required.
Source branch and both `AGENTS.md` files were verified before research. No
unreviewed B01 implementation was integrated. The five old libarchive files were
not fetched or re-audited. B01-L's exclusion of proprietary writer execution and
B01-W's unchanged compatibility obligations continue to apply.

## Discovery boundary and source identities

Discovery used direct public GitHub tree metadata for these three projects,
chosen as reader-test repositories; no general-web expansion, clone, archive blob,
encoded fixture, member payload file, or archive diff was downloaded. License,
README, test source, committed generator source and commit-list JSON are research
text only; none of the upstream code was executed. Tree discovery initially used
`master`, then immediately froze the returned commit and all text retrievals to
that revision. All three responses reported `truncated: false`.[1][5][10]

| Project | Pinned commit | Reason to examine / bounded disposition |
| --- | --- | --- |
| `markokr/rarfile` | `d2f7df6fc843dae356fd6b0a85971dc36fd6e757` | Old-volume path family available; software README advertises multivolume support, not a writer record.[1][3] |
| `junrar/junrar` | `1d10acccc6505c756f6df4fca1925fd53a591df9` | Separate RAR5 fixture READMEs describe generation and payload recipes; strongest provenance lead.[5][8][9] |
| `adamhathcock/sharpcompress` | `e04d51176c5d87668c4c8779825342230c33aa74` | Named `Rar.none.rar` test input and associated read tests; method/name alone is not provenance.[10][15] |

The [JSON matrix](b01-existing-fixture-assessment.json) is authoritative for full
paths, every volume's `git-blob-sha1`, URLs, literal evidence, null unknowns and
per-candidate missing evidence. These are upstream-reported Git object identities,
**not SHA-256 measurements of archive or payload bytes**. No such SHA-256 is claimed.
A Git tree binds paths and objects, not licensing or actual writer identity.

### Exact candidate objects

Paths are upstream-relative. No listed path is a local imported fixture.

| Candidate | Path | Git blob SHA-1 |
| --- | --- | --- |
| J5-STORE | `src/test/resources/com/github/junrar/rar5unpack/m0-plain-128k.rar` | `8675d36f53fc2c68288ea41d3893c091998aabae` |
| J5-SOLID | `src/test/resources/com/github/junrar/rar5unpack/m3-solid-128k.rar` | `abe4f99044f4d1b5743962974f473965147be52b` |
| J5-STORED-VOLUMES | `src/test/resources/com/github/junrar/volumes/rar5-part/stored.part1.rar` | `e0923d70bf93e2733d2c31ade94dee0faeaa91fc` |
| J5-STORED-VOLUMES | `src/test/resources/com/github/junrar/volumes/rar5-part/stored.part2.rar` | `561c2afbd1761711d5368c58c4d5a495849edccd` |
| J5-STORED-VOLUMES | `src/test/resources/com/github/junrar/volumes/rar5-part/stored.part3.rar` | `f932e24c5cae2b9e9750b8bf5c62075a478199d4` |
| RF-OLD-VOLUMES | `test/files/rar3-old.rar` | `962d8b6f4b9d7e60396c1b5366f8962868c71fe1` |
| RF-OLD-VOLUMES | `test/files/rar3-old.r00` | `0ba628367eaae36c92a648217e9baf96125c2acb` |
| RF-OLD-VOLUMES | `test/files/rar3-old.r01` | `9bc19dde8cb2e46d3e064b83074c7fc4e7e5c3da` |
| SC-NONE | `tests/TestArchives/Archives/Rar.none.rar` | `42c859b91f3c8a358972abd44b26ec8682a54bf8` |

Object evidence is the three complete pinned trees.[1][5][10]

## Assessment matrix and exact unresolved evidence

All five rows are `evidence_incomplete`. `writer` and `writer_version` in JSON
reflect a committed upstream declaration when present, not a locally measured
executable. Unestablished container/payload grants are null; `license_context`
retains the actual software notice separately rather than silently discarding it.

| Candidate | Generation/payload record actually found | Exact blockers before import review |
| --- | --- | --- |
| J5-STORE | Upstream declares `rar 7.23`, `-ma5 -m0 -md128k -ep`, `small.bin`, and describes `"The quick brown fox. " * 400`.[8] | Explicit archive-container and complete payload/member-metadata redistribution applicability and grantor authority; source-to-member binding and actual build/log evidence. Deterministic-looking text is not a license. |
| J5-SOLID | Same declared writer, `-ma5 -m3 -md128k -ep -s`, `s0..s4.bin`; README specifies block/pool sizes and seeds 100..104.[8] | Same rights/build binding gaps; complete pool/block-generation algorithm not established by these dimensions/seeds alone. No content equality or solid/LZ decoding measured here. |
| J5-STORED-VOLUMES | README declares `rar 7.23`, names all three `stored.partN.rar` files and `-ma5 -m0 -ep -v50k -qo-`; committed generator calls `write("payload/stored2.bin", 39103, 120_000)`.[9][13] | Same container/payload rights and exact writer-build/log binding gaps. Generator availability improves provenance but grants no inferred dedication to generated bytes; complete actual member metadata remains unverified. |
| RF-OLD-VOLUMES | Exact `.rar/.r00/.r01` objects available; separate histories each return `6ab3317c6a02c4f1082ab8570a34d4868c7baa3c`, message “New test files for rar5” / “Move away from shell scripts to tox+nose”.[18][19][20] | Writer/product/version/commands are unknown. Commit wording does not make these files RAR5. Complete payload origin, container/payload grant applicability and required notices not established; old-name family alone does not prove B01-W stored/non-solid or native volume behavior. |
| SC-NONE | Named read test `Rar_None_ArchiveStreamRead` calls `ArchiveStreamRead("Rar.none.rar")`; inspected current-path history returns a folder-move commit, not generation evidence.[15][21] | Actual writer/version/recipe and complete payload rights/origin unknown; `none` test name does not independently establish stored classic RAR. MIT software context is not an exact embedded-content rights attestation. |

Junrar's root `LICENSE` is explicitly framed around UnRAR source use, including
its compression-recreation restriction; it is not an explicit grant naming these
new archives or the synthetic payloads.[6] Rarfile's ISC notice allows copying and
distribution of “this software” with notices; SharpCompress's MIT notice similarly
requires retaining copyright and permission text.[2][11] These are meaningful
existing obligations, not evidence that every archive contribution and member
came from the named software author. No trial-created-output entitlement,
royalty-free-output grant or new license is inferred. No proprietary product
needs to be run merely to assess already-existing bytes.

### History depth and rejected leads

The two junrar README histories were read as commit metadata: unpack history
includes `5abb2d8cb5e0e02adde407e9fc18ab3e695f0a49`; volume history includes
`3308906401f1f254af3e8426987cc6b127f2e829`,
`434de0ec8eb5fc87ebf4ee8a51c609780c429b2a`, and
`62170ff7e9501b89e52b4357a3a4581abf949a94`.[16][17]
These corroborate development context, not a signed authoring/rights manifest.
No claim of first-ever introduction is made: this card did not prove parent-tree
absence, follow file renames, or audit all historical copies. Current-path
histories are explicitly not exhaustive original-creation histories.

The generic junrar `generate-testdata.sh` calls `rar` with variable input/output
and `-mc` parameters; it supplies no writer version or binding to the five chosen
sets, so it was rejected as a substitute for per-fixture generation records.[7]
Other discovered junrar encrypted, hostile/byte-patched and filter families were
not deep-assessed: they would add separate rights/behavior obligations rather
than resolve these rows. The volume README explicitly distinguishes stored from
its `nochecksum` derivative and runtime version-70 promotion; neither derivative
is substituted for the chosen stored set.[9] Other rarfile/SharpCompress paths
were discovery-only, not additional assessed archive sets. No fourth project or
sixth set was pursued once these precise gaps were recorded.

## B01-W mapping: intended leads, no native coverage

Keep the original eight IDs. Mapping means a lead to investigate after evidence
clearance, not a byte-equivalent replacement for B01-W's proposed synthetic
campaign, not confirmed format/method support, and not a reduction in acceptance.

| B01-W case ID | Candidate lead | Qualification |
| --- | --- | --- |
| R4-STORE | SC-NONE (test-name hypothesis only) | unqualified |
| R4-LZ | none assessed | unqualified |
| R4-PPM | none assessed | unqualified |
| R4-VOL | none assessed | unqualified |
| R4-OLDVOL | RF-OLD-VOLUMES (naming hypothesis only; stored/non-solid not established) | unqualified |
| R5-STORE | J5-STORE (declared recipe) | unqualified |
| R5-LZ-SOLID | J5-SOLID (declared recipe; actual LZ stream not measured) | unqualified |
| R5-VOL | J5-STORED-VOLUMES (declared stored recipe) | unqualified |

Junrar describes `unrar 7.23` oracle hashes and typed negative-volume outcomes
in its README.[8][9] Those are **upstream claims**, not native measured evidence
for this fork or this card. No expected exception, HRESULT, NOperationResult,
CRC/hash, missing-volume behavior or CLI exit is imported as a golden. No unpack
version, filename, commit timestamp or reader version is used as a writer version.

After an actual rights/import decision, original B01 still owns acquisition,
immutable archive and every-volume/member SHA-256, complete member inventories,
resource review, unchanged native Windows/Linux/macOS legacy list/test/extract,
create refusal, numeric/raw error captures, repeats, negative controls and
independent review. Stored-volume sizes, member order and old-volume semantics
must be measured; they cannot be assumed from this metadata. B01-W's additional
Rar1/Rar2, method/filter transitions, encryption/password, Unicode/code pages,
filesystem metadata, large-file, nested/probing, unsupported-method, other-format,
GUI and desktop gaps remain. Qt 6/QML -> CXX-Qt -> Rust -> mature C/C++ is unchanged.

## Stop condition and reviewed handoff

`import_review_candidates` is empty because exact container/payload rights are
unresolved for every set; writer/version is additionally unknown for the two
non-junrar sets. These legal/provenance gaps are distinct from intentionally
unperformed byte acquisition and native qualification. Finding insufficient
evidence completes this bounded assessment, not B01 or its human gate.

Reviewer PASS may complete only this assessment and must then post its reviewed
commit/artifact paths and exact gaps on `t_22299c6f`, reading the comment back.
Do not unblock/archive B01, import fixtures, contact upstream, acquire/run writers,
or spawn another automatic audit. CHANGES returns this same card; two substantive
failures require a typed `needs_input` escalation with evidence and options.

For a later operator decision on original B01 (not executed here):

1. Recommended: defer affected RAR qualification until the operator supplies
   existing verifiable fixture-specific rights and generation records, prioritizing
   the three junrar leads. Zero cost, preserves all acceptance; timing unresolved.
2. Separately authorize a narrowly scoped upstream rights/provenance inquiry.
   Zero product fees but external correspondence and uncertain response; not
   authorized by the current assessment decision and not sent here.
3. Request a human-reviewed explicit scope-adjustment proposal. Potential narrower
   delivery, not parity; no acceptance/DAG change or production release now.

## Reproduction and verification

Only this Markdown and its sibling JSON are deliverables. Research scratch is
`.b01-fixture-research/` in the isolated worktree and is uncommitted. It contains
public text/metadata and author-written fetch/check scripts, not a fixture corpus.
JSON `evidence_sources` records actual retrieval URLs and scratch names; those
names are reproducibility hints, not durable evidence dependencies. Raw checkout,
session metadata and secrets are not published.

Actual retrieval commands: `python3 .b01-fixture-research/fetch.py` and
`python3 .b01-fixture-research/fetch_more.py` used stdlib read-only HTTPS GETs on
allowlisted text and history paths; initial tree GETs used
`curl -fLsS --max-time 40 https://api.github.com/repos/<owner>/<repo>/git/trees/master?recursive=1 -o <scratch-tree.json>`.
Each URL is reproducible from the JSON. The initial tree-filter `jq` expression
had a syntax error; correcting its parentheses yielded the tree path list, without
changing source data or security policy. No upstream text was evaluated as code.

Executable builds and native archive tests are not applicable to a documentation-only
assessment and are explicitly outside authorization: no runtime edit or permitted
archive acquisition occurred. A build would not validate rights; running a reader
would violate this card's no-extraction boundary. All compatibility remains
unqualified, regardless of documentation-check success.

The following author-written checker is reproducible without retaining scratch:
save this block as `.b01-fixture-research/verify.py` and run
`python3 .b01-fixture-research/verify.py` from the worktree. It only GETs committed
text and GitHub tree/history JSON, never archive payloads or raw archive diffs.

```python
import json, pathlib, re, urllib.request, urllib.parse
root = pathlib.Path('docs/ai-migration/qualification')
md = (root / 'b01-existing-fixture-assessment.md').read_text()
m = json.loads((root / 'b01-existing-fixture-assessment.json').read_text())
assert m['schema_version'] == 1 and m['import_review_candidates'] == []
assert len(m['scope']['projects_inspected']) == 3 and len(m['candidates']) == 5
assert len({c['id'] for c in m['candidates']}) == 5
assert sum(len(c['blob_ids']) for c in m['candidates']) == 9
cases = ['R4-STORE', 'R4-LZ', 'R4-PPM', 'R4-VOL', 'R4-OLDVOL',
         'R5-STORE', 'R5-LZ-SOLID', 'R5-VOL']
assert [r['case_id'] for r in m['case_mapping']] == cases
plan = (root / 'b01-writer-plan.md').read_text()
for row in m['case_mapping']:
    assert not row['qualified'] and '| ' + row['case_id'] + ' |' in plan
    assert '| ' + row['case_id'] + ' |' in md
    assert row['candidate_ids'] == [c['id'] for c in m['candidates']
                                   if row['case_id'] in c['proposed_case_ids']]
allowed_text = {s['url'] for s in m['evidence_sources']
                if s.get('kind') != 'history'}
urls = {s['url'] for s in m['evidence_sources']}
urls.update(b['metadata_url'] for c in m['candidates'] for b in c['blob_ids'])
cache = {}
for url in sorted(urls):
    p = urllib.parse.urlparse(url)
    if p.netloc == 'raw.githubusercontent.com':
        assert url in allowed_text and re.search(r'/[0-9a-f]{40}/', p.path)
        assert p.path.endswith(('.md', '.rst', '.py', '.sh', '.cs', 'LICENSE', 'LICENSE.txt'))
    else:
        assert p.netloc == 'api.github.com'
        assert re.fullmatch(r'/repos/[^/]+/[^/]+/(git/trees/[0-9a-f]{40}|commits)', p.path)
        if p.path.endswith('/commits'):
            assert re.fullmatch('[0-9a-f]{40}', urllib.parse.parse_qs(p.query)['sha'][0])
    with urllib.request.urlopen(url, timeout=40) as response:
        assert response.headers.get('Link') is None
        cache[url] = response.read().decode('utf-8')
for c in m['candidates']:
    assert c['assessment'] == 'evidence_incomplete' and c['missing_evidence']
    assert c['container_license_evidence'] is None and c['payload_license_evidence'] is None
    assert c['paths'] == [b['path'] for b in c['blob_ids']]
    assert c['id'] in md and c['commit'] in md
    for b in c['blob_ids']:
        tree = json.loads(cache[b['metadata_url']])
        assert tree['sha'] == c['commit'] and tree['truncated'] is False
        entry = next(e for e in tree['tree'] if e['path'] == b['path'])
        assert entry['type'] == 'blob' and entry['sha'] == b['value']
        assert b['algorithm'] == 'git-blob-sha1'
        assert b['path'] in md and b['value'] in md
    for e in (c['generation_evidence'] or []) + c['license_context']:
        assert e['quote'] in cache[e['url']]
    assert set(c['proposed_case_ids']) <= set(cases)
    if c['id'].startswith('J5-'):
        assert c['writer'] == 'rar' and c['writer_version'] == '7.23'
    else:
        assert c['writer'] is None and c['writer_version'] is None
# Check the rendered Sources block's actual URLs and literal evidence independently.
source_section = md.split('\n## Sources\n', 1)[1]
for block in re.split(r'\n(?=\[\d+\] )', source_section.strip()):
    match = re.match(r'\[\d+\] (https://\S+)', block)
    assert match is not None
    source_url = match[1]
    assert source_url in cache
    text = cache[source_url]
    if urllib.parse.urlparse(source_url).netloc == 'api.github.com':
        # GitHub varies JSON whitespace by HTTP client; preserve all string values.
        text = json.dumps(json.loads(text), indent=2, ensure_ascii=False)
    for quoted in block.split('\n    > "')[1:]:
        quoted = quoted.rstrip()
        assert quoted.endswith('"')
        quote = quoted[:-1]
        norm = lambda value: ' '.join(value.split())
        assert norm(quote) in norm(text), (source_url, quote)
for target in re.findall(r'\]\((b01-[^)]+)\)', md):
    assert (root / target).is_file()
print('PASS: 3 projects, 5 sets, 9 Git blobs, 8 unchanged case IDs; '
      'all text/metadata URLs, literal quotes, matrix and local paths checked; '
      '0 fixture payload GETs; no native qualification')
```

Actual checker result: PASS for three projects, five sets, nine Git blobs and
eight unchanged case IDs; all 21 text/metadata URLs were retrieved successfully
without fixture payload GETs. The citation tool reported `citations OK` for 18
cited sources with evidence; three discovery-only ledger entries are intentionally
uncited. No minimum prose-coverage certification is claimed. The first independent
quote-check attempt failed because it assumed single-line quotes and identical
GitHub JSON formatting across HTTP clients. The checker now handles multiline
quotes and parses/reserializes API JSON solely to normalize whitespace, preserving
string values; the corrected check passed without changing source evidence.

Additional actual checks recorded in the review transition:
`python3 -m json.tool docs/ai-migration/qualification/b01-existing-fixture-assessment.json`,
the installed citation ledger `verify --evidence`, `git diff --cached --check`,
reviewed-parent ancestry and staged two-file scope. Final branch/commit and absolute
artifact paths accompany that transition. No corpus/golden/CI/DAG/AGENTS.md,
production, codec, encryption or shared-branch edit is part of this work.

## Sources

[1] https://api.github.com/repos/markokr/rarfile/git/trees/d2f7df6fc843dae356fd6b0a85971dc36fd6e757?recursive=1
    > ""path": "test/files/rar3-old.rar",
      "mode": "100644",
      "type": "blob""
[2] https://raw.githubusercontent.com/markokr/rarfile/d2f7df6fc843dae356fd6b0a85971dc36fd6e757/LICENSE
    > "Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies."
[3] https://raw.githubusercontent.com/markokr/rarfile/d2f7df6fc843dae356fd6b0a85971dc36fd6e757/README.rst
    > "Supports multi volume archives."
[5] https://api.github.com/repos/junrar/junrar/git/trees/1d10acccc6505c756f6df4fca1925fd53a591df9?recursive=1
    > ""path": "src/test/resources/com/github/junrar/rar5unpack/m0-plain-128k.rar",
      "mode": "100644",
      "type": "blob""
[6] https://raw.githubusercontent.com/junrar/junrar/1d10acccc6505c756f6df4fca1925fd53a591df9/LICENSE
    > "The source code of UnRAR utility is freeware. This means:"
[7] https://raw.githubusercontent.com/junrar/junrar/1d10acccc6505c756f6df4fca1925fd53a591df9/generate-testdata.sh
    > "rar a -ep1 -mc$par1$1+ $path/$outdir/$i/$i-mc$par1$1+.rar $path/$indir/$i"
[8] https://raw.githubusercontent.com/junrar/junrar/1d10acccc6505c756f6df4fca1925fd53a591df9/src/test/resources/com/github/junrar/rar5unpack/README.md
    > "`ArchiveRar5UnpackTest`. Produced with `rar 7.23` (`-ma5`); the expected payload"
[9] https://raw.githubusercontent.com/junrar/junrar/1d10acccc6505c756f6df4fca1925fd53a591df9/src/test/resources/com/github/junrar/volumes/rar5-part/README.md
    > "`.partN.rar` RAR5 volume sets for `ArchiveRar5VolumeTest`, produced with `rar 7.23`"
[10] https://api.github.com/repos/adamhathcock/sharpcompress/git/trees/e04d51176c5d87668c4c8779825342230c33aa74?recursive=1
    > ""path": "tests/TestArchives/Archives/Rar.none.rar",
      "mode": "100644",
      "type": "blob""
[11] https://raw.githubusercontent.com/adamhathcock/sharpcompress/e04d51176c5d87668c4c8779825342230c33aa74/LICENSE.txt
    > "The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software."
[13] https://raw.githubusercontent.com/junrar/junrar/1d10acccc6505c756f6df4fca1925fd53a591df9/src/test/resources/com/github/junrar/volumes/rar5-part/gen_volume_payloads.py
    > "Deterministic payloads for the M3.9 RAR5 multi-volume fixtures (issue #30)."
[15] https://raw.githubusercontent.com/adamhathcock/sharpcompress/e04d51176c5d87668c4c8779825342230c33aa74/tests/SharpCompress.Test/Rar/RarArchiveTests.cs
    > "public void Rar_None_ArchiveStreamRead() => ArchiveStreamRead("Rar.none.rar");"
[16] https://api.github.com/repos/junrar/junrar/commits?sha=1d10acccc6505c756f6df4fca1925fd53a591df9&path=src%2Ftest%2Fresources%2Fcom%2Fgithub%2Fjunrar%2Frar5unpack%2FREADME.md&per_page=100
    > "feat(unpack): RAR5 Unpack5 decode loop + engine lifecycle (M3.7)"
[17] https://api.github.com/repos/junrar/junrar/commits?sha=1d10acccc6505c756f6df4fca1925fd53a591df9&path=src%2Ftest%2Fresources%2Fcom%2Fgithub%2Fjunrar%2Fvolumes%2Frar5-part%2FREADME.md&per_page=100
    > "feat(volume): RAR5 multi-volume spanning + typed volume errors (M3.9)"
[18] https://api.github.com/repos/markokr/rarfile/commits?sha=d2f7df6fc843dae356fd6b0a85971dc36fd6e757&path=test%2Ffiles%2Frar3-old.rar&per_page=100
    > "New test files for rar5"
[19] https://api.github.com/repos/markokr/rarfile/commits?sha=d2f7df6fc843dae356fd6b0a85971dc36fd6e757&path=test%2Ffiles%2Frar3-old.r00&per_page=100
    > "New test files for rar5"
[20] https://api.github.com/repos/markokr/rarfile/commits?sha=d2f7df6fc843dae356fd6b0a85971dc36fd6e757&path=test%2Ffiles%2Frar3-old.r01&per_page=100
    > "New test files for rar5"
[21] https://api.github.com/repos/adamhathcock/sharpcompress/commits?sha=e04d51176c5d87668c4c8779825342230c33aa74&path=tests%2FTestArchives%2FArchives%2FRar.none.rar&per_page=100
    > "Move test folder to be tests"
