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

static DWORD diagnostic(const char *stage, const char *api, DWORD error)
{
  printf("B04-launch stage=%s api=%s error=%lu\n", stage, api, (unsigned long)error);
  return error;
}

static DWORD grant(const wchar_t *path, PSID sid, DWORD mask)
{
  PACL old_acl = NULL, new_acl = NULL;
  PSECURITY_DESCRIPTOR sd = NULL;
  DWORD error = GetNamedSecurityInfoW((LPWSTR)path, SE_FILE_OBJECT,
      DACL_SECURITY_INFORMATION, NULL, NULL, &old_acl, NULL, &sd);
  if (error) return diagnostic("setup", "GetNamedSecurityInfoW", error);
  EXPLICIT_ACCESSW ea = {0};
  ea.grfAccessPermissions = mask;
  ea.grfAccessMode = GRANT_ACCESS;
  ea.grfInheritance = SUB_CONTAINERS_AND_OBJECTS_INHERIT;
  ea.Trustee.TrusteeForm = TRUSTEE_IS_SID;
  ea.Trustee.TrusteeType = TRUSTEE_IS_UNKNOWN;
  ea.Trustee.ptstrName = (LPWSTR)sid;
  error = SetEntriesInAclW(1, &ea, old_acl, &new_acl);
  if (error) diagnostic("setup", "SetEntriesInAclW", error);
  else {
    error = SetNamedSecurityInfoW((LPWSTR)path, SE_FILE_OBJECT,
        DACL_SECURITY_INFORMATION, NULL, NULL, new_acl, NULL);
    if (error) diagnostic("setup", "SetNamedSecurityInfoW(DACL)", error);
  }
  if (new_acl) LocalFree(new_acl);
  LocalFree(sd);
  return error;
}

