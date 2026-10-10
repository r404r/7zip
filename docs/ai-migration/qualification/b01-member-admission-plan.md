# B01-I-P: bounded member inspection and corpus admission plan

Task `t_ccd5caf7`; branch `wt/t_ccd5caf7`. Documentation only; pending independent
review. **No currently justified executable inspection path.** This is a finite
admission plan and source assessment, not an import manifest, sandbox implementation,
execution approval, or change to compatibility acceptance.

## 1. Authority, immutable basis and stopping rule

The actual operator decision “按照你的建议进行推进”, recorded on B01
`t_22299c6f` at `1789142630`, authorizes this plan and independent review only.
It does not authorize opening an archive even to list its headers. B01 remains
`triage`, `import_approved=false`, `qualified=false`; B03 is unchanged.
B04 `t_2a64c953` comment **135**, read directly from the board, records
“B04 按照推荐推进” as **freeze B04**, not another diagnostic preparation or run.
Native budget remains **0**; preserve stage PASS/evidence at
`b1719b6d8a3b169edd696084c58921f228f41451`. Notification wake is not approval.
Do not use this B01 plan to restart B04 under a new name.

Read both source/worktree [AGENTS.md](../../../AGENTS.md); source checkout was
`ai/migration-bootstrap-20260911`, task started clean at
`8f1ea18b67d535449575eceb4ee92846253e4012`. Reviewed B01-Q parent
`4ac792d008bf75c23e11aa429780231568a1dbed` and reviewed O1
`3cf4421d081b912763e326c47322f095211fbd47` are already ancestors; no merge needed.
B01 comments confirm independent PASS of both. Their documents' historical
“awaiting review” language is not rewritten. No unreviewed original B01
`9d01d5069f5b117aa5c69dd5cc62f090869d7650` is integrated or approved.
Complete parent subscription inheritance and default Telegram `notify+wake`
were verified read-only, without emitting identities or modifying routes.

Controlling sources (the named sections/fields below are precise evidence locators):

- [O1 replay policy](b01-replay-policy.md), “Normative evidence classes”,
  “Acquired case-intent equivalence” and “Future validator acceptance”.
- [O1 rights assessment](b01-o1-rights-review.md), “What the licensing evidence
  actually says”, “Container, members and metadata” and eight-case table;
  [O1 JSON](b01-o1-rights-review.json), `rights_common`, `candidates`,
  `case_mapping`, `remaining_other_b01_coverage`, `sources`.
- [B01-Q report](b01-quarantine-acquisition.md), “Final authorized continuation
  and current result”; [resume.json](../../../.github/tests/migration/b01-quarantine/resume.json),
  `candidates.*.files`, the authoritative acquired byte identities.
- [B01-W](b01-writer-plan.md), “Native qualification and negative controls”
  (lines 328–393); [B01-P](b01-provenance.md), provenance gates G/P/L/H/N;
  [M1](../characterization-baseline.md), blockers B01–B08;
  [M2](../migration-stages.md), compatibility matrix and rollback policy;
  [DAG](../migration-dag.md), unchanged production dependencies.
- [B04-P](b04-actions-recovery-plan.md), “Exactly two approaches assessed” and
  “Provider eligibility, costs and acceptable use”, reviewed source assessment
  commit `9c038dc7ed89034ac0b2c14c4d12bec2e6eed7ca`. Its proposed diagnostic round
  is historical, not current permission. Later B04 evidence is cited by exact
  Git object below because that branch is intentionally not integrated.

No archives, opaque bytes or derivatives were read, parsed, listed, decoded,
re-fetched, copied, attached or executed here. No compiler, sandbox, native CI,
writer, push, correspondence, paid product, new service, or privilege change.
Only committed text/metadata/source, board records and offline document checks
were used. Input digests below are **inherited reviewed measurements**, not new
hashing of the quarantine. Do not run B01-Q's complete verifier on this card:
it reopens opaque bytes, beyond this plan-only scope.

## 2. Exact finite inputs and three candidate mappings

All source paths below are under Debian `python-rarfile` **`4.5-1`**,
`test/files/`. Full original/final URLs, acquisition times and private paths are
in `resume.json`; no URL is an authorization to fetch it again. Part order is
as shown within each family, subject to later actual header/volume verification.

