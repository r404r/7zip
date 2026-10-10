//! The safe facade adapter: RAII handles, owned snapshots, no raw pointers.
//!
//! Ownership rules implemented here, from
//! `docs/ai-migration/qualification/abi-v1.md`:
//!
//! * C++ owns contexts and immutable result arenas. Rust copies everything it
//!   needs out of a borrowed view before the result is destroyed, and never
//!   frees a native handle with a Rust allocator. All of that pointer work
//!   lives in `archive-engine-sys`; this crate keeps
//!   `#![forbid(unsafe_code)]`.
//! * A result is destroyed before its owning context, so `destroy_context`
//!   never has to report `Busy` during ordinary teardown. The `Busy` path is
//!   still real and tested, because the facade enforces it independently of
//!   this wrapper.
//! * Handles are neither `Send` nor `Sync`: initial global execution is
//!   serialized and only the owning worker may invoke context and result
//!   operations.

use archive_domain::EngineText;
use archive_engine_sys as sys;

/// `registration_id` sentinel meaning the retained library never registered a
/// `CArcInfo` slot for this row. It is never a fabricated native ID; in the
/// matched build the only such row is the coordinator-added `Hash` handler from
/// `CPP/7zip/UI/Common/HashCalc.cpp`.
pub const REGISTRATION_ID_ABSENT: u32 = sys::ARCHIVE_BRIDGE_V1_REGISTRATION_ID_ABSENT;

/// A raw bridge status, retained exactly as the facade returned it.
///
/// Deliberately not collapsed into a coarse success/failure flag: the
/// distinctions between `Mismatch`, `StaleEntry` and `Busy` are contractual.
/// It is not an `HRESULT` and not a process exit status.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct BridgeStatus(pub i32);

impl BridgeStatus {
    pub fn raw(self) -> i32 {
        self.0
    }
    pub fn is_ok(self) -> bool {
        self.0 == sys::ARCHIVE_BRIDGE_V1_OK
    }
    pub fn is_mismatch(self) -> bool {
        self.0 == sys::ARCHIVE_BRIDGE_V1_MISMATCH
    }
    pub fn is_stale_entry(self) -> bool {
        self.0 == sys::ARCHIVE_BRIDGE_V1_STALE_ENTRY
    }
    pub fn is_busy(self) -> bool {
        self.0 == sys::ARCHIVE_BRIDGE_V1_BUSY
    }
    pub fn is_invalid_request(self) -> bool {
        self.0 == sys::ARCHIVE_BRIDGE_V1_INVALID_REQUEST
    }
    pub fn is_allocation_failure(self) -> bool {
        self.0 == sys::ARCHIVE_BRIDGE_V1_ALLOCATION_FAILURE
    }
}

/// An adapter error.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum EngineError {
    /// The facade refused the matched-build handshake. There is no fallback.
    Mismatch(BridgeStatus),
    /// Any other non-OK facade status, retained verbatim.
    Bridge(BridgeStatus),
    /// The facade returned OK but violated its own output contract. The adapter
    /// refuses rather than inventing a value.
    ContractViolation(&'static str),
}

impl EngineError {
    fn from_snapshot(error: sys::SnapshotError) -> Self {
        match error {
            sys::SnapshotError::Status(status) => {
                let status = BridgeStatus(status);
                if status.is_mismatch() {
                    Self::Mismatch(status)
                } else {
                    Self::Bridge(status)
                }
            }
            sys::SnapshotError::Contract(message) => Self::ContractViolation(message),
        }
    }
}

/// The exact build identity a caller demands.
///
/// There is deliberately no constructor that guesses these values: the header
/// digest and the build identity digest come from the reviewed header bytes and
/// the manifest emitted by `rust/bridge/build-manifest.py`, supplied by the
/// application.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct MatchedBuild {
    pub target: u32,
    pub header_sha256: [u8; 32],
    pub build_manifest_sha256: [u8; 32],
}

impl MatchedBuild {
    pub fn new(target: u32, header_sha256: [u8; 32], build_manifest_sha256: [u8; 32]) -> Self {
        Self {
            target,
            header_sha256,
            build_manifest_sha256,
        }
    }

    fn to_info(self) -> sys::ArchiveBridgeInfo {
        sys::expected_info(self.target, self.header_sha256, self.build_manifest_sha256)
    }
}

/// What the loaded facade says about itself. Diagnostic only: a filled record
/// never grants fallback compatibility.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct LoadedBuild {
    pub abi_major: u32,
    pub revision: u32,
    pub pointer_bits: u32,
    pub target: u32,
    pub little_endian: u32,
    pub header_sha256: [u8; 32],
    pub build_manifest_sha256: [u8; 32],
}

/// Runs the matched-build handshake without allocating a context.
pub fn handshake(expected: MatchedBuild) -> (BridgeStatus, LoadedBuild) {
    let (status, actual) = sys::handshake_info(&expected.to_info());
    (
        BridgeStatus(status),
        LoadedBuild {
            abi_major: actual.abi_major,
            revision: actual.revision,
            pointer_bits: actual.pointer_bits,
            target: actual.target,
            little_endian: actual.little_endian,
            header_sha256: actual.header_sha256,
            build_manifest_sha256: actual.build_manifest_sha256,
        },
    )
}

