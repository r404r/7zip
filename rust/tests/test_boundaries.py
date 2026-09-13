"""Negative controls for the S1 dependency/pin gate (no production engine)."""
import copy
import importlib.util
from pathlib import Path
import tomllib
import unittest

SPEC = importlib.util.spec_from_file_location("boundaries", Path(__file__).with_name("check_boundaries.py"))
assert SPEC is not None and SPEC.loader is not None
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


class Boundaries(unittest.TestCase):
    def test_forbidden_native_source(self):
        for text in (
            "use std::os::windows::io::RawHandle;",
            "use std::{os::fd::RawFd};",
            "extern \"C\" { fn foreign(); }",
            "unsafe fn native() {}",
        ):
            with self.subTest(text=text), self.assertRaises(ValueError):
                GATE.check_source(text)

    @classmethod
    def setUpClass(cls):
        cls.metadata = GATE.metadata()

    def test_real_workspace(self):
        GATE.check_metadata(self.metadata)

    def test_forbidden_dependency_even_if_renamed_or_target_specific(self):
        for package in ("archive-domain", "archive-app"):
            for target in (None, "cfg(windows)"):
                for kind in (None, "dev", "build"):
                    with self.subTest(package=package, target=target, kind=kind):
                        data = copy.deepcopy(self.metadata)
                        node = next(p for p in data["packages"] if p["name"] == package)
                        node["dependencies"].append({"name": "windows", "rename": "harmless", "target": target, "kind": kind, "source": "registry+example"})
                        with self.assertRaises(ValueError):
                            GATE.check_metadata(data)

    def test_scoped_unsafe_is_confined_to_the_ffi_crate(self):
        # The FFI crate must relax the forbid; nobody else may.
        self.assertEqual(GATE.SCOPED_UNSAFE_CRATE, "archive-engine-sys")
        self.assertEqual(GATE.SCOPED_UNSAFE_LEVEL, "deny")
        self.assertNotIn(GATE.SCOPED_UNSAFE_CRATE, GATE.UNSAFE_FREE_CRATES)
        for name in ("archive-domain", "archive-app", "archive-cli", "archive-qt"):
            self.assertIn(name, GATE.UNSAFE_FREE_CRATES)
        # The real manifests must match that policy on disk.
        ffi = tomllib.loads(
            (GATE.ROOT / "crates/archive-engine-sys/Cargo.toml").read_text())
        self.assertEqual(ffi["lints"]["rust"]["unsafe_code"], "deny")
        self.assertNotIn("workspace", ffi.get("lints", {}))
        for name in GATE.ALLOWED:
            if name == GATE.SCOPED_UNSAFE_CRATE:
                continue
            with self.subTest(crate=name):
                package = tomllib.loads(
                    (GATE.ROOT / "crates" / name / "Cargo.toml").read_text())
                self.assertIs(package["lints"]["workspace"], True)
                self.assertNotIn("rust", package.get("lints", {}))

    def test_unsafe_outside_the_ffi_crate_is_rejected(self):
        # The safe adapter and the contract tests must stay unsafe-free; the
        # source scan is what enforces that, so prove it still bites.
        for text in (
            "pub fn adapt() { unsafe { native() } }",
            "unsafe impl Send for Handle {}",
            "unsafe extern \"C\" { safe fn peek() -> i32; }",
        ):
            with self.subTest(text=text), self.assertRaises(ValueError):
                GATE.check_source(text)

    def test_a_production_edge_cannot_hide_as_a_dev_dependency(self):
        # A dev-only edge is permitted exactly where declared, and only where
        # declared. Everything else must still be refused.
        self.assertEqual(GATE.DEV_ONLY_ALLOWED, {"archive-engine": {"archive-engine-sys"}})
        for package in ("archive-domain", "archive-app", "archive-cli", "archive-qt"):
            with self.subTest(package=package):
                data = copy.deepcopy(self.metadata)
                node = next(p for p in data["packages"] if p["name"] == package)
                node["dependencies"].append(
                    {"name": "archive-engine-sys", "kind": "dev", "source": None})
                with self.assertRaises(ValueError):
                    GATE.check_metadata(data)

    def test_a_dev_dependency_does_not_satisfy_a_library_edge(self):
        # Downgrading a required library edge to dev-only must not pass.
        data = copy.deepcopy(self.metadata)
        node = next(p for p in data["packages"] if p["name"] == "archive-engine")
        for dep in node["dependencies"]:
            if dep["name"] == "archive-engine-sys" and dep.get("kind") is None:
                dep["kind"] = "dev"
        with self.assertRaises(ValueError):
            GATE.check_metadata(data)

    def test_facade_feature_must_stay_off_by_default(self):
        for package, feature_map in GATE.FACADE_FEATURE_CRATES.items():
            with self.subTest(package=package):
                data = copy.deepcopy(self.metadata)
                node = next(p for p in data["packages"] if p["name"] == package)
                node.setdefault("features", {})["default"] = list(feature_map)
                with self.assertRaises(ValueError):
                    GATE.check_metadata(data)

    def test_facade_feature_cannot_appear_on_another_crate(self):
        for package in ("archive-domain", "archive-app", "archive-cli", "archive-qt"):
            with self.subTest(package=package):
                data = copy.deepcopy(self.metadata)
                node = next(p for p in data["packages"] if p["name"] == package)
                node.setdefault("features", {})["facade"] = []
                with self.assertRaises(ValueError):
                    GATE.check_metadata(data)

    def test_facade_feature_wiring_drift_is_rejected(self):
        # archive-engine's facade must forward to archive-engine-sys/facade, so
        # the adapter can never be enabled without the matching ABI layer.
        data = copy.deepcopy(self.metadata)
        node = next(p for p in data["packages"] if p["name"] == "archive-engine")
        node.setdefault("features", {})["facade"] = []
        with self.assertRaises(ValueError):
            GATE.check_metadata(data)

    def test_forbidden_internal_edge(self):
        data = copy.deepcopy(self.metadata)
        node = next(p for p in data["packages"] if p["name"] == "archive-domain")
        node["dependencies"].append({"name": "archive-engine-sys", "source": None})
        with self.assertRaises(ValueError):
            GATE.check_metadata(data)

    def test_external_package_and_default_gui_rejected(self):
        data = copy.deepcopy(self.metadata)
        data["packages"][0]["source"] = "registry+example"
        with self.assertRaises(ValueError):
            GATE.check_metadata(data)
        data = copy.deepcopy(self.metadata)
        data["workspace_default_members"] = data["workspace_members"]
        with self.assertRaises(ValueError):
            GATE.check_metadata(data)

    def test_native_build_script_rejected(self):
        data = copy.deepcopy(self.metadata)
        data["packages"][0]["targets"].append({"kind": ["custom-build"]})
        with self.assertRaises(ValueError):
            GATE.check_metadata(data)

    def test_pin_drift_rejected(self):
        data = copy.deepcopy(self.metadata)
        data["packages"][0]["rust_version"] = "1.97.0"
        with self.assertRaises(ValueError):
            GATE.check_metadata(data)


if __name__ == "__main__":
    unittest.main()
