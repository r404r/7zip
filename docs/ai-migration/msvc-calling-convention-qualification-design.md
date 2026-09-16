# MSVC calling-convention qualification design

Status: design only; no qualification has been run and no Windows facade build is authorized.
Task: `t_a7a3f958`.

## 1. Decision and boundary

The calling-convention obligation can be tested without running the guarded
Windows facade makefile, but only as two deliberately separate kinds of evidence:

1. an AMD64 normative lane proves that the frozen declarations, the five current
   bridge definitions, an MSVC C caller, and a Rust `extern "C"` caller all use the
   one Windows x64 ABI and exact undecorated C names; and
2. an x86 diagnostic lane, built by the same MSVC installation on the AMD64
   runner, makes `__cdecl`, `__fastcall`, and `__stdcall` observably different. It
   proves that `ARCHIVE_BRIDGE_V1_CALL` overrides `/Gr` in declarations,
   definitions, function-pointer checks, and callback typedefs, and it executes
   mandatory negative controls.

The x86 lane is a compiler-semantic diagnostic, not a supported or qualified
32-bit product target. The AMD64 lane is the Q1 target lane. Both are necessary:
on x64 MSVC accepts and normally ignores `__cdecl`, `__fastcall`, and
`__stdcall`, so an AMD64 object alone cannot distinguish those three spellings.
A report that claims otherwise from an undecorated x64 symbol is invalid.

A future implementation of this design must be a separately named,
bridge-owned, non-product test target. It may compile the bridge-owned
`rust/bridge/archive_bridge_v1.cpp` to an object and may build a standalone ABI
probe, but it must not invoke `rust/bridge/makefile`, compile retained engine
translation units, link `archive_bridge_v1.dll`, or produce a facade package.
The fail-closed `!ERROR` at `rust/bridge/makefile:24-27` remains reachable and
unchanged. The qualification job must also run an explicit guard probe and
require that NMAKE fails at that `!ERROR`; success would fail the job.

This design is feasible, but its claim is intentionally narrow. It qualifies
MSVC's treatment of the ABI declarations and current bridge boundary source; it
does not qualify the retained facade or an archive operation.

## 2. Normative inventory

The authority is
[`qualification/archive_bridge_v1.h`](qualification/archive_bridge_v1.h).
[`qualification/abi-v1.md`](qualification/abi-v1.md), lines 68-77, requires all
exported and callback functions to use explicit `__cdecl` on Windows and records
Windows x64 MSVC as the Q1 native target. Revision 1 declares eight exports and
three callback function types. Every row below requires
`ARCHIVE_BRIDGE_V1_CALL`, which expands to `__cdecl` under `_WIN32`.

### 2.1 Export declarations

| Frozen header lines | Export | Required convention | x86 argument bytes |
| --- | --- | --- | ---: |
| 293-294 | `archive_bridge_v1_handshake` | `__cdecl` | 8 |
| 295-296 | `archive_bridge_v1_create_context` | `__cdecl` | 8 |
| 297 | `archive_bridge_v1_destroy_context` | `__cdecl` | 4 |
| 298-300 | `archive_bridge_v1_capabilities` | `__cdecl` | 12 |
| 301-304 | `archive_bridge_v1_open` | `__cdecl` | 20 |
| 305-308 | `archive_bridge_v1_entries` | `__cdecl` | 20 |
| 309-310 | `archive_bridge_v1_close` | `__cdecl` | 20 |
| 311-312 | `archive_bridge_v1_result_destroy` | `__cdecl` | 8 |

Only five of these names currently have definitions in
`rust/bridge/archive_bridge_v1.cpp`: `handshake`, `create_context`,
`destroy_context`, `capabilities`, and `result_destroy` (definitions begin at
lines 490, 504, 572, 595, and 658). `open`, `entries`, and `close` remain frozen
Q1 declarations, not implemented or qualified operations. The probe must not
turn those declarations into product exposure; test-only stub definitions exist
only to inspect all frozen signatures.

### 2.2 Callback function types

| Frozen header lines | Callback typedef | Required convention | x86 argument bytes |
| --- | --- | --- | ---: |
| 222 | `archive_bridge_v1_is_cancelled` | `__cdecl` | 4 |
| 223-224 | `archive_bridge_v1_on_progress` | `__cdecl` | 8 |
| 225-226 | `archive_bridge_v1_ask` | `__cdecl` | 12 |

