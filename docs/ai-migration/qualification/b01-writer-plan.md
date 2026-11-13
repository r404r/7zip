# B01-W: writer selection and self-owned corpus generation contract

Task `t_e1e04fc6`; branch `wt/t_e1e04fc6`; research date 2026-09-11 UTC.
Status: **proposal only; no writer acquired, installed or executed, no corpus generated**.

## Decision and authority

Recommend a **single licensed, isolated native Windows x64 generation station**
using the English WinRAR 6.24 distribution's console `Rar.exe`, conditionally on
operator approval of the exact scope below and successful acquisition/preflight.
This is the bounded candidate that can address both classic RAR4 and RAR5 writing;
current RAR 7.23 is the safer modern alternative but cannot replace classic writing.
The 6.x command reference describes `-ma4` and `-ma5`, while the official 7.00
change explicitly removes creation in RAR 4.x format.[11][3]
The retrieved command reference identifies itself as **RAR 6.02**, not 6.24, and
is a pinned third-party text mirror, not a vendor-authenticated 6.24 manual.[11]
Therefore the exact 6.24 bundled manual/help check is a mandatory pre-execution
checkpoint, not a claimed completed verification.

User decisions on `t_22299c6f` selected option 2 and then explicitly clarified
“生成新语料”: screen writers/terms and propose scope, then generate original
payloads. Do not ask the user to select that path again. This does **not** authorize
purchase, new proprietary terms, writer installation/execution, public upstream
contact, importing unknown fixtures, or weakening B01 acceptance.

Reviewed parent `34ba13bd440647ded178e07c6b08cd53e15b239b` is already an ancestor
of this clean task's starting HEAD `95412e657feea601fe52c4d6039908b402e4aac5`.
Both source and task `AGENTS.md` were read; source is on
`ai/migration-bootstrap-20260911`. No cherry-pick/merge was needed.
Read [B01-P report](b01-provenance.md) and [its matrix](b01-provenance.json).
B01 implementation commit `9d01d5069f5b117aa5c69dd5cc62f090869d7650` was inspected
read-only with `git show` (manifest and qualification report), not integrated:
it remains unreviewed. Its `schema_version=1` field names are reused below.

B01-P's five archives are still not selected. These will be new fixtures with
new names, not byte-equivalent recreations of the libarchive archives. The
large HTML/text payloads, original four-volume layout, symlink assertions and
historical codec transitions in that family are not automatically replaced by
small synthetic files. No B01 goldens, DAG, source, codec or encryption changes
are made. Qt 6/QML -> CXX-Qt -> Rust -> mature C/C++ remains unchanged.

## Candidate comparison and acquisition pins

| Candidate | Evidence-backed capabilities | Terms and proposed disposition |
| --- | --- | --- |
| WinRAR 6.24 English x64, console `Rar.exe` | Official change history has a 6.24 section; pinned winget metadata identifies the exact distribution. 6.x manual documents RAR4/RAR5, store `-m0`, compression levels `-m1` through `-m5`, solid/non-solid, multipart and RAR4 old-style volume names.[7][6][11] | Proprietary; recommended only for this bounded isolated writer run after paid-seat scope and old-version risk approval. Actual 6.24 switches/internal build must be captured, not inferred from winget's product version. |
| RAR for Linux x64 7.23 | Official current CLI trial distribution; RAR5 writing, not new RAR4 writing. Vendor advertises multivolume creation.[1][3][10] | Modern-only alternative after separate use approval; cannot close classic gaps. No reason to install on all three oracle runners. |
| WinRAR x64 7.23 / RAR macOS ARM or x64 7.23 | Official current GUI/CLI or CLI trial packages.[1] Same 7.x RAR4-creation limit.[3] | Alternatives if generation host changes, not extra required writer installations; recheck seat/network scope. |
| libarchive/bsdtar (official page lists 3.8.9) | New BSD library; documented write formats include tar/pax/cpio/zip/xar/ar/ISO/mtree/shar, while RAR is in the read list.[5] | Prefer for future supported formats, **not a RAR writer**. No download selected here, and no claim that all third-party fixtures inherit its source license. |
| retained 7-Zip / upstream 26.03 | RAR is unpacking-only; 7z/XZ/BZIP2/GZIP/TAR/ZIP/WIM writing is documented; free commercial use, mostly LGPL with other restrictions.[4] | Already useful for split 7z/control cases, **not RAR multipart generation** and not a permissive-license RAR-writing substitute. |
| UnRAR / modified UnRAR | EULA explicitly separates UnRAR components and prohibits using UnRAR source/binary to recreate the proprietary RAR compression algorithm without permission.[2] | Reader route only; no codec-writing workaround or reverse engineering. |

