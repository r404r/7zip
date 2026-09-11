# M0: current architecture

Status: source archaeology, not an implementation ADR or compatibility certification.
Task: `t_48d08249`; branch: `ai/migration-m0`; inspected baseline: `d1fcc44`.
The required bootstrap parent is already an ancestor of this worktree. No source,
fixture, build configuration, codec, encryption or GUI behavior is changed here.

Companion maps: [Win32 dependencies](win32-dependencies.md),
[engine boundaries](archive-engine-boundaries.md), [risks and validation](migration-risks.md).
Full source citations below use repository-relative paths and baseline line numbers;
short filenames/suffixes inherit the directory identified in their row or paragraph.
Symbols are the durable anchors if later commits move lines.

## Existing execution paths

```text
Console main -> Main2 / command parsing
                     -> CCodecs + CArchiveLink / format probing
                     -> ListArchives / Extract / UpdateArchive
                              -> IInArchive / IOutArchive
                              -> format handlers -> codecs / crypto -> C / assembly

Win32 File Manager WinMain -> CApp / CPanel -> Agent / IFolder interfaces
Win32 archive GUI WinMain  -> GUI option dialogs / progress workers
                              -> shared UI/Common orchestration -> same engine
Explorer DLL -> COM context menu -> operation dispatch / external GUI commands
```

* CLI entry: `CPP/7zip/UI/Console/MainAr.cpp:103`, `main`, installs console
  break handling and catches exceptions around `Main2`. The latter is defined in
  `CPP/7zip/UI/Console/Main.cpp:806`; it parses options (`CArcCmdLineParser`,
  line 908), loads codecs (1014), and calls `Extract` (1403), `ListArchives`
  (1526), and `UpdateArchive` (1602). Test mode uses extraction machinery, not a
  separate decoder implementation. This CLI executable is not a reentrant library
  API: it owns process output streams, signals and command-line exit mapping.
* File Manager: `CPP/7zip/UI/FileManager/FM.cpp:785`, `WinMain`, delegates to
  `WinMain2` (577). `g_App` (195) owns application state. Panels and archive-folder
  proxies are coupled to Win32 messages and controls, rather than a portable UI.
* Archive GUI: `CPP/7zip/UI/GUI/GUI.cpp:408`, `WinMain`, and `Main2` (137).
  `ExtractGUI.cpp` and `UpdateGUI.cpp` in that directory adapt dialogs/options to
  shared operation machinery. This is distinct from the browsing File Manager.
* Explorer: `CPP/7zip/UI/Explorer/DllExportsExplorer.cpp:182`,
  `DllGetClassObject`, constructs the shell COM class; `ContextMenu.cpp:586`,
  `CZipContextMenu::QueryContextMenu`, and `InvokeCommand` (1196) implement the
  shell entry path. The shell DLL is not the archive-format DLL.
* Other retained entry products: `CPP/7zip/Bundles/SFXCon/SfxCon.cpp:257`,
  `Main2`; `CPP/7zip/Bundles/SFXWin/SfxWin.cpp:238`, `WinMain`;
  `CPP/7zip/Bundles/SFXSetup/SfxSetup.cpp:122`, `WinMain`;
  `CPP/7zip/Bundles/LzmaCon/LzmaAlone.cpp:800`, `main`. Their existence is
  inventoried, not a promise of migrated feature parity. `UI/Far` is a separate
  integration surface; `UI/Client7z/Client7z.cpp:821` is an example client, not
  a full CLI replacement.

## Module and disposition inventory

Classification is a migration recommendation, not permission to edit production:
A = retain mature C/C++; B = wrap from Rust; C = later rewrite application policy
in Rust after characterization; D = isolate behind platform adapter; E = later
explicit decision. Combined classifications separate layers within a directory.

| Component | Existing responsibility and evidence | Class / intended treatment |
| --- | --- | --- |
| `C/`, `Asm/` | Primitive compression, checksums, crypto and CPU-specific paths; e.g. `C/LzmaDec.c`, `C/Aes.c`, `Asm/x86/AesOpt.asm` | A; no codec translation |
| `CPP/7zip/Compress/` | C++ coder/filter implementations and registration; `CPP/7zip/Common/CreateCoder.cpp:32`, `RegisterCodec` | A, reached through B |
| `CPP/7zip/Crypto/` | Format crypto, password derivation, random generator; `7zAes.cpp`, `WzAes.cpp`, `ZipCrypto.cpp`, `RandGen.h:35` | A; passwords reach it through retained callbacks |
| `CPP/7zip/Archive/` | Format probing, properties, extract/update; `Archive/IArchive.h`, `Archive/7z/7zHandler.cpp:682` | A + B; keep archive semantics |
| `CPP/7zip/Common/` | Streams, buffers, coder creation, progress plumbing; `FileStreams.h`, `CreateCoder.cpp` | A/B first; ownership stays C++ |
| `CPP/Common/` | Strings, vectors, COM-like support and command parsing; `MyCom.h:10`, `StringConvert.cpp:51` | B first; C only for independently characterized app helpers |
| `CPP/Windows/` | Both native Win32 wrappers and portable implementations; `FileIO.h:154` / `FileIO.h:387` | D, not a directory-wide delete |
| `CPP/7zip/UI/Common/` | Archive selection, paths, overwrite, filesystem callbacks, update planning; `Extract.cpp:278`, `Update.cpp:1125` | B first, C/D incrementally; not all UI/Common is portable |
| `CPP/7zip/UI/Console/` | CLI parsing, printing and user prompts | Existing oracle retained; C for a new CLI layer, not whole `Main2` FFI |
| `CPP/7zip/UI/Agent/` | Archive-as-folder proxy model and update/reopen | B initially; C candidate for future domain navigation |
| `CPP/7zip/UI/FileManager/`, `UI/GUI/` | Win32 controls, browsing, dialogs and progress | C presentation/app model + D native services; retain legacy UI until replacement validated |
| `CPP/7zip/UI/Explorer/` | Explorer COM shell integration and registration | D; retain separately from Qt GUI |
| `CPP/7zip/UI/Far/`, SFX products | Host integration / specialized launchers | E; remain intact, not implied M3 scope |
| `CPP/7zip/Bundles/`, make fragments | Product-specific composition | B/E; choose equivalent engine capability set before bridge build |
| `Lang/`, `.github/msi/` | Localization assets / Windows coexistence packaging | D/E; retain identities and provenance |

