# B01-P: bounded external RAR provenance audit

Task `t_f337e38d`; branch `wt/t_f337e38d`; public evidence retrieved 2026-09-11 UTC.

## Disposition and boundary

**No candidate is selected for import. The B01 gate is not resolved.** This is an
independently reviewable evidence report, not a legal opinion, fixture acceptance,
permission to contact upstream, or permission to release affected production.
Unknown provenance is not a finding of prohibited redistribution.

The audit covers exactly the B01 named basic RAR file plus the four-volume classic
RAR family referenced in the adjacent C test. Their paths are present at libarchive
commit `60b1d17ddf2fbabc6bca31dae01613d6dbea3cde`.[2][5]
Other RAR/RAR5, encrypted, compressed-method and regression fixture families are
not audited or implicitly rejected. This deliberately bounded scope does not
reduce B01's remaining format/method or native qualification requirements.

The read-only local lead was task `t_22299c6f`, commit
`9d01d5069f5b117aa5c69dd5cc62f090869d7650`,
`docs/ai-migration/qualification/b01.md`, especially its external RAR gate.
That implementation is unreviewed; none of its changes were merged or its claims
used as upstream proof. Source and task `AGENTS.md` were read. Source branch was
`ai/migration-bootstrap-20260911`; the clean task started at
`2eeeb0084ef1fd3c4e7abd8282c969ea5b7ab86a`. Reviewed M3 commit
`0706af3d714e8c2701691a19a0c663ae7b749c88` was already an ancestor; no parent
merge/cherry-pick was necessary.

[Machine-readable evidence matrix](b01-provenance.json) repeats the five exact
identities, introduction/parent commits, missing evidence and disposition. Git
blob IDs below identify the **uuencoded file**, as reported by GitHub tree
metadata; they are not measured archive SHA-256 or member hashes. No `.uu`, `.rar`,
archive blob, clone or archive diff was acquired; only public metadata, license
text, and the C test as non-executable research text were retrieved.

## File identities and history

All paths below are relative to the upstream repository, not local fixture paths.
Encoded sizes and pinned blob IDs come from the complete tree response
(`truncated: false`).[5]

| ID | Exact upstream path | Pinned Git blob ID | Encoded bytes | Introduction | Missing evidence / disposition |
| --- | --- | --- | ---: | --- | --- |
| basic | `libarchive/test/test_read_format_rar.rar.uu` | `f197a2983302f5829de2719bdddcf43b8c59b201` | 505 | A | G, P-basic, L, H, N; not selected |
| part0001 | `libarchive/test/test_read_format_rar_multivolume.part0001.rar.uu` | `bbe4be4c9070c0551dd9450cafa6ea0e617157ef` | 82730 | B | G, P-multi, L, H, N; not selected |
| part0002 | `libarchive/test/test_read_format_rar_multivolume.part0002.rar.uu` | `a61a2fbc73121a0593b2645e4804415c1e6de383` | 82730 | B | G, P-multi, L, H, N; not selected |
| part0003 | `libarchive/test/test_read_format_rar_multivolume.part0003.rar.uu` | `ef70b9eba606f7e2d03e8be7233495450d9dac83` | 82730 | B | G, P-multi, L, H, N; not selected |
| part0004 | `libarchive/test/test_read_format_rar_multivolume.part0004.rar.uu` | `20931f62c5858e1b17b5275f058fc45cdc51ddb9` | 12740 | B | G, P-multi, L, H, N; not selected |

A is `099075c11ce9143f7375ed4b1264a10a45a072f9`, authored/committed by Tim
Kientzle at `2011-06-27T00:40:08Z`; its exact message starts
“First cut at RAR support, including RARv3.” and records `SVN-Revision: 3427`.[6]
The basic path is absent in parent `ab0f070f92105199e8b71d6de9afdbc05667e9d5`
and present in A with blob `75f93b4c281a9512b24f094a6d6e23fcc17e0868`.[13][14]
This establishes a repository introduction, **not** who generated the archive,
which writer build was used, or who owns its embedded text.

B is `416694915449219d505531b1096384f3237dd6cc`, authored by Andres Mejia at
`2012-02-24T16:05:00Z`, committed at `2012-03-26T02:47:14Z`; the complete message
is “Implement support for reading multivolume RAR archive files.”[7]
All four paths are absent in parent `7b543b13d813e529364c7b70ae204ce7c0eddfc3`
and present in B; per-file introduction blob IDs are retained in the matrix.[15][16]
Again, commit authorship is not a fixture-generation or payload-rights attestation.