| Family | File | Acquired bytes | Acquired SHA-256 |
| --- | --- | --- | --- |
| DRF-OLD | rar3-old.rar | 102400 | 57f57c2d61f4a6b437cbb38fbabecb42e6f826b5d3ce952d6e74cbbc7d5dcd71 |
| DRF-OLD | rar3-old.r00 | 102400 | f0741e5cba62f81280136d841318af1a448c1d446d931c34039d0b4c834dab42 |
| DRF-OLD | rar3-old.r01 | 2572 | c0bd5bf9d02916b2aa23661e1448833bab3e96cc244189ae3ffdba9909d6d9a5 |
| DRF-SOLID | rar5-solid.rar | 169 | d97d23b2edee9a7daa49e45015ea72aa3f162efeb0abaf559740ab797276203b |
| DRF-VOL | rar5-vols.part1.rar | 102400 | c997e965ad319646e3bead59b372a9bd87459aa471c8bc8ad02267d43e328c2f |
| DRF-VOL | rar5-vols.part2.rar | 102400 | 484343c1ca19e1eac8103946f1c0e7746d6df5d995f8f55395f03786ad34e709 |
| DRF-VOL | rar5-vols.part3.rar | 11384 | 0b117cf1cb7b46877124d5f07ebc45580b4a5feadc24f5578196036a32c9eadc |

Reviewed total: 423725 bytes. Preserve private root
`/home/ding/work/github/r404r/b01-quarantine-t_d32ff791`, all original files,
`manifest.json`, `resume.json`, failed-response evidence and attempt marker.
The tracked result SHA-256 is
`a275139f24d853b6efe405eaf3f9df32f798acfb89d1a91f9b5b2c3f9445773b`.
Mode 0400 with directories 0700, as measured by B01-Q, is private retention,
not immutable storage against a compromised same-owner process or a sandbox.
The `.opaque` suffix is not an archive format or a safe execution policy.

Only these **three** candidate rows are mapped; all are unqualified:

| Candidate | B01-W row | Expected metadata only; actual evidence still needed |
| --- | --- | --- |
| DRF-OLD | R4-OLDVOL | Expected `vols/bigfile.txt` 205000 and `vols/smallfile.txt` 2050 bytes; stored `meth=0`, old-name split set. Verify handler, method, exact full set and entrypoint; `ver=20` is not writer identity or full Rar3 coverage. |
| DRF-SOLID | R5-LZ-SOLID | Expected `stest1.txt`, `stest2.txt`, 2048 bytes each, `cmp_meth=3`, second `solid=True`. Verify actual decoder/solid behavior, payloads and metadata. |
| DRF-VOL | R5-VOL | Expected `vols/bigfile.txt` 205000 and `vols/smallfile.txt` 2050 bytes; `cmp_meth=0`, `solid=False`, numbered split set. Verify actual full set, method and volume outcomes. |

These are O1 JSON `expected_metadata.literal_text`, not an inventory of the
acquired archives. Expected CRC equality does not imply equal full byte hashes,
rights or content. Unexpected extra, service, link, stream or directory entries
must not disappear through CLI filtering or expected-name matching.

## 3. Requirement and ownership matrix

“Satisfied” below always names its limited scope. Future work owners are roles,
not new task assignments or authorization. The coordinator owns permission/scope,
coder any later harness/validator, tester measurements, architect rights/boundary
assessment, and reviewer independent acceptance. No role can self-approve.

