"""arkAgent command line.

Usage (from the arkAgent folder):
  python -m ark_agent.main --web             modern web interface (v2 primary)
  python -m ark_agent.main --gui            Tkinter GUI (fallback)
  python -m ark_agent.main --text           typed-command loop
  python -m ark_agent.main --text --dry-run safe testing, no real actions
  python -m ark_agent.main --check           registry + handler self-check
  python -m ark_agent.main --list-commands   print all 418+ commands

The text loop is the reference implementation: the GUI calls the
same Parser and ActionExecutor, so a command that works here works
in the GUI and in voice mode.
"""
from __future__ import annotations

import argparse
import sys

from .actions import ActionExecutor
from .intelligence import IntelligentParser
from .parser import Parser
from .registry import find_duplicates, load_commands
from .tasks import TaskPlanner
from .tts import Speaker


def self_check() -> int:
    """Return 0 if the registry is sound, 1 otherwise."""
    specs = load_commands()
    problems: list[str] = []
    if len(specs) < 300:
        problems.append(f"Only {len(specs)} commands, expected at least 300.")
    dupes = find_duplicates(specs)
    if dupes:
        problems.append(f"Duplicate phrases: {dupes[:10]}")
    executor = ActionExecutor(dry_run=True)
    handlers = executor._handlers()
    missing = sorted({s.action for s in specs} - set(handlers))
    if missing:
        problems.append(f"Actions without handlers: {missing}")
    if problems:
        print("SELF-CHECK FAILED")
        for problem in problems:
            print(f" - {problem}")
        return 1
    print(f"SELF-CHECK OK: {len(specs)} commands, {len(handlers)} handlers, no duplicates.")
    return 0


def _run_commands(executor: ActionExecutor, speaker: Speaker, commands) -> None:
    """Execute resolved commands, honouring confirmations per command."""
    for command in commands:
        result = executor.execute(command)
        print(result.message)
        speaker.speak(result.message)
        if result.needs_confirmation:
            try:
                answer = input("yes/no> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nCancelled.")
                return
            confirm_result = executor.confirm_pending(answer)
            print(confirm_result.message)
            speaker.speak(confirm_result.message)


def text_loop(dry_run: bool = False) -> int:
    parser = Parser()
    smart = IntelligentParser(parser)
    planner = TaskPlanner(smart)
    executor = ActionExecutor(dry_run=dry_run)
    speaker = Speaker(enabled=True)
    print("arkAgent v2.0 (text mode). Type a task or command, 'exit' to quit.")
    print("Daily sentences work too: 'please open chrome for me',")
    print("'open chrome and open notepad', 'set volume to fifty percent'.")
    print("Confirmations: answer 'yes' or 'no' when asked.")
    pending_suggestion: str | None = None
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return 0
        if text.lower() in ("exit", "quit"):
            print("Goodbye.")
            return 0
        # A "yes" after a "Did you mean?" question runs that suggestion.
        # A "yes" with no question waiting is not a command (v1 lesson).
        if pending_suggestion is not None:
            if text.lower() in ("yes", "confirm", "do it"):
                suggestion = pending_suggestion
                pending_suggestion = None
                parsed = parser.parse(suggestion)
                if parsed is not None:
                    _run_commands(executor, speaker, [parsed])
                continue
            pending_suggestion = None
            if text.lower() in ("no", "cancel"):
                print("OK, not running that.")
                continue
        if executor.confirmations.pending is not None:
            result = executor.confirm_pending(text)
            print(result.message)
            speaker.speak(result.message)
            continue
        # v2: a multi-step task gets a visible plan before it runs.
        plan = planner.plan(text)
        if plan is not None and len(plan.steps) >= 2:
            print(f"Task: {plan.title}")
            for i, step in enumerate(plan.steps, start=1):
                print(f"  {i}. {step}")
            task_commands = planner.plan_to_commands(plan)
            if len(task_commands) < len(plan.steps):
                print("Warning: one task step could not be understood and will be skipped.")
            _run_commands(executor, speaker, task_commands)
            continue
        resolved = smart.resolve(text)
        if resolved.method == "ask" and resolved.suggestion:
            pending_suggestion = resolved.suggestion
            message = f"Did you mean: {resolved.suggestion}? Say yes or no."
            print(message)
            speaker.speak(message)
            continue
        if not resolved.commands:
            message = "I do not recognise that command."
            print(message)
            speaker.speak(message)
            continue
        if resolved.method in ("paraphrase", "fuzzy"):
            print(f"Understood as: {resolved.understood_as}")
        if resolved.method == "multi":
            print(f"Running {len(resolved.commands)} commands: {resolved.understood_as}")
        _run_commands(executor, speaker, resolved.commands)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = argparse.ArgumentParser(prog="arkAgent")
    args.add_argument("--gui", action="store_true", help="Open the Tkinter GUI (fallback)")
    args.add_argument("--web", action="store_true", help="Open the modern web interface (v2 primary)")
    args.add_argument("--text", action="store_true", help="Typed-command loop")
    args.add_argument("--dry-run", action="store_true", help="Report actions without running them")
    args.add_argument("--check", action="store_true", help="Registry and handler self-check")
    args.add_argument("--list-commands", action="store_true", help="Print every command")
    parsed_args = args.parse_args(argv)
    if parsed_args.check:
        return self_check()
    if parsed_args.list_commands:
        for spec in load_commands():
            print(f"{spec.phrase}  [{spec.category} | {spec.action} | {spec.risk}]")
        return 0
    if parsed_args.web:
        from .web_server import run_server

        run_server(dry_run=parsed_args.dry_run, open_browser=True)
        return 0
    if parsed_args.gui:
        from .gui import run_gui

        run_gui(dry_run=parsed_args.dry_run)
        return 0
    return text_loop(dry_run=parsed_args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
