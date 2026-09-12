// b05_password_harness.cpp
//
// B05-MAN harness. Exercises the retained legacy C++ IPassword callback
// boundary (CPP/7zip/IPassword.h: ICryptoGetTextPassword,
// ICryptoGetTextPassword2) directly -- NOT the CLI -p flag -- against the
// unmodified 7z.dll/7z.so archive engine. Modeled on the existing retained
// sample client CPP/7zip/UI/Client7z/Client7z.cpp (same load-library +
// CreateObject + password-callback pattern), extended with a
// --password-mode selector so every state the CLI -p flag cannot produce
// (defined-empty, prompt cancel, prompt EOF, wrong vs undefined) is
// directly selectable and observable.
//
// This file adds NO new archive/codec/crypto/password semantics: it is a
// driver that implements the SAME retained interfaces the console/GUI/FM
// callers already implement (see CArchiveOpenCallback /
// CArchiveExtractCallback / CArchiveUpdateCallback in Client7z.cpp, and
// COpenCallbackConsole / CExtractCallbackConsole / CUpdateCallbackConsole
// in CPP/7zip/UI/Console/*). It calls into the retained engine exactly as
// those callers do; it does not reimplement or bypass any crypto.
//
// Build: see ../BUILD.md. Requires the retained 7z.dll (Windows) /
// 7z.so (Linux) built unmodified from CPP/7zip/Bundles/Format7zF, plus the
// unmodified C/CPP sources listed in ARC.mak, exactly like Client7z.

#include "StdAfx.h"

#include <stdio.h>
#include <string.h>

#include "../../../Common/MyWindows.h"
#include "../../../Common/MyInitGuid.h"

#include "../../../Common/Defs.h"
#include "../../../Common/IntToString.h"
#include "../../../Common/StringConvert.h"

#include "../../../Windows/DLL.h"
#include "../../../Windows/FileDir.h"
#include "../../../Windows/FileFind.h"
#include "../../../Windows/FileName.h"
#include "../../../Windows/NtCheck.h"
#include "../../../Windows/PropVariant.h"
#include "../../../Windows/PropVariantConv.h"

#include "../../Common/FileStreams.h"

#include "../../Archive/IArchive.h"

#include "../../IPassword.h"
#include "../../../../C/7zVersion.h"

#ifdef _WIN32
extern HINSTANCE g_hInstance;
HINSTANCE g_hInstance = NULL;
#endif

Z7_DIAGNOSTIC_IGNORE_CAST_FUNCTION

// 7z format GUID, same constant Client7z.cpp uses.
#define DEFINE_GUID_ARC(name, id) Z7_DEFINE_GUID(name, \
  0x23170F69, 0x40C1, 0x278A, 0x10, 0x00, 0x00, 0x01, 0x10, id, 0x00, 0x00);

enum { kId_Zip = 1, kId_7z = 7 };

DEFINE_GUID_ARC(CLSID_Format7z, kId_7z)
DEFINE_GUID_ARC(CLSID_FormatZip, kId_Zip)

using namespace NWindows;
using namespace NFile;
using namespace NDir;

#ifdef _WIN32
#define kDllName "7z.dll"
#else
#define kDllName "7z.so"
#endif

// ---------------------------------------------------------------------
// Output helpers. Everything the harness prints goes through Print() so a
// single choke point exists for the redaction contract: the harness must
// NEVER pass a real/synthetic password value to Print() except inside the
// one deliberately-labeled "harness self-check" block used by the
// redaction NEGATIVE control (see --leak-selfcheck below), which exists
// solely so the human can verify check_no_leak.py actually detects a
// leak when one is deliberately present.
// ---------------------------------------------------------------------

static void Print(const char *s) { fputs(s, stdout); fflush(stdout); }
static void PrintErr(const char *s) { fputs(s, stderr); fflush(stderr); }

static void PrintLine(const char *s) { Print(s); Print("\n"); }

static void Convert_UString_to_AString(const UString &s, AString &temp)
{
  UnicodeStringToMultiByte2(temp, s, (UINT)CP_UTF8);
}

static void Print(const UString &s)
{
  AString as;
  Convert_UString_to_AString(s, as);
  Print(as.Ptr());
}

