// ExtractDialog.cpp

#include "StdAfx.h"

#include "../../../Common/StringConvert.h"
#include "../../../Common/Wildcard.h"

#include "../../../Windows/FileName.h"
#include "../../../Windows/FileDir.h"
#include "../../../Windows/ResourceString.h"

#ifndef Z7_NO_REGISTRY
#include "../FileManager/HelpUtils.h"
#endif


#include "../FileManager/BrowseDialog.h"
#include "../FileManager/LangUtils.h"
#include "../FileManager/resourceGui.h"

#include "ExtractDialog.h"
#include "ExtractDialogRes.h"
#include "ExtractRes.h"

using namespace NWindows;
using namespace NFile;
using namespace NName;

extern HINSTANCE g_hInstance;

#ifndef Z7_SFX

static const UInt32 kPathMode_IDs[] =
{
  IDS_EXTRACT_PATHS_FULL,
  IDS_EXTRACT_PATHS_NO,
  IDS_EXTRACT_PATHS_ABS
};

static const UInt32 kOverwriteMode_IDs[] =
{
  IDS_EXTRACT_OVERWRITE_ASK,
  IDS_EXTRACT_OVERWRITE_WITHOUT_PROMPT,
  IDS_EXTRACT_OVERWRITE_SKIP_EXISTING,
  IDS_EXTRACT_OVERWRITE_RENAME,
  IDS_EXTRACT_OVERWRITE_RENAME_EXISTING
};

struct CCodePagePair
{
  UInt32 CodePage;
  const char *Name;
};

/* The list is fixed and the combo box is read only, so there is no input to
   check. A code page that is not here can still be used from the command
   line: "-mzip.cp=N". */
static const CCodePagePair k_CodePages[] =
{
  { 65001, "UTF-8" },
  {   932, "Japanese" },
  {   936, "Chinese Simplified" },
  {   949, "Korean" },
  {   950, "Chinese Traditional" },
  {   874, "Thai" },
  {  1250, "Central European" },
  {  1251, "Cyrillic" },
  {  1252, "Western European" },
  {  1253, "Greek" },
  {  1254, "Turkish" },
  {  1255, "Hebrew" },
  {  1256, "Arabic" },
  {  1257, "Baltic" },
  {  1258, "Vietnamese" },
  {   437, "OEM United States" },
  {   850, "OEM Latin 1" },
  {   852, "OEM Latin 2" },
  {   866, "OEM Cyrillic" }
};

static const
  // NExtract::NPathMode::EEnum
  int
  kPathModeButtonsVals[] =
{
  NExtract::NPathMode::kFullPaths,
  NExtract::NPathMode::kNoPaths,
  NExtract::NPathMode::kAbsPaths
};

static const
  int
  // NExtract::NOverwriteMode::EEnum
  kOverwriteButtonsVals[] =
{
  NExtract::NOverwriteMode::kAsk,
  NExtract::NOverwriteMode::kOverwrite,
  NExtract::NOverwriteMode::kSkip,
  NExtract::NOverwriteMode::kRename,
  NExtract::NOverwriteMode::kRenameExisting
};

#endif

#ifdef Z7_LANG

static const UInt32 kLangIDs[] =
{
  IDT_EXTRACT_EXTRACT_TO,
  IDT_EXTRACT_PATH_MODE,
  IDT_EXTRACT_OVERWRITE_MODE,
  IDT_EXTRACT_CODEPAGE,
  // IDX_EXTRACT_ALT_STREAMS,
  IDX_EXTRACT_NT_SECUR,
  IDX_EXTRACT_ELIM_DUP,
  IDG_PASSWORD,
  IDX_PASSWORD_SHOW
};
#endif

// static const int kWildcardsButtonIndex = 2;

#ifndef Z7_NO_REGISTRY
static const unsigned kHistorySize = 16;
#endif

#ifndef Z7_SFX

