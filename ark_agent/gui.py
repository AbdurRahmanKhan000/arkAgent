"""Professional Tkinter interface for arkAgent.

Layout:
  Left  : animated cartoon character (canvas-drawn, no image files),
          status line, last heard transcript, confidence display.
  Right : command log, text input, Run / Listen / Stop buttons,
          command search box.

Threading rule: voice recording runs in a background thread. It never
touches Tkinter directly; it puts results in a queue and the UI polls
that queue with after(). That is what keeps the window responsive
while voice is running.

If Tkinter is unavailable, run_gui() raises a clear error and the
user should use the text CLI in main.py instead.
"""
from __future__ import annotations

import queue
import threading

from .actions import ActionExecutor
from .character import next_frame, state_message
from .parser import Parser
from .tts import Speaker
from .voice import VoiceEngine

BG = "#0f172a"
PANEL = "#1e293b"
TEXT = "#e2e8f0"
ACCENT = "#38bdf8"
GREEN = "#22c55e"
RED = "#ef4444"
AMBER = "#f59e0b"


class ArkGui:
    def __init__(self, dry_run: bool = False) -> None:
        try:
            import tkinter as tk
            from tkinter import ttk
        except ImportError as exc:
            raise RuntimeError("Tkinter is not available on this Python install.") from exc
        self.tk = tk
        self.parser = Parser()
        self.executor = ActionExecutor(dry_run=dry_run)
        self.speaker = Speaker(enabled=True)
        self.voice = VoiceEngine(parser=self.parser)
        self.state = "idle"
        self.tick = 0
        self.voice_queue: queue.Queue = queue.Queue()
        self.voice_thread: threading.Thread | None = None

        self.root = tk.Tk()
        self.root.title("arkAgent — Fixed-Command Laptop Agent")
        self.root.geometry("900x560")
        self.root.configure(bg=BG)
        self._build_widgets(ttk)
        self._animate()
        self.root.after(200, self._poll_voice_queue)

    def _build_widgets(self, ttk) -> None:
        tk = self.tk
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", background=ACCENT, foreground="#0f172a", padding=8)
        style.configure("TEntry", padding=8)

        left = tk.Frame(self.root, bg=PANEL, width=320)
        left.pack(side="left", fill="y", padx=10, pady=10)
        self.canvas = tk.Canvas(left, width=280, height=280, bg=PANEL, highlightthickness=0)
        self.canvas.pack(pady=10)
        self.status_var = tk.StringVar(value=state_message("idle"))
        tk.Label(left, textvariable=self.status_var, bg=PANEL, fg=TEXT, wraplength=280, font=("Segoe UI", 11, "bold")).pack(pady=4)
        self.heard_var = tk.StringVar(value="Last heard: —")
        tk.Label(left, textvariable=self.heard_var, bg=PANEL, fg="#94a3b8", wraplength=280, font=("Segoe UI", 10)).pack(pady=4)
        tk.Label(left, text="arkAgent speaks and works locally. No LLM, no cloud.", bg=PANEL, fg="#94a3b8", wraplength=280, font=("Segoe UI", 9)).pack(pady=8)

        right = tk.Frame(self.root, bg=BG)
        right.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.log = tk.Text(right, bg="#020617", fg=TEXT, font=("Consolas", 10), height=20)
        self.log.pack(fill="both", expand=True)
        self.log.insert("end", "Welcome to arkAgent. Type a command below, or press Listen.\n")
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

        search_row = tk.Frame(right, bg=BG)
        search_row.pack(fill="x")
        self.search_var = tk.StringVar()
        ttk.Entry(search_row, textvariable=self.search_var, width=30).pack(side="left", padx=(0, 8))
        ttk.Button(search_row, text="Search commands", command=self.search_commands).pack(side="left")

    # -- character drawing ----------------------------------------------------
    def _draw_character(self) -> None:
        frame = next_frame(self.state, self.tick)
        c = self.canvas
        c.delete("all")
        # Body / head
        c.create_oval(60, 30, 220, 190, fill="#38bdf8", outline="")
        # Ears: raised when listening or working
        ear_y = 20 if frame.ears_up else 35
        c.create_oval(70, ear_y, 100, 55, fill="#0ea5e9", outline="")
        c.create_oval(180, ear_y, 210, 55, fill="#0ea5e9", outline="")
        # Eyes: closed line when blinking, happy arcs on success, worried on error
        if frame.blinking:
            c.create_line(95, 100, 125, 100, fill="#0f172a", width=3)
            c.create_line(155, 100, 185, 100, fill="#0f172a", width=3)
        elif frame.happy:
            c.create_arc(95, 90, 125, 115, start=0, extent=180, fill="#0f172a", width=3, style="arc")
            c.create_arc(155, 90, 185, 115, start=0, extent=180, fill="#0f172a", width=3, style="arc")
        elif frame.worried:
            c.create_line(95, 90, 125, 105, fill="#0f172a", width=3)
            c.create_line(155, 105, 185, 90, fill="#0f172a", width=3)
        else:
            c.create_oval(100, 90, 120, 110, fill="#0f172a", outline="")
            c.create_oval(160, 90, 180, 110, fill="#0f172a", outline="")
        # Mouth: open oval when speaking, smile otherwise, flat on error
        if frame.mouth_open:
            c.create_oval(125, 135, 155, 160, fill="#0f172a", outline="")
        elif frame.worried:
            c.create_line(125, 155, 155, 155, fill="#0f172a", width=3)
        else:
            c.create_arc(120, 130, 160, 155, start=180, extent=180, fill="#0f172a", width=3, style="arc")
        # Working gear, bottom-right
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

    # -- logging --------------------------------------------------------------
    def _log(self, text: str) -> None:
        self.log.config(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    # -- command handling (shared with the CLI) --------------------------------
    def handle_text(self, text: str) -> None:
        if self.executor.confirmations.pending is not None:
            result = self.executor.confirm_pending(text)
            self._log(result.message)
            self._set_state("success" if result.success else "error")
            if result.success and result.message:
                self._set_state("speaking")
                self.speaker.speak(result.message)
            return
        self._set_state("working")
        parsed = self.parser.parse(text)
        if parsed is None:
            suggestions = self.parser.suggestions(text)
            message = "I do not recognise that command."
            if suggestions:
                message += f" Did you mean: {', '.join(suggestions)}?"
            self._log(message)
            self._set_state("error")
            self.speaker.speak(message)
            return
        result = self.executor.execute(parsed)
        self._log(result.message)
        if result.needs_confirmation:
            self._set_state("speaking")
            self.speaker.speak(result.message)
            return
        self._set_state("success" if result.success else "error")
        self.speaker.speak(result.message)

    def run_typed(self) -> None:
        text = self.entry_var.get().strip()
        if not text:
            return
        self.entry_var.set("")
        self._log(f"> {text}")
        self.handle_text(text)

    def search_commands(self) -> None:
        query = self.search_var.get().strip().lower()
        matches = [s.phrase for s in self.parser.specs if query in s.phrase] if query else []
        self._log(f"Commands matching '{query}': {', '.join(matches[:20]) if matches else 'none'}")

    # -- voice ------------------------------------------------------------------
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
                elif result.command is not None:
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
