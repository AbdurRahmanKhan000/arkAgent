# arkAgent — Fixed-Command Laptop Agent (No LLM)

A small, fast, offline laptop agent for Windows. You speak or type a
command, it does exactly that command — nothing more, nothing guessed.

**418 commands in v1**, including apps, browsers, IDEs, Windows
settings, files, volume/media, power, screenshots, and a large
Microsoft Word / Excel / PowerPoint / Outlook set. See `commands.md`
for the full registry, and `commands.json` for the machine-readable
version the code actually loads.

## Why no LLM?

An LLM would add gigabytes of RAM, seconds of delay, and wrong
guesses. A fixed registry is the opposite: ~100–200 MB install,
sub-second commands, and a clear "I do not recognise that command"
instead of a wrong action. That is the trade-off this project makes
on purpose, for heavy daily voice use.

## What you get

- **Text + voice, one parser** (`ark_agent/parser.py`). If it works
  typed, it works spoken.
- **Voice that is hard to fool** (`ark_agent/voice.py`):
  - Command mode: grammar-constrained Vosk, only registry phrases.
  - Dictation mode: after "start dictation", speech is typed only
    and never executed as a command. "stop dictation" exits.
  - Low-confidence results are not executed; the agent asks you
    to repeat and shows what it heard.
  - Push-to-talk by default, so TV and background speech do not
    trigger it. Wake-word (openWakeWord) is a future add-on, not v1.
- **Professional GUI + cartoon character** (`ark_agent/gui.py`,
  `ark_agent/character.py`): dark interface, command log, search,
  and a canvas-drawn character that blinks idle, raises its ears
  when listening, turns a gear when working, opens its mouth when
  speaking, smiles on success, and looks worried on error.
- **Safe actions** (`ark_agent/actions.py`): allowlist only, fixed
  argument lists, no shell, no user text as a command, protected
  processes (including explorer.exe) can never be closed, and
  close / shutdown / delete / send-email always ask "yes or no"
  first, with a 60-second expiry.

## Project structure

```
arkAgent/
  commands.md            418-command registry (human-readable)
  commands.json          same registry, loaded by the code
  tools/generate_commands.py   regenerates commands.md
  ark_agent/
    parser.py            normalise + synonyms + registry matching
    registry.py          commands.json -> match patterns
    config.py            app / website / settings mappings, synonyms
    actions.py           safe handlers + confirmation manager
    voice.py             Vosk command + dictation modes
    tts.py               OS voice (SAPI on Windows)
    character.py         animated character state machine
    gui.py               Tkinter professional interface
    main.py              CLI: --gui / --text / --check / --list-commands
  tests/                 parser, actions, security, registry, voice, character
  requirements.txt
  run_gui.bat / run_text.bat   (Windows launchers)
```

## Install on Windows

1. Install Python 3.10+ from python.org, ticking "Add python.exe
   to PATH" during install.
2. Unzip this project, open a terminal in the `arkAgent` folder:
   ```
   python -m pip install -r requirements.txt
   ```
3. Voice model (voice mode only, text mode needs none of this):
   download `vosk-model-small-en-us` from the official Vosk models
   page, unzip it, and note its folder path. If accuracy is poor
   in noise, try the medium English model instead — it is larger
   but still far smaller than any LLM.
4. Tell the code where the model is. The simplest v1 way is to
   pass it in code when creating `VoiceEngine(model_path=...)`,
   or set it in `gui.py` before launch. The GUI will otherwise
   show a clear "model not set" message instead of crashing.

## Run it — safest order

Test in this order, so a mistake costs nothing:

```
REM 1. Dry run: see what it WOULD do, without doing it
python -m ark_agent.main --text --dry-run

REM 2. Real text mode
python -m ark_agent.main --text

REM 3. Professional GUI
python -m ark_agent.main --gui
REM or double-click run_gui.bat
```

Try, in order: `open notepad`, `set volume to 50 percent`,
`open chrome`, `close chrome` (it will ask yes/no — say `yes`).

## Self-check and tests

```
python -m ark_agent.main --check
python -m unittest discover -s tests
REM or: python -m pytest tests/
```

`--check` verifies: at least 300 commands, no duplicates, and
every registered action has a handler. The test suite covers the
parser, actions, security (no shell, protected processes),
registry agreement between `commands.md` and `commands.json`,
voice modes and confidence, and the character state machine.

## Voice tips for heavy use

- Use push-to-talk in a quiet room, with the mic close to you.
- Say the canonical phrase from `commands.md` at first. The
  synonym list covers common variants (VS Code, IntelliJ, notebook),
  but it does not guess new ones.
- If a phrase is repeatedly misheard, add it as a synonym in
  `config.py`, add the phrase to `commands.md` / `commands.json`,
  and add a test in `tests/test_parser.py`. Never widen the
  grammar to "any English" — that is what destroys accuracy.
- For long typing, say "start dictation", dictate, then
  "stop dictation". Dictated text is never executed as a command.

## Custom apps: arkmedia, arksnap, arkdownload

These are in the registry, but their real `.exe` names must be
filled in in `config.py` (`APP_EXECUTABLES`) once those apps are
installed. Until then the agent reports "not found" instead of
guessing a path.

## Uploading this to GitHub (arkAgent)

You already chose the repo name `arkAgent`. From the unzipped
folder, on a terminal with Git installed:

```
git init
git add .
git commit -m "arkAgent v1: fixed-command agent, 418 commands, voice + GUI + tests"
git branch -M main
git remote add origin https://github.com/AbdurRahmanKhan000/arkAgent.git
git push -u origin main
```

If the repo already exists on GitHub and is empty, the same
commands work. If it is not empty, clone it first, copy these
files in, then add / commit / push.

## Known limits (honest v1 limits)

- Windows-first. On Linux/macOS the code runs in dry-run / report
  mode for Windows actions; it does not pretend to have acted.
- Word/Excel actions that need a focused document use keyboard
  shortcuts and need the right app in focus. They are not AI
  vision or document editing — they are fixed shortcuts.
- Voice accuracy depends on mic, noise, and the Vosk model size.
  The grammar design reduces errors, it does not remove them.
  That is why confirmations, logs, and the "did you mean?" reply
  exist.
- The GUI was logic-tested here; the live Windows GUI, mic, and
  speaker must be tested on your laptop before daily use. Run
  the dry-run first, then one safe command at a time.
