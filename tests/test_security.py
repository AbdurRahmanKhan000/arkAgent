"""Security tests: allowlist, protected processes, no shell execution."""
import pathlib
import re
import unittest

from ark_agent.actions import ActionExecutor
from ark_agent.parser import Parser

SRC = pathlib.Path(__file__).resolve().parent.parent / "ark_agent"


class TestSecurity(unittest.TestCase):
    def test_no_shell_or_arbitrary_code_execution_in_source(self):
        forbidden = [r"os\.system\s*\(", r"shell\s*=\s*True", r"\beval\s*\(", r"\bexec\s*\("]
        for path in SRC.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden:
                with self.subTest(file=path.name, pattern=pattern):
                    self.assertIsNone(re.search(pattern, text), f"{pattern} found in {path.name}")

    def test_protected_process_cannot_be_closed(self):
        parser = Parser()
        executor = ActionExecutor(dry_run=True)
        cmd = parser.parse("close file explorer")
        assert cmd is not None
        result = executor.execute(cmd)
        # close file explorer is confirm-gated, so confirm first, then
        # the protected-process check must still deny it.
        pending = executor.confirm_pending("yes")
        self.assertFalse(pending.success)
        self.assertIn("protected", pending.message.lower())

    def test_user_text_never_becomes_a_subprocess_argument(self):
        # "type X and press enter" must type X, not run X. In dry-run
        # the message must contain the text as data, not as a command.
        parser = Parser()
        executor = ActionExecutor(dry_run=True)
        cmd = parser.parse("type rm -rf / and press enter")
        assert cmd is not None
        result = executor.execute(cmd)
        self.assertTrue(result.success)
        self.assertIn("rm -rf", result.message)


if __name__ == "__main__":
    unittest.main()
