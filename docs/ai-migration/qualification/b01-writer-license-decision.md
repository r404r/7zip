# B01-L: zero-extra-cost RAR writer feasibility decision

Task `t_1bca5039`; branch `wt/t_1bca5039`; researched 2026-09-11 UTC.
Status: **document for independent review; no eligible RAR writer selected**.

## Controlling decision and result

The operator's latest instruction, delivered during this run and recorded on B01,
was: “仅使用无需授权，无需额外费用之产品”. Its accompanying clarification limits
execution to products requiring no separately acquired commercial/proprietary
permission and zero additional fees; existing open-source license obligations
still apply. This supersedes this card's original purchase/SKU/quote assignment.
**Stop paid acquisition research, proprietary writer preparation and vendor contact.**
Do not ask whether the user would pay again. A free trial or an already-paid seat
is not a workaround for this constraint.

**No verifiable, eligible off-the-shelf writer for the required new RAR corpus was
established in this bounded check. The current tool route cannot generate that
corpus under the new constraint.** This is a feasibility result for the tools
checked, not a universal claim that no RAR-writing implementation exists anywhere,
nor a legal opinion that independent RAR writing is forbidden.

WinRAR/RARLab RAR, including Linux RAR, older 6.24, current releases and all
limited trials, are excluded execution routes. No purchase, proprietary download,
installation, execution, fixture generation or supplier correspondence occurred.
Spending remains zero. Documentation PASS will mean only the evidence and decision
memo passed review, not entitlement acquisition, corpus qualification or release.

## Delta from reviewed B01-W

[B01-W](b01-writer-plan.md), reviewed commit
`11ea1a217ed2fdd801346e1e0b7bd576447e9092`, already compared the mature tools and
specified the eight-case RAR4/RAR5 generation campaign. This memo does not repeat
its command matrix or reopen the user's choice to generate new content.

Its W624/W723 recommendations and paid-seat/trial/acquisition prerequisites are
**superseded as execution recommendations by the latest instruction**, not secretly
satisfied. The historical document is preserved unchanged; its immutable corpus,
provenance, negative-control and native-platform requirements remain relevant.
The new payload CC0-1.0 and new standalone generator MIT grants remain proposed,
not accepted by the latest message. No codec implementation is commissioned.

New evidence here: a direct recheck of eligible tools' advertised write formats,
libarchive's separate library read/write lists and file-level license conditions,
rarfile's explicit refusal to provide RAR creation, and the fork's actual input-only
registration macros. These establish a precise writer capability gap rather than
another request for an unspecified paid entitlement.

## Bounded eligibility and capability check

Read-only project documentation was checked; no package was installed or executed.
The additional broad discovery query `open source RAR archive creation writer
libarchive rarfile` returned mainly libarchive forks and rarfile documentation;
forks/search snippets were not treated as independent writer evidence. The check
stops at the already-reviewed mature candidates plus that concrete Python lead.
A candidate would need both an applicable existing license and actual documented
RAR writing, including the required compression and multipart features, before
execution qualification could even begin.

| Tool | Existing terms and actual documented capability | Disposition |
| --- | --- | --- |
| 7-Zip / retained fork | Upstream says “You don't need to register or pay for 7-Zip.” Its packing list is 7z, XZ, BZIP2, GZIP, TAR, ZIP and WIM; RAR is explicitly in “Unpacking only”. LGPL/BSD and unRAR restrictions remain applicable.[10] | Eligible no-fee tool for its supported operations, **not a RAR writer**. Keep the retained reader; do not add Linux RAR. |
| libarchive / bsdtar | Project labels its license New BSD and distinguishes RAR reading from its non-RAR write list.[9] Library README includes RAR/RAR5 in reads but not in the full create list, which also includes 7-Zip, ZIPX and WARC beyond the shorter homepage list.[13] COPYING permits redistribution/use subject to conditions and says individual file statements control.[14] | No separately purchased writer license identified; **no documented RAR creation**. Do not confuse format conversion or RAR reading with RAR output. |
| Python rarfile | “This is Python module for RAR archive reading.” / “Licensed under ISC license.”[12] Its FAQ asks “Will it support creating RAR archives?” and answers “No.”[11] | The wrapper's ISC license does not add an encoder or license its external backends. Reading stored members or copying already-compressed entries into temporary archives is not creation of the required original compressed corpus.[11][12] |
| RARLab WinRAR / RAR / UnRAR workaround | RAR EULA allows a maximum 40-day test and specifically grants archive distribution without additional royalties to license owners.[2] | Excluded by the operator, not pending purchase approval. No trial reset, existing-seat exception, paid acquisition or inference of trial output rights. UnRAR is not selected as a writer; B01-W's reader/reverse-engineering distinction remains. |

