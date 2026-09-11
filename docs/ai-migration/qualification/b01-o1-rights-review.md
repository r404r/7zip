# B01-O1: finite three-family rights assessment

Task `t_4ea8d1ca`; branch `wt/t_4ea8d1ca`; assessment date 2026-09-11 UTC.
Status: **author assessment awaiting independent review; no import permission**.
Companions: [normative replay policy](b01-replay-policy.md) and
[structured evidence and exact paths](b01-o1-rights-review.json), `schema_version=1`.

## Result and authority

**DRF-OLD, DRF-SOLID and DRF-VOL are `ready_for_import_decision` as an engineering
risk assessment, not accepted fixtures or certified complete rights chains.**
The affirmative evidence is a versioned distribution declaration covering the
actual archive paths plus matching upstream contributor attribution. The remaining
embedded-rights uncertainty is disclosed below, not erased by the replay policy.
No personalized grant is demanded merely because no historical writer hash exists.
No inference that a generic software license necessarily owns all embedded content
is made. This assessment is not legal advice.

Original B01 `t_22299c6f` comment 89 records actual **「批准」**, Unix timestamp
`1789127406`; the operator's subsequent **「选择O1」** confirms the same limited
phase. [B01-R](b01-resolution-options.md), reviewed commit
`1fc1f83091a50bab2c691e372eb8b86b745fe008` / integration
`b7c30b273fd930c3167434c87b85c685aac846cd`, is the immutable basis. Both AGENTS.md
files and complete controlling comment were read. Source branch was verified as
`ai/migration-bootstrap-20260911`, clean task branch as `wt/t_4ea8d1ca`; reviewed
parent is already an ancestor. No extra merge was necessary. Complete parent
subscription inheritance and default Telegram notify+wake were checked read-only,
without emitting route identities or changing configuration.

Only policy formalization and rights assessment are authorized now. No archives
or payload members were downloaded, imported or extracted; no writer/native run,
upstream contact, spending, broader project search, DAG/golden/production change,
B01 unblock/archive or B03/B04 authorization change occurred. The policy document
contains the complete M1/B01/B01-P/W/F/M2/M3 requirement trace. Earlier reports and
unreviewed B01 implementation remain untouched.

## What the licensing evidence actually says

The Debian `python-rarfile` `4.5-1` copyright file has the literal assignment
`Files: *`, `Copyright: 2005-2026 Marko Kreen` (full notice in JSON), `License: ISC`;
its only later file stanza is `Files: debian/*`, `License: GPL-2+`.[2]
Under the documented copyright-format matching rules, `*` includes slash-separated
paths and later matching paragraphs prevail.[1] Thus every selected `test/files/`
archive path is affirmatively assigned ISC, not packaging GPL-2+.[1][2]
The versioned directory metadata lists all seven selected paths and sizes.[7]

The operative permission literally says: “Permission to use, copy, modify, and/or
distribute this software for any purpose with or without fee is hereby granted,
provided that the above copyright notice and this permission notice appear in all
copies.”[2] The full stanza, including the literal disclaimer naming ISC, is
preserved in JSON; do not silently modernize/rewrite it.[2] For any later authorized
redistribution, retain full copyright/permission/disclaimer and source/version/path
mapping alongside fixtures and permitted derivatives. Do not replace this existing
notice with B01-W's proposed CC0 payload or MIT generator grant. Packaging GPL-2+
is a separate obligation if packaging files themselves are ever copied.[2]

Current-entrypoint histories for the three families each identify Marko Kreen,
commit `6ab3317c6a02c4f1082ab8570a34d4868c7baa3c`, with message
“New test files for rar5” / “Move away from shell scripts to tox+nose”.[8][9][10]
Pinned tree metadata at `d2f7df6fc843dae356fd6b0a85971dc36fd6e757` separately binds
all seven upstream object paths and blob SHA-1 identities recorded in JSON.[3]
History is corroborating attribution, not proof of original creation, exhaustive
rename history, original writer version or authority over all member sources.
The message does not make `rar3-old` a RAR5 archive. Debian bytes have NOT been
equated with those upstream objects; no archive/member SHA-256 was measured here.

### Container, members and metadata: separate findings

1. Container paths: the distribution manifest explicitly assigns the selected
   files, not just neighboring source code.[2] Combined with matching contribution
   attribution, this is meaningful affirmative evidence for a bounded import
   decision.[8][9][10] No selected-path exclusion or contradictory attribution was
   found in these inspected sources. That limited observation is not a global
   rights search or a legal warranty.