No viable permissively licensed compressed RAR writer was established in this
bounded comparison. This is not a proof that no tool exists anywhere; unsupported
writers must not be selected based merely on their ability to open `.rar` files.

### W624: primary candidate identity (not downloaded)

- Product: WinRAR 6.24, English Windows x64 distribution; winget package version
  `6.24.0`, architecture `x64`, locale `en-US`.[6]
- Exact vendor URL: `https://www.rarlab.com/rar/winrar-x64-624.exe`.[6]
- Expected **installer** SHA-256 from the pinned Microsoft winget manifest:
  `794481DBBC9009A2565726FB5B4A4AB2FE216FF9EDBB08951548EE765DE9B4A6`.[6]
  This is a published expected digest, **not locally measured downloaded bytes**,
  not a vendor signature and not `Rar.exe`'s hash.
- Metadata pin: `microsoft/winget-pkgs` commit
  `67707b1e6db26d50df506f7b67f4369874facbb0`, path
  `manifests/r/RARLab/WinRAR/6.24.0/RARLab.WinRAR.installer.yaml`;
  retrieved tree reports blob `fbaa8d29f32b9c6a6dea2110538d431a29acf344`.[6]
- Read-only HEAD probe returned HTTP 200, content-length `3589048`, Last-Modified
  `Tue, 03 Oct 2023 07:52:28 GMT`. Those are mutable server observations, not a
  hash verification or a guarantee of future availability.
- Later authorized acquisition must use only the exact vendor URL; verify download
  hash against the pin, inspect Authenticode status/signer/timestamp natively,
  and retain package, bundled `license.txt`/manual/acknowledgments digests privately.
  Stop on hash/signature/version/terms mismatch; never substitute another mirror,
  auto-upgrade, or suppress a security finding. Independently verify the actual
  package layout before installing; this proposal supplies no silent installer
  command and does not authorize shell integration or elevated system changes.

### W723: modern-only alternative identity (not downloaded)

The official download page links `https://www.rarlab.com/rar/rarlinux-x64-723.tar.gz`
for **RAR for Linux x64 7.23**, command line only, Trial.[1]
Read-only HEAD returned HTTP 200, length `746868`, Last-Modified
`Sat, 27 Jun 2026 11:36:23 GMT`. The page also links
`winrar-x64-723.exe`, `rarmacos-arm-723.tar.gz` and `rarmacos-x64-723.tar.gz` under
`https://www.rarlab.com/rar/`.[1]
No vendor-published immutable hash for those packages was established here.
A versioned URL is not content-addressed: this alternative needs a verified
acquisition digest/signature or approved equivalent authenticity evidence before
running. Do not invent a SHA-256. Only the W624 command matrix below is proposed
for execution; W723 selection requires matching its bundled manual and a revised
RAR5-only generation record, not silently running the W624 matrix.

## License applicability and execution gate

The live EULA is not a frozen 6.24 license. Save/hash/compare the bundled version
before accepting it; material differences go back to the operator. Exact relevant
live clauses follow (not a legal opinion):

- Clause 2: “anyone may use the software during a test period of a maximum of
  40 days at no charge”; afterward a license must be purchased to continue.[2]