// it's used in CompressDialog also
void AddComboItems(NControl::CComboBox &combo, const UInt32 *langIDs, unsigned numItems, const int *values, int curVal);
void AddComboItems(NControl::CComboBox &combo, const UInt32 *langIDs, unsigned numItems, const int *values, int curVal)
{
  unsigned curSel = 0;
  for (unsigned i = 0; i < numItems; i++)
  {
    UString s = LangString(langIDs[i]);
    s.RemoveChar(L'&');
    combo.AddString_SetItemData(s, (LPARAM)i);
    if (values[i] == curVal)
      curSel = i;
  }
  combo.SetCurSel(curSel);
}

// it's used in CompressDialog also
bool GetBoolsVal(const CBoolPair &b1, const CBoolPair &b2);
bool GetBoolsVal(const CBoolPair &b1, const CBoolPair &b2)
{
  if (b1.Def) return b1.Val;
  if (b2.Def) return b2.Val;
  return b1.Val;
}

void CExtractDialog::CheckButton_TwoBools(UINT id, const CBoolPair &b1, const CBoolPair &b2)
{
  CheckButton(id, GetBoolsVal(b1, b2));
}

void CExtractDialog::GetButton_Bools(UINT id, CBoolPair &b1, CBoolPair &b2)
{
  const bool val = IsButtonCheckedBool(id);
  const bool oldVal = GetBoolsVal(b1, b2);
  if (val != oldVal)
    b1.Def = b2.Def = true;
  b1.Val = b2.Val = val;
}

#endif

bool CExtractDialog::OnInit()
{
  #ifdef Z7_LANG
  {
    UString s;
    LangString_OnlyFromLangFile(IDD_EXTRACT, s);
    if (s.IsEmpty())
      GetText(s);
    if (!ArcPath.IsEmpty())
    {
      s += " : ";
      s += ArcPath;
    }
    SetText(s);
    // LangSetWindowText(*this, IDD_EXTRACT);
    LangSetDlgItems(*this, kLangIDs, Z7_ARRAY_SIZE(kLangIDs));
  }
  #endif
  
  #ifndef Z7_SFX
  _passwordControl.Attach(GetItem(IDE_EXTRACT_PASSWORD));
  _passwordControl.SetText(Password);
  _passwordControl.SetPasswordChar(TEXT('*'));
  _pathName.Attach(GetItem(IDE_EXTRACT_NAME));
  #endif

  #ifdef Z7_NO_REGISTRY
  
  PathMode = NExtract::NPathMode::kFullPaths;
  OverwriteMode = NExtract::NOverwriteMode::kAsk;
  
  #else
  
  _info.Load();

  if (_info.PathMode == NExtract::NPathMode::kCurPaths)
    _info.PathMode = NExtract::NPathMode::kFullPaths;

  if (!PathMode_Force && _info.PathMode_Force)
    PathMode = _info.PathMode;
  if (!OverwriteMode_Force && _info.OverwriteMode_Force)
    OverwriteMode = _info.OverwriteMode;

  // CheckButton_TwoBools(IDX_EXTRACT_ALT_STREAMS, AltStreams, _info.AltStreams);
  CheckButton_TwoBools(IDX_EXTRACT_NT_SECUR,    NtSecurity, _info.NtSecurity);
  CheckButton_TwoBools(IDX_EXTRACT_ELIM_DUP,    ElimDup,    _info.ElimDup);
  
  CheckButton(IDX_PASSWORD_SHOW, _info.ShowPassword.Val);
  UpdatePasswordControl();

  #endif

  _path.Attach(GetItem(IDC_EXTRACT_PATH));

  UString pathPrefix = DirPath;

  #ifndef Z7_SFX
  
  if (_info.SplitDest.Val)
  {
    CheckButton(IDX_EXTRACT_NAME_ENABLE, true);
    UString pathName;
    SplitPathToParts_Smart(DirPath, pathPrefix, pathName);
    if (pathPrefix.IsEmpty())
      pathPrefix = pathName;
    else
      _pathName.SetText(pathName);
  }
  else
    ShowItem_Bool(IDE_EXTRACT_NAME, false);

  #endif

  _path.SetText(pathPrefix);

  #ifndef Z7_NO_REGISTRY
  for (unsigned i = 0; i < _info.Paths.Size() && i < kHistorySize; i++)
    _path.AddString(_info.Paths[i]);
  #endif

  /*
  if (_info.Paths.Size() > 0)
    _path.SetCurSel(0);
  else
    _path.SetCurSel(-1);
  */

  #ifndef Z7_SFX

  _pathMode.Attach(GetItem(IDC_EXTRACT_PATH_MODE));
  _overwriteMode.Attach(GetItem(IDC_EXTRACT_OVERWRITE_MODE));

  AddComboItems(_pathMode, kPathMode_IDs, Z7_ARRAY_SIZE(kPathMode_IDs), kPathModeButtonsVals, PathMode);
  AddComboItems(_overwriteMode, kOverwriteMode_IDs, Z7_ARRAY_SIZE(kOverwriteMode_IDs), kOverwriteButtonsVals, OverwriteMode);

  _codePage.Attach(GetItem(IDC_EXTRACT_CODEPAGE));
  {
    UString s;
    LangString(IDS_EXTRACT_CODEPAGE_AUTO, s);
    if (s.IsEmpty())
      s = "Auto";
    _codePage.AddString_SetItemData(s, (LPARAM)(Int32)-1);
    for (unsigned i = 0; i < Z7_ARRAY_SIZE(k_CodePages); i++)
    {
      const CCodePagePair &pair = k_CodePages[i];
      UString s2;
      s2.Add_UInt32(pair.CodePage);
      s2 += " (";
      s2 += pair.Name;
      s2 += ")";
      _codePage.AddString_SetItemData(s2, (LPARAM)pair.CodePage);
    }
    /* the dialog always starts with Auto: the code page fixes one archive,
       and keeping it would garble the names of the next one */
    _codePage.SetCurSel(0);
  }

  #endif

  HICON icon = LoadIcon(g_hInstance, MAKEINTRESOURCE(IDI_ICON));
  SetIcon(ICON_BIG, icon);
 
  // CWindow filesWindow = GetItem(IDC_EXTRACT_RADIO_FILES);
  // filesWindow.Enable(_enableFilesButton);

  NormalizePosition();

  return CModalDialog::OnInit();
}

