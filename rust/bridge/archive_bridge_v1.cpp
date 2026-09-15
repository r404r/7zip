// archive_bridge_v1.cpp -- S2a-DEV retained-engine facade (development acceptance).
//
// Implements exactly four of the exports declared in the reviewed Q1 header:
//   archive_bridge_v1_handshake
//   archive_bridge_v1_create_context / archive_bridge_v1_destroy_context
//   archive_bridge_v1_capabilities
//   archive_bridge_v1_result_destroy
//
// Every other name reserved by archive_bridge_v1.h (open, entries, close,
// extract, test, create) is deliberately NOT defined here. A reserved name is
// not an implementation and not permission to expose its operation.
//
// Semantics are fixed by docs/ai-migration/qualification/abi-v1.md. No mature
// codec, encryption or handler logic is modified: this translation unit only
// reads the retained CCodecs registration tables.
//
// Boundary rules enforced here:
//   * Every exported function catches all C++ exceptions and converts them to
//     an int32_t bridge status. Nothing propagates across the ABI.
//   * A mismatching handshake allocates nothing.
//   * Contexts, results and the immutable result arenas are owned by C++ only.
//     Callers copy out of a view before destroying the result.
//   * destroy_context returns ARCHIVE_BRIDGE_V1_BUSY while any result is live.
//   * result_destroy is exactly-once: a repeat returns
//     ARCHIVE_BRIDGE_V1_STALE_ENTRY.
//   * qualified_operations is the literal 0. Enumerating a capability is not
//     qualifying an operation.

#include "CPP/Common/MyInitGuid.h"

#include <cstddef>
#include <cstdlib>
#include <cstring>
#include <new>
#include <vector>

#include "CPP/7zip/Common/RegisterArc.h"
#include "CPP/7zip/Common/RegisterCodec.h"
#include "CPP/7zip/Common/CreateCoder.h"
#include "CPP/7zip/UI/Common/HashCalc.h"
#include "CPP/7zip/UI/Common/LoadCodecs.h"

#include "archive_bridge_v1.h"
#include "archive_bridge_registration.h"
#include "archive_bridge_registration_correspondence.h"

// The build system supplies the digests of the exact matched build. Absent or
// empty values make every handshake fail closed rather than silently accept an
// unidentified library.
#ifndef ARCHIVE_BRIDGE_V1_HEADER_SHA256_HEX
#define ARCHIVE_BRIDGE_V1_HEADER_SHA256_HEX ""
#endif
#ifndef ARCHIVE_BRIDGE_V1_BUILD_SHA256_HEX
#define ARCHIVE_BRIDGE_V1_BUILD_SHA256_HEX ""
#endif

// Retained built-in codec and hasher tables, declared exactly as the retained
// CPP/7zip/UI/Console/Main.cpp:97-101 declares them.
extern unsigned g_NumCodecs;
extern const CCodecInfo *g_Codecs[];
extern unsigned g_NumHashers;
extern const CHasherInfo *g_Hashers[];

