"""arkAgent command line.

Usage (from the arkAgent folder):
  python -m ark_agent.main --gui            professional GUI + character
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
from .parser import Parser
from .registry import find_duplicates, load_commands
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


def text_loop(dry_run: bool = False) -> int:
    parser = Parser()
    executor = ActionExecutor(dry_run=dry_run)
    speaker = Speaker(enabled=True)
    print("arkAgent (text mode). Type a command, 'exit' to quit.")
    print("Confirmations: answer 'yes' or 'no' when asked.")
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return 0
        if text.lower() in ("exit", "quit"):
            print("Goodbye.")
            return 0
        if executor.confirmations.pending is not None:
            result = executor.confirm_pending(text)
            print(result.message)
            speaker.speak(result.message)
            continue
        parsed = parser.parse(text)
        if parsed is None:
            suggestions = parser.suggestions(text)
            message = "I do not recognise that command."
            if suggestions:
                message += f" Did you mean: {', '.join(suggestions)}?"
            print(message)
            speaker.speak(message)
            continue
        result = executor.execute(parsed)
        print(result.message)
        speaker.speak(result.message)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = argparse.ArgumentParser(prog="arkAgent")
    args.add_argument("--gui", action="store_true", help="Open the professional GUI")
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
    if parsed_args.gui:
        from .gui import run_gui

        run_gui(dry_run=parsed_args.dry_run)
        return 0
    return text_loop(dry_run=parsed_args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
