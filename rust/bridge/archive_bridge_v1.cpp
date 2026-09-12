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

// The build system supplies the digests of the exact matched build. Absent or
// empty values make every handshake fail closed rather than silently accept an
// unidentified library.
#ifndef ARCHIVE_BRIDGE_V1_HEADER_SHA256_HEX
#define ARCHIVE_BRIDGE_V1_HEADER_SHA256_HEX ""
#endif
#ifndef ARCHIVE_BRIDGE_V1_BUILD_SHA256_HEX
#define ARCHIVE_BRIDGE_V1_BUILD_SHA256_HEX ""
#endif

// ---------------------------------------------------------------------------
// Retained CArcInfo registration-byte recovery
// ---------------------------------------------------------------------------
//
// CCodecs::Formats holds CArcInfoEx, which does not retain CArcInfo::Id. The
// registration byte is therefore captured at its source: the link wraps the
// retained registrar so every built-in CArcInfo pointer passed to it is
// recorded, and __real_ still runs, so CCodecs::Formats is built exactly as
// before. No retained source file is edited and no registration is dropped.
//
// The wrapped symbol is the C++-mangled name of
// RegisterArc(const CArcInfo *) as emitted by this host's Itanium C++ ABI
// toolchain; rust/bridge/makefile.gcc passes the matching --wrap option.
// Recovering this byte on a non-Itanium-ABI toolchain (native Windows MSVC) is
// a deferred obligation of S2a t_071e4cd7, not something this development
// slice claims to have solved.
#define ARCHIVE_BRIDGE_V1_REGISTER_ARC_SYMBOL _Z11RegisterArcPK8CArcInfo
#define ARCHIVE_BRIDGE_V1_CAT_(a, b) a##b
#define ARCHIVE_BRIDGE_V1_CAT(a, b) ARCHIVE_BRIDGE_V1_CAT_(a, b)
#define ARCHIVE_BRIDGE_V1_REAL_REGISTER_ARC \
  ARCHIVE_BRIDGE_V1_CAT(__real_, ARCHIVE_BRIDGE_V1_REGISTER_ARC_SYMBOL)
#define ARCHIVE_BRIDGE_V1_WRAP_REGISTER_ARC \
  ARCHIVE_BRIDGE_V1_CAT(__wrap_, ARCHIVE_BRIDGE_V1_REGISTER_ARC_SYMBOL)

extern "C" void ARCHIVE_BRIDGE_V1_REAL_REGISTER_ARC(const CArcInfo *arcInfo) throw();

namespace {

// Bound taken from the retained registrar itself (ArchiveExports.cpp:13 and
// LoadCodecs.cpp:112 both use kNumArcsMax = 72).
const unsigned kRegisteredArcsMax = 72;

const CArcInfo *g_registered_arcs[kRegisteredArcsMax];
unsigned g_registered_arc_count;

}  // namespace

extern "C" void ARCHIVE_BRIDGE_V1_WRAP_REGISTER_ARC(const CArcInfo *arcInfo) throw()
{
  // Static-initialization time, single-threaded, before any export runs.
  if (arcInfo && g_registered_arc_count < kRegisteredArcsMax)
    g_registered_arcs[g_registered_arc_count++] = arcInfo;
  ARCHIVE_BRIDGE_V1_REAL_REGISTER_ARC(arcInfo);
}

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
  archive_bridge_v1_text Add(const wchar_t *source)
  {
    archive_bridge_v1_text view;
    view.data = NULL;
    view.length = 0;
    if (!source || source[0] == 0)
      return view;  // An empty view may be null; abi-v1.md "Text" section.
    std::vector<uint16_t> *block = new std::vector<uint16_t>();
    try
    {
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
          // Not representable as UTF-16; refuse rather than truncate.
          delete block;
          throw std::bad_alloc();
        }
      }
      _blocks.push_back(block);
    }
    catch (...)
    {
      // push_back is the only throwing step left; block is still owned here.
      if (_blocks.empty() || _blocks.back() != block)
        delete block;
      throw;
    }
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

// Maps a retained format name to the CArcInfo registration byte recorded at
// registration time. Returns the literal 256 for a row that the retained
// library never registered as a CArcInfo slot -- the coordinator-added Hash
// handler from HashCalc.cpp. 256 explicitly means absent; it is never a
// fabricated native ID.
uint32_t RegistrationIdFor(const CArcInfoEx &format)
{
  for (unsigned i = 0; i < g_registered_arc_count; i++)
  {
    const CArcInfo *info = g_registered_arcs[i];
    if (info && info->Name && format.Name.IsEqualTo(info->Name))
      return (uint32_t)info->Id;
  }
  return UINT32_C(256);
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