- Clause 6: “Business users require one license per computer or mobile device on
  which the software is installed.” Network use additionally requires a copy for
  each separate client where installed, used or accessed, even at different times.[2]
- Clause 6 grants licensed use “for any legal purpose”; neither this clause nor
  the inspected EULA supplies a special CI-runner exemption.[2]
- Clause 7: “Owners of a license may use their copies of the software to produce
  archives and self-extracting archives and to distribute those archives free of
  any additional royalties.”[2]
- Clause 3.1: “Nobody may distribute separate parts of the package, with the
  exception of the UnRAR components, without written permission.” Clause 3.2
  disallows bundling the unlicensed trial inside another software package without
  written permission; 3.3 prohibits bundling the installer.[2]
- Clause 12: “Installing and using the software signifies acceptance of these
  terms and conditions of the license.” Clause 10 bars specified unauthorized
  cloning/reverse engineering, including recreating RAR compression.[2]

Interpretation for approval: command-line unattended synthetic archive generation
on a properly licensed station appears consistent with general lawful-use rights,
**not an explicit vendor attestation for this automation/network deployment**.
The operator must establish ownership/entitlement, who accesses the station, and
whether a network/client license is needed. Do not claim a single seat covers
arbitrary remote workers, containers, or hosted CI. No license key or invoice
with personal details may be committed or printed in task logs.

Separate rights tracks:

1. **Writer binary:** remains proprietary. Do not commit `Rar.exe`, installer,
   license key, SFX module, or distribute a writer-equipped CI/container image.
   Keep approved install/acquisition evidence in operator-controlled private
   storage; commit only non-secret hashes/version/provenance and authorized
   excerpts/links. Native oracle runners consume archives, not this writer.
2. **Archive output:** clause 7 supports royalty-free distribution for license
   owners, but it does not license another person's payload.[2] Recommend a paid
   or already-owned applicable seat rather than infer that trial-created fixtures
   have the same output grant. No trial reset/reinstall cycle or expired trial use.
3. **New synthetic content and generator:** propose original numeric/ASCII data
   with a new, explicit **CC0-1.0 dedication for fixture payloads, names and generated
   container contribution to the extent rights exist**, and **MIT for the newly
   authored standalone generator**. These are proposed rights-holder grants, not
   existing grants inferred from the EULA, adjacent tests or triviality. Operator
   must confirm authority and approve the grant/notice text before corpus import.
   Preserve all existing engine/repository licenses; do not relicense existing code.
   Tester must record authorship, generator source commit/blob/SHA-256 and explicit
   notices separately. No copied HTML, executable sample, public issue attachment,
   user archive or unidentified seeded corpus is permitted.

### Concrete operator options (unresolved; not a new path selection)

1. **Recommended:** authorize W624 only on one named native Windows x64 isolated
   station for one bounded generation campaign, with an already-owned applicable
   paid license and verified 6.24 entitlement, including unattended access scope;
   approve old-version containment and the proposed synthetic-content/source grants.
   Cost ceiling **USD 0 incremental spending**, no purchase allowed. If no suitable
   entitlement exists, return a current vendor quote and exact tax/seat/version
   terms for a separately approved budget; do not buy automatically. Impact:
   potentially fills classic plus RAR5 cases, but obsolete writer risk and all
   downstream runtime/coverage gates remain.
2. Authorize W723 on one already-licensed Linux x64 station for modern RAR5 only
   under the same USD 0 incremental limit, content grants and no-redistribution
   rule. Impact: avoids choosing 6.24 but **classic RAR remains unqualified**;
   no acceptance reduction and no implicit approval of a second station.
3. Defer proprietary execution while supplying a verifiable existing licensed
   installation/entitlement and desired grant text. Cost USD 0; impact: no new
   RAR corpus yet, B01 and affected descendants remain gated; independent work
   continues. This does not reopen or substitute public upstream inquiry.