| Requirement | Evidence now / precise authoritative source | Acceptance method and owner |
| --- | --- | --- |
| Evidence class | Policy settled: exactly `acquired-immutable` / `generated-reproducible`, `schema_version=1`; O1 policy lines 45–98 | Coder binds each later fixture to reviewed class record; reviewer rejects implicit defaults or relaxing existing records. No schema edit here. |
| Historical writer | Explicit unknowns with reasons: O1 and resume `candidates.*.historical_writer` | Architect retains known values and cited reasons for nulls. Unknown historical writer alone is NOT a blocker for acquired replay. No named-writer/regeneration claim. Generated fixtures keep B01-W writer/version/build/invocation/repeat requirements. |
| Input identity / source | Satisfied for quarantined byte identities only: resume `distribution`, `version`, `candidates.*.files.{path,sha256,actual_size,original_url,final_url}` and Q final reviewer handoff | On a later authorized run, tester binds read-only input handles to exact bytes/lengths and before/after evidence under trusted custody; reviewer checks all seven, not just entrypoints. SHA-1 tree IDs are not SHA-256 or proof of Debian/upstream byte equality. |
| Volume identity / completeness | Proposed order/names recorded in resume; actual native membership/entrypoint not measured | Tester records header identities, requested/resolved volume names, order and all-part set from retained reader; rejects missing/extra/out-of-set access. Headers and naming claims alone do not qualify missing-volume behavior. |
| Container rights | Affirmative versioned path attribution, not a warranty: O1 JSON `rights_common`, sources 1/2/3/8/9/10 | Architect reuses `Files: *` ISC plus matching contribution history; reviewer assesses applicability and any contrary evidence. Do not invent a compulsory personal grant or treat one as universal. |
| Member bytes and names | Missing: resume `actual_member_hashes=null`; expected dumps are not actual observations | Authorized tester obtains every actual member identity, full SHA-256/decoded length, exact name representation and source index/order. Record empty files, duplicates, directories/service records and unsupported properties explicitly; no missing accepted hashes. Reviewer checks completeness. |
| Member metadata / links | Missing: O1 `member_metadata_applicability`, `expected_metadata`; no actual inventory | Tester records property IDs/types/definedness, attributes/modes/times with precision/timezone, raw name encoding where available, stream/dir/link classification, exact link targets and applicable flags. Absent property is explicit absence, not an invented default. No filesystem materialization to discover targets. If retained APIs cannot expose needed identity, stop; do not fill from expected dumps. |
| Member/metadata rights | Missing complete actual source-to-member binding; O1 rights sections 67–88 | Architect maps each actual item/name/metadata and discovered notice/source against ISC evidence, resolves exceptions, documents reasoning and independent review. Bounded plain-text review only after authorization/containment; hashes alone cannot establish authorship. Contradictory/third-party notices stop; no automatic correspondence or expansion. |
| Notices | Satisfied for retained copies: O1 literal selected stanza and Q three notice files | Preserve full copyright, permission and literal ISC disclaimer verbatim, source/version/path and rights-review binding with every later authorized copy/derivative; reviewer compares exact notice bytes. No replacement with CC0/MIT, no packaging GPL-2+ relabel of test paths. |
| Inspection safety | Missing an independently demonstrated usable boundary; sections 4–6 below, B04 comment135 | Coder/tester would need exact harness/control evidence under separate authority; reviewer verifies confinement and supervision before opaque inputs. Current freeze prohibits attempts to generate that missing evidence. |
| Native reader identity | Missing for these files: O1 policy lines 67–73, M2 matrix | Tester pins legacy commit, selected objects/product, executable SHA-256, compiler/flags/dependencies, OS/CPU, filesystem/locale and exact argv/environment. Reader identity must never be null merely because historical writer is unknown. |
| Native behavior | Missing: Q `native_results_produced=false`, B01-W lines 328–393 | Windows MSVC x64, Linux GCC x64, macOS Apple clang arm64: clean repeats, uninstrumented controls, raw stdout/stderr/exit and actual numeric HRESULT/NOperationResult/CArcErrorInfo definedness/flags, ordered callbacks/stable operation/item identity and partial effects. Tester captures, reviewer accepts; no Wine/cross-build/CLI-to-FFI inference. |
| Formal admission / CI / distribution | None authorized: B01 current comment and Q false flags | Coordinator records distinct exact scopes; reviewer verifies rights/identity/native requirements before accepted fixture status. No plan PASS can set B01 qualified or release its DAG edges. |

Full notices already exist at
[DRF-OLD-NOTICE.txt](../../../.github/tests/migration/b01-quarantine/DRF-OLD-NOTICE.txt),
[DRF-SOLID-NOTICE.txt](../../../.github/tests/migration/b01-quarantine/DRF-SOLID-NOTICE.txt),
[DRF-VOL-NOTICE.txt](../../../.github/tests/migration/b01-quarantine/DRF-VOL-NOTICE.txt).
They are retained, not recopied into a shortened new license. Positive distribution
attribution is substantive evidence; unknown embedded applicability remains a
separate acceptance gap, not a declaration that redistribution is unlawful.

## 4. Retained reader trace: narrower output is not containment