namespace {

// ---------------------------------------------------------------------------
// Matched build identity
// ---------------------------------------------------------------------------

bool HexNibble(char c, unsigned &out)
{
  if (c >= '0' && c <= '9') { out = (unsigned)(c - '0'); return true; }
  if (c >= 'a' && c <= 'f') { out = (unsigned)(c - 'a') + 10; return true; }
  return false;
}

// Parses exactly 64 lowercase hex characters into 32 raw bytes. Anything else,
// including an empty compile-time digest, yields false so the handshake fails
// closed instead of comparing against a fabricated identity.
bool ParseSha256Hex(const char *hex, uint8_t out[32])
{
  if (!hex)
    return false;
  size_t length = 0;
  while (hex[length] != 0)
  {
    if (++length > 64)
      return false;
  }
  if (length != 64)
    return false;
  for (unsigned i = 0; i < 32; i++)
  {
    unsigned high = 0, low = 0;
    if (!HexNibble(hex[i * 2], high) || !HexNibble(hex[i * 2 + 1], low))
      return false;
    out[i] = (uint8_t)((high << 4) | low);
  }
  return true;
}

uint32_t LoadedTarget()
{
  // 1 Linux x64, 2 Windows x64 MSVC, 3 macOS arm64, per abi-v1.md. An
  // unlisted host reports 0, which matches no caller expectation.
#if defined(_WIN32) && defined(_M_X64)
  return UINT32_C(2);
#elif defined(__APPLE__) && defined(__aarch64__)
  return UINT32_C(3);
#elif defined(__linux__) && defined(__x86_64__)
  return UINT32_C(1);
#else
  return UINT32_C(0);
#endif
}

uint32_t LoadedLittleEndian()
{
  const uint16_t probe = 0x0102;
  uint8_t bytes[2];
  std::memcpy(bytes, &probe, sizeof(bytes));
  return bytes[0] == 0x02 ? UINT32_C(1) : UINT32_C(0);
}

// Describes the build that is actually loaded. Filling `actual` is diagnostic
// only; it never grants fallback compatibility.
bool DescribeLoadedBuild(archive_bridge_v1_info &info)
{
  std::memset(&info, 0, sizeof(info));
  info.struct_size = (uint32_t)sizeof(archive_bridge_v1_info);
  info.abi_major = ARCHIVE_BRIDGE_V1_MAJOR;
  info.revision = ARCHIVE_BRIDGE_V1_REVISION;
  info.pointer_bits = (uint32_t)(sizeof(void *) * 8);
  info.target = LoadedTarget();
  info.little_endian = LoadedLittleEndian();
  const bool header_ok = ParseSha256Hex(ARCHIVE_BRIDGE_V1_HEADER_SHA256_HEX, info.header_sha256);
  const bool build_ok = ParseSha256Hex(ARCHIVE_BRIDGE_V1_BUILD_SHA256_HEX, info.build_manifest_sha256);
  return header_ok && build_ok && info.target != 0 && info.little_endian == 1;
}

// Compares every declared info field. Returns OK only on an exact match of all
// of them; a single differing field is a mismatch with no partial acceptance.
int32_t CompareInfo(const archive_bridge_v1_info *expected, archive_bridge_v1_info *actual)
{
  archive_bridge_v1_info loaded;
  const bool identified = DescribeLoadedBuild(loaded);
  if (actual)
    *actual = loaded;
  if (!expected)
    return ARCHIVE_BRIDGE_V1_INVALID_REQUEST;
  // Size must equal the matched declaration exactly; a larger envelope is not
  // silently accepted (abi-v1.md, "Handshake, initialization and errors").
  if (expected->struct_size != (uint32_t)sizeof(archive_bridge_v1_info))
    return ARCHIVE_BRIDGE_V1_INVALID_REQUEST;
  if (!identified)
    return ARCHIVE_BRIDGE_V1_MISMATCH;
  if (expected->abi_major != loaded.abi_major
      || expected->revision != loaded.revision
      || expected->pointer_bits != loaded.pointer_bits
      || expected->target != loaded.target
      || expected->little_endian != loaded.little_endian
      || std::memcmp(expected->header_sha256, loaded.header_sha256, 32) != 0
      || std::memcmp(expected->build_manifest_sha256, loaded.build_manifest_sha256, 32) != 0)
    return ARCHIVE_BRIDGE_V1_MISMATCH;
  return ARCHIVE_BRIDGE_V1_OK;
}

// ---------------------------------------------------------------------------
// Result arena
// ---------------------------------------------------------------------------
//
// A result owns every byte its views point at. The vectors below are never
// reallocated after the view is published, so the borrowed pointers stay valid
// until result_destroy.

class CTextArena
{
  // Each entry is one NUL-free block of UTF-16 code units. Blocks are stored
  // in separately owned vectors so that appending one never moves another.
  std::vector<std::vector<uint16_t> *> _blocks;

  // Owns a block until it is published into _blocks. Every failure path
  // destroys the block exactly once through this guard, so no error path in
  // Add performs a manual delete and no throw can free the block twice.
  class CBlockGuard
  {
    std::vector<uint16_t> *_block;

    CBlockGuard(const CBlockGuard &);
    CBlockGuard &operator=(const CBlockGuard &);

  public:
    CBlockGuard(): _block(new std::vector<uint16_t>()) {}
    ~CBlockGuard() { delete _block; }
    std::vector<uint16_t> *Get() const { return _block; }
    // Ownership moves to the caller; the guard becomes empty and its
    // destructor then deletes nothing.
    void Release() { _block = NULL; }
  };

public:
  CTextArena() {}

  ~CTextArena()
  {
    for (size_t i = 0; i < _blocks.size(); i++)
      delete _blocks[i];
  }