// ---------------------------------------------------------------------
// Password mode: the central thing this harness adds beyond Client7z.
// Selected once on the command line and applied to whichever password
// callback the engine calls (open / extract / update).
// ---------------------------------------------------------------------
enum class PwMode
{
  kUndefined,     // caller never defines a password; CryptoGetTextPassword
                   // reports failure (mirrors "not defined" branches already
                   // present in Client7z.cpp and the console callbacks).
  kDefinedEmpty,  // caller DOES define a password, value is the empty string.
                   // Not reachable via CLI -p (an empty -p argument cannot be
                   // told apart from "no -p" on most shells/argv parsers, and
                   // the existing CLI parser requires PostStrings[0] to be
                   // non-empty for -p to register as ThereIs+non-empty in
                   // some paths -- this harness makes the state explicit and
                   // unambiguous instead of relying on shell quoting).
  kWrong,         // caller defines a syntactically valid but incorrect value.
  kCorrect,       // caller defines the correct value (passed by --password).
  kCancel,        // simulates an interactive prompt cancel: the callback
                   // returns E_ABORT without ever supplying a string, exactly
                   // as CArchiveOpenCallback::CryptoGetTextPassword does in
                   // Client7z.cpp's "#else" branch (PrintError + E_ABORT).
  kEof,           // simulates a prompt hitting EOF with no characters typed:
                   // callback returns a distinct HRESULT (E_ABORT here too,
                   // by construction) but the harness LOGS which branch fired
                   // so the human can distinguish "cancel" from "EOF" in the
                   // per-check evidence even though this harness intentionally
                   // gives them the same return code -- see BUILD.md and the
                   // runbook Section 4 for why per-item vs per-call callers
                   // cannot always tell these apart from HRESULT alone, and
                   // Console's own GetPassword_HRESULT (UserInputUtils.cpp)
                   // which returns E_INVALIDARG/E_FAIL/E_ABORT for exactly
                   // this reason.
};

static PwMode g_PwMode = PwMode::kUndefined;
static UString g_PwValue;         // used for kCorrect / kWrong / non-ASCII

// Every password-callback invocation increments this and prints a
// call-numbered, VALUE-FREE log line, so per-item vs per-call behavior is
// externally observable without ever printing the secret itself.
static unsigned g_PwCallCount = 0;

static void LogPwCall(const char *which)
{
  g_PwCallCount++;
  char buf[256];
  snprintf(buf, sizeof(buf), "[harness] password-callback #%u fired: %s (mode=",
           g_PwCallCount, which);
  Print(buf);
  switch (g_PwMode)
  {
    case PwMode::kUndefined:    Print("undefined"); break;
    case PwMode::kDefinedEmpty: Print("defined-empty"); break;
    case PwMode::kWrong:        Print("wrong"); break;
    case PwMode::kCorrect:      Print("correct"); break;
    case PwMode::kCancel:       Print("cancel"); break;
    case PwMode::kEof:          Print("eof"); break;
  }
  PrintLine(")");
}

// Central decision used by both ICryptoGetTextPassword and
// ICryptoGetTextPassword2 implementations below. Returns S_OK/E_ABORT per
// mode, and fills passwordIsDefined / password accordingly. This function
// never prints the password itself.
static HRESULT ResolvePassword(bool &passwordIsDefined, UString &password)
{
  switch (g_PwMode)
  {
    case PwMode::kUndefined:
      passwordIsDefined = false;
      password.Empty();
      return S_OK; // ICryptoGetTextPassword2 callers read passwordIsDefined;
                   // ICryptoGetTextPassword-only callers get an empty BSTR,
                   // see CryptoGetTextPassword() below for the distinct
                   // "hard fail" behavior matching Client7z's #else branch.
    case PwMode::kDefinedEmpty:
      passwordIsDefined = true;
      password.Empty();
      return S_OK;
    case PwMode::kWrong:
    case PwMode::kCorrect:
      passwordIsDefined = true;
      password = g_PwValue;
      return S_OK;
    case PwMode::kCancel:
      passwordIsDefined = false;
      password.Empty();
      return E_ABORT; // matches Client7z.cpp's PrintError()+E_ABORT branch,
                        // i.e. the same code path 7z takes today when no
                        // password source is wired up.
    case PwMode::kEof:
      passwordIsDefined = false;
      password.Empty();
      return E_ABORT; // see class comment: this harness intentionally cannot
                        // give EOF a different HRESULT than cancel through
                        // this callback alone; the LogPwCall() line is what
                        // lets the human tell which state was requested.
  }
  return E_ABORT;
}

