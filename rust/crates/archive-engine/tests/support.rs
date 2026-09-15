//! Test support: read the frozen Q1 reference and the matched build identity.
//!
//! Deliberately dependency-free. The workspace has no external crates
//! (`rust/tests/check_boundaries.py` enforces that), so this module contains a
//! small purpose-built JSON reader instead of pulling in serde. It reads the
//! reviewed oracle files directly rather than through a generated intermediate.
//!
//! Nothing here ever writes to a golden or reference file. If the
//! implementation disagrees with the frozen reference, the test fails and the
//! implementation gets investigated — the reference is not edited to pass.
#![cfg(feature = "facade")]
#![allow(dead_code)]

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use archive_engine::MatchedBuild;

// ---------------------------------------------------------------------------
// Minimal JSON value + parser
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, PartialEq)]
pub enum Json {
    Null,
    Bool(bool),
    Number(f64),
    String(String),
    Array(Vec<Json>),
    Object(BTreeMap<String, Json>),
}

impl Json {
    pub fn get(&self, key: &str) -> &Json {
        match self {
            Json::Object(map) => map
                .get(key)
                .unwrap_or_else(|| panic!("missing JSON key {key}")),
            other => panic!("expected an object to index with {key}, found {other:?}"),
        }
    }

    pub fn array(&self) -> &[Json] {
        match self {
            Json::Array(items) => items,
            other => panic!("expected a JSON array, found {other:?}"),
        }
    }

    pub fn string(&self) -> &str {
        match self {
            Json::String(text) => text,
            other => panic!("expected a JSON string, found {other:?}"),
        }
    }

    pub fn u64(&self) -> u64 {
        match self {
            Json::Number(value) => {
                assert!(
                    value.fract() == 0.0 && *value >= 0.0,
                    "expected a non-negative integer, found {value}"
                );
                *value as u64
            }
            other => panic!("expected a JSON number, found {other:?}"),
        }
    }

    pub fn u32(&self) -> u32 {
        u32::try_from(self.u64()).expect("value fits in u32")
    }
}

struct Parser<'a> {
    bytes: &'a [u8],
    at: usize,
}

impl<'a> Parser<'a> {
    fn new(text: &'a str) -> Self {
        Self {
            bytes: text.as_bytes(),
            at: 0,
        }
    }

    fn skip_whitespace(&mut self) {
        while self.at < self.bytes.len() && self.bytes[self.at].is_ascii_whitespace() {
            self.at += 1;
        }
    }

    fn peek(&self) -> u8 {
        assert!(self.at < self.bytes.len(), "unexpected end of JSON");
        self.bytes[self.at]
    }

    fn expect(&mut self, byte: u8) {
        assert_eq!(
            self.peek(),
            byte,
            "expected {:?} at {}",
            byte as char,
            self.at
        );
        self.at += 1;
    }

    fn literal(&mut self, text: &str) {
        assert!(
            self.bytes[self.at..].starts_with(text.as_bytes()),
            "expected literal {text} at {}",
            self.at
        );
        self.at += text.len();
    }

    fn value(&mut self) -> Json {
        self.skip_whitespace();
        match self.peek() {
            b'{' => self.object(),
            b'[' => self.array(),
            b'"' => Json::String(self.string()),
            b't' => {
                self.literal("true");
                Json::Bool(true)
            }
            b'f' => {
                self.literal("false");
                Json::Bool(false)
            }
            b'n' => {
                self.literal("null");
                Json::Null
            }
            _ => self.number(),
        }
    }

    fn object(&mut self) -> Json {
        self.expect(b'{');
        let mut map = BTreeMap::new();
        self.skip_whitespace();
        if self.peek() == b'}' {
            self.at += 1;
            return Json::Object(map);
        }
        loop {
            self.skip_whitespace();
            let key = self.string();
            self.skip_whitespace();
            self.expect(b':');
            let value = self.value();
            map.insert(key, value);
            self.skip_whitespace();
            match self.peek() {
                b',' => self.at += 1,
                b'}' => {
                    self.at += 1;
                    return Json::Object(map);
                }
                other => panic!("unexpected {:?} in object at {}", other as char, self.at),
            }
        }
    }

