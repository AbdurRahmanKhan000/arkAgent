"""Web API tests: status, command, task plan, suggestion, settings.

Uses a real HTTP server on an ephemeral port, in a thread, so the
test proves the web interface actually serves and answers — not
just that the code imports.
"""
import json
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

from ark_agent.web_server import ArkWebState, make_handler


def _post(base, path, data):
    req = urllib.request.Request(
        base + path,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


class TestWeb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state = ArkWebState(dry_run=True)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cls.state))
        cls.port = cls.server.server_address[1]
        cls.base = f"http://127.0.0.1:{cls.port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_index_serves_web_ui(self):
        with urllib.request.urlopen(self.base + "/", timeout=10) as resp:
            body = resp.read().decode("utf-8")
        self.assertIn("arkAgent", body)
        self.assertIn("character", body)

    def test_status(self):
        with urllib.request.urlopen(self.base + "/api/status", timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(data["version"], "2.0.0")
        self.assertGreaterEqual(data["commands"], 400)

    def test_command_execution_via_web(self):
        data = _post(self.base, "/api/command", {"text": "open notepad"})
        self.assertEqual(data["type"], "executed")
        self.assertIn("notepad", " ".join(data.get("messages", [])).lower())

    def test_task_plan_via_web(self):
        data = _post(self.base, "/api/command", {"text": "open chrome and search for cats"})
        self.assertEqual(data["type"], "task_plan")
        self.assertEqual(len(data["steps"]), 2)
        # Run it (dry-run) and check it completes.
        result = _post(self.base, "/api/execute_task", {"plan_id": data["plan_id"]})
        self.assertEqual(result["type"], "executed")

    def test_suggestion_via_web(self):
        data = _post(self.base, "/api/command", {"text": "clise chrome"})
        self.assertEqual(data["type"], "ask")
        self.assertEqual(data["suggestion"], "close chrome")
        # Answer "no" — the suggestion must not execute.
        result = _post(self.base, "/api/command", {"text": "no"})
        self.assertIn("not running", result["message"].lower())

    def test_unknown_via_web(self):
        data = _post(self.base, "/api/command", {"text": "do something impossible right now"})
        self.assertEqual(data["type"], "unknown")


if __name__ == "__main__":
    unittest.main()
