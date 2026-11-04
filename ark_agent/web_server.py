"""Web interface for arkAgent v2 — a modern web UI, not a Tkinter window.

The server runs only on your laptop (127.0.0.1), with no internet
and no cloud. It uses only the Python standard library, so it adds
no size or dependencies. Open http://127.0.0.1:8765 in your browser.

API (all JSON):
  GET  /api/status          version, command count, voice mode, last heard
  GET  /api/commands?q=...  search registry phrases
  POST /api/command  {text} resolve, plan, ask, or execute; returns
                            type: executed | task_plan | ask | confirm |
                            unknown, plus messages and character state
  POST /api/execute_task {plan_id} run a planned task step by step
  POST /api/listen         start one server-side Vosk utterance
  GET  /api/listen_result  poll the voice result (transcript + mode)
  POST /api/settings {vosk_model_path, default_browser} save config
  POST /api/stop_dictation exit dictation mode immediately

Safety is unchanged: the web UI never executes anything directly.
It calls the same IntelligentParser, TaskPlanner and ActionExecutor
as the text loop, so confirmations, allowlists and protected
processes still apply. A task plan is shown before it runs, and
a failing step stops the task and reports which step failed.
"""
from __future__ import annotations

import json
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .actions import ActionExecutor
from .intelligence import IntelligentParser
from .parser import Parser
from .tasks import TaskPlan, TaskPlanner
from .tts import Speaker
from .user_config import get_default_browser, get_vosk_model_path, save_config
from .voice import VoiceEngine

WEB_DIR = Path(__file__).resolve().parent / "web"
VERSION = "2.0.0"


class ArkWebState:
    """All server state in one place, so tests can drive it directly."""

    def __init__(self, dry_run: bool = False):
        self.parser = Parser()
        self.smart = IntelligentParser(self.parser)
        self.planner = TaskPlanner(self.smart)
        self.executor = ActionExecutor(dry_run=dry_run)
        self.speaker = Speaker(enabled=False)  # web UI speaks via TTS in v2.1; v2 logs text
        self.voice = VoiceEngine(parser=self.parser)
        self.pending_suggestion: str | None = None
        self.pending_plan: TaskPlan | None = None
        self.pending_plan_id: str | None = None
        self.plan_counter = 0
        self.voice_result: dict | None = None
        self.voice_thread: threading.Thread | None = None
        self.last_heard = ""
        self.state = "idle"

    # -- command handling ----------------------------------------------------
    def handle_text(self, text: str) -> dict:
        value = text.strip()
        if not value:
            return {"type": "unknown", "message": "Empty command.", "state": "error"}
        # Confirmation answers first: a "yes" after a question must
        # answer that question, never be parsed as a new command.
        if self.executor.confirmations.pending is not None:
            result = self.executor.confirm_pending(value)
            self.state = "success" if result.success else "error"
            return {"type": "executed", "message": result.message, "state": self.state}
        if self.pending_suggestion is not None:
            suggestion = self.pending_suggestion
            self.pending_suggestion = None
            if value.lower() in ("yes", "confirm", "do it", "yeah", "yep", "sure"):
                return self._execute_commands([suggestion])
            return {"type": "executed", "message": "OK, not running that.", "state": "idle"}
        # Task first: a multi-step goal gets a plan, not just step one.
        plan = self.planner.plan(value)
        if plan is not None and len(plan.steps) >= 2:
            self.plan_counter += 1
            self.pending_plan = plan
            self.pending_plan_id = f"plan-{self.plan_counter}"
            self.state = "working"
            return {
                "type": "task_plan",
                "plan_id": self.pending_plan_id,
                "title": plan.title,
                "steps": plan.steps,
                "message": f"Task plan: {plan.title} — {len(plan.steps)} steps. Confirm to run it.",
                "state": "working",
            }
        resolved = self.smart.resolve(value)
        if resolved.method == "ask" and resolved.suggestion:
            self.pending_suggestion = resolved.suggestion
            self.state = "speaking"
            return {"type": "ask", "suggestion": resolved.suggestion, "message": f"Did you mean: {resolved.suggestion}?", "state": "speaking"}
        if not resolved.commands:
            self.state = "error"
            return {"type": "unknown", "message": "I do not recognise that command.", "state": "error"}
        messages = []
        if resolved.method in ("paraphrase", "fuzzy"):
            messages.append(f"Understood as: {resolved.understood_as}")
        return self._execute_resolved(resolved, messages)

    def _execute_commands(self, command_texts: list[str]) -> dict:
        messages: list[str] = []
        for step_text in command_texts:
            resolved = self.smart.resolve(step_text)
            if not resolved.commands:
                messages.append(f"Step failed — could not understand: {step_text}")
                self.state = "error"
                return {"type": "executed", "messages": messages, "state": "error"}
            for command in resolved.commands:
                result = self.executor.execute(command)
                messages.append(result.message)
                if result.needs_confirmation:
                    self.state = "speaking"
                    return {"type": "confirm", "messages": messages, "message": result.message, "state": "speaking"}
                if not result.success:
                    self.state = "error"
                    return {"type": "executed", "messages": messages, "state": "error"}
        self.state = "success"
        return {"type": "executed", "messages": messages, "message": " ".join(messages), "state": "success"}

    def _execute_resolved(self, resolved, messages: list[str]) -> dict:
        for command in resolved.commands:
            result = self.executor.execute(command)
            messages.append(result.message)
            if result.needs_confirmation:
                self.state = "speaking"
                return {"type": "confirm", "messages": messages, "message": result.message, "state": "speaking"}
            if not result.success:
                self.state = "error"
                return {"type": "executed", "messages": messages, "state": "error"}
        self.state = "success"
        return {"type": "executed", "messages": messages, "message": " ".join(messages), "state": "success"}

    def execute_plan(self, plan_id: str) -> dict:
        if self.pending_plan is None or plan_id != self.pending_plan_id:
            return {"type": "unknown", "message": "That task plan is no longer waiting.", "state": "error"}
        plan = self.pending_plan
        self.pending_plan = None
        self.pending_plan_id = None
        return self._execute_commands(plan.steps)

    def start_listen(self) -> dict:
        if self.voice_thread and self.voice_thread.is_alive():
            return {"started": False, "message": "Already listening."}
        self.voice_result = None
        self.state = "listening"

        def worker():
            result = self.voice.listen_once()
            self.last_heard = result.text
            self.voice_result = {
                "text": result.text,
                "mode": result.mode,
                "message": result.message,
                "dictation_text": result.dictation_text,
            }
            if result.mode == "dictation":
                self.voice.mode = "dictation"
            elif result.mode == "command":
                self.voice.mode = "command"

        self.voice_thread = threading.Thread(target=worker, daemon=True)
        self.voice_thread.start()
        return {"started": True, "message": "Listening..."}

    def status(self) -> dict:
        return {
            "version": VERSION,
            "commands": len(self.parser.specs),
            "mode": self.voice.mode,
            "last_heard": self.last_heard,
            "state": self.state,
            "vosk_model_path": get_vosk_model_path() or "",
            "default_browser": get_default_browser(),
        }


