// Internal, bridge-owned retained registrar redirection shim.
#include "CPP/7zip/Common/RegisterArc.h"
#include "archive_bridge_registration.h"

namespace {
const unsigned kRegisteredArcsMax = 72;
const CArcInfo *g_registered_arcs[kRegisteredArcsMax];
unsigned g_registered_arc_count;
bool g_registered_arc_overflow;
}  // namespace

void ArchiveBridgeRegisterArc(const CArcInfo *arcInfo) throw()
{
  if (g_registered_arc_count < kRegisteredArcsMax)
    g_registered_arcs[g_registered_arc_count++] = arcInfo;
  else
    g_registered_arc_overflow = true;
  RegisterArc(arcInfo);
}

unsigned ArchiveBridgeRegisteredArcCount() throw()
{
  return g_registered_arc_count;
}

const CArcInfo *ArchiveBridgeRegisteredArcAt(unsigned index) throw()
{
  return index < g_registered_arc_count ? g_registered_arcs[index] : 0;
}

bool ArchiveBridgeRegistrationOverflowed() throw()
{
  return g_registered_arc_overflow;
}
