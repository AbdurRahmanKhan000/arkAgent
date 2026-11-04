"""Registry tests: commands.md and commands.json must agree, and every
registered action must have a handler."""
import json
import pathlib
import unittest

from ark_agent.actions import ActionExecutor
from ark_agent.registry import find_duplicates, load_commands

ROOT = pathlib.Path(__file__).resolve().parent.parent


class TestRegistry(unittest.TestCase):
    def test_at_least_400_commands(self):
        specs = load_commands()
        self.assertGreaterEqual(len(specs), 400, f"Only {len(specs)} commands")

    def test_no_duplicate_phrases(self):
        specs = load_commands()
        self.assertEqual(find_duplicates(specs), [])

    def test_commands_md_and_json_agree(self):
        specs = load_commands()
        data = json.loads((ROOT / "commands.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data), len(specs))
        json_phrases = {entry["phrase"] for entry in data}
        spec_phrases = {spec.phrase for spec in specs}
        self.assertEqual(json_phrases, spec_phrases)

    def test_every_action_has_a_handler(self):
        specs = load_commands()
        handlers = ActionExecutor(dry_run=True)._handlers()
        missing = sorted({s.action for s in specs} - set(handlers))
        self.assertEqual(missing, [], f"Missing handlers: {missing}")

    def test_every_command_has_a_category_and_risk(self):
        for spec in load_commands():
            with self.subTest(phrase=spec.phrase):
                self.assertTrue(spec.category)
                self.assertIn(spec.risk, ("safe", "confirm"))


if __name__ == "__main__":
    unittest.main()
