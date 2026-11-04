# Changelog

## v2.0 — Ultra-intelligent tasks + web GUI + Vosk performance (2026-11-04)

Built from the v1.1 GUI voice test, where Chrome, VS Code,
Notepad, PowerShell, Word and This PC worked, but some phrases
were misheard, dictation got stuck on, and "set brightness level
to 50" / "create a blank page in ms word" were not recognised.

- **Vosk performance, without changing the offline model:**
  - Vosk now returns up to 3 alternatives per utterance, and
    the agent tries each alternative through the intelligent
    parser. A top transcript of "open crome" is recovered by
    the second alternative "open chrome".
  - Listening timeout raised from 10 to 30 seconds, so long
    task sentences are not cut off. Short commands still end
    early on silence.
  - Recommended model changed to **vosk-model-en-us-0.22
    (about 128 MB)** for heavy daily use. The small 0.15 model
    still works, but 0.22 hears longer sentences and accents
    better. Both are offline, CPU-only, and no cloud.
  - Dictation can never get stuck: "stop dictation please"
    also exits, the web UI shows a Dictation ON banner with
    a Stop button, and dictation text is never executed.
- **Tasks, not just single actions:**
  - "open chrome and search for cats" shows a 2-step plan
    and runs it. "create a word document and type hello"
    shows a 3-step plan. "set up my work" opens Chrome,
    VS Code and Spotify. Any multi-command sentence is a
    task. A failing step stops the task and names the step.
  - Task plans are shown in the web UI before running, and
    printed in the text loop before running. Dangerous steps
    still ask yes/no.
- **Longer, more human sentences:**
  - More paraphrases: brightness/volume "level", "open
    windows settings", "create a blank page in ms word",
    "show me / bring up / turn on" verbs, and "then / after
    that / ," clause splitting.
  - Yes/no answers accept "yeah", "yep", "sure", "yes
    please" and "yese" — but "yeah not sure" stays ambiguous
    and never executes (a test caught this regression).
  - A single vague word like "page" no longer suggests
    "page up". It is simply not a command.
- **Web GUI, not a hard Tkinter face:**
  - `run_web.bat` / `python -m ark_agent.main --web` opens
    http://127.0.0.1:8765 — a modern dark web interface with
    a CSS-animated character (blinking, talking mouth,
    spinning working gear), chat log, task-plan panel,
    suggestion Yes/No bar, quick actions, command search,
    and settings (Vosk model + default browser, saved to
    arkagent_config.json). Server is stdlib-only, local-only.
  - Tkinter GUI remains as a fallback (`--gui`).
- **Tests grew from 51 to 71**, with new task, web-API and
  voice-v2 suites. Web tests run a real HTTP server on an
  ephemeral port.

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
