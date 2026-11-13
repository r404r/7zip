//! Typed requests, not feature authorization. Adapters must reject unqualified
//! options before effects. No command line, filesystem policy or ABI is implemented.
use crate::{ArchiveId, EngineText, Generation, NativePath, PropertyValue};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum FormatChoice {
    Auto,
    /// Local to the matched CCodecs runtime; validated before conversion to i32.
    Index(u32),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct ProbePositions {
    pub frontal: bool,
    pub tail: bool,
    pub mid: bool,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ProbeOptions {
    pub format: FormatChoice,
    pub forced: ProbePositions,
    pub main: ProbePositions,
    pub wrong_extension: ProbePositions,
    pub unknown_extension: ProbePositions,
    pub recursive: bool,
    pub can_return_archive: bool,
    pub can_return_parser: bool,
    pub is_hash_type: bool,
    pub each_position: bool,
    pub zeros_tail_allowed: bool,
    pub max_start_offset: Option<u64>,
}

impl Default for ProbeOptions {
    /// CPP/7zip/UI/Common/OpenArchive.h COpenType, frozen by Q1 ABI v1.
    fn default() -> Self {
        Self {
            format: FormatChoice::Auto,
            forced: ProbePositions {
                frontal: true,
                tail: true,
                mid: true,
            },
            main: ProbePositions {
                frontal: true,
                tail: false,
                mid: false,
            },
            wrong_extension: ProbePositions {
                frontal: false,
                tail: false,
                mid: false,
            },
            unknown_extension: ProbePositions {
                frontal: true,
                tail: true,
                mid: true,
            },
            recursive: true,
            can_return_archive: true,
            can_return_parser: false,
            is_hash_type: false,
            each_position: false,
            zeros_tail_allowed: false,
            max_start_offset: None,
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ScopedProperty {
    pub scope: EngineText,
    pub name: EngineText,
    pub value: PropertyValue,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum CodePageChoice {
    /// Omit the operation-local override, not an assumed ACP.
    Auto,
    Explicit {
        handler: EngineText,
        code_page: u32,
    },
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct OpenRequest {
    pub source: NativePath,
    pub probe: ProbeOptions,
    pub types: Vec<ProbeOptions>,
    pub excluded_formats: Vec<u32>,
    /// Preserve order, explicit-option precedence and empty handler reset.
    /// Passwords MUST NOT be transported through general properties.
    pub properties: Vec<ScopedProperty>,
    pub code_page: CodePageChoice,
}

/// Vocabulary from ExtractMode.h, not measured/application-enabled options.
/// No Default is supplied; B04 and S4 must qualify every exposed choice.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum OverwriteMode {
    Ask,
    Overwrite,
    Skip,
    Rename,
    RenameExisting,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ExtractPathMode {
    FullPaths,
    CurrentPaths,
    NoPaths,
    AbsolutePaths,
    NoPathsAlternateStreams,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ExtractRequest {
    pub destination: NativePath,
    pub path_mode: ExtractPathMode,
    pub overwrite: OverwriteMode,
    pub properties: Vec<ScopedProperty>,
    pub code_page: CodePageChoice,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Recursion {
    Recursive,
    WildcardOnly,
    NonRecursive,
}

/// Retained scanner inputs, not a second Rust scanner or path sanitizer.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct InputScanPolicy {
    pub roots: Vec<NativePath>,
    pub recursion: Recursion,
    pub wildcard_parsing: bool,
    pub preserve_access_time: bool,
    pub open_share_for_write: bool,
    pub stop_after_open_error: bool,
    pub store_symlinks: Option<bool>,
    pub store_hardlinks: Option<bool>,
    pub store_alternate_streams: Option<bool>,
    pub store_security: Option<bool>,
}

/// CUpdateOptions::ArcNameMode vocabulary. No update/delete action set is exposed.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ArchiveNameMode {
    Smart,
    Exact,
    AddExtension,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct DestinationPolicy {
    pub path: NativePath,
    pub name_mode: ArchiveNameMode,
    pub working_directory: Option<NativePath>,
    pub volume_sizes: Vec<u64>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MethodChoice {
    pub id: u64,
    pub properties: Vec<ScopedProperty>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct CreateRequest {
    pub format: FormatChoice,
    pub method: Option<MethodChoice>,
    pub properties: Vec<ScopedProperty>,
    pub scan: InputScanPolicy,
    pub destination: DestinationPolicy,
}

/// Later browsing only: CanReOpen eligibility/rollback remains in the engine.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct NameDecodeRequest {
    pub archive_id: ArchiveId,
    pub generation: Generation,
    pub code_page: CodePageChoice,
}
