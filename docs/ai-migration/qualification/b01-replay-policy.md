# B01-O1: authoritative additive replay evidence policy

Task `t_4ea8d1ca`, branch `wt/t_4ea8d1ca`.
Status: approved human policy scope, implementation document awaiting independent review.
This is a normative additive amendment, not a rewrite of historical evidence and
not an executable manifest-validator change.

## Authority and precedence

Controlling decision: original B01 `t_22299c6f`, comment 89, recorded at Unix
`1789127406`, quotes the operator's **「批准」** for the immediately preceding
limited O1 proposal. During this task the operator additionally confirmed
**「选择O1」**. Both authorize this same phase; neither is import approval.
The complete comment was read, not inferred from a notification wake.

Reviewed basis: [B01-R](b01-resolution-options.md) and its JSON at commit
`1fc1f83091a50bab2c691e372eb8b86b745fe008`, integrated as
`b7c30b273fd930c3167434c87b85c685aac846cd`. That report's historical statements
that O1 is unapproved remain accurate as of that report; this later decision
supersedes only that status and the exact requirements below. Other proposals
O2/O3, candidate findings and unqualified statuses are not retrospectively changed.

This policy is authoritative for the approved distinction in M1/B01 evidence.
Its immediate operational scope is documentation and rights review of DRF-OLD,
DRF-SOLID, DRF-VOL from Debian `python-rarfile` `4.5-1` only. No additional
candidate search, archive/member download, import, extraction, writer installation
or execution, native run, upstream correspondence, spending or commercial
execution is authorized. No DAG/B01 state change or B03/B04 authorization change.
The [rights assessment](b01-o1-rights-review.md) is an engineering assessment for
independent review and a later import decision, not legal advice or permission.

## Requirement trace and exact delta

| Origin | Before / controlling obligation | O1 disposition |
| --- | --- | --- |
| [AGENTS.md](../../../AGENTS.md), 24–28, 64–78, 123–165 | Legacy oracle, mature codecs, native platforms, full compatibility, independent review, isolated worktrees | Unchanged. No runtime/codec/encryption/GUI/AGENTS edit. |
| [M1](../characterization-baseline.md), 155–173, B01 row 166; B01 card body | Actual generator/version/license provenance, immutable external bytes/hashes, required format/error/volume behavior | For `acquired-immutable` ONLY, actual known generator/version remain recorded; unavailable historical values MUST be explicit null with reasons. Their absence alone is not a replay qualification failure. License applicability and all byte/behavior evidence remain mandatory. |
| [B01-P](b01-provenance.md), 158–182 | G writer/build/options/creator binding; P/L source and rights; H hashes; N native reports | G may be unknown for acquired replay, with no regeneration or named-writer claim. P/L/H/N are not waived. The old candidate findings are not overwritten or automatically promoted. |
| [B01-W](b01-writer-plan.md), 183–238, 240–326 | Exact fresh writer environment, package/executable identity, argv, ALL-member recipe, repeated generation and immutable records | All retained for `generated-reproducible`. For acquired replay, replace generation-recipe equivalence with documented case-intent and measured-behavior equivalence, as bounded below. No claim the old recipe was executed. |
| [B01-F](b01-existing-fixture-assessment.md), 74–109 | Historical build/log/member binding gaps in earlier audit | Unknown build/log is no longer automatically fatal for acquired replay; rights and member binding remain independent. No retrospective PASS of any candidate. |
| [M2](../migration-stages.md), 71–110 | Actual legacy reader digest/build/scope, native raw and structured outcomes, preselected rollback | Unchanged. Reader identity is NOT the unknown historical writer. No after-write fallback. |
| [M3](../migration-dag.md), 93–123; B01 prerequisites | Qualified parents before affected production | Unchanged. Completing this document cannot release B01-gated production. Never archive/unblock B01 or unreviewed prerequisites to bypass edges. |
| [B01-L](b01-writer-license-decision.md), 8–41; controlling B01 comments | No separately obtained commercial authorization / added fees | Unchanged. Neither class licenses writer execution, output redistribution or procurement. |

## Normative evidence classes (schema_version=1)

The enum is exactly `acquired-immutable` or `generated-reproducible`. A future
reviewed B01 validator extension MUST bind each fixture to its class and an
associated `schema_version=1` record, without silently accepting new nulls in the
existing accepted manifest. Existing records without the extension keep their
current validation; no migration/default to the permissive class is implicit.
This card's companion JSON is an assessment, NOT an accepted-fixture manifest.

For both classes, before fixture acceptance require:

- Exact source project/version/revision and paths; immutable retrievable or
  committed authorized bytes; each archive/part's full SHA-256 and byte length;
  volume order, membership and entrypoint. URL or Git SHA-1 is not SHA-256.
- Complete actual member inventory, full byte hashes/lengths and metadata including
  names and link targets, with source/rights mapping, exceptions, notice files and
  review record. Do not equate expected metadata or CRC with complete payloads.