Each path's history was queried separately with `sha` pinned and `per_page=100`.
Basic and part0001 each return introduction plus later envelope maintenance.[3][4]
Part0002, part0003 and part0004 independently return the same multipart
introduction and maintenance commits; no family-level assumption substituted
for these queries.[10][11][12]
The later commit is `33140186cb7b918f2b84df68c2a2fdbbf8d4881a`, titled
“Gardening: Fix the `begin` lines in many of the uuencoded test data (#2043)”.[3]
PR #2043 explains: “The libarchive test harness always extracts these to the
truncated source filename, ignoring the name in the `begin` line.”[8]
That is evidence about envelope naming, not a new RAR writer version. This audit
did not decode/compare old and new archives and makes no byte-equality claim.

## Associated discussion and author statements

GitHub associates multipart introduction B with PR #2, **Multivolume File Read
Support**, whose head is B and whose merge commit is
`e69e0e5292ef592dac1f3e2ab96804c3af0a0c56`.[18]
Its author states: “This will enable multivolume support for libarchive. It
includes support to read files split using the 'split' program, and also support
to read RAR multivolume files.”[18]
This does not establish that `split` generated the RAR parts, nor identify a
proprietary writer product/build.

The PR conversation concerns implementation placement and possible libunrar
integration. One author's statement is “Libunrar does not support v3, which is
what I'm looking to support first.”[21]
That is historical reader discussion, not verified present-day capabilities or
a grant for the payloads. The discussion's question about format-spec restrictions
is a participant's question, not a legal determination; it must not be upgraded
into a prohibition on these archives.[21]

The matrix records exact empty responses for the basic introduction's associated
PR lookup, both introduction commit-comment endpoints, PR #2 review comments and
reviews, and PR #2043 issue comments. All were read-only queries. Empty responses
only bound this retrieval; they do not prove that no historical mailing-list,
SVN, Google Code or private generation records exist. The seven PR #2 issue
comments were inspected in full; no fixture-specific writer/version, payload
rights or redistribution confirmation was found in that inspected conversation.[21]

Supplemental web searches used the literal queries:

- `"libarchive" "RAR" "Mejia" "test" "2011"`
- `"test_read_format_rar_multivolume" license`
- `"libarchive" "rar" "fixtures" "license"`
- `"libarchive" "RAR" "test" "license" "Mejia"`
- `"test_read_format_rar.rar" "created"`
- `"libarchive" "multivolume" "2012" "RAR"`

Results were discovery leads only, not license evidence. They did not yield the
missing file-specific attestation. No assertion is made that this is an exhaustive
search of the public web; alternate repositories discovered in search were not
substituted for the assigned immutable libarchive corpus.

## Payload and licensing applicability

At the pin, `COPYING` begins “The libarchive distribution as a whole is Copyright
by Tim Kientzle” and says it is subject to the notice at the bottom.[1]
It also states that individual files should carry clear licensing statements and
“the actual statements in the files are controlling.”[1]
The summarized default explicitly mentions C sources and documentation, and the
notice permits source/binary redistribution subject to notice retention.[1]
This is meaningful distribution-wide licensing context, not no license at all.
It does not, in the material inspected, identify the writer/version or establish
the origin and rights chain for every embedded payload. This report therefore
makes **no automatic license inference** from neighboring C source to the archives.

The neighboring C file carries its own copyright/redistribution notice. Its
`test_read_format_rar_basic` expects `test.txt` and `testdir/test.txt`, each holding
`const char test_txt[] = "test text document\r\n";`, plus a symlink and directories.[2]
This establishes what the test expects, not an independently read member manifest
or a rights-holder statement. Trivial-looking text is not assigned CC0/public-domain
status by this audit.

The multipart helper at upstream `libarchive/test/test_read_format_rar.c:926-1046`
expects `ppmd_lzss_conversion_test.txt` of 241647978 bytes,
`LibarchiveAddingTest.html` and `testdir/LibarchiveAddingTest.html` of 20111 bytes,
`testdir/test.txt` of 20 bytes, `testlink` targeting `LibarchiveAddingTest.html`,
and directory entries.[2]
It checks trailing portions for the large text and HTML entries, not a complete
origin/rights manifest.[2]
The HTML filename is not evidence that every byte was authored by libarchive
contributors or covered by the C test's license. A huge member must also receive
resource-budget review before later extraction; none was extracted here.

No actual writer product/version, generating command tied to these blobs, or
payload-specific redistribution attestation was found in the inspected history,
PR discussion, `COPYING` and adjacent C test. Format label `RARv3`, commit dates,
libarchive reader versions and expected file timestamps are not writer versions.
The B01 lead's statement about missing `.uu` headers was not independently
revalidated by downloading those files in this audit; it remains only a lead.

## Exact missing evidence and confidence

The table and matrix apply the following obligations separately to every row:

- **G**: Actual archive writer product and exact version/build, command/options,
  plus a generation record or responsible creator attestation binding it to the
  named immutable files. Currently product and version are **unknown**, not guessed.
- **P-basic**: Creator/source and rights-holder confirmation for the test text,
  path/link metadata and archive container in the basic file.
- **P-multi**: Creator/source and rights for the **whole** large text, both HTML
  copies, test text and path/link metadata across all four volumes. Identify the
  HTML's original revision and incorporated material; checking tails is insufficient.
- **L**: Applicable redistribution terms for exact encoded archives, decoded
  containers and all embedded material; attribution/notice obligations and the
  grantor's authority. A maintainer can confirm existing applicable terms rather
  than necessarily inventing a new license. A claim must be bound to filenames
  and immutable identities, not merely “all tests should be fine.”
- **H**: After evidence review and authorized acquisition, calculate encoded and
  decoded SHA-256 and full member hashes; do not substitute these Git blob IDs.
- **N**: B01 native Windows/Linux/macOS list/test/extract and required error/volume
  qualification, immutable oracle handling and independent review. This research
  neither runs nor replaces those tests.

Confidence is high for the path/commit identities and what the C assertions say;
limited for absence of provenance outside the material inspected; no legal
conclusion is offered. The selected-candidate set is empty because **G/P/L remain
unresolved**, separately from the intentionally deferred H/N engineering work.

## Draft inquiry — not sent; operator approval required

Suggested audience: libarchive maintainers, asking them to route historical
creation questions to the relevant contributors. Do not guess private addresses,
post publicly, or attach any fixture bytes without separate approval.

> Subject: Provenance and redistribution confirmation for five pinned RAR test fixtures
>
> We are documenting an external interoperability corpus and have not imported
> these fixtures. Could you help locate the original generation and rights records
> for the five exact libarchive paths in the table above at commit
> 60b1d17ddf2fbabc6bca31dae01613d6dbea3cde (including the listed Git blob IDs)?
>
> We traced test_read_format_rar.rar.uu to commit
> 099075c11ce9143f7375ed4b1264a10a45a072f9 / SVN revision 3427, and all four
> test_read_format_rar_multivolume.part0001.rar.uu through part0004.rar.uu to
> 416694915449219d505531b1096384f3237dd6cc / PR #2. Later commit
> 33140186cb7b918f2b84df68c2a2fdbbf8d4881a describes uuencode filename maintenance.
>
> 1. Who created each archive/set, using which actual writer product, version/build
>    and command/options? Are contemporaneous logs or generation scripts available?
>    If the version is unknown, please say so rather than infer it from RAR format
>    version or archive timestamps.
> 2. What are the original sources/authors of all embedded payloads, particularly
>    ppmd_lzss_conversion_test.txt and both LibarchiveAddingTest.html copies?
>    Which exact document revision and any third-party material were incorporated?
> 3. Does the distribution's COPYING notice authorize redistribution of these exact
>    encoded fixtures, decoded archives and all their contents in another project's
>    test corpus and CI? Please identify applicable terms, required notices and the
>    basis for the rights confirmation, including any exceptions.
> 4. Can the confirmation be recorded in an upstream commit or a stable public
>    statement explicitly naming these files/identities? If original records cannot
>    be recovered, is there a separately documented replacement corpus with known
>    writer/version and fully authorized synthetic payloads?
>
> We are not requesting a license waiver, proprietary writer license keys, or any
> private/user archive. A partial answer is useful but will not be treated as
> confirmation of fields that remain unknown.

## Operator options and downstream handoff

1. **Recommended:** approve sending the draft inquiry (or supply equivalent
   verifiable existing records). Impact: preserves all B01 requirements and avoids
   importing unknown bytes; depends on historical records and upstream response.
   General permission to continue research is not permission to publish the inquiry.
2. Supply a documented, authorized alternative corpus or approved writer with actual
   version evidence and rights-cleared payloads. Impact: requires separate fixture
   engineering/review, license-term verification and unchanged native qualification;
   this audit does not buy, install or run a proprietary writer.
3. Defer RAR-dependent qualification. Impact: affected production remains gated;
   independent eligible work continues, without scope reduction or archiving gates.

B01 remains in its existing `triage` escalation. The report can receive independent
PASS as a bounded audit even though it finds insufficient evidence. That PASS must
not unblock B01, authorize import, or count as an answer to the inquiry. After PASS,
the reviewer/coordinator should post the reviewed commit and these artifact paths
on `t_22299c6f`, verify the remaining G/P/L gaps, and obtain an actual operator
answer before any public contact. Any new human gate must use a real
`needs_input` blocked event, not an initial status or notification wake. This audit
does not create a duplicate gate or request the already-granted read-only research
permission again. Two substantive failed reviews return this same card and then
require escalation; no repair-card chain.

## Verification and reproduction

No executable archive build/test is applicable: only this document and the JSON
matrix change; corpus, expected results, engine, codecs, encryption, GUI and DAG
are unchanged. Qt 6/QML -> CXX-Qt -> Rust -> mature C/C++ remains the direction.
No new runtime compatibility evidence is claimed.

Research scratch is `.b01-provenance-research/` in this task's isolated worktree;
it is not a corpus and is not committed. Sources below are the durable retrieval
handles. Commit/tree/raw-text URLs are pinned; GitHub issue/PR content and API
association envelopes remain mutable. The matrix retains exact excerpts and
SHA-256 of the three nonempty mutable responses used in the narrative. These
response hashes document this retrieval, not a promise future JSON envelopes
will match. The full raw responses contain public metadata and stay in scratch.

Read-only fetch pattern actually used (no clone, blobs or patch endpoint):

```sh
curl --fail --silent --show-error '<source URL below>' -o '.b01-provenance-research/<response>.json'
```

The initial `web_extract` tree/test results were incomplete. Direct `curl` GETs
retrieved complete text/JSON instead; tree completeness and JSON shape were
checked with `jq`. Execution-policy denials for `execute_code` and inline
`python3 -c` were respected: neither was executed, no policy was changed, and
ordinary `curl`, `jq` and the installed citation verifier were used instead.

Validation commands/results, the final commit and exact handoff paths are recorded
on this card's review transition. Required checks are: pinned-tree identity and
size equality for every matrix row; introduction presence and parent absence;
all five independently queried histories; no selected/imported candidate; document
and matrix path/hash/size/missing-code consistency; literal quote/citation checks;
all registered source links returning successful GET; pagination/completeness;
`git diff --check`; and no diff outside the two owned deliverables.

Actual validation outcome before review:

- Matrix/tree/document and introduction/parent checks returned `true`, exit 0.
- The five path-history and citation-ID checks returned `true`, exit 0. An initial
  history-check expression shadowed the part0002 input variable and failed with
  `Cannot index object with number`; distinct variable names fixed the checker.
  Neither source evidence nor matrix data was changed to make that check pass.
- All six empty endpoint responses, the seven-comment count and the three exact
  mutable-response excerpts passed `jq -e` checks; response SHA-256 values matched
  the matrix. The read-only B01 lead's working-file Git blob matched its recorded
  commit (`257c97d16fef7ee7aaf9a43e2db415dc58fbe064`).
- All 23 registered sources were successfully retrieved with `curl --fail`;
  five path-history and two nonempty PR list endpoint HEAD checks returned
  `HTTP/2 200` with no pagination `Link` header. All five tree responses report
  `truncated: false`. This is link/retrieval validation, not legal verification.
- The installed citation verifier returned `citations OK`, exit 0, for 17 cited
  sources with literal evidence. Six uncited ledger entries are deliberately the
  exact empty API observations preserved in the matrix, not fabricated prose
  quotations. No minimum-prose-coverage certification is claimed.
- `git diff --check` and production/config preservation checks returned exit 0;
  staged scope is checked again before committing the two deliverables.

No golden, native result, source URL, generator version or licensing grant was
fabricated to close the gap.

## Sources

[1] https://raw.githubusercontent.com/libarchive/libarchive/60b1d17ddf2fbabc6bca31dae01613d6dbea3cde/COPYING
    > "the actual statements in the files are controlling."
    > "The libarchive distribution as a whole is Copyright by Tim Kientzle"
[2] https://raw.githubusercontent.com/libarchive/libarchive/60b1d17ddf2fbabc6bca31dae01613d6dbea3cde/libarchive/test/test_read_format_rar.c
    > "const char test_txt[] = "test text document\r\n";"
    > "int file1_size = 241647978;"
[3] https://api.github.com/repos/libarchive/libarchive/commits?sha=60b1d17ddf2fbabc6bca31dae01613d6dbea3cde&path=libarchive%2Ftest%2Ftest_read_format_rar.rar.uu&per_page=100
    > "First cut at RAR support, including RARv3."
[4] https://api.github.com/repos/libarchive/libarchive/commits?sha=60b1d17ddf2fbabc6bca31dae01613d6dbea3cde&path=libarchive%2Ftest%2Ftest_read_format_rar_multivolume.part0001.rar.uu&per_page=100
    > "Implement support for reading multivolume RAR archive files."
[5] https://api.github.com/repos/libarchive/libarchive/git/trees/60b1d17ddf2fbabc6bca31dae01613d6dbea3cde?recursive=1
    > ""path": "libarchive/test/test_read_format_rar.rar.uu", "mode": "100644", "type": "blob", "sha": "f197a2983302f5829de2719bdddcf43b8c59b201""
[6] https://api.github.com/repos/libarchive/libarchive/git/commits/099075c11ce9143f7375ed4b1264a10a45a072f9
    > "First cut at RAR support, including RARv3."
[7] https://api.github.com/repos/libarchive/libarchive/git/commits/416694915449219d505531b1096384f3237dd6cc
    > "Implement support for reading multivolume RAR archive files."
[8] https://api.github.com/repos/libarchive/libarchive/issues/2043
    > "The libarchive test harness always extracts these to the truncated source filename, ignoring the name in the `begin` line."
[10] https://api.github.com/repos/libarchive/libarchive/commits?sha=60b1d17ddf2fbabc6bca31dae01613d6dbea3cde&path=libarchive%2Ftest%2Ftest_read_format_rar_multivolume.part0002.rar.uu&per_page=100
    > "Implement support for reading multivolume RAR archive files."
[11] https://api.github.com/repos/libarchive/libarchive/commits?sha=60b1d17ddf2fbabc6bca31dae01613d6dbea3cde&path=libarchive%2Ftest%2Ftest_read_format_rar_multivolume.part0003.rar.uu&per_page=100
    > "Implement support for reading multivolume RAR archive files."
[12] https://api.github.com/repos/libarchive/libarchive/commits?sha=60b1d17ddf2fbabc6bca31dae01613d6dbea3cde&path=libarchive%2Ftest%2Ftest_read_format_rar_multivolume.part0004.rar.uu&per_page=100
    > "Implement support for reading multivolume RAR archive files."
[13] https://api.github.com/repos/libarchive/libarchive/git/trees/099075c11ce9143f7375ed4b1264a10a45a072f9?recursive=1
    > ""sha": "099075c11ce9143f7375ed4b1264a10a45a072f9", "url": "https://api.github.com/repos/libarchive/libarchive/git/trees/099075c11ce9143f7375ed4b1264a10a45a072f9""
[14] https://api.github.com/repos/libarchive/libarchive/git/trees/ab0f070f92105199e8b71d6de9afdbc05667e9d5?recursive=1
    > ""sha": "ab0f070f92105199e8b71d6de9afdbc05667e9d5", "url": "https://api.github.com/repos/libarchive/libarchive/git/trees/ab0f070f92105199e8b71d6de9afdbc05667e9d5""
[15] https://api.github.com/repos/libarchive/libarchive/git/trees/416694915449219d505531b1096384f3237dd6cc?recursive=1
    > ""sha": "416694915449219d505531b1096384f3237dd6cc", "url": "https://api.github.com/repos/libarchive/libarchive/git/trees/416694915449219d505531b1096384f3237dd6cc""
[16] https://api.github.com/repos/libarchive/libarchive/git/trees/7b543b13d813e529364c7b70ae204ce7c0eddfc3?recursive=1
    > ""sha": "7b543b13d813e529364c7b70ae204ce7c0eddfc3", "url": "https://api.github.com/repos/libarchive/libarchive/git/trees/7b543b13d813e529364c7b70ae204ce7c0eddfc3""
[18] https://api.github.com/repos/libarchive/libarchive/commits/416694915449219d505531b1096384f3237dd6cc/pulls?per_page=100
    > "This will enable multivolume support for libarchive. It includes support to read files split using the 'split' program, and also support to read RAR multivolume files."
[21] https://api.github.com/repos/libarchive/libarchive/issues/2/comments?per_page=100
    > "Libunrar does not support v3, which is what I'm looking to support first."
