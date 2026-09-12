//! S2a-DEV self-owned contract tests for the retained-engine facade.
//!
//! These run only with the non-default `facade` feature and a matched facade
//! library on the link path. They exercise the real retained engine's
//! registration tables through the real ABI.
//!
//! What they deliberately do NOT do: open an archive, read a fixture, request a
//! password, write a path, or process hostile input. Those belong to the
//! deferred behavior gates B01/B03/B05/B06 and B08.
//!
//! The expected capability table is the frozen Q1 reference
//! `docs/ai-migration/qualification/native-observations.json` /
//! `engine-build.json` for this host. It is read, never rewritten: if the
//! implementation disagrees with the frozen reference, this test fails and the
//! implementation is investigated.
#![cfg(feature = "facade")]

mod support;

use archive_engine::{EngineError, FacadeContext, handshake};
use support::{expected_registry, matched_build, mutated_builds, utf16};

#[test]
fn handshake_succeeds_on_a_matched_build() {
    let (status, loaded) = handshake(matched_build());
    assert!(
        status.is_ok(),
        "matched handshake rejected with status {}; loaded build was {:?}",
        status.raw(),
        loaded
    );
    // The loaded record must describe this host exactly, not a fallback.
    assert_eq!(loaded.abi_major, 1);
    assert_eq!(loaded.revision, 1);
    assert_eq!(loaded.pointer_bits, usize::BITS);
    assert_eq!(loaded.little_endian, 1);
    let expected = matched_build();
    assert_eq!(loaded.target, expected.target);
    assert_eq!(loaded.header_sha256, expected.header_sha256);
    assert_eq!(loaded.build_manifest_sha256, expected.build_manifest_sha256);
}

#[test]
fn handshake_rejects_each_individually_mutated_field() {
    for (field, mutated) in mutated_builds() {
        let (status, _loaded) = handshake(mutated);
        assert!(
            status.is_mismatch(),
            "mutating {field} alone did not produce MISMATCH; got status {}",
            status.raw()
        );
    }
}

#[test]
fn create_context_rejects_a_mutated_handshake() {
    // Re-checking inside create_context is what makes skipping the handshake
    // unable to produce an incompatible context.
    for (field, mutated) in mutated_builds() {
        match FacadeContext::create(mutated) {
            Err(EngineError::Mismatch(status)) => {
                assert!(status.is_mismatch(), "unexpected status for {field}");
            }
            Err(other) => panic!("mutating {field} produced {other:?} instead of Mismatch"),
            Ok(_context) => {
                panic!("mutating {field} still produced a context; the re-check is missing")
            }
        }
    }
}

#[test]
fn capabilities_match_the_frozen_q1_reference_exactly() {
    let context = FacadeContext::create(matched_build()).expect("matched context");
    let capabilities = context.capabilities().expect("capabilities");
    let reference = expected_registry();

    assert_eq!(
        capabilities.formats.len(),
        reference.formats.len(),
        "format row count differs from the frozen Q1 reference"
    );

    // Compare by name and actual registration identity, never by row index:
    // indices are local to this matched CCodecs table.
    for expected in &reference.formats {
        let row = capabilities
            .format_by_name(&expected.name)
            .unwrap_or_else(|| panic!("frozen format {} missing from the facade", expected.name));
        assert_eq!(
            row.registration_id, expected.registration_id,
            "registration id differs for format {}",
            expected.name
        );
        assert_eq!(
            row.flags, expected.flags,
            "flags differ for format {}",
            expected.name
        );
        // Effective CCodecs TimeFlags, NOT the raw registered CArcInfo value.
        //
        // abi-v1.md "Capabilities and qualification boundary" records these
        // separately on purpose: the retained built-in LoadCodecs path leaves
        // TimeFlags at the CArcInfoEx constructor default, while the dynamic
        // library path obtains the exported property. The frozen
        // `format_registry` rows carry the raw registered value observed
        // through the library's own exports, which is a different quantity.
        //
        // The facade is built on the built-in path, so the effective value it
        // must report is the constructor default. Asserting the raw value here
        // would demand exactly the "repair" that abi-v1.md forbids.
        assert_eq!(
            row.time_flags, expected.effective_time_flags,
            "effective time flags differ for format {}",
            expected.name
        );
        assert_eq!(
            row.has_writer, expected.has_writer,
            "writer factory presence differs for format {}",
            expected.name
        );
        assert!(
            row.has_reader,
            "every retained format row must expose a reader factory: {}",
            expected.name
        );
        assert_eq!(row.name.units(), utf16(&expected.name));
    }

    // Every row index in the table is distinct and covers 0..count.
    let mut indices: Vec<u32> = capabilities.formats.iter().map(|row| row.index).collect();
    indices.sort_unstable();
    let expected_indices: Vec<u32> = (0..capabilities.formats.len() as u32).collect();
    assert_eq!(indices, expected_indices);
}

