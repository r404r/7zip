// Bridge-owned, allocation-free correspondence verifier used by production
// registration capture validation and its isolated negative controls.
#ifndef ARCHIVE_BRIDGE_REGISTRATION_CORRESPONDENCE_H
#define ARCHIVE_BRIDGE_REGISTRATION_CORRESPONDENCE_H

#include <stdint.h>

struct ArchiveBridgeRegistrationCapture
{
  const char *Name;
  uint32_t Id;
};

struct ArchiveBridgeRegistrationRow
{
  const wchar_t *Name;
  uint32_t Id;
};

// Verifies the frozen 60 native rows plus exactly one coordinator-added Hash
// row. Inputs are borrowed only; this function does not allocate or mutate.
bool ArchiveBridgeValidateRegistrationCorrespondence(
    const ArchiveBridgeRegistrationCapture *captures, unsigned capture_count,
    bool overflowed, const ArchiveBridgeRegistrationRow *rows,
    const ArchiveBridgeRegistrationRow *expected_rows, unsigned row_count);

#endif  // ARCHIVE_BRIDGE_REGISTRATION_CORRESPONDENCE_H
