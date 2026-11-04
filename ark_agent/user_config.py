"""User configuration file for arkAgent v1.1.

File: arkagent_config.json in the project folder (the folder you run
from), or ~/.arkagent.json in your home folder. The project file wins
if both exist, because that is the copy you edit next to the code.

Example:
{
  "default_browser": "edge",
  "vosk_model_path": "C:\\models\\vosk-model-small-en-us",
  "apps": {
    "chrome": "F:\\Google\\Chrome\\Application\\chrome.exe",
    "arkmedia": "F:\\ARK\\arkmedia\\arkmedia.exe"
  }
}

The "apps" section is the fix for apps on D:, E: or F: drives, and
for portable apps: you tell arkAgent once where an app lives, and
it never has to guess again. Discovery (app_discovery.py) checks
this file before it searches any drive.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

PROJECT_CONFIG = Path(__file__).resolve().parent.parent / "arkagent_config.json"
HOME_CONFIG = Path.home() / ".arkagent.json"


def load_config() -> dict:
    data: dict = {}
    for path in (HOME_CONFIG, PROJECT_CONFIG):
        try:
            if path.is_file():
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    data.update(loaded)
        except Exception:
            continue
    return data


def save_config(updates: dict, path: Path | None = None) -> Path:
    target = path or PROJECT_CONFIG
    data = load_config()
    data.update(updates)
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def get_app_paths() -> dict:
    apps = load_config().get("apps", {})
    return apps if isinstance(apps, dict) else {}


def get_default_browser() -> str:
    value = load_config().get("default_browser", "chrome")
    return str(value).lower() if value else "chrome"


def get_vosk_model_path() -> str | None:
    value = load_config().get("vosk_model_path") or os.environ.get("ARKAGENT_VOSK_MODEL")
    return str(value) if value else None
