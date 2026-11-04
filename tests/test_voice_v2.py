"""Voice v2 tests: alternatives, dictation exit, long-sentence handling."""
import unittest

from ark_agent.voice import VoiceEngine, parse_vosk_alternatives


class TestVoiceV2(unittest.TestCase):
    def setUp(self):
        self.voice = VoiceEngine()

    def test_alternatives_parsing(self):
        alts = parse_vosk_alternatives(
            '{"alternatives": [{"text": "open crome", "confidence": 0.6}, {"text": "open chrome", "confidence": 0.9}]}'
        )
        self.assertEqual(alts[0][0], "open crome")
        self.assertEqual(alts[1][0], "open chrome")

    def test_alternative_recovers_correct_command(self):
        result = self.voice.process_transcript_with_alternatives(
            [("open crome", 0.6), ("open chrome", 0.9)]
        )
        self.assertIsNotNone(result.command)
        assert result.command is not None
        self.assertEqual(result.command.action, "launch_app")

    def test_dictation_exit_with_politeness(self):
        self.voice.process_transcript("start dictation")
        self.assertEqual(self.voice.mode, "dictation")
        result = self.voice.process_transcript("stop dictation please")
        self.assertEqual(self.voice.mode, "command")
        self.assertIn("stopped", result.message.lower())

    def test_dictation_still_never_executes(self):
        self.voice.process_transcript("start dictation")
        result = self.voice.process_transcript("close chrome")
        self.assertEqual(result.mode, "dictation")
        self.assertIsNone(result.command)

    def test_brightness_level_phrase(self):
        # v1.1 screenshot failure: "set brightness level to 50"
        from ark_agent.intelligence import IntelligentParser

        resolved = IntelligentParser().resolve("set brightness level to 50")
        self.assertTrue(resolved.commands)
        self.assertEqual(resolved.commands[0].variables.get("number"), 50)

    def test_single_word_page_is_not_a_suggestion(self):
        from ark_agent.intelligence import IntelligentParser

        resolved = IntelligentParser().resolve("page")
        self.assertEqual(resolved.method, "none")
        self.assertEqual(resolved.suggestion, "")

    def test_yes_variants(self):
        from ark_agent.actions import ConfirmationManager

        mgr = ConfirmationManager()
        for text in ("yes", "yeah", "yep", "yes please", "yese"):
            with self.subTest(text=text):
                self.assertTrue(mgr.decide(text))
        for text in ("no", "nope", "cancel"):
            with self.subTest(text=text):
                self.assertFalse(mgr.decide(text))
        self.assertIsNone(mgr.decide("yeah not sure"))


if __name__ == "__main__":
    unittest.main()