## Portable CLI is already present

`CPP/7zip/Bundles/Alone2/makefile.gcc:1` builds `7zz` and includes
`CPP/7zip/Bundles/Format7zF/Arc_gcc.mak:1`. Its `UI_COMMON_OBJS` (48) and
`CONSOLE_OBJS` (70) combine application services and engine code. Non-MinGW builds
use `MyWindows.o` (37), whereas MinGW includes registry/DLL objects (27).
The common arc fragment still includes `WIN_OBJS` (69): a path named Windows does
not imply a runtime Windows dependency. `CPP/Common/MyWindows.h:20` selects native
Windows definitions or a compatibility vocabulary for HRESULT/GUID/BSTR/FILETIME.

The native Linux/macOS workflow builds this product with make; Windows CI builds
MSVC products. Neither establishes that the Win32 File Manager runs on Unix.
The bootstrap parent reports native CLI verification; this M0 report does not
relabel that as desktop compatibility. No Qt, QML or Rust production layer is
introduced by this card.

## State, configuration and task model

* Engine registration state: `CPP/7zip/Archive/ArchiveExports.cpp:14` has
  `g_NumArcs`/`g_Arcs`; `CPP/7zip/Common/CreateCoder.cpp:15` has `g_NumCodecs`.
  `CCodecs` (`UI/Common/LoadCodecs.h:294`) also owns formats and optionally
  libraries. Freezing registration/loading before requests is an M2 candidate;
  safe simultaneous loading is not proven by this inventory.
* Process/app state: `Console/MainAr.cpp:23` output pointers;
  `Console/ConsoleClose.cpp:18` break counter; `FileManager/FM.cpp:195` `g_App`;
  `Common/StringConvert.cpp:260` `g_ForceToUTF8`;
  `UI/Common/ExtractingFilePath.cpp:13` `g_PathTrailReplaceMode`.
  Multiple independent Rust jobs must not mutate these as per-job options.
* Persistent settings: `CPP/7zip/UI/FileManager/RegistryUtils.cpp:58`,
  `SaveRegLang`/`ReadRegLang`, plus editor/viewer settings. Archive dialog settings
  live in `CPP/7zip/UI/Common/ZipRegistry.cpp`: UTF-8-name preference is saved
  at 275, defaults true at 319, loaded at 378. Extract/name-code-page selection
  is per operation/archive, not a global default to remember.
* Workers: `CPP/7zip/UI/FileManager/ProgressDialog2.h:292`,
  `CProgressThreadVirt`, starts work alongside a modal Win32 dialog (315-351).
  `ProgressDialog2.cpp:100`, `CProgressSync::CheckStop`, locks shared state,
  reports `E_ABORT` on stop and sleeps while paused. Codec threads are a separate
  layer: `CPP/Windows/Thread.h:12` wraps `C/Threads.h:39` with native Windows or
  pthread backing. Reusing engine parallelism does not make archive objects
  concurrently callable: `Archive/IArchive.h:305` explicitly forbids that.
* Fork browsing exception: `CAgentFolder::SetNameCodePage_ReOpen` is synchronous
  and invalidates proxies (`UI/Agent/ArchiveFolderOut.cpp:35`). The File Manager
  calls it with a null open callback (`PanelOperations.cpp:496`). Do not describe
  that operation as already cancellable.

## Assessment of provisional direction

Qt 6/QML -> CXX-Qt -> Rust application core -> mature C/C++ engine is consistent
with the observed separable CLI/engine and highly native desktop surface. It is
not a mechanical port of `CPanel` or an instruction to expose HWND through Rust.
CXX-Qt belongs between Qt objects and Rust presentation/application data; a
separate narrow C++ engine adapter should hide COM-like interfaces and allocation
rules. Retain native Explorer integration behind a Windows adapter.

M2 must settle bridge technology/packaging, models, thread ownership and queued UI
notifications after consulting this evidence. Qt licensing/deployment and actual
CXX-Qt toolchain viability remain to be verified; no alternative GUI framework is
approved. M1 must characterize the risky policy paths before Rust replaces them.
M3 requires reviewed M1 and M2; this M0 document does not authorize a skeleton,
engine bridge, GUI rewrite or codec rewrite.
