//! Safe adapter over the retained-engine facade.
//!
//! Scope (S2a-DEV, development acceptance only): the matched-build handshake,
//! context lifetime and capability enumeration. Nothing here opens an archive,
//! lists entries, extracts, tests or creates: those facade exports do not
//! exist yet, and a reserved ABI name is not permission to expose its
//! operation.
//!
//! The whole surface is behind the non-default `facade` feature, so the default
//! workspace build links no native code and is behaviorally unchanged.
//!
//! Safety posture: this crate contains no `unsafe`, no foreign-function
//! declaration and no raw pointer in its public API. `archive-engine-sys` owns
//! the FFI boundary; `rust/tests/check_boundaries.py` enforces that split, and
//! its conservative scan intentionally rejects even the spelling of those
//! tokens here.

#![forbid(unsafe_code)]

#[cfg(feature = "facade")]
mod facade;

#[cfg(feature = "facade")]
pub use facade::{
    BridgeStatus, Capabilities, EngineError, FacadeContext, FormatCapability, LoadedBuild,
    MatchedBuild, MethodCapability, REGISTRATION_ID_ABSENT, handshake,
};

/// No facade operation is qualified for production use by this slice.
///
/// The facade reports `qualified_operations == 0` and the adapter refuses to
/// report otherwise. Bits 0..=4 (capabilities, open/list, extract, test,
/// create) may only be enabled by the later reviewed application gates in
/// `docs/ai-migration/qualification/abi-v1.md`.
pub const QUALIFIED_OPERATIONS: u64 = 0;

/// True when this build links the native facade.
pub const fn links_facade() -> bool {
    cfg!(feature = "facade")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn no_operation_is_qualified() {
        assert_eq!(QUALIFIED_OPERATIONS, 0);
    }

    #[test]
    fn facade_linkage_matches_feature() {
        assert_eq!(links_facade(), cfg!(feature = "facade"));
    }
}