/// One retained format row, fully owned.
///
/// `index` is local to this matched `CCodecs` table and is not stable across
/// products, sort orders or builds. Match rows by name and actual registration
/// identity, never by row index.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct FormatCapability {
    pub index: u32,
    /// `0..=255` native `CArcInfo` ID, or [`REGISTRATION_ID_ABSENT`] (256).
    pub registration_id: u32,
    /// Effective `CCodecs` flags for this runtime table.
    pub flags: u32,
    /// Effective `CCodecs` time flags. The retained built-in `LoadCodecs` path
    /// leaves this at its constructor default; that behavior is preserved here,
    /// not repaired, and it does not change any timestamp policy.
    pub time_flags: u32,
    /// Actual reader factory presence, not a claim about any operation.
    pub has_reader: bool,
    /// Actual writer factory presence. This is not proof of every create or
    /// update property.
    pub has_writer: bool,
    pub name: EngineText,
    pub extensions: EngineText,
    pub additional_extensions: EngineText,
}

impl FormatCapability {
    /// True when the retained library registered no `CArcInfo` slot for this
    /// row, i.e. it is a coordinator-added handler.
    pub fn is_coordinator_added(&self) -> bool {
        self.registration_id == REGISTRATION_ID_ABSENT
    }
}

/// One retained codec or hasher row, fully owned.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MethodCapability {
    pub method_id: u64,
    pub encoder: bool,
    pub decoder: bool,
    pub is_filter: bool,
    /// Nonzero for hashers only.
    pub digest_size: u32,
    pub name: EngineText,
}

/// An owned snapshot of the retained engine's built capability tables.
///
/// "Built" is not "qualified": the facade reports `qualified_operations == 0`
/// and the adapter refuses any other value.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Capabilities {
    pub formats: Vec<FormatCapability>,
    pub codecs: Vec<MethodCapability>,
    pub hashers: Vec<MethodCapability>,
}

impl Capabilities {
    /// Looks a format up by its retained name, the identity the Q1 contract
    /// says to match on.
    pub fn format_by_name(&self, name: &str) -> Option<&FormatCapability> {
        let wanted: Vec<u16> = name.encode_utf16().collect();
        self.formats.iter().find(|row| row.name.units() == wanted)
    }
}

/// An RAII facade context.
///
/// Neither `Send` nor `Sync`, inherited from the owned handle in
/// `archive-engine-sys`.
pub struct FacadeContext {
    inner: sys::OwnedContext,
}

impl FacadeContext {
    /// Creates a context. The facade re-checks the handshake internally, so
    /// skipping [`handshake`] cannot produce an incompatible context.
    pub fn create(expected: MatchedBuild) -> Result<Self, EngineError> {
        sys::OwnedContext::create(&expected.to_info())
            .map(|inner| Self { inner })
            .map_err(EngineError::from_snapshot)
    }

    /// Enumerates the retained capability tables.
    ///
    /// Every row is copied out of the facade's arena and the arena is released
    /// before this returns, so nothing borrowed escapes.
    pub fn capabilities(&self) -> Result<Capabilities, EngineError> {
        let snapshot = self
            .inner
            .capability_snapshot()
            .map_err(EngineError::from_snapshot)?;
        if snapshot.qualified_operations != crate::QUALIFIED_OPERATIONS {
            // Enumerating a capability is not qualifying an operation. Any
            // nonzero value here would be an unauthorized capability claim.
            return Err(EngineError::ContractViolation(
                "facade reported a nonzero qualified_operations bitmask",
            ));
        }
        Ok(Capabilities {
            formats: snapshot.formats.iter().map(format_from).collect(),
            codecs: snapshot.codecs.iter().map(method_from).collect(),
            hashers: snapshot.hashers.iter().map(method_from).collect(),
        })
    }
}

fn format_from(row: &sys::FormatRow) -> FormatCapability {
    FormatCapability {
        index: row.index,
        registration_id: row.registration_id,
        flags: row.flags,
        time_flags: row.time_flags,
        // The ABI declares these as 0/1 only; treat anything else as set rather
        // than assuming false.
        has_reader: row.has_reader != 0,
        has_writer: row.has_writer != 0,
        name: EngineText::new(row.name.clone()),
        extensions: EngineText::new(row.extensions.clone()),
        additional_extensions: EngineText::new(row.additional_extensions.clone()),
    }
}

fn method_from(row: &sys::MethodRow) -> MethodCapability {
    MethodCapability {
        method_id: row.method_id,
        encoder: row.encoder != 0,
        decoder: row.decoder != 0,
        is_filter: row.is_filter != 0,
        digest_size: row.digest_size,
        name: EngineText::new(row.name.clone()),
    }
}
