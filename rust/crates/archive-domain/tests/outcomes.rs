use archive_domain::*;

#[test]
fn failed_open_keeps_diagnostics_without_session_and_call_success_keeps_item_failure() {
    let diagnostic = Diagnostic {
        domain: NativeErrorDomain::HResult,
        code: 1,
        chain_position: Some(0),
        flags: 0,
        message: EngineText::new(vec![0xd800]),
        properties: vec![],
        operation: OperationKind::Open,
        redacted_path_context: None,
    };
    let outcome = OperationOutcome {
        status: CallStatus::NotRecognized,
        diagnostics: vec![diagnostic.clone()],
        open_diagnostics: vec![],
        items: vec![],
        warnings: vec![],
        completed: 0,
        skipped: 0,
        partial_effects: vec![],
    };
    let arc_error = OpenDiagnostic {
        chain_position: 1,
        there_is_tail: true,
        unexpected_end: true,
        ignore_tail: false,
        error_flags_defined: false,
        error_flags: 0xffff_ffff,
        warning_flags: 7,
        error_format_index: -1,
        tail_size: u64::MAX,
        error_message: EngineText::new(vec![0xd800]),
        warning_message: EngineText::new(vec![0xdc00]),
    };
    let chain = HandlerChain {
        position: 0,
        format_index: -1,
        format_name: EngineText::new(vec![90, 105, 112]),
        item_count: u64::MAX,
        offset: i64::MIN,
        properties: vec![Property {
            id: 99,
            source: PropertySource::Raw,
            value: PropertyValue::Bytes {
                original_type: 19,
                value: vec![255],
            },
        }],
        diagnostic: arc_error.clone(),
    };
    let failed = OpenOutcome {
        archive: None,
        chains: vec![chain.clone()],
        non_open_error: Some(arc_error.clone()),
        outcome,
    };
    assert!(failed.archive.is_none());
    assert_eq!(failed.chains, vec![chain]);
    assert_eq!(failed.non_open_error, Some(arc_error));
    assert_eq!(failed.outcome.diagnostics[0].code, 1);
    let item_failure = OperationOutcome {
        status: CallStatus::Succeeded,
        items: vec![ItemResult {
            entry: None,
            input: Some(NativePath::Unix(vec![0xff])),
            original_result: 3,
            category: ItemResultCategory::CrcError,
            diagnostics: vec![],
        }],
        ..failed.outcome
    };
    assert_eq!(item_failure.status, CallStatus::Succeeded);
    assert_eq!(item_failure.items[0].category, ItemResultCategory::CrcError);
    let capabilities = CapabilitySet {
        manifest: BuildManifest {
            abi_major: 1,
            revision: 1,
            target: BuildTarget::LinuxX64,
            pointer_bits: 64,
            little_endian: true,
            header_sha256: [0; 32],
            identity_sha256: [0; 32],
        },
        formats: vec![],
        codecs: vec![],
        hashers: vec![],
        qualified_features: vec![],
    };
    let archive = Archive {
        id: ArchiveId::new(1).unwrap(),
        generation: Generation::new(1).unwrap(),
        source: NativePath::Unix(vec![0xff]),
        chain: vec![],
        capabilities,
        properties: vec![],
        open_diagnostics: vec![],
        diagnostics: vec![diagnostic],
        state: ArchiveState::Open,
    };
    let snapshot = archive.clone();
    drop(archive);
    assert_eq!(snapshot.source, NativePath::Unix(vec![0xff]));
    assert!(snapshot.capabilities.qualified_features.is_empty());
}
