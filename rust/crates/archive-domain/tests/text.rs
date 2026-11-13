use archive_domain::{EngineText, NativePath};

#[test]
fn lossless_text_is_not_a_native_path() {
    let units = vec![0xd800, 0x61, 0xdc00, 0];
    let text = EngineText::new(units.clone());
    assert_eq!(text.units(), units);
    assert_eq!(text.display_lossy(), "\u{fffd}a\u{fffd}\0");
    let windows = NativePath::Windows(units);
    let unix = NativePath::Unix(vec![0xff, b'a', 0]);
    assert_ne!(windows, unix);
    assert_eq!(unix.clone(), NativePath::Unix(vec![0xff, b'a', 0]));
}