#ifndef Z7_SFX
void CExtractDialog::UpdatePasswordControl()
{
  _passwordControl.SetPasswordChar(IsShowPasswordChecked() ? 0 : TEXT('*'));
  UString password;
  _passwordControl.GetText(password);
  _passwordControl.SetText(password);
}
#endif

bool CExtractDialog::OnButtonClicked(unsigned buttonID, HWND buttonHWND)
{
  switch (buttonID)
  {
    case IDB_EXTRACT_SET_PATH:
      OnButtonSetPath();
      return true;
    #ifndef Z7_SFX
    case IDX_EXTRACT_NAME_ENABLE:
      ShowItem_Bool(IDE_EXTRACT_NAME, IsButtonCheckedBool(IDX_EXTRACT_NAME_ENABLE));
      return true;
    case IDX_PASSWORD_SHOW:
    {
      UpdatePasswordControl();
      return true;
    }
    #endif
  }
  return CModalDialog::OnButtonClicked(buttonID, buttonHWND);
}

void CExtractDialog::OnButtonSetPath()
{
  UString currentPath;
  _path.GetText(currentPath);
  UString title = LangString(IDS_EXTRACT_SET_FOLDER);
  UString resultPath;
  if (!MyBrowseForFolder(*this, title, currentPath, resultPath))
    return;
  #ifndef Z7_NO_REGISTRY
  _path.SetCurSel(-1);
  #endif
  _path.SetText(resultPath);
}

void AddUniqueString(UStringVector &list, const UString &s);
void AddUniqueString(UStringVector &list, const UString &s)
{
  FOR_VECTOR (i, list)
    if (s.IsEqualTo_NoCase(list[i]))
      return;
  list.Add(s);
}

