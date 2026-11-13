#include "archive_bridge_registration_correspondence.h"

#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <cwchar>

namespace {
const unsigned kNativeCount = 60;
const unsigned kRowCount = 61;

ArchiveBridgeRegistrationCapture g_captures[kNativeCount];
ArchiveBridgeRegistrationRow g_rows[kRowCount];
ArchiveBridgeRegistrationRow g_expected_rows[kRowCount];
char g_names[kNativeCount][8];
wchar_t g_wide_names[kNativeCount][8];

void Initialize()
{
  for (unsigned i = 0; i < kNativeCount; i++)
  {
    std::snprintf(g_names[i], sizeof(g_names[i]), "F%02u", i);
    std::swprintf(g_wide_names[i], sizeof(g_wide_names[i]) / sizeof(g_wide_names[i][0]), L"F%02u", i);
    g_captures[i].Name = g_names[i];
    g_captures[i].Id = i;
    g_rows[i].Name = g_wide_names[i];
    g_rows[i].Id = i;
  }
  g_rows[kNativeCount].Name = L"Hash";
  g_rows[kNativeCount].Id = 256;
  std::memcpy(g_expected_rows, g_rows, sizeof(g_rows));
}

bool Verify()
{
  return ArchiveBridgeValidateRegistrationCorrespondence(
      g_captures, kNativeCount, false, g_rows, g_expected_rows, kRowCount);
}

void Require(bool condition, const char *label)
{
  if (!condition)
  {
    std::fprintf(stderr, "FAIL: %s\n", label);
    std::exit(1);
  }
}

void NegativeWrongId()
{
  Initialize(); g_rows[0].Id++;
  Require(!Verify(), "wrong ID must fail closed");
}
void NegativeMissingRow()
{
  Initialize(); g_rows[0] = g_rows[1];
  Require(!Verify(), "missing row must fail closed");
}
void NegativeDuplicateRow()
{
  Initialize(); g_rows[1] = g_rows[0];
  Require(!Verify(), "duplicate row must fail closed");
}
void NegativeReorderedRows()
{
  Initialize(); ArchiveBridgeRegistrationRow row = g_rows[0]; g_rows[0] = g_rows[1]; g_rows[1] = row;
  Require(!Verify(), "reordered rows must fail closed");
}
void NegativeFalse256()
{
  Initialize(); g_rows[0].Id = 256;
  Require(!Verify(), "false 256 must fail closed");
}
void NegativeNativeIdOnHash()
{
  Initialize(); g_rows[kNativeCount].Id = 59;
  Require(!Verify(), "native ID on Hash must fail closed");
}
void NegativePhantom()
{
  Initialize(); g_rows[0].Name = L"Phantom";
  Require(!Verify(), "phantom format must fail closed");
}
void NegativeNull()
{
  Initialize(); g_captures[7].Name = 0;
  Require(!Verify(), "in-range null must fail closed");
}
void NegativeDuplicateCapture()
{
  Initialize(); g_captures[7].Name = g_captures[6].Name;
  Require(!Verify(), "duplicate captured name must fail closed");
}
void NegativeMissingHash()
{
  Initialize(); g_rows[kNativeCount].Name = L"F00"; g_rows[kNativeCount].Id = 0;
  Require(!Verify(), "missing Hash must fail closed");
}
void NegativeDuplicateHash()
{
  Initialize(); g_rows[0].Name = L"Hash"; g_rows[0].Id = 256;
  Require(!Verify(), "duplicate Hash must fail closed");
}
}  // namespace

int main()
{
  Initialize();
  Require(Verify(), "positive correspondence must pass");
  std::puts("PASS: correspondence positive control");
  NegativeWrongId(); NegativeMissingRow(); NegativeDuplicateRow(); NegativeReorderedRows();
  NegativeFalse256(); NegativeNativeIdOnHash(); NegativePhantom();
  std::puts("PASS: correspondence negative controls");
  Initialize();
  Require(!ArchiveBridgeValidateRegistrationCorrespondence(g_captures, kNativeCount, true, g_rows, g_expected_rows, kRowCount),
          "73rd-call overflow must fail closed");
  std::puts("PASS: 73rd-call overflow control");
  NegativeNull(); std::puts("PASS: in-range null control");
  NegativeDuplicateCapture(); std::puts("PASS: duplicate captured name control");
  NegativeMissingHash(); std::puts("PASS: missing Hash control");
  NegativeDuplicateHash(); std::puts("PASS: duplicate Hash control");
  return 0;
}