The convention belongs inside each function-pointer declarator. Applying a
macro only to the containing `archive_bridge_v1_operation` struct, to a callback
adapter class, or to the exported function that receives the struct would not
constrain the callback pointer type.

## 3. MSVC model: `/Gr`, explicit attributes, and x64

`CPP/Build.mak:52-54` adds `-Gr` (MSVC also accepts the `/Gr` spelling) except
for ARM and ARM64. Microsoft documents `/Gr` as selecting `__fastcall` for
otherwise-unmarked x86 functions, while functions explicitly marked `__cdecl`,
`__stdcall`, or `__vectorcall` override it. Microsoft also documents `/Gr` as
ignored for non-x86 targets. Therefore:

- on x86, a declaration or definition with `ARCHIVE_BRIDGE_V1_CALL` must be
  `__cdecl` despite `/Gr`;
- on x86, an unmarked declaration or definition under `/Gr` becomes
  `__fastcall` and is observably wrong;
- on x64, `/Gr` is ignored and `__cdecl`, `__fastcall`, and `__stdcall` map to
  the platform's single ordinary x64 convention; and
- `__vectorcall` remains distinct on x64 and must not appear in this ABI.

The macro reliably controls a declaration only where it is present in the
function declarator. It controls a definition only where the definition includes
the reviewed header and/or repeats the macro on the definition. It controls a
function pointer only when it appears between the return type and `*`, as in the
three frozen callback typedefs. It can silently fail to constrain the intended
boundary if:

- a definition does not include the frozen/matched header and omits the macro;
- a second hand-written declaration, generated binding, cast, or `GetProcAddress`
  conversion uses an unannotated or different pointer type;
- a callback typedef moves the macro outside the parenthesized pointer
  declarator;
- a source is compiled without `_WIN32`, making the macro empty;
- a test observes only AMD64, where the ordinary convention keywords collapse;
- a linker `.def` file or alias hides the underlying decorated x86 symbol; or
- a check examines only source text or flags rather than a compiler artifact.

The future test must pass `/D_WIN32` only through a real Windows MSVC invocation;
it must not fake `_WIN32` on another compiler.

## 4. Observable object and DLL evidence

The job must retain literal output from:

- `dumpbin /symbols <object>` for each test object; and
- `dumpbin /exports <probe-dll>` for the standalone probe DLL.

There is no DUMPBIN `/noundecorate` option. `/symbols` is authoritative for the
raw COFF object definition: the parser must read the raw token after `|` and
must not substitute the parenthesized explanatory rendering DUMPBIN may append.
`/exports` proves the PE export-table name a dynamic caller can resolve. The
test must parse the export-table `name` column separately from any `= internal`
annotation. Neither view alone proves the whole claim; the controlled linker
inputs, COFF symbol, PE export name, and caller result are one evidence set.

For x86 C linkage, the expected forms are:

| Convention | COFF object spelling for `name` with N argument bytes |
| --- | --- |
| correct `__cdecl` | `_name` |
| wrong inherited `__fastcall` under `/Gr` | `@name@N` |
| wrong forced `__stdcall` | `_name@N` |

Thus the correct x86 handshake symbol is
`_archive_bridge_v1_handshake`; an omitted macro under `/Gr` produces
`@archive_bridge_v1_handshake@8`; forced `__stdcall` produces
`_archive_bridge_v1_handshake@8`. The argument-byte values for every export and
callback probe are listed in section 2 and must be asserted rather than matched
with a loose wildcard.

The PE export table is a separate assertion. With direct
`__declspec(dllexport)` and no `.def`, alias, `/EXPORT`, or linker pragma, MSVC's
x86 C `__cdecl` export-table name is the undecorated source name (`name`) even
though its internal COFF symbol is `_name`; DUMPBIN may show a line such as
`name = _name`. The wrong `__fastcall` and `__stdcall` mutations expose their
convention-decorated names instead. Therefore both AMD64 and the positive x86
diagnostic caller resolve the public source spelling `archive_bridge_v1_*`,
while the object parser requires the architecture-specific COFF spelling. The
x86 lane does not redefine the frozen public namespace.

For AMD64, each ordinary C symbol is exactly the unprefixed name, for example
`archive_bridge_v1_handshake`. `__cdecl`, `__fastcall`, and `__stdcall` all
produce that same ordinary x64 form. Consequently:

