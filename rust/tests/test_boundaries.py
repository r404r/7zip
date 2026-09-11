"""Negative controls for the S1 dependency/pin gate (no production engine)."""
import copy
import importlib.util
from pathlib import Path
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
