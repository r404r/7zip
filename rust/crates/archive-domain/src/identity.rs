//! Worker-issued identities and checked, owned selections. Not native handles.
use std::num::NonZeroU64;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ContractError {
    InvalidRequest,
    StaleEntry,
    GenerationOverflow,
}

/// Allocated by the single process worker, never reused during that process.
/// Constructing this value does not register or authorize a session.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct ArchiveId(NonZeroU64);

impl ArchiveId {
    pub fn new(value: u64) -> Result<Self, ContractError> {
        NonZeroU64::new(value)
            .map(Self)
            .ok_or(ContractError::InvalidRequest)
    }
    pub fn value(self) -> u64 {
        self.0.get()
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Generation(NonZeroU64);

impl Generation {
    pub fn new(value: u64) -> Result<Self, ContractError> {
        NonZeroU64::new(value)
            .map(Self)
            .ok_or(ContractError::InvalidRequest)
    }
    pub fn value(self) -> u64 {
        self.0.get()
    }
    /// Failure leaves the number unchanged. The session must become unusable.
    pub fn advance(&mut self) -> Result<(), ContractError> {
        let next = self
            .value()
            .checked_add(1)
            .ok_or(ContractError::GenerationOverflow)?;
        *self = Self::new(next)?;
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct EntryId {
    pub archive_id: ArchiveId,
    pub generation: Generation,
    pub chain_position: u32,
    pub item_index: u32,
}

/// Worker-side identity state only. The future registry remains the authority;
/// user-created values and snapshot copies never authorize native access.
#[derive(Debug)]
pub struct SessionIdentity {
    id: ArchiveId,
    generation: Generation,
    active: bool,
}

impl SessionIdentity {
    pub fn new(id: ArchiveId, generation: Generation) -> Self {
        Self {
            id,
            generation,
            active: true,
        }
    }
    pub fn id(&self) -> ArchiveId {
        self.id
    }
    pub fn generation(&self) -> Generation {
        self.generation
    }
    pub fn validate(&self, entry: EntryId) -> Result<(), ContractError> {
        self.validate_epoch(entry.archive_id, entry.generation)
    }
    pub fn validate_epoch(
        &self,
        id: ArchiveId,
        generation: Generation,
    ) -> Result<(), ContractError> {
        if self.active && self.id == id && self.generation == generation {
            Ok(())
        } else {
            Err(ContractError::StaleEntry)
        }
    }
    /// Invoke BEFORE any invalidating attempt, including one that rolls back.
    /// Exhaustion permanently disables this session instead of wrapping.
    pub fn invalidate(&mut self) -> Result<(), ContractError> {
        self.validate_epoch(self.id, self.generation)?;
        if let Err(error) = self.generation.advance() {
            self.active = false;
            return Err(error);
        }
        Ok(())
    }
    pub fn close(&mut self) -> Result<(), ContractError> {
        self.validate_epoch(self.id, self.generation)?;
        self.active = false;
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct PageRange {
    first: u64,
    count: u64,
}
impl PageRange {
    pub fn new(first: u64, count: u64, item_count: u64) -> Result<Self, ContractError> {
        if first
            .checked_add(count)
            .is_some_and(|end| end <= item_count)
        {
            Ok(Self { first, count })
        } else {
            Err(ContractError::InvalidRequest)
        }
    }
    pub fn first(self) -> u64 {
        self.first
    }
    pub fn count(self) -> u64 {
        self.count
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
enum SelectionItems {
    All,
    Indices {
        display: Vec<EntryId>,
        engine: Vec<u32>,
    },
}

/// Private payload keeps construction checked; dispatch must revalidate the
/// epoch and bounds against the live worker registry, not a caller snapshot.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Selection {
    archive_id: ArchiveId,
    generation: Generation,
    chain_position: u32,
    items: SelectionItems,
}
impl Selection {
    pub fn all(session: &SessionIdentity, chain_position: u32) -> Result<Self, ContractError> {
        session.validate_epoch(session.id, session.generation)?;
        Ok(Self {
            archive_id: session.id,
            generation: session.generation,
            chain_position,
            items: SelectionItems::All,
        })
    }
    pub fn indices(
        session: &SessionIdentity,
        chain_position: u32,
        item_count: u64,
        display: Vec<EntryId>,
    ) -> Result<Self, ContractError> {
        let mut selected = Self::all(session, chain_position)?;
        let mut engine = Vec::with_capacity(display.len());
        for &entry in &display {
            session.validate(entry)?;
            if entry.chain_position != chain_position || u64::from(entry.item_index) >= item_count {
                return Err(ContractError::InvalidRequest);
            }
            engine.push(entry.item_index);
        }
        engine.sort_unstable();
        engine.dedup();
        selected.items = SelectionItems::Indices { display, engine };
        Ok(selected)
    }
    pub fn archive_id(&self) -> ArchiveId {
        self.archive_id
    }
    pub fn generation(&self) -> Generation {
        self.generation
    }
    pub fn chain_position(&self) -> u32 {
        self.chain_position
    }
    /// None means All, not a Rust-side all-items sentinel. Some(empty) selects none.
    pub fn engine_indices(&self) -> Option<&[u32]> {
        match &self.items {
            SelectionItems::All => None,
            SelectionItems::Indices { engine, .. } => Some(engine),
        }
    }
    pub fn display_entries(&self) -> &[EntryId] {
        match &self.items {
            SelectionItems::All => &[],
            SelectionItems::Indices { display, .. } => display,
        }
    }
}
