"""Find installed Windows apps, on any drive — not only C: and PATH.

v1 only used shutil.which(), which is why Notepad worked (it lives
in C:\\Windows\\System32, which is in PATH) and Chrome/Brave failed
(they usually live in Program Files or %LOCALAPPDATA%, which are
not in PATH). v1.1 searches, in order, for each app:

1. arkagent_config.json "apps" override (your explicit path wins).
2. PATH (shutil.which).
3. Windows "App Paths" registry keys, e.g. chrome.exe -> its folder.
4. Known install folders, on EVERY drive that exists:
   <Drive>:\\Program Files\\<vendor>\\...,
   <Drive>:\\Program Files (x86)\\<vendor>\\...,
   %LOCALAPPDATA%\\<vendor>\\..., %APPDATA%\\<vendor>\\...
5. A shallow scan of each drive's top-level folders for the .exe
   name (portable apps on F: or E: often live here). This is only
   run when steps 1-4 fail, and its result is cached by the caller.

Nothing here runs user text. App names and .exe names come only
from config.APP_EXECUTABLES, and candidate paths are built from
fixed vendor folders plus the .exe name.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from .config import APP_EXECUTABLES
from .user_config import get_app_paths, get_default_browser

# Special Windows targets that are not .exe files at all.
# kind: "shell_folder" opens a shell location in Explorer,
#       "system_exe" runs a fixed Windows system program,
#       "settings" opens a ms-settings: page.
SPECIAL_APPS: dict[str, tuple[str, str]] = {
    "this pc": ("shell_folder", "::{20D04FE0-3AEA-1069-A2D8-08002B30309D}"),
    "recycle bin": ("shell_folder", "shell:RecycleBinFolder"),
    "file explorer": ("system_exe", "explorer.exe"),
    "settings": ("settings", "ms-settings:"),
    "windows security": ("settings", "ms-settings:windowsdefender"),
    "control panel": ("system_exe", "control.exe"),
    "task manager": ("system_exe", "taskmgr.exe"),
    "command prompt": ("system_exe", "cmd.exe"),
    "powershell": ("system_exe", "powershell.exe"),
    "windows terminal": ("system_exe", "wt.exe"),
    "snipping tool": ("system_exe", "SnippingTool.exe"),
}

# Vendor-relative paths, checked under Program Files, Program Files
# (x86), %LOCALAPPDATA% and %APPDATA%, on each drive.
RELATIVE_PATHS: dict[str, list[str]] = {
    "chrome": [r"Google/Chrome/Application/chrome.exe"],
    "brave": [r"BraveSoftware/Brave-Browser/Application/brave.exe"],
    "edge": [r"Microsoft/Edge/Application/msedge.exe"],
    "firefox": [r"Mozilla Firefox/firefox.exe"],
    "opera": [r"Opera/opera.exe"],
    "spotify": [r"Spotify/Spotify.exe"],
    "visual studio code": [r"Microsoft VS Code/Code.exe"],
    "visual studio": [r"Microsoft Visual Studio/2022/Community/Common7/IDE/devenv.exe"],
    "pycharm": [r"JetBrains/PyCharm/current/bin/pycharm64.exe"],
    "intellij idea": [r"JetBrains/IntelliJ IDEA/current/bin/idea64.exe"],
    "webstorm": [r"JetBrains/WebStorm/current/bin/webstorm64.exe"],
    "android studio": [r"Android/Android Studio/bin/studio64.exe"],
    "discord": [r"Discord/Discord.exe"],
    "zoom": [r"Zoom/bin/Zoom.exe"],
    "vlc media player": [r"VideoLAN/VLC/vlc.exe"],
    "notepad++": [r"Notepad++/notepad++.exe"],
    "postman": [r"Postman/Postman.exe"],
    "docker desktop": [r"Docker/Docker/Docker Desktop.exe"],
    "github desktop": [r"GitHub Desktop/GitHubDesktop.exe"],
}


def get_drives() -> list[Path]:
    """All existing drive roots on Windows, else just the root."""
    if not sys.platform.startswith("win"):
        return [Path("/")]
    drives: list[Path] = []
    try:
        import ctypes

        mask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in range(26):
            if mask & (1 << letter):
                drives.append(Path(f"{chr(65 + letter)}:\\"))
        if drives:
            return drives
    except Exception:
        pass
    for letter in "CDEFGHIJ":
        root = Path(f"{letter}:\\")
        if root.exists():
            drives.append(root)
    return drives or [Path("C:\\")]


def _app_paths_registry(exe: str) -> Path | None:
    """Windows App Paths registry: the official way Windows finds apps."""
    if not sys.platform.startswith("win"):
        return None
    try:
        import winreg
    except ImportError:
        return None
    key_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{exe}"
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(hive, key_path) as key:
                value, _ = winreg.QueryValueEx(key, "")
                if value and Path(value).is_file():
                    return Path(value)
        except OSError:
            continue
    return None


def _candidate_bases(drives: list[Path]) -> list[Path]:
    bases: list[Path] = []
    for drive in drives:
        bases.append(drive / "Program Files")
        bases.append(drive / "Program Files (x86)")
    for env in ("LOCALAPPDATA", "APPDATA", "ProgramFiles", "ProgramFiles(x86)"):
        value = os.environ.get(env)
        if value:
            bases.append(Path(value))
    return bases


def find_app_executable(
    app_name: str,
    drives: list[Path] | None = None,
    search_roots: list[Path] | None = None,
) -> Path | None:
    """Return the full path of an installed app, or None if not found."""
    name = app_name.lower().strip()
    # 1. Explicit user override.
    override = get_app_paths().get(name)
    if override and Path(override).is_file():
        return Path(override)
    exe = APP_EXECUTABLES.get(name)
    if exe is None:
        return None
    # 2. PATH.
    found = shutil.which(exe)
    if found:
        return Path(found)
    # 3. App Paths registry.
    registry_path = _app_paths_registry(exe)
    if registry_path is not None:
        return registry_path
    drive_list = drives if drives is not None else get_drives()
    # 4. Known vendor folders on every drive.
    for base in _candidate_bases(drive_list):
        for relative in RELATIVE_PATHS.get(name, []):
            candidate = base / relative
            if candidate.is_file():
                return candidate
        # Generic: <base>\<exe> (covers simple installs).
        candidate = base / exe
        if candidate.is_file():
            return candidate
    # 5. Shallow scan: <drive>:\<exe> and <drive>:\<folder>\<exe>.
    roots = search_roots if search_roots is not None else drive_list
    for root in roots:
        direct = Path(root) / exe
        if direct.is_file():
            return direct
        try:
            entries = list(os.scandir(root))
        except OSError:
            continue
        for entry in entries:
            try:
                if not entry.is_dir():
                    continue
                candidate = Path(entry.path) / exe
                if candidate.is_file():
                    return candidate
            except OSError:
                continue
    return None


def find_default_browser(drives: list[Path] | None = None) -> str:
    """First installed browser, in preference order. Edge is the
    Windows built-in fallback, so it is last-resort, not first."""
    preferred = get_default_browser()
    order = [preferred, "edge", "chrome", "brave", "firefox", "opera"]
    seen: list[str] = []
    for name in order:
        if name in seen:
            continue
        seen.append(name)
        if find_app_executable(name, drives=drives) is not None:
            return name
    return "edge"