- Separately reviewed container, member and metadata redistribution applicability;
  preserve applicable copyright, permission and disclaimer texts. Repository-wide
  distribution attribution plus contribution history is affirmative evidence;
  a new personal grant is not universally mandatory. It is not a warranty of
  authority over unidentified third-party members. Ambiguity is not permission.
- Actual pinned native legacy reader executable digest, build/toolchain/OS/CPU,
  filesystem/locale, exact argv/environment, raw stdout/stderr/exit and numeric
  HRESULT/NOperationResult/CArcErrorInfo definedness/flags at the measured levels.
  Stable operation/item identity, ordered callbacks and partial side effects remain.
- Windows MSVC x64, Linux GCC x64 and macOS Apple clang arm64 measurements with
  repeated clean runs, uninstrumented controls and independent review. No Wine or
  cross-build as native Windows evidence. CLI results do not prove FFI/GUI parity.

`acquired-immutable`:

- `generator`, `version`, historical build/package/executable digests and invocation
  may be null ONLY when unavailable, each accompanied by an explicit unknown reason
  and the inspected evidence references. Record known values rather than erasing
  them. Decoder/unpack version, signature, filename, timestamp, contributor name or
  reader version MUST NOT be substituted for historical writer identity.
- Claim only replay of identified fixed bytes under measured readers/platforms.
  No named-writer/version interoperability, regeneration or deterministic authoring
  claim follows. Repeat reader execution is not repeat archive generation.
- Archive/member hashes and rights/native acceptance fields are NOT allowed to
  remain null in accepted fixtures. Nulls in this pre-acquisition assessment are
  intentional evidence gaps and never accepted corpus placeholders.

`generated-reproducible`:

- Keep all B01-W prospective writer/package/executable/version/build/log, bundled
  manual/terms, source recipe/rights, metadata/order, exact argv, resource budgets,
  independent repeat authoring and output comparison controls. Different repeat
  hashes require explanation/review, not fabricated deterministic equivalence.
- Do not relabel a newly generated fixture as acquired merely to evade missing
  campaign records. A later derivative of acquired bytes records its actual
  transformation tool/version/recipe/base hashes; the base's historical unknowns
  may remain null, but the performed transformation is never unknown by design.

## Acquired case-intent equivalence, not recipe identity

For this pilot, O1 explicitly removes the requirement that the three selected
families reproduce B01-W's `ALL` member names/content/order, fixed timestamps,
`Rar.exe` switches, 65536-byte part size, exact dictionary/thread setting or
repeat-generation outputs. Their actual values MUST instead be inventoried.
B01-W's prospective commands are not attributed to these historical files.

This changes the means of producing an input, NOT the behavior/coverage target.
Only R4-OLDVOL, R5-LZ-SOLID and R5-VOL have candidates in this pilot. Preserve
stored/non-solid old-name volume intent, modern compressed solid intent and
modern stored/non-solid native multipart intent respectively. Check actual format,
method and handler selection; `rar3-old` and `ver=20` do not prove all Rar3 methods
or a particular writer. All other eight-case rows remain explicitly unqualified.
Empty member, binary/text repetition and nested-path features of the original
recipe that are not demonstrated by these files remain uncovered obligations;
do not silently drop them or claim one candidate substitutes for every case.

Required operation and derivative coverage remains B01-W 328–382: list/test/extract,
actual create refusal; missing first/middle/last volume and non-first entrypoint;
probing; justified header/data/truncation cases and raw/numeric distinctions.
Recipe-specific corruption offsets/member searches may only be replaced by a
reviewed, byte-layout-verified equivalent after acquisition; never flip a guessed
offset or pretend `sequence.bin` exists. Unsupported RAR methods, nested chains,
Rar1/Rar2, PPM/LZ/filter transitions, encrypted/password, code-page, filesystem,
large-file, FFI and GUI/desktop gaps stay visible under their owning prerequisites.

## Future validator acceptance and negative controls (not implemented here)

A separately authorized B01 implementation must prove unchanged controls pass,
and reject: invalid/missing evidence class; generated records with unknown writer;
acquired unknowns without reasons; invented named-writer/regeneration claims;
missing accepted input/member digests; altered archive byte, member hash, volume
order/membership, class binding, raw output or structured/numeric error record.
Bind derivatives to base hashes. Reject missing platform reports or unmeasured
operation scope rather than filling defaults. Existing golden data stays immutable.

Lifecycle is policy documentation -> independent review -> explicit bounded import
resolution if warranted -> authorized acquisition/quarantine -> actual rights/byte
binding and native qualification -> independent B01 review. None is collapsed
into another. Reviewer PASS may complete only this policy/rights card and post its
reviewed findings back to B01. No approval of unreviewed B01 implementation
`9d01d5069f5b117aa5c69dd5cc62f090869d7650`, shared merge, release or follow-up audit.

Documentation-only: no executable/native builds apply because no runtime changed
and running archives is expressly outside scope. Reproducible documentation/source
checks and actual results are in the companion report and review metadata.