static DWORD identity(const wchar_t *path, BOOL directory)
{
  DWORD attributes = GetFileAttributesW(path);
  if (attributes == INVALID_FILE_ATTRIBUTES)
    return diagnostic("identity", "GetFileAttributesW", GetLastError());
  if ((attributes & FILE_ATTRIBUTE_REPARSE_POINT) ||
      (!!(attributes & FILE_ATTRIBUTE_DIRECTORY) != !!directory))
    return diagnostic("identity", "unexpected-type", ERROR_INVALID_DATA);
  HANDLE file = CreateFileW(path, FILE_READ_ATTRIBUTES,
      FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, NULL,
      OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT, NULL);
  if (file == INVALID_HANDLE_VALUE)
    return diagnostic("identity", "CreateFileW", GetLastError());
  wchar_t final_path[4096];
  DWORD count = GetFinalPathNameByHandleW(file, final_path, 4096, FILE_NAME_NORMALIZED);
  DWORD error = 0;
  if (!count) error = diagnostic("identity", "GetFinalPathNameByHandleW", GetLastError());
  else if (count >= 4096) error = diagnostic("identity", "final-path-cap", ERROR_INSUFFICIENT_BUFFER);
  else printf("B04-identity directory=%d attributes=%lu final_path=%ls\n",
      (int)directory, (unsigned long)attributes, final_path);
  CloseHandle(file);
  if (!error && !directory) {
    DWORD binary_type = 0;
    if (!GetBinaryTypeW(path, &binary_type))
      error = diagnostic("identity", "GetBinaryTypeW", GetLastError());
    else {
      printf("B04-identity binary_type=%lu\n", (unsigned long)binary_type);
      if (binary_type != SCS_64BIT_BINARY)
        error = diagnostic("identity", "unexpected-binary-type", ERROR_INVALID_DATA);
    }
  }
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
  HANDLE job = NULL;
  wchar_t exe[4096], work[4096], command[16384];
  /* Only the parent-created disposable envelope is accepted by this test entry.
     This is not a reusable security launcher API. */
  if (argc != 2) { diagnostic("setup", "arguments", ERROR_BAD_ARGUMENTS); return 90; }
  if (swprintf_s(exe, 4096, L"%s\\probe.exe", argv[1]) < 0 ||
      swprintf_s(work, 4096, L"%s\\work", argv[1]) < 0 ||
      swprintf_s(command, 16384, L"\"%s\" \"%s\" \"%s\\outside\"", exe, work, argv[1]) < 0)
    { diagnostic("setup", "swprintf_s", ERROR_INSUFFICIENT_BUFFER); return 91; }
  HRESULT hr = DeriveAppContainerSidFromAppContainerName(L"B04.Prerequisite.NoProfile", &sid);
  if (FAILED(hr)) {
    printf("B04-launch stage=setup api=DeriveAppContainerSidFromAppContainerName HRESULT=%08lx\n",
        (unsigned long)hr);
    return 92;
  }
  result = grant(argv[1], sid, FILE_GENERIC_READ | FILE_GENERIC_EXECUTE);
  if (!result) result = grant(work, sid, FILE_ALL_ACCESS);
  if (result) { printf("grant error=%lu\n", (unsigned long)result); goto cleanup; }
  PSECURITY_DESCRIPTOR label = NULL;
  PACL sacl = NULL;
  BOOL present = FALSE, defaulted = FALSE;
  if (!ConvertStringSecurityDescriptorToSecurityDescriptorW(L"S:(ML;OICI;NW;;;LW)",
      SDDL_REVISION_1, &label, NULL)) {
    result = GetLastError();
    diagnostic("setup", "ConvertStringSecurityDescriptorToSecurityDescriptorW", result);
    goto cleanup;
  }
  if (!GetSecurityDescriptorSacl(label, &present, &sacl, &defaulted)) {
    result = GetLastError();
    diagnostic("setup", "GetSecurityDescriptorSacl", result);
  } else if (!present) {
    result = diagnostic("setup", "missing-SACL", ERROR_INVALID_SECURITY_DESCR);
  } else {
    result = SetNamedSecurityInfoW(work, SE_FILE_OBJECT, LABEL_SECURITY_INFORMATION,
        NULL, NULL, NULL, sacl);
    if (result) diagnostic("setup", "SetNamedSecurityInfoW(label)", result);
  }
  LocalFree(label);
  if (result) goto cleanup;
  caps.AppContainerSid = sid;
  si.StartupInfo.cb = sizeof(si);
  if (InitializeProcThreadAttributeList(NULL, 1, 0, &bytes)) {
    result = diagnostic("setup", "attribute-size-unexpected-success", ERROR_INVALID_DATA);
    goto cleanup;
  }
  result = GetLastError();
  if (result != ERROR_INSUFFICIENT_BUFFER || !bytes) {
    diagnostic("setup", "InitializeProcThreadAttributeList(size)", result);
    if (!result) result = ERROR_INVALID_DATA;
    goto cleanup;
  }
  si.lpAttributeList = (LPPROC_THREAD_ATTRIBUTE_LIST)HeapAlloc(GetProcessHeap(), 0, bytes);
  if (!si.lpAttributeList) {
    result = diagnostic("setup", "HeapAlloc", ERROR_NOT_ENOUGH_MEMORY); goto cleanup;
  }
  if (!InitializeProcThreadAttributeList(si.lpAttributeList, 1, 0, &bytes)) {
    result = GetLastError();
    diagnostic("setup", "InitializeProcThreadAttributeList", result);
    HeapFree(GetProcessHeap(), 0, si.lpAttributeList);
    si.lpAttributeList = NULL;
    goto cleanup;
  }
  if (!UpdateProcThreadAttribute(si.lpAttributeList, 0,
      PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES, &caps, sizeof(caps), NULL, NULL)) {
    result = GetLastError();
    diagnostic("setup", "UpdateProcThreadAttribute", result); goto cleanup;
  }
  /* Environment is explicitly empty (double NUL), not inherited from CI. */
  wchar_t environment[2] = {0, 0};
  result = identity(exe, FALSE);
  if (!result) result = identity(work, TRUE);
  if (result) goto cleanup;
  job = CreateJobObjectW(NULL, NULL);
  if (!job) { result = diagnostic("setup", "CreateJobObjectW", GetLastError()); goto cleanup; }
  JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits = {0};
  limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
  if (!SetInformationJobObject(job, JobObjectExtendedLimitInformation, &limits, sizeof(limits))) {
    result = diagnostic("setup", "SetInformationJobObject", GetLastError()); goto cleanup;
  }
  if (!CreateProcessW(exe, command, NULL, NULL, FALSE,
      EXTENDED_STARTUPINFO_PRESENT | CREATE_UNICODE_ENVIRONMENT | CREATE_SUSPENDED,
      environment, work, &si.StartupInfo, &pi)) {
    result = GetLastError();
    diagnostic("launch", "CreateProcessW", result); goto cleanup;
  }
  if (!AssignProcessToJobObject(job, pi.hProcess)) {
    result = diagnostic("setup", "AssignProcessToJobObject", GetLastError());
    if (!TerminateProcess(pi.hProcess, 96))
      diagnostic("cleanup", "TerminateProcess", GetLastError());
    goto cleanup;
  }
  if (ResumeThread(pi.hThread) == (DWORD)-1) {
    result = diagnostic("launch", "ResumeThread", GetLastError()); goto cleanup;
  }
  DWORD wait = WaitForSingleObject(pi.hProcess, 20000);
  if (wait != WAIT_OBJECT_0) {
    DWORD error = wait == WAIT_FAILED ? GetLastError() : wait;
    diagnostic(wait == WAIT_TIMEOUT ? "timeout" : "wait", "WaitForSingleObject", error);
    if (!TerminateProcess(pi.hProcess, 96)) {
      error = GetLastError(); diagnostic("cleanup", "TerminateProcess", error);
    }
    result = 96;
  } else if (!GetExitCodeProcess(pi.hProcess, &result)) {
    result = GetLastError(); diagnostic("wait", "GetExitCodeProcess", result);
  } else {
    printf("B04-launch stage=child exit_code=%lu\n", (unsigned long)result);
  }
cleanup:
  if (job) CloseHandle(job);
  if (pi.hProcess) {
    DWORD final_wait = WaitForSingleObject(pi.hProcess, 5000);
    if (final_wait != WAIT_OBJECT_0) {
      DWORD error = final_wait == WAIT_FAILED ? GetLastError() : final_wait;
      diagnostic("cleanup", "WaitForSingleObject", error);
      printf("B04-launch quiescent=false\n");
      result = 96;
    } else printf("B04-launch quiescent=true\n");
  }
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
