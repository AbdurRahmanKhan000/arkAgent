"""Voice pipeline for heavy, daily voice use. No LLM, no cloud.

Why this design is more reliable than open dictation for commands:
- COMMAND mode uses a grammar-constrained recogniser. Vosk is only
  allowed to return phrases from the registry (plus number steps).
  That removes most mis-hearings of unrelated words.
- DICTATION mode is separate. After "start dictation", speech is
  typed as text only. It is never parsed as a command, so a dictated
  sentence can never accidentally close an app or shut down the PC.
  "stop dictation" returns to command mode.
- Low-confidence results are not executed. The agent asks the user
  to repeat, and shows the transcript it heard.
- Push-to-talk is the default. Always-listening wake-word mode is a
  later, optional add-on (openWakeWord), not a v1 requirement, because
  it adds false triggers from TV and background speech.

If Vosk is not installed, this module still imports, and the GUI /
CLI report a clear install message instead of crashing. Text mode
always works without voice.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .parser import Parser
from .user_config import get_vosk_model_path

LOW_CONFIDENCE_THRESHOLD = 0.5


@dataclass
class VoiceResult:
    text: str
    mode: str  # "command", "dictation", "low_confidence", "unavailable"
    command: object | None = None
    dictation_text: str = ""
    confidence: float | None = None
    message: str = ""


def parse_vosk_result(result_json: str) -> tuple[str, float | None]:
    """Extract text and mean word confidence from a Vosk JSON result.

    Vosk word entries carry a "conf" value when available. If the
    model does not supply confidences, confidence is None and the
    caller must not treat the result as low-confidence.
    """
    try:
        data = json.loads(result_json)
    except json.JSONDecodeError:
        return "", None
    text = (data.get("text") or "").strip()
    words = data.get("result") or []
    confs = [w["conf"] for w in words if isinstance(w, dict) and "conf" in w]
    confidence = sum(confs) / len(confs) if confs else None
    return text, confidence


class VoiceEngine:
    def __init__(self, parser: Parser | None = None, model_path: str | None = None):
        self.parser = parser if parser is not None else Parser()
        # v1.1: read the model path from arkagent_config.json if the
        # caller did not pass one, so the GUI no longer needs a code edit.
        self.model_path = model_path or get_vosk_model_path()
        self.mode = "command"  # or "dictation"
        self.listening = False
        self.last_transcript = ""
        self._model = None
        self._recognizer = None

    # -- availability -------------------------------------------------------
    @property
    def vosk_available(self) -> bool:
        try:
            import vosk  # noqa: F401
            return True
        except ImportError:
            return False

    def load_model(self) -> str:
        """Load Vosk if available. Returns an empty string on success,
        otherwise a human-readable install message."""
        if not self.vosk_available:
            return (
                "Vosk is not installed. Install it, then download the small "
                "English model (vosk-model-small-en-us) from the official "
                "Vosk models page and set model_path to that folder. "
                "Text mode works without voice."
            )
        if not self.model_path:
            return (
                "No Vosk model folder is set. Download vosk-model-small-en-us "
                "from the official Vosk models page and set model_path."
            )
        try:
            from vosk import KaldiRecognizer, Model

            self._model = Model(self.model_path)
            grammar = json.dumps(self.parser.grammar_phrases())
            self._recognizer = KaldiRecognizer(self._model, 16000, grammar)
            return ""
        except Exception as exc:
            return f"Could not load Vosk model: {exc}"

    # -- transcript handling (pure, testable, no microphone needed) ---------
    def process_transcript(self, transcript: str, confidence: float | None = None) -> VoiceResult:
        text = " ".join(transcript.strip().lower().split())
        self.last_transcript = text
        if not text:
            return VoiceResult("", "command", message="I did not hear anything.")
        if text in ("start dictation", "start dictating"):
            self.mode = "dictation"
            return VoiceResult(text, "dictation", message="Dictation started. Speech will be typed, not run as commands.")
        if text in ("stop dictation", "stop dictating", "end dictation"):
            self.mode = "command"
            return VoiceResult(text, "command", message="Dictation stopped. Back to commands.")
        if self.mode == "dictation":
            return VoiceResult(text, "dictation", dictation_text=text, confidence=confidence)
        if confidence is not None and confidence < LOW_CONFIDENCE_THRESHOLD:
            return VoiceResult(
                text, "low_confidence", confidence=confidence,
                message=f"I heard '{text}', but I am not sure. Please repeat it.",
            )
        command = self.parser.parse(text)
        if command is None:
            suggestions = self.parser.suggestions(text)
            hint = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
            return VoiceResult(text, "command", message=f"I do not recognise that command.{hint}")
        return VoiceResult(text, "command", command=command, confidence=confidence)

    def process_vosk_json(self, result_json: str) -> VoiceResult:
        text, confidence = parse_vosk_result(result_json)
        return self.process_transcript(text, confidence=confidence)

    # -- microphone (only used by the GUI / CLI voice loop) ------------------
    def listen_once(self, timeout_seconds: int = 10) -> VoiceResult:
        """Record one push-to-talk utterance and return its VoiceResult.

        Requires vosk + sounddevice + a loaded model. This method is
        intentionally not used by any unit test.
        """
        error = self.load_model()
        if error:
            return VoiceResult("", "unavailable", message=error)
        try:
            import queue
            import sounddevice as sd
        except ImportError:
            return VoiceResult("", "unavailable", message="sounddevice is not installed. Run: pip install sounddevice")
        audio_queue: queue.Queue = queue.Queue()

        def callback(indata, _frames, _time, _status):
            audio_queue.put(bytes(indata))

        self.listening = True
        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=callback):
                import time

                deadline = time.monotonic() + timeout_seconds
                while time.monotonic() < deadline:
                    try:
                        data = audio_queue.get(timeout=0.5)
                    except queue.Empty:
                        continue
                    if self._recognizer.AcceptWaveform(data):
                        return self.process_vosk_json(self._recognizer.Result())
                return self.process_vosk_json(self._recognizer.FinalResult())
        finally:
            self.listening = False


def clean_transcript_for_grammar(text: str) -> str:
    """Strip characters a grammar recogniser should never need."""
    return re.sub(r"[^a-z0-9 %]", "", text.lower()).strip()
