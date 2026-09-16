#!/usr/bin/env python3
"""Host-independent tests for the non-product MSVC ABI probe driver."""

import importlib.util
import pathlib
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE / "msvc-abi-convention-probe.py"


def load_probe():
    spec = importlib.util.spec_from_file_location("msvc_abi_probe", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ProbeDriverTests(unittest.TestCase):
    def setUp(self):
        self.probe = load_probe()

    def test_expected_symbols_cover_all_frozen_exports(self):
        self.assertEqual(
            set(self.probe.EXPORT_ARGUMENT_BYTES),
            {
                "archive_bridge_v1_handshake",
                "archive_bridge_v1_create_context",
                "archive_bridge_v1_destroy_context",
                "archive_bridge_v1_capabilities",
                "archive_bridge_v1_open",
                "archive_bridge_v1_entries",
                "archive_bridge_v1_close",
                "archive_bridge_v1_result_destroy",
            },
        )
        self.assertEqual(
            self.probe.expected_coff_symbol("x86", "archive_bridge_v1_close"),
            "_archive_bridge_v1_close",
        )
        self.assertEqual(
            self.probe.expected_coff_symbol("amd64", "archive_bridge_v1_close"),
            "archive_bridge_v1_close",
        )

    def test_frozen_input_validation_rejects_guard_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            frozen = root / "docs/ai-migration/qualification/archive_bridge_v1.h"
            production = root / "rust/bridge/archive_bridge_v1.h"
            makefile = root / "rust/bridge/makefile"
            frozen.parent.mkdir(parents=True)
            production.parent.mkdir(parents=True)
            frozen.write_bytes(b"same")
            production.write_bytes(b"same")
            makefile.write_text("PROG = archive_bridge_v1.dll\n!ERROR too late\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "fail-closed guard"):
                self.probe.validate_source_inputs(root, expected_hash=None)

    def test_mutations_are_isolated_and_named(self):
        source = self.probe.contract_header_mutation_fixture()
        mutations = self.probe.build_mutations(source)
        self.assertEqual(
            set(mutations),
            {"export_without_call", "callback_stdcall", "export_stdcall", "def_alias_evasion"},
        )
        for name, text in mutations.items():
            self.assertNotEqual(text, source, name)
            self.assertIn("ARCHIVE_BRIDGE_V1_H", text)

    def test_dumpbin_parsers_ignore_filename_and_undefined_symbols(self):
        exports = """Dump of file archive_bridge_v1_cc_probe.dll
          ordinal hint RVA      name
                1    0 00001000 archive_bridge_v1_handshake = _archive_bridge_v1_handshake
        """
        self.assertEqual(
            self.probe.pe_export_names(exports), {"archive_bridge_v1_handshake"}
        )
        symbols = """
        00A 00000000 UNDEF  notype ()    External     | _missing
        00B 00000000 SECT3  notype ()    External     | _defined
        """
        self.assertEqual(self.probe.raw_symbols(symbols), {"_defined"})


if __name__ == "__main__":
    unittest.main()