  // Copies a retained UString into the arena as uint16_t code units.
  // wchar_t is 32-bit on this host; a code point above the BMP is re-encoded
  // as a surrogate pair so no information is lost and no unit exceeds 16 bits.
  //
  // Exception safety: the block is owned by CBlockGuard for the whole build.
  // Release happens only after push_back has succeeded, so every throw path
  // (the refusal below, a push_back allocation failure, or anything else)
  // frees the block exactly once and never twice.
  archive_bridge_v1_text Add(const wchar_t *source)
  {
    archive_bridge_v1_text view;
    view.data = NULL;
    view.length = 0;
    if (!source || source[0] == 0)
      return view;  // An empty view may be null; abi-v1.md "Text" section.
    CBlockGuard guard;
    std::vector<uint16_t> *block = guard.Get();
    for (const wchar_t *p = source; *p != 0; p++)
    {
      const uint32_t code = (uint32_t)*p;
      if (code <= 0xFFFF)
        block->push_back((uint16_t)code);
      else if (code <= 0x10FFFF)
      {
        const uint32_t rest = code - 0x10000;
        block->push_back((uint16_t)(0xD800 + (rest >> 10)));
        block->push_back((uint16_t)(0xDC00 + (rest & 0x3FF)));
      }
      else
      {
        // Not representable as UTF-16; refuse rather than truncate. The guard
        // owns the block here, so this throw must not delete it by hand.
        throw std::bad_alloc();
      }
    }
    _blocks.push_back(block);
    guard.Release();  // Published; the arena destructor owns it from now on.
    view.data = block->empty() ? NULL : &(*block)[0];
    view.length = (uint64_t)block->size();
    return view;
  }
};

// The joined extension text the retained CLI prints for a format row
// (Main.cpp:1147-1159): "ext" or "ext (addext)", space separated.
UString JoinExtensions(const CArcInfoEx &format)
{
  UString joined;
  FOR_VECTOR (i, format.Exts)
  {
    if (i != 0)
      joined.Add_Space();
    const CArcExtInfo &ext = format.Exts[i];
    joined += ext.Ext;
    if (!ext.AddExt.IsEmpty())
    {
      joined += " (";
      joined += ext.AddExt;
      joined.Add_Char(')');
    }
  }
  return joined;
}

UString JoinAdditionalExtensions(const CArcInfoEx &format)
{
  UString joined;
  FOR_VECTOR (i, format.Exts)
  {
    const UString &additional = format.Exts[i].AddExt;
    if (additional.IsEmpty())
      continue;
    if (!joined.IsEmpty())
      joined.Add_Space();
    joined += additional;
  }
  return joined;
}

struct CBridgeContext;

struct CBridgeResult
{
  // Non-zero while the handle is live; cleared before the object is freed so a
  // stale pointer cannot be mistaken for a live one by an owner check alone.
  uint32_t Magic;
  CBridgeContext *Owner;
  CTextArena Text;
  std::vector<archive_bridge_v1_format> Formats;
  std::vector<archive_bridge_v1_method> Codecs;
  std::vector<archive_bridge_v1_method> Hashers;

  CBridgeResult(): Magic(0), Owner(NULL) {}
};

const uint32_t kContextMagic = UINT32_C(0x41423143);  // "AB1C"
const uint32_t kResultMagic = UINT32_C(0x41423152);   // "AB1R"

struct CBridgeContext
{
  uint32_t Magic;
  CCodecs *Codecs;
#ifdef Z7_EXTERNAL_CODECS
  // Breaks the CCodecs/Libs reference cycle on teardown exactly as the
  // retained CREATE_CODECS_OBJECT external branch does (LoadCodecs.h:469-475
  // and CReleaser at LoadCodecs.h:320-335).
  CCodecs::CReleaser Releaser;
  CExternalCodecs ExternalCodecs;
#endif
  // The retained non-external branch of CREATE_CODECS_OBJECT
  // (LoadCodecs.h:477-479) holds exactly this one COM reference. In that
  // configuration CCodecs::Libs does not exist, so there is no library cycle
  // for CReleaser to break; the reference drop alone is the retained teardown.
  CMyComPtr<IUnknown> CodecsRef;
  std::vector<CBridgeResult *> Live;

