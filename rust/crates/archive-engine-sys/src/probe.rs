//! Lifetime-contract probes over the raw ABI.
//!
//! Why this module exists: the safe adapter deliberately makes the `Busy` and
//! exactly-once `StaleEntry` states unreachable — it destroys a result before
//! its context and consumes each result handle once. The facade enforces those
//! states independently of that discipline, so they must be exercised against
//! the raw exports rather than against the wrapper's good behaviour.
//!
//! Driving the raw exports needs raw pointers, which belong in this crate.
//! Each probe returns the raw statuses it observed, so the card's contract
//! tests in `archive-engine/tests/` can assert on them without any `unsafe`.
//!
//! Every probe cleans up after itself: on return no context and no result arena
//! it created is still live.

use super::abi::{
    ARCHIVE_BRIDGE_V1_MAJOR, ARCHIVE_BRIDGE_V1_OK, ArchiveBridgeCapabilityView,
    ArchiveBridgeContext, ArchiveBridgeContextOptions, ArchiveBridgeInfo, ArchiveBridgeResult,
};
use super::link;

/// Statuses observed while a result handle is deliberately kept live.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct BusyProbe {
    /// Status of `capabilities`, expected OK.
    pub capabilities: i32,
    /// Rows the enumeration published; proves the arena was real.
    pub format_count: u64,
    /// `qualified_operations` as reported, expected to be the literal 0.
    pub qualified_operations: u64,
    /// `destroy_context` attempted while the result is live, expected BUSY.
    pub destroy_while_live: i32,
    /// `result_destroy` for the live handle, expected OK.
    pub release_result: i32,
    /// `destroy_context` after the dependent is gone, expected OK.
    pub destroy_after_release: i32,
}

/// Statuses observed when the same result handle is destroyed twice.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct ExactlyOnceProbe {
    pub first_release: i32,
    /// Expected STALE_ENTRY, not a double free.
    pub second_release: i32,
    pub destroy_context: i32,
}

/// Statuses observed when a foreign context tries to free another's result.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct OwnershipProbe {
    /// Expected STALE_ENTRY: the facade checks the owning context.
    pub foreign_release: i32,
    pub foreign_destroy: i32,
    pub owner_release: i32,
    pub owner_destroy: i32,
}

/// Statuses observed when a destroyed context handle is reused.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct StaleContextProbe {
    pub first_destroy: i32,
    /// Expected STALE_ENTRY. An arbitrary pointer remains caller misuse that no
    /// status check can make safe; this only covers a handle the facade itself
    /// produced and then destroyed.
    pub second_destroy: i32,
}

/// Statuses and output state observed for rejected malformed envelopes.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct EnvelopeProbe {
    /// `create_context` with a null options pointer, expected INVALID_REQUEST.
    pub null_options: i32,
    /// True when the output handle was left null, as required before effects.
    pub null_options_left_handle_null: bool,
    /// `create_context` with an all-zero envelope, expected INVALID_REQUEST.
    pub zeroed_options: i32,
    pub zeroed_options_left_handle_null: bool,
    /// `capabilities` with an oversized view, expected INVALID_REQUEST: a
    /// larger envelope is never silently accepted.
    pub oversized_view: i32,
    /// True when the rejected view kept the caller-supplied size and published
    /// no borrowed pointer.
    pub oversized_view_unpublished: bool,
    pub destroy_context: i32,
}

/// Allocation accounting over many create/enumerate/destroy cycles.
///
/// Balance is observable rather than inferred: while any arena is live the
/// facade must report BUSY, and once every arena is released `destroy_context`
/// must report OK. A leaked arena would keep the live set non-empty and turn
/// that final teardown into BUSY.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct AllocationBalanceProbe {
    pub contexts_created: usize,
    pub results_created: usize,
    pub results_released_ok: usize,
    pub busy_observed_while_live: usize,
    pub contexts_destroyed_ok: usize,
    /// Any unexpected status encountered, so the caller can assert it is None.
    pub first_unexpected_status: Option<i32>,
}

fn options_for(expected: &ArchiveBridgeInfo) -> ArchiveBridgeContextOptions {
    ArchiveBridgeContextOptions {
        struct_size: core::mem::size_of::<ArchiveBridgeContextOptions>() as u32,
        abi_major: ARCHIVE_BRIDGE_V1_MAJOR,
        expected: *expected,
    }
}

fn create_raw(expected: &ArchiveBridgeInfo) -> Option<*mut ArchiveBridgeContext> {
    let options = options_for(expected);
    let (status, handle) = link::create_context(&options);
    if status != ARCHIVE_BRIDGE_V1_OK || handle.is_null() {
        return None;
    }
    Some(handle)
}