All following code locators refer to the source at base
`8f1ea18b67d535449575eceb4ee92846253e4012`. No binary was built or invoked.

### 4.1 Header/property inspection still executes a parser

[IArchive.h](../../../CPP/7zip/Archive/IArchive.h):278–328 defines
`IInArchive::Open`, `GetNumberOfItems`, `GetProperty`, `Extract`, `Close`.
`maxCheckStartPosition=0` constrains start probing, not memory/time or filesystem
access. The same object must not be used concurrently from different threads
(306–307). No resource/sandbox guarantee is part of this interface.

CLI `ListArchives` in [List.cpp](../../../CPP/7zip/UI/Console/List.cpp):1173–1191
calls `arcLink.Open_Strict` before listing. Lines 1276–1340 get properties/items,
and may skip auxiliary entries/alternate streams or apply filters. Therefore
`l -slt` is neither a parser-free operation nor inherently complete member evidence.
It emits names/properties to stdout, not full decoded member SHA-256s.

[RarHandler.cpp](../../../CPP/7zip/Archive/Rar/RarHandler.cpp):1073–1154 queries
open-volume/password callbacks, generates next volume names, requests streams and
parses item headers. [Rar5Handler.cpp](../../../CPP/7zip/Archive/Rar/Rar5Handler.cpp):2260–2336
likewise acquires further streams; 941–1003 reads names, declared sizes and extra
metadata, allocating `item.Extra` from parsed size. The normal
[ArchiveOpenCallback.cpp](../../../CPP/7zip/UI/Common/ArchiveOpenCallback.cpp):284–364
checks `IsSafePath` but resolves a filesystem path and calls `Find_FollowLink`
then opens it, retaining streams. This is not a strict seven-handle allowlist or
race-resistant no-link boundary. `.opaque` names also do not match the reader's
normal next-volume naming. A later test-only callback could map exact logical
volume names to pinned handles; it must never rename originals or resolve an
arbitrary request on the host. That callback does not exist as an approved path.

### 4.2 Getting member hashes requires decoding, not just listing/test success

`IInArchive::Extract` test mode means testing without writing payload to the
outStream, not avoiding decoding. RarHandler.cpp:1403–1566 includes preceding
solid members in work, requests `GetStream`, and wraps output in CRC accounting;
a null stream may skip a file or still decode it for a later solid member.
Rar5Handler.cpp:3090–3247 similarly handles solid/link dependencies and skip/test
modes. Returning null and calling that a complete hash inventory is incorrect.

Rar5Handler.cpp:1129–1174 selects copy/LZ code, can allocate `linkFile->Data` to
the declared member size, then invokes the coder. Decoder allocations occur
before/outside any caller's output byte cap:
[Rar5Decoder.cpp](../../../CPP/7zip/Compress/Rar5Decoder.cpp):1960–2028 allocates
the dictionary window with `BigAlloc` and an input buffer, then `CodeReal`;
[Rar3Decoder.cpp](../../../CPP/7zip/Compress/Rar3Decoder.cpp):431, 899–907 includes
PPMd/VM/window allocations. Small compressed input, advertised member size, CRC,
and a streaming hash sink do not bound all internal work or prevent memory faults.

### 4.3 Output, processes and ownership

[ArchiveExtractCallback.cpp](../../../CPP/7zip/UI/Common/ArchiveExtractCallback.cpp):1698–1785
reads per-item/link/size properties; 1930–2003 distinguishes a stream callback,
stdout (`CStdOutFileStream`) and normal filesystem extraction. The latter reaches
`GetExtractStream` and `Create_ALWAYS_or_Open_ALWAYS` at 1576, with directory,
link and metadata handling elsewhere in the same callback. `x` is consequently
not an inspection-only operation. `x -so` selects stdout payload output; it does
not provide an authenticated per-member framing protocol or confinement. Capturing
stdout into RAM still executes the vulnerable parser/decoder and can exhaust RAM.

The traced retained RAR API path invokes in-process codecs and caller callbacks;
no external writer/helper child launch is evident in these paths. This is a
bounded source observation, not proof that a compromised decoder cannot launch
processes or write files. Build identity must also exclude unpinned plugin loading:
[LoadCodecs.cpp](../../../CPP/7zip/UI/Common/LoadCodecs.cpp):3–30 describes
`Z7_EXTERNAL_CODECS` discovery, and line605 loads a library. Do not assume any
binary named `7z`/`7zz` has the required bundle/macros. No GUI/shell-open, system
rarfile backend substitution, shell command constructed from names, or payload
execution is proposed.

