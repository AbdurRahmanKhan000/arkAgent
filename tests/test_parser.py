"""Parser tests: exact, synonym, variable, and rejection cases."""
import unittest

from ark_agent.parser import Parser, normalize


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_exact_command(self):
        cmd = self.parser.parse("open chrome")
        self.assertIsNotNone(cmd)
        assert cmd is not None
        self.assertEqual(cmd.action, "launch_app")
        self.assertFalse(cmd.needs_confirmation)

    def test_case_and_filler_words(self):
        cmd = self.parser.parse("Please Open Chrome.")
        self.assertIsNotNone(cmd)
        assert cmd is not None
        self.assertEqual(cmd.action, "launch_app")

    def test_synonyms(self):
        self.assertEqual(normalize("open intelligi"), "open intellij idea")
        self.assertEqual(normalize("open vs code"), "open visual studio code")
        self.assertEqual(normalize("open notebook"), "open jupyter notebook")
        self.assertEqual(normalize("open browser"), "open chrome")

    def test_variable_text_command(self):
        cmd = self.parser.parse("type hello world and press enter")
        self.assertIsNotNone(cmd)
        assert cmd is not None
        self.assertEqual(cmd.variables.get("text"), "hello world")

    def test_variable_number_command(self):
        cmd = self.parser.parse("set volume to 50 percent")
        self.assertIsNotNone(cmd)
        assert cmd is not None
        self.assertEqual(cmd.variables.get("number"), 50)

    def test_out_of_range_number_rejected(self):
        self.assertIsNone(self.parser.parse("set volume to 150 percent"))
        self.assertIsNone(self.parser.parse("set volume to 999 percent"))

    def test_unknown_command_rejected_not_guessed(self):
        self.assertIsNone(self.parser.parse("delete everything on my computer"))
        self.assertIsNone(self.parser.parse("open a random thing that does not exist"))
        self.assertIsNone(self.parser.parse(""))

    def test_word_commands_present(self):
        for phrase in (
            "bold selected text in word",
            "insert header in word",
            "save document as pdf",
            "change page orientation to landscape in word",
        ):
            with self.subTest(phrase=phrase):
                self.assertIsNotNone(self.parser.parse(phrase))

    def test_suggestions_do_not_execute(self):
        suggestions = self.parser.suggestions("open chorme")
        self.assertIn("open chrome", suggestions)
        # Suggestions are only a hint; parsing the typo itself must fail.
        self.assertIsNone(self.parser.parse("open chorme"))


if __name__ == "__main__":
    unittest.main()
