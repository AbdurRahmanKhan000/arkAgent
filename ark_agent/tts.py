"""Text-to-speech. Uses the operating system's voice on Windows
(SAPI via pyttsx3), so no TTS model download is needed.

If pyttsx3 is unavailable, speaking falls back to printing the text,
so the agent still works in text mode.
"""
from __future__ import annotations


class Speaker:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self._engine = None
        if enabled:
            try:
                import pyttsx3

                self._engine = pyttsx3.init()
                self._engine.setProperty("rate", 175)
            except Exception:
                self._engine = None

    def speak(self, text: str) -> str:
        if not text:
            return ""
        if self._engine is not None:
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception:
                pass
        return text
