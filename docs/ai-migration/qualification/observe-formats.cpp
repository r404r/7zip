// Q1 qualification-only observation of the retained Format7zF exports.
// Not the migration facade. Uses the matched native library's original ABI.
#include <cstdio>
#include <cstring>
#include "CPP/Common/MyWindows.h"
#include "CPP/7zip/Archive/IArchive.h"

STDAPI GetNumberOfFormats(UInt32 *count);
STDAPI GetHandlerProperty2(UInt32 index, PROPID id, PROPVARIANT *value);

static bool ReadUInt32(UInt32 index, PROPID id, UInt32 &out)
{
  PROPVARIANT value = {};
  const HRESULT status = GetHandlerProperty2(index, id, &value);
  if (status != S_OK || value.vt != VT_UI4)
  {
    if (value.vt == VT_BSTR) SysFreeString(value.bstrVal);
    return false;
  }
  out = value.ulVal;
  return true;
}

int main()
{
  UInt32 count = 0;
  if (GetNumberOfFormats(&count) != S_OK || count == 0) return 1;
  std::puts("index\tregistration_id\tflags\ttime_flags\twriter\tname");
  for (UInt32 index = 0; index < count; ++index)
  {
    PROPVARIANT cls = {}, name = {}, update = {};
    UInt32 flags = 0, time_flags = 0;
    const HRESULT cs = GetHandlerProperty2(index, NArchive::NHandlerPropID::kClassID, &cls);
    const HRESULT ns = GetHandlerProperty2(index, NArchive::NHandlerPropID::kName, &name);
    const HRESULT us = GetHandlerProperty2(index, NArchive::NHandlerPropID::kUpdate, &update);
    const bool valid = cs == S_OK && cls.vt == VT_BSTR && cls.bstrVal != NULL
        && SysStringByteLen(cls.bstrVal) == sizeof(GUID)
        && ns == S_OK && name.vt == VT_BSTR && name.bstrVal != NULL
        && us == S_OK && update.vt == VT_BOOL
        && ReadUInt32(index, NArchive::NHandlerPropID::kFlags, flags)
        && ReadUInt32(index, NArchive::NHandlerPropID::kTimeFlags, time_flags);
    if (valid)
    {
      GUID guid;
      std::memcpy(&guid, cls.bstrVal, sizeof(guid));
      // ArchiveExports.cpp CLS_ARC_ID_ITEM defines the exact registration byte.
      std::printf("%u\t%u\t%u\t%u\t%u\t%ls\n", (unsigned)index,
          (unsigned)guid.Data4[5], (unsigned)flags, (unsigned)time_flags,
          (unsigned)(update.boolVal != VARIANT_FALSE), name.bstrVal);
    }
    if (cls.vt == VT_BSTR) SysFreeString(cls.bstrVal);
    if (name.vt == VT_BSTR) SysFreeString(name.bstrVal);
    if (update.vt == VT_BSTR) SysFreeString(update.bstrVal);
    if (!valid) return 2;
  }
  return 0;
}
