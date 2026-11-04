"""Daily-language understanding for arkAgent — still no LLM.

v1 only understood exact registry phrases. Real daily speech is
messier: "please open chrome for me", "can you launch notepad?",
"turn the sound off", "clise chrome" (a typo), "open chrome and
open notepad". v1.1 adds a small, explainable intelligence layer
on top of the strict parser:

1. Paraphrase normalisation: polite fillers, verb synonyms
   (launch/start/run -> open, exit/quit -> close), articles,
   and "go to X" -> "open X". Then the strict parser runs.
2. Number words: "set volume to fifty percent" -> 50.
3. Typo auto-correction, but only when it is safe:
   - Safe commands, best match >= 0.85 and clearly better than
     the second-best match: auto-execute, and log what was
     understood ("Understood as: close chrome").
   - Anything else with a close match: ask "Did you mean X?"
     and wait for yes/no. Never auto-execute a guess.
   - Dangerous / confirm commands are NEVER auto-corrected.
     A typo of "shut down computer" must be confirmed with
     its exact phrase, or it does not run.
4. Multi-command sentences: "open chrome and open notepad"
   splits only if every part parses on its own. Otherwise the
   whole sentence is treated as one command and rejected
   cleanly if it does not match.

The strict Parser.parse() is unchanged and still used for the
final match, so every executed action is still a registry action.
"""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field

from .parser import Parser, ParsedCommand, normalize

_ONES = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19,
}
_TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}

_LEADING_FILLERS = (
    "hey ark ", "ark ", "please ", "kindly ", "can you please ",
    "could you please ", "can you ", "could you ", "would you ",
    "i want to ", "i would like to ", "i need to ", "just ",
)


def words_to_number(text: str) -> str:
    """Replace spoken numbers with digits, outside 'type ...' text."""
    if text.strip().lower().startswith("type "):
        return text
    tokens = text.split()
    out: list[str] = []
    i = 0
    while i < len(tokens):
        token = tokens[i].lower().strip(",")
        if token in _TENS and i + 1 < len(tokens) and tokens[i + 1].lower() in _ONES:
            out.append(str(_TENS[token] + _ONES[tokens[i + 1].lower()]))
            i += 2
        elif token in _TENS:
            out.append(str(_TENS[token]))
            i += 1
        elif token in _ONES:
            out.append(str(_ONES[token]))
            i += 1
        elif token == "a" and i + 1 < len(tokens) and tokens[i + 1].lower() == "hundred":
            out.append("100")
            i += 2
        else:
            out.append(tokens[i])
            i += 1
    return " ".join(out)


def normalize_daily(text: str) -> str:
    """Turn a daily sentence into a registry-shaped sentence."""
    value = " ".join(text.strip().lower().split()).rstrip(".!?")
    # Specific volume / sound paraphrases first, before generic verbs.
    replacements = [
        ("turn the sound off", "mute volume"),
        ("turn sound off", "mute volume"),
        ("turn the sound on", "unmute volume"),
        ("turn sound on", "unmute volume"),
        ("turn the volume up", "volume up"),
        ("turn up the volume", "volume up"),
        ("turn the volume down", "volume down"),
        ("turn down the volume", "volume down"),
        ("make the volume ", "set volume to "),
        ("set the volume to ", "set volume to "),
        ("increase the volume", "volume up"),
        ("decrease the volume", "volume down"),
        ("scroll down a bit", "scroll down a little"),
        ("scroll up a bit", "scroll up a little"),
    ]
    for old, new in replacements:
        value = value.replace(old, new)
    changed = True
    while changed:
        changed = False
        for filler in _LEADING_FILLERS:
            if value.startswith(filler):
                value = value[len(filler):].strip()
                changed = True
    # Trailing politeness.
    for suffix in (" for me", " please", " now"):
        if value.endswith(suffix):
            value = value[: -len(suffix)].strip()
    # Verb synonyms, only at the start of the sentence.
    for old, new in (
        ("launch ", "open "), ("start ", "open "), ("run ", "open "),
        ("open up ", "open "), ("exit ", "close "), ("quit ", "close "),
        ("go to ", "open "),
    ):
        if value.startswith(old):
            value = new + value[len(old):]
            break
    # "close the chrome browser" -> "close chrome"
    if value.startswith(("open ", "close ")):
        verb, _, rest = value.partition(" ")
        tokens = [t for t in rest.split() if t not in ("the", "my", "a", "an")]
        if tokens and tokens[-1] in ("browser", "app", "application", "program"):
            tokens = tokens[:-1]
        value = f"{verb} {' '.join(tokens)}"
    return words_to_number(value)


@dataclass
class ResolvedCommand:
    commands: list[ParsedCommand] = field(default_factory=list)
    method: str = "none"  # exact | paraphrase | fuzzy | multi | ask | none
    confidence: float = 0.0
    understood_as: str = ""
    suggestion: str = ""
    original: str = ""


class IntelligentParser:
    """Wraps Parser with paraphrase, fuzzy and multi-command logic."""

    def __init__(self, parser: Parser | None = None):
        self.parser = parser if parser is not None else Parser()

    def _fuzzy_best(self, text: str) -> tuple[str, float, float]:
        """Best and second-best registry phrase, by similarity."""
        candidates = [
            spec.phrase for spec in self.parser.specs if "<" not in spec.phrase
        ]
        scored = sorted(
            ((difflib.SequenceMatcher(None, text, phrase).ratio(), phrase) for phrase in candidates),
            reverse=True,
        )
        if not scored:
            return "", 0.0, 0.0
        best, best_score = scored[0][1], scored[0][0]
        second = scored[1][0] if len(scored) > 1 else 0.0
        return best, best_score, second

    def resolve(self, text: str) -> ResolvedCommand:
        original = text
        # 1. Exact.
        exact = self.parser.parse(text)
        if exact is not None:
            return ResolvedCommand([exact], "exact", 1.0, normalize(text), original=original)
        # 2. Paraphrase.
        daily = normalize_daily(text)
        if daily != " ".join(text.strip().lower().split()).rstrip(".!?"):
            parsed = self.parser.parse(daily)
            if parsed is not None:
                return ResolvedCommand([parsed], "paraphrase", 0.95, daily, original=original)
        # 3. Multi-command: only if every part resolves on its own.
        for separator in (" and then ", " and "):
            if separator in daily:
                parts = [p.strip() for p in daily.split(separator) if p.strip()]
                if len(parts) >= 2:
                    resolved_parts = [self.resolve(part) for part in parts]
                    if all(r.commands and r.method in ("exact", "paraphrase", "fuzzy") for r in resolved_parts):
                        commands = [r.commands[0] for r in resolved_parts]
                        return ResolvedCommand(
                            commands, "multi", 0.9,
                            " + ".join(r.understood_as for r in resolved_parts), original=original,
                        )
        # 4. Fuzzy: auto only for safe commands with a clear winner.
        best, best_score, second_score = self._fuzzy_best(daily)
        if best:
            parsed = self.parser.parse(best)
            if parsed is not None and not parsed.needs_confirmation:
                if best_score >= 0.85 and (best_score - second_score) >= 0.10:
                    return ResolvedCommand([parsed], "fuzzy", best_score, best, original=original)
            if best_score >= 0.70:
                return ResolvedCommand([], "ask", best_score, "", suggestion=best, original=original)
        return ResolvedCommand([], "none", 0.0, "", original=original)