- AMD64 `dumpbin` proves C linkage, exact import/export spelling, absence of a
  `__vectorcall` suffix, and the architecture of the object;
- it does **not** distinguish `__cdecl` from `__fastcall` or `__stdcall`; and
- the x86 diagnostic lane is required to demonstrate that the source-level
  macro overrides `/Gr` rather than merely coinciding with x64's unified ABI.

The probe linker must export the test definitions directly with
`__declspec(dllexport)`. It must not use a `.def`, `/EXPORT`, linker pragma, or
alias that normalizes a wrong decorated name. The log parser must reject extra
`archive_bridge_v1_*` exports as well as missing ones and must retain both the
PE name and any displayed internal target.

## 5. Separate non-product target

A later implementation card should create one explicit target named
`msvc-abi-convention-probe`, with sources and scripts under a bridge-owned test
area. This design card creates none of them. The target has three products:

1. **Current-source objects.** Compile only
   `rust/bridge/archive_bridge_v1.cpp` with `/c /TP /Gr /W4 /WX` for AMD64 and
   x86. Do not link it. This inspects the five real definitions without compiling
   or linking retained engine translation units. Header dependencies may be
   read, but they are not target objects. The object is test evidence, not a
   facade binary.
2. **Contract-probe objects/DLL.** A standalone C/C++ test source includes an
   immutable copied-at-build-time view of the frozen header, defines test-only
   bodies for all eight declared functions, and defines three callback targets.
   Bodies only validate fixed integer/pointer sentinels and return fixed status
   values. The DLL must be named `archive_bridge_v1_cc_probe.dll`, carry a
   `NOT_PRODUCT` marker export/resource, and never contain retained engine code.
3. **Callers.** An MSVC C executable dynamically loads that probe DLL from an
   absolute temporary path. A separately linked Rust executable imports the
   probe through its generated import library, is launched with the probe DLL
   beside the executable in an otherwise isolated directory, and verifies the
   loaded module path before accepting results. The C loader has no fallback.
   A Rust link-time import cannot prevent Windows loader search before `main`;
   its canonical-path comparison is therefore a fail-closed detection control:
   a module resolved from `PATH` or a system directory makes the test fail
   before any result is accepted.

The target must be driven by a dedicated script that invokes `cl`, `link`, and
`dumpbin` directly after initializing Visual Studio's AMD64 and x86 environments.
It must not invoke either bridge makefile. Output goes to a temporary
`msvc-abi-convention-probe` directory, never a package, installer, release, or
normal facade output directory. The CI evidence bundle should contain commands,
versions, source/hash manifests, COFF headers, symbol/export dumps, caller logs,
and negative-control logs. The runnable probe DLL and executables should be
deleted before upload; they are not deliverables.

Before compiling, the script must require:

- the frozen and production header hashes are equal;
- the frozen header hash is
  `eabe714b31e2076735b8313c06618e5dbb3db4ea924cbef244b78a8b107ee26d`;
- `rust/bridge/makefile` still contains the fail-closed `!ERROR` before any
  target/include; and
- the target input allowlist contains no source under `C/`, `CPP/`, or `Asm/`
  except headers read while compiling the current bridge-owned translation unit.

A compile-only current-source object cannot be promoted into a facade: it has
unresolved retained-engine references and no DLL import/export policy. The
standalone probe DLL cannot be promoted either: it contains no retained engine
and returns only test sentinels. Any attempt to name either output
`archive_bridge_v1.dll`, add retained objects, use a production manifest, sign,
package, or publish it must fail the script.

## 6. Compile-time type enforcement

The generated positive check must create an explicit `__cdecl` function-pointer
type for every export and assign the frozen declaration to it. The pattern is:

```c
typedef int32_t (__cdecl *expected_handshake_fn)(
    const archive_bridge_v1_info *, archive_bridge_v1_info *);
static expected_handshake_fn const check_handshake =
    &archive_bridge_v1_handshake;
```

Equivalent declarations are required for the other seven exports. Callback
checks must compare each frozen typedef with an explicit `__cdecl` target, for
example:

```c
static uint32_t __cdecl probe_is_cancelled(void *user);
static archive_bridge_v1_is_cancelled const check_is_cancelled =
    &probe_is_cancelled;
```

