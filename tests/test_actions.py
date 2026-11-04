"""Action tests: confirmation gating, dry-run behaviour, time/date."""
import unittest

from ark_agent.actions import ActionExecutor
from ark_agent.parser import Parser


class TestActions(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        self.executor = ActionExecutor(dry_run=True)

    def test_safe_command_runs_in_dry_run(self):
        cmd = self.parser.parse("open chrome")
        assert cmd is not None
        result = self.executor.execute(cmd)
        self.assertTrue(result.success)
        self.assertIn("chrome", result.message.lower())

    def test_confirm_command_does_not_run_without_yes(self):
        cmd = self.parser.parse("close chrome")
        assert cmd is not None
        result = self.executor.execute(cmd)
        self.assertTrue(result.needs_confirmation)
        self.assertFalse(result.success)
        self.assertIsNotNone(self.executor.confirmations.pending)

    def test_confirm_yes_then_runs(self):
        cmd = self.parser.parse("close chrome")
        assert cmd is not None
        self.executor.execute(cmd)
        result = self.executor.confirm_pending("yes")
        self.assertTrue(result.success)

    def test_confirm_no_cancels(self):
        cmd = self.parser.parse("close chrome")
        assert cmd is not None
        self.executor.execute(cmd)
        result = self.executor.confirm_pending("no")
        self.assertTrue(result.success)
        self.assertIn("cancelled", result.message.lower())

    def test_ambiguous_confirmation_answer(self):
        cmd = self.parser.parse("shut down computer")
        assert cmd is not None
        self.executor.execute(cmd)
        result = self.executor.confirm_pending("yeah not sure")
        self.assertFalse(result.success)
        self.assertIn("yes or no", result.message)

    def test_unknown_action_is_not_run(self):
        result = self.executor.execute(None)
        self.assertFalse(result.success)

    def test_tell_time(self):
        cmd = self.parser.parse("what time is it")
        assert cmd is not None
        result = self.executor.execute(cmd)
        self.assertTrue(result.success)
        self.assertIn("time is", result.message.lower())


if __name__ == "__main__":
    unittest.main()