A possible future **test-only**, single-threaded API observer would retain
COM references for input streams, archive and callbacks until decoding returns,
copy typed `PROPVARIANT` values before release, and hash bounded per-index output
rather than retaining an entire payload or using names as paths. `GetStream`
returns reference-counted output; callback/stream lifetime must cover all engine
uses. Propagate callback failures, distinguish abort from engine errors, close
archive/streams on normal completion; an outer supervisor must handle hangs or
memory corruption without trusting destructor execution. A decoder-host process
and its callbacks share one compromise boundary. No production FFI/module/API
change or implementation approval follows from this design sketch.

## 5. Minimum bounded envelope (proposals, not measured limits)

This section defines what a later proposal would have to prove, **not runnable
instructions**. All numerical caps here are proposed rejection thresholds, not
observations, not adjusted goldens, and not current execution budgets. Exceeding a
cap leaves evidence incomplete; never increase it automatically. There is no
claim that the current reader will run within these numbers.

| Boundary | Proposed ceiling / behavior | Required proof before inputs |
| --- | --- | --- |
| Inputs | Only section 2; at most three read-only part handles per family; total pinned bytes 423725 | Trusted custodian verifies identities and read-only immutable backing before/after; decoder cannot change directory entries, original evidence or supplied handles. No symlink/hardlink/device substitution or same-owner write escape. No new acquisition. |
| Reader | One pinned retained-reader process per family, single-threaded observer; no nested archive recursion | Exact executable/dependency/config identity; only intended RAR handler, no external plugins, prompts/passwords or automatic fallback. Unknown/encrypted/unsupported format stops without broader probing. |
| Work | At most 16 observed entries per family, 4096 bytes per name/link-target representation, 64 KiB total metadata per family | Bound parser process before Open, not just check count after Open; no silently truncated accepted identity. Unexpected entries/types stop for review even below limits. |
| Decoded bytes | 1 MiB per logical member and 4 MiB aggregate per family including solid dependencies/service/link work | Check actual emitted bytes before accepting a chunk, account intermediate work where observable, fail if accounting incomplete; OS memory/time bounds independently constrain pre-output/internal work. Never trust declared lengths. |
| Memory / CPU / time | 256 MiB decoder process-tree memory, 10 CPU seconds and 30 wall seconds per family | OS-enforced limits established before untrusted execution; include descendants, shared accounting and allocation before first callback. Trusted supervisor has separate bounded resources. No in-process cooperative limit alone. |
| Processes | One decoder process, no child exec/fork, bounded threads; serial families, no retry | Deny creation/escape, handle reparenting and thread-count semantics explicitly. Parent outside child's writable/control scope. Empty process tree confirmed after every outcome, not only direct-child exit. |
| Filesystem / disk | No member materialization; zero writable host mounts; at most 8 MiB isolated scratch and 1 MiB encoded evidence per family | Kernel-enforced bounded private scratch; no agent/workspace/home/credential/control access. Parent-owned manifests and outputs not child-writable. Refuse link/reparse following on collection. |
| Output | Framed member index/length/digest and typed metadata; bounded private plain-text review if later expressly authorized | Per-member hashes are not content-rights review. Decode text only into non-executable bounded representation; never preview in an app, interpret escapes/HTML/scripts, use names as paths, or emit raw workflow commands. No derived payload retention/distribution permission implicit. |
| Network / credentials | No network, DNS, loopback, inherited credential/environment/agent sockets, runner token or IPC access | Enforced denial below compromised process, with self-owned negative controls. Clearing environment alone is inadequate; parent required networking cannot be accessible to child. |
| Termination / cleanup | On breach, kill entire contained tree; proposed 5-second quiescence deadline | Supervisor owns timeout/kill authority outside child; if quiescence unproved, stop and do not inspect/delete child-writable results or launch another family. Preserve original quarantine/attempt records always. Clean only separately authorized disposable storage after no-follow quiescent collection. |

At most one pass per family could be proposed after prerequisite PASS; stop the
whole pilot at the first violation, unexpected member/source/notice, byte drift,
unknown format/link/password, malformed/oversized output, resource kill, incomplete
inventory or supervision failure. No full qualification can be claimed from that
single inspection pass. Native repeat/error/corruption campaigns have separate
scope and budgets, currently unauthorized.

