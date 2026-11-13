use archive_domain::*;

#[test]
fn requests_keep_retained_probe_defaults_and_operation_local_code_page() {
    let probe = ProbeOptions::default();
    assert_eq!(probe.format, FormatChoice::Auto);
    assert_eq!(
        probe.forced,
        ProbePositions {
            frontal: true,
            tail: true,
            mid: true
        }
    );
    assert_eq!(
        probe.main,
        ProbePositions {
            frontal: true,
            tail: false,
            mid: false
        }
    );
    assert_eq!(
        probe.wrong_extension,
        ProbePositions {
            frontal: false,
            tail: false,
            mid: false
        }
    );
    assert_eq!(probe.unknown_extension, probe.forced);
    assert!(probe.recursive && probe.can_return_archive);
    assert!(
        !probe.can_return_parser
            && !probe.is_hash_type
            && !probe.each_position
            && !probe.zeros_tail_allowed
    );
    assert_eq!(probe.max_start_offset, None);
    let request = OpenRequest {
        source: NativePath::Windows(vec![0xd800]),
        probe,
        types: vec![],
        excluded_formats: vec![],
        properties: vec![],
        code_page: CodePageChoice::Auto,
    };
    let explicit = OpenRequest {
        code_page: CodePageChoice::Explicit {
            handler: EngineText::new(vec![90, 105, 112]),
            code_page: 932,
        },
        ..request.clone()
    };
    assert_ne!(request.code_page, explicit.code_page);
    assert_eq!(request.source, explicit.source);
    assert_eq!(
        format!("{:?}", SecretText::new(vec![83, 69, 67, 82, 69, 84])),
        "SecretText([REDACTED])"
    );
    let secret = SecretText::new(vec![]);
    assert_eq!(secret.units(), &[]);
    let defined = PasswordReply::Defined(secret);
    assert!(matches!(defined, PasswordReply::Defined(_)));
    assert!(matches!(PasswordReply::Undefined, PasswordReply::Undefined));
    fn assert_port_is_object_safe(_: Option<&mut dyn ArchiveEngine>) {}
    assert_port_is_object_safe(None);
}