fn enumerate_raw(
    context: *mut ArchiveBridgeContext,
) -> (i32, *mut ArchiveBridgeResult, ArchiveBridgeCapabilityView) {
    let mut view = ArchiveBridgeCapabilityView::empty();
    // INVARIANT: `context` is a live handle from `create_raw`; the two output
    // slots are valid writable locals that the facade nulls and zeroes before
    // any effect.
    #[allow(unsafe_code)]
    let (status, result) = unsafe { link::capabilities(context, &mut view) };
    (status, result, view)
}

/// Keeps a result live, attempts teardown, then releases in the correct order.
pub fn probe_busy(expected: &ArchiveBridgeInfo) -> Option<BusyProbe> {
    let context = create_raw(expected)?;
    let (capabilities, result, view) = enumerate_raw(context);
    if capabilities != ARCHIVE_BRIDGE_V1_OK || result.is_null() {
        // INVARIANT: live handle, no dependent was published.
        #[allow(unsafe_code)]
        let _ = unsafe { link::destroy_context(context) };
        return None;
    }
    // INVARIANT: `context` is live and `result` is its live dependent, so this
    // exercises exactly the Busy guard.
    #[allow(unsafe_code)]
    let destroy_while_live = unsafe { link::destroy_context(context) };
    // INVARIANT: `result` is the live arena this context produced and has not
    // been released yet.
    #[allow(unsafe_code)]
    let release_result = unsafe { link::result_destroy(context, result) };
    // INVARIANT: every dependent is released, so the context can be destroyed.
    #[allow(unsafe_code)]
    let destroy_after_release = unsafe { link::destroy_context(context) };
    Some(BusyProbe {
        capabilities,
        format_count: view.format_count,
        qualified_operations: view.qualified_operations,
        destroy_while_live,
        release_result,
        destroy_after_release,
    })
}

/// Destroys the same result handle twice.
pub fn probe_exactly_once(expected: &ArchiveBridgeInfo) -> Option<ExactlyOnceProbe> {
    let context = create_raw(expected)?;
    let (status, result, _view) = enumerate_raw(context);
    if status != ARCHIVE_BRIDGE_V1_OK || result.is_null() {
        #[allow(unsafe_code)]
        let _ = unsafe { link::destroy_context(context) };
        return None;
    }
    // INVARIANT: first release of a live arena owned by this context.
    #[allow(unsafe_code)]
    let first_release = unsafe { link::result_destroy(context, result) };
    // INVARIANT: the handle is no longer in the context's live set, so the
    // facade must reject it as stale instead of freeing it again. This is the
    // behaviour under test.
    #[allow(unsafe_code)]
    let second_release = unsafe { link::result_destroy(context, result) };
    #[allow(unsafe_code)]
    let destroy_context = unsafe { link::destroy_context(context) };
    Some(ExactlyOnceProbe {
        first_release,
        second_release,
        destroy_context,
    })
}

/// Tries to free one context's result through a different live context.
pub fn probe_owner_check(expected: &ArchiveBridgeInfo) -> Option<OwnershipProbe> {
    let owner = create_raw(expected)?;
    let Some(foreign) = create_raw(expected) else {
        #[allow(unsafe_code)]
        let _ = unsafe { link::destroy_context(owner) };
        return None;
    };
    let (status, result, _view) = enumerate_raw(owner);
    if status != ARCHIVE_BRIDGE_V1_OK || result.is_null() {
        #[allow(unsafe_code)]
        let _ = unsafe { link::destroy_context(foreign) };
        #[allow(unsafe_code)]
        let _ = unsafe { link::destroy_context(owner) };
        return None;
    }
    // INVARIANT: `foreign` is live but does not own `result`, so the facade's
    // owner check must reject it.
    #[allow(unsafe_code)]
    let foreign_release = unsafe { link::result_destroy(foreign, result) };
    // INVARIANT: `foreign` has no dependents of its own.
    #[allow(unsafe_code)]
    let foreign_destroy = unsafe { link::destroy_context(foreign) };
    // INVARIANT: `owner` is live and still owns `result`.
    #[allow(unsafe_code)]
    let owner_release = unsafe { link::result_destroy(owner, result) };
    #[allow(unsafe_code)]
    let owner_destroy = unsafe { link::destroy_context(owner) };
    Some(OwnershipProbe {
        foreign_release,
        foreign_destroy,
        owner_release,
        owner_destroy,
    })
}

/// Destroys a context, then reuses the handle the facade just invalidated.
pub fn probe_stale_context(expected: &ArchiveBridgeInfo) -> Option<StaleContextProbe> {
    let context = create_raw(expected)?;
    // INVARIANT: live handle with no dependents.
    #[allow(unsafe_code)]
    let first_destroy = unsafe { link::destroy_context(context) };
    // INVARIANT: the facade produced this handle and has since invalidated it,
    // so it recognizes it as stale. This is deliberately NOT a claim about
    // arbitrary pointers, which remain caller misuse.
    #[allow(unsafe_code)]
    let second_destroy = unsafe { link::destroy_context(context) };
    Some(StaleContextProbe {
        first_destroy,
        second_destroy,
    })
}

