#include <cstdio>
#include <cstdlib>

// Test-only declarations intentionally omit the retained C++98 throw()
// spelling so Apple Clang can audit this isolated C++11 test translation unit
// under -Weverything. The linked production shim retains its reviewed
// declarations and ordinary C++ symbol names.
struct CArcInfo;
void ArchiveBridgeRegisterArc(const CArcInfo *arcInfo);
unsigned ArchiveBridgeRegisteredArcCount();
const CArcInfo *ArchiveBridgeRegisteredArcAt(unsigned index);
bool ArchiveBridgeRegistrationOverflowed();
void RegisterArc(const CArcInfo *arcInfo);

namespace {
const unsigned kExpectedCapacity = 72;
const CArcInfo *g_forwarded[kExpectedCapacity + 2];
unsigned g_forwarded_count;

void Require(bool condition, const char *message)
{
  if (!condition)
  {
    std::fprintf(stderr, "FAIL: %s\n", message);
    std::exit(1);
  }
}
}  // namespace

void RegisterArc(const CArcInfo *arcInfo)
{
  if (g_forwarded_count < kExpectedCapacity + 2)
    g_forwarded[g_forwarded_count] = arcInfo;
  g_forwarded_count++;
}

int main()
{
  unsigned char arc_tokens[kExpectedCapacity + 1] = {};
  const unsigned null_index = 17;
  for (unsigned i = 0; i < kExpectedCapacity; i++)
  {
    const CArcInfo *arc = i == null_index ? NULL :
        static_cast<const CArcInfo *>(static_cast<const void *>(&arc_tokens[i]));
    ArchiveBridgeRegisterArc(arc);
    Require(g_forwarded_count == i + 1, "true registrar must be called exactly once");
    Require(g_forwarded[i] == arc, "true registrar must receive the identical pointer");
  }

  Require(ArchiveBridgeRegisteredArcCount() == kExpectedCapacity,
          "capture count must reach the 72-slot bound");
  Require(ArchiveBridgeRegisteredArcAt(null_index) == NULL,
          "an in-range null must occupy its capture slot");
  Require(!ArchiveBridgeRegistrationOverflowed(),
          "the 72nd call must not overflow");

  const CArcInfo *overflow_arc = static_cast<const CArcInfo *>(
      static_cast<const void *>(&arc_tokens[kExpectedCapacity]));
  ArchiveBridgeRegisterArc(overflow_arc);
  Require(g_forwarded_count == kExpectedCapacity + 1,
          "the 73rd call must be forwarded exactly once");
  Require(g_forwarded[kExpectedCapacity] == overflow_arc,
          "the 73rd call must preserve pointer identity");
  Require(ArchiveBridgeRegisteredArcCount() == kExpectedCapacity,
          "capture count must not wrap or grow after overflow");
  Require(ArchiveBridgeRegistrationOverflowed(),
          "the 73rd call must set sticky overflow");

  ArchiveBridgeRegisterArc(NULL);
  Require(g_forwarded_count == kExpectedCapacity + 2,
          "post-overflow calls must still be forwarded exactly once");
  Require(ArchiveBridgeRegisteredArcCount() == kExpectedCapacity,
          "post-overflow capture count must remain bounded");
  Require(ArchiveBridgeRegistrationOverflowed(),
          "overflow must remain sticky");

  std::puts("PASS: process-isolated registration shim controls");
  return 0;
}