Compile the C check with `/TC /Gr /W4 /WX` and a C++ companion with
`/TP /Gr /W4 /WX`; the latter may additionally use `std::is_same` static
assertions. `/WX` is mandatory because MSVC can diagnose an incompatible C
function-pointer assignment as a warning. Casts are forbidden: a cast would
suppress the evidence. The object check must follow compilation so that a
compiler accepting a construct under extensions cannot turn a warning-only
pass into a false qualification.

On AMD64 these types may compare equal because the ordinary convention keywords
are ignored. AMD64 assignment success is therefore positive compatibility
evidence, not a convention discriminator. The x86 compile is the discriminator.

## 7. Caller-side tests

### 7.1 MSVC C caller

The positive C caller loads the probe by absolute path and resolves all eight
exact public source names. The one unavoidable `GetProcAddress` conversion is
made directly from `FARPROC` to the corresponding explicit `__cdecl` pointer;
no untyped pointer is stored or forwarded after that checked loader boundary.
It invokes each function with unique nonzero sentinels and verifies return
values and out-parameters.
It also passes all three callback types. The probe invokes each callback and
verifies callback return values and argument identity. The caller verifies each
callback count is exactly one.

Run this positive test on AMD64 and x86. Build the x86 caller unoptimized with
`/Od /RTC1`; `/RTCs` (included by `/RTC1`) performs stack-pointer verification
and is specifically documented to detect a function-pointer calling-convention
mismatch. A clean exit plus all sentinel assertions is required. The AMD64 run
proves the actual Q1 x64 caller/callee ABI; the x86 run makes stack cleanup and
register placement testable.

### 7.2 Rust FFI caller

The Rust positive caller uses link-time `extern "C"` declarations with the exact
five currently implemented names and signatures from
`rust/crates/archive-engine-sys/src/link.rs`: `handshake`, `create_context`,
`destroy_context`, `capabilities`, and `result_destroy`. It links against the
probe import library. Before accepting any call result, it uses Windows module
inspection to require that the imported module's canonical path is the probe DLL
beside the test executable in the isolated directory. This is not an in-process
`LoadLibrary` claim: Windows resolves link-time imports before Rust `main`.

The current Rust sys source declares no Q1 callback types yet. The test-only
caller must therefore declare all three callback signatures directly as
`Option<unsafe extern "C" fn(...)>` from `abi-v1.md:68-77`, verify them on the
positive path, and report that these are contract probes rather than current sys
bindings. To make those pointers cross the DLL boundary, the probe defines a
test-only helper outside the `archive_bridge_v1_*` namespace that accepts an
`archive_bridge_v1_operation`, invokes `is_cancelled`, `on_progress`, and `ask`,
and returns fixed observations. This helper is excluded from the Q1 export-set
assertion and cannot be mistaken for a facade operation. The five current-name
imports and the callback-helper test are separate assertions. The probe checks
fixed test-only returns; it must not claim retained facade semantics or current
sys callback coverage.

Run the Rust caller for `x86_64-pc-windows-msvc`; an additional
`i686-pc-windows-msvc` positive run is diagnostic only. Record `rustc -vV` and
the installed target. Rust's Reference defines `extern "C"` as the dominant C
compiler ABI for the target and defines explicit `cdecl` only on x86_32.

These probe calls establish that MSVC C and Rust declarations can call the exact
boundary signatures and callback shapes. They do not execute the real retained
facade. Executing the real five exports on Windows would require the separately
gated facade link and is outside this target.

### 7.3 Runtime mismatch limits

On x86, a `__cdecl`/`__stdcall` mismatch disagrees about stack cleanup and can
corrupt ESP; a `__cdecl`/`__fastcall` mismatch also disagrees about argument
registers. A crash or later corruption without instrumentation is not a
repeatable test. The required deterministic mechanisms are:

- compile/link name mismatch, where normal typed imports cannot resolve a wrong
  decorated symbol;
- `/RTC1` stack-pointer verification at the process and call site that makes an
  intentionally convention-erased negative call; and
- distinct argument sentinels and exact callback counts to detect wrong register
  placement before accepting the call.