The rarfile FAQ's explanation about RARLab's intentions is the project's wording,
not an independent legal conclusion.[11] No new compression implementation,
reverse-engineered UnRAR encoder, ad-hoc stored-only RAR container generator,
ZIP renamed `.rar`, or raw file splitting is substituted for a qualified writer.
Even an eligible stored-only experiment would not establish the compressed,
solid, method/filter and native RAR multipart requirements.

### Fork-specific evidence, not a platform-name inference

At starting HEAD `e242aa9f116973ed69be9f36329f115955ccc5a4`:

- `CPP/7zip/Archive/Rar/RarHandler.cpp:1768-1773` registers `Rar` with
  `REGISTER_ARC_I`; `Rar5Handler.cpp:3399-3404` does likewise for `Rar5`.
- `CPP/7zip/Common/RegisterArc.h:53-62` expands that macro to `CreateArc, NULL`
  in the input/output factory positions; lines 68-71 separately define the
  input/output registration using `CreateArcOut`. These are built-in readers,
  not evidence of a RARLab Linux writer dependency or owned commercial license.
- `DOC/License.txt:10,18-19` assigns `CPP/7zip/Compress/Rar*` GNU LGPL with the
  unRAR restriction, requiring both. No-fee use is not “no license obligations”.

Qt 6/QML -> CXX-Qt -> Rust -> retained mature C/C++ remains unchanged. No engine,
FFI, ownership, lifetime, error, filesystem, GUI or codec boundary is altered.

## Compatibility gaps and what stays gated

Without an eligible writer or separately approved, rights-cleared existing corpus,
**all eight proposed B01-W rows remain unqualified**: R4-STORE, R4-LZ, R4-PPM,
R4-VOL, R4-OLDVOL, R5-STORE, R5-LZ-SOLID and R5-VOL. No bytes or new runtime evidence
were produced. Specifically missing are original classic/modern RAR compressed
and stored cases, solid behavior, actual native multipart headers and old/new
volume naming, plus their missing-volume and corruption controls.

B01-W's other gaps also remain: Rar1/Rar2, Rar3 method transitions and filters,
password/encryption, Unicode and fork code pages, timestamps/permissions/symlinks,
large files, recovery/SFX, unsupported RAR methods, nested/probing chains, and
list/create numeric observations. Non-RAR formats, GUI and desktop qualification
are not closed by this memo either. A missing corpus is **unqualified testing**,
not an assertion the retained reader does not support the format.

Native Windows/Linux/macOS oracle runs, immutable archive and every-volume hashes,
actual writer/version provenance, complete payload rights and numeric/raw error
captures plus negative controls remain required under original B01. Prior B01
partial CI is not rerun or promoted to full PASS. No goldens or acceptance change.

## Exact next decision, without another payment question

Recommend asking the operator on original B01 whether to authorize **only a bounded
read-only assessment of zero-cost, already-existing RAR fixtures with explicit
payload/container redistribution rights and recorded writer/version provenance**.
This would be a new direction requiring approval, not a silent switch from the
chosen new-generation route. Do not import even a promising fixture on this memo.

Options for the existing human gate (all zero spending):

1. **Recommended: approve that bounded existing-fixture assessment.** Require
   immutable source revision/path, exact archive and payload terms, authorship,
   actual generator/version records, complete-volume provenance and notices before
   proposing import. Cost impact: no product fees; additional evidence and native
   testing work. Coverage is unknown until proven; no assurance such fixtures exist.
2. **Keep the new-generation requirement and defer affected RAR qualification.**
   No paid/trial alternative or codec project is started. Impact: no new RAR corpus
   with the verified tools; B01 and affected dependents remain gated while independent
   eligible work continues. This is the default absent further approval.
3. **Request an explicit human-reviewed scope adjustment proposal.** Name every
   omitted capability and retained production block before approving any revised
   acceptance/DAG. Impact: potentially narrower delivery, not compatibility parity;
   no adjustment is performed here and no automatic acceptance reduction is allowed.

