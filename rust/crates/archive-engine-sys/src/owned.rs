//! A safe, owned-snapshot layer over the raw facade bindings.
//!
//! This module exists so that `archive-engine` — the safe adapter — can keep
//! `#![forbid(unsafe_code)]` and contain no raw pointer at all. Every unsafe
//! site in the workspace lives in this crate, each with its documented
//! invariant.
//!
//! What crosses out of here is plain owned data: no borrowed view, no handle
//! that a caller could use after the arena died.

use super::abi::{
    ARCHIVE_BRIDGE_V1_MAJOR, ARCHIVE_BRIDGE_V1_OK, ARCHIVE_BRIDGE_V1_REVISION,
    ArchiveBridgeCapabilityView, ArchiveBridgeContext, ArchiveBridgeContextOptions,
    ArchiveBridgeFormat, ArchiveBridgeInfo, ArchiveBridgeMethod,
};
use super::link;
use core::marker::PhantomData;

/// A plain owned copy of one published format row, with text already copied out
/// of the arena.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct FormatRow {
    pub index: u32,
    pub registration_id: u32,
    pub flags: u32,
    pub time_flags: u32,
    pub has_reader: u32,
    pub has_writer: u32,
    pub name: Vec<u16>,
    pub extensions: Vec<u16>,
    pub additional_extensions: Vec<u16>,
}

/// A plain owned copy of one published codec or hasher row.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MethodRow {
    pub method_id: u64,
    pub encoder: u32,
    pub decoder: u32,
    pub is_filter: u32,
    pub digest_size: u32,
    pub name: Vec<u16>,
}

/// A plain owned snapshot of one capability enumeration.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct CapabilitySnapshot {
    pub formats: Vec<FormatRow>,
    pub codecs: Vec<MethodRow>,
    pub hashers: Vec<MethodRow>,
    /// Retained verbatim so the adapter can refuse any nonzero value.
    pub qualified_operations: u64,
}

/// Why a snapshot could not be produced.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum SnapshotError {
    /// The facade returned this non-OK status, retained verbatim.
    Status(i32),
    /// The facade returned OK but violated its own output contract.
    Contract(&'static str),
}

/// Builds a caller `expected` record for the given target and digests.
///
/// There is deliberately no constructor that guesses the digests: they come
/// from the reviewed header bytes and the manifest emitted by
/// `rust/bridge/build-manifest.py`.
pub fn expected_info(
    target: u32,
    header_sha256: [u8; 32],
    build_manifest_sha256: [u8; 32],
) -> ArchiveBridgeInfo {
    let mut info = ArchiveBridgeInfo::empty();
    info.abi_major = ARCHIVE_BRIDGE_V1_MAJOR;
    info.revision = ARCHIVE_BRIDGE_V1_REVISION;
    info.pointer_bits = usize::BITS;
    info.target = target;
    // The declared marker for the only endianness the Q1 targets support.
    info.little_endian = 1;
    info.header_sha256 = header_sha256;
    info.build_manifest_sha256 = build_manifest_sha256;
    info
}

/// Runs the matched-build handshake. Allocates no context on any path.
pub fn handshake_info(expected: &ArchiveBridgeInfo) -> (i32, ArchiveBridgeInfo) {
    let mut actual = ArchiveBridgeInfo::empty();
    let status = link::handshake(expected, &mut actual);
    (status, actual)
}

/// An owning facade context handle.
///
/// Neither `Send` nor `Sync`: per `abi-v1.md` initial global execution is
/// serialized and only the owning worker may invoke context and result
/// operations.
pub struct OwnedContext {
    handle: *mut ArchiveBridgeContext,
    _not_send_sync: PhantomData<*const ()>,
}

impl OwnedContext {
    /// Creates a context. The facade re-checks the handshake internally, so
    /// skipping [`handshake_info`] cannot produce an incompatible context.
    pub fn create(expected: &ArchiveBridgeInfo) -> Result<Self, SnapshotError> {
        let options = ArchiveBridgeContextOptions {
            struct_size: core::mem::size_of::<ArchiveBridgeContextOptions>() as u32,
            abi_major: ARCHIVE_BRIDGE_V1_MAJOR,
            expected: *expected,
        };
        let (status, handle) = link::create_context(&options);
        if status != ARCHIVE_BRIDGE_V1_OK {
            // The facade nulls the output handle before any effect, so there is
            // nothing to release on this path.
            return Err(SnapshotError::Status(status));
        }
        if handle.is_null() {
            return Err(SnapshotError::Contract(
                "create_context returned OK with a null context handle",
            ));
        }
        Ok(Self {
            handle,
            _not_send_sync: PhantomData,
        })
    }