  CBridgeContext(): Magic(0), Codecs(NULL) {}
};

// Frozen Q1 Linux/Windows/Darwin built-in CCodecs order and registration IDs,
// transcribed from engine-build.json (SHA-256 4e9a98a95daced0f0b20f4db9011793c934a51328a63780a473685808195704b).
// This is an immutable bridge-owned oracle, not a value generated from the
// candidate table. Hash is the sole coordinator row and has no native ID.
const ArchiveBridgeRegistrationRow kFrozenQ1FormatRows[61] = {
  { L"7z", 7, 0 }, { L"APFS", 195, 0 }, { L"APM", 212, 0 }, { L"Ar", 236, 0 },
  { L"Arj", 4, 0 }, { L"Base64", 197, 0 }, { L"COFF", 198, 0 }, { L"Cab", 8, 0 },
  { L"Chm", 233, 0 }, { L"Compound", 229, 0 }, { L"Cpio", 237, 0 }, { L"CramFS", 211, 0 },
  { L"Dmg", 228, 0 }, { L"ELF", 222, 0 }, { L"Ext", 199, 0 }, { L"FAT", 218, 0 },
  { L"FLV", 214, 0 }, { L"GPT", 203, 0 }, { L"HFS", 227, 0 }, { L"Hxs", 206, 0 },
  { L"IHex", 205, 0 }, { L"Iso", 231, 0 }, { L"LP", 193, 0 }, { L"Lzh", 6, 0 },
  { L"MBR", 219, 0 }, { L"MachO", 223, 0 }, { L"MsLZ", 213, 0 }, { L"Mub", 226, 0 },
  { L"NTFS", 217, 0 }, { L"Nsis", 9, 0 }, { L"PE", 221, 0 }, { L"Ppmd", 13, 0 },
  { L"QCOW", 202, 0 }, { L"Rar", 3, 0 }, { L"Rar5", 204, 0 }, { L"Rpm", 235, 0 },
  { L"SWF", 215, 0 }, { L"SWFc", 216, 0 }, { L"Sparse", 194, 0 }, { L"Split", 234, 0 },
  { L"SquashFS", 210, 0 }, { L"TE", 207, 0 }, { L"UEFIc", 208, 0 }, { L"UEFIf", 209, 0 },
  { L"Udf", 224, 0 }, { L"VDI", 201, 0 }, { L"VHD", 220, 0 }, { L"VHDX", 196, 0 },
  { L"VMDK", 200, 0 }, { L"Xar", 225, 0 }, { L"Z", 5, 0 }, { L"bzip2", 2, 0 },
  { L"gzip", 239, 0 }, { L"lzma", 10, 0 }, { L"lzma86", 11, 0 }, { L"tar", 238, 0 },
  { L"wim", 230, 0 }, { L"xz", 12, 0 }, { L"zip", 1, 0 }, { L"zstd", 14, 0 },
  { L"Hash", 256, 0 }
};

// Checks the complete native registration capture before a context or result
// can be published. Hash is added by the coordinator and is the only row with
// no native registration byte. The function deliberately performs no repair:
// missing, duplicate, null, or unmatched rows fail the complete export.
bool ValidateRegistrationCorrespondence(const CCodecs &codecs)
{
  if (ArchiveBridgeRegistrationOverflowed() || ArchiveBridgeRegisteredArcCount() != 60
      || codecs.Formats.Size() != 61)
    return false;
  ArchiveBridgeRegistrationCapture captures[60];
  ArchiveBridgeRegistrationRow rows[61];
  for (unsigned i = 0; i < 60; i++)
  {
    const CArcInfo *info = ArchiveBridgeRegisteredArcAt(i);
    if (!info || !info->Name || info->Name[0] == 0)
      return false;
    captures[i].Name = info->Name;
    captures[i].Id = (uint32_t)info->Id;
  }
  FOR_VECTOR (index, codecs.Formats)
  {
    const CArcInfoEx &format = codecs.Formats[index];
    rows[index].Name = (const wchar_t *)format.Name;
    rows[index].Id = UINT32_C(257);
    if (format.Name.IsEqualTo("Hash"))
      rows[index].Id = UINT32_C(256);
    for (unsigned capture = 0; capture < 60; capture++)
    {
      if (format.Name.IsEqualTo(captures[capture].Name))
      {
        rows[index].Id = captures[capture].Id;
        break;
      }
    }
  }
  // Compare the live retained table to the independent frozen Q1 order before
  // allowing the arena to be built. Passing rows as both arguments would make
  // reorder drift self-consistent and therefore invisible.
  return ArchiveBridgeValidateRegistrationCorrespondence(
      captures, 60, false, rows, kFrozenQ1FormatRows, 61);
}

uint32_t RegistrationIdFor(const CArcInfoEx &format)
{
  if (format.Name.IsEqualTo("Hash"))
    return UINT32_C(256);
  for (unsigned i = 0; i < 60; i++)
  {
    const CArcInfo *info = ArchiveBridgeRegisteredArcAt(i);
    if (format.Name.IsEqualTo(info->Name))
      return (uint32_t)info->Id;
  }
  return UINT32_C(256);  // Unreachable after ValidateRegistrationCorrespondence().
}

void FillFormats(const CCodecs &codecs, CBridgeResult &result)
{
  result.Formats.reserve((size_t)codecs.Formats.Size());
  FOR_VECTOR (index, codecs.Formats)
  {
    const CArcInfoEx &format = codecs.Formats[index];
    archive_bridge_v1_format row;
    std::memset(&row, 0, sizeof(row));
    row.index = (uint32_t)index;
    row.registration_id = RegistrationIdFor(format);
    // Effective CCodecs flags/time flags for this runtime table, not the raw
    // library-observer metadata. abi-v1.md forbids repairing the retained
    // built-in TimeFlags default here.
    row.flags = (uint32_t)format.Flags;
    row.time_flags = (uint32_t)format.TimeFlags;
    // Actual factory presence, not a claim about every operation.
    row.has_reader = (format.CreateInArchive != NULL) ? UINT32_C(1) : UINT32_C(0);
    row.has_writer = (format.CreateOutArchive != NULL) ? UINT32_C(1) : UINT32_C(0);
    row.name = result.Text.Add((const wchar_t *)format.Name);
    const UString extensions = JoinExtensions(format);
    row.extensions = result.Text.Add((const wchar_t *)extensions);
    const UString additional = JoinAdditionalExtensions(format);
    row.additional_extensions = result.Text.Add((const wchar_t *)additional);
    result.Formats.push_back(row);
  }
}

void FillMethods(CBridgeResult &result)
{
  // Built-in registration tables only. The frozen Q1 identity pins
  // plugin_policy to built-in-only-no-external-discovery, so there is no
  // external module list to merge and no plugin search of any kind.
  result.Codecs.reserve((size_t)g_NumCodecs);
  for (unsigned i = 0; i < g_NumCodecs; i++)
  {
    const CCodecInfo &codec = *g_Codecs[i];
    archive_bridge_v1_method row;
    std::memset(&row, 0, sizeof(row));
    row.method_id = (uint64_t)codec.Id;
    row.encoder = (codec.CreateEncoder != NULL) ? UINT32_C(1) : UINT32_C(0);
    row.decoder = (codec.CreateDecoder != NULL) ? UINT32_C(1) : UINT32_C(0);
    row.is_filter = codec.IsFilter ? UINT32_C(1) : UINT32_C(0);
    row.digest_size = 0;  // Nonzero for hashers only.
    row.name = result.Text.Add((const wchar_t *)UString(codec.Name));
    result.Codecs.push_back(row);
  }
  result.Hashers.reserve((size_t)g_NumHashers);
  for (unsigned i = 0; i < g_NumHashers; i++)
  {
    const CHasherInfo &hasher = *g_Hashers[i];
    archive_bridge_v1_method row;
    std::memset(&row, 0, sizeof(row));
    row.method_id = (uint64_t)hasher.Id;
    row.encoder = 0;
    row.decoder = 0;
    row.is_filter = 0;
    row.digest_size = (uint32_t)hasher.DigestSize;
    row.name = result.Text.Add((const wchar_t *)UString(hasher.Name));
    result.Hashers.push_back(row);
  }
}

CBridgeContext *ValidContext(archive_bridge_v1_context *handle)
{
  if (!handle)
    return NULL;
  CBridgeContext *context = reinterpret_cast<CBridgeContext *>(handle);
  // An arbitrary invalid pointer remains caller misuse that no status check can
  // make safe (abi-v1.md, "Callback and allocation lifetime"). This only
  // rejects a destroyed or non-context handle we can recognize.
  if (context->Magic != kContextMagic)
    return NULL;
  return context;
}

}  // namespace

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------