Negative controls would have to include: unchanged harmless positive control;
input write/rename and out-of-set volume request; traversal/symlink/reparse and
host/control-file access; denied network and credential probes against self-owned
canaries; fork/exec escape, memory and output flood, hang and reparented descendant;
malformed/truncated/forged result framing; full scratch; late output after exit;
kill/cleanup failure. Verify expected denials and trusted collection integrity,
not merely unchanged sentinels after a failed startup. Synthetic harness unit tests
cannot replace a native boundary test. No such controls are run on this card;
B04 remains frozen, and its evidence is neither reset nor generalized.

## 6. Already-known zero-additional-cost facilities: evidence, not a new search

Only the existing facilities evaluated by B04 are considered. B04-P's linked
GitHub runner/billing/terms, Microsoft API and bubblewrap source references are
inherited read-only research, not freshly fetched current-service guarantees.
Later B04 source/evidence at `b1719b6d8a3b169edd696084c58921f228f41451`,
`docs/ai-migration/qualification/b04.md`, “Authorized offline follow-up (tester
run79)”, was read with `git show`; no B04 code or tests were imported/executed.

| Known facility | Evidence and limitation | Consequence for this plan |
| --- | --- | --- |
| Existing GitHub standard hosted Linux x64 | B04-P reported PUBLIC repository/free standard-runner eligibility. Latest B04 report ties bubblewrap `0.9.0-1ubuntu0.1` to package source; loopback setup fails before mounts/payload. Netlink helper failure does not prove the printed errno identifies the denial. | A no-write API sink does not cure failed confinement. No host-network/namespace/capability workaround, trial launch or private-machine fallback. No justified executable path. |
| Existing GitHub hosted Windows x64 | Later B04 report: suspended `CreateProcessW` fails with error2 before Job assignment/resume; parent path identity does not prove child-token/loader access. Derived AppContainer SID is not profile creation. | Proposed Job supervision is not a successfully exercised boundary. Do not repeat obsolete B04-P “no Job Object” as latest source state; no profile/storage/ACL/environment expansion or launch authorized. |
| Existing GitHub hosted macOS arm64 | Later offline stage fixed metadata-test mock isolation; its synthetic regression is not native startup evidence. Earlier sandbox signal -6 remains unexplained. | Test repair does not establish usable sandbox. No fresh run or new sandbox API. |
| Hosted VM alone / nested guest | B04-P: runner/controller and privileged tools live inside the hosted VM; provider networking remains. An independent guest needs an outer supervisor, immutable transfer and credential-free isolated guest. Standard hosted macOS nested virtualization unsupported in cited docs; Linux/Windows generic independent nested guest not established. | Disposable VM is not containment of decoder from the trusted collector. No new VM/service, paid/larger runner, self-hosted/private host default, or unverified image license. |
| Local existing process sandbox observations | B04-P notes local Linux positive evidence but different hosted policy; Q private directories protect retention only. | Not permission to open files on this workstation. No verified independently supervised inspection envelope follows from these observations. |

Original native evidence remains negative; a read-only listing still exercises
Open and a memory sink still exercises decoders. “No payload execution” is not
proof against parser compromise. Nothing in this bounded assessment proves that
all free solutions are impossible; it establishes that **none of the known paths
has the missing reviewed, measured envelope for this operation**.

Cost/license constraints stay explicit. The retained source's
[License.txt](../../../DOC/License.txt):8–19, 136–149 assigns LGPL plus unRAR
restriction to RAR decoder files; [unRarLicense.txt](../../../DOC/unRarLicense.txt):13–19
permits handling RAR free of charge but not recreating its proprietary compressor.
No commercial writer, trial or separately obtained commercial authorization is
needed/proposed for retained decoding; existing source/binary notice obligations
are not waived. This does not license acquired members automatically.
GitHub free-compute eligibility would need revalidation at execution time;
artifact/cache storage allowance was not proven. No new artifact/cache upload or
paid storage is proposed. B04-P's bounded encoded-log idea is a possible evidence
transport only after rights and trusted collection review, not authority to publish
private member names/content in public logs. This task incurs no product fees and
uses no hosted execution. Do not assume costs/terms or image rights from a label.

