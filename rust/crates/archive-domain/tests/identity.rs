use archive_domain::{
    ArchiveId, ContractError, EntryId, Generation, PageRange, Selection, SessionIdentity,
};

#[test]
fn identity_validation_and_overflow_never_wrap() {
    assert!(ArchiveId::new(0).is_err());
    assert!(Generation::new(0).is_err());
    let id = ArchiveId::new(u64::MAX).unwrap();
    let mut generation = Generation::new(u64::MAX).unwrap();
    assert_eq!(generation.advance(), Err(ContractError::GenerationOverflow));
    assert_eq!(generation.value(), u64::MAX);
    let mut session = SessionIdentity::new(id, Generation::new(1).unwrap());
    let entry = EntryId {
        archive_id: id,
        generation: session.generation(),
        chain_position: 2,
        item_index: u32::MAX,
    };
    assert_eq!(session.validate(entry), Ok(()));
    session.invalidate().unwrap();
    assert_eq!(session.validate(entry), Err(ContractError::StaleEntry));
    let fresh = EntryId {
        generation: session.generation(),
        ..entry
    };
    assert_eq!(session.validate(fresh), Ok(()));
    session.close().unwrap();
    assert_eq!(session.validate(fresh), Err(ContractError::StaleEntry));
    assert_eq!(session.close(), Err(ContractError::StaleEntry));
    let mut exhausted = SessionIdentity::new(id, generation);
    assert_eq!(
        exhausted.invalidate(),
        Err(ContractError::GenerationOverflow)
    );
    assert_eq!(
        exhausted.validate(EntryId {
            generation,
            ..entry
        }),
        Err(ContractError::StaleEntry)
    );
}

#[test]
fn pages_and_selection_preserve_bounds_and_user_order() {
    let id = ArchiveId::new(1).unwrap();
    let session = SessionIdentity::new(id, Generation::new(1).unwrap());
    let entry = EntryId {
        archive_id: id,
        generation: session.generation(),
        chain_position: 0,
        item_index: 9,
    };
    let selected = Selection::indices(
        &session,
        0,
        10,
        vec![
            entry,
            EntryId {
                item_index: 2,
                ..entry
            },
            entry,
        ],
    )
    .unwrap();
    assert_eq!(selected.engine_indices(), Some(&[2, 9][..]));
    assert_eq!(
        selected.display_entries(),
        &[
            entry,
            EntryId {
                item_index: 2,
                ..entry
            },
            entry
        ]
    );
    assert!(Selection::indices(&session, 0, 9, vec![entry]).is_err());
    assert!(Selection::indices(&session, 1, 10, vec![entry]).is_err());
    assert!(
        Selection::indices(
            &session,
            0,
            10,
            vec![EntryId {
                archive_id: ArchiveId::new(2).unwrap(),
                ..entry
            }]
        )
        .is_err()
    );
    assert!(PageRange::new(u64::MAX, 1, u64::MAX).is_err());
    assert!(PageRange::new(10, 1, 10).is_err());
    assert_eq!(PageRange::new(u64::MAX, 0, u64::MAX).unwrap().count(), 0);
}