extern "C" {

int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_handshake(
    const archive_bridge_v1_info *expected, archive_bridge_v1_info *actual)
{
  try
  {
    // Allocates nothing on any path, including mismatch.
    return CompareInfo(expected, actual);
  }
  catch (...)
  {
    return ARCHIVE_BRIDGE_V1_INTERNAL_FAILURE;
  }
}

int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_create_context(
    const archive_bridge_v1_context_options *options, archive_bridge_v1_context **context)
{
  // Output handles initialize to null before any effect.
  if (context)
    *context = NULL;
  if (!options || !context)
    return ARCHIVE_BRIDGE_V1_INVALID_REQUEST;
  try
  {
    if (options->struct_size != (uint32_t)sizeof(archive_bridge_v1_context_options)
        || options->abi_major != ARCHIVE_BRIDGE_V1_MAJOR)
      return ARCHIVE_BRIDGE_V1_INVALID_REQUEST;
    // Re-check the handshake here, so skipping handshake cannot produce an
    // incompatible context.
    const int32_t matched = CompareInfo(&options->expected, NULL);
    if (matched != ARCHIVE_BRIDGE_V1_OK)
      return matched;

    CBridgeContext *created = new (std::nothrow) CBridgeContext();
    if (!created)
      return ARCHIVE_BRIDGE_V1_ALLOCATION_FAILURE;
    try
    {
      // Retained CREATE_CODECS_OBJECT pattern (LoadCodecs.h:469-480). Both
      // branches hold one COM reference; the external branch also arms the
      // releaser and publishes the CExternalCodecs links.
      created->Codecs = new CCodecs;
      created->CodecsRef = created->Codecs;
#ifdef Z7_EXTERNAL_CODECS
      created->ExternalCodecs.GetCodecs = created->Codecs;
      created->ExternalCodecs.GetHashers = created->Codecs;
      created->Releaser.Set(created->Codecs);
#endif
      const HRESULT loaded = created->Codecs->Load();
      if (loaded != S_OK)
      {
        delete created;
        return ARCHIVE_BRIDGE_V1_ENGINE_FAILURE;
      }
      // The retained coordinator-added Hash handler, preserved exactly as the
      // retained callers add it (Main.cpp:1015).
      Codecs_AddHashArcHandler(created->Codecs);
      if (!ValidateRegistrationCorrespondence(*created->Codecs))
      {
        delete created;
        return ARCHIVE_BRIDGE_V1_ENGINE_FAILURE;
      }
      created->Magic = kContextMagic;
    }
    catch (...)
    {
      delete created;
      throw;
    }
    *context = reinterpret_cast<archive_bridge_v1_context *>(created);
    return ARCHIVE_BRIDGE_V1_OK;
  }
  catch (const std::bad_alloc &)
  {
    return ARCHIVE_BRIDGE_V1_ALLOCATION_FAILURE;
  }
  catch (...)
  {
    return ARCHIVE_BRIDGE_V1_INTERNAL_FAILURE;
  }
}

int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_destroy_context(
    archive_bridge_v1_context *context)
{
  try
  {
    CBridgeContext *owned = ValidContext(context);
    if (!owned)
      return ARCHIVE_BRIDGE_V1_STALE_ENTRY;
    // Busy while any dependent result handle is still live; the wrapper must
    // destroy dependents first.
    if (!owned->Live.empty())
      return ARCHIVE_BRIDGE_V1_BUSY;
    owned->Magic = 0;
    // ~CBridgeContext runs CCodecs::CReleaser, closing the library cycle.
    delete owned;
    return ARCHIVE_BRIDGE_V1_OK;
  }
  catch (...)
  {
    return ARCHIVE_BRIDGE_V1_INTERNAL_FAILURE;
  }
}

int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_capabilities(
    archive_bridge_v1_context *context, archive_bridge_v1_result **result,
    archive_bridge_v1_capability_view *view)
{
  if (result)
    *result = NULL;
  if (!result || !view)
    return ARCHIVE_BRIDGE_V1_INVALID_REQUEST;
  // The view keeps the caller-supplied size/version and is zeroed before any
  // effect; every borrowed pointer is null until the result exists.
  const uint32_t requested_size = view->struct_size;
  const uint32_t requested_major = view->abi_major;
  std::memset(view, 0, sizeof(*view));
  view->struct_size = requested_size;
  view->abi_major = requested_major;
  if (requested_size != (uint32_t)sizeof(archive_bridge_v1_capability_view)
      || requested_major != ARCHIVE_BRIDGE_V1_MAJOR)
    return ARCHIVE_BRIDGE_V1_INVALID_REQUEST;
  CBridgeContext *owned = ValidContext(context);
  if (!owned)
    return ARCHIVE_BRIDGE_V1_STALE_ENTRY;
  try
  {
    if (!ValidateRegistrationCorrespondence(*owned->Codecs))
      return ARCHIVE_BRIDGE_V1_ENGINE_FAILURE;
    CBridgeResult *created = new (std::nothrow) CBridgeResult();
    if (!created)
      return ARCHIVE_BRIDGE_V1_ALLOCATION_FAILURE;
    try
    {
      FillFormats(*owned->Codecs, *created);
      FillMethods(*created);
      owned->Live.push_back(created);
    }
    catch (...)
    {
      delete created;
      throw;
    }
    created->Owner = owned;
    created->Magic = kResultMagic;

    view->formats = created->Formats.empty() ? NULL : &created->Formats[0];
    view->format_count = (uint64_t)created->Formats.size();
    view->codecs = created->Codecs.empty() ? NULL : &created->Codecs[0];
    view->codec_count = (uint64_t)created->Codecs.size();
    view->hashers = created->Hashers.empty() ? NULL : &created->Hashers[0];
    view->hasher_count = (uint64_t)created->Hashers.size();
    // Built capabilities are not qualified operations. S2a-DEV enables none.
    view->qualified_operations = 0;
    *result = reinterpret_cast<archive_bridge_v1_result *>(created);
    return ARCHIVE_BRIDGE_V1_OK;
  }
  catch (const std::bad_alloc &)
  {
    return ARCHIVE_BRIDGE_V1_ALLOCATION_FAILURE;
  }
  catch (...)
  {
    return ARCHIVE_BRIDGE_V1_INTERNAL_FAILURE;
  }
}

int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_result_destroy(
    archive_bridge_v1_context *context, archive_bridge_v1_result *result)
{
  try
  {
    CBridgeContext *owned = ValidContext(context);
    if (!owned || !result)
      return ARCHIVE_BRIDGE_V1_STALE_ENTRY;
    CBridgeResult *target = reinterpret_cast<CBridgeResult *>(result);
    if (target->Magic != kResultMagic || target->Owner != owned)
      return ARCHIVE_BRIDGE_V1_STALE_ENTRY;
    // Exactly-once ownership: the handle must still be in this context's live
    // set. A repeat destroy therefore returns STALE_ENTRY, not a double free.
    for (size_t i = 0; i < owned->Live.size(); i++)
    {
      if (owned->Live[i] != target)
        continue;
      owned->Live.erase(owned->Live.begin() + (ptrdiff_t)i);
      target->Magic = 0;
      target->Owner = NULL;
      delete target;
      return ARCHIVE_BRIDGE_V1_OK;
    }
    return ARCHIVE_BRIDGE_V1_STALE_ENTRY;
  }
  catch (...)
  {
    return ARCHIVE_BRIDGE_V1_INTERNAL_FAILURE;
  }
}

}  // extern "C"

