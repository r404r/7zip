// Test-only observer, copied into a disposable build tree, never production.
// Reads callback arguments synchronously; retains no engine pointers or ownership.
// Item/result calls run inside the console's existing MT_LOCK. Open is serial.
// ASCII JSON on stderr is a separate tagged channel. No message/exit inference.
#include <stdio.h>

static void B01Text(const UString &text)
{
  fputc('[', stderr);
  for (unsigned i = 0; i < text.Len(); ++i)
    fprintf(stderr, "%s%u", i ? "," : "", (unsigned)text[i]);
  fputc(']', stderr);
}

static void B01Error(const CArcErrorInfo &e, int level)
{
  fprintf(stderr, "B01_NATIVE {\"event\":\"arc_error\",\"level\":%d,"
      "\"ErrorFlags_Defined\":%u,\"ErrorFlags\":%u,\"WarningFlags\":%u,"
      "\"effective_error_flags\":%u,\"effective_warning_flags\":%u,"
      "\"ThereIsTail\":%u,\"UnexpecedEnd\":%u,\"IgnoreTail\":%u,"
      "\"ErrorFormatIndex\":%d,\"TailSize\":%llu,\"wchar_bits\":%u,\"ErrorMessage_units\":",
      level, (unsigned)e.ErrorFlags_Defined, (unsigned)e.ErrorFlags,
      (unsigned)e.WarningFlags, (unsigned)e.GetErrorFlags(),
      (unsigned)e.GetWarningFlags(), (unsigned)e.ThereIsTail,
      (unsigned)e.UnexpecedEnd, (unsigned)e.IgnoreTail, e.ErrorFormatIndex,
      (unsigned long long)e.TailSize, (unsigned)(sizeof(wchar_t) * 8));
  B01Text(e.ErrorMessage);
  fputs(",\"WarningMessage_units\":", stderr);
  B01Text(e.WarningMessage);
  fputs("}\n", stderr);
}

static void B01Open(const CArchiveLink &link, HRESULT result)
{
  fprintf(stderr, "B01_NATIVE {\"event\":\"open_result\",\"hresult_bits\":%u,\"levels\":%u}\n",
      (unsigned)(UInt32)result, (unsigned)link.Arcs.Size());
  FOR_VECTOR (i, link.Arcs)
    B01Error(link.Arcs[i].ErrorInfo, (int)i);
  // -1 identifies NonOpen_ErrorInfo, not an invented archive index.
  B01Error(link.NonOpen_ErrorInfo, -1);
  fflush(stderr);
}

static void B01Item(Int32 result, Int32 encrypted)
{
  fprintf(stderr, "B01_NATIVE {\"event\":\"item_result\",\"NOperationResult\":%d,\"encrypted\":%d}\n",
      (int)result, (int)encrypted);
  fflush(stderr);
}

static void B01Result(HRESULT result)
{
  fprintf(stderr, "B01_NATIVE {\"event\":\"extract_result\",\"hresult_bits\":%u}\n",
      (unsigned)(UInt32)result);
  fflush(stderr);
}