2. Members: expected dumps identify the members listed below, not their complete
   contents or original authors.[4][5][6] Neither the dumps nor the history contains
   a per-member rights chain. The distribution declaration contains no selected
   fixture carve-out, which supports considering the files as project test assets,
   but extending it to every actual embedded member remains an engineering inference
   with third-party-content risk. It is NOT recorded as a proven complete grant.
3. Names/metadata: inventory is also incomplete until actual bytes may be examined;
   expected names/times/modes are not source-to-member rights attestations.[4][5][6]
   Names resembling test data, small sizes or equal CRCs are not copyright grants.
   A copied payload/notice discovered later must stop the pilot for review.
4. Grant authority: distribution attribution aligns with contributor identity, but
   no exhaustive chain of title or personal attestation was established. Missing
   personal confirmation alone does not invalidate coherent public distribution
   evidence; nor can this author invent confirmation from that contributor.

## Exact bounded families and findings

All paths below are relative to Debian `python-rarfile` `4.5-1`; JSON supplies exact
versioned retrieval URLs (not fetched archive URLs), declared sizes, upstream
context SHA-1 and literal expected dumps. Only `.exp`, copyright/specification and
directory/history/tree metadata were inspected. Every null has an explicit reason.

| Family | Exact selected archive paths | Expected member evidence (not extracted data) | Outcome |
| --- | --- | --- | --- |
| DRF-OLD | `test/files/rar3-old.rar`, `test/files/rar3-old.r00`, `test/files/rar3-old.r01` | `vols/bigfile.txt` 205000 bytes, `vols/smallfile.txt` 2050; `meth=0`, split flag, member on `vol=2`, `ver=20`.[6] | `ready_for_import_decision`; stored old-name volume lead, not named-writer or full classic decoder coverage. |
| DRF-SOLID | `test/files/rar5-solid.rar` | `stest1.txt`, `stest2.txt`, 2048 bytes each; `cmp_meth=3`, second `solid=True`.[4] | `ready_for_import_decision`; small solid/compressed lead, not measured LZ decoding or known payload authorship. |
| DRF-VOL | `test/files/rar5-vols.part1.rar`, `test/files/rar5-vols.part2.rar`, `test/files/rar5-vols.part3.rar` | `vols/bigfile.txt` 205000 bytes, `vols/smallfile.txt` 2050; `cmp_meth=0`, `solid=False`, split and `vol=2`.[5] | `ready_for_import_decision`; stored multipart lead, not actual missing-volume/entrypoint qualification. |

For EACH family the decision is the same for a specific reason: all its selected
parts fall in the same affirmative ISC path assignment, its entrypoint history
corroborates the named contributor, and no distinct contrary notice is present in
this bounded evidence. There is no justified differential rejection solely from
its filename or size. `evidence_incomplete` would instead be required if the review
finds a material contradictory/excluded path or insufficient basis for the stated
bounded decision; `rejected` would require affirmative incompatibility evidence,
not merely absence of a historical writer executable. Neither alternative is a
finding made here. Independent reviewer may disagree with this risk assessment.

`ready_for_import_decision` means ready to present a finite, disclosed-risk choice
on these exact paths, not “all rights resolved,” “download allowed,” or “B01 PASS.”
Actual archive hashes, complete member/source/metadata binding, native results and
case-feature equivalence remain absent. If the operator requires demonstrated
complete embedded rights before even quarantine acquisition, this evidence does
not satisfy that stricter threshold; stop and record that exact unresolved
question, without an automatic inquiry or broader audit.

## Original eight B01-W case IDs: no coverage silently removed

| B01-W ID | Candidate in THIS pilot | Retained requirement / current gap |
| --- | --- | --- |
| R4-STORE | none | Classic stored single-archive row remains unqualified. |
| R4-LZ | none | Classic general compressed row remains unqualified. |
| R4-PPM | none | PPM/text-method row remains unqualified. |
| R4-VOL | none | Stored/non-solid numbered native classic multipart remains unqualified; DRF-OLD is not this naming contract. |
| R4-OLDVOL | DRF-OLD | Stored old-name native volumes remain unqualified pending actual handler/method, complete set, missing-first/middle/last and non-first entrypoint results. |
| R5-STORE | none | Modern stored single-archive row remains unqualified; DRF-VOL does not automatically fill it. |
| R5-LZ-SOLID | DRF-SOLID | Modern compressed solid row remains unqualified pending actual native solid/method effects and full operation coverage. |
| R5-VOL | DRF-VOL | Modern stored/non-solid native multipart remains unqualified pending set/entrypoint/error measurements. |

