"""Intelligence tests: daily sentences, number words, typos, multi."""
import unittest

from ark_agent.intelligence import IntelligentParser, normalize_daily, words_to_number


class TestIntelligence(unittest.TestCase):
    def setUp(self):
        self.smart = IntelligentParser()

    def test_daily_paraphrases(self):
        for sentence, expected in (
            ("please open chrome for me", "open chrome"),
            ("can you launch notepad?", "open notepad"),
            ("turn the sound off", "mute volume"),
            ("close the chrome browser", "close chrome"),
            ("go to youtube", "open youtube"),
        ):
            with self.subTest(sentence=sentence):
                resolved = self.smart.resolve(sentence)
                self.assertTrue(resolved.commands, sentence)
                self.assertEqual(resolved.commands[0].phrase, expected)

    def test_number_words(self):
        self.assertIn("50", words_to_number("set volume to fifty percent"))
        resolved = self.smart.resolve("set volume to fifty percent")
        self.assertTrue(resolved.commands)
        self.assertEqual(resolved.commands[0].variables.get("number"), 50)

    def test_typo_safe_command_auto_corrected(self):
        # The exact dry-run screenshot case: "clise chrome" -> close chrome
        # is confirm-gated, so it must NOT auto-correct; it must ask.
        resolved = self.smart.resolve("clise chrome")
        self.assertEqual(resolved.method, "ask")
        self.assertEqual(resolved.suggestion, "close chrome")
        # A safe typo, e.g. "opem chrome", should auto-correct.
        resolved = self.smart.resolve("opem chrome")
        self.assertEqual(resolved.method, "fuzzy")
        self.assertEqual(resolved.commands[0].phrase, "open chrome")

    def test_dangerous_typo_never_auto_executes(self):
        resolved = self.smart.resolve("shut down computr")
        self.assertNotEqual(resolved.method, "fuzzy")
        self.assertTrue(resolved.method in ("ask", "none"))

    def test_multi_command_sentence(self):
        resolved = self.smart.resolve("open chrome and open notepad")
        self.assertEqual(resolved.method, "multi")
        self.assertEqual(len(resolved.commands), 2)
        self.assertEqual(resolved.commands[0].phrase, "open chrome")
        self.assertEqual(resolved.commands[1].phrase, "open notepad")

    def test_multi_with_bad_part_is_not_split(self):
        resolved = self.smart.resolve("open chrome and do something impossible")
        self.assertNotEqual(resolved.method, "multi")

    def test_normalize_daily(self):
        self.assertEqual(normalize_daily("Please open Chrome for me."), "open chrome")
        self.assertEqual(normalize_daily("Can you launch Notepad?"), "open notepad")


if __name__ == "__main__":
    unittest.main()