Every acceptance-critical x86 convention mutation also has a mandatory isolated
runtime negative. The module containing the mismatched call site must install
its own `_RTC_SetErrorFuncW` handler through the same RTC runtime instance used
by that instrumented module. The handler writes a fixed
`EXPECTED_RTC_STACK_MISMATCH` marker and terminates the process with a dedicated
nonzero exit code. This avoids an interactive assertion dialog or a report
followed by undefined continuation. Its log must contain that exact marker or
the separately selected sentinel assertion. A generic crash or any other
nonzero exit is a test failure, not a pass. No mismatched call is executed in
the main test process.

For an export mismatch the `/Od /RTC1` call site and handler registration are in
the C caller. For a callback mismatch they are inside the probe DLL's test-only
callback helper, so that helper translation unit must use `/Od /RTC1` and must
register the DLL-local RTC handler before making the mismatched callback. The
harness must not assume a handler registered in the executable controls a
statically linked RTC instance in the DLL.

On AMD64, changing among `__cdecl`, `__stdcall`, and `__fastcall` does not create
such a mismatch; the keywords map to the same ordinary x64 ABI. A design that
expects an x64 stack imbalance from those mutations is incorrect.

## 8. Mandatory negative controls

Negative controls operate only on generated temporary copies and probe sources.
They must never edit the frozen Q1 header or production source. Each mutation is
run separately from a clean generated tree, and every mutation must make at
least one specifically named check fail. The harness itself fails if a negative
case unexpectedly passes.

| Mutation | Required failing evidence |
| --- | --- |
| Remove `ARCHIVE_BRIDGE_V1_CALL` from exactly the generated x86 declaration and definition of `archive_bridge_v1_handshake` while retaining `/Gr` | Explicit-pointer assignment fails under `/WX`; raw object symbol changes from `_archive_bridge_v1_handshake` to `@archive_bridge_v1_handshake@8`; exact export-name/caller check fails. A separate forced runtime fixture resolves the decorated negative name, calls through the deliberately wrong `__cdecl` type, and must produce the local RTC marker or the exact argument-sentinel failure. |
| Change generated `archive_bridge_v1_is_cancelled` typedef to `__stdcall` while its target remains `__cdecl` | Callback assignment/static type check fails under `/WX`; a separate forced runtime fixture must bypass only that compile check, then the probe DLL's test-only callback helper and DLL-local RTC handler must emit the deterministic marker. |
| Force exactly one generated export, `archive_bridge_v1_close`, to `__stdcall` | Explicit-pointer assignment fails under `/WX`; raw x86 symbol is `_archive_bridge_v1_close@20`, not `_archive_bridge_v1_close`; exact export/caller check fails. A separate forced runtime fixture resolves the decorated negative name and must produce the caller-local RTC marker. |
| Remove the macro from one current-source definition in a generated temporary copy | The x86 current-source object symbol check must observe `@name@N` or compilation must reject conflict with the included frozen declaration. Either outcome is a required failure; silent pass is forbidden. |
| Change one Rust probe import to `extern "system"` for `i686-pc-windows-msvc` | Static import/name resolution or the isolated runtime negative must fail, demonstrating that Windows x86 `system` (`stdcall`) is not accepted as C `cdecl`. This is diagnostic and does not enable i686. |

The first three controls are acceptance-critical. The latter two defend the
actual-definition and Rust caller checks. Record expected and actual exit codes,
diagnostic IDs, raw symbol lines, and log hashes. Matching only generic text such
as `error` is insufficient.

AMD64 versions of the first three mutations are expected **not** to distinguish
the ordinary conventions. Record that result as a platform fact, but never count
it as a negative-control pass. The corresponding x86 failures are mandatory.

## 9. CI placement and architecture gate

Implement this later as a new required job named exactly
`MSVC ABI convention qualification (non-product)` on GitHub-hosted
`windows-latest`. This public repository does not require an operator-owned
machine for this build/ABI question.

At job start, print and archive:

- `runner.os`, `runner.arch`, `ImageOS`, and `ImageVersion`;
- `$env:PROCESSOR_ARCHITECTURE` and
  `[System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture`;
- `cl` banner for the AMD64 and x86 developer environments;
- `dumpbin /headers` machine fields for every object and probe DLL; and
- `rustc -vV` plus installed Rust targets.

Fail before compilation unless `runner.os == Windows`, `runner.arch == X64`,
`PROCESSOR_ARCHITECTURE == AMD64`, and runtime `OSArchitecture == X64`. Also
fail if an AMD64 artifact is not COFF machine `8664` or an x86 diagnostic
artifact is not machine `14C`. The host/runner requirement remains AMD64 even
when the diagnostic compiler target is x86.