// ---------------------------------------------------------------------------
// Development self-test (not part of the shared library)
// ---------------------------------------------------------------------------
//
// Compiled only when ARCHIVE_BRIDGE_V1_SELF_TEST is defined, which the shared
// library build never does, so the exported surface is unchanged. It exists to
// cover CTextArena::Add's throw path, which no capability query can reach: the
// retained format/codec/hasher names are ASCII, so the "not representable as
// UTF-16" refusal is unreachable through the four exported operations. A
// bounded synthetic code point drives it directly.
//
// Double free is detected without a sanitizer or any external dependency by
// replacing global operator new/delete with a tracking pair: freeing a pointer
// that is not live is recorded as a violation instead of corrupting the heap.

#ifdef ARCHIVE_BRIDGE_V1_SELF_TEST

#include <cstdio>

namespace {

const size_t kAuditCapacity = 8192;

struct CHeapAudit
{
  void *Live[kAuditCapacity];
  size_t LiveCount;
  long Allocations;
  long Frees;
  long DoubleOrForeignFrees;
  bool Overflowed;

  void Reset()
  {
    LiveCount = 0;
    Allocations = 0;
    Frees = 0;
    DoubleOrForeignFrees = 0;
    Overflowed = false;
  }

  void Track(void *p)
  {
    Allocations++;
    if (LiveCount >= kAuditCapacity)
    {
      Overflowed = true;
      return;
    }
    Live[LiveCount++] = p;
  }