The policy explicitly substitutes acquired measured-intent evidence for exact
B01-W generation recipe identity only where mapped; it does not substitute a
smaller acceptance target. These members do not demonstrate `ALL`, empty/binary/
nested-path/dictionary dimensions of the original recipe. Unshown dimensions and
B01-W corruption/probing/list/test/extract/create-refusal outcomes remain required.
Stored `ver=20` is not evidence of all Rar3 PPM/LZ filters. PPM transitions,
levels/dictionaries, classic compressed solid/multipart, Rar1/Rar2, unsupported
and damaged compressed RAR, B02 code pages, B03/B04 metadata/safety/large files,
B05 passwords, B08 FFI, recovery/SFX, nested chains, other retained formats and
GUI/desktop gaps remain as enumerated in B01-R and the JSON. No production
prerequisite is released by this policy/rights document.

## Finite next decision, not an action request in this run

After independent PASS, reviewer reports these exact findings to original B01
and reads back the handoff. The subsequent human choice is distinct from the
already-approved O1 policy, which MUST NOT be re-requested:

- Recommended: authorize a separately bounded acquisition/quarantine/import pilot
  of only the seven pinned files, accepting the disclosed distribution-attribution
  risk for that step; preserve ISC notices and require complete actual byte/member
  inventory, source/rights recheck and reviewed native qualification before corpus
  acceptance. Impact: makes an engineering pilot possible, not full rights warranty
  or B01 closure. Resource/security limits must be explicit before execution.
- Require stronger embedded-member authority evidence before acquisition. Exact
  question: “Are every actual member and its names/metadata covered by the stated
  ISC grant, what are their original sources, and is there any contrary notice?”
  This report cannot answer from unread payloads. Impact: keep these families
  pending; no inquiry is sent or automatically commissioned.
- Defer the pilot. Impact: zero acquisition risk and zero new qualification;
  B01 remains gated, eligible independent work continues under its own decisions.

Any actual later permission must specify scope; this report confers none. Stop
this task after independent review/handoff. No repeated general research, external
questions, follow-up cards, reapproval of O1, or B01 state/DAG change.

## Reproduction and actual checks

Document-only: native builds/tests are not applicable because no executable code
changed, compilation cannot establish redistribution rights, and archive/native
execution is outside authorization. No Windows/Linux/macOS compatibility result
is claimed. The below checker validates documentation/evidence, not legal reasoning.

This run fetched six specification/copyright/expected-dump/directory text-metadata
sources online. GitHub tree/history retrieval encountered the unchanged error:
`urllib.error.HTTPError: HTTP Error 403: rate limit exceeded`.
The four corresponding public text/metadata snapshots from the reviewed B01-R
worktree were then read and their raw SHA-256 verified against its committed JSON.
This is locally verified reviewed evidence, NOT a successful fresh GitHub fetch.
No credentials, rate-limit workaround, alternate project or archive GET was used.
The companion JSON records each verification mode, original retrieval URL, exact
quotes and raw text-response digest. All ten evidence contents were checked.

To reproduce without relying on surviving worktrees, save the following single
Python block as a temporary file and run `python3 <checker.py>` from repository
root. It fetches only the exact ten allowlisted text/metadata URLs already in
B01-R. A network failure is a failure, not permission to fetch other content.
For offline review using this run's verified snapshots, run
`python3 <checker.py> --offline .b01-o1`; offline mode requires exact raw digests.
The full files are reproducible from the recorded URLs, not stored as hidden
prerequisites. Server JSON formatting may change online; compare parsed values
and literal text quotes, not response serialization equality in that mode.