    fn array(&mut self) -> Json {
        self.expect(b'[');
        let mut items = Vec::new();
        self.skip_whitespace();
        if self.peek() == b']' {
            self.at += 1;
            return Json::Array(items);
        }
        loop {
            items.push(self.value());
            self.skip_whitespace();
            match self.peek() {
                b',' => self.at += 1,
                b']' => {
                    self.at += 1;
                    return Json::Array(items);
                }
                other => panic!("unexpected {:?} in array at {}", other as char, self.at),
            }
        }
    }

    fn string(&mut self) -> String {
        self.expect(b'"');
        let mut out = String::new();
        loop {
            let byte = self.peek();
            self.at += 1;
            match byte {
                b'"' => return out,
                b'\\' => {
                    let escape = self.peek();
                    self.at += 1;
                    match escape {
                        b'"' => out.push('"'),
                        b'\\' => out.push('\\'),
                        b'/' => out.push('/'),
                        b'b' => out.push('\u{8}'),
                        b'f' => out.push('\u{c}'),
                        b'n' => out.push('\n'),
                        b'r' => out.push('\r'),
                        b't' => out.push('\t'),
                        b'u' => {
                            let hex = std::str::from_utf8(&self.bytes[self.at..self.at + 4])
                                .expect("valid \\u escape");
                            self.at += 4;
                            let unit = u16::from_str_radix(hex, 16).expect("hex escape");
                            // The reviewed reference files are ASCII; a
                            // surrogate would mean the oracle changed shape.
                            out.push(char::from_u32(unit as u32).expect("BMP scalar"));
                        }
                        other => panic!("unsupported escape \\{}", other as char),
                    }
                }
                _ => {
                    // Multi-byte UTF-8 passes through byte by byte.
                    let start = self.at - 1;
                    let mut end = self.at;
                    while end < self.bytes.len() && self.bytes[end] & 0xC0 == 0x80 {
                        end += 1;
                    }
                    out.push_str(std::str::from_utf8(&self.bytes[start..end]).expect("utf-8"));
                    self.at = end;
                }
            }
        }
    }

    fn number(&mut self) -> Json {
        let start = self.at;
        while self.at < self.bytes.len()
            && matches!(
                self.bytes[self.at],
                b'-' | b'+' | b'.' | b'e' | b'E' | b'0'..=b'9'
            )
        {
            self.at += 1;
        }
        let text = std::str::from_utf8(&self.bytes[start..self.at]).expect("utf-8 number");
        Json::Number(text.parse().expect("parsable number"))
    }
}

pub fn parse_json(text: &str) -> Json {
    let mut parser = Parser::new(text);
    let value = parser.value();
    parser.skip_whitespace();
    assert_eq!(parser.at, parser.bytes.len(), "trailing JSON content");
    value
}

// ---------------------------------------------------------------------------
// Repository and environment locations
// ---------------------------------------------------------------------------

/// Repository root, derived from this crate's manifest directory.
pub fn repo_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .ancestors()
        .nth(3)
        .expect("repository root above rust/crates/archive-engine")
        .to_path_buf()
}

/// The development facade manifest produced by `rust/bridge/build-manifest.py`.
///
/// Required: without it there is no matched build identity, and the tests must
/// not invent one.
pub fn dev_manifest() -> Json {
    let path = std::env::var("ARCHIVE_BRIDGE_V1_DEV_MANIFEST").expect(
        "set ARCHIVE_BRIDGE_V1_DEV_MANIFEST to the facade-build-dev.json emitted by \
         rust/bridge/build-manifest.py; these tests refuse to guess a build identity",
    );
    let text = std::fs::read_to_string(&path)
        .unwrap_or_else(|error| panic!("cannot read {path}: {error}"));
    parse_json(&text)
}

