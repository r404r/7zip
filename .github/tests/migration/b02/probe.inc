// Test-only entry point compiled into a disposable copy of the legacy CLI.
// Handler code and the scoped property helper remain unmodified.
#include <cstdio>
#include <cstdlib>
#include <vector>
#include "../../Archive/Zip/ZipHandler.h"
#include "../../Archive/Tar/TarHandler.h"
#include "../../Common/StreamObjects.h"
#include "../Common/SetProperties.h"
#include "../../../Windows/PropVariant.h"

static HRESULT B02Names(IInArchive *arc)
{
  UInt32 count = 0;
  HRESULT hr = arc->GetNumberOfItems(&count);
  printf("\"count_hr\":%u,\"items\":[", (unsigned)hr);
  for (UInt32 i = 0; hr == S_OK && i < count; ++i)
  {
    NWindows::NCOM::CPropVariant value;
    HRESULT itemHr = arc->GetProperty(i, kpidPath, &value);
    printf("%s{\"index\":%u,\"hr\":%u,\"vt\":%u,\"wchar_units\":[",
        i ? "," : "", (unsigned)i, (unsigned)itemHr, (unsigned)value.vt);
    if (itemHr == S_OK && value.vt == VT_BSTR)
      for (unsigned j = 0; j < SysStringLen(value.bstrVal); ++j)
        printf("%s%u", j ? "," : "", (unsigned)value.bstrVal[j]);
    printf("]}");
  }
  printf("]");
  return hr;
}

static int B02Probe()
{
  FILE *file = fopen("input.arc", "rb");
  if (!file) return 91;
  std::vector<Byte> data;
  int c;
  while ((c = fgetc(file)) != EOF) data.push_back((Byte)c);
  const bool readError = ferror(file) != 0;
  fclose(file);
  if (readError || data.empty()) return 92;
  const bool zip = strcmp(getenv("B02_FORMAT"), "zip") == 0;
  CMyComPtr<IInArchive> arc;
  if (zip) arc = new NArchive::NZip::CHandler;
  else arc = new NArchive::NTar::CHandler;
  CMyComPtr<ISetProperties> setter;
  if (arc->QueryInterface(IID_ISetProperties, (void **)&setter) != S_OK) return 93;
  CBufInStream *streamSpec = new CBufInStream;
  CMyComPtr<IInStream> stream = streamSpec;
  streamSpec->Init(&data[0], data.size());
  HRESULT openHr = arc->Open(stream, NULL, NULL);
  printf("{\"wchar_bytes\":%u,\"open_hr\":%u,\"phases\":[", (unsigned)sizeof(wchar_t), (unsigned)openHr);
  const char *labels[] = {"fresh", "cp932", "cp936", "cp65001", "unscoped_empty", "scoped_empty", "cp936_again", "filtered_empty", "cp936_direct", "direct_empty"};
  for (unsigned phase = 0; phase < 10; ++phase)
  {
    CObjectVector<CProperty> props;
    HRESULT setHr = S_OK;
    if (phase == 1 || phase == 2 || phase == 3 || phase == 6 || phase == 8)
    {
      CProperty &p = props.AddNew();
      p.Name = L"cp";
      p.Value = phase == 1 ? L"932" : phase == 3 ? L"65001" : L"936";
    }
    if (phase == 7)
    {
      CProperty &p = props.AddNew();
      p.Name = zip ? L"tar.cp" : L"zip.cp";
      p.Value = L"932";
    }
    if (phase == 4) setHr = SetProperties(arc, props);
    else if (phase == 9) setHr = setter->SetProperties(NULL, NULL, 0);
    else if (phase) setHr = SetProperties(arc, props, zip ? UString(L"zip") : UString(L"tar"));
    printf("%s{\"phase\":\"%s\",\"set_hr\":%u,", phase ? "," : "", labels[phase], (unsigned)setHr);
    if (openHr == S_OK) B02Names(arc);
    else printf("\"items\":[]");
    const HRESULT closeHr = arc->Close();
    streamSpec->Init(&data[0], data.size());
    const HRESULT reopenHr = arc->Open(stream, NULL, NULL);
    printf(",\"close_hr\":%u,\"reopen_hr\":%u,\"reopened\":{", (unsigned)closeHr, (unsigned)reopenHr);
    if (reopenHr == S_OK) B02Names(arc);
    else printf("\"items\":[]");
    printf("}}");
  }
  printf("]}\n");
  arc->Close();
  return openHr == S_OK ? 0 : 94;
}