/// Sends malformed envelopes and checks nothing is published.
pub fn probe_envelopes(expected: &ArchiveBridgeInfo) -> Option<EnvelopeProbe> {
    let mut handle: *mut ArchiveBridgeContext = core::ptr::null_mut();
    // INVARIANT: a null options pointer is exactly the malformed input under
    // test; the facade validates it before any dereference, and `&mut handle`
    // is a valid writable slot.
    #[allow(unsafe_code)]
    let null_options = unsafe { link::create_context_raw(core::ptr::null(), &mut handle) };
    let null_options_left_handle_null = handle.is_null();

    let zeroed = ArchiveBridgeContextOptions {
        struct_size: 0,
        abi_major: 0,
        expected: ArchiveBridgeInfo::empty_zeroed(),
    };
    let (zeroed_options, zeroed_handle) = link::create_context(&zeroed);
    let zeroed_options_left_handle_null = zeroed_handle.is_null();

    let context = create_raw(expected)?;
    let mut view = ArchiveBridgeCapabilityView::empty();
    view.struct_size += 8;
    let requested = view.struct_size;
    // INVARIANT: `context` is live; the oversized view is the malformed input
    // under test and the facade must reject it without publishing a pointer.
    #[allow(unsafe_code)]
    let (oversized_view, result) = unsafe { link::capabilities(context, &mut view) };
    let oversized_view_unpublished = result.is_null()
        && view.struct_size == requested
        && view.formats.is_null()
        && view.format_count == 0
        && view.codecs.is_null()
        && view.codec_count == 0
        && view.hashers.is_null()
        && view.hasher_count == 0;
    #[allow(unsafe_code)]
    let destroy_context = unsafe { link::destroy_context(context) };
    Some(EnvelopeProbe {
        null_options,
        null_options_left_handle_null,
        zeroed_options,
        zeroed_options_left_handle_null,
        oversized_view,
        oversized_view_unpublished,
        destroy_context,
    })
}

/// Runs `cycles` create/enumerate/destroy rounds with `per_cycle` arenas each.
pub fn probe_allocation_balance(
    expected: &ArchiveBridgeInfo,
    cycles: usize,
    per_cycle: usize,
) -> AllocationBalanceProbe {
    let mut probe = AllocationBalanceProbe {
        contexts_created: 0,
        results_created: 0,
        results_released_ok: 0,
        busy_observed_while_live: 0,
        contexts_destroyed_ok: 0,
        first_unexpected_status: None,
    };
    let note = |probe: &mut AllocationBalanceProbe, status: i32| {
        if status != ARCHIVE_BRIDGE_V1_OK && probe.first_unexpected_status.is_none() {
            probe.first_unexpected_status = Some(status);
        }
    };
    for _ in 0..cycles {
        let Some(context) = create_raw(expected) else {
            probe.first_unexpected_status = probe.first_unexpected_status.or(Some(i32::MIN));
            return probe;
        };
        probe.contexts_created += 1;
        let mut handles = Vec::new();
        for _ in 0..per_cycle {
            let (status, result, view) = enumerate_raw(context);
            note(&mut probe, status);
            if status != ARCHIVE_BRIDGE_V1_OK || result.is_null() {
                break;
            }
            // Enumerating a capability is never qualifying an operation.
            if view.qualified_operations != 0 && probe.first_unexpected_status.is_none() {
                probe.first_unexpected_status = Some(i32::MAX);
            }
            probe.results_created += 1;
            handles.push(result);
        }
        if !handles.is_empty() {
            // INVARIANT: `context` is live with live dependents, so the Busy
            // guard must trip.
            #[allow(unsafe_code)]
            let busy = unsafe { link::destroy_context(context) };
            if busy == super::abi::ARCHIVE_BRIDGE_V1_BUSY {
                probe.busy_observed_while_live += 1;
            } else if probe.first_unexpected_status.is_none() {
                probe.first_unexpected_status = Some(busy);
            }
        }
        for handle in handles {
            // INVARIANT: each handle is a distinct live arena owned by
            // `context` and released exactly once here.
            #[allow(unsafe_code)]
            let status = unsafe { link::result_destroy(context, handle) };
            note(&mut probe, status);
            if status == ARCHIVE_BRIDGE_V1_OK {
                probe.results_released_ok += 1;
            }
        }
        // INVARIANT: every dependent has been released. A leaked arena would
        // leave the live set non-empty and make this report Busy instead of OK,
        // which is exactly what the caller asserts against.
        #[allow(unsafe_code)]
        let status = unsafe { link::destroy_context(context) };
        note(&mut probe, status);
        if status == ARCHIVE_BRIDGE_V1_OK {
            probe.contexts_destroyed_ok += 1;
        }
    }
    probe
}
