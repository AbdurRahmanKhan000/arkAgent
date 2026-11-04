"""App discovery tests: drives other than C:, special apps, overrides."""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ark_agent.app_discovery import SPECIAL_APPS, find_app_executable, find_default_browser


class TestDiscovery(unittest.TestCase):
    def test_special_apps_cover_v1_failures(self):
        # "open this pc" and "open recycle bin" failed in v1 because
        # they are not .exe files. They must be special targets in v1.1.
        for name in ("this pc", "recycle bin", "settings", "file explorer"):
            with self.subTest(name=name):
                self.assertIn(name, SPECIAL_APPS)

    def test_finds_app_on_a_non_c_drive(self):
        # Simulate F: as a temp folder with a Chrome install layout.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chrome = root / "Program Files" / "Google" / "Chrome" / "Application" / "chrome.exe"
            chrome.parent.mkdir(parents=True)
            chrome.write_bytes(b"fake exe")
            with mock.patch("ark_agent.app_discovery.shutil.which", return_value=None), \
                 mock.patch("ark_agent.app_discovery._app_paths_registry", return_value=None):
                found = find_app_executable("chrome", drives=[root])
            self.assertEqual(found, chrome)

    def test_user_override_wins_over_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            custom = Path(tmp) / "my-chrome.exe"
            custom.write_bytes(b"fake exe")
            with mock.patch("ark_agent.app_discovery.get_app_paths", return_value={"chrome": str(custom)}):
                found = find_app_executable("chrome", drives=[])
            self.assertEqual(found, custom)

    def test_missing_app_returns_none_not_a_guess(self):
        with mock.patch("ark_agent.app_discovery.shutil.which", return_value=None), \
             mock.patch("ark_agent.app_discovery._app_paths_registry", return_value=None):
            self.assertIsNone(find_app_executable("chrome", drives=[]))

    def test_default_browser_prefers_an_installed_browser(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            edge = root / "Program Files" / "Microsoft" / "Edge" / "Application" / "msedge.exe"
            edge.parent.mkdir(parents=True)
            edge.write_bytes(b"fake exe")
            with mock.patch("ark_agent.app_discovery.shutil.which", return_value=None), \
                 mock.patch("ark_agent.app_discovery._app_paths_registry", return_value=None), \
                 mock.patch("ark_agent.app_discovery.get_default_browser", return_value="chrome"):
                # Chrome is not in this fake drive, Edge is: Edge wins.
                self.assertEqual(find_default_browser(drives=[root]), "edge")


if __name__ == "__main__":
    unittest.main()
