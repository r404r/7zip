# M0: Win32 and platform dependencies

Baseline `d1fcc44`, task `t_48d08249`. Static source evidence, not native runtime
certification. Disposition letters follow [current architecture](architecture-current.md):
A retain engine, B wrap, C later application rewrite, D platform adapter, E later decision.
See [risks](migration-risks.md) for prerequisite coverage and human gates.

## Dependency map

| Surface | Source anchor / symbol | Boundary and disposition |
| --- | --- | --- |
| Window lifetime and message loop | `CPP/7zip/UI/FileManager/FM.cpp:577`, `WinMain2`; `FM.cpp:785`, `WinMain`; `CPP/7zip/UI/GUI/GUI.cpp:408`, `WinMain` | C/D: Windows UI remains until Qt GUI parity; do not put HWND in domain models |
| Controls, dialogs and notifications | `CPP/Windows/Control/`; `CPP/7zip/UI/FileManager/ProgressDialog2.h:106`, `CProgressDialog`; `ProgressDialog2.h:307`, HWND parent of worker dialog | C/D: replace presentation later; progress synchronization is not a reusable QML object |
| Global window/module state | `CPP/7zip/UI/Explorer/DllExportsExplorer.cpp:59`, `g_hInstance`, `g_HWND`, `g_DllRefCount` | D: module/window lifetime is local to native host; no global window pointer in Rust core |
| Archive interface vocabulary | `CPP/Common/MyWindows.h:20`, native/compatibility branches; `CPP/7zip/Archive/IArchive.h:328`, `IInArchive`; `CPP/Common/MyCom.h:10`, `CMyComPtr` | B: COM-like archive ABI exists on Unix too; hide in C++ wrapper, not an OS COM service in the domain |
| Actual shell COM activation | `CPP/7zip/UI/Explorer/DllExportsExplorer.cpp:79`, `CShellExtClassFactory`; `DllGetClassObject` (182); `ContextMenu.h:29`, `IContextMenu`/`IShellExtInit` | D: real Explorer interfaces, host and DLL reference rules; cannot be replaced by an engine wrapper |
| Shell menu actions | `CPP/7zip/UI/Explorer/ContextMenu.cpp:586`, `QueryContextMenu`; `InvokeCommand` (1196), `InvokeCommandCommon` (1259) | D: translate selected native paths and verbs to operation requests; preserve shell's command-ID/language behavior |
| OLE drag/drop | `CPP/7zip/UI/FileManager/FM.cpp:632`, `OleInitialize`; `RegisterDragDrop` (1023); `PanelDrag.cpp:1690`, `DoDragDrop` | D/E: native data-object and temp-file lifetime need characterization; Qt drag/drop is not assumed equivalent |
| Delete/recycle behavior | `CPP/7zip/UI/FileManager/PanelOperations.cpp:116`, `CPanel::DeleteItems`; `SHFileOperationW` (197) | D/C: recycle vs permanent deletion and confirmation are data-loss-sensitive; retain until native oracle exists |
| Registry preferences | `CPP/Windows/Registry.h:14`, `CKey`; `CPP/7zip/UI/FileManager/RegistryUtils.cpp:58`, `SaveRegLang`/`ReadRegLang`; `CPP/7zip/UI/Common/ZipRegistry.cpp:275` | D: Rust settings service may map platform storage later, preserving defaults/migration semantics |
| File handles and metadata | `CPP/Windows/FileIO.h:154`, Windows `CFileBase`; POSIX variant (387); `CPP/7zip/Common/FileStreams.h` | D/B: HANDLE on Windows vs descriptor on POSIX remains adapter-owned; stream seek/size contracts stay intact |
| Enumeration, names and time | `CPP/Windows/FileFind.h`, `FileName.h`, `TimeUtils.h`; `CPP/7zip/UI/Common/EnumDirItems.cpp` | D/B: retain current scanner and conversion first; no universal UTF-8 filesystem assumption |
| Links/security/attributes | `CPP/7zip/UI/Common/ArchiveExtractCallback.cpp:2221`, `SetLink`; `SetAttrib` (2776), `SetSecurityInfo` (2795), `SetDirsTimes` (3171) | D/B: OS effect belongs outside format handlers, but existing implementation is compatibility policy, not disposable glue |
| Threads/synchronization | `CPP/Windows/Thread.h:12`, `CThread`; `C/Threads.h:44` HANDLE and (75) pthread structure; `CPP/Windows/Synchronization.h` | A/D: codec worker primitives stay; new application task ownership must not expose native handles |
| Console stop/encoding | `CPP/7zip/UI/Console/ConsoleClose.cpp:23`, `HandlerRoutine`, and (63) POSIX handler; `CPP/Common/StringConvert.cpp:51`, `MultiByteToUnicodeString2` | D/C: signal or control handler is executable-owned, not installed for each library request |
| DLL loading | `CPP/7zip/UI/Common/LoadCodecs.h:313`, `Libs`, `LoadDll` (341), `CreateArchiveHandler` (344); `CPP/Windows/DLL.h` | B/D: module lifetime must exceed all engine objects/callbacks; search-path and plugin policy require M2 decision |
| Packaging/coexistence | `.github/msi/7zip-fork.wxs`; `CPP/7zip/UI/Explorer/DllExportsExplorer.cpp:45`, fork shell identity | D/E: native installers/associations are separate from GUI; no release changes in M0 |