No authoritative payable quote was obtained: the attempted `/price.html` and
`/pricelist.html` routes failed, and the old `/buy/index_shop.php` redirects to
`https://www.win-rar.com/` rather than a checkout quote. Search snippets and homepage
price metadata are not an approved purchase price. Spending stays at zero.

B01 already has a real `needs_input` escalation and is `triage`; do not create a
duplicate generation/gate card or unblock it on proposal PASS. The reviewer posts
the reviewed document/commit and these exact options to B01; coordinator records
actual operator resolution there. If a new execution gate must be surfaced, use a
real `kanban_block(kind="needs_input")` event on the owning B01 work, not only an
initial blocked status. This documentation card may finish review independently
with the execution gate explicitly unresolved. Notify+wake is not approval.

## Proposed bounded generation contract — tester executes later, not here

### Environment and deterministic source data

W624 campaign: native Windows x64, dedicated disposable VM, non-administrator
runtime account, fixed local NTFS work disk, UTC timezone and English UTF-8 capture.
Record exact OS build, VM image identity, CPU architecture, filesystem, code pages,
locale/timezone, Python executable/version/hash, writer package/`Rar.exe` hashes,
full help/banner and manual hashes. No Wine, emulator or Linux cross-build counts
as Windows evidence. Disable network access during writer execution, no shared
host folders, credentials, browser data, user files, or automatic shell integration.
A security scan is mandatory; policy denial is a stop, not a workaround invitation.
Old-version vulnerabilities are real: official 7.23 notes fixes to recovery-volume
heap overflow and symlink extraction, and other 7.x entries report prior extraction
issues.[3] W624 only reads our controlled local payloads; no writer extraction,
repair, SFX, recovery volumes or untrusted archives. This reduces risk, not a proof
that an old binary is safe.

The later tester authors a new test-only `generate_rar.py` in the original B01
scope (filename is **proposed, does not exist in this card**). Use CPython stdlib
only, reviewed original source and the grants above. Do not copy the mirrored
manual's source or any downloaded executable code. Input recipe v1:

| Relative member | Exact byte recipe | Purpose |
| --- | --- | --- |
| `empty.bin` | empty byte string | empty member |
| `sequence.bin` | `bytes(range(256)) * 768` | store/volume crossing |
| `text.txt` | `(b"B01 synthetic sequence 0123456789 ABCDEF\n" * 4096)` | compressible original ASCII, PPM candidate |
| `copy.txt` | same bytes as `text.txt`, distinct member | solid inter-file repetition |
| `nested/item.bin` | `bytes(range(256)) * 16` | relative directory path |

No random input, symlinks, hardlinks, reserved paths, Unicode, ADS, executable,
password or borrowed text in this first bounded campaign. Set all input files'
modification timestamps to epoch `1700000000`, create/access times to the same
instant where supported; preserve exact actual metadata separately. All names
ASCII, relative, unique; generate files using exclusive-create and reject any
pre-existing source/output directory. Record member size and full SHA-256, never
tail-only hashes. No payload bytes are generated in B01-W.

Cap the campaign at 16 successful authoring invocations (8 cases, one independent
repeat each), 32 volumes per invocation, 16 MiB aggregate source data, 64 MiB
output per invocation, 512 MiB scratch total, 512 MiB process-tree memory and
120 seconds wall time per command. Kill the isolated process tree on timeout,
retain failure evidence; do not retry unboundedly or silently raise budgets.
These are design limits, not measured consumption. Capture stdout/stderr as raw
bytes (Base64 in JSON), exact argv/cwd, environment allowlist, exit, duration and
resource-limit events. stdin is EOF, not an interactive prompt loop.

### Preflight and exact proposed argv

After actual approval and safe installation, bind `Rar.exe` to its absolute path;
never resolve an arbitrary PATH executable. Capture a no-argument help invocation,
file version resources, executable SHA-256 and bundled manual before any creation.
If actual banner is not the approved 6.24 build or any proposed switch is missing
or has different semantics, stop and reconcile with reviewer. Command syntax
below is supported by the pinned **6.02** manual as a planning aid only.[11]

