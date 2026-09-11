/* Q1 normative declaration artifact; not a production bridge implementation.
 * See abi-v1.md. Matched builds only. No C++/Rust exceptions across this ABI.
 */
#ifndef ARCHIVE_BRIDGE_V1_H
#define ARCHIVE_BRIDGE_V1_H
#include <stdint.h>

#if defined(_WIN32)
#define ARCHIVE_BRIDGE_V1_CALL __cdecl
#else
#define ARCHIVE_BRIDGE_V1_CALL
#endif
#ifdef __cplusplus
extern "C" {
#endif

#define ARCHIVE_BRIDGE_V1_MAJOR UINT32_C(1)
#define ARCHIVE_BRIDGE_V1_REVISION UINT32_C(1)
/* Status is int32_t, never a compiler-sized enum or an HRESULT alias. */
#define ARCHIVE_BRIDGE_V1_OK INT32_C(0)
#define ARCHIVE_BRIDGE_V1_INVALID_REQUEST INT32_C(1)
#define ARCHIVE_BRIDGE_V1_MISMATCH INT32_C(2)
#define ARCHIVE_BRIDGE_V1_STALE_ENTRY INT32_C(3)
#define ARCHIVE_BRIDGE_V1_UNSUPPORTED INT32_C(4)
#define ARCHIVE_BRIDGE_V1_ALLOCATION_FAILURE INT32_C(5)
#define ARCHIVE_BRIDGE_V1_INTERNAL_FAILURE INT32_C(6)
#define ARCHIVE_BRIDGE_V1_ENGINE_FAILURE INT32_C(7)
#define ARCHIVE_BRIDGE_V1_CANCELLED INT32_C(8)
#define ARCHIVE_BRIDGE_V1_INTERACTION_UNAVAILABLE INT32_C(9)
#define ARCHIVE_BRIDGE_V1_BUSY INT32_C(10)

typedef struct archive_bridge_v1_context archive_bridge_v1_context;
typedef struct archive_bridge_v1_result archive_bridge_v1_result;
/* All lengths count elements, not bytes except in bytes. */
typedef struct archive_bridge_v1_bytes {
  const uint8_t *data;
  uint64_t length;
} archive_bridge_v1_bytes;
typedef struct archive_bridge_v1_text {
  const uint16_t *data;
  uint64_t length;
} archive_bridge_v1_text;
#define ARCHIVE_BRIDGE_V1_PATH_WINDOWS UINT32_C(1)
#define ARCHIVE_BRIDGE_V1_PATH_UNIX UINT32_C(2)
typedef struct archive_bridge_v1_path {
  uint32_t tag;
  uint32_t reserved;
  archive_bridge_v1_bytes unix_bytes;
  archive_bridge_v1_text windows_units;
} archive_bridge_v1_path;

typedef struct archive_bridge_v1_identity {
  uint64_t archive_id;
  uint64_t generation;
  uint32_t chain_position;
  uint32_t item_index;
} archive_bridge_v1_identity;

#define ARCHIVE_BRIDGE_V1_VALUE_EMPTY UINT32_C(0)
#define ARCHIVE_BRIDGE_V1_VALUE_BOOL UINT32_C(1)
#define ARCHIVE_BRIDGE_V1_VALUE_SIGNED UINT32_C(2)
#define ARCHIVE_BRIDGE_V1_VALUE_UNSIGNED UINT32_C(3)
#define ARCHIVE_BRIDGE_V1_VALUE_TEXT UINT32_C(4)
#define ARCHIVE_BRIDGE_V1_VALUE_TIME UINT32_C(5)
#define ARCHIVE_BRIDGE_V1_VALUE_BYTES UINT32_C(6)
#define ARCHIVE_BRIDGE_V1_VALUE_UNSUPPORTED UINT32_C(7)
/* Time format/units and precision are original engine property metadata,
 * not an obligatory Unix epoch conversion. Unknown raw tags are preserved. */
typedef struct archive_bridge_v1_timestamp {
  uint32_t format;
  uint32_t precision;
  uint64_t raw_low;
  uint64_t raw_high;
  uint32_t defined;
  uint32_t reserved;
} archive_bridge_v1_timestamp;
typedef struct archive_bridge_v1_value {
  uint32_t tag;
  uint32_t original_type;
  uint32_t integer_width;
  uint32_t reserved;
  int64_t signed_value;
  uint64_t unsigned_value;
  archive_bridge_v1_text text;
  archive_bridge_v1_bytes bytes;
  archive_bridge_v1_timestamp timestamp;
} archive_bridge_v1_value;
typedef struct archive_bridge_v1_property {
  uint32_t property_id;
  uint32_t source_kind; /* 0 PROPVARIANT, 1 copied IArchiveGetRawProps */
  archive_bridge_v1_value value;
} archive_bridge_v1_property;
typedef struct archive_bridge_v1_scoped_property {
  archive_bridge_v1_text scope;
  archive_bridge_v1_text name;
  archive_bridge_v1_value value;
} archive_bridge_v1_scoped_property;

/* Original native domain/code stay separate from the bridge status. */
#define ARCHIVE_BRIDGE_V1_ERROR_NONE UINT32_C(0)
#define ARCHIVE_BRIDGE_V1_ERROR_HRESULT UINT32_C(1)
#define ARCHIVE_BRIDGE_V1_ERROR_WIN32 UINT32_C(2)
#define ARCHIVE_BRIDGE_V1_ERROR_ERRNO UINT32_C(3)
typedef struct archive_bridge_v1_diagnostic {
  uint32_t domain;
  uint32_t code;
  uint32_t chain_position;
  uint32_t flags;
  archive_bridge_v1_text message;
  const archive_bridge_v1_property *properties;
  uint64_t property_count;
} archive_bridge_v1_diagnostic;
typedef struct archive_bridge_v1_arc_error {
  uint32_t there_is_tail;
  uint32_t unexpected_end;
  uint32_t ignore_tail;
  uint32_t error_flags_defined;
  uint32_t error_flags;
  uint32_t warning_flags;
  int32_t error_format_index;
  uint32_t chain_position;
  uint64_t tail_size;
  archive_bridge_v1_text error_message;
  archive_bridge_v1_text warning_message;
} archive_bridge_v1_arc_error;
typedef struct archive_bridge_v1_chain {
  uint32_t chain_position;
  int32_t format_index;
  uint64_t item_count;
  int64_t offset;
  archive_bridge_v1_text format_name;
  const archive_bridge_v1_property *properties;
  uint64_t property_count;
  archive_bridge_v1_arc_error error;
} archive_bridge_v1_chain;
typedef struct archive_bridge_v1_entry {
  archive_bridge_v1_identity identity;
  archive_bridge_v1_text name;
  const archive_bridge_v1_property *properties;
  uint64_t property_count;
} archive_bridge_v1_entry;

typedef struct archive_bridge_v1_info {
  uint32_t struct_size;
  uint32_t abi_major;
  uint32_t revision;
  uint32_t pointer_bits;
  uint32_t target; /* 1 Linux x64, 2 Windows x64 MSVC, 3 macOS arm64 */
  uint32_t little_endian;
  uint8_t header_sha256[32];
  uint8_t build_manifest_sha256[32];
} archive_bridge_v1_info;
typedef struct archive_bridge_v1_context_options {
  uint32_t struct_size;
  uint32_t abi_major;
  archive_bridge_v1_info expected;
} archive_bridge_v1_context_options;

typedef struct archive_bridge_v1_format {
  uint32_t index;
  uint32_t registration_id; /* 0..255 native CArcInfo ID; 256 means absent */
  uint32_t flags;
  uint32_t time_flags;
  uint32_t has_reader;
  uint32_t has_writer;
  archive_bridge_v1_text name;
  archive_bridge_v1_text extensions;
  archive_bridge_v1_text additional_extensions;
} archive_bridge_v1_format;
typedef struct archive_bridge_v1_method {
  uint64_t method_id;
  uint32_t encoder;
  uint32_t decoder;
  uint32_t is_filter;
  uint32_t digest_size; /* nonzero for hashers only */
  archive_bridge_v1_text name;
} archive_bridge_v1_method;
typedef struct archive_bridge_v1_capability_view {
  uint32_t struct_size;
  uint32_t abi_major;
  const archive_bridge_v1_format *formats;
  uint64_t format_count;
  const archive_bridge_v1_method *codecs;
  uint64_t codec_count;
  const archive_bridge_v1_method *hashers;
  uint64_t hasher_count;
  uint64_t qualified_operations;
} archive_bridge_v1_capability_view;

#define ARCHIVE_BRIDGE_V1_QUESTION_PASSWORD UINT32_C(1)
#define ARCHIVE_BRIDGE_V1_QUESTION_VOLUME UINT32_C(2)
#define ARCHIVE_BRIDGE_V1_REPLY_UNAVAILABLE UINT32_C(0)
#define ARCHIVE_BRIDGE_V1_REPLY_CANCEL UINT32_C(1)
#define ARCHIVE_BRIDGE_V1_REPLY_PASSWORD_UNDEFINED UINT32_C(2)
#define ARCHIVE_BRIDGE_V1_REPLY_PASSWORD_DEFINED UINT32_C(3)
#define ARCHIVE_BRIDGE_V1_REPLY_VOLUME UINT32_C(4)
typedef struct archive_bridge_v1_question {
  uint32_t struct_size;
  uint32_t kind;
  uint64_t task_id;
  uint64_t request_id;
  uint64_t archive_id;
  uint64_t generation;
  archive_bridge_v1_text volume_name;
} archive_bridge_v1_question;
typedef struct archive_bridge_v1_reply {
  uint32_t struct_size;
  uint32_t kind;
  uint64_t request_id;
  archive_bridge_v1_text password;
  archive_bridge_v1_path volume_path;
} archive_bridge_v1_reply;
typedef struct archive_bridge_v1_progress {
  uint32_t struct_size;
  uint32_t counter_kind; /* 1 files, 2 bytes, 3 engine-specific */
  uint64_t task_id;
  uint64_t total;
  uint64_t completed;
  uint32_t total_defined;
  uint32_t completed_defined;
} archive_bridge_v1_progress;
typedef uint32_t (ARCHIVE_BRIDGE_V1_CALL *archive_bridge_v1_is_cancelled)(void *user);
typedef int32_t (ARCHIVE_BRIDGE_V1_CALL *archive_bridge_v1_on_progress)(
    void *user, const archive_bridge_v1_progress *event);
typedef int32_t (ARCHIVE_BRIDGE_V1_CALL *archive_bridge_v1_ask)(
    void *user, const archive_bridge_v1_question *question, archive_bridge_v1_reply *reply);
typedef struct archive_bridge_v1_operation {
  uint32_t struct_size;
  uint32_t abi_major;
  uint64_t task_id;
  void *user;
  archive_bridge_v1_is_cancelled is_cancelled;
  archive_bridge_v1_on_progress on_progress;
  archive_bridge_v1_ask ask;
} archive_bridge_v1_operation;

/* Bit flags map frontal=1, tail=2, mid=4 to COpenSpecFlags. */
typedef struct archive_bridge_v1_open_type {
  int32_t format_index;
  uint32_t forced_flags;
  uint32_t main_flags;
  uint32_t wrong_extension_flags;
  uint32_t unknown_extension_flags;
  uint32_t recursive;
  uint32_t can_return_arc;
  uint32_t can_return_parser;
  uint32_t is_hash_type;
  uint32_t each_position;
  uint32_t zeros_tail_allowed;
  uint32_t max_start_offset_defined;
  uint64_t max_start_offset;
} archive_bridge_v1_open_type;
typedef struct archive_bridge_v1_open_request {
  uint32_t struct_size;
  uint32_t abi_major;
  uint64_t archive_id;
  uint64_t generation;
  archive_bridge_v1_path source;
  archive_bridge_v1_open_type open_type;
  const archive_bridge_v1_open_type *types;
  uint64_t type_count;
  const int32_t *excluded_formats;
  uint64_t excluded_format_count;
  const archive_bridge_v1_scoped_property *properties;
  uint64_t property_count;
} archive_bridge_v1_open_request;
typedef struct archive_bridge_v1_entries_request {
  uint32_t struct_size;
  uint32_t abi_major;
  uint64_t archive_id;
  uint64_t generation;
  uint32_t chain_position;
  uint32_t reserved;
  uint64_t first;
  uint64_t count;
} archive_bridge_v1_entries_request;
typedef struct archive_bridge_v1_view {
  uint32_t struct_size;
  uint32_t abi_major;
  uint64_t archive_id;
  uint64_t generation;
  const archive_bridge_v1_entry *entries;
  uint64_t entry_count;
  const archive_bridge_v1_property *archive_properties;
  uint64_t archive_property_count;
  const archive_bridge_v1_diagnostic *diagnostics;
  uint64_t diagnostic_count;
  const archive_bridge_v1_chain *chains;
  uint64_t chain_count;
  archive_bridge_v1_arc_error non_open_error;
} archive_bridge_v1_view;

int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_handshake(
    const archive_bridge_v1_info *expected, archive_bridge_v1_info *actual);
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_create_context(
    const archive_bridge_v1_context_options *options, archive_bridge_v1_context **context);
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_destroy_context(archive_bridge_v1_context *context);
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_capabilities(
    archive_bridge_v1_context *context, archive_bridge_v1_result **result,
    archive_bridge_v1_capability_view *view);
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_open(
    archive_bridge_v1_context *context, const archive_bridge_v1_open_request *request,
    const archive_bridge_v1_operation *operation, archive_bridge_v1_result **result,
    archive_bridge_v1_view *view);
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_entries(
    archive_bridge_v1_context *context, const archive_bridge_v1_entries_request *request,
    const archive_bridge_v1_operation *operation, archive_bridge_v1_result **result,
    archive_bridge_v1_view *view);
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_close(
    archive_bridge_v1_context *context, uint64_t archive_id, uint64_t generation);
int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_result_destroy(
    archive_bridge_v1_context *context, archive_bridge_v1_result *result);

#ifdef __cplusplus
}
#endif
#endif
