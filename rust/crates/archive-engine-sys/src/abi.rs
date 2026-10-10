//! `repr(C)` declarations for the four in-scope `archive_bridge_v1` operations.
//!
//! Spelling, field order, types and constants come from the reviewed
//! `rust/bridge/archive_bridge_v1.h`, which is the layout authority. Field
//! offsets/sizes/alignments are proven equal across C11, C++17 and Rust 2024 by
//! `docs/ai-migration/qualification/check-layout.py` against
//! `docs/ai-migration/qualification/abi-layout.txt`.
//!
//! Only the declarations the four in-scope operations need are reproduced.
//! Structs for the reserved open/entries/close/extract/test/create operations
//! are deliberately absent: a reserved name is not an implementation.

#![allow(non_camel_case_types)]

/// Status is `i32` with the exact header macros, never a compiler-sized enum
/// and never an `HRESULT` alias.
pub const ARCHIVE_BRIDGE_V1_OK: i32 = 0;
pub const ARCHIVE_BRIDGE_V1_INVALID_REQUEST: i32 = 1;
pub const ARCHIVE_BRIDGE_V1_MISMATCH: i32 = 2;
pub const ARCHIVE_BRIDGE_V1_STALE_ENTRY: i32 = 3;
pub const ARCHIVE_BRIDGE_V1_ALLOCATION_FAILURE: i32 = 5;
pub const ARCHIVE_BRIDGE_V1_INTERNAL_FAILURE: i32 = 6;
pub const ARCHIVE_BRIDGE_V1_ENGINE_FAILURE: i32 = 7;
pub const ARCHIVE_BRIDGE_V1_BUSY: i32 = 10;

pub const ARCHIVE_BRIDGE_V1_MAJOR: u32 = 1;
pub const ARCHIVE_BRIDGE_V1_REVISION: u32 = 1;

/// `registration_id` sentinel: 256 explicitly means the retained library never
/// registered a `CArcInfo` slot for this row. It is never a fabricated native
/// ID. The only such row in the matched build is the coordinator-added `Hash`
/// handler from `CPP/7zip/UI/Common/HashCalc.cpp`.
pub const ARCHIVE_BRIDGE_V1_REGISTRATION_ID_ABSENT: u32 = 256;

/// Opaque, C++-owned context handle. Never allocated or freed by Rust.
#[repr(C)]
pub struct ArchiveBridgeContext {
    _opaque: [u8; 0],
}

/// Opaque, C++-owned immutable result arena handle. Never allocated or freed by
/// Rust.
#[repr(C)]
pub struct ArchiveBridgeResult {
    _opaque: [u8; 0],
}

/// Borrowed view of `u16` code units, including ill-formed UTF-16. `length`
/// counts elements, not bytes, and implies no NUL terminator. An empty view may
/// have a null pointer.
#[repr(C)]
#[derive(Clone, Copy)]
pub struct ArchiveBridgeText {
    pub data: *const u16,
    pub length: u64,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub struct ArchiveBridgeInfo {
    pub struct_size: u32,
    pub abi_major: u32,
    pub revision: u32,
    pub pointer_bits: u32,
    /// 1 Linux x64, 2 Windows x64 MSVC, 3 macOS arm64.
    pub target: u32,
    pub little_endian: u32,
    /// Raw 32-byte SHA-256 of the exact header bytes.
    pub header_sha256: [u8; 32],
    /// Raw 32-byte SHA-256 of the canonical input-identity object.
    pub build_manifest_sha256: [u8; 32],
}

#[repr(C)]
#[derive(Clone, Copy)]
pub struct ArchiveBridgeContextOptions {
    pub struct_size: u32,
    pub abi_major: u32,
    pub expected: ArchiveBridgeInfo,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub struct ArchiveBridgeFormat {
    pub index: u32,
    /// 0..=255 native `CArcInfo` ID, or 256 meaning absent.
    pub registration_id: u32,
    pub flags: u32,
    pub time_flags: u32,
    pub has_reader: u32,
    pub has_writer: u32,
    pub name: ArchiveBridgeText,
    pub extensions: ArchiveBridgeText,
    pub additional_extensions: ArchiveBridgeText,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub struct ArchiveBridgeMethod {
    pub method_id: u64,
    pub encoder: u32,
    pub decoder: u32,
    pub is_filter: u32,
    /// Nonzero for hashers only.
    pub digest_size: u32,
    pub name: ArchiveBridgeText,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub struct ArchiveBridgeCapabilityView {
    pub struct_size: u32,
    pub abi_major: u32,
    pub formats: *const ArchiveBridgeFormat,
    pub format_count: u64,
    pub codecs: *const ArchiveBridgeMethod,
    pub codec_count: u64,
    pub hashers: *const ArchiveBridgeMethod,
    pub hasher_count: u64,
    /// Built capabilities are distinct from qualified operations. S2a-DEV
    /// observes the literal 0 here and enables nothing.
    pub qualified_operations: u64,
}

impl ArchiveBridgeInfo {
    /// All-zero info with only the declared envelope fields set. Used to build
    /// a caller `expected` record and as the writable `actual` output.
    pub fn empty() -> Self {
        Self {
            struct_size: core::mem::size_of::<Self>() as u32,
            abi_major: 0,
            revision: 0,
            pointer_bits: 0,
            target: 0,
            little_endian: 0,
            header_sha256: [0; 32],
            build_manifest_sha256: [0; 32],
        }
    }

    /// Fully zeroed info, including `struct_size`. Used only by the contract
    /// tests to prove a zeroed envelope is rejected rather than defaulted.
    pub fn empty_zeroed() -> Self {
        let mut info = Self::empty();
        info.struct_size = 0;
        info
    }
}

impl ArchiveBridgeCapabilityView {
    /// Zeroed view retaining the caller-supplied size and ABI major, exactly as
    /// `abi-v1.md` requires before any effect.
    pub fn empty() -> Self {
        Self {
            struct_size: core::mem::size_of::<Self>() as u32,
            abi_major: ARCHIVE_BRIDGE_V1_MAJOR,
            formats: core::ptr::null(),
            format_count: 0,
            codecs: core::ptr::null(),
            codec_count: 0,
            hashers: core::ptr::null(),
            hasher_count: 0,
            qualified_operations: 0,
        }
    }
}