The job sequence is:

1. verify hashes, source allowlists, architecture, and the retained guard;
2. invoke NMAKE on `rust/bridge/makefile` and require the exact fail-closed
   `U1050` guard outcome;
3. compile and inspect current-source AMD64 and x86 objects;
4. compile-time check all exports and callbacks in both architectures;
5. build/inspect/run positive C and Rust probes;
6. run every negative control in isolated subprocesses and require its named
   failure; and
7. delete runnable probe binaries, then upload only the evidence bundle.

No existing legacy workflow is modified by this design. The later implementation
card may add the job only after normal independent review.

## 10. Acceptance record

A qualifying run must publish a machine-readable manifest and human-readable
summary containing:

- exact repository commit and clean-tree status;
- SHA-256 for the frozen and production headers and equality result;
- every exact command and exit code;
- MSVC, linker, DUMPBIN, Windows image, and Rust versions;
- architecture checks and COFF machine values;
- expected/actual symbol and export tables for all eight exports and three
  callback targets;
- positive MSVC C and Rust caller results;
- every negative mutation, named failing check, diagnostic, exit code, and log
  hash;
- proof that NMAKE still stopped at the retained `!ERROR`; and
- an explicit scope statement copied from section 11.

A pass requires all positive checks and all negative controls. A positive-only
run, an x64-only run, a source grep, compiler flags without object inspection, or
an export-name-only listing is not sufficient. If a future MSVC version no
longer makes the x86 controls distinguishable, the job must fail and return for
architecture review rather than weakening the check.

## 11. What this does not establish

This qualification design and any future probe implementing it do **not**:

- qualify the retained facade;
- authorize a Windows facade build or bypass, remove, weaken, or conditionally
  skip the `!ERROR` guard;
- execute the real current exports against retained engine objects on Windows;
- qualify any archive operation on Windows or any other platform;
- establish archive-format, codec, encryption, password, filesystem, callback
  lifetime, cancellation, or retained-registration behavior;
- change `qualified_operations` from `0`;
- enable or qualify Windows x86 as a product target;
- authorize product exposure, packaging, signing, installers, tags, releases,
  or a merge to `dev-main`; or
- replace later S2a/B08 native facade, lifetime, sanitizer, and behavior work.

Lifting the Windows `!ERROR` guard requires **both** this calling-convention
obligation and the independently PASSed S2a-R portable registration redirection
(`t_13a346c7`, commit
`f6ca43ab5d370ef7a379a58e1735b45b17cd91f9`) to be qualified, followed by a
separate explicit human gate. Independent reviewer PASS on this design is not
that gate, is not operator approval, and does not authorize the facade build.

## 12. References

Repository authorities:

- `docs/ai-migration/qualification/archive_bridge_v1.h:8-12,222-226,293-312`
- `docs/ai-migration/qualification/abi-v1.md:68-83,257-261`
- `CPP/Build.mak:52-54`
- `rust/bridge/makefile:1-30`
- `rust/bridge/archive_bridge_v1.cpp:488-660`
- `rust/crates/archive-engine-sys/src/link.rs:7-59`

External toolchain authorities:

- Microsoft, `/Gd, /Gr, /Gv, /Gz (Calling Convention)`:
  <https://learn.microsoft.com/en-us/cpp/build/reference/gd-gr-gv-gz-calling-convention?view=msvc-170>
- Microsoft, `__cdecl`:
  <https://learn.microsoft.com/en-us/cpp/cpp/cdecl?view=msvc-170>
- Microsoft, decorated names:
  <https://learn.microsoft.com/en-us/cpp/build/reference/decorated-names?view=msvc-170>
- Microsoft, DUMPBIN `/SYMBOLS` and `/EXPORTS`:
  <https://learn.microsoft.com/en-us/cpp/build/reference/symbols?view=msvc-170>
  and
  <https://learn.microsoft.com/en-us/cpp/build/reference/dash-exports?view=msvc-170>
- Microsoft, `/RTC` run-time checks:
  <https://learn.microsoft.com/en-us/cpp/build/reference/rtc-run-time-error-checks?view=msvc-170>
- Rust Reference, external blocks and calling-convention ABI strings:
  <https://doc.rust-lang.org/reference/items/external-blocks.html>
