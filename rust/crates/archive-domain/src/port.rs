//! Synchronous port and operation-scoped callback contracts. No scheduler,
//! callback transport, native engine implementation, or write operation is enabled.
use crate::*;
use std::fmt;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct TaskId(pub u64);
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct RequestId(pub u64);

/// Operation-private password units. No Clone/Display/serialization, redacted
/// Debug. Drop clears controlled storage best effort; compiler/allocator/engine
/// copies and process memory erasure are explicitly NOT guaranteed.
pub struct SecretText(Vec<u16>);
impl SecretText {
    pub fn new(units: Vec<u16>) -> Self {
        Self(units)
    }
    pub fn units(&self) -> &[u16] {
        &self.0
    }
}
impl fmt::Debug for SecretText {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str("SecretText([REDACTED])")
    }
}
impl Drop for SecretText {
    fn drop(&mut self) {
        self.0.fill(0);
    }
}

#[derive(Debug)]
pub enum PasswordReply {
    Undefined,
    Defined(SecretText),
}

/// Retained IFileExtractCallback.h NOverwriteAnswer vocabulary ONLY. B04 must
/// measure the allowed choices before a future adapter publishes this question.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum OverwriteAnswer {
    Yes,
    YesToAll,
    No,
    NoToAll,
    AutoRename,
    Cancel,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct OverwriteItem {
    pub name: EngineText,
    pub size: Option<u64>,
    pub time: Option<Timestamp>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Question {
    Password,
    Volume {
        name: EngineText,
    },
    Overwrite {
        existing: OverwriteItem,
        incoming: OverwriteItem,
        allowed: Vec<OverwriteAnswer>,
    },
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RequestReply {
    pub task_id: TaskId,
    pub archive_id: ArchiveId,
    pub generation: Generation,
    pub request_id: RequestId,
    pub question: Question,
}

#[derive(Debug)]
pub enum ReplyValue {
    Unavailable,
    Cancel,
    Password(PasswordReply),
    Volume(NativePath),
    Overwrite(OverwriteAnswer),
}

/// The future adapter accepts this once, with all IDs and question kind matched.
/// Stale/wrong/duplicate replies must fail, never default to a password/overwrite.
#[derive(Debug)]
pub struct InteractionReply {
    pub task_id: TaskId,
    pub archive_id: ArchiveId,
    pub generation: Generation,
    pub request_id: RequestId,
    pub value: ReplyValue,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum ProgressPhase {
    Opening,
    Scanning,
    Listing,
    Extracting,
    Testing,
    Creating,
    Finishing,
    EngineSpecific(u32),
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum CounterUnit {
    Files,
    InputBytes,
    OutputBytes,
    EngineSpecific(u32),
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ProgressEvent {
    pub task_id: TaskId,
    pub sequence: u64,
    pub phase: ProgressPhase,
    pub unit: CounterUnit,
    pub total: Option<u64>,
    pub completed: Option<u64>,
    pub item: Option<EntryId>,
}

pub trait Cancellation: Sync {
    fn is_cancelled(&self) -> bool;
}

/// Implementations synchronize concurrent codec notifications. Assign sequence
/// at publication; a total correction is not a protocol violation.
pub trait ProgressSink: Sync {
    fn publish(&self, event: ProgressEvent) -> Result<(), CallStatus>;
}

/// Delivery/cancellation must bypass the occupied engine command queue. Waiting
/// releases mailbox locks; replies must never reenter the engine. Cancellation
/// implementation must wake pending questions, not merely expose a sticky bit.
pub trait InteractionChannel: Sync {
    fn ask(
        &self,
        request: RequestReply,
        cancellation: &dyn Cancellation,
    ) -> Result<InteractionReply, CallStatus>;
}

/// Borrowed only for the synchronous call, including callback quiescence.
/// No Qt objects. Consumers are explicit: None never means a default reply.
pub struct OperationContext<'a> {
    pub task_id: TaskId,
    pub cancellation: &'a dyn Cancellation,
    pub progress: Option<&'a dyn ProgressSink>,
    pub interaction: Option<&'a dyn InteractionChannel>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct EntryPage {
    pub entries: Vec<ArchiveEntry>,
    pub outcome: OperationOutcome,
}

/// Called only on the single owning worker, serialized across ALL sessions.
/// No Send/Sync requirement: native adapter handles must be neither. &mut self
/// alone is not evidence of global serialization; the later composition enforces it.
///
/// Implementations validate live IDs/generations/chain/bounds before native access,
/// check all width conversions, copy snapshots before releasing native results,
/// and return only after callback quiescence. These declarations authorize no
/// features: S2a/B08 and the respective native behavior gates control exposure.
/// There are deliberately no fake-success or default operation implementations.
pub trait ArchiveEngine {
    fn capabilities(&mut self) -> Result<CapabilitySet, CallStatus>;
    fn open(&mut self, request: OpenRequest, context: OperationContext<'_>) -> OpenOutcome;
    fn entries(
        &mut self,
        archive: ArchiveId,
        generation: Generation,
        chain_position: u32,
        range: PageRange,
        context: OperationContext<'_>,
    ) -> EntryPage;
    fn extract(
        &mut self,
        selection: Selection,
        request: ExtractRequest,
        context: OperationContext<'_>,
    ) -> OperationOutcome;
    fn test(&mut self, selection: Selection, context: OperationContext<'_>) -> OperationOutcome;
    fn create(&mut self, request: CreateRequest, context: OperationContext<'_>) -> CreateOutcome;
    /// Later browsing only, not initial list parity or ABI revision 1.
    /// Advance epoch BEFORE invalidation; rollback also uses the advanced epoch.
    fn reopen(&mut self, request: NameDecodeRequest, context: OperationContext<'_>) -> OpenOutcome;
    /// Owner closes only after active operations finish; duplicate close is stale.
    fn close(&mut self, archive: ArchiveId) -> Result<(), CallStatus>;
}
