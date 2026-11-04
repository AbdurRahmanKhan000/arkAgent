# Self-review — arkAgent v2

Reviewer: Muse, before delivery. This file is the verification
record. It does not claim the agent is error-free on Windows —
it records exactly what was tested, what failed, what was fixed,
and what still needs testing on the user's laptop.

## v2 review (this machine, Linux, Python 3.12)

```
python -m unittest discover -s tests
Ran 71 tests — OK

python -m ark_agent.main --check
SELF-CHECK OK: 418 commands, 241 handlers, no duplicates.

Text dry-run verified:
  "open chrome and search for cats"
    -> Task: Search in Chrome for 'cats' (2 steps, both dry-run OK)
  "create a word document and type hello world"
    -> Task: Word document with 'hello world' (3 steps, dry-run OK)
  "set brightness level to 50"
    -> Understood as: set brightness to 50 percent (v1.1 failure, fixed)
  "page"
    -> I do not recognise that command (no more "page up" suggestion)
```

What failed during v2 development, and was fixed before delivery:
- Two tests failed on first run: "yeah not sure" was counted as
  yes (ConfirmationManager first-word logic). Fixed by checking
  ambiguous phrases ("not sure", "maybe", "i don't know") before
  the first-word rule. Both the old action test and the new
  voice-v2 test now pass.
- Web test helper contained a broken unused function; removed.
- Web UI files and server were tested with a real HTTP server
  on an ephemeral port (status, command, task plan + execution,
  suggestion yes/no, unknown).

What v2 does NOT claim:
- Vosk accuracy on the user's voice, accent, mic and room is
  still only measurable on their laptop. v2 improves the odds
  (alternatives, 30-second listening, 0.22 model recommendation),
  but it cannot promise perfect recognition.
- Web UI rendering and mic capture in their browser, and real
  Word/Chrome automation steps on Windows, still need live
  testing. Dry-run proves the plan logic, not Windows GUI steps.
- A task plan is not a guarantee: if a step's app is missing
  or a dialog needs manual input (e.g. a Save As filename),
  the task stops and reports the step — it does not invent one.

---

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

## v1.1 addendum — review after real Windows testing

Real v1 failures reproduced from the user's screenshots:
- "open browser" / "open chrome" / "open brave": PATH-only search.
- "open this pc": no executable mapping, because it is a shell folder.
- "yes" after a failed command: confusing, because no confirmation was pending.

Fixes verified here (Linux, plus a fake-drive test):
- 51 tests pass (was 36), self-check OK: 418 commands, 241 handlers.
- Fake-drive discovery test: Chrome found under a non-C: drive layout.
- Text-loop smoke test in dry-run: "please open chrome for me",
  "open this pc", "open chrome and open notepad",
  "set volume to fifty percent", and "clise chrome" -> asks
  "Did you mean: close chrome?" and "no" correctly cancels.
- Two new discovery tests failed on first run and were fixed:
  a backslash path bug that only shows on Linux, and a mock
  target for the default-browser helper.

Still NOT tested here, and still needing the user's Windows run:
- Real Chrome/Brave on C:/F:/E: drives, real This PC / Recycle Bin
  shell opens, real Tkinter GUI window, real microphone + Vosk.
  The v1.1 code paths for those are in place, but only a Windows
  run can prove them.
