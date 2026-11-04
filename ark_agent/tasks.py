"""Multi-step task planner for arkAgent v2 — automation, not just
one action per command.

A "task" is a goal the user states in one sentence, which the agent
breaks into a short, visible plan of registry commands, then runs
step by step. Every step is still a registry command, so every step
is still allowlisted, still confirm-gated if it is dangerous, and
still logged. If a step fails, the task stops and reports exactly
which step failed — it does not silently skip to the next step.

Task templates (pattern -> steps, with <...> filled from speech):
- "open chrome and search for <query>"
  -> open chrome, type <query> and press enter (in the address bar)
- "open youtube and search for <query>"
  -> open youtube, search for <query>
- "open notepad, type <text>, and save it as <file>"
  -> open notepad, type <text> and press enter, save document as
     (the save dialog step is a keyboard step; the user types the
     name if the dialog needs it — see the plan before confirming)
- "create a word document, type <text>, and save it"
  -> open microsoft word, create new word document, type <text>
- "set up my work" / "start my work"
  -> open chrome, open visual studio code, open spotify
- "create a folder named <name> on desktop"
  -> open desktop folder, create new folder (then rename in the UI)
- "open chrome, open youtube, and play <query>"
  -> open chrome, open youtube, search for <query>

Anything that does not match a template falls back to the
multi-command splitter in intelligence.py ("open A and open B").
Anything that matches neither is not a task — the agent says so,
instead of inventing steps.

The web GUI shows the plan before running it for confirm-gated
tasks. The text loop prints the plan and asks yes/no for any
confirm step, exactly as for single commands.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .intelligence import IntelligentParser
from .parser import ParsedCommand


@dataclass
class TaskPlan:
    title: str
    steps: list[str] = field(default_factory=list)  # canonical command strings
    description: str = ""

    @property
    def step_count(self) -> int:
        return len(self.steps)


# Each template: (regex, title template, step templates)
_TEMPLATES: list[tuple[str, str, list[str]]] = [
    (
        r"open chrome and search for (.+)",
        "Search in Chrome for '{0}'",
        ["open chrome", "search for {0}"],
    ),
    (
        r"open youtube and search for (.+)",
        "Search YouTube for '{0}'",
        ["open youtube", "search for {0}"],
    ),
    (
        r"open youtube and play (.+)",
        "Play '{0}' on YouTube",
        ["open youtube", "search for {0}"],
    ),
    (
        r"open notepad,? type (.+?),? and save it as (.+)",
        "Notepad note saved as '{1}'",
        ["open notepad", "type {0} and press enter", "save document as"],
    ),
    (
        r"create a word document,? type (.+)",
        "Word document with '{0}'",
        ["open microsoft word", "create new word document", "type {0} and press enter"],
    ),
    (
        r"create a word document and type (.+)",
        "Word document with '{0}'",
        ["open microsoft word", "create new word document", "type {0} and press enter"],
    ),
    (
        r"(?:set up my work|start my work|start work)",
        "Set up work: browser, IDE and music",
        ["open chrome", "open visual studio code", "open spotify"],
    ),
    (
        r"create a folder named (.+?) on desktop",
        "Create folder '{0}' on Desktop",
        ["open desktop folder", "create new folder"],
    ),
    (
        r"open chrome,? open youtube,? and play (.+)",
        "Play '{0}' on YouTube",
        ["open chrome", "open youtube", "search for {0}"],
    ),
    (
        r"take a screenshot and open it",
        "Screenshot",
        ["take screenshot"],
    ),
]


class TaskPlanner:
    def __init__(self, smart: IntelligentParser | None = None):
        self.smart = smart if smart is not None else IntelligentParser()

    def plan(self, text: str) -> TaskPlan | None:
        """Return a plan for a task sentence, or None if it is not a task."""
        value = " ".join(text.strip().lower().split()).rstrip(".!?")
        # Strip the same leading politeness as the intelligent parser.
        for filler in ("please ", "can you ", "could you ", "ark "):
            if value.startswith(filler):
                value = value[len(filler):].strip()
        for pattern, title_template, step_templates in _TEMPLATES:
            match = re.fullmatch(pattern, value)
            if match:
                groups = [g.strip() for g in match.groups()]
                title = title_template
                for i, group in enumerate(groups):
                    title = title.replace(f"{{{i}}}", group)
                steps = []
                for template in step_templates:
                    step = template
                    for i, group in enumerate(groups):
                        step = step.replace(f"{{{i}}}", group)
                    steps.append(step)
                return TaskPlan(title=title, steps=steps, description=f"Task: {title} ({len(steps)} steps)")
        # Fallback: multi-command sentence is a task with one step each.
        resolved = self.smart.resolve(text)
        if resolved.method == "multi" and len(resolved.commands) >= 2:
            # understood_as is the actual clause text for each part
            # ("search for cats", not the "search for <text>" template).
            return TaskPlan(
                title=resolved.understood_as,
                steps=[part.strip() for part in resolved.understood_as.split(" + ")],
                description="Multi-command task",
            )
        return None

    def plan_to_commands(self, plan: TaskPlan) -> list[ParsedCommand]:
        """Resolve every step string back through the intelligent parser.

        A step that does not resolve is kept out, and the caller must
        report it — a task must never run a step it cannot explain.
        """
        commands: list[ParsedCommand] = []
        for step in plan.steps:
            resolved = self.smart.resolve(step)
            if resolved.commands:
                commands.append(resolved.commands[0])
        return commands
