# The vendored `Lang/` directory

7-Zip is fully translated, and the machinery for it is in the source tree:
`CPP/Common/Lang.cpp` parses the `;!@Lang2@!UTF-8!` format,
`CPP/7zip/UI/FileManager/LangUtils.cpp` loads `Lang\<id>.txt` from the
directory the executable is in, and Options → Language lists what it finds.
`-DZ7_LANG` is set for the File Manager, the GUI and the shell extension.

What the source tree does **not** contain is the language data. Those files
ship only with the official binary release. A build straight from upstream
sources is therefore English-only — not because anything is missing from the
code, but because the directory beside the executable is empty.

So this fork vendors them. `Lang/` holds the files from the official release
named in [`SOURCE.txt`](SOURCE.txt), unchanged, with the fork's own strings
appended to the four files listed below.

With `Lang/` in place, 7-Zip picks the system language by itself the first
time it runs (`OpenDefaultLang()`), and the user can change it in
Options → Language.

## Refreshing after an upstream release

```sh
python3 .github/scripts/lang_tool.py refresh --version <new version>
python3 .github/tests/lang_files_test.py .
```

`refresh` downloads the official installer, records its sha256 in
`SOURCE.txt`, unpacks `Lang/`, appends the fork block again and rewrites
`MANIFEST.sha256`. It needs a 7-Zip binary to unpack the installer
(`--seven <path>`, `$SEVENZIP`, `7zz`/`7z` on PATH, or the one this tree
builds). CI never runs it; CI only checks the result.

## What the check enforces

`.github/tests/lang_files_test.py` (CI step *Check the vendored language
files*) holds two things:

1. **Every file still parses** the way `Lang.cpp` parses it. A file that does
   not parse is dropped silently — that language simply disappears from the
   Options list.
2. **Below its fork block every file is byte for byte the official one**,
   against `MANIFEST.sha256`. The hash is taken with CR removed, because
   `ja.txt` is CRLF, the rest are LF, and a checkout with
   `core.autocrlf=true` would otherwise rewrite them. `Lang.cpp` strips CR
   before parsing too, so this is the same view of the file the program has.

## The fork's own strings

They live at **ids 30000 and up**, in a block **appended** to the end of the
file. Never insert one in the middle: an id that goes backwards makes
`Lang.cpp` reject the whole file, and an id inserted below the ones already
there shifts every following string onto the wrong control without any
complaint. Upstream ids stop at 7822 and dialog resource ids at 17600, so
30000+ will not collide with either.

| id | English | kind | defined in |
| --- | --- | --- | --- |
| 30000 | `Auto` | STRINGTABLE + language | `CPP/7zip/UI/GUI/ExtractRes.h` |
| 30001 | `Incorrect code page` | STRINGTABLE + language | `CPP/7zip/UI/GUI/ExtractRes.h` |
| 30002 | `Name code page:` | language only | `CPP/7zip/UI/GUI/ExtractDialogRes.h` |
| 30003 | `Use UTF-8 for file names` | language only | `CPP/7zip/UI/GUI/CompressDialogRes.h` |
| 30004 | `Name Code Page...` | language only | `CPP/7zip/UI/FileManager/resource.h` |
| 30005 | `Name Code Page` | STRINGTABLE + language | `CPP/7zip/UI/FileManager/resource.h` |
| 30006 | `Read the names of this archive as:` | STRINGTABLE + language | `CPP/7zip/UI/FileManager/resource.h` |

*STRINGTABLE + language*: read with `LangString(id)`, which falls back to the
`.rc` string table when the language file has no such id, so both have to
exist. *language only*: the English fallback is the text of the control or
menu item itself in the `.rc`.

The translations are in `STRINGS` in `.github/scripts/lang_tool.py`, which is
also where a new one is added. Currently translated: `en.ttt` (the reference
English file), `ja.txt`, `zh-cn.txt`, `zh-tw.txt`. The other 89 languages
fall back to English for these seven strings.

Deliberately **not** translated: the code page names in
`CPP/7zip/UI/Common/NameCodePageProps.h` (`936 (Chinese Simplified)` and the
literal `Auto` beside them) — `ParseNameCodePage()` reads those same literals
back — and the `7-Zip-fork` context menu caption, which is a name.

## License

The language files are part of 7-Zip and carry its license: LGPL 2.1 or
later, as in [`DOC/License.txt`](../../DOC/License.txt). Each file credits
its translators in the comment lines at the top; those lines are kept as they
came.