void CExtractDialog::OnOK()
{
  #ifndef Z7_SFX
  int pathMode2 = kPathModeButtonsVals[_pathMode.GetCurSel()];
  if (PathMode != NExtract::NPathMode::kCurPaths ||
      pathMode2 != NExtract::NPathMode::kFullPaths)
    PathMode = (NExtract::NPathMode::EEnum)pathMode2;

  OverwriteMode = (NExtract::NOverwriteMode::EEnum)kOverwriteButtonsVals[_overwriteMode.GetCurSel()];

  // _filesMode = (NExtractionDialog::NFilesMode::EEnum)GetFilesMode();

  _passwordControl.GetText(Password);

  {
    const LPARAM v = _codePage.GetItemData_of_CurSel();
    CodePage = (v < 0) ? kNameCodePage_Auto : (UInt32)v;
  }

  #endif

  #ifndef Z7_NO_REGISTRY

  // GetButton_Bools(IDX_EXTRACT_ALT_STREAMS, AltStreams, _info.AltStreams);
  GetButton_Bools(IDX_EXTRACT_NT_SECUR,    NtSecurity, _info.NtSecurity);
  GetButton_Bools(IDX_EXTRACT_ELIM_DUP,    ElimDup,    _info.ElimDup);

  bool showPassword = IsShowPasswordChecked();
  if (showPassword != _info.ShowPassword.Val)
  {
    _info.ShowPassword.Def = true;
    _info.ShowPassword.Val = showPassword;
  }

  if (_info.PathMode != pathMode2)
  {
    _info.PathMode_Force = true;
    _info.PathMode = (NExtract::NPathMode::EEnum)pathMode2;
    /*
    // we allow kAbsPaths in registry.
    if (_info.PathMode == NExtract::NPathMode::kAbsPaths)
      _info.PathMode = NExtract::NPathMode::kFullPaths;
    */
  }

  if (!OverwriteMode_Force && _info.OverwriteMode != OverwriteMode)
    _info.OverwriteMode_Force = true;
  _info.OverwriteMode = OverwriteMode;


  #else
  
  ElimDup.Val = IsButtonCheckedBool(IDX_EXTRACT_ELIM_DUP);

  #endif
  
  UString s;
  
  #ifdef Z7_NO_REGISTRY
  
  _path.GetText(s);
  
  #else

  int currentItem = _path.GetCurSel();
  if (currentItem == CB_ERR)
  {
    _path.GetText(s);
    if (_path.GetCount() >= (int)kHistorySize)
      currentItem = _path.GetCount() - 1;
  }
  else
    _path.GetLBText(currentItem, s);
  
  #endif

  s.Trim();
  NName::NormalizeDirPathPrefix(s);
  
  #ifndef Z7_SFX
  
  const bool splitDest = IsButtonCheckedBool(IDX_EXTRACT_NAME_ENABLE);
  if (splitDest)
  {
    UString pathName;
    _pathName.GetText(pathName);
    pathName.Trim();
    s += pathName;
    NName::NormalizeDirPathPrefix(s);
  }
  if (splitDest != _info.SplitDest.Val)
  {
    _info.SplitDest.Def = true;
    _info.SplitDest.Val = splitDest;
  }

  #endif

  DirPath = s;
  
  #ifndef Z7_NO_REGISTRY
  _info.Paths.Clear();
  #ifndef Z7_SFX
  AddUniqueString(_info.Paths, s);
  #endif
  for (int i = 0; i < _path.GetCount(); i++)
    if (i != currentItem)
    {
      UString sTemp;
      _path.GetLBText(i, sTemp);
      sTemp.Trim();
      AddUniqueString(_info.Paths, sTemp);
    }
  _info.Save();
  #endif
  
  CModalDialog::OnOK();
}

#ifndef Z7_NO_REGISTRY
#define kHelpTopic "fm/plugins/7-zip/extract.htm"
void CExtractDialog::OnHelp()
{
  ShowHelpWindow(kHelpTopic);
  CModalDialog::OnHelp();
}
#endif
