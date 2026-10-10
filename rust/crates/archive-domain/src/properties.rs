//! Lossless property snapshots. No serialization or native interpretation.
use crate::{EngineText, EntryId};

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum SignedInteger {
    I8(i8),
    I16(i16),
    I32(i32),
    I64(i64),
}
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum UnsignedInteger {
    U8(u8),
    U16(u16),
    U32(u32),
    U64(u64),
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum TimestampUnits {
    Filetime100Nanoseconds,
    /// Preserve an unrecognized source unit tag; do not interpret it as FILETIME.
    Unknown(u32),
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Timestamp {
    pub format: u32,
    pub units: TimestampUnits,
    pub raw_low: u64,
    /// Q1 FILETIME: original wReserved2 | (wReserved3 << 16).
    pub raw_high: u64,
    /// Q1 FILETIME: original wReserved1, not a synthesized precision.
    pub precision: u32,
    pub defined: bool,
    /// Optional presentation value only; never replaces original fields.
    pub display_instant: Option<std::time::SystemTime>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum PropertyValue {
    /// Present VT_EMPTY. Absence is no Property record, not this variant.
    Empty {
        original_type: u32,
    },
    Bool {
        original_type: u32,
        value: bool,
    },
    Signed {
        original_type: u32,
        value: SignedInteger,
    },
    Unsigned {
        original_type: u32,
        value: UnsignedInteger,
    },
    Text {
        original_type: u32,
        value: EngineText,
    },
    Timestamp {
        original_type: u32,
        value: Timestamp,
    },
    Bytes {
        original_type: u32,
        value: Vec<u8>,
    },
    Unsupported {
        original_type: u32,
    },
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum PropertySource {
    Variant,
    Raw,
    Unknown(u32),
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Property {
    pub id: u32,
    pub source: PropertySource,
    pub value: PropertyValue,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum EntryKind {
    File,
    Directory,
    Link,
    AlternateStream,
    Unknown,
}

/// Only populated when actually supplied by the handler, never reverse-encoded.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RawName {
    pub bytes: Vec<u8>,
    pub property_id: u32,
    pub source: PropertySource,
    pub original_type: u32,
}

/// Fully owned snapshot; cloning/dropping it never invokes the engine.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ArchiveEntry {
    pub id: EntryId,
    pub name: EngineText,
    pub display_text: String,
    pub raw_name: Option<RawName>,
    pub kind: EntryKind,
    pub unpacked_size: Option<u64>,
    pub packed_size: Option<u64>,
    pub encrypted: Option<bool>,
    /// Property IDs retain the role (creation/access/modification/other).
    pub timestamps: Vec<Property>,
    pub attributes: Vec<Property>,
    pub checksums: Vec<Property>,
    pub properties: Vec<Property>,
}