// ---------------------------------------------------------------------
// Archive Open callback
// ---------------------------------------------------------------------
class CArchiveOpenCallback Z7_final:
  public IArchiveOpenCallback,
  public ICryptoGetTextPassword,
  public CMyUnknownImp
{
  Z7_IFACES_IMP_UNK_2(IArchiveOpenCallback, ICryptoGetTextPassword)
public:
  CArchiveOpenCallback() {}
};

Z7_COM7F_IMF(CArchiveOpenCallback::SetTotal(const UInt64 *, const UInt64 *)) { return S_OK; }
Z7_COM7F_IMF(CArchiveOpenCallback::SetCompleted(const UInt64 *, const UInt64 *)) { return S_OK; }

Z7_COM7F_IMF(CArchiveOpenCallback::CryptoGetTextPassword(BSTR *password))
{
  LogPwCall("Open.CryptoGetTextPassword");
  bool defined = false;
  UString pw;
  HRESULT hr = ResolvePassword(defined, pw);
  if (hr != S_OK)
  {
    PrintLine("[harness] password prompt aborted (open)");
    return hr;
  }
  if (!defined)
  {
    // Mirrors Client7z.cpp's CArchiveOpenCallback::CryptoGetTextPassword
    // "not defined" branch exactly: this single-return-value interface has
    // no way to say "not defined" except failing the call.
    PrintLine("[harness] password not defined (open) -- reporting failure per legacy ICryptoGetTextPassword contract");
    return E_ABORT;
  }
  return StringToBstr(pw, password);
}

// ---------------------------------------------------------------------
// Archive Extract callback
// ---------------------------------------------------------------------
class CArchiveExtractCallback Z7_final:
  public IArchiveExtractCallback,
  public ICryptoGetTextPassword,
  public CMyUnknownImp
{
  Z7_IFACES_IMP_UNK_2(IArchiveExtractCallback, ICryptoGetTextPassword)
  Z7_IFACE_COM7_IMP(IProgress)

  CMyComPtr<IInArchive> _archiveHandler;
  FString _directoryPath;
  UString _filePath;
  FString _diskFilePath;
  bool _extractMode;
  struct { bool isDir; } _pfi;
  COutFileStream *_outFileStreamSpec;
  CMyComPtr<ISequentialOutStream> _outFileStream;

public:
  UInt64 NumErrors;
  UInt64 NumOK;

  void Init(IInArchive *h, const FString &dir)
  {
    NumErrors = 0; NumOK = 0;
    _archiveHandler = h; _directoryPath = dir;
    NName::NormalizeDirPathPrefix(_directoryPath);
  }
};

Z7_COM7F_IMF(CArchiveExtractCallback::SetTotal(UInt64)) { return S_OK; }
Z7_COM7F_IMF(CArchiveExtractCallback::SetCompleted(const UInt64 *)) { return S_OK; }

Z7_COM7F_IMF(CArchiveExtractCallback::GetStream(UInt32 index,
    ISequentialOutStream **outStream, Int32 askExtractMode))
{
  *outStream = NULL;
  _outFileStream.Release();
  {
    NCOM::CPropVariant prop;
    RINOK(_archiveHandler->GetProperty(index, kpidPath, &prop))
    _filePath = (prop.vt == VT_BSTR) ? UString(prop.bstrVal) : UString(L"[Content]");
  }
  if (askExtractMode != NArchive::NExtract::NAskMode::kExtract)
    return S_OK;
  {
    NCOM::CPropVariant prop;
    RINOK(_archiveHandler->GetProperty(index, kpidIsDir, &prop))
    _pfi.isDir = (prop.vt == VT_BOOL) && VARIANT_BOOLToBool(prop.boolVal);
  }
  {
    int slashPos = _filePath.ReverseFind_PathSepar();
    if (slashPos >= 0)
      CreateComplexDir(_directoryPath + us2fs(_filePath.Left(slashPos)));
  }
  FString fullProcessedPath = _directoryPath + us2fs(_filePath);
  _diskFilePath = fullProcessedPath;
  if (_pfi.isDir)
  {
    CreateComplexDir(fullProcessedPath);
  }
  else
  {
    NFind::CFileInfo fi;
    if (fi.Find(fullProcessedPath))
      DeleteFileAlways(fullProcessedPath);
    _outFileStreamSpec = new COutFileStream;
    CMyComPtr<ISequentialOutStream> outStreamLoc(_outFileStreamSpec);
    if (!_outFileStreamSpec->Create_ALWAYS(fullProcessedPath))
    {
      PrintLine("[harness] ERROR: cannot open output file");
      return E_ABORT;
    }
    _outFileStream = outStreamLoc;
    *outStream = outStreamLoc.Detach();
  }
  return S_OK;
}

