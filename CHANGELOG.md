# Changelog

## v1.1 — Intelligence and professionalism (2026-11-04)

Fixed from real v1 testing on Windows, where only Notepad worked:

- **App discovery on any drive.** v1 only used PATH, so Notepad
  worked (System32 is in PATH) and Chrome/Brave failed (they live
  in Program Files / AppData, not PATH). v1.1 searches, in order:
  arkagent_config.json override, PATH, Windows App Paths registry,
  known vendor folders on every drive (C:, D:, E:, F:, ...), then
  a shallow scan of drive roots for portable apps.
- **Special system targets now work.** "open this pc" and
  "open recycle bin" failed in v1 because they are not .exe
  files. They now open their shell locations, and Settings,
  File Explorer, Control Panel, Task Manager etc. are handled
  as system targets, not as missing executables.
- **Daily sentences.** "please open chrome for me", "can you
  launch notepad?", "turn the sound off", "set volume to
  fifty percent", and "open chrome and open notepad" now work.
  Safe typos are auto-corrected and logged ("Understood as:
  open chrome"). Close matches ask "Did you mean: X?" with
  Yes/No. Dangerous commands are never auto-corrected.
- **"yes" only works after a question.** In v1, typing "yes"
  after a failed command confusingly replied "I do not
  recognise that command". v1.1 explains this in the loop:
  yes/no only answer a pending confirmation or a
  "Did you mean?" question.
- **GUI is now the main interface.** Header, status pill,
  quick-action buttons, command search, and a settings panel
  that saves the Vosk model folder and default browser to
  arkagent_config.json — no code editing needed for voice.
  The cartoon character states are unchanged.
- **Clearer errors.** "Program not found on this PC: chrome.exe.
  Is chrome installed?" is replaced with a message listing
  where it searched and how to add a custom path.
- **Tests grew from 36 to 51**, with new discovery,
  intelligence, and user-config suites. Two discovery tests
  initially failed (a Windows/Linux path separator bug and a
  mock target bug) and were fixed before delivery.

## v1.0 — First build (2026-11-04)

418 commands, fixed parser, Vosk command/dictation modes,
Tkinter GUI with animated character, 36 tests, self-check.
