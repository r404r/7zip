//! Private ABI boundary for the retained-engine facade (`archive_bridge_v1`).
//!
//! Scope: this crate declares the reviewed Q1 ABI, links the matched facade,
//! and hands the safe adapter plain owned snapshots. It is the ONLY crate in
//! the workspace that contains `unsafe`, `extern` or raw pointers;
//! `rust/tests/check_boundaries.py` enforces that.
//!
//! Safety posture:
//!
//! * Every declaration is `repr(C)` with fixed-width integer fields, matching
//!   the frozen layout proven by
//!   `docs/ai-migration/qualification/check-layout.py`.
//! * The crate lint is `unsafe_code = "deny"`, not `allow`, so every unsafe
//!   site is individually opted in next to its documented invariant.
//! * No Rust allocator ever touches a native handle; the facade owns every
//!   context and result arena.
//! * Rust never unwinds into C: this crate defines no callback, and the four
//!   in-scope operations take no function pointer.
//! * [`OwnedContext`] is neither `Send` nor `Sync`.
//!
//! Everything native is gated behind the non-default `facade` feature, so the
//! default workspace build links nothing and is behaviorally unchanged.

#[cfg(feature = "facade")]
mod abi;
#[cfg(feature = "facade")]
mod link;
#[cfg(feature = "facade")]
mod owned;
#[cfg(feature = "facade")]
mod probe;

#[cfg(feature = "facade")]
pub use abi::{
    ARCHIVE_BRIDGE_V1_ALLOCATION_FAILURE, ARCHIVE_BRIDGE_V1_BUSY, ARCHIVE_BRIDGE_V1_ENGINE_FAILURE,
    ARCHIVE_BRIDGE_V1_INTERNAL_FAILURE, ARCHIVE_BRIDGE_V1_INVALID_REQUEST, ARCHIVE_BRIDGE_V1_MAJOR,
    ARCHIVE_BRIDGE_V1_MISMATCH, ARCHIVE_BRIDGE_V1_OK, ARCHIVE_BRIDGE_V1_REGISTRATION_ID_ABSENT,
    ARCHIVE_BRIDGE_V1_REVISION, ARCHIVE_BRIDGE_V1_STALE_ENTRY, ArchiveBridgeInfo,
};
#[cfg(feature = "facade")]
pub use owned::{
    CapabilitySnapshot, FormatRow, MethodRow, OwnedContext, SnapshotError, expected_info,
    handshake_info,
};
#[cfg(feature = "facade")]
pub use probe::{
    AllocationBalanceProbe, BusyProbe, EnvelopeProbe, ExactlyOnceProbe, OwnershipProbe,
    StaleContextProbe, probe_allocation_balance, probe_busy, probe_envelopes, probe_exactly_once,
    probe_owner_check, probe_stale_context,
};

/// Declared even without the `facade` feature so callers can state, in safe
/// code, that no facade operation is qualified for production use.
///
/// S2a-DEV enables no bit. `qualified_operations` is the literal 0 in the
/// facade and stays that way until the reviewed application gates in
/// `docs/ai-migration/qualification/abi-v1.md` are passed.
pub const QUALIFIED_OPERATIONS_NONE: u64 = 0;

/// True when this build actually links the native facade.
pub const fn links_facade() -> bool {
    cfg!(feature = "facade")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn no_operation_is_qualified() {
        assert_eq!(QUALIFIED_OPERATIONS_NONE, 0);
    }

    #[test]
    fn facade_linkage_matches_feature() {
        assert_eq!(links_facade(), cfg!(feature = "facade"));
    }
}