def make_handler(state: ArkWebState):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):  # keep the console clean
            pass

        def _send_json(self, data: dict, status: int = 200) -> None:
            body = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_file(self, filename: str, content_type: str) -> None:
            path = WEB_DIR / filename
            if not path.is_file():
                self.send_error(404)
                return
            body = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> dict:
            length = int(self.headers.get("Content-Length") or 0)
            if not length:
                return {}
            try:
                return json.loads(self.rfile.read(length).decode("utf-8"))
            except Exception:
                return {}

        def do_GET(self):  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path in ("/", "/index.html"):
                self._send_file("index.html", "text/html; charset=utf-8")
            elif parsed.path == "/style.css":
                self._send_file("style.css", "text/css; charset=utf-8")
            elif parsed.path == "/app.js":
                self._send_file("app.js", "text/javascript; charset=utf-8")
            elif parsed.path == "/api/status":
                self._send_json(state.status())
            elif parsed.path == "/api/listen_result":
                result = state.voice_result
                state.voice_result = None
                self._send_json({"result": result})
            elif parsed.path == "/api/commands":
                query = urllib.parse.parse_qs(parsed.query).get("q", [""])[0].lower()
                matches = [s.phrase for s in state.parser.specs if query in s.phrase][:30]
                self._send_json({"commands": matches})
            else:
                self.send_error(404)

        def do_POST(self):  # noqa: N802
            data = self._read_json()
            if self.path == "/api/command":
                self._send_json(state.handle_text(str(data.get("text", ""))))
            elif self.path == "/api/execute_task":
                self._send_json(state.execute_plan(str(data.get("plan_id", ""))))
            elif self.path == "/api/listen":
                self._send_json(state.start_listen())
            elif self.path == "/api/settings":
                save_config({
                    "vosk_model_path": str(data.get("vosk_model_path", "")).strip(),
                    "default_browser": str(data.get("default_browser", "edge")).strip() or "edge",
                })
                state.voice.model_path = str(data.get("vosk_model_path", "")).strip() or None
                state.parser = Parser()
                state.smart = IntelligentParser(state.parser)
                state.planner = TaskPlanner(state.smart)
                self._send_json({"saved": True, "message": "Settings saved to arkagent_config.json."})
            elif self.path == "/api/stop_dictation":
                state.voice.mode = "command"
                self._send_json({"mode": "command", "message": "Dictation stopped. Back to commands."})
            else:
                self.send_error(404)

    return Handler


def run_server(port: int = 8765, dry_run: bool = False, open_browser: bool = True) -> None:
    state = ArkWebState(dry_run=dry_run)
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(state))
    url = f"http://127.0.0.1:{port}"
    print(f"arkAgent v{VERSION} web interface: {url}")
    print("This server runs only on your laptop (127.0.0.1). Press Ctrl+C to stop.")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping arkAgent web interface.")