For each row launch `Rar.exe` from a fresh source root using a subprocess argument
array, not an interpolated shell string. Common argv prefix is exactly:

```text
Rar.exe a -cfg- -ma4 -md4m -mt1 -tsm1 -tsc- -tsa-
```

For RAR5 rows replace only `-ma4` with `-ma5`. Append the row's switches, then its
new absolute output archive path, then members in the displayed order. `ALL` is
expanded by the harness to these literal arguments, not passed to RAR and not a
glob/listfile: `empty.bin sequence.bin text.txt copy.txt nested/item.bin`.
No password, `-y`, overwrite, delete/move, config file, recursion, SFX or repair
switch. Clear inherited `RAR` and `RARINISWITCHES`; common `-cfg-` ignores 6.x
configuration defaults.[11] Never update an existing archive: `-ma` does not
change the format of an existing archive according to the 6.x manual.[11]

| ID | Format | Additional switches | New output basename | Members | Intended observation, not a PASS |
| --- | --- | --- | --- | --- | --- |
| R4-STORE | RAR4 | `-m0 -s-` | `r4-store.rar` | ALL | classic container/store |
| R4-LZ | RAR4 | `-m3 -mc- -s-` | `r4-lz.rar` | ALL | classic general compression; disable optional modules |
| R4-PPM | RAR4 | `-m5 -mc10:16t+ -s-` | `r4-ppm.rar` | `text.txt copy.txt` | forced text/PPM candidate, order 10 and 16 MB requested |
| R4-VOL | RAR4 | `-m0 -s- -v65536b` | `r4-vol.rar` | ALL | RAR-native part-number volumes, not raw split |
| R4-OLDVOL | RAR4 | `-m0 -s- -v65536b -vn` | `r4-oldvol.rar` | ALL | `.rar`, `.r00` naming family |
| R5-STORE | RAR5 | `-m0 -s-` | `r5-store.rar` | ALL | RAR5 container/store |
| R5-LZ-SOLID | RAR5 | `-m3 -mc- -s` | `r5-solid.rar` | ALL | modern compressed solid set |
| R5-VOL | RAR5 | `-m0 -s- -v65536b` | `r5-vol.rar` | ALL | modern native multipart |

The 6.x manual documents `-mc-` disabling optional modules, `t+` forcing text
compression, `-md4m` dictionary selection, `-mt1` recommended thread maximum,
`-tsm1` second precision and `-v65536b` explicit byte units.[11]
It documents `-vn` for RAR4 only; do not apply it to RAR5.[11]
Do not promise one compression switch proves every internal method/filter, that
the chosen dictionary will be retained for small inputs, or that the requested
thread limit is a hard scheduler limit; inspect actual reader properties/events.

Require at least two volumes for each volume row and record actual ordered names,
count, lengths and per-part digest; do not predict four parts, pad/rename to mimic
libarchive, or treat byte concatenation as a RAR volume writer. Generate a second
copy in a different fresh directory with identical metadata/argv. If archive
hashes differ, preserve both logs and characterize why; deterministic input does
not imply byte-deterministic writer output. Choose immutable approved first-run
bytes only after review, never regenerate fixtures during CI.

Validate RAR4 signature `52 61 72 21 1A 07 00` versus RAR5 signature
`52 61 72 21 1A 07 01 00`, and native handler/method selection separately; format
signatures alone do not establish method coverage.[9]
Legacy `CPP/7zip/Archive/Rar/RarHandler.cpp:1688-1700` selects Rar1 for unpack
version below 20, Rar2 below 29, Rar3 otherwise through 40. A 6.24 RAR4 archive
is **not evidence of Rar1 or Rar2**, nor a recreation of all classic RAR3 filters.

## B01 manifest integration: retain schema_version=1

Do not insert pending/null-hash proposal rows into B01's accepted fixture manifest.
After generation and actual qualification, add new fixture records using its
existing structure:

