"""Voice tests: command mode, dictation mode, low confidence, grammar."""
import unittest

from ark_agent.voice import VoiceEngine, parse_vosk_result


class TestVoice(unittest.TestCase):
    def setUp(self):
        self.voice = VoiceEngine()

    def test_command_mode_parses_command(self):
        result = self.voice.process_transcript("open chrome")
        self.assertEqual(result.mode, "command")
        self.assertIsNotNone(result.command)

    def test_unknown_voice_command_does_not_execute(self):
        result = self.voice.process_transcript("delete everything please")
        self.assertIsNone(result.command)
        self.assertIn("do not recognise", result.message)

    def test_dictation_mode_never_executes_commands(self):
        self.voice.process_transcript("start dictation")
        self.assertEqual(self.voice.mode, "dictation")
        result = self.voice.process_transcript("close chrome and shut down computer")
        self.assertEqual(result.mode, "dictation")
        self.assertIsNone(result.command)
        self.assertEqual(result.dictation_text, "close chrome and shut down computer")
        self.voice.process_transcript("stop dictation")
        self.assertEqual(self.voice.mode, "command")

    def test_low_confidence_is_not_executed(self):
        result = self.voice.process_transcript("open chrome", confidence=0.2)
        self.assertEqual(result.mode, "low_confidence")
        self.assertIsNone(result.command)

    def test_vosk_json_parsing(self):
        text, conf = parse_vosk_result(
            '{"text": "open chrome", "result": [{"conf": 0.9, "word": "open"}, {"conf": 0.8, "word": "chrome"}]}'
        )
        self.assertEqual(text, "open chrome")
        self.assertAlmostEqual(conf, 0.85)

    def test_grammar_includes_core_commands(self):
        # Grammar phrases are what a constrained recogniser may return.
        # They must include the user's core apps, without variables.
        from ark_agent.parser import Parser

        grammar = Parser().grammar_phrases()
        for phrase in ("open chrome", "open spotify", "open visual studio code", "close chrome"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, grammar)
        self.assertNotIn("open <app>", grammar)


if __name__ == "__main__":
    unittest.main()