Z7_COM7F_IMF(CArchiveExtractCallback::PrepareOperation(Int32 askExtractMode))
{
  _extractMode = (askExtractMode == NArchive::NExtract::NAskMode::kExtract);
  return S_OK;
}

Z7_COM7F_IMF(CArchiveExtractCallback::SetOperationResult(Int32 operationResult))
{
  char buf[128];
  if (operationResult == NArchive::NExtract::NOperationResult::kOK)
  {
    NumOK++;
    snprintf(buf, sizeof(buf), "[harness] item result OK: ");
    Print(buf);
    Print(_filePath);
    PrintLine("");
  }
  else
  {
    NumErrors++;
    snprintf(buf, sizeof(buf), "[harness] item result CODE=%d for: ", (int)operationResult);
    Print(buf);
    Print(_filePath);
    PrintLine("");
  }
  if (_outFileStream) { RINOK(_outFileStreamSpec->Close()) }
  _outFileStream.Release();
  return S_OK;
}

Z7_COM7F_IMF(CArchiveExtractCallback::CryptoGetTextPassword(BSTR *password))
{
  LogPwCall("Extract.CryptoGetTextPassword");
  bool defined = false;
  UString pw;
  HRESULT hr = ResolvePassword(defined, pw);
  if (hr != S_OK)
  {
    PrintLine("[harness] password prompt aborted (extract)");
    return hr;
  }
  if (!defined)
  {
    PrintLine("[harness] password not defined (extract) -- reporting failure per legacy ICryptoGetTextPassword contract");
    return E_ABORT;
  }
  return StringToBstr(pw, password);
}

// ---------------------------------------------------------------------
// Archive Update callback (create), uses ICryptoGetTextPassword2 which DOES
// carry an explicit passwordIsDefined out-parameter -- this is the
// interface that makes "defined-empty" externally distinguishable from
// "undefined" at the type level, per IPassword.h's own doc comment.
// ---------------------------------------------------------------------
struct CDirItem: public NWindows::NFile::NFind::CFileInfoBase
{
  UString Path_For_Handler;
  FString FullPath;
  CDirItem(const NWindows::NFile::NFind::CFileInfo &fi): CFileInfoBase(fi) {}
};

class CArchiveUpdateCallback Z7_final:
  public IArchiveUpdateCallback2,
  public ICryptoGetTextPassword2,
  public CMyUnknownImp
{
  Z7_IFACES_IMP_UNK_2(IArchiveUpdateCallback2, ICryptoGetTextPassword2)
  Z7_IFACE_COM7_IMP(IProgress)
  Z7_IFACE_COM7_IMP(IArchiveUpdateCallback)

public:
  FString DirPrefix;
  const CObjectVector<CDirItem> *DirItems;
  bool m_NeedBeClosed;

  CArchiveUpdateCallback(): DirItems(NULL), m_NeedBeClosed(false) {}
  ~CArchiveUpdateCallback() { Finilize(); }
  HRESULT Finilize() { m_NeedBeClosed = false; return S_OK; }

  void Init(const CObjectVector<CDirItem> *dirItems) { DirItems = dirItems; m_NeedBeClosed = false; }
};

Z7_COM7F_IMF(CArchiveUpdateCallback::SetTotal(UInt64)) { return S_OK; }
Z7_COM7F_IMF(CArchiveUpdateCallback::SetCompleted(const UInt64 *)) { return S_OK; }

Z7_COM7F_IMF(CArchiveUpdateCallback::GetUpdateItemInfo(UInt32,
      Int32 *newData, Int32 *newProperties, UInt32 *indexInArchive))
{
  if (newData) *newData = BoolToInt(true);
  if (newProperties) *newProperties = BoolToInt(true);
  if (indexInArchive) *indexInArchive = (UInt32)(Int32)-1;
  return S_OK;
}