[B01-P](b01-provenance.md) and [its matrix](b01-provenance.json) already found
missing generator/version, payload provenance and exact applicable terms for the
previous libarchive candidates. They are not now approved just because the project
is open source or its test files are publicly downloadable. Do not repeat the
same audit without genuinely new evidence, contact a supplier/upstream, or create
a duplicate generation card. Original B01 `t_22299c6f` retains its existing typed
`needs_input` escalation and current `triage` state; this author does not unblock,
archive or re-block it. Reviewer should post the approved findings and these
non-purchase options there after independent PASS.

## Retrieval and validation evidence

Research interval: 2026-09-11 UTC; final capability sources were fetched by
`curl -fLsS --max-time 40 <source-url> -o <scratch-file>` and converted from HTML
without scripts by local Python `HTMLParser`. Sources are mutable snapshots, not
immutable package identities. Raw text was never executed. These are SHA-256 of
retrieved document bytes, **not writer/package/fixture hashes**:

| Source | Scratch snapshot | SHA-256 |
| --- | --- | --- |
| [9] | `libarchive.html` | `6d374ad773e834962527629511c35c3f9797a079c27d5908d1008e7e5cb68abd` |
| [10] | `7zip.html` | `db616b63d363d47256fade9620341dfcc6ffba09658795c09552baf5c0964fde` |
| [11] | `rarfile-faq.html` | `df0086eaf3a2f55ef3d9f07ef00cff0d50267ced43f04d349c66b2c0451773ec` |
| [12] | `rarfile.html` | `4559bbe4f79c4ee77a25592828945817fb623d801c9a57faf46e534047491730` |
| [13] | `libarchive-readme.txt` | `158527b45cc55cce474530d54e8c7e1a6fd3f57c6cf0967777421c07ea34398d` |
| [14] | `libarchive-copying.txt` | `30e556b3959e3985d66efefec5eaac51d4995053caa1d3cffe6eb916f146f229` |

Before the override, read-only vendor EULA/FAQ/contact and public checkout HTML
were retrieved under the original scope. No order form was submitted, identity or
payment data supplied, terms accepted, or email sent. That abandoned procurement
material is not an actionable quote or recommendation and is not committed;
checkout HTML may contain server-generated session/network metadata and must not
be attached or published. The existing EULA is cited solely to explain exclusion,
not to prepare trial/paid execution. No further procurement retrieval followed
the override. Initial `web_extract` was incomplete; direct text GETs supplied the
actual evidence. The guessed rarfile `/en/latest/` path returned HTTP 404; the
project's root and FAQ pages succeeded. A local `python3 -c` inspection command
was denied by policy; no configuration was changed.

Both AGENTS.md files were read. Source branch verified as
`ai/migration-bootstrap-20260911`, assigned branch `wt/t_1bca5039`, and reviewed
parent commit was already an ancestor; no merge/cherry-pick needed. Only this
owned document is committed. Scratch `.b01-license-research/` remains untracked.
Executable builds/archive tests are not applicable: this is documentation-only
feasibility research with no selected writer or runtime modifications. Actual
checks include literal quote matching, citation verification, source snapshot
hashes, local links/code paths, case IDs against B01-W, preserved protected trees,
and `git diff --check`; exact results and final commit are in the review handoff.
This is not a native compatibility test result. Same-card independent review is
required; CHANGES returns this card and two substantive failures escalate.

## Sources

[2] https://www.rarlab.com/license.htm — license
    > "anyone may use the software during a test period of a maximum of 40 days at no charge."
    > "Owners of a license may use their copies of the software to produce archives and self-extracting archives and to distribute those archives free of any additional royalties."
[9] https://www.libarchive.org — libarchive
    > "Writes tar, pax, cpio, zip, xar, ar, ISO, mtree, and shar archives."
[10] https://www.7-zip.org — 7zip
    > "You don't need to register or pay for 7-Zip."
    > "Packing / unpacking: 7z, XZ, BZIP2, GZIP, TAR, ZIP and WIM"
[11] https://rarfile.readthedocs.io/faq.html — rarfile-faq
    > "Will it support creating RAR archives?"
    > "No. RARLAB is not interested in RAR becoming open format and specifically discourages writing RAR creation software."
[12] https://rarfile.readthedocs.io — rarfile
    > "This is Python module for RAR archive reading."
    > "Licensed under ISC license."
[13] https://raw.githubusercontent.com/libarchive/libarchive/master/README.md — libarchive-readme
    > "RAR and RAR 5.0 archives (with some limitations due to RAR's proprietary status)"
    > "The library can create archives in any of the following formats:"
[14] https://raw.githubusercontent.com/libarchive/libarchive/master/COPYING — libarchive-copying
    > "the actual statements in the files are controlling."
    > "Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:"
