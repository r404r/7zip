//! Owned domain contracts. No archive operations or native resources.
#![forbid(unsafe_code)]

mod identity;
pub use identity::*;
mod properties;
pub use properties::*;
mod outcomes;
pub use outcomes::*;
mod requests;
pub use requests::*;
mod port;
pub use port::*;

/// Lossless retained UString code units. Display output is never a filesystem input.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct EngineText(Vec<u16>);

impl EngineText {
    pub fn new(units: Vec<u16>) -> Self {
        Self(units)
    }

    pub fn units(&self) -> &[u16] {
        &self.0
    }

    pub fn display_lossy(&self) -> String {
        String::from_utf16_lossy(&self.0)
    }
}

/// Unvalidated native locator. Platform adapters must check host tag, embedded
/// NUL and retained-engine representability before I/O, without normalization.
/// There is deliberately no conversion from display text or EngineText.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum NativePath {
    Windows(Vec<u16>),
    Unix(Vec<u8>),
}