- Top level `schema_version: 1`, `fixtures`, `payload`, `authoring`, `qualification`.
- Each record keeps `id`, `files: [{path, sha256}]`, `format`, `method`, `generator`,
  `version`, `license`, `provenance: {recipe, source, base}`, `operations`, and
  `native_oracle_reports`. Use `generator` for actual RAR product, `version` for
  real captured version, not Python/reader version. `files` must list **every**
  volume with actual digest, not only the first part. Keep casing conventions
  consistent with B01's implementation; archive generation labels are distinct
  from registry handler identifiers `Rar` and `Rar5`.
- `provenance.recipe` stores exact argv per invocation; `source` identifies the
  committed new generator source, `base` binds derivatives to immutable parent
  fixture IDs/digests. Store additional structured non-secret detail in a linked
  generation record (also `schema_version=1`) rather than changing existing field
  types or substituting narrative for hashes. Explicitly extend/test B01 validators
  for the linked record; this card does not silently declare new fields supported.
- Linked record must include source commit/blob/SHA-256, package URL/pin/actual
  digest, actual executable digest and help output, bundled terms/manual hashes,
  approval reference (no key/PII), payload rights/grant/notice paths, complete
  ordered member paths/bytesizes/digests and times, actual archive method/header
  properties, volume order/count, command raw results and resource limits,
  full native report paths/digests and CI URL/exact head/toolchains.
- `operations` describes actual list/test/extract scope; create rejection belongs
  to operation evidence, not a claim the retained engine can write RAR.
  `native_oracle_reports` points to real per-platform new captures only after they
  exist. `qualification` stays bounded; `production_release=false` remains until
  all required B01 and downstream gates are independently satisfied.

Immutable strategy: commit only rights-cleared archive bytes plus provenance and
notices under original B01 scope, marked binary/non-text, or use an approved
content-addressed retrievable store with rights-cleared immutable hashes. Do not
rely on a task scratch directory, mutable download URL or expiring CI artifact
as the only corpus copy. No proprietary writer package goes in that corpus.

## Native qualification and negative controls (later tester obligations)

Run unchanged native legacy Alone2 and the B01 disposable test-only observer on
**each of Windows MSVC x64, Linux GCC x64, macOS Apple clang arm64**, with exact
commit, compiler, binaries/digests, OS and build logs. Use B01's native workflow
and reviewed ancestor discipline; do not count W624's generation as an oracle run
or run a substituted system 7z. Its existing `capture.py`/`numeric_capture.py`
need additive case coverage before these commands can qualify the new matrix.
No full B01 PASS is inferred from existing historical CI.

Per fixture, capture/repeat in clean bounded scratch:

```text
<legacy> l -slt <first-or-single-volume>
<legacy> t <first-or-single-volume>
<legacy> x <first-or-single-volume> -o<fresh-output-directory>
<legacy> a -trar <new-abs-output.rar> <controlled-source-file>
```

Use EOF stdin, the same process-tree limits, exact argv/raw exit/stdout/stderr;
no `-y` to hide prompts. Capture all extracted members, including failure side
effects, full hashes/sizes and listing order. Create probe is an expected
**observation of retained-engine refusal**, not authorization to synthesize an
error enum; observe actual result on every native platform. Do not automatically
open extracted content. Add B01 observer test/extract runs against uninstrumented
controls and record actual HRESULT bits, NOperationResult, CArcErrorInfo definedness,
flags and ordered callbacks at available levels. List/create numeric gaps remain
explicit until actually instrumented/qualified; never derive them from CLI exit.

For all three multipart rows, keep a complete set and independently test copies
with missing first, missing middle, missing last, and non-first entrypoint. Never
delete an approved fixture to simulate loss; build scratch subsets with recorded
membership. Preserve requested versus resolved volume names and actual outcomes.
Additional derivative/probing recipes, each with separate ID/base hashes:

- Rename copies of each single archive to `.dat` without changing bytes; record
  probing handler and operation results rather than assume the extension decides.
