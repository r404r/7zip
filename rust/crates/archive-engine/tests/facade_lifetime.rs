//! S2a-DEV lifetime and envelope contract tests.
//!
//! These assert the facade's own guards, not the safe wrapper's discipline. The
//! adapter deliberately makes `Busy` and repeated-destroy unreachable, so the
//! states are driven through the raw-ABI probes in `archive-engine-sys`, which
//! is the one crate permitted scoped unsafe. This test file contains no
//! `unsafe` and no raw pointer.
//!
//! Nothing here opens an archive, reads a fixture, requests a password, writes
//! a path or processes hostile input.
#![cfg(feature = "facade")]

mod support;

use archive_engine_sys as sys;
use support::matched_info;

#[test]
fn destroy_context_reports_busy_while_a_result_is_live() {
    let probe = sys::probe_busy(&matched_info()).expect("matched context and enumeration");
    assert_eq!(probe.capabilities, sys::ARCHIVE_BRIDGE_V1_OK);
    assert!(
        probe.format_count > 0,
        "the enumeration must publish a real arena"
    );
    // Enumerating a capability is never qualifying an operation.
    assert_eq!(probe.qualified_operations, 0);
    assert_eq!(
        probe.destroy_while_live,
        sys::ARCHIVE_BRIDGE_V1_BUSY,
        "destroy_context must report BUSY while a result handle is live"
    );
    assert_eq!(probe.release_result, sys::ARCHIVE_BRIDGE_V1_OK);
    assert_eq!(
        probe.destroy_after_release,
        sys::ARCHIVE_BRIDGE_V1_OK,
        "teardown must succeed once every dependent is released"
    );
}

#[test]
fn a_repeated_result_destroy_is_a_stale_entry() {
    let probe = sys::probe_exactly_once(&matched_info()).expect("matched context");
    assert_eq!(probe.first_release, sys::ARCHIVE_BRIDGE_V1_OK);
    assert_eq!(
        probe.second_release,
        sys::ARCHIVE_BRIDGE_V1_STALE_ENTRY,
        "exactly-once ownership: a repeated result_destroy must return STALE_ENTRY"
    );
    assert_eq!(probe.destroy_context, sys::ARCHIVE_BRIDGE_V1_OK);
}

#[test]
fn a_result_cannot_be_destroyed_through_a_foreign_context() {
    let probe = sys::probe_owner_check(&matched_info()).expect("two matched contexts");
    assert_eq!(
        probe.foreign_release,
        sys::ARCHIVE_BRIDGE_V1_STALE_ENTRY,
        "result_destroy must verify the owning context"
    );
    assert_eq!(probe.foreign_destroy, sys::ARCHIVE_BRIDGE_V1_OK);
    assert_eq!(probe.owner_release, sys::ARCHIVE_BRIDGE_V1_OK);
    assert_eq!(probe.owner_destroy, sys::ARCHIVE_BRIDGE_V1_OK);
}

#[test]
fn a_destroyed_context_handle_is_a_stale_entry() {
    let probe = sys::probe_stale_context(&matched_info()).expect("matched context");
    assert_eq!(probe.first_destroy, sys::ARCHIVE_BRIDGE_V1_OK);
    assert_eq!(
        probe.second_destroy,
        sys::ARCHIVE_BRIDGE_V1_STALE_ENTRY,
        "a handle the facade produced and then destroyed must be refused, not freed again"
    );
}

#[test]
fn malformed_envelopes_are_rejected_without_publishing_anything() {
    let probe = sys::probe_envelopes(&matched_info()).expect("matched context");
    assert_eq!(
        probe.null_options,
        sys::ARCHIVE_BRIDGE_V1_INVALID_REQUEST,
        "a null options pointer must be an invalid request"
    );
    assert!(
        probe.null_options_left_handle_null,
        "output handles initialize to null before any effect"
    );
    assert_eq!(
        probe.zeroed_options,
        sys::ARCHIVE_BRIDGE_V1_INVALID_REQUEST,
        "a zeroed envelope must be rejected, never defaulted"
    );
    assert!(probe.zeroed_options_left_handle_null);
    assert_eq!(
        probe.oversized_view,
        sys::ARCHIVE_BRIDGE_V1_INVALID_REQUEST,
        "a larger envelope must not be silently accepted"
    );
    assert!(
        probe.oversized_view_unpublished,
        "a rejected view must retain the caller-supplied size and publish no pointer"
    );
    assert_eq!(probe.destroy_context, sys::ARCHIVE_BRIDGE_V1_OK);
}

#[test]
fn every_allocation_is_released_across_many_cycles() {
    // Leak accounting. Balance is observable rather than inferred: while any
    // arena is live the facade must report BUSY, and once every arena has been
    // released `destroy_context` must report OK. A leaked arena would keep the
    // live set non-empty and turn that final teardown into BUSY.
    let cycles = 64;
    let per_cycle = 4;
    let probe = sys::probe_allocation_balance(&matched_info(), cycles, per_cycle);
    assert_eq!(probe.first_unexpected_status, None);
    assert_eq!(probe.contexts_created, cycles);
    assert_eq!(probe.results_created, cycles * per_cycle);
    assert_eq!(
        probe.results_released_ok,
        cycles * per_cycle,
        "every result arena must be released exactly once with OK"
    );
    assert_eq!(
        probe.busy_observed_while_live, cycles,
        "every cycle must observe the BUSY guard while its arenas are live"
    );
    assert_eq!(
        probe.contexts_destroyed_ok, cycles,
        "every context must tear down cleanly, which is only possible with an empty live set"
    );
}