#[test]
fn the_hash_handler_is_the_only_coordinator_added_row_and_reports_256() {
    let context = FacadeContext::create(matched_build()).expect("matched context");
    let capabilities = context.capabilities().expect("capabilities");

    let coordinator: Vec<&str> = capabilities
        .formats
        .iter()
        .filter(|row| row.is_coordinator_added())
        .map(|row| {
            // Retained names in the matched table are ASCII.
            Box::leak(String::from_utf16_lossy(row.name.units()).into_boxed_str()) as &str
        })
        .collect();
    assert_eq!(
        coordinator,
        vec!["Hash"],
        "exactly the coordinator-added Hash handler must report an absent registration id"
    );

    let hash = capabilities
        .format_by_name("Hash")
        .expect("Hash handler present");
    // The literal 256 from the reviewed ABI: absent, never a fabricated ID.
    assert_eq!(hash.registration_id, 256);
    assert_eq!(hash.registration_id, archive_engine::REGISTRATION_ID_ABSENT);
    // HashCalc.cpp registers both factories for the Hash handler.
    assert!(hash.has_reader && hash.has_writer);
    // Retained flags: kKeepName | kStartOpen | kByExtOnlyOpen | kHashHandler.
    assert_eq!(hash.flags, 12353);
    // Codecs_AddHashArcHandler never sets TimeFlags.
    assert_eq!(hash.time_flags, 0);
}

#[test]
fn codecs_and_hashers_match_the_frozen_q1_reference_exactly() {
    let context = FacadeContext::create(matched_build()).expect("matched context");
    let capabilities = context.capabilities().expect("capabilities");
    let reference = expected_registry();

    assert_eq!(capabilities.codecs.len(), reference.codecs.len());
    assert_eq!(capabilities.hashers.len(), reference.hashers.len());

    for expected in &reference.codecs {
        let row = capabilities
            .codecs
            .iter()
            .find(|row| row.name.units() == utf16(&expected.name))
            .unwrap_or_else(|| panic!("frozen codec {} missing", expected.name));
        assert_eq!(
            row.method_id, expected.method_id,
            "method id differs for codec {}",
            expected.name
        );
        assert_eq!(
            row.encoder, expected.encoder,
            "encoder availability differs for codec {}",
            expected.name
        );
        assert_eq!(
            row.decoder, expected.decoder,
            "decoder availability differs for codec {}",
            expected.name
        );
        assert_eq!(
            row.is_filter, expected.is_filter,
            "filter status differs for codec {}",
            expected.name
        );
        // digest_size is nonzero for hashers only.
        assert_eq!(
            row.digest_size, 0,
            "codec {} reported a digest size",
            expected.name
        );
    }

    for expected in &reference.hashers {
        let row = capabilities
            .hashers
            .iter()
            .find(|row| row.name.units() == utf16(&expected.name))
            .unwrap_or_else(|| panic!("frozen hasher {} missing", expected.name));
        assert_eq!(row.method_id, expected.method_id);
        assert_eq!(
            row.digest_size, expected.digest_size,
            "digest size differs for hasher {}",
            expected.name
        );
        assert!(row.digest_size > 0);
        // Hashers are not codecs: they expose no encoder/decoder/filter.
        assert!(!row.encoder && !row.decoder && !row.is_filter);
    }

    // No RAR writer and no RAR encoder may ever appear, matching the reviewed
    // Q1 boundary controls in docs/ai-migration/qualification/validate.py.
    for row in &capabilities.formats {
        let name = String::from_utf16_lossy(row.name.units());
        if name.starts_with("Rar") {
            assert!(!row.has_writer, "{name} must not expose a writer factory");
        }
    }
    for row in &capabilities.codecs {
        let name = String::from_utf16_lossy(row.name.units());
        if name.starts_with("Rar") {
            assert!(!row.encoder, "{name} must not expose an encoder");
        }
    }
}

#[test]
fn no_operation_is_reported_as_qualified() {
    let context = FacadeContext::create(matched_build()).expect("matched context");
    // capabilities() itself fails the call if the facade ever reports a nonzero
    // qualified_operations bitmask, so a successful call proves the literal 0.
    context.capabilities().expect("capabilities");
    assert_eq!(archive_engine::QUALIFIED_OPERATIONS, 0);
}

#[test]
fn capabilities_are_stable_across_repeated_enumerations() {
    // Each call allocates and releases its own arena; the owned snapshots must
    // be identical, which also shows nothing is left dangling between calls.
    let context = FacadeContext::create(matched_build()).expect("matched context");
    let first = context.capabilities().expect("first enumeration");
    let second = context.capabilities().expect("second enumeration");
    assert_eq!(first, second);
}

#[test]
fn many_contexts_and_results_release_cleanly() {
    // Leak check at the adapter level: every context and every result arena is
    // created and released repeatedly. A missing release would grow the
    // process's allocation set without bound; the raw-ABI leak accounting test
    // in facade_raw.rs checks the exact allocation balance.
    for _ in 0..16 {
        let context = FacadeContext::create(matched_build()).expect("matched context");
        for _ in 0..4 {
            let capabilities = context.capabilities().expect("capabilities");
            assert!(!capabilities.formats.is_empty());
        }
    }
}
