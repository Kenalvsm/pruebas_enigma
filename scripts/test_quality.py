import importlib.util
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    'quality', Path(__file__).with_name('quality.py')
)
quality = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quality)


class Gates(unittest.TestCase):
    def calls(self, stage, branch, refs=''):
        """Etapas que habrian ejecutado la suite; [] si la rama se ignora."""
        with (
            patch.object(sys, 'argv', ['quality', stage, '--branch', branch]),
            patch.object(sys, 'stdin', io.StringIO(refs)),
            patch.object(quality, 'suite') as suite,
        ):
            quality.main()
            return [call.args[0] for call in suite.call_args_list]

    def test_python_branches_detected(self):
        for branch in ('feature/work/python', 'chore/infra/python', 'fix/python'):
            self.assertTrue(quality.is_python_branch(branch))

    def test_other_branches_ignored(self):
        for branch in (
            'feature/work',
            'feature/work/javafx',
            'feature/work/android',
            'feature/work/unity',
            'feature/PYTHON',
            'python-legacy',
            '',
        ):
            self.assertFalse(quality.is_python_branch(branch))

    def test_pre_commit_runs_python(self):
        self.assertEqual(self.calls('pre-commit', 'feature/work/python'), ['pre-commit'])

    def test_ignored_branch_skips_suite(self):
        for branch in ('feature/work/javafx', 'feature/work/android', 'feature/work/unity'):
            self.assertEqual(self.calls('pre-commit', branch), [])

    def test_protected_commit(self):
        for branch in ('main', 'develop'):
            with self.assertRaises(ValueError):
                self.calls('pre-commit', branch)

    def test_protected_push_from_other_branch(self):
        for target in ('main', 'develop'):
            with self.assertRaises(ValueError):
                self.calls(
                    'pre-push',
                    'feature/work/python',
                    'refs/heads/feature/work/python a refs/heads/' + target + ' b\n',
                )

    def test_push_other_ref_rejected(self):
        with self.assertRaises(ValueError):
            self.calls(
                'pre-push',
                'feature/work/python',
                'refs/heads/other/python a refs/heads/other/python b\n',
            )

    def test_valid_push_runs_python(self):
        refs = 'refs/heads/feature/work/python a refs/heads/feature/work/python b\n'
        self.assertEqual(self.calls('pre-push', 'feature/work/python', refs), ['pre-push'])

    def test_ignored_branch_push_skips_suite(self):
        refs = 'refs/heads/feature/work/javafx a refs/heads/feature/work/javafx b\n'
        self.assertEqual(self.calls('pre-push', 'feature/work/javafx', refs), [])

    def test_ignored_branch_push_to_protected_still_blocked(self):
        with self.assertRaises(ValueError):
            self.calls(
                'pre-push',
                'feature/work/javafx',
                'refs/heads/feature/work/javafx a refs/heads/main b\n',
            )

    def test_ci_only_python_without_git(self):
        with (
            patch.object(sys, 'argv', ['quality', 'ci']),
            patch.object(
                quality.subprocess,
                'check_output',
                side_effect=AssertionError('CI must not call Git'),
            ),
            patch.object(quality, 'suite') as suite,
        ):
            quality.main()
            suite.assert_called_once_with('ci')

    def test_manual_run_without_git(self):
        with (
            patch.object(sys, 'argv', ['quality', 'test', '--platform', 'python']),
            patch.object(
                quality.subprocess,
                'check_output',
                side_effect=AssertionError('Explicit platform needs no Git'),
            ),
            patch.object(quality, 'suite') as suite,
        ):
            quality.main()
            suite.assert_called_once_with('test')


if __name__ == '__main__':
    unittest.main()
