//! `extern "C"` declarations and the minimal scoped-unsafe wrappers over them.
//!
//! Every `unsafe` site carries an explicit `#[allow(unsafe_code)]` next to the
//! invariant it depends on; the crate lint is `deny`, so none can appear by
//! accident.
//!
//! The exported functions use `__cdecl` on Windows, overriding the retained
//! engine's `-Gr` default; on the POSIX targets the C ABI is the platform
//! default, which `extern "C"` already selects.
//!
//! Nothing here frees a native handle with a Rust allocator, and no Rust
//! closure or callback crosses the boundary, so Rust cannot unwind into C.

use super::abi::{
    ARCHIVE_BRIDGE_V1_MAJOR, ArchiveBridgeCapabilityView, ArchiveBridgeContext,
    ArchiveBridgeContextOptions, ArchiveBridgeInfo, ArchiveBridgeResult, ArchiveBridgeText,
};

// The four in-scope exports. Every other name reserved by the header (open,
// entries, close, extract, test, create) is deliberately NOT declared: a
// reserved name is not an implementation and not permission to expose it.
//
// These are `safe fn` in an `unsafe extern` block: the facade's contract is
// that each one validates its own arguments, treats any pointer it cannot
// recognize as a stale entry, catches every C++ exception at the boundary and
// converts it to an `i32` status. The raw pointers the callers pass in are
// produced under the documented invariants below.
#[allow(unsafe_code)]
unsafe extern "C" {
    /// Compares every `expected` info field against the loaded build. Allocates
    /// nothing on any path, including mismatch.
    #[link_name = "archive_bridge_v1_handshake"]
    safe fn archive_bridge_v1_handshake(
        expected: *const ArchiveBridgeInfo,
        actual: *mut ArchiveBridgeInfo,
    ) -> i32;

    #[link_name = "archive_bridge_v1_create_context"]
    safe fn archive_bridge_v1_create_context(
        options: *const ArchiveBridgeContextOptions,
        context: *mut *mut ArchiveBridgeContext,
    ) -> i32;

    #[link_name = "archive_bridge_v1_destroy_context"]
    safe fn archive_bridge_v1_destroy_context(context: *mut ArchiveBridgeContext) -> i32;

    #[link_name = "archive_bridge_v1_capabilities"]
    safe fn archive_bridge_v1_capabilities(
        context: *mut ArchiveBridgeContext,
        result: *mut *mut ArchiveBridgeResult,
        view: *mut ArchiveBridgeCapabilityView,
    ) -> i32;

    #[link_name = "archive_bridge_v1_result_destroy"]
    safe fn archive_bridge_v1_result_destroy(
        context: *mut ArchiveBridgeContext,
        result: *mut ArchiveBridgeResult,
    ) -> i32;
}

/// Runs the matched-build handshake.
///
/// Returns the raw bridge status and fills `actual` with the loaded build's
/// description. A filled `actual` is diagnostic only: it never grants fallback
/// compatibility.
pub fn handshake(expected: &ArchiveBridgeInfo, actual: &mut ArchiveBridgeInfo) -> i32 {
    // INVARIANT: both pointers come from live Rust references, so each is
    // non-null, aligned and points at exactly one initialized
    // `ArchiveBridgeInfo` whose layout the frozen ABI check proves identical to
    // the C declaration. The facade only reads `expected` and only writes
    // `actual`, both within this call, and allocates nothing.
    archive_bridge_v1_handshake(expected as *const _, actual as *mut _)
}

/// Creates a facade context, re-checking the handshake inside the facade so
/// skipping the handshake cannot produce an incompatible context.
///
/// On any non-OK status the returned pointer is null. The returned handle is
/// owned by C++ and must be released with [`destroy_context`], never with a
/// Rust allocator.
pub fn create_context(options: &ArchiveBridgeContextOptions) -> (i32, *mut ArchiveBridgeContext) {
    let mut context: *mut ArchiveBridgeContext = core::ptr::null_mut();
    // INVARIANT: `options` is a live Rust reference (non-null, aligned,
    // initialized, matching the C layout) that the facade only reads during the
    // call. `&mut context` is a valid writable slot for exactly one pointer;
    // the facade nulls it before any effect and only stores a handle it
    // allocated itself.
    let status = archive_bridge_v1_create_context(options as *const _, &mut context);
    (status, context)
}

/// Calls `create_context` with a caller-supplied raw options pointer.
///
/// Exists so the contract tests can prove that a null envelope is rejected
/// before any dereference and leaves the output handle null.
///
/// # Safety
///
/// `options` must be either null or a valid pointer to one initialized
/// `ArchiveBridgeContextOptions`.
#[allow(unsafe_code)]
pub unsafe fn create_context_raw(
    options: *const ArchiveBridgeContextOptions,
    context: *mut *mut ArchiveBridgeContext,
) -> i32 {
    // INVARIANT: `options` validity is this function's safety contract; the
    // facade checks for null before dereferencing. `context` comes from a live
    // Rust mutable reference at every call site in this crate.
    archive_bridge_v1_create_context(options, context)
}

