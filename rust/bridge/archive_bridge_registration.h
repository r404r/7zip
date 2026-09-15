// Internal, bridge-owned registration capture. This is not part of the Q1 ABI.
#ifndef ARCHIVE_BRIDGE_REGISTRATION_H
#define ARCHIVE_BRIDGE_REGISTRATION_H

struct CArcInfo;

void ArchiveBridgeRegisterArc(const CArcInfo *arcInfo) throw();
unsigned ArchiveBridgeRegisteredArcCount() throw();
const CArcInfo *ArchiveBridgeRegisteredArcAt(unsigned index) throw();
bool ArchiveBridgeRegistrationOverflowed() throw();

#endif  // ARCHIVE_BRIDGE_REGISTRATION_H