```python
import copy, fnmatch, hashlib, json, pathlib, re, sys, urllib.request
from html.parser import HTMLParser
q=pathlib.Path('docs/ai-migration/qualification')
m=json.loads((q/'b01-o1-rights-review.json').read_text())
p=json.loads((q/'b01-resolution-options.json').read_text())
report=(q/'b01-o1-rights-review.md').read_text()
policy=(q/'b01-replay-policy.md').read_text()
ids=['DRF-OLD','DRF-SOLID','DRF-VOL']
cases=['R4-STORE','R4-LZ','R4-PPM','R4-VOL','R4-OLDVOL','R5-STORE','R5-LZ-SOLID','R5-VOL']
def schema(d):
    assert type(d['schema_version']) is int and d['schema_version']==1
    assert d['evidence_class_enum']==['acquired-immutable','generated-reproducible']
    assert list(d['candidates'])==ids and list(d['case_mapping'])==cases
    assert d['authority']['policy_approved'] is True
    assert d['authority']['import_authorized'] is False
    assert not d['accepted_fixtures'] and not d['complete_b01_solution']
    assert not d['native_results_produced']
    assert d['import_review_candidates']==ids
    for key in ['archive_payload_downloads','imports','extractions','writer_executions','native_tests','correspondence_sent','spending','dag_changes']:
        assert type(d['scope'][key]) is int and d['scope'][key]==0
    for cid,c in d['candidates'].items():
        assert c['evidence_class'] in d['evidence_class_enum']
        assert c['evidence_class']=='acquired-immutable'  # This pilot only.
        assert c['outcome'] in ['ready_for_import_decision','evidence_incomplete','rejected']
        assert c['qualified'] is False and c['import_approved'] is False
        w=c['historical_writer']
        assert all(w[k] is None for k in ['generator','version','build','package_sha256','executable_sha256','invocation'])
        assert w['unknown_reason'] and w['named_writer_interoperability_claim'] is False
        assert w['regeneration_claim'] is False
        for key in ['known_facts','unknowns','risks','finite_next_action','stop_condition','decision_question','unresolved_evidence_question']:
            assert c[key]
        assert c['rights_assessment']['outcome_not_permission'] is True
        assert c['case_ids']==p['candidates'][cid]['proposed_case_ids']
        assert [f['path'] for f in c['files']]==[f['path'] for f in p['candidates'][cid]['objects']]
        assert c['proposed_volume_order']==[f['path'] for f in c['files']]
        assert all(f['archive_sha256'] is None and f['sha256_unknown_reason'] for f in c['files'])
        assert all(x['sha256'] is None and x['rights_source_binding'] is None for x in c['expected_metadata']['members'])
    for case,row in d['case_mapping'].items():
        assert row['qualified'] is False and row['recipe_identity_claim'] is False
        assert row['candidate_ids']==[cid for cid,c in d['candidates'].items() if case in c['case_ids']]
schema(m)
mutations=[lambda d:d.update(schema_version=2),
           lambda d:d['candidates']['DRF-OLD'].update(evidence_class='unknown'),
           lambda d:d['candidates']['DRF-OLD']['historical_writer'].update(unknown_reason=''),
           lambda d:d['candidates']['DRF-OLD']['historical_writer'].update(named_writer_interoperability_claim=True),
           lambda d:d['case_mapping'].pop('R4-PPM'),
           lambda d:d['candidates']['DRF-SOLID'].update(qualified=True)]
for mutate in mutations:
    d=copy.deepcopy(m); mutate(d)
    try: schema(d)
    except AssertionError: pass
    else: raise AssertionError('Assessment negative control escaped')
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]
    def handle_data(self,data): self.parts.append(data)
assert len(m['sources'])==10
cache={}; rawtexts={}
allowed={s['retrieval_url'] for s in p['sources'] if s['id'] in [1,8,9,10,11,16,19,20,21,22]}
assert {s['retrieval_url'] for s in m['sources']}==allowed
for s in m['sources']:
    if len(sys.argv)>1:
        assert len(sys.argv)==3 and sys.argv[1]=='--offline'
        raw=(pathlib.Path(sys.argv[2])/s['snapshot_file']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==s['raw_snapshot_sha256']
    else:
        with urllib.request.urlopen(s['retrieval_url'],timeout=40) as r:
            assert not r.headers.get('Link'), 'Unconsumed pagination'
            raw=r.read()
    text=raw.decode('utf-8'); rawtexts[s['id']]=text
    if s['kind']=='html_text':
        parser=Text(); parser.feed(text); text=' '.join(parser.parts)
    elif s['kind']=='history':
        entries=json.loads(text)
        assert len(entries)==1
        e=entries[0]
        assert e['sha']=='6ab3317c6a02c4f1082ab8570a34d4868c7baa3c'
        assert e['commit']['author']['name']=='Marko Kreen'
        text='\n'.join(e['commit']['message'] for e in entries)
    elif s['kind']=='tree':
        data=json.loads(text)
        if 'truncated' in data: assert data['truncated'] is False
        text=json.dumps(data,indent=2,ensure_ascii=False)
    for quote in s['quotes']:
        assert ' '.join(quote.split()) in ' '.join(text.split()),(s['id'],quote)
    cache[s['id']]=text
copyright=rawtexts[2]
for key in ['literal_selected_stanza','literal_exception_stanza']:
    assert m['rights_common'][key] in copyright
stanzas=[]
for paragraph in copyright.split('\n\n'):
    if paragraph.startswith('Files: '):
        pattern=paragraph.splitlines()[0].removeprefix('Files: ')
        license_id=re.search(r'^License: (.+)$',paragraph,re.M)
        assert license_id
        stanzas.append((pattern,license_id[1]))
assert stanzas==[('*','ISC'),('debian/*','GPL-2+')]
tree=json.loads(rawtexts[3]); directory=json.loads(rawtexts[7])
for cid,c in m['candidates'].items():
    exp=rawtexts[c['expected_metadata']['source_id']]
    assert c['expected_metadata']['literal_text']==exp
    for member in c['expected_metadata']['members']:
        assert 'name='+member['name'] in exp
        assert 'dec='+str(member['declared_decoded_size']) in exp
    history=json.loads(rawtexts[c['history']['source_id']])[0]
    assert c['history']['literal_message']==history['commit']['message']
    for f in c['files']:
        matches=[lic for pat,lic in stanzas if fnmatch.fnmatchcase(f['path'],pat)]
        assert matches[-1]=='ISC'
        entry=next(e for e in directory['content'] if e['name']==pathlib.PurePosixPath(f['path']).name)
        assert entry['stat']['size']==f['declared_size']
        obj=next(e for e in tree['tree'] if e['path']==f['path'])
        assert obj['sha']==f['upstream_context_git_blob_sha1']
for doc in [report,policy]:
    for target in re.findall(r'\]\(([^)]+)\)',doc):
        if '://' not in target:
            assert (q/target.split('#')[0]).is_file(), target
for case in cases: assert '| '+case+' |' in report
for term in ['M1','B01-P','B01-W','B01-F','M2','M3','B01-L','acquired-immutable','generated-reproducible','schema_version=1']:
    assert term in policy
prose=re.sub(r'```.*?```','',report.split('\n## Sources\n')[0],flags=re.S)
cited={int(n) for n in re.findall(r'\[(\d+)\]',prose)}
rendered={int(n):url for n,url in re.findall(r'^\[(\d+)\] (https://\S+)',report.split('\n## Sources\n')[1],re.M)}
assert cited==set(rendered)=={s['id'] for s in m['sources']}
assert all(rendered[s['id']]==s['url'] for s in m['sources'])
print('PASS: 10 source contents, 3 families, 7 paths/ISC assignments, 8 cases, schema, 6 negative controls, quotes/history/member metadata, local links/citations/policy trace; no native or rights certification')
```

