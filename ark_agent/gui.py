"""Professional Tkinter interface for arkAgent v1.1.

v1.1 changes, from real v1 testing:
- The GUI is now the main interface, not an afterthought: header,
  status pill, quick-action buttons, command search, and a settings
  panel are all on one screen.
- Settings are saved to arkagent_config.json (no code editing):
  Vosk model folder and default browser. Voice reads that file, so
  "Listen" works once the model path is saved here.
- Daily sentences work here too, because the GUI uses
  IntelligentParser, not just the strict parser. A close match
  shows a "Did you mean: X? Yes / No" bar instead of silently
  failing, and a typo of a safe command is auto-corrected and
  logged as "Understood as: ...".
- The character (character.py) still shows idle / listening /
  working / speaking / success / error, drawn on canvas with no
  image files.

Threading rule: voice recording runs in a background thread. It
never touches Tkinter directly; it puts results in a queue and
the UI polls that queue with after(). That keeps the window
responsive while voice is running.
"""
from __future__ import annotations

import queue
import threading

from .actions import ActionExecutor
from .character import next_frame, state_message
from .intelligence import IntelligentParser
from .parser import Parser
from .tts import Speaker
from .user_config import get_default_browser, get_vosk_model_path, save_config
from .voice import VoiceEngine

BG = "#0f172a"
PANEL = "#1e293b"
TEXT = "#e2e8f0"
MUTED = "#94a3b8"
ACCENT = "#38bdf8"
GREEN = "#22c55e"
RED = "#ef4444"
AMBER = "#f59e0b"

QUICK_ACTIONS = [
    ("Notepad", "open notepad"),
    ("Edge", "open edge"),
    ("Chrome", "open chrome"),
    ("VS Code", "open visual studio code"),
    ("Word", "open microsoft word"),
    ("Mute", "mute volume"),
    ("Volume Up", "volume up"),
    ("This PC", "open this pc"),
]