## 7. Permission boundaries, admission sequence and complete coverage

These are separate decisions/evidence obligations, **not new status enums**:

1. Private inspection: exact inputs, platform/reader/observer identity, restricted
   operations and private evidence sink require explicit permission plus section 5
   prerequisite evidence. Existing acquisition permission does not extend to this.
   Unknown embedded applicability is disclosed for that bounded decision; no
   invented warranty or mandatory new personal grant. Safety remains independent.
2. Formal corpus admission: actual complete member/name/metadata/link/source-rights
   review, full input/member hashes/notices and required native replay evidence
   must be non-null and independently accepted under O1 before a fixture is marked
   accepted. A private provisional inventory is not accepted regression data.
   Permission to conduct qualification experiments is not fixture acceptance.
3. CI use: additionally specify which CI/visibility/transfer/retention scopes are
   allowed, demonstrate safe execution and zero added cost, and verify rights for
   copies/logged metadata. Do not put opaque bytes or decoded content in caches,
   logs, artifacts or public branches merely because private inspection passed.
4. Redistribution: separately authorize exact archives, members/metadata/derivatives
   and destination with reviewed applicability/notices; no publication follows
   from CI use or corpus admission. Input-source software license is not a generic
   license for every discovered embedded item or provider guest image.

Preserve O1's accepted-fixture threshold rather than introducing an “accepted but
native unknown” tier. Once separate authority and prerequisites exist, the finite
sequence would be private observation -> independent byte/member-rights assessment
-> authorized native qualification -> independent fixture admission review. Failure
at any step leaves B01 gated; no endless search or repeated unchanged permission
question. Success for these fixtures still does not complete B01.

The unmapped original rows **R4-STORE, R4-LZ, R4-PPM, R4-VOL, R5-STORE** remain
unqualified with no new candidate search. All three mapped rows also remain
unqualified. Retain B01-W's list/test/extract and observed RAR create-refusal;
missing first/middle/last volumes and non-first entrypoints, probing and nested
chains; justified header/data/truncation corruption cases with base/derivative
hashes and numeric/raw distinctions. No derivatives are authorized here. Original
`ALL` recipe identity is waived only as O1 states: empty member, binary/text
repetition, nested paths, dictionary/thread/metadata dimensions not demonstrated
by these files remain uncovered. Never assume `sequence.bin` or a corruption
offset exists; byte-layout-verified equivalents need separate review.

Other retained obligations from O1/B01-R/M1: Rar1/Rar2; Rar3 PPM/LZ transitions and
filters; classic compressed solid/multipart; levels/dictionary boundaries;
RAR-specific unsupported/damaged compressed methods (ZIP unsupported is not a
substitute); recovery/SFX; external 7z/CAB/ISO/WIM and remaining retained capability
inventory; code-page/Unicode paths B02; metadata/links/permissions/ACL/ADS/sparse,
ZIP64/large files/short I/O/full disk B03; traversal/overwrite/reparse/races/partial
failure B04; passwords/encryption B05; cancellation/progress B06; GUI/desktop B07;
FFI ownership/concurrency B08. Stable operation/item identity, raw versus numeric
list/create coverage and platform/product scope remain explicit. No migration
sequence, Qt 6/QML -> CXX-Qt -> Rust -> mature C/C++ boundary, or DAG edge changes.

A future validator (not implemented here) must bind fixture ID, evidence class,
`schema_version=1`, exact base/part/member/notice hashes, volume membership/order,
rights review and native report scope. Reject invalid/missing class, generated
unknown writer, acquired unknowns without reasons, unjustified named-writer or
regeneration claims, and derivatives lacking actual transformation identity.
Require complete member identity/rights/native evidence; never accept their nulls
under the historical-writer exception. Existing manifests retain their old
validation until explicitly extended, not silently defaulted to acquired.

Its negative controls must independently mutate an input byte/hash, member hash,
class binding, part order/set, member name/link/metadata/source-rights or notice,
raw outcome, HRESULT bits/NOperationResult/CArcErrorInfo definedness/flags,
platform/reader/handler identity, repeat control or operation scope. Every altered
record must fail while unchanged controls pass. Preserve original M1 goldens and
raw native reports; no expected-data rewrites to force agreement. These planned
validator tests do not replace section 5's separate confinement controls.

