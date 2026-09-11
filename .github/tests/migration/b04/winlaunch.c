/* Test-only AppContainer candidate. No profile, capabilities, handle inheritance,
   host policy changes or arbitrary command execution. Failure never falls back. */
#define _WIN32_WINNT 0x0602
#define UNICODE
#define _UNICODE
#include <windows.h>
#include <userenv.h>
#include <aclapi.h>
#include <sddl.h>
#include <stdio.h>

static DWORD grant(const wchar_t *path, PSID sid, DWORD mask)
{
  PACL old_acl = NULL, new_acl = NULL;
  PSECURITY_DESCRIPTOR sd = NULL;
  DWORD error = GetNamedSecurityInfoW((LPWSTR)path, SE_FILE_OBJECT,
      DACL_SECURITY_INFORMATION, NULL, NULL, &old_acl, NULL, &sd);
  if (error) return error;
  EXPLICIT_ACCESSW ea = {0};
  ea.grfAccessPermissions = mask;
  ea.grfAccessMode = GRANT_ACCESS;
  ea.grfInheritance = SUB_CONTAINERS_AND_OBJECTS_INHERIT;
  ea.Trustee.TrusteeForm = TRUSTEE_IS_SID;
  ea.Trustee.TrusteeType = TRUSTEE_IS_UNKNOWN;
  ea.Trustee.ptstrName = (LPWSTR)sid;
  error = SetEntriesInAclW(1, &ea, old_acl, &new_acl);
  if (!error) error = SetNamedSecurityInfoW((LPWSTR)path, SE_FILE_OBJECT,
      DACL_SECURITY_INFORMATION, NULL, NULL, new_acl, NULL);
  if (new_acl) LocalFree(new_acl);
  LocalFree(sd);
  return error;
}
int wmain(int argc, wchar_t **argv)
{
  PSID sid = NULL;
  STARTUPINFOEXW si = {0};
  PROCESS_INFORMATION pi = {0};
  SECURITY_CAPABILITIES caps = {0};
  SIZE_T bytes = 0;
  DWORD result = 95;
  wchar_t exe[4096], work[4096], command[16384];
  /* Only the parent-created disposable envelope is accepted by this test entry.
     This is not a reusable security launcher API. */
  if (argc != 2) return 90;
  if (swprintf_s(exe, 4096, L"%s\\probe.exe", argv[1]) < 0 ||
      swprintf_s(work, 4096, L"%s\\work", argv[1]) < 0 ||
      swprintf_s(command, 16384, L"\"%s\" \"%s\" \"%s\\outside\"", exe, work, argv[1]) < 0)
    return 91;
  HRESULT hr = DeriveAppContainerSidFromAppContainerName(L"B04.Prerequisite.NoProfile", &sid);
  if (FAILED(hr)) { printf("DeriveAppContainerSid HRESULT=%08lx\n", (unsigned long)hr); return 92; }
  result = grant(argv[1], sid, FILE_GENERIC_READ | FILE_GENERIC_EXECUTE);
  if (!result) result = grant(work, sid, FILE_ALL_ACCESS);
  if (result) { printf("grant error=%lu\n", (unsigned long)result); goto cleanup; }
  PSECURITY_DESCRIPTOR label = NULL;
  PACL sacl = NULL;
  BOOL present = FALSE, defaulted = FALSE;
  if (!ConvertStringSecurityDescriptorToSecurityDescriptorW(L"S:(ML;OICI;NW;;;LW)",
      SDDL_REVISION_1, &label, NULL)) { result = GetLastError(); goto cleanup; }
  if (!GetSecurityDescriptorSacl(label, &present, &sacl, &defaulted) || !present)
    result = ERROR_INVALID_SECURITY_DESCR;
  else result = SetNamedSecurityInfoW(work, SE_FILE_OBJECT, LABEL_SECURITY_INFORMATION,
      NULL, NULL, NULL, sacl);
  LocalFree(label);
  if (result) goto cleanup;
  caps.AppContainerSid = sid;
  si.StartupInfo.cb = sizeof(si);
  InitializeProcThreadAttributeList(NULL, 1, 0, &bytes);
  si.lpAttributeList = (LPPROC_THREAD_ATTRIBUTE_LIST)HeapAlloc(GetProcessHeap(), 0, bytes);
  if (!si.lpAttributeList) { result = 93; goto cleanup; }
  if (!InitializeProcThreadAttributeList(si.lpAttributeList, 1, 0, &bytes)) {
    result = GetLastError();
    HeapFree(GetProcessHeap(), 0, si.lpAttributeList);
    si.lpAttributeList = NULL;
    goto cleanup;
  }
  if (!UpdateProcThreadAttribute(si.lpAttributeList, 0,
      PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES, &caps, sizeof(caps), NULL, NULL)) {
    result = GetLastError(); goto cleanup;
  }
  /* Environment is explicitly empty (double NUL), not inherited from CI. */
  wchar_t environment[2] = {0, 0};
  if (!CreateProcessW(exe, command, NULL, NULL, FALSE,
      EXTENDED_STARTUPINFO_PRESENT | CREATE_UNICODE_ENVIRONMENT,
      environment, work, &si.StartupInfo, &pi)) {
    result = GetLastError(); goto cleanup;
  }
  if (WaitForSingleObject(pi.hProcess, 20000) != WAIT_OBJECT_0) {
    TerminateProcess(pi.hProcess, 96);
    WaitForSingleObject(pi.hProcess, INFINITE);
    result = 96;
  } else if (!GetExitCodeProcess(pi.hProcess, &result)) result = 97;
cleanup:
  printf("AppContainer candidate result=%lu\n", (unsigned long)result);
  if (pi.hThread) CloseHandle(pi.hThread);
  if (pi.hProcess) CloseHandle(pi.hProcess);
  if (si.lpAttributeList) {
    DeleteProcThreadAttributeList(si.lpAttributeList);
    HeapFree(GetProcessHeap(), 0, si.lpAttributeList);
  }
  if (sid) FreeSid(sid);
  return result == 0 ? 0 : 1;
}
