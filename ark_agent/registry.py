"""Load commands.json and compile each phrase into a match pattern.

A phrase may contain one spoken variable:
  <text>    any non-empty text, e.g. "type hello world and press enter"
  <number>  digits only, checked against NUMBER_RANGES in config.py
  <website> a single host-like word, e.g. "open website example.com"
  <file>    any non-empty text, e.g. "search for file report"

Patterns without variables are tried before patterns with variables,
and longer patterns before shorter ones, so "close current tab" wins
over a shorter, vaguer match.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandSpec:
    phrase: str
    action: str
    risk: str
    category: str
    pattern: re.Pattern
    has_variable: bool


def _phrase_to_regex(phrase: str) -> re.Pattern:
    parts = re.split(r"(<text>|<number>|<website>|<file>)", phrase)
    out = []
    for part in parts:
        if part == "<text>":
            out.append(r"(?P<text>.+)")
        elif part == "<number>":
            out.append(r"(?P<number>\d+)")
        elif part == "<website>":
            out.append(r"(?P<website>[A-Za-z0-9.\-]+)")
        elif part == "<file>":
            out.append(r"(?P<file>.+)")
        else:
            out.append(re.escape(part))
    return re.compile("^" + "".join(out) + "$")


def load_commands(path: Path | None = None) -> list[CommandSpec]:
    if path is None:
        path = Path(__file__).resolve().parent.parent / "commands.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    specs = []
    for entry in raw:
        phrase = entry["phrase"]
        specs.append(
            CommandSpec(
                phrase=phrase,
                action=entry["action"],
                risk=entry["risk"],
                category=entry.get("category", ""),
                pattern=_phrase_to_regex(phrase),
                has_variable=("<" in phrase),
            )
        )
    # Exact patterns first, then variable patterns; longest first.
    specs.sort(key=lambda s: (s.has_variable, -len(s.phrase)))
    return specs


def find_duplicates(specs: list[CommandSpec]) -> list[str]:
    seen: set[str] = set()
    dupes: list[str] = []
    for spec in specs:
        if spec.phrase in seen:
            dupes.append(spec.phrase)
        seen.add(spec.phrase)
    return dupes