fn digest_from_hex(hex: &str) -> [u8; 32] {
    assert_eq!(hex.len(), 64, "expected a 64-character SHA-256 hex digest");
    let mut out = [0u8; 32];
    for (index, slot) in out.iter_mut().enumerate() {
        *slot = u8::from_str_radix(&hex[index * 2..index * 2 + 2], 16).expect("hex digest");
    }
    out
}

/// Numeric target code for the system/machine the frozen manifest records.
fn target_code(target: &str) -> u32 {
    match target {
        "x86_64-unknown-linux-gnu" => 1,
        "x86_64-pc-windows-msvc" => 2,
        "aarch64-apple-darwin" => 3,
        other => panic!("unsupported target {other}"),
    }
}

/// The exact matched-build identity the loaded facade must agree with.
pub fn matched_build() -> MatchedBuild {
    let manifest = dev_manifest();
    let identity = manifest.get("development_build").get("identity");
    MatchedBuild::new(
        target_code(identity.get("target").string()),
        digest_from_hex(identity.get("header_sha256").string()),
        digest_from_hex(
            manifest
                .get("development_build")
                .get("identity_sha256")
                .string(),
        ),
    )
}

/// The same matched identity as the raw `archive_bridge_v1_info` record the
/// lifetime probes need.
pub fn matched_info() -> archive_engine_sys::ArchiveBridgeInfo {
    let matched = matched_build();
    archive_engine_sys::expected_info(
        matched.target,
        matched.header_sha256,
        matched.build_manifest_sha256,
    )
}

/// One individually mutated copy of the matched identity per comparable field.
///
/// Each entry differs from the matched identity in exactly one field, so a
/// MISMATCH proves that field is actually compared.
pub fn mutated_builds() -> Vec<(&'static str, MatchedBuild)> {
    let matched = matched_build();
    let mut mutations = Vec::new();

    let mut target = matched;
    // Any other declared target code; 1/2/3 are the only valid values.
    target.target = if matched.target == 1 { 3 } else { 1 };
    mutations.push(("target", target));

    let mut header = matched;
    header.header_sha256[0] ^= 0x01;
    mutations.push(("header_sha256 first byte", header));

    let mut header_last = matched;
    header_last.header_sha256[31] ^= 0x80;
    mutations.push(("header_sha256 last byte", header_last));

    let mut build = matched;
    build.build_manifest_sha256[0] ^= 0x01;
    mutations.push(("build_manifest_sha256 first byte", build));

    let mut build_last = matched;
    build_last.build_manifest_sha256[31] ^= 0x80;
    mutations.push(("build_manifest_sha256 last byte", build_last));

    mutations
}

// ---------------------------------------------------------------------------
// Frozen Q1 capability reference
// ---------------------------------------------------------------------------

#[derive(Clone, Debug)]
pub struct FormatReference {
    pub name: String,
    pub registration_id: u32,
    pub flags: u32,
    /// Raw registered `CArcInfo::TimeFlags`, observed through the retained
    /// library's own exports by the Q1 format observer.
    pub raw_time_flags: u32,
    /// Effective `CCodecs::Formats[i].TimeFlags` on the built-in `LoadCodecs`
    /// path, which is what a facade built without external codec loading must
    /// report.
    ///
    /// `abi-v1.md` records the raw and effective values separately on purpose:
    /// the built-in path leaves `TimeFlags` at the `CArcInfoEx` constructor
    /// default, while the dynamic library path obtains the exported property.
    /// That retained behaviour must be preserved, not repaired.
    pub effective_time_flags: u32,
    pub has_writer: bool,
}

pub struct MethodReference {
    pub name: String,
    pub method_id: u64,
    pub encoder: bool,
    pub decoder: bool,
    pub is_filter: bool,
    pub digest_size: u32,
}

pub struct RegistryReference {
    pub formats: Vec<FormatReference>,
    pub codecs: Vec<MethodReference>,
    pub hashers: Vec<MethodReference>,
}