class ArkGui:
    def __init__(self, dry_run: bool = False) -> None:
        try:
            import tkinter as tk
            from tkinter import ttk
        except ImportError as exc:
            raise RuntimeError("Tkinter is not available on this Python install.") from exc
        self.tk = tk
        self.parser = Parser()
        self.smart = IntelligentParser(self.parser)
        self.executor = ActionExecutor(dry_run=dry_run)
        self.speaker = Speaker(enabled=True)
        self.voice = VoiceEngine(parser=self.parser)
        self.state = "idle"
        self.tick = 0
        self.voice_queue: queue.Queue = queue.Queue()
        self.voice_thread: threading.Thread | None = None
        self.pending_suggestion: str | None = None

        self.root = tk.Tk()
        self.root.title("arkAgent v1.1 — Fixed-Command Laptop Agent")
        self.root.geometry("980x620")
        self.root.configure(bg=BG)
        self._build_widgets(ttk)
        self._animate()
        self.root.after(200, self._poll_voice_queue)

    def _build_widgets(self, ttk) -> None:
        tk = self.tk
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", background=ACCENT, foreground="#0f172a", padding=7)
        style.configure("TEntry", padding=7)
        style.configure("TCombobox", padding=5)

        # Header
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=10, pady=(10, 0))
        tk.Label(header, text="arkAgent", bg=BG, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(side="left")
        tk.Label(header, text="  v1.1  •  No LLM  •  Offline  •  418 commands", bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(side="left", pady=6)
        self.pill_var = tk.StringVar(value="● Ready")
        tk.Label(header, textvariable=self.pill_var, bg=GREEN, fg="#0f172a", font=("Segoe UI", 10, "bold"), padx=10, pady=3).pack(side="right")

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: character + status + settings
        left = tk.Frame(main, bg=PANEL, width=320)
        left.pack(side="left", fill="y", padx=(0, 10))
        self.canvas = tk.Canvas(left, width=280, height=260, bg=PANEL, highlightthickness=0)
        self.canvas.pack(pady=8)
        self.status_var = tk.StringVar(value=state_message("idle"))
        tk.Label(left, textvariable=self.status_var, bg=PANEL, fg=TEXT, wraplength=280, font=("Segoe UI", 11, "bold")).pack(pady=2)
        self.heard_var = tk.StringVar(value="Last heard: —")
        tk.Label(left, textvariable=self.heard_var, bg=PANEL, fg=MUTED, wraplength=280, font=("Segoe UI", 10)).pack(pady=2)

        # Suggestion bar (hidden until a close match needs asking)
        self.suggest_frame = tk.Frame(left, bg=PANEL)
        self.suggest_var = tk.StringVar(value="")
        tk.Label(self.suggest_frame, textvariable=self.suggest_var, bg=PANEL, fg=AMBER, wraplength=280, font=("Segoe UI", 10, "bold")).pack()
        suggest_btns = tk.Frame(self.suggest_frame, bg=PANEL)
        suggest_btns.pack(pady=4)
        ttk.Button(suggest_btns, text="Yes", command=self._suggestion_yes).pack(side="left", padx=4)
        ttk.Button(suggest_btns, text="No", command=self._suggestion_no).pack(side="left", padx=4)

        # Settings: Vosk model path + default browser, saved to config file
        tk.Label(left, text="Settings (saved, no code editing needed)", bg=PANEL, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(pady=(10, 2), anchor="w", padx=10)
        tk.Label(left, text="Vosk model folder:", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=10)
        self.model_var = tk.StringVar(value=get_vosk_model_path() or "")
        ttk.Entry(left, textvariable=self.model_var, width=36).pack(padx=10, pady=2)
        tk.Label(left, text="Default browser:", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=10)
        self.browser_var = tk.StringVar(value=get_default_browser())
        browser_box = ttk.Combobox(left, textvariable=self.browser_var, values=["edge", "chrome", "brave", "firefox", "opera"], width=33, state="readonly")
        browser_box.pack(padx=10, pady=2)
        ttk.Button(left, text="Save settings", command=self._save_settings).pack(pady=6)

        # Right: log, input, quick actions, search
        right = tk.Frame(main, bg=BG)
        right.pack(side="right", fill="both", expand=True)
        self.log = tk.Text(right, bg="#020617", fg=TEXT, font=("Consolas", 10), height=20)
        self.log.pack(fill="both", expand=True)
        self.log.insert("end", "Welcome to arkAgent v1.1.\nType a daily sentence, or press Listen.\nExamples: please open chrome for me • open chrome and open notepad • set volume to fifty percent\n")
        self.log.config(state="disabled")

        entry_row = tk.Frame(right, bg=BG)
        entry_row.pack(fill="x", pady=8)
        self.entry_var = tk.StringVar()
        entry = ttk.Entry(entry_row, textvariable=self.entry_var, width=50)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        entry.bind("<Return>", lambda _e: self.run_typed())
        ttk.Button(entry_row, text="Run", command=self.run_typed).pack(side="left", padx=2)
        ttk.Button(entry_row, text="Listen", command=self.start_listen).pack(side="left", padx=2)
        ttk.Button(entry_row, text="Stop", command=self.stop_listen).pack(side="left", padx=2)

        quick = tk.Frame(right, bg=BG)
        quick.pack(fill="x", pady=(0, 8))
        tk.Label(quick, text="Quick actions:", bg=BG, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 6))
        for label, command in QUICK_ACTIONS:
            ttk.Button(quick, text=label, command=lambda c=command: self.run_command(c)).pack(side="left", padx=2)

        search_row = tk.Frame(right, bg=BG)
        search_row.pack(fill="x")
        self.search_var = tk.StringVar()
        ttk.Entry(search_row, textvariable=self.search_var, width=30).pack(side="left", padx=(0, 8))
        ttk.Button(search_row, text="Search commands", command=self.search_commands).pack(side="left")

    # -- character drawing (same states as v1, slightly larger canvas) -------
    def _draw_character(self) -> None:
        frame = next_frame(self.state, self.tick)
        c = self.canvas
        c.delete("all")
        c.create_oval(60, 30, 220, 190, fill="#38bdf8", outline="")
        ear_y = 20 if frame.ears_up else 35
        c.create_oval(70, ear_y, 100, 55, fill="#0ea5e9", outline="")
        c.create_oval(180, ear_y, 210, 55, fill="#0ea5e9", outline="")
        if frame.blinking:
            c.create_line(95, 100, 125, 100, fill="#0f172a", width=3)
            c.create_line(155, 100, 185, 100, fill="#0f172a", width=3)
        elif frame.happy:
            c.create_arc(95, 90, 125, 115, start=0, extent=180, width=3, style="arc", outline="#0f172a")
            c.create_arc(155, 90, 185, 115, start=0, extent=180, width=3, style="arc", outline="#0f172a")
        elif frame.worried:
            c.create_line(95, 90, 125, 105, fill="#0f172a", width=3)
            c.create_line(155, 105, 185, 90, fill="#0f172a", width=3)
        else:
            c.create_oval(100, 90, 120, 110, fill="#0f172a", outline="")
            c.create_oval(160, 90, 180, 110, fill="#0f172a", outline="")
        if frame.mouth_open:
            c.create_oval(125, 135, 155, 160, fill="#0f172a", outline="")
        elif frame.worried:
            c.create_line(125, 155, 155, 155, fill="#0f172a", width=3)
        else:
            c.create_arc(120, 130, 160, 155, start=180, extent=180, width=3, style="arc", outline="#0f172a")
        if self.state == "working":
            c.create_text(230, 220, text="⚙", font=("Segoe UI", 28), fill=AMBER)
            c.create_text(230, 245, text="working", fill=AMBER, font=("Segoe UI", 9, "bold"))
        elif self.state == "listening":
            c.create_text(140, 220, text="● listening", fill=RED, font=("Segoe UI", 10, "bold"))
        elif self.state == "speaking":
            c.create_text(140, 220, text="♪ speaking", fill=GREEN, font=("Segoe UI", 10, "bold"))

    def _animate(self) -> None:
        self.tick += 1
        self._draw_character()
        self.root.after(250, self._animate)

    def _set_state(self, state: str) -> None:
        self.state = state
        self.status_var.set(state_message(state))
        pill = {"idle": "● Ready", "listening": "● Listening", "working": "● Working", "speaking": "● Speaking", "success": "● Done", "error": "● Error"}.get(state, "● Ready")
        self.pill_var.set(pill)

    def _log(self, text: str) -> None:
        self.log.config(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def _save_settings(self) -> None:
        save_config({
            "vosk_model_path": self.model_var.get().strip(),
            "default_browser": self.browser_var.get().strip() or "edge",
        })
        # Refresh the running voice engine and parser default immediately.
        self.voice.model_path = self.model_var.get().strip() or None
        self.parser = Parser()
        self.smart = IntelligentParser(self.parser)
        self._log("Settings saved to arkagent_config.json.")

    # -- suggestion handling ----------------------------------------------------
    def _show_suggestion(self, suggestion: str) -> None:
        self.pending_suggestion = suggestion
        self.suggest_var.set(f"Did you mean: {suggestion}?")
        self.suggest_frame.pack(pady=4)
        self._set_state("speaking")
        self.speaker.speak(f"Did you mean: {suggestion}?")

    def _hide_suggestion(self) -> None:
        self.pending_suggestion = None
        self.suggest_frame.pack_forget()

    def _suggestion_yes(self) -> None:
        suggestion = self.pending_suggestion
        self._hide_suggestion()
        if suggestion:
            self.run_command(suggestion)

    def _suggestion_no(self) -> None:
        self._hide_suggestion()
        self._log("OK, not running that.")
        self._set_state("idle")

    # -- command handling ---------------------------------------------------------
    def handle_text(self, text: str) -> None:
        if self.executor.confirmations.pending is not None:
            result = self.executor.confirm_pending(text)
            self._log(result.message)
            self._set_state("success" if result.success else "error")
            if result.success:
                self.speaker.speak(result.message)
            return
        self._set_state("working")
        resolved = self.smart.resolve(text)
        if resolved.method == "ask" and resolved.suggestion:
            self._show_suggestion(resolved.suggestion)
            return
        if not resolved.commands:
            message = "I do not recognise that command."
            self._log(message)
            self._set_state("error")
            self.speaker.speak(message)
            return
        if resolved.method in ("paraphrase", "fuzzy"):
            self._log(f"Understood as: {resolved.understood_as}")
        if resolved.method == "multi":
            self._log(f"Running {len(resolved.commands)} commands: {resolved.understood_as}")
        for command in resolved.commands:
            result = self.executor.execute(command)
            self._log(result.message)
            if result.needs_confirmation:
                self._set_state("speaking")
                self.speaker.speak(result.message)
                return
            self._set_state("success" if result.success else "error")
            self.speaker.speak(result.message)

    def run_command(self, command: str) -> None:
        self._log(f"> {command}")
        self.handle_text(command)

    def run_typed(self) -> None:
        text = self.entry_var.get().strip()
        if not text:
            return
        self.entry_var.set("")
        self.run_command(text)

    def search_commands(self) -> None:
        query = self.search_var.get().strip().lower()
        matches = [s.phrase for s in self.parser.specs if query in s.phrase] if query else []
        self._log(f"Commands matching '{query}': {', '.join(matches[:20]) if matches else 'none'}")

    # -- voice ----------------------------------------------------------------------
    def start_listen(self) -> None:
        if self.voice_thread and self.voice_thread.is_alive():
            return
        self._set_state("listening")
        self._log("Listening... (push-to-talk: one utterance)")

        def worker():
            result = self.voice.listen_once()
            self.voice_queue.put(result)

        self.voice_thread = threading.Thread(target=worker, daemon=True)
        self.voice_thread.start()

    def stop_listen(self) -> None:
        self.voice.listening = False
        self._set_state("idle")

    def _poll_voice_queue(self) -> None:
        try:
            while True:
                result = self.voice_queue.get_nowait()
                self.heard_var.set(f"Last heard: {result.text or '—'}")
                if result.mode == "unavailable":
                    self._log(result.message)
                    self._set_state("error")
                elif result.mode == "dictation":
                    self._log(f"Dictation: {result.dictation_text}")
                    self._set_state("speaking")
                elif result.mode == "command":
                    # Route voice text through the intelligent parser, so
                    # daily sentences and typos work by voice too.
                    self.handle_text(result.text)
                else:
                    self._log(result.message)
                    self._set_state("error")
        except queue.Empty:
            pass
        self.root.after(200, self._poll_voice_queue)

    def run(self) -> None:
        self.root.mainloop()


def run_gui(dry_run: bool = False) -> None:
    ArkGui(dry_run=dry_run).run()