Z7_COM7F_IMF(CArchiveUpdateCallback::GetProperty(UInt32 index, PROPID propID, PROPVARIANT *value))
{
  NCOM::CPropVariant prop;
  if (propID == kpidIsAnti) { prop = false; prop.Detach(value); return S_OK; }
  const CDirItem &di = (*DirItems)[index];
  switch (propID)
  {
    case kpidPath: prop = di.Path_For_Handler; break;
    case kpidIsDir: prop = di.IsDir(); break;
    case kpidSize: prop = di.Size; break;
    case kpidAttrib: prop = (UInt32)di.GetWinAttrib(); break;
    default: break;
  }
  prop.Detach(value);
  return S_OK;
}

Z7_COM7F_IMF(CArchiveUpdateCallback::GetStream(UInt32 index, ISequentialInStream **inStream))
{
  RINOK(Finilize())
  const CDirItem &dirItem = (*DirItems)[index];
  if (dirItem.IsDir()) return S_OK;
  CInFileStream *inStreamSpec = new CInFileStream;
  CMyComPtr<ISequentialInStream> inStreamLoc(inStreamSpec);
  FString path = DirPrefix + dirItem.FullPath;
  if (!inStreamSpec->Open(path))
  {
    PrintLine("[harness] WARNING: can't open input file");
    return S_FALSE;
  }
  *inStream = inStreamLoc.Detach();
  return S_OK;
}

Z7_COM7F_IMF(CArchiveUpdateCallback::SetOperationResult(Int32)) { m_NeedBeClosed = true; return S_OK; }
Z7_COM7F_IMF(CArchiveUpdateCallback::GetVolumeSize(UInt32, UInt64 *)) { return S_FALSE; }
Z7_COM7F_IMF(CArchiveUpdateCallback::GetVolumeStream(UInt32, ISequentialOutStream **)) { return S_FALSE; }

Z7_COM7F_IMF(CArchiveUpdateCallback::CryptoGetTextPassword2(Int32 *passwordIsDefined, BSTR *password))
{
  LogPwCall("Update.CryptoGetTextPassword2");
  bool defined = false;
  UString pw;
  HRESULT hr = ResolvePassword(defined, pw);
  if (hr != S_OK)
  {
    PrintLine("[harness] password prompt aborted (update)");
    return hr;
  }
  *passwordIsDefined = BoolToInt(defined);
  return StringToBstr(pw, password);
}

// ---------------------------------------------------------------------
// main
// ---------------------------------------------------------------------
static void PrintHelp()
{
  PrintLine("Usage:");
  PrintLine("  b05_password_harness a  <7z|zip> <archive> <file...> --password-mode MODE [--password VALUE]");
  PrintLine("  b05_password_harness l  <archive>                    --password-mode MODE [--password VALUE]");
  PrintLine("  b05_password_harness x  <archive> <outDir>            --password-mode MODE [--password VALUE]");
  PrintLine("  b05_password_harness selftest-leak                    (see BUILD.md / runbook 7.0)");
  PrintLine("");
  PrintLine("MODE in {undefined, defined-empty, wrong, correct, cancel, eof}");
  PrintLine("--password VALUE is required for MODE=wrong and MODE=correct; ignored otherwise.");
  PrintLine("--header-encrypt (create only): forces -mhe=on-equivalent (encrypt header + names, 7z only).");
}

