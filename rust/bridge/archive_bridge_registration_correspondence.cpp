#include "archive_bridge_registration_correspondence.h"

#include <cstring>
#include <cwchar>

namespace {
const unsigned kNativeRegistrationCount = 60;
const unsigned kTotalFormatCount = 61;

bool IsHash(const wchar_t *name)
{
  return name && std::wcscmp(name, L"Hash") == 0;
}

bool SameCaptureName(const wchar_t *row_name, const char *capture_name)
{
  if (!row_name || !capture_name)
    return false;
  while (*row_name && *capture_name)
  {
    if ((wchar_t)(unsigned char)*capture_name != *row_name)
      return false;
    ++row_name;
    ++capture_name;
  }
  return *row_name == 0 && *capture_name == 0;
}
}  // namespace

bool ArchiveBridgeValidateRegistrationCorrespondence(
    const ArchiveBridgeRegistrationCapture *captures, unsigned capture_count,
    bool overflowed, const ArchiveBridgeRegistrationRow *rows,
    const ArchiveBridgeRegistrationRow *expected_rows, unsigned row_count) throw()
{
  if (!captures || !rows || !expected_rows || overflowed || capture_count != kNativeRegistrationCount
      || row_count != kTotalFormatCount)
    return false;

  unsigned consumed[kNativeRegistrationCount];
  std::memset(consumed, 0, sizeof(consumed));
  for (unsigned capture = 0; capture < kNativeRegistrationCount; capture++)
  {
    const char *name = captures[capture].Name;
    if (!name || name[0] == 0)
      return false;
    for (unsigned previous = 0; previous < capture; previous++)
      if (std::strcmp(name, captures[previous].Name) == 0)
        return false;
  }

  unsigned hash_count = 0;
  for (unsigned row = 0; row < kTotalFormatCount; row++)
  {
    const ArchiveBridgeRegistrationRow &candidate = rows[row];
    const ArchiveBridgeRegistrationRow &expected = expected_rows[row];
    if (!candidate.Name || candidate.Name[0] == 0)
      return false;
    if (!expected.Name || std::wcscmp(candidate.Name, expected.Name) != 0
        || candidate.Id != expected.Id)
      return false;
    if (IsHash(candidate.Name))
    {
      if (candidate.Id != UINT32_C(256))
        return false;
      hash_count++;
      continue;
    }
    if (candidate.Id == UINT32_C(256))
      return false;

    unsigned matches = 0;
    for (unsigned capture = 0; capture < kNativeRegistrationCount; capture++)
    {
      if (SameCaptureName(candidate.Name, captures[capture].Name))
      {
        matches++;
        consumed[capture]++;
        if (candidate.Id != captures[capture].Id)
          return false;
      }
    }
    if (matches != 1)
      return false;
  }
  if (hash_count != 1)
    return false;
  for (unsigned capture = 0; capture < kNativeRegistrationCount; capture++)
    if (consumed[capture] != 1)
      return false;
  return true;
}