## Avoid the false Windows-directory boundary

`CPP/7zip/Bundles/Format7zF/Arc_gcc.mak:69` compiles `FileDir`, `FileFind`,
`FileIO`, `FileName`, `PropVariant`, `System`, and `TimeUtils` into the portable
product. In `CPP/Windows/FileIO.h:387`, `CFileBase` stores an integer descriptor,
closes it in destruction and uses POSIX `fstat`. `CPP/Windows/Thread.h:6` delegates
to `C/Threads.h`, which selects pthread on non-Windows. `CPP/Common/MyWindows.h`
provides BSTR, HRESULT and FILETIME compatibility declarations there.

Thus stripping `CPP/Windows` or replacing every HRESULT with a Win32 error would
break the existing Linux/macOS CLI. Conversely, seeing portable COM-like engine
interfaces does not prove that Explorer COM, OLE or window controls are portable.
Application/domain Rust must depend on operation values and opaque engine ownership,
not HWND, HANDLE, Registry, COM pointers, native dialogs or `PROPVARIANT` layout.

## Filesystem names are three separate concerns

1. Archive name decoding: the format handler owns encoding flags, Unicode extra
   fields and fallback properties. `CPP/7zip/Archive/Zip/ZipItem.cpp:405`,
   `CItem::GetUnicodeString`, checks EFS/Unicode extras before fallback; under
   Windows it also tries UTF-8 for Unix-host names without an explicit code page.
   `CPP/7zip/Archive/Tar/TarHandler.cpp:1021`, `CHandler::SetProperties`, has
   separate TAR code-page state. Do not implement a generic ZIP decoder in QML.
2. Filesystem mapping: `CPP/7zip/UI/Common/ExtractingFilePath.cpp:23`,
   `ReplaceIncorrectChars`, is platform-conditioned; trailing space/dot replacement
   defaults differ via `g_PathTrailReplaceMode` (13).
   `ArchiveExtractCallback.cpp:1081`, `CorrectPathParts`, and `CheckExistFile`
   (1246) feed actual extraction/overwrite decisions. Display names are not safe
   destination paths; identity cannot be a normalized display string alone.
3. Native string conversion/display: Windows uses `MultiByteToWideChar` in
   `CPP/Common/StringConvert.cpp:83`. Non-Windows conversion (262) defaults to
   `g_ForceToUTF8 = true` (260); it does not implement arbitrary Windows code-page
   conversion just because an integer code page reaches it. The file's note
   (229-233) says UString still uses surrogate pairs even with 32-bit wchar_t.
   FFI must explicitly convert code units rather than cast wchar_t buffers to
   Rust UTF-16 or assume all names fit Rust `String` losslessly.

`DOC/zip-name-encoding.txt` is useful feature documentation, but its short fallback
summary omits the ZIP Unix-host heuristic above. Likewise its statement about
non-Windows `-mcp` should not become an unconditional API theorem: source has
UTF-8 and locale branches. M1 should record actual per-platform behavior before
any expanded code-page support is proposed. No semantic change is made here.

## Fork desktop behavior to preserve

* `CPP/7zip/UI/Common/NameCodePageProps.h:116`, `AddNameCodePageProps`, emits
  handler-scoped properties. `UI/Common/SetProperties.cpp:48` filters the prefix
  case-insensitively and calls the setter even for an empty filtered list to reset
  reused handler state. Unprefixed properties preserve their previous meaning.
* `CPP/7zip/UI/GUI/ExtractGUI.cpp:250` adds the dialog's per-operation code page;
  `ExtractDialog.h:123` starts at Auto. It must not silently become a saved default.
* `CPP/7zip/UI/GUI/UpdateGUI.cpp:255` adds ZIP `cu` only if explicit name-encoding
  parameters do not take precedence. `UI/Common/ZipRegistry.cpp:319` defaults
  UTF-8 names on; persistence is distinct from extraction selection.
* `CPP/7zip/UI/FileManager/PanelOperations.cpp:430`, `GetNameCodePageAgent`,
  restricts eligible browsing objects; `CPanel::NameCodePage` (457) passes null
  progress callback at 496. `CAgent::CanReOpen` (`UI/Agent/Agent.cpp:1616`)
  requires a single handler and no shortened proxy paths. This must not be widened
  to nested in-memory archives or multi-handler chains without tests and approval
  for any semantic differences.
* `CPP/7zip/UI/Explorer/ContextMenu.cpp:627` takes `Lang_CriticalSection()`;
  the fork's language reload and identity checks in `.github/tests/` are source
  guards, not native UI automation. Keep both those guards and real desktop tests.

## Native validation contract

Native Windows is canonical for Win32 effects. M1 needs controlled temporary
fixtures for paths (UNC/long/reserved names), alternate streams, security and
attributes, overwrite/recycle/delete, code-page selections, archive reopen
rollback, OLE temp-file lifetime, settings and shell language/identity. CLI tests
alone cannot observe GUI selection/restoration or Explorer activation.

Linux/macOS need their own name, mode, link, timestamp and cancellation evidence;
Linux results are not macOS results. Wine and cross-compilation are useful
additional checks, not substitutes for canonical native evidence. Qt GUI and
Windows/Linux/macOS desktop integration must have separate later acceptance.
No missing desktop capability is silently replaced with a different framework.
