//! Archive snapshots and structured outcomes, independent of ABI memory layouts.
use crate::{ArchiveId, EngineText, EntryId, Generation, NativePath, Property};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum OperationKind {
    Capabilities,
    Open,
    Entries,
    Extract,
    Test,
    Create,
    Reopen,
    Close,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum NativeErrorDomain {
    HResult,
    Windows,
    Errno,
    Unknown(u32),
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Diagnostic {
    pub domain: NativeErrorDomain,
    pub code: u32,
    pub chain_position: Option<u32>,
    pub flags: u32,
    pub message: EngineText,
    pub properties: Vec<Property>,
    pub operation: OperationKind,
    pub redacted_path_context: Option<String>,
}

/// Original CArcErrorInfo definedness and nested context. No inferred defaults.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct OpenDiagnostic {
    pub chain_position: u32,
    pub there_is_tail: bool,
    pub unexpected_end: bool,
    pub ignore_tail: bool,
    pub error_flags_defined: bool,
    pub error_flags: u32,
    pub warning_flags: u32,
    pub error_format_index: i32,
    pub tail_size: u64,
    pub error_message: EngineText,
    pub warning_message: EngineText,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CallStatus {
    Succeeded,
    EngineFailure,
    NotRecognized,
    Cancelled,
    StaleEntry,
    InvalidRequest,
    UnsupportedCapability,
    AllocationFailure,
    InternalFailure,
    InteractionUnavailable,
    Busy,
    AbiMismatch,
    Unknown(u32),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ItemResultCategory {
    Succeeded,
    DataError,
    CrcError,
    HeaderError,
    WrongPassword,
    UnsupportedMethod,
    Unknown,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ItemResult {
    pub entry: Option<EntryId>,
    pub input: Option<NativePath>,
    pub original_result: u32,
    pub category: ItemResultCategory,
    pub diagnostics: Vec<Diagnostic>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum EffectState {
    Completed,
    Partial,
    Unknown,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct PartialEffect {
    pub path: NativePath,
    pub state: EffectState,
    /// None means no cleanup observation, not successful rollback.
    pub cleanup: Option<CallStatus>,
    pub diagnostics: Vec<Diagnostic>,
}

/// Call status is NOT an aggregate success predicate. Preserve ordered item
/// failures and partial artifacts even when the native call itself succeeded.
/// Later task infrastructure owns bounded batching/spooling of large reports.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct OperationOutcome {
    pub status: CallStatus,
    pub diagnostics: Vec<Diagnostic>,
    pub open_diagnostics: Vec<OpenDiagnostic>,
    pub items: Vec<ItemResult>,
    pub warnings: Vec<Diagnostic>,
    pub completed: u64,
    pub skipped: u64,
    pub partial_effects: Vec<PartialEffect>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum BuildTarget {
    LinuxX64,
    WindowsX64Msvc,
    MacosArm64,
    Unknown(u32),
}

/// Matched manifest identity (Q1 canonical input digest), not serialized JSON or
/// proof of qualification. The adapter must verify every field before allocation.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct BuildManifest {
    pub abi_major: u32,
    pub revision: u32,
    pub target: BuildTarget,
    pub pointer_bits: u32,
    pub little_endian: bool,
    pub header_sha256: [u8; 32],
    pub identity_sha256: [u8; 32],
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Support {
    Supported,
    Unsupported,
    Unknown,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct FormatCapability {
    /// Runtime-local CCodecs index; never persisted as a universal format ID.
    pub index: u32,
    pub registration_id: Option<u8>,
    pub flags: u32,
    pub time_flags: u32,
    pub has_reader: bool,
    pub has_writer: bool,
    pub name: EngineText,
    pub extensions: EngineText,
    pub additional_extensions: EngineText,
    pub read: Support,
    pub test: Support,
    pub create: Support,
    pub update: Support,
    pub volumes: Support,
    /// None means unknown, Some(empty) means known empty.
    pub property_ids: Option<Vec<u32>>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MethodCapability {
    pub id: u64,
    pub name: EngineText,
    pub encoder: bool,
    pub decoder: bool,
    pub is_filter: bool,
    pub digest_size: u32,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct CapabilitySet {
    pub manifest: BuildManifest,
    pub formats: Vec<FormatCapability>,
    pub codecs: Vec<MethodCapability>,
    pub hashers: Vec<MethodCapability>,
    /// Separate from built registry/factory presence. S1 enables nothing.
    pub qualified_features: Vec<OperationKind>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct HandlerChain {
    pub position: u32,
    pub format_index: i32,
    pub format_name: EngineText,
    pub item_count: u64,
    pub offset: i64,
    pub properties: Vec<Property>,
    pub diagnostic: OpenDiagnostic,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ArchiveState {
    Open,
    Closed,
    Unusable,
}

/// Snapshot, not the live worker registry. State may be historical after close.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Archive {
    pub id: ArchiveId,
    pub generation: Generation,
    pub source: NativePath,
    pub chain: Vec<HandlerChain>,
    pub capabilities: CapabilitySet,
    pub properties: Vec<Property>,
    pub open_diagnostics: Vec<OpenDiagnostic>,
    pub diagnostics: Vec<Diagnostic>,
    pub state: ArchiveState,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct OpenOutcome {
    pub archive: Option<Archive>,
    /// Preserve partial/nested open evidence even without a valid session.
    /// On success this agrees with Archive.chain; do not fabricate an Archive
    /// just to transport failed-open chains or their signed offsets/properties.
    pub chains: Vec<HandlerChain>,
    pub non_open_error: Option<OpenDiagnostic>,
    pub outcome: OperationOutcome,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct CreateOutcome {
    /// Observed output only; never implicitly opens an archive. Partial outputs
    /// also remain in outcome.partial_effects on failure or cancellation.
    pub output: Option<NativePath>,
    pub outcome: OperationOutcome,
}