    /// Enumerates the retained capability tables and copies every row out of
    /// the facade's arena before releasing it.
    ///
    /// Every borrowed view lives only inside this call, and the result arena is
    /// destroyed before returning, so no borrowed pointer can outlive it.
    pub fn capability_snapshot(&self) -> Result<CapabilitySnapshot, SnapshotError> {
        let mut view = ArchiveBridgeCapabilityView::empty();
        // INVARIANT: `self.handle` is non-null and live for as long as `self`
        // exists, which covers this whole call; `OwnedContext` is not `Clone`
        // and `Drop` destroys the handle exactly once.
        #[allow(unsafe_code)]
        let (status, result) = unsafe { link::capabilities(self.handle, &mut view) };
        if status != ARCHIVE_BRIDGE_V1_OK {
            return Err(SnapshotError::Status(status));
        }
        if result.is_null() {
            return Err(SnapshotError::Contract(
                "capabilities returned OK with a null result handle",
            ));
        }
        // Copy everything out while the arena is still live, then release it
        // exactly once regardless of whether the copy succeeded.
        let copied = copy_snapshot(&view);
        // INVARIANT: `result` is the live handle this context just produced,
        // `self.handle` is its owning context, and every borrowed view taken
        // from it above has already been copied and dropped. The facade
        // additionally enforces exactly-once ownership, so this cannot double
        // free.
        #[allow(unsafe_code)]
        let released = unsafe { link::result_destroy(self.handle, result) };
        let snapshot = copied?;
        if released != ARCHIVE_BRIDGE_V1_OK {
            return Err(SnapshotError::Status(released));
        }
        Ok(snapshot)
    }
}

impl Drop for OwnedContext {
    fn drop(&mut self) {
        // Every result arena this context produced was already destroyed inside
        // the method that created it, so no dependent handle is live here and
        // the facade's `Busy` guard cannot trip during ordinary teardown.
        //
        // INVARIANT: the handle came from `create`, is non-null, and is
        // destroyed exactly once because `Drop` runs once and `OwnedContext`
        // is neither `Clone` nor `Copy`.
        #[allow(unsafe_code)]
        let _ = unsafe { link::destroy_context(self.handle) };
        self.handle = core::ptr::null_mut();
    }
}

fn copy_snapshot(view: &ArchiveBridgeCapabilityView) -> Result<CapabilitySnapshot, SnapshotError> {
    let formats = rows::<ArchiveBridgeFormat>(view.formats, view.format_count, "formats")?;
    let codecs = rows::<ArchiveBridgeMethod>(view.codecs, view.codec_count, "codecs")?;
    let hashers = rows::<ArchiveBridgeMethod>(view.hashers, view.hasher_count, "hashers")?;
    Ok(CapabilitySnapshot {
        formats: formats.iter().map(copy_format).collect(),
        codecs: codecs.iter().map(copy_method).collect(),
        hashers: hashers.iter().map(copy_method).collect(),
        qualified_operations: view.qualified_operations,
    })
}

fn rows<T: Copy>(data: *const T, count: u64, label: &'static str) -> Result<Vec<T>, SnapshotError> {
    // INVARIANT delegated to `link::copy_rows`: on OK the facade published
    // exactly `count` initialized, aligned `repr(C)` rows owned by the result
    // arena, which is still live at this point.
    #[allow(unsafe_code)]
    let copied = unsafe { link::copy_rows(data, count) };
    copied.map_err(|error| match (error, label) {
        (link::RowError::NullWithNonzeroCount, "formats") => {
            SnapshotError::Contract("nonzero format_count with a null formats pointer")
        }
        (link::RowError::NullWithNonzeroCount, "codecs") => {
            SnapshotError::Contract("nonzero codec_count with a null codecs pointer")
        }
        (link::RowError::NullWithNonzeroCount, _) => {
            SnapshotError::Contract("nonzero hasher_count with a null hashers pointer")
        }
        (link::RowError::CountNotAddressable, _) => {
            SnapshotError::Contract("capability row count exceeds this host's addressable range")
        }
    })
}

fn copy_format(row: &ArchiveBridgeFormat) -> FormatRow {
    FormatRow {
        index: row.index,
        registration_id: row.registration_id,
        flags: row.flags,
        time_flags: row.time_flags,
        has_reader: row.has_reader,
        has_writer: row.has_writer,
        name: text(&row.name),
        extensions: text(&row.extensions),
        additional_extensions: text(&row.additional_extensions),
    }
}

fn copy_method(row: &ArchiveBridgeMethod) -> MethodRow {
    MethodRow {
        method_id: row.method_id,
        encoder: row.encoder,
        decoder: row.decoder,
        is_filter: row.is_filter,
        digest_size: row.digest_size,
        name: text(&row.name),
    }
}

fn text(view: &super::abi::ArchiveBridgeText) -> Vec<u16> {
    // INVARIANT delegated to `link::text_code_units`: the view was published by
    // the facade into a result arena that is still live here.
    #[allow(unsafe_code)]
    unsafe {
        link::text_code_units(view)
    }
}