/// Destroys a facade context.
///
/// Returns `ARCHIVE_BRIDGE_V1_BUSY` while any result handle from this context
/// is still live, so dependents must be destroyed first.
///
/// # Safety
///
/// `context` must be either null or a handle obtained from [`create_context`]
/// that has not already been destroyed. An arbitrary pointer is caller misuse
/// that no status check can make safe.
#[allow(unsafe_code)]
pub unsafe fn destroy_context(context: *mut ArchiveBridgeContext) -> i32 {
    // INVARIANT: delegated to this function's own safety contract above. The
    // facade additionally rejects handles it can recognize as already
    // destroyed, returning STALE_ENTRY rather than double-freeing.
    archive_bridge_v1_destroy_context(context)
}

/// Enumerates the retained engine's capability tables into a C++-owned result
/// arena.
///
/// On OK, `view` borrows memory owned by the returned result handle. The caller
/// must copy everything it needs out of the view before calling
/// [`result_destroy`].
///
/// # Safety
///
/// `context` must be a live handle from [`create_context`].
#[allow(unsafe_code)]
pub unsafe fn capabilities(
    context: *mut ArchiveBridgeContext,
    view: &mut ArchiveBridgeCapabilityView,
) -> (i32, *mut ArchiveBridgeResult) {
    let mut result: *mut ArchiveBridgeResult = core::ptr::null_mut();
    // INVARIANT: `context` liveness is this function's safety contract.
    // `&mut result` is a valid writable pointer slot the facade nulls before
    // any effect. `view` is a live Rust reference to one initialized
    // `ArchiveBridgeCapabilityView`; the facade zeroes it (retaining the
    // caller-supplied size/version) before publishing any borrowed pointer, and
    // every pointer it publishes is owned by `result`.
    let status = archive_bridge_v1_capabilities(context, &mut result, view as *mut _);
    (status, result)
}

/// Frees exactly one result arena.
///
/// The facade checks owner context and exactly-once ownership; a repeat returns
/// `ARCHIVE_BRIDGE_V1_STALE_ENTRY` rather than double-freeing.
///
/// # Safety
///
/// `context` must be the live context that produced `result`, and every view
/// borrowed from `result` must already be dead.
#[allow(unsafe_code)]
pub unsafe fn result_destroy(
    context: *mut ArchiveBridgeContext,
    result: *mut ArchiveBridgeResult,
) -> i32 {
    // INVARIANT: delegated to this function's own safety contract above.
    archive_bridge_v1_result_destroy(context, result)
}

/// Copies a borrowed `archive_bridge_v1_text` view into owned code units.
///
/// # Safety
///
/// The view must be one the facade published into a still-live result arena:
/// either empty, or `length` initialized, aligned `u16` elements at `data`.
#[allow(unsafe_code)]
pub unsafe fn text_code_units(text: &ArchiveBridgeText) -> Vec<u16> {
    if text.length == 0 || text.data.is_null() {
        // An empty view is permitted to have a null pointer, so it must never
        // be turned into a slice.
        return Vec::new();
    }
    // Checked element-count conversion before any indexing: a length this host
    // cannot address is a facade bug, not something to silently truncate.
    let Ok(length) = usize::try_from(text.length) else {
        return Vec::new();
    };
    // INVARIANT: per this function's safety contract `data` points at exactly
    // `length` initialized, aligned `u16` elements inside a live result arena
    // that outlives this call, and the facade never hands out an aliasing
    // mutable reference to that storage. The slice is copied immediately and
    // never retained.
    let units = unsafe { core::slice::from_raw_parts(text.data, length) };
    units.to_vec()
}

/// Why a published capability array could not be copied.
///
/// The adapter refuses rather than inventing a row, so these are contract
/// violations by the facade, not recoverable conditions.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RowError {
    /// A nonzero count arrived with a null array pointer.
    NullWithNonzeroCount,
    /// The count exceeds this host's addressable range.
    CountNotAddressable,
}

/// Copies `count` published capability rows into an owned `Vec`.
///
/// This is the only place a published capability array is dereferenced, so the
/// safe adapter crate needs no raw pointers and no `unsafe` at all.
///
/// # Safety
///
/// On an OK status the facade published exactly `count` initialized, aligned,
/// `repr(C)` rows owned by a result arena that must still be live for this
/// call.
#[allow(unsafe_code)]
pub unsafe fn copy_rows<T: Copy>(data: *const T, count: u64) -> Result<Vec<T>, RowError> {
    if count == 0 {
        // A zero count yields an empty result, not the all-rows sentinel, and a
        // null pointer is permitted here.
        return Ok(Vec::new());
    }
    if data.is_null() {
        return Err(RowError::NullWithNonzeroCount);
    }
    // Checked element-count conversion before any indexing.
    let Ok(length) = usize::try_from(count) else {
        return Err(RowError::CountNotAddressable);
    };
    // INVARIANT: per this function's safety contract `data` points at exactly
    // `length` initialized, aligned, `repr(C)` rows inside a live result arena
    // that outlives this call, and the facade hands out no aliasing mutable
    // reference to them. The rows are only read and copied immediately.
    let rows = unsafe { core::slice::from_raw_parts(data, length) };
    Ok(rows.to_vec())
}

/// Compile-time assertion that the declared ABI major matches the header.
const _: () = assert!(ARCHIVE_BRIDGE_V1_MAJOR == 1);
