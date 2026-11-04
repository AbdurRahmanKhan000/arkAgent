"""The only parser in arkAgent. Text and voice use this same code.

Design rules, chosen for heavy voice use:
1. Normalise first: lower-case, collapse spaces, strip "please" and
   a leading wake word ("ark", "hey ark").
2. Apply developer-written synonyms (config.SYNONYMS), longest first.
3. Match only against the registry. Unknown input returns None and
   the caller must reply "I do not recognise that command" and do
   nothing. It must never guess a nearby dangerous action.
4. Numbers are range-checked. "set volume to 150 percent" is rejected,
   not silently clamped to 100.
"""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field

from .config import NUMBER_RANGES, SYNONYMS
from .registry import CommandSpec, load_commands
from .user_config import get_default_browser

_FILLERS = ("please ", "hey ark ", "ark ", "ok ark ", "okay ark ")


@dataclass
class ParsedCommand:
    phrase: str
    action: str
    risk: str
    category: str
    variables: dict = field(default_factory=dict)

    @property
    def needs_confirmation(self) -> bool:
        return self.risk == "confirm"


def normalize(text: str) -> str:
    """Lower-case, trim, collapse spaces, strip fillers and synonyms."""
    value = " ".join(text.strip().lower().split())
    value = value.rstrip(".!?")
    changed = True
    while changed:
        changed = False
        for filler in _FILLERS:
            if value.startswith(filler):
                value = value[len(filler):].strip()
                changed = True
    if value == "open browser":
        value = f"open {get_default_browser()}"
    if value == "open intellij":
        value = "open intellij idea"
    # Longest synonym first, so "vs code" is not split into "vs" + "code".
    for spoken in sorted(SYNONYMS, key=len, reverse=True):
        target = SYNONYMS[spoken]
        if value == spoken:
            value = target
        elif value.startswith(spoken + " "):
            value = target + value[len(spoken):]
        elif value.endswith(" " + spoken):
            value = value[: -len(spoken)] + target
        elif f" {spoken} " in value:
            value = value.replace(f" {spoken} ", f" {target} ")
    return " ".join(value.split())


def _number_in_range(action: str, number: int) -> bool:
    low, high = NUMBER_RANGES.get(action, (0, 10**9))
    return low <= number <= high


class Parser:
    def __init__(self, specs: list[CommandSpec] | None = None):
        self.specs = specs if specs is not None else load_commands()

    def parse(self, text: str) -> ParsedCommand | None:
        value = normalize(text)
        if not value:
            return None
        for spec in self.specs:
            match = spec.pattern.match(value)
            if not match:
                continue
            variables = {
                key: val.strip()
                for key, val in match.groupdict().items()
                if val is not None
            }
            if "number" in variables:
                try:
                    number = int(variables["number"])
                except ValueError:
                    continue
                if not _number_in_range(spec.action, number):
                    continue
                variables["number"] = number
            return ParsedCommand(
                phrase=spec.phrase,
                action=spec.action,
                risk=spec.risk,
                category=spec.category,
                variables=variables,
            )
        return None

    def suggestions(self, text: str, limit: int = 3) -> list[str]:
        """Closest registry phrases, for the 'did you mean?' reply only.

        Suggestions are never executed automatically.
        """
        value = normalize(text)
        phrases = [spec.phrase for spec in self.specs]
        return difflib.get_close_matches(value, phrases, n=limit, cutoff=0.6)

    def grammar_phrases(self) -> list[str]:
        """Phrases for a grammar-constrained recogniser (Vosk).

        Variable phrases cannot be fully constrained, so they are
        represented by their trigger words plus, for numbers, the
        common 0-100 steps. Free text is handled in dictation mode
        (see voice.py), never as a command.
        """
        phrases: list[str] = []
        for spec in self.specs:
            if "<number>" in spec.phrase:
                for step in (0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100):
                    phrases.append(spec.phrase.replace("<number>", str(step)))
            elif "<text>" in spec.phrase or "<file>" in spec.phrase:
                trigger = re.split(r"<", spec.phrase)[0].strip()
                if trigger and trigger not in phrases:
                    phrases.append(trigger)
            elif "<website>" in spec.phrase:
                phrases.append(spec.phrase.replace("<website>", "example"))
            else:
                phrases.append(spec.phrase)
        return sorted(set(phrases))