int Z7_CDECL main(int numArgs, const char *args[])
{
  NT_CHECK
  #ifdef ENV_HAVE_LOCALE
  MY_SetLocale();
  #endif

  if (numArgs < 2)
  {
    PrintHelp();
    return 1;
  }

  AString cmd(args[1]);

  if (cmd == "selftest-leak")
  {
    // Negative control target for check_no_leak.py: deliberately writes a
    // marker secret to stdout so the human can confirm the checker script
    // actually flags a leak, before trusting its PASS verdicts elsewhere.
    // This is the ONLY place in this harness a secret-shaped string is ever
    // printed, and it is not a real or synthetic archive password -- it is
    // a fixed marker string, kept out of ResolvePassword()/LogPwCall()
    // entirely so ordinary runs can never reach this branch by accident.
    PrintLine("[harness] SELFTEST: deliberately printing marker below for check_no_leak.py's own negative control.");
    PrintLine("SELFTEST_MARKER_SECRET=b05-harness-selftest-leak-marker-77219");
    return 0;
  }

  // Parse --password-mode / --password / --header-encrypt anywhere in argv.
  CObjectVector<FString> positional;
  bool headerEncrypt = false;
  for (int i = 2; i < numArgs; i++)
  {
    AString a(args[i]);
    if (a == "--password-mode")
    {
      if (++i >= numArgs) { PrintErr("missing value for --password-mode\n"); return 2; }
      AString m(args[i]);
      if (m == "undefined") g_PwMode = PwMode::kUndefined;
      else if (m == "defined-empty") g_PwMode = PwMode::kDefinedEmpty;
      else if (m == "wrong") g_PwMode = PwMode::kWrong;
      else if (m == "correct") g_PwMode = PwMode::kCorrect;
      else if (m == "cancel") g_PwMode = PwMode::kCancel;
      else if (m == "eof") g_PwMode = PwMode::kEof;
      else { PrintErr("unknown --password-mode value\n"); return 2; }
    }
    else if (a == "--password")
    {
      if (++i >= numArgs) { PrintErr("missing value for --password\n"); return 2; }
      g_PwValue = GetUnicodeString(args[i]);
    }
    else if (a == "--header-encrypt")
    {
      headerEncrypt = true;
    }
    else
    {
      positional.Add(us2fs(GetUnicodeString(args[i])));
    }
  }

  if ((g_PwMode == PwMode::kWrong || g_PwMode == PwMode::kCorrect) && g_PwValue.IsEmpty())
  {
    PrintErr("--password-mode wrong|correct requires --password VALUE\n");
    return 2;
  }

  FString dllPrefix;
  #ifdef _WIN32
  dllPrefix = NDLL::GetModuleDirPrefix();
  #else
  {
    AString s(args[0]);
    int sep = s.ReverseFind_PathSepar();
    s.DeleteFrom(sep + 1);
    dllPrefix = s;
  }
  #endif

  NDLL::CLibrary lib;
  if (!lib.Load(dllPrefix + FTEXT(kDllName)))
  {
    PrintErr("Cannot load 7-zip library (expected beside this binary)\n");
    return 1;
  }

  Func_CreateObject f_CreateObject = Z7_GET_PROC_ADDRESS(
      Func_CreateObject, lib.Get_HMODULE(), "CreateObject");
  if (!f_CreateObject)
  {
    PrintErr("Cannot get CreateObject\n");
    return 1;
  }

  if (cmd == "a")
  {
    if (positional.Size() < 3) { PrintHelp(); return 2; }
    const FString &formatArg = positional[0];
    const FString &archiveName = positional[1];
    const GUID *clsid = (formatArg == FTEXT("zip")) ? (const GUID *)&CLSID_FormatZip : (const GUID *)&CLSID_Format7z;

    CObjectVector<CDirItem> dirItems;
    for (unsigned i = 2; i < positional.Size(); i++)
    {
      NFind::CFileInfo fi;
      if (!fi.Find(positional[i]))
      {
        PrintErr("Can't find input file\n");
        return 1;
      }
      CDirItem di(fi);
      di.Path_For_Handler = fs2us(positional[i]);
      di.FullPath = positional[i];
      dirItems.Add(di);
    }

    COutFileStream *outFileStreamSpec = new COutFileStream;
    CMyComPtr<IOutStream> outFileStream = outFileStreamSpec;
    if (!outFileStreamSpec->Create_NEW(archiveName))
    {
      PrintErr("can't create archive file (already exists? harness never overwrites)\n");
      return 1;
    }

    CMyComPtr<IOutArchive> outArchive;
    if (f_CreateObject(clsid, &IID_IOutArchive, (void **)&outArchive) != S_OK)
    {
      PrintErr("Cannot get class object for requested format\n");
      return 1;
    }

    if (headerEncrypt)
    {
      CMyComPtr<ISetProperties> setProperties;
      outArchive->QueryInterface(IID_ISetProperties, (void **)&setProperties);
      if (setProperties)
      {
        const wchar_t *names[] = { L"he" };
        NCOM::CPropVariant values[1] = { true };
        if (setProperties->SetProperties(names, values, 1) != S_OK)
        {
          PrintErr("SetProperties(he=on) failed -- format may not support header encryption\n");
          return 1;
        }
      }
      else
      {
        PrintErr("ISetProperties unsupported by this format -- --header-encrypt not applicable\n");
        return 1;
      }
    }

    CArchiveUpdateCallback *updateCallbackSpec = new CArchiveUpdateCallback;
    CMyComPtr<IArchiveUpdateCallback2> updateCallback(updateCallbackSpec);
    updateCallbackSpec->Init(&dirItems);

    HRESULT result = outArchive->UpdateItems(outFileStream, dirItems.Size(), updateCallback);
    updateCallbackSpec->Finilize();

    char buf[128];
    snprintf(buf, sizeof(buf), "[harness] UpdateItems HRESULT=0x%08X\n", (unsigned)result);
    Print(buf);
    snprintf(buf, sizeof(buf), "[harness] password-callback total calls=%u\n", g_PwCallCount);
    Print(buf);

    return (result == S_OK) ? 0 : 1;
  }
  else if (cmd == "l" || cmd == "x")
  {
    if (positional.Size() < 1) { PrintHelp(); return 2; }
    const FString &archiveName = positional[0];

    CMyComPtr<IInArchive> archive;
    // Try 7z then zip: list/extract auto-detect by probing both, since the
    // harness does not require the human to pass --format for read paths
    // (the retained engine itself determines applicability via Open()).
    const GUID *tryClsids[2] = { (const GUID *)&CLSID_Format7z, (const GUID *)&CLSID_FormatZip };
    bool opened = false;
    CInFileStream *fileSpec = NULL;
    CMyComPtr<IInStream> file;

    for (int t = 0; t < 2 && !opened; t++)
    {
      archive.Release();
      if (f_CreateObject(tryClsids[t], &IID_IInArchive, (void **)&archive) != S_OK)
        continue;
      fileSpec = new CInFileStream;
      file = fileSpec;
      if (!fileSpec->Open(archiveName))
      {
        PrintErr("Cannot open archive file\n");
        return 1;
      }
      CArchiveOpenCallback *openCallbackSpec = new CArchiveOpenCallback;
      CMyComPtr<IArchiveOpenCallback> openCallback(openCallbackSpec);
      const UInt64 scanSize = 1 << 23;
      HRESULT openRes = archive->Open(file, &scanSize, openCallback);
      if (openRes == S_OK)
      {
        opened = true;
      }
      else
      {
        char buf[128];
        snprintf(buf, sizeof(buf), "[harness] Open() with format candidate %d returned HRESULT=0x%08X\n", t, (unsigned)openRes);
        Print(buf);
        if (g_PwMode == PwMode::kCancel || g_PwMode == PwMode::kEof)
        {
          // A cancelled/EOF prompt legitimately aborts Open() before format
          // detection can even matter; do not keep probing the second
          // format after a deliberate abort -- surface it immediately.
          PrintLine("[harness] treating Open() failure as the expected abort outcome for this password-mode; not probing further formats");
          return 2;
        }
      }
    }
    if (!opened)
    {
      PrintErr("Cannot open file as archive (tried 7z, zip)\n");
      return 2;
    }

    if (cmd == "l")
    {
      UInt32 numItems = 0;
      archive->GetNumberOfItems(&numItems);
      char buf[64];
      snprintf(buf, sizeof(buf), "[harness] item count=%u\n", numItems);
      Print(buf);
      for (UInt32 i = 0; i < numItems; i++)
      {
        NCOM::CPropVariant prop;
        archive->GetProperty(i, kpidPath, &prop);
        Print("  ");
        if (prop.vt == VT_BSTR) Print(UString(prop.bstrVal));
        else Print("(no path)");
        PrintLine("");
      }
      return 0;
    }
    else
    {
      if (positional.Size() < 2) { PrintHelp(); return 2; }
      FString outDir = positional[1];
      CArchiveExtractCallback *extractCallbackSpec = new CArchiveExtractCallback;
      CMyComPtr<IArchiveExtractCallback> extractCallback(extractCallbackSpec);
      extractCallbackSpec->Init(archive, outDir);
      HRESULT result = archive->Extract(NULL, (UInt32)(Int32)(-1), false, extractCallback);
      char buf[128];
      snprintf(buf, sizeof(buf), "[harness] Extract() HRESULT=0x%08X items_ok=%llu items_error=%llu calls=%u\n",
               (unsigned)result,
               (unsigned long long)extractCallbackSpec->NumOK,
               (unsigned long long)extractCallbackSpec->NumErrors,
               g_PwCallCount);
      Print(buf);
      return (result == S_OK && extractCallbackSpec->NumErrors == 0) ? 0 : 1;
    }
  }

  PrintHelp();
  return 2;
}