/// Reads the reviewed Q1 `engine-build.json` reference for THIS host.
///
/// `format_registry` supplies the numeric registration identities observed
/// through the retained library's own exports; the coordinator-added `Hash`
/// row is added with the literal 256 because the retained library never
/// registered a `CArcInfo` slot for it. `standalone` supplies the codec and
/// hasher rows and the `Hash` row's effective flags.
pub fn expected_registry() -> RegistryReference {
    let path = std::env::var_os("ARCHIVE_BRIDGE_V1_FROZEN_REFERENCE")
        .map(PathBuf::from)
        .unwrap_or_else(|| repo_root().join("docs/ai-migration/qualification/engine-build.json"));
    let text = std::fs::read_to_string(&path)
        .unwrap_or_else(|error| panic!("cannot read {}: {error}", path.display()));
    let manifest = parse_json(&text);
    // The reference must still be the reviewed retained-native-reference; these
    // tests never consume or produce a "qualified" manifest.
    assert_eq!(manifest.get("status").string(), "retained-native-reference");
    let system = host_system();
    let build = manifest
        .get("builds")
        .array()
        .iter()
        .find(|entry| entry.get("system").string() == system)
        .unwrap_or_else(|| panic!("no frozen Q1 build for {system}"));

    let numeric_formats: BTreeMap<String, FormatReference> = build
        .get("format_registry")
        .array()
        .iter()
        .map(|row| FormatReference {
            name: row.get("name").string().to_string(),
            registration_id: row.get("registration_id").u32(),
            flags: row.get("flags").u32(),
            raw_time_flags: row.get("time_flags").u32(),
            // The retained CArcInfoEx constructor default (LoadCodecs.h:216-218)
            // is 0, and CCodecs::Load() on the built-in path never overwrites
            // it — it copies arc.Flags but not arc.TimeFlags
            // (LoadCodecs.cpp:813-816). That default is the effective value.
            effective_time_flags: 0,
            has_writer: row.get("writer").u32() == 1,
        })
        .map(|row| (row.name.clone(), row))
        .collect();

    // CCodecs exposes the loaded table in retained name-sort order. Join the
    // numeric registration observer by name, but preserve this independent
    // loaded order so a runtime reorder cannot compare equal to itself.
    let formats: Vec<FormatReference> = build
        .get("loaded")
        .get("formats")
        .array()
        .iter()
        .map(|row| {
            let name = row.get("name").string();
            if name == "Hash" {
                return FormatReference {
                    name: "Hash".to_string(),
                    registration_id: 256,
                    flags: 12353,
                    raw_time_flags: 0,
                    effective_time_flags: 0,
                    has_writer: true,
                };
            }
            numeric_formats
                .get(name)
                .unwrap_or_else(|| panic!("loaded format {name} has no registration row"))
                .clone()
        })
        .collect();

    let standalone = build.get("standalone");
    let codecs = standalone
        .get("codecs")
        .array()
        .iter()
        .map(|row| {
            let flags = row.get("flags_text").string();
            MethodReference {
                name: row.get("name").string().to_string(),
                method_id: row.get("method_id").u64(),
                encoder: flags.contains('E'),
                decoder: flags.contains('D'),
                is_filter: flags.contains('F'),
                digest_size: 0,
            }
        })
        .collect();
    let hashers = standalone
        .get("hashers")
        .array()
        .iter()
        .map(|row| MethodReference {
            name: row.get("name").string().to_string(),
            method_id: row.get("method_id").u64(),
            encoder: false,
            decoder: false,
            is_filter: false,
            digest_size: row.get("digest_size").u32(),
        })
        .collect();

    RegistryReference {
        formats,
        codecs,
        hashers,
    }
}

fn host_system() -> &'static str {
    if cfg!(target_os = "linux") {
        "Linux"
    } else if cfg!(target_os = "windows") {
        "Windows"
    } else if cfg!(target_os = "macos") {
        "Darwin"
    } else {
        panic!("unsupported host system")
    }
}

/// UTF-16 code units for an ASCII reference name.
pub fn utf16(text: &str) -> Vec<u16> {
    text.encode_utf16().collect()
}