- Put the committed B01 `store.zip` bytes (verified against its own manifest) into
  a separately approved outer fixture only in a later additive campaign; the
  eight-row budget above does not secretly include extra nested generation.
  Until then general/nested RAR chains remain explicitly unqualified.
- Truncation controls for R4-STORE/R5-STORE: first 16 bytes and all but last 16
  bytes. Record actual errors; neither is pre-labelled `Headers Error`.
- Header integrity control: on a scratch copy flip one bit of the first header
  CRC at offset 7 (RAR4) or 8 (RAR5), after asserting signature and non-SFX layout.
  Record offset, old/new byte, base and derived digest; retain actual error label.
- Data integrity control: on a stored archive locate the unique full
  `sequence.bin` byte run, assert it occurs once and is a stored member data
  span from header/listing evidence, then flip its first byte without changing
  checksum fields. If placement cannot be established, stop this recipe rather
  than guess an offset. Retain actual CRC/data/header distinctions from oracle.
- Unsupported-method differentiation: retain B01's immutable `unsupported.zip`
  control. No documented writer switch creates an unsupported RAR method here;
  **RAR-specific unsupported-method rejection stays unqualified**, not covered
  by randomly damaged headers or by ZIP evidence.

Comparator negative controls must fail after independently changing a temporary
copy of (a) one archive/volume byte, (b) volume membership/order, (c) one extracted
member hash, (d) raw exit/diagnostic observation, (e) actual HRESULT bits,
(f) NOperationResult, (g) CArcErrorInfo definedness/flags, (h) native platform or
handler registration, or (i) writer/payload provenance binding. The unchanged
control must pass; a detector that also rejects unchanged evidence is invalid.
Keep raw reports immutable; freeze new per-platform captures additively only after
repeat equality and independent review. Run original M1 and existing B01 frozen
comparisons without updating their expected values. A semantic conflict goes to
the owning card's actual human gate, not changed goldens.

### Required gaps that this proposal does not close

Every R4/R5 row is **unqualified pending execution**, even where writing support
is documented. Beyond those rows, the following stay required/unqualified where
B01 requires them: Rar1/Rar2 streams; Rar3 PPM/LZ transitions and audio/RGB/delta/x86
filters; classic compressed solid/multipart variants; all compression levels and
dictionary boundaries; old/new RAR encryption and password behavior; Unicode and
this fork's filename code pages; symlinks/permissions/timestamp fidelity; >4 GiB
members; recovery records/volumes and SFX; corrupted compressed streams and RAR
unsupported methods; arbitrary automatic nested/probing chains; external 7z/CAB/
ISO/WIM and the other inventory gaps; list/create numeric observation; GUI and
desktop integration. An intended PPM switch is not proof the emitted stream
exercises every PPM path. New small synthetic volumes do not certify the large
upstream conversion testcase. No gap is silently labelled unsupported by the
engine or removed from B01 acceptance.

## Review and validation record

Only this document is a deliverable; the in-document candidate/case matrices are
the authoritative proposal. No optional plan JSON is used, so there is no second
matrix to drift. Executable archive builds/tests are not applicable to this card:
no production or test execution changes, archive acquisition or generation are
allowed. All command blocks above are **planned**, not captured runtime output.

Read-only research scratch: `.b01-writer-research/` under this isolated worktree.
Raw HTML/manual/manifest are evidence only and were never executed. Source 11 is
a third-party 6.02 manual mirror with immutable raw revision, explicitly not an
approved writer download. Official vendor pages are mutable; record the retrieved
snapshots below and recheck bundled terms before execution. These are SHA-256 of
research text bytes, not archives or writer binaries:

| Snapshot | SHA-256 |
| --- | --- |
| `download.html` | `e82a77be205a7591c0b13f751a51e677bada743ccd744e72ccf5f4ab6e8ccfec` |
| `license.html` | `370d2961ca494ba887baeee544253bd6c0e1185d5acbed3b62623af3b428668c` |
| `changes.html` | `eb152f5b8cda112631b0153a1ed3a75836ac79992f7933d0c3f99136c5ad022e` |
| `installer.yaml` | `f82cbbcf215bd34edbf327c6a773e8fa681f038fb87c8f52e7f9bd6a93cc127c` |
| `rar-manual.txt` | `97d14eb04ef101dd34e769ce6927a1535279509acfaf8ca7683007d716ff2c26` |