## 8. Verification and review handoff

Only this Markdown report is a deliverable. Temporary standard-library checkers
are ignored under `.github/tests/migration/b01-quarantine/__pycache__/`; they read
text/metadata, not opaque files. Production builds/native tests are inapplicable
and forbidden here: no executable changes, and compilation cannot prove rights
or inspection containment. No compatibility, measured resource-limit or sandbox
PASS is claimed. Source review is bounded, not a vulnerability-completeness audit.

Commands executed from this task worktree (all exited 0):

```text
python3 .github/tests/migration/b01-quarantine/__pycache__/check_member_plan.py
python3 docs/ai-migration/validate-migration-dag.py
python3 -m json.tool .github/tests/migration/b01-quarantine/resume.json /dev/null
python3 -m json.tool docs/ai-migration/qualification/b01-o1-rights-review.json /dev/null
git diff --check
```

The temporary checker passed seven table identities/lengths/order and total
423725 against committed resume, three candidate mappings, all eight B01-W IDs,
three literal notices against O1 stanza, 26 local links and line-range bounds in
11 source files. It verified those sources unchanged from base, single-report
scope, parent ancestry, source branch/clean HEAD and unchanged dev-main, full
inherited subscription fields and B01 `triage` / B04 `blocked` / comment135.
The unchanged DAG validator passed 29 children, 104 child edges, acyclicity and
three negative controls (offline manifest, not a new live dispatch approval).
JSON/whitespace checks passed. The checker reads only this report, linked source,
committed JSON/notices and read-only Git/board state, never the quarantine root.
An initial `execute_code` helper was denied before any tool calls; work continued
through normal reads and explicit harmless file-based checkers, without changing
approval settings. A shell probe found no `sqlite3` executable; standard-library
read-only SQLite inspection succeeded, without installation or board writes.
The document checker validates evidence bindings, not legal reasoning or containment. Both
source and task must remain clean after the single-file commit. Full commit SHA,
branch, artifact path and command outcomes accompany same-card review request.
Reviewer independently cold-reads this report, checks current authority, evidence
meaning and coverage, then PASS/CHANGES. Two substantive failures require typed
`needs_input`; no duplicate repair cards. PASS completes only this preparation
card; reviewer posts exact commit/path/limits to B01 and reads it back. B01/B04
must not be unblocked, completed, archived or integrated as a side effect; B03 and
downstream dependencies stay unchanged. No push/shared merge/release by author.

## 9. Exact blocker and bounded disposition

**Not executable:** no approved/measured restricted reader + trusted supervision
and output protocol meeting section 5 is available in the known evidence; current
B04 decision freezes further diagnosis and native budget is 0. The missing
prerequisite is not another approval for O1 or acquisition, and not the historical
writer. It is operation-specific containment/termination/collection proof plus
explicit inspection authority. Actual member and native admission evidence cannot
be obtained by relabeling a header-only/decoder-to-memory run as safe.

There is no warranted request to execute the seven files now. After independent
review, return the following finite disposition to the coordinator; do not create
work, change B04, or repeatedly ask the operator to reconsider the same freeze:

- **Recommended: retain quarantine and the current freeze.** Stop this plan at
  reviewed handoff. Zero new execution/cost/redistribution risk; affected B01 and
  dependent work remain gated, independent eligible work continues. No unresolved
  prerequisite is archived and no qualification target is reduced.
- **If genuinely new, already-existing evidence is supplied:** review only the
  identified facility/version, independent supervision, enforced caps and harmless
  native controls for the section 2 inputs/section 5 operation. Documentary review
  is not commissioning a new diagnostic, private machine or service. Evidence may
  make a subsequent exact proposal possible; it does not grant execution. Cost,
  license, private output and current authority must all still be checked.
- **Only if the operator explicitly changes the freeze:** coordinator may define
  a separate finite prerequisite proposal with exact platform/commit/controls and
  budget; obtain independent review and a new execution decision before any run.
  This is neither recommended now nor initiated here. Impact: new bounded safety
  investigation, uncertain success, no automatic import or full B01 acceptance;
  zero-additional-cost/no-commercial-authorization constraints remain.

Do not substitute endless candidate search, commercial authoring, hosted-VM trust,
private machines, a broad audit, or an acceptance/DAG reduction for this blocker.
