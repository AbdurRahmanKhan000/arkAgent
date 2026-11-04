# Self-review — arkAgent v1

Reviewer: Muse, before delivery. This file is the verification
record. It does not claim the agent is error-free on Windows —
it records exactly what was tested, what failed, what was fixed,
and what still needs testing on the user's laptop.

## 1. Tests run (this machine, Linux, Python 3.12)

```
python -m unittest discover -s tests
Ran 36 tests — OK

python -m ark_agent.main --check
SELF-CHECK OK: 418 commands, 241 handlers, no duplicates.
```

Coverage by level:
- Parser: exact, case/filler, synonyms, text/number variables,
  out-of-range rejection, unknown rejection, Word phrases,
  suggestions-never-execute.
- Actions: dry-run success, confirm gating, yes/no/ambiguous
  answers, time telling.
- Security: source scan for os.system / shell=True / eval / exec
  (clean), protected-process denial, dictated text never run
  as a command.
- Registry: >=400 commands, no duplicates, commands.md and
  commands.json agree, every action has a handler, every
  command has a category and a risk level.
- Voice: command mode, unknown rejection, dictation mode
  never executing commands, low-confidence blocking, Vosk
  JSON parsing, grammar includes core commands and no
  variable placeholders.
- Character: all states have messages, speaking mouth
  animates, working gear turns, idle/listening states,
  unknown state falls back to idle.

## 2. Bugs found by the tests, and fixed

1. **Synonym double-expansion.** "open intelligi" became
   "open intellij idea idea" because "intellij" was then
   expanded again. Fixed: removed the overlapping synonym
   and added an explicit "open intellij" case.
2. **Word suffix broken by a synonym.** "bold selected text
   in word" was normalised to "... in microsoft word" and
   stopped matching. Fixed: removed the generic word/excel/
   powerpoint synonyms (only "ms word" etc. remain, which
   do not collide with "in word" phrases).
3. **Missing handler.** `word_insert_table` was registered
   but had no handler, so --check failed. Fixed: added it
   to the generic Word handler table.

After these fixes, all 36 tests and the self-check pass.
A live text-loop smoke test was also run in dry-run mode:
open chrome, open intelligi, set volume to 50 percent,
type hello world and press enter, close chrome + yes —
all produced the expected dry-run / confirmation output.

## 3. Manual code review checks

- [x] No user text reaches a subprocess argument list.
- [x] No shell, eval, or exec in ark_agent/*.py (grep-checked).
- [x] Confirmations are request-bound, expiring (60 s), and
  ambiguous answers ("yeah not sure") do not execute.
- [x] Protected processes denied even after confirmation.
- [x] Dry-run results are labelled "[dry-run]" everywhere.
- [x] Voice dictation cannot execute commands.
- [x] Low-confidence voice results are not executed.
- [x] Character logic is display-independent and unit-tested.

## 4. What was NOT tested here (must test on your laptop)

- Live Windows execution: launching/closing real apps,
  volume via pycaw, Word shortcuts in a focused document.
- Live microphone + Vosk model + speaker, in your room,
  with your voice and accent.
- Live Tkinter GUI window (character logic tested, window
  rendering needs a Windows desktop).
- arkmedia / arksnap / arkdownload, whose .exe paths are
  not yet filled in (see README).

## 5. Recommended first-run checklist on your laptop

1. `python -m ark_agent.main --text --dry-run` — try 10 commands.
2. `python -m ark_agent.main --text` — try only safe commands.
3. `python -m ark_agent.main --gui` — check the character
   animates: idle -> listening -> working -> speaking.
4. Voice: one push-to-talk command, then dictation on/off.
5. Only then: confirm-gated commands (close, shutdown) — and
   never test shutdown first.