Actual research used `curl -fSs --max-time 40 <text-url> -o <scratch-file>`,
`curl -fSsI --max-time 30 <writer-url>` (HEAD only), `git show`, `sha256sum`,
`jq`, and the installed citation ledger. `web_extract` had timeouts/partial pages;
direct text GETs recovered cited documents. Unavailable manual/price routes were
not treated as evidence. `execute_code` was denied by single-query policy and did
not run; no security setting was changed. One evidence quote attempt containing
only `Version 6.24` was rejected as too short; replaced with a literal longer
sentence from the same fetched page, not fabricated source text.

Validation commands/results, final commit and absolute artifact path are recorded
on the review transition. Required checks: source/task branch and parent ancestry;
all cited sources retrieved with actual content; exact quotations and generated
Sources block; expected installer hash bound to English x64 entry; eight unique
case IDs with correct RAR4/RAR5 and old-volume restriction; all planned gates and
unqualified coverage intact; local document links/paths; snapshot digests;
`git diff --check`; only this owned deliverable changed. No runtime PASS claimed.

Commit before same-card independent review with `reviewer`. Reviewer PASS applies
only to this proposal, not to proprietary-use approval or B01 qualification.
Reviewer/coordinator must post the **reviewed** commit and artifact path to
`t_22299c6f`; author must not label this unreviewed draft a reviewed handoff.
CHANGES returns this same card; two substantive failures require escalation.
No generation child, gate archiving, shared-branch merge or release is authorized.

## Sources

[1] https://www.rarlab.com/download.htm
    > "RAR for Linux x64 7.23"
[2] https://www.rarlab.com/license.htm
    > "There are no additional license fees, apart from the cost of the license, associated with the creation and distribution of RAR archives, volumes, self-extracting archives or self-extracting volumes."
    > "Business users require one license per computer or mobile device on which the software is installed."
    > "Installing and using the software signifies acceptance of these terms and conditions of the license."
[3] https://www.rarlab.com/rarnew.htm
    > "Creating archives in RAR 4.x format isn't supported anymore."
[4] https://www.7-zip.org
    > "You can use 7-Zip on any computer, including a computer in a commercial organization."
[5] https://www.libarchive.org
    > "Writes tar, pax, cpio, zip, xar, ar, ISO, mtree, and shar archives."
[6] https://raw.githubusercontent.com/microsoft/winget-pkgs/67707b1e6db26d50df506f7b67f4369874facbb0/manifests/r/RARLab/WinRAR/6.24.0/RARLab.WinRAR.installer.yaml
    > "Architecture: x64 InstallerUrl: https://www.rarlab.com/rar/winrar-x64-624.exe InstallerSha256: 794481DBBC9009A2565726FB5B4A4AB2FE216FF9EDBB08951548EE765DE9B4A6"
[7] https://www.win-rar.com/whatsnew.html
    > "WinRAR and UnRAR.dll extraction command dereferenced a null pointer"
[9] https://www.rarlab.com/technote.htm
    > "RAR 5.0 signature consists of 8 bytes: 0x52 0x61 0x72 0x21 0x1A 0x07 0x01 0x00."
[10] https://www.rarlab.com/rar_archiver.htm
    > "WinRAR offers the ability to create self-extracting and multivolume archives."
[11] https://gist.githubusercontent.com/YenForYang/5953ad8355cf32188aa75c0139cc9261/raw/d163c85e2e9e6442982d90980b2d63101258659f/rar.txt
    > "Use -ma4 to create RAR 4.x archives."
    > "RAR 6.02 console version"
    > "RAR 5.0 archives do not support -vn and extension based names."