  // Returns false when p was not live: that is exactly a double or foreign
  // free, which is what this regression must catch.
  bool Untrack(void *p)
  {
    for (size_t i = 0; i < LiveCount; i++)
    {
      if (Live[i] != p)
        continue;
      Live[i] = Live[LiveCount - 1];
      LiveCount--;
      Frees++;
      return true;
    }
    DoubleOrForeignFrees++;
    return false;
  }
};

CHeapAudit g_Audit;
bool g_AuditEnabled = false;

}  // namespace

void *operator new(size_t size)
{
  if (size == 0)
    size = 1;
  void *p = std::malloc(size);
  if (!p)
    throw std::bad_alloc();
  if (g_AuditEnabled)
    g_Audit.Track(p);
  return p;
}

void operator delete(void *p) throw()
{
  if (!p)
    return;
  if (g_AuditEnabled && !g_Audit.Untrack(p))
    return;  // Do not hand a non-live pointer back to free().
  std::free(p);
}

// Sized and array forms must route to the same bookkeeping.
void *operator new[](size_t size) { return operator new(size); }
void operator delete[](void *p) throw() { operator delete(p); }
void operator delete(void *p, size_t) throw() { operator delete(p); }
void operator delete[](void *p, size_t) throw() { operator delete(p); }

namespace {

int g_Failures = 0;

void Check(bool condition, const char *what)
{
  std::printf("%s: %s\n", condition ? "ok" : "FAILED", what);
  if (!condition)
    g_Failures++;
}

// The refusal path: Add must throw, free the block exactly once, and leave the
// arena with nothing published.
void TestAddRefusalDoesNotDoubleFree()
{
  const wchar_t unrepresentable[] = { (wchar_t)0x110000, 0 };
  bool threw = false;
  g_Audit.Reset();
  g_AuditEnabled = true;
  {
    CTextArena arena;
    try
    {
      arena.Add(unrepresentable);
    }
    catch (const std::bad_alloc &)
    {
      threw = true;
    }
  }  // Arena destructor runs here; a published-and-guarded block would be
     // deleted twice and Untrack would record it.
  g_AuditEnabled = false;

  Check(threw, "Add refuses an unrepresentable code point by throwing");
  Check(g_Audit.Allocations >= 1,
      "the audit observed the block allocation (test is not vacuous)");
  Check(g_Audit.DoubleOrForeignFrees == 0,
      "Add's throw path performs no double free");
  Check(!g_Audit.Overflowed, "heap audit did not overflow");
  Check(g_Audit.Allocations == g_Audit.Frees,
      "every allocation on the throw path is released exactly once");
  Check(g_Audit.LiveCount == 0, "no block leaks after the arena is destroyed");
}

// Mixed input: valid text before the refusal, and the refusal must not disturb
// text already published in the same arena.
void TestRefusalAfterSuccessfulAdds()
{
  const wchar_t good[] = { 'z', 'i', 'p', 0 };
  const wchar_t astral[] = { (wchar_t)0x1F600, 0 };  // Surrogate pair path.
  const wchar_t unrepresentable[] = { 'a', (wchar_t)0x7FFFFFFF, 0 };
  bool threw = false;
  g_Audit.Reset();
  g_AuditEnabled = true;
  {
    CTextArena arena;
    const archive_bridge_v1_text first = arena.Add(good);
    const archive_bridge_v1_text second = arena.Add(astral);
    bool lengths_ok = (first.length == 3 && second.length == 2);
    bool surrogates_ok = (second.data != NULL
        && second.data[0] >= 0xD800 && second.data[0] <= 0xDBFF
        && second.data[1] >= 0xDC00 && second.data[1] <= 0xDFFF);
    bool preserved = false;
    try
    {
      arena.Add(unrepresentable);
    }
    catch (const std::bad_alloc &)
    {
      threw = true;
      // Text published before the refusal must still be intact.
      preserved = (first.data != NULL
          && first.data[0] == 'z' && first.data[1] == 'i' && first.data[2] == 'p');
    }
    g_AuditEnabled = false;
    Check(lengths_ok, "published views report their code-unit lengths");
    Check(surrogates_ok, "an astral code point becomes a surrogate pair");
    Check(preserved, "a later refusal does not disturb published text");
    g_AuditEnabled = true;
  }
  g_AuditEnabled = false;

  Check(threw, "Add still refuses when earlier adds succeeded");
  Check(g_Audit.DoubleOrForeignFrees == 0,
      "no double free with published blocks present");
  Check(g_Audit.LiveCount == 0, "arena releases published blocks exactly once");
}

// Repeating the refusal must stay balanced; a leak or double free would
// accumulate here rather than cancel out.
void TestRepeatedRefusalsStayBalanced()
{
  const wchar_t unrepresentable[] = { (wchar_t)0x200000, 0 };
  int thrown = 0;
  g_Audit.Reset();
  g_AuditEnabled = true;
  {
    CTextArena arena;
    for (int i = 0; i < 256; i++)
    {
      try
      {
        arena.Add(unrepresentable);
      }
      catch (const std::bad_alloc &)
      {
        thrown++;
      }
    }
  }
  g_AuditEnabled = false;

  Check(thrown == 256, "every one of 256 refusals throws");
  Check(g_Audit.DoubleOrForeignFrees == 0,
      "256 refusals perform no double free");
  Check(g_Audit.Allocations == g_Audit.Frees,
      "256 refusals stay allocation balanced");
  Check(g_Audit.LiveCount == 0, "256 refusals leak nothing");
}

// Guard against the audit itself being vacuous: a deliberate double free must
// be reported. Without this, a broken audit would make the tests above pass.
//
// The allocation functions are called explicitly rather than through
// `new int`/`delete`: C++14 lets the compiler elide a new/delete pair whose
// object never escapes, and GCC does elide it at -O1, which would leave this
// control auditing nothing. An explicit operator new call cannot be elided,
// and it exercises exactly the code path the audit replaces.
void TestAuditDetectsADeliberateDoubleFree()
{
  g_Audit.Reset();
  g_AuditEnabled = true;
  void *cell = ::operator new(sizeof(int));
  ::operator delete(cell);
  ::operator delete(cell);  // Intentional: the audit swallows the second one.
  g_AuditEnabled = false;
  Check(g_Audit.Allocations == 1, "the audit observed the control allocation");
  Check(g_Audit.DoubleOrForeignFrees == 1,
      "the heap audit reports a deliberate double free (control)");
  Check(g_Audit.Frees == 1, "the audit frees a double-deleted pointer only once");
}

}  // namespace

int main()
{
  std::printf("archive_bridge_v1 CTextArena self-test (development only)\n");
  TestAddRefusalDoesNotDoubleFree();
  TestRefusalAfterSuccessfulAdds();
  TestRepeatedRefusalsStayBalanced();
  TestAuditDetectsADeliberateDoubleFree();
  std::printf("%s: %d failure(s)\n", g_Failures == 0 ? "PASS" : "FAIL", g_Failures);
  return g_Failures == 0 ? 0 : 1;
}

#endif  // ARCHIVE_BRIDGE_V1_SELF_TEST
