// Test-only boundary fault injection. Never installed in the source checkout.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include "../../Common/MyWindows.h"
#include "../../Common/MyTypes.h"

static HRESULT B03Limit(const char *direction, UInt32 &size)
{
#ifdef _WIN32
  char mode[32];
  const DWORD n = GetEnvironmentVariableA("B03_FAULT", mode, sizeof(mode));
  if (!n || n >= sizeof(mode)) return S_OK;
#else
  const char *mode = getenv("B03_FAULT");
  if (!mode) return S_OK;
#endif
  if (strncmp(mode, direction, strlen(direction)) != 0 || size == 0) return S_OK;
  // The tests use a single input/output and -mmt=off. This counter counts
  // permitted bytes, not OS-completed bytes; native inventories record the latter.
  static UInt32 permitted = 0;
  if (!permitted) fprintf(stderr, "B03_FAULT active=%s\n", mode);
  const bool shortOnly = strstr(mode, "short") != NULL;
  if (!shortOnly && permitted >= 4096)
  {
    fprintf(stderr, "B03_FAULT triggered=%s permitted=%u\n", mode, (unsigned)permitted);
#ifdef _WIN32
    return HRESULT_FROM_WIN32(strcmp(direction, "write") == 0 ? ERROR_DISK_FULL : ERROR_READ_FAULT);
#else
    return HRESULT_FROM_WIN32(strcmp(direction, "write") == 0 ? ENOSPC : EIO);
#endif
  }
  if (size > 7) size = 7;
  if (!shortOnly && size > 4096 - permitted) size = 4096 - permitted;
  permitted += size;
  return S_OK;
}
