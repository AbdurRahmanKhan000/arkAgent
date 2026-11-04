"""User config tests: save/load, default browser, model path."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ark_agent import user_config


class TestUserConfig(unittest.TestCase):
    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "arkagent_config.json"
            with mock.patch.object(user_config, "PROJECT_CONFIG", target), \
                 mock.patch.object(user_config, "HOME_CONFIG", Path(tmp) / "missing.json"):
                user_config.save_config({"default_browser": "edge", "apps": {"chrome": "F:\\chrome.exe"}}, path=target)
                data = json.loads(target.read_text(encoding="utf-8"))
                self.assertEqual(data["default_browser"], "edge")
                self.assertEqual(data["apps"]["chrome"], "F:\\chrome.exe")

    def test_default_browser_falls_back_to_chrome(self):
        with mock.patch.object(user_config, "load_config", return_value={}):
            self.assertEqual(user_config.get_default_browser(), "chrome")

    def test_vosk_model_path_from_config(self):
        with mock.patch.object(user_config, "load_config", return_value={"vosk_model_path": "C:\\models\\small"}):
            self.assertEqual(user_config.get_vosk_model_path(), "C:\\models\\small")


if __name__ == "__main__":
    unittest.main()
