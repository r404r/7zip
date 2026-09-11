// Test-only retained handler properties and real native file stream calls.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "../../Archive/Zip/ZipHandler.h"
#include "../../Archive/Tar/TarHandler.h"
#include "../../Archive/7z/7zHandler.h"
#include "../../Common/FileStreams.h"
#include "../../../Windows/PropVariant.h"

static const char *B03Mode()
{
#ifdef _WIN32
  static char mode[16];
  const DWORD n = GetEnvironmentVariableA("B03_MODE", mode, sizeof(mode));
  return n && n < sizeof(mode) ? mode : NULL;
#else
  return getenv("B03_MODE");
#endif
}

static void B03Value(const PROPVARIANT &v)
{
  printf("\"vt\":%u", (unsigned)v.vt);
  // PropID.h defines precision words only for VT_FILETIME. CPropVariant's
  // constructor/scalar setters do not initialize wReserved2/3. Do not read
  // indeterminate storage for non-time tags (including VT_EMPTY).
  if (v.vt == VT_FILETIME)
  {
    // Backward-compatible precision 0 explicitly leaves words 2/3 undefined
    // (PropID.h:146-148); null labels absence, it is not a measured zero.
    if (v.wReserved1 == 0)
      printf(",\"reserved\":[0,null,null]");
    else
      printf(",\"reserved\":[%u,%u,%u]", (unsigned)v.wReserved1,
          (unsigned)v.wReserved2, (unsigned)v.wReserved3);
    printf(",\"filetime\":[%u,%u]", (unsigned)v.filetime.dwLowDateTime, (unsigned)v.filetime.dwHighDateTime);
  }
  else if (v.vt == VT_UI8) printf(",\"ui8\":%llu", (unsigned long long)v.uhVal.QuadPart);
  else if (v.vt == VT_UI4) printf(",\"ui4\":%u", (unsigned)v.ulVal);
  else if (v.vt == VT_BOOL) printf(",\"bool\":%d", (int)v.boolVal);
  else if (v.vt == VT_BSTR)
  {
    printf(",\"units\":[");
    for (unsigned j = 0; j < SysStringLen(v.bstrVal); ++j)
      printf("%s%u", j ? "," : "", (unsigned)v.bstrVal[j]);
    printf("]");
  }
}

static int B03Probe()
{
  CInFileStream *input = new CInFileStream;
  CMyComPtr<IInStream> stream = input;
  const bool opened = input->Open(FTEXT("input.arc"));
  if (!opened) return 91;
  const char *mode = B03Mode();
  printf("{\"wchar_bytes\":%u,", (unsigned)sizeof(wchar_t));
  if (strcmp(mode, "io") == 0)
  {
    const Int64 offsets[] = {0, -1, 4294967313LL, 0, 1, 0};
    const UInt32 origins[] = {0, 0, 0, 2, 2, 9};
    printf("\"operations\":[");
    for (unsigned i = 0; i < 6; ++i)
    {
      UInt64 pos = 0;
      const HRESULT hr = stream->Seek(offsets[i], origins[i], &pos);
      Byte data[16] = {0};
      UInt32 got = 0;
      const HRESULT readHr = stream->Read(data, sizeof(data), &got);
      printf("%s{\"offset\":%lld,\"origin\":%u,\"seek_hr\":%u,\"position\":%llu,\"position_defined\":%s,\"read_hr\":%u,\"processed\":%u,\"bytes\":[",
          i ? "," : "", (long long)offsets[i], (unsigned)origins[i], (unsigned)hr,
          (unsigned long long)pos, hr == S_OK ? "true" : "false", (unsigned)readHr, (unsigned)got);
      for (UInt32 j = 0; j < got; ++j) printf("%s%u", j ? "," : "", (unsigned)data[j]);
      printf("]}");
    }
    printf("]}\n");
    return 0;
  }
  CMyComPtr<IInArchive> arc;
  if (strcmp(mode, "zip") == 0) arc = new NArchive::NZip::CHandler;
  else if (strcmp(mode, "tar") == 0) arc = new NArchive::NTar::CHandler;
  else arc = new NArchive::N7z::CHandler;
  const HRESULT openHr = arc->Open(stream, NULL, NULL);
  UInt32 count = 0;
  HRESULT countHr = openHr;
  if (openHr == S_OK) countHr = arc->GetNumberOfItems(&count);
  printf("\"open_hr\":%u,\"count_hr\":%u,\"items\":[", (unsigned)openHr, (unsigned)countHr);
  const PROPID props[] = {kpidPath, kpidIsDir, kpidSize, kpidAttrib, kpidPosixAttrib,
      kpidCTime, kpidATime, kpidMTime, kpidTimeType, kpidNtSecure, kpidIsAltStream};
  for (UInt32 i = 0; countHr == S_OK && i < count; ++i)
  {
    printf("%s{\"index\":%u,\"properties\":[", i ? "," : "", (unsigned)i);
    for (unsigned j = 0; j < sizeof(props) / sizeof(props[0]); ++j)
    {
      NWindows::NCOM::CPropVariant value;
      const HRESULT hr = arc->GetProperty(i, props[j], &value);
      printf("%s{\"id\":%u,\"hr\":%u,", j ? "," : "", (unsigned)props[j], (unsigned)hr);
      B03Value(value);
      printf("}");
    }
    printf("]}");
  }
  printf("],\"close_hr\":%u}\n", (unsigned)arc->Close());
  return 0;
}