Actual `python3 .b01-o1/verify.py --offline .b01-o1` returned PASS for ten source
contents, three families, seven paths/ISC assignments, eight cases, six assessment
negative controls, literal evidence and local links/citations. The citation tool's
`verify --strict --evidence` returned `citations OK` for all ten cited sources;
its prose coverage statistic was 8%, not a completeness certification (much of
this report states policy/engineering judgments and locally traced obligations).
`python3 .b01-o1/local-check.py` passed exact embedded/executed checker equality,
syntax, three-owned-file staging, secret-pattern and whitespace checks, reviewed
parent ancestry and unchanged clean automation base/dev-main baseline checks.
`python3 -m json.tool` also passed. No native build/test result is implied.

Exact local commands and outputs, source/base preservation and commit are recorded
in the review transition. Reviewer independently cold-reads all three artifacts,
checks authority and licensing meaning (automated tests cannot approve either),
then uses same-card PASS/CHANGES. Two substantive failed rounds require typed
`needs_input`, not endless repairs. PASS completes only this card; B01 stays gated.

## Sources

[1] https://www.debian.org/doc/packaging-manuals/copyright-format/1.0
[2] https://sources.debian.org/data/main/p/python-rarfile/4.5-1/debian/copyright
[3] https://api.github.com/repos/markokr/rarfile/git/trees/d2f7df6fc843dae356fd6b0a85971dc36fd6e757?recursive=1
[4] https://sources.debian.org/data/main/p/python-rarfile/4.5-1/test/files/rar5-solid.rar.exp
[5] https://sources.debian.org/data/main/p/python-rarfile/4.5-1/test/files/rar5-vols.part1.rar.exp
[6] https://sources.debian.org/data/main/p/python-rarfile/4.5-1/test/files/rar3-old.rar.exp
[7] https://sources.debian.org/api/src/python-rarfile/4.5-1/test/files
[8] https://api.github.com/repos/markokr/rarfile/commits?sha=d2f7df6fc843dae356fd6b0a85971dc36fd6e757&path=test%2Ffiles%2Frar5-solid.rar&per_page=100
[9] https://api.github.com/repos/markokr/rarfile/commits?sha=d2f7df6fc843dae356fd6b0a85971dc36fd6e757&path=test%2Ffiles%2Frar5-vols.part1.rar&per_page=100
[10] https://api.github.com/repos/markokr/rarfile/commits?sha=d2f7df6fc843dae356fd6b0a85971dc36fd6e757&path=test%2Ffiles%2Frar3-old.rar&per_page=100
