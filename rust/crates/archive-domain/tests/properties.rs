use archive_domain::*;

#[test]
fn property_projection_retains_absence_unknown_width_and_time_metadata() {
    let time = Timestamp {
        format: 1,
        units: TimestampUnits::Filetime100Nanoseconds,
        raw_low: u64::MAX,
        raw_high: 0xffff_ffff,
        precision: 7,
        defined: false,
        display_instant: None,
    };
    let properties = vec![
        Property {
            id: 0,
            source: PropertySource::Variant,
            value: PropertyValue::Empty { original_type: 0 },
        },
        Property {
            id: 1,
            source: PropertySource::Variant,
            value: PropertyValue::Unsupported {
                original_type: 0xbeef,
            },
        },
        Property {
            id: 2,
            source: PropertySource::Variant,
            value: PropertyValue::Unsigned {
                original_type: 21,
                value: UnsignedInteger::U64(u64::MAX),
            },
        },
        Property {
            id: 3,
            source: PropertySource::Variant,
            value: PropertyValue::Signed {
                original_type: 20,
                value: SignedInteger::I64(i64::MIN),
            },
        },
        Property {
            id: 4,
            source: PropertySource::Variant,
            value: PropertyValue::Timestamp {
                original_type: 64,
                value: time.clone(),
            },
        },
        Property {
            id: 4,
            source: PropertySource::Raw,
            value: PropertyValue::Bytes {
                original_type: 99,
                value: vec![0xff, 0],
            },
        },
    ];
    assert!(!properties.iter().any(|p| p.id == 5));
    assert_ne!(properties[0].value, properties[1].value);
    let owned = properties.clone();
    drop(properties);
    assert_eq!(
        owned[4].value,
        PropertyValue::Timestamp {
            original_type: 64,
            value: time
        }
    );
    assert_ne!(owned[4].source, owned[5].source);
    let entry = ArchiveEntry {
        id: EntryId {
            archive_id: ArchiveId::new(1).unwrap(),
            generation: Generation::new(1).unwrap(),
            chain_position: 0,
            item_index: u32::MAX,
        },
        name: EngineText::new(vec![0xd800]),
        display_text: "\u{fffd}".into(),
        raw_name: None,
        kind: EntryKind::Unknown,
        unpacked_size: Some(u64::MAX),
        packed_size: None,
        encrypted: None,
        timestamps: vec![owned[4].clone()],
        attributes: vec![],
        checksums: vec![],
        properties: owned,
    };
    assert_eq!(entry.clone().unpacked_size, Some(u64::MAX));
    assert_eq!(entry.packed_size, None);
    assert_eq!(entry.encrypted, None);
    assert_eq!(entry.name.units(), &[0xd800]);
}
