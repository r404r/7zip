#!/usr/bin/env python3
"""Host-independent tests for the non-product MSVC ABI probe driver."""

import importlib.util
import pathlib
import subprocess
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE / "msvc-abi-convention-probe.py"
WORKFLOW = HERE.parents[1] / ".github/workflows/rebuild-ci.yml"


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

    def test_generated_probe_header_is_exact_frozen_view_plus_exports(self):
        frozen = (
            HERE.parents[1] / "docs/ai-migration/qualification/archive_bridge_v1.h"
        ).read_text(encoding="utf-8")
        generated = self.probe.generated_probe_header(frozen)
        self.probe.validate_generated_probe_header(frozen, generated)
        self.assertTrue(generated.startswith(self.probe.GENERATED_HEADER_PREAMBLE))
        self.assertEqual(generated.count("__declspec(dllexport)"), 8)
        for name in self.probe.EXPORT_ARGUMENT_BYTES:
            self.assertIn(
                "__declspec(dllexport) int32_t ARCHIVE_BRIDGE_V1_CALL " + name + "(",
                generated,
            )

    def test_generated_probe_header_validator_rejects_drift(self):
        frozen = (
            HERE.parents[1] / "docs/ai-migration/qualification/archive_bridge_v1.h"
        ).read_text(encoding="utf-8")
        generated = self.probe.generated_probe_header(frozen)
        mutations = (
            generated.replace(
                "const archive_bridge_v1_info *expected", "const void *expected", 1
            ),
            generated.replace(
                "__declspec(dllexport) int32_t ARCHIVE_BRIDGE_V1_CALL "
                "archive_bridge_v1_handshake(",
                "int32_t ARCHIVE_BRIDGE_V1_CALL archive_bridge_v1_handshake(",
                1,
            ),
            generated.replace(
                "__declspec(dllexport) int32_t ARCHIVE_BRIDGE_V1_CALL "
                "archive_bridge_v1_close(",
                "__declspec(dllexport) int32_t archive_bridge_v1_close(",
                1,
            ),
        )
        for mutated in mutations:
            self.assertNotEqual(mutated, generated)
            with self.assertRaises(RuntimeError):
                self.probe.validate_generated_probe_header(frozen, mutated)

    def test_generated_sources_mark_all_entry_points_cdecl(self):
        self.assertIn("int __cdecl main(void)", self.probe.typecheck_source())
        self.assertIn("int __cdecl main()", self.probe.cpp_typecheck_source())
        self.assertIn("int __cdecl main(int argc", self.probe.c_caller_source())

    def test_probe_callback_helper_initializes_only_observed_fields(self):
        source = self.probe.definitions_source()
        helper = source[source.index("cc_probe_invoke_callbacks") :]
        self.assertNotIn("= {0}", helper)
        self.assertIn("progress.counter_kind = 0x7011", helper)
        self.assertIn("question.kind = 0x7022", helper)
        self.assertIn("reply.kind = 0", helper)

    def test_rtc_handler_calls_exit_process_indirectly(self):
        source = self.probe.rtc_handler_source(85)
        self.assertIn("typedef void (WINAPI *exit_process_fn)(UINT);", source)
        self.assertIn("exit_process_fn exit_process = ExitProcess;", source)
        self.assertIn("exit_process(85); return 0;", source)
        self.assertNotIn("ExitProcess(85)", source)

    def test_export_decorated_header_is_isolated_to_probe_definition(self):
        frozen = (
            HERE.parents[1] / "docs/ai-migration/qualification/archive_bridge_v1.h"
        ).read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as temp:
            work = pathlib.Path(temp)
            generated = self.probe.write_sources(work, frozen)
            self.assertEqual(
                (work / "archive_bridge_v1.h").read_text(encoding="utf-8"), frozen
            )
            self.assertEqual(
                (work / "archive_bridge_v1_probe_exports.h").read_text(
                    encoding="utf-8"
                ),
                generated,
            )
            self.assertIn(
                '#include "archive_bridge_v1_probe_exports.h"',
                (work / "probe.cpp").read_text(encoding="utf-8"),
            )
            self.assertIn(
                '#include "archive_bridge_v1.h"',
                (work / "caller.c").read_text(encoding="utf-8"),
            )

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

    def test_compile_diagnostic_sweep_runs_every_translation_unit_before_failing(self):
        class FakeRunner:
            def __init__(self, evidence):
                self.evidence = evidence
                self.names = []
                self.commands = []

            def run(self, name, command, *, cwd, expected=0):
                del cwd, expected
                self.names.append(name)
                output = {
                    "diagnostic-current-source": "current.cpp(1): error C2001: first\n",
                    "diagnostic-probe": "probe.cpp(2): warning C4312: second\n",
                }.get(name, "")
                return_code = 2 if output else 0
                self.commands.append(
                    {"name": name, "command": subprocess.list2cmdline(command), "exit_code": return_code}
                )
                return subprocess.CompletedProcess([], return_code, output)

        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp) / "root"
            output = pathlib.Path(temp) / "output"
            evidence = output / "evidence" / "amd64"
            evidence.mkdir(parents=True)
            frozen = root / "docs/ai-migration/qualification/archive_bridge_v1.h"
            frozen.parent.mkdir(parents=True)
            frozen.write_text(
                (HERE.parents[1] / "docs/ai-migration/qualification/archive_bridge_v1.h")
                .read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            runner = FakeRunner(evidence)

            with self.assertRaisesRegex(
                RuntimeError,
                "diagnostic-current-source.*C2001.*diagnostic-probe.*C4312",
            ):
                self.probe.compile_diagnostic_sweep(root, output, "amd64", runner)

            self.assertEqual(
                runner.names,
                [
                    "diagnostic-current-source",
                    "diagnostic-typecheck-c",
                    "diagnostic-typecheck-cpp",
                    "diagnostic-probe",
                    "diagnostic-c-caller",
                ],
            )
            summary = (evidence / "compile-diagnostic-summary.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn("diagnostic-current-source: exit_code=2; diagnostics=C2001", summary)
            self.assertIn("diagnostic-probe: exit_code=2; diagnostics=C4312", summary)
            commands = (evidence / "compile-diagnostic-commands.json").read_text(
                encoding="utf-8"
            )
            self.assertIn('"architecture": "amd64"', commands)
            self.assertIn('"name": "diagnostic-current-source"', commands)
            self.assertIn('"name": "diagnostic-c-caller"', commands)

    def test_runtime_negative_diagnostic_sweep_collects_every_translation_unit(self):
        class FakeRunner:
            def __init__(self, evidence):
                self.evidence = evidence
                self.names = []

            def run(self, name, command, *, cwd, expected=0):
                del command, cwd, expected
                self.names.append(name)
                output = {
                    "runtime-diagnostic-fastcall-caller": "fastcall-caller.c(4): warning C4702\n",
                    "runtime-diagnostic-callback-dll": "callback-dll.c(8): error C2001\n",
                }.get(name, "")
                return subprocess.CompletedProcess([], 2 if output else 0, output)

        with tempfile.TemporaryDirectory() as temp:
            base = pathlib.Path(temp) / "work"
            evidence = pathlib.Path(temp) / "evidence"
            base.mkdir()
            evidence.mkdir()
            runner = FakeRunner(evidence)

            with self.assertRaisesRegex(RuntimeError, "C4702.*C2001"):
                self.probe.runtime_negative_compile_diagnostic_sweep(base, runner)

            self.assertEqual(
                runner.names,
                [
                    "runtime-diagnostic-fastcall-dll",
                    "runtime-diagnostic-fastcall-caller",
                    "runtime-diagnostic-stdcall-dll",
                    "runtime-diagnostic-stdcall-caller",
                    "runtime-diagnostic-callback-dll",
                    "runtime-diagnostic-callback-caller",
                ],
            )
            summary = (evidence / "runtime-negative-compile-diagnostic-summary.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn("runtime-diagnostic-fastcall-caller: exit_code=2; diagnostics=C4702", summary)
            self.assertIn("runtime-diagnostic-callback-dll: exit_code=2; diagnostics=C2001", summary)

    def test_workflow_collects_both_architecture_sweeps_before_failing(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        amd64 = workflow.index("--diagnostics-only amd64")
        x86 = workflow.index("--diagnostics-only x86")
        aggregate = workflow.index("MSVC compile diagnostic sweeps failed after both architectures")
        formal_amd64 = workflow.index("--arch amd64", aggregate)
        native_errors_disabled = workflow.index(
            "$PSNativeCommandUseErrorActionPreference = $false"
        )
        native_errors_restored = workflow.index(
            "$PSNativeCommandUseErrorActionPreference = $previousNativeErrorPreference"
        )

        self.assertLess(native_errors_disabled, amd64)
        self.assertLess(amd64, x86)
        self.assertLess(x86, native_errors_restored)
        self.assertLess(native_errors_restored, aggregate)
        self.assertLess(x86, aggregate)
        self.assertLess(aggregate, formal_amd64)
        between_sweeps = workflow[amd64:x86]
        self.assertNotIn("exit $LASTEXITCODE", between_sweeps)

    def test_workflow_restores_pristine_environment_before_each_vcvars_import(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        snapshot = workflow.index("$pristineProcessEnvironment = @{}")
        restore_function = workflow.index("function Restore-PristineProcessEnvironment")
        import_function = workflow.index("function Import-VcVars")
        restore_call = workflow.index("Restore-PristineProcessEnvironment", import_function)
        vcvars_call = workflow.index('cmd /d /s /c "`"$vcvars`" $target', import_function)

        self.assertLess(snapshot, restore_function)
        self.assertLess(restore_function, import_function)
        self.assertLess(import_function, restore_call)
        self.assertLess(restore_call, vcvars_call)
        self.assertIn(
            "SetEnvironmentVariable([string]$name, $null, 'Process')",
            workflow[restore_function:import_function],
        )


if __name__ == "__main__":
    unittest.main()
