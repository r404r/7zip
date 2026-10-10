# Q1 selected retained-input license audit

Status: engineering inventory for independent review, not a distribution or legal
approval. No codec, encryption implementation, existing notice or legacy source
was changed. [Machine inventory](license-inventory.json) and
[per-product manifest](engine-build.json) are generated from actual native compile
logs and make inputs, not from all files found in a directory.

## Selected products and source attribution

The initial reference preserves the full Alone2 composition and separately builds
Format7zF plus Console. It is not the public-domain C decoder SDK. The audited
native product matrix currently contains:

| Platform | Alone2 units/resources | Format7zF units/resources | Console units/resources |
| --- | ---: | ---: | ---: |
| Linux x86_64 | 322 | 284 | 86 |
| Windows x64 | 329 | 286 | 84 |
| macOS arm64 | 323 | 285 | 86 |

These counts are per product, not disjoint totals or claims that every source byte
survives dead stripping. The Windows Alone2 count includes resource.rc; the lower
328 count in the raw observation refers only to translation units. The union of
selected units/resources and transitive make fragments has 373 distinct paths,
with per-file SHA-256 and license basis. File-header classification is SOURCE
attribution, not a claim that a compiled object containing included inline code
has only that license. The combined full engine remains subject to all applicable
LGPL, unRAR restriction and BSD obligations.

| Source attribution in the audited union | Paths | Basis |
| --- | ---: | --- |
| LGPL-2.1-or-later | 302 | DOC/License.txt:15-30, default for code without another stated license |
| Explicit public-domain source | 62 | Public-domain statement in that selected file's source header; never generalized to full engine |
| LGPL-2.1-or-later plus unRAR restriction | 6 | CPP/7zip/Compress/Rar* and DOC/License.txt:10,18-19,136-149 |
| BSD-3-Clause | 2 | CPP/7zip/Compress/LzfseDecoder.cpp and C/ZstdDec.c; DOC/License.txt:45-89 |
| BSD-2-Clause | 1 | C/Xxh64.c; DOC/License.txt:96-129 |

The audit retains assembly rather than converting it: Windows selects ml64 x86
assembly, macOS selects its arm64 composition, and canonical Linux uses the
portable optimized C composition. Source hashes, command flags and actual linked
registration enumeration distinguish these choices. `audit-inputs.py` resolves
actual emitted translation-unit/resource paths, NMAKE `/G` included fragments,
and an explicit GNU make variable whitelist. It does not scrape a speculative
codec directory list, dump process environments, or claim a complete preprocessor
header-dependency graph. Repository headers and resource includes remain available
at the exact source commit under their original notices; an eventual distribution
must carry the complete corresponding source/build materials, not just this list.

## Obligations carried forward

- Preserve DOC/License.txt, DOC/copying.txt and DOC/unRarLicense.txt. Their exact
  notice file hashes are in the inventory; they are notices, not objects assigned
  a fabricated source-code license. Preserve copyright and modified-source notices.
- LGPL-covered modifications and combined library distribution require the
  applicable corresponding source/interface/build materials and notices. A linked
  application distribution must select and satisfy the applicable LGPL mechanism,
  including relinking/replacement and reverse-engineering rights where required;
  calling something a shared library is not by itself compliance.
- Retain the unRAR restriction verbatim. RAR decoder material may not be used to
  recreate the proprietary RAR compression algorithm. The actual registry reports
  no RAR writer and the codec reports no RAR encoder; the validator checks both.
  Existing RAR reading remains selected, not silently removed to avoid the audit.
- Preserve BSD copyright/conditions/disclaimers and the BSD-3 non-endorsement term
  in applicable source/binary materials. The two BSD families are not interchangeable.
- Public-domain C/assembly components do not make LGPL C++ handlers/orchestration,
  Rust application code, Qt or the combined binary public domain.

No selected repository translation unit has an unresolved attribution under the
stated repository rule. This is a bounded engineering finding, not permission to
relicense the project. Selected OS/compiler runtimes are separately identified in
[toolchain pins](toolchains.json) and raw dependency/version captures. Microsoft
CRT/SDK, GNU runtime and Apple system runtime redistribution terms, installer
contents, source/relink delivery and final packaging remain explicit distribution
checks; Q1 does not ship an installer or approve static application linking.

## Native library and allocation boundary

Windows retained products compile with -MT and -EHsc; dumpbin shows their actual
OS DLL dependencies, rather than falsely labeling them /MD builds. Unix builds
record actual libstdc++/libgcc/glibc or Apple libc++/libSystem dependencies. The
retained Format7zF filename is 7z.so on both native Linux and macOS, and 7z.dll on
Windows. These legacy names are not the final facade install names.

The qualification observer uses original GetNumberOfFormats/GetHandlerProperty2
exports with matching native types. Windows Archive2.def declares them PRIVATE,
so the observer resolves them with LoadLibraryExW/GetProcAddress from the supplied
absolute library path, not through an import-library fiction or global PATH
changes. Property BSTRs are released before unloading. Unix observation links the
exact local library path. This is a test of the RETAINED library's registration
and native loading, not implementation of the new Rust facade.

New facade requests/results retain the allocation rules in [ABI v1](abi-v1.md):
C++ arenas and contexts are released only by their owning module/worker, no CRT
FILE*/STL/COM ownership or Rust deallocation crosses the C ABI, and callbacks must
quiesce before releasing operation state. No static-linking compliance shortcut is
inferred from this allocator boundary.

## Facade selection contract for S2a

The manifest is an actual ORACLE/reference input set, not a claim that Q1 already
built the future facade. S2a must produce its own actual selected-object manifest
and input-only handshake identity under [the schema](engine-build-schema.json).

- Retain handler/codec/crypto/C/assembly coverage from the full reference and the
  needed UI/Common coordination: CArchiveLink, SetProperties, scans, extraction/
  update policy when those operations become eligible, and HashCalc's separately
  added Hash handler. Link registration units deliberately and compare resulting
  capabilities; do not assume a static library archive retains constructors.
- Do not combine LoadCodecs.cpp's internal RegisterArc implementation with
  ArchiveExports.cpp's alternate product registration implementation indiscriminately.
  Format7zF is a comparison product, not another set of objects to duplicate into
  the facade alongside Alone2.
- Exclude Console entry points/parsing/printing/signal policy from the facade:
  CPP/7zip/UI/Console sources (including Main.cpp, MainAr.cpp and ConsoleClose.cpp)
  are oracle-only. Do not call Main2, install console handlers, or expose CLI text
  parsing as the engine API. Common stream/utilities needed by retained code are
  a different category; trace their actual dependencies rather than deleting them.
- Native GUI launchers, FileManager/Agent/Explorer presentation and Qt are not
  part of this reference facade selection. Do not compile all UI/Common merely
  because it has "Common" in the name; CompressCall.cpp is an example to exclude.
- Keep external plugin discovery disabled in the new application; the legacy
  plugin-capable Console/Format7zF products remain untouched comparison oracles.

S2a linkage is still subject to its actual input/ABI/lifetime review; Qt packages
and their obligations are owned by Q2, and release/distribution by later human
gates. A newly selected dependency or unclear obligation must block the affected
linkage/packaging decision rather than inherit an unrelated Q1 permission.
