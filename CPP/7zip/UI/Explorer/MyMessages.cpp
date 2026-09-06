// MyMessages.cpp
// Modified in 7-Zip-fork, 2026: https://github.com/r404r/7zip

#include "StdAfx.h"

#include "MyMessages.h"

#include "../../../Windows/ErrorMsg.h"
#include "../../../Windows/ResourceString.h"

#include "../FileManager/LangUtils.h"

using namespace NWindows;

extern bool g_DisableUserQuestions;

void ShowErrorMessage(HWND window, LPCWSTR message)
{
  if (!g_DisableUserQuestions)
    ::MessageBoxW(window, message, L"7-Zip", MB_OK | MB_ICONSTOP);
}

void ShowErrorMessageHwndRes(HWND window, UInt32 resID)
{
  UString s;
  {
    #ifdef Z7_LANG
    // the table can be reloaded by another thread of the shell extension
    NSynchronization::CCriticalSectionLock lock(Lang_CriticalSection());
    #endif
    s = LangString(resID);
  }
  if (s.IsEmpty())
    s.Add_UInt32(resID);
  ShowErrorMessage(window, s);
}

void ShowErrorMessageRes(UInt32 resID)
{
  ShowErrorMessageHwndRes(NULL, resID);
}

static void ShowErrorMessageDWORD(HWND window, DWORD errorCode)
{
  ShowErrorMessage(window, NError::MyFormatMessage(errorCode));
}

void ShowLastErrorMessage(HWND window)
{
  ShowErrorMessageDWORD(window, ::GetLastError());
}
