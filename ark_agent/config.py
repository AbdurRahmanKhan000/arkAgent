"""Static configuration for arkAgent.

No user speech is ever turned into a shell command here. App names map
to verified Windows executable names or Start-menu names. On other
platforms the executor runs in dry-run mode and reports what it would
do, instead of guessing a command.
"""
from __future__ import annotations

# Default choices. The user can change these in commands, e.g.
# "set default browser to edge" (handled as a config action in v1.1;
# in v1.0 the default below is used for the generic "open browser").
DEFAULT_BROWSER = "chrome"
DEFAULT_IDE = "visual studio code"

# Windows executable / Start-menu names. Keep this list short and
# explicit: an app that is not listed here cannot be launched.
APP_EXECUTABLES = {
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "brave": "brave.exe",
    "firefox": "firefox.exe",
    "opera": "opera.exe",
    "spotify": "spotify.exe",
    "whatsapp": "whatsapp.exe",
    "telegram": "telegram.exe",
    "discord": "discord.exe",
    "zoom": "zoom.exe",
    "microsoft teams": "ms-teams.exe",
    "vlc media player": "vlc.exe",
    "notepad": "notepad.exe",
    "calculator": "calculator.exe",
    "paint": "mspaint.exe",
    "visual studio code": "code.exe",
    "visual studio": "devenv.exe",
    "intellij idea": "idea64.exe",
    "pycharm": "pycharm64.exe",
    "webstorm": "webstorm64.exe",
    "android studio": "studio64.exe",
    "eclipse": "eclipse.exe",
    "dev c++": "devcpp.exe",
    "notepad++": "notepad++.exe",
    "python interpreter": "python.exe",
    "python idle": "idle.exe",
    "microsoft word": "winword.exe",
    "microsoft excel": "excel.exe",
    "microsoft powerpoint": "powerpnt.exe",
    "microsoft outlook": "outlook.exe",
    "microsoft onenote": "onenote.exe",
    # ARK apps: fill in the real .exe name once each app is installed.
    # Until then these are reported as "not installed", never guessed.
    "arkmedia": "arkmedia.exe",
    "arksnap": "arksnap.exe",
    "arkdownload": "arkdownload.exe",
}

WEBSITES = {
    "claude": "https://claude.ai",
    "gemini": "https://gemini.google.com",
    "grok": "https://grok.com",
    "chatgpt": "https://chatgpt.com",
    "copilot": "https://copilot.microsoft.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "google drive": "https://drive.google.com",
    "linkedin": "https://www.linkedin.com",
    "whatsapp web": "https://web.whatsapp.com",
    "stack overflow": "https://stackoverflow.com",
    "wikipedia": "https://www.wikipedia.org",
    "google docs": "https://docs.google.com",
    "google sheets": "https://sheets.google.com",
    "notion": "https://www.notion.so",
    "netflix": "https://www.netflix.com",
    "google maps": "https://maps.google.com",
    "google translate": "https://translate.google.com",
    "weather": "https://www.google.com/search?q=weather",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "amazon": "https://www.amazon.com",
    "daraz": "https://www.daraz.pk",
    "spotify web player": "https://open.spotify.com",
}

# Processes that must never be closed by the agent. explorer.exe is
# the Windows shell, not an ordinary app.
PROTECTED_PROCESSES = {
    "explorer.exe", "system", "registry", "winlogon.exe", "csrss.exe",
    "smss.exe", "services.exe", "lsass.exe",
}

# Spoken synonyms. Longest phrases are applied first in parser.py.
# These are written by the developer, never inferred from speech.
SYNONYMS = {
    "visual studio code": "visual studio code",
    "vs code": "visual studio code",
    "vscode": "visual studio code",
    "intelligi": "intellij idea",
    "intellij idea": "intellij idea",
    "jupyter notebook": "jupyter notebook",
    "notebook": "jupyter notebook",
    "this pc": "this pc",
    "my computer": "this pc",
    "dev c plus plus": "dev c++",
    "dev c++": "dev c++",
    "ms word": "microsoft word",
    "ms excel": "microsoft excel",
    "ms powerpoint": "microsoft powerpoint",
    "chrome browser": "chrome",
    "edge browser": "edge",
    "brave browser": "brave",
}

# Valid ranges for spoken numbers. Out-of-range values are rejected
# by the parser instead of being clamped silently.
NUMBER_RANGES = {
    "set_volume": (0, 100),
    "set_brightness": (0, 100),
    "word_font_size": (8, 72),
    "set_timer": (1, 180),
    "scroll_down_n": (1, 20),
    "scroll_up_n": (1, 20),
}
