// LangUtils.h
// Modified in 7-Zip-fork, 2026: https://github.com/r404r/7zip

#ifndef ZIP7_INC_LANG_UTILS_H
#define ZIP7_INC_LANG_UTILS_H

#include "../../../Common/Lang.h"

#include "../../../Windows/ResourceString.h"
#include "../../../Windows/Synchronization.h"

extern UString g_LangID;
extern CLang g_Lang;

#ifdef Z7_LANG

struct CIDLangPair
{
  UInt32 ControlID;
  UInt32 LangID;
};

void ReloadLang();
void LoadLangOneTime();
// for a host that keeps this code loaded across a change of the setting
// (explorer.exe); the caller reads the table under the same lock.
// Without g_LangFollowsRegistry (the shell extension sets it) this is
// LoadLangOneTime: the File Manager reloads on its own and refreshes its
// windows when it does.
extern bool g_LangFollowsRegistry;
NWindows::NSynchronization::CCriticalSection &Lang_CriticalSection();
void ReloadLangIfRegChanged();

void LangSetDlgItemText(HWND dialog, UInt32 controlID, UInt32 langID);
void LangSetDlgItems(HWND dialog, const UInt32 *ids, unsigned numItems);
void LangSetDlgItems_Colon(HWND dialog, const UInt32 *ids, unsigned numItems);
void LangSetDlgItems_RemoveColon(HWND dialog, const UInt32 *ids, unsigned numItems);
void LangSetWindowText(HWND window, UInt32 langID);

UString LangString(UInt32 langID);
void AddLangString(UString &s, UInt32 langID);
void LangString(UInt32 langID, UString &dest);
void LangString_OnlyFromLangFile(UInt32 langID, UString &dest);
 
#else

inline UString LangString(UInt32 langID) { return NWindows::MyLoadString(langID); }
inline void LangString(UInt32 langID, UString &dest) { NWindows::MyLoadString(langID, dest); }
inline void AddLangString(UString &s, UInt32 langID) { s += NWindows::MyLoadString(langID); }

#endif

FString GetLangDirPrefix();
// bool LangOpen(CLang &lang, CFSTR fileName);

void Lang_GetShortNames_for_DefaultLang(AStringVector &names, unsigned &subLang);

#endif
