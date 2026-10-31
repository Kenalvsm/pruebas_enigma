import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("quality", Path(__file__).with_name("quality.py"))
quality = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quality)

class Gates(unittest.TestCase):
    def call(self, stage, branch, refs=""):
        with patch.object(sys, "argv", ["quality", stage, "--branch", branch]), patch.object(sys, "stdin", io.StringIO(refs)), patch.object(quality, "suite") as suite:
            quality.main()
            return suite.call_args.args[0]

    def test_suffixes(self):
        for platform in quality.PLATFORMS:
            self.assertEqual(quality.branch_platform("feature/work/" + platform), platform)

    def test_invalid_branch(self):
        for branch in ("feature/work", "python", "", "feature/PYTHON"):
            with self.assertRaises(ValueError): quality.branch_platform(branch)

    def test_protected_commit(self):
        for branch in ("main", "develop"):
            with self.assertRaises(ValueError): self.call("pre-commit", branch)

    def test_protected_push_from_other_branch(self):
        for target in ("main", "develop"):
            with self.assertRaises(ValueError):
                self.call("pre-push", "feature/work/python", "refs/heads/feature/work/python a refs/heads/" + target + " b\n")

    def test_push_other_ref_rejected(self):
        with self.assertRaises(ValueError):
            self.call("pre-push", "feature/work/javafx", "refs/heads/other/python a refs/heads/other/python b\n")

    def test_valid_push_routes_platform(self):
        self.assertEqual(self.call("pre-push", "feature/work/android", "refs/heads/feature/work/android a refs/heads/feature/work/android b\n"), "android")

    def test_ci_only_python(self):
        self.assertEqual(self.call("ci", "feature/game/unity"), "python")

    def test_ci_without_git(self):
        with patch.object(sys, "argv", ["quality", "ci"]), patch.object(quality.subprocess, "check_output", side_effect=AssertionError("CI must not call Git")), patch.object(quality, "suite") as suite:
            quality.main()
            suite.assert_called_once_with("python", "ci")

    def test_explicit_local_platform_without_git(self):
        with patch.object(sys, "argv", ["quality", "test", "--platform", "javafx"]), patch.object(quality.subprocess, "check_output", side_effect=AssertionError("Explicit platform needs no Git")), patch.object(quality, "suite") as suite:
            quality.main()
            suite.assert_called_once_with("javafx", "test")

    def test_bad_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "coverage.xml"
            for xml in ('<coverage lines-valid="10" line-rate="0.79"/>', '<coverage lines-valid="0" line-rate="1"/>', '<report><counter type="LINE" covered="79" missed="21"/></report>'):
                p.write_text(xml)
                with self.assertRaises(ValueError): quality.coverage(p)

    def test_good_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "coverage.xml"
            p.write_text('<report><counter type="LINE" covered="80" missed="20"/></report>')
            quality.coverage(p)

if __name__ == "__main__": unittest.main()
