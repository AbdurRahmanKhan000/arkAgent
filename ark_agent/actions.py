"""Safe action execution for arkAgent.

Safety rules (enforced here, not in the UI):
- Only actions present in commands.json can run, and only through
  the handler table below.
- User text is never a command line. Every subprocess call uses a
  list of fixed arguments. There is no shell, no string command.
- Protected processes (see config.PROTECTED_PROCESSES) are denied,
  including explorer.exe, which is the Windows shell.
- Risk "confirm" actions never run until ConfirmationManager has a
  clear, unexpired "yes" for that exact action.
- On a non-Windows machine, or in dry-run mode, Windows actions
  report a dry-run / not-supported result instead of guessing.
  A dry-run result is always labelled as a dry run, so a test or a
  log can never mistake it for a real action.
"""
from __future__ import annotations

import datetime
import os
import shutil
import subprocess
import sys
import time
import uuid
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path

from .config import APP_EXECUTABLES, PROTECTED_PROCESSES, WEBSITES
from .parser import ParsedCommand

CONFIRM_TTL_SECONDS = 60


@dataclass
class ActionResult:
    success: bool
    message: str
    needs_confirmation: bool = False
    token: str | None = None
    action: str = ""


@dataclass
class PendingConfirmation:
    token: str
    command: ParsedCommand
    created_at: float = field(default_factory=time.monotonic)

    def is_expired(self) -> bool:
        return time.monotonic() - self.created_at > CONFIRM_TTL_SECONDS


class ConfirmationManager:
    """One pending confirmation at a time, expiring and request-bound."""

    def __init__(self) -> None:
        self.pending: PendingConfirmation | None = None

    def create(self, command: ParsedCommand) -> PendingConfirmation:
        self.pending = PendingConfirmation(token=uuid.uuid4().hex[:8], command=command)
        return self.pending

    def decide(self, text: str) -> bool | None:
        """True = clear yes, False = clear no, None = ambiguous."""
        value = " ".join(text.strip().lower().split())
        if value in ("yes", "confirm", "yes confirm", "do it"):
            return True
        if value in ("no", "cancel", "stop", "do not"):
            return False
        return None

    def take(self) -> PendingConfirmation | None:
        pending = self.pending
        self.pending = None
        if pending is None or pending.is_expired():
            return None
        return pending


# Keyboard shortcuts for Word / editing actions. These are fixed
# shortcuts, never built from user text.
_WORD_SHORTCUTS = {
    "word_bold": ["ctrl", "b"],
    "word_italic": ["ctrl", "i"],
    "word_underline": ["ctrl", "u"],
    "word_font_up": ["ctrl", "]"],
    "word_font_down": ["ctrl", "["],
    "word_align_left": ["ctrl", "l"],
    "word_align_center": ["ctrl", "e"],
    "word_align_right": ["ctrl", "r"],
    "word_align_justify": ["ctrl", "j"],
    "word_page_break": ["ctrl", "enter"],
    "word_bullet_list": ["ctrl", "shift", "l"],
    "word_numbered_list": ["ctrl", "shift", "n"],
    "word_select_paragraph": ["ctrl", "shift", "up"],
    "word_count": ["ctrl", "shift", "g"],
    "word_clear_formatting": ["ctrl", "space"],
}

_SETTINGS_URIS = {
    "system about": "ms-settings:about",
    "windows update": "ms-settings:windowsupdate",
    "windows security and update": "ms-settings:windowsupdate",
    "bluetooth settings": "ms-settings:bluetooth",
    "wifi settings": "ms-settings:network-wifi",
    "network settings": "ms-settings:network",
    "sound settings": "ms-settings:sound",
    "display settings": "ms-settings:display",
    "personalization settings": "ms-settings:personalization",
    "accounts settings": "ms-settings:yourinfo",
    "privacy settings": "ms-settings:privacy",
    "storage settings": "ms-settings:storagesense",
    "battery settings": "ms-settings:batterysaver",
    "power settings": "ms-settings:powersleep",
    "date and time settings": "ms-settings:dateandtime",
    "language settings": "ms-settings:regionlanguage",
    "mouse settings": "ms-settings:mousetouchpad",
    "apps settings": "ms-settings:appsfeatures",
    "notifications settings": "ms-settings:notifications",
    "accessibility settings": "ms-settings:easeofaccess",
}


class ActionExecutor:
    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self.is_windows = sys.platform.startswith("win")
        self.confirmations = ConfirmationManager()
        self.last_command: ParsedCommand | None = None

    # -- public entry point -------------------------------------------------
    def execute(self, command: ParsedCommand | None, confirmed: bool = False) -> ActionResult:
        if command is None:
            return ActionResult(False, "I do not recognise that command.")
        if command.needs_confirmation and not confirmed:
            pending = self.confirmations.create(command)
            return ActionResult(
                False,
                f"Are you sure you want to: {command.phrase}? Say yes or no.",
                needs_confirmation=True,
                token=pending.token,
                action=command.action,
            )
        self.last_command = command
        handler = self._handlers().get(command.action)
        if handler is None:
            return ActionResult(
                False,
                f"Action '{command.action}' is registered but has no handler yet.",
                action=command.action,
            )
        try:
            return handler(command)
        except Exception as exc:  # never crash the agent loop on one action
            return ActionResult(False, f"Action failed: {exc}", action=command.action)

    def confirm_pending(self, answer_text: str) -> ActionResult:
        decision = self.confirmations.decide(answer_text)
        if decision is None:
            return ActionResult(False, "Please say yes or no.")
        pending = self.confirmations.take()
        if pending is None:
            return ActionResult(False, "No confirmation is waiting, or it expired.")
        if not decision:
            return ActionResult(True, f"Cancelled: {pending.command.phrase}.")
        return self.execute(pending.command, confirmed=True)

    # -- helpers ------------------------------------------------------------
    def _dry(self, message: str, action: str) -> ActionResult:
        if self.dry_run or not self.is_windows:
            return ActionResult(True, f"[dry-run] {message}", action=action)
        return ActionResult(False, "unreachable", action=action)

    def _run_fixed(self, args: list[str]) -> ActionResult:
        """Run a fixed argument list. No shell, no user text in args."""
        if self.dry_run or not self.is_windows:
            return ActionResult(True, f"[dry-run] would run: {' '.join(args)}")
        try:
            subprocess.Popen(args)
            return ActionResult(True, f"Started: {' '.join(args)}")
        except FileNotFoundError:
            return ActionResult(False, f"Program not found: {args[0]}")

    def _hotkey(self, keys: list[str], action: str) -> ActionResult:
        if self.dry_run or not self.is_windows:
            return ActionResult(True, f"[dry-run] hotkey: {'+'.join(keys)}", action=action)
        try:
            import pyautogui
        except ImportError:
            return ActionResult(False, "pyautogui is not installed. Run: pip install pyautogui", action=action)
        pyautogui.hotkey(*keys)
        return ActionResult(True, f"Pressed {'+'.join(keys)}", action=action)

    # -- handlers -----------------------------------------------------------
    def _handlers(self) -> dict:
        generic_browser = self._generic_browser
        generic_key = self._generic_key
        generic_word = self._generic_word
        generic_system = self._generic_system
        generic_office = self._generic_office
        generic_file = self._generic_file
        generic_voice = self._generic_voice
        return {
            "launch_app": self._launch_app,
            "close_app": self._close_app,
            "close_window": generic_browser,
            "close_all_browsers": generic_browser,
            "close_all_apps": generic_browser,
            "open_website": self._open_website,
            "open_website_typed": self._open_website_typed,
            "open_settings": self._open_settings,
            "open_folder": self._open_folder,
            "open_new_tab": generic_browser,
            "close_tab": generic_browser,
            "reopen_tab": generic_browser,
            "next_tab": generic_browser,
            "previous_tab": generic_browser,
            "first_tab": generic_browser,
            "last_tab": generic_browser,
            "refresh": generic_browser,
            "hard_refresh": generic_browser,
            "go_back": generic_browser,
            "go_forward": generic_browser,
            "go_home": generic_browser,
            "open_new_window": generic_browser,
            "open_private_window": generic_browser,
            "open_history": generic_browser,
            "open_browser_downloads": generic_browser,
            "open_bookmarks": generic_browser,
            "bookmark_page": generic_browser,
            "search_text": self._search_text,
            "type_and_enter": self._type_and_enter,
            "type_search_and_enter": self._type_and_enter,
            "focus_address_bar": generic_browser,
            "clear_address_bar": generic_browser,
            "scroll_down": generic_key,
            "scroll_up": generic_key,
            "scroll_down_small": generic_key,
            "scroll_up_small": generic_key,
            "scroll_down_large": generic_key,
            "scroll_up_large": generic_key,
            "scroll_top": generic_key,
            "scroll_bottom": generic_key,
            "scroll_right": generic_key,
            "scroll_left": generic_key,
            "page_down": generic_key,
            "page_up": generic_key,
            "scroll_down_n": generic_key,
            "scroll_up_n": generic_key,
            "mouse_up": generic_key,
            "mouse_down": generic_key,
            "mouse_left": generic_key,
            "mouse_right": generic_key,
            "mouse_click": generic_key,
            "mouse_double_click": generic_key,
            "mouse_right_click": generic_key,
            "key_enter": generic_key,
            "key_escape": generic_key,
            "key_tab": generic_key,
            "key_space": generic_key,
            "key_select_all": generic_key,
            "key_copy": generic_key,
            "key_paste": generic_key,
            "key_cut": generic_key,
            "key_undo": generic_key,
            "key_redo": generic_key,
            "mute": self._volume,
            "unmute": self._volume,
            "volume_up": self._volume,
            "volume_down": self._volume,
            "set_volume": self._volume,
            "media_play": generic_key,
            "media_pause": generic_key,
            "media_play_pause": generic_key,
            "media_next": generic_key,
            "media_previous": generic_key,
            "media_stop": generic_key,
            "play_music": generic_key,
            "open_volume_mixer": generic_system,
            "brightness_up": generic_system,
            "brightness_down": generic_system,
            "set_brightness": generic_system,
            "lock": generic_system,
            "sleep": generic_system,
            "restart": generic_system,
            "shutdown": generic_system,
            "sign_out": generic_system,
            "cancel_shutdown": generic_system,
            "show_desktop": generic_system,
            "minimize_all": generic_system,
            "restore_all": generic_system,
            "alt_tab": generic_system,
            "task_view": generic_system,
            "wifi_on": generic_system,
            "wifi_off": generic_system,
            "bluetooth_on": generic_system,
            "bluetooth_off": generic_system,
            "airplane_on": generic_system,
            "airplane_off": generic_system,
            "show_wifi": generic_system,
            "dark_mode_on": generic_system,
            "dark_mode_off": generic_system,
            "screenshot": self._screenshot,
            "screenshot_window": self._screenshot,
            "clipboard_history": generic_system,
            "clear_clipboard": generic_system,
            "empty_recycle_bin": generic_system,
            "tell_time": self._tell_time,
            "tell_date": self._tell_date,
            "battery_status": generic_system,
            "system_info": generic_system,
            "new_word_doc": generic_office,
            "save_doc": generic_office,
            "save_doc_as": generic_office,
            "close_doc": generic_office,
            "type_in_word": self._type_and_enter,
            "print_doc": generic_office,
            "word_zoom_in": generic_word,
            "word_zoom_out": generic_word,
            "word_find": generic_word,
            "word_replace": generic_word,
            "word_spellcheck": generic_word,
            "new_excel_workbook": generic_office,
            "new_ppt": generic_office,
            "new_email": generic_office,
            "send_email": generic_office,
            "word_insert_header": generic_word,
            "word_insert_footer": generic_word,
            "word_insert_page_number": generic_word,
            "word_bullet_list": generic_word,
            "word_numbered_list": generic_word,
            "word_remove_list": generic_word,
            "word_indent_up": generic_word,
            "word_indent_down": generic_word,
            "word_insert_image": generic_word,
            "word_insert_table": generic_word,
            "word_insert_hyperlink": generic_word,
            "word_insert_date": generic_word,
            "word_insert_time": generic_word,
            "word_spacing_single": generic_word,
            "word_spacing_double": generic_word,
            "word_spacing_1_5": generic_word,
            "save_doc_as_pdf": generic_office,
            "word_open_recent": generic_word,
            "close_all_word_docs": generic_word,
            "word_select_paragraph": generic_word,
            "word_select_line": generic_word,
            "doc_start": generic_word,
            "doc_end": generic_word,
            "word_insert_comment": generic_word,
            "word_track_on": generic_word,
            "word_track_off": generic_word,
            "word_count": generic_word,
            "word_insert_line": generic_word,
            "word_clear_formatting": generic_word,
            "word_color_red": generic_word,
            "word_color_blue": generic_word,
            "word_color_black": generic_word,
            "word_highlight": generic_word,
            "word_toc_create": generic_word,
            "word_toc_update": generic_word,
            "word_cover_page": generic_word,
            "word_margins_narrow": generic_word,
            "word_margins_normal": generic_word,
            "word_portrait": generic_word,
            "word_landscape": generic_word,
            "word_section_break": generic_word,
            "word_footnote": generic_word,
            "word_endnote": generic_word,
            "word_font_size": generic_word,
            "word_new_paragraph": generic_word,
            "word_bold": generic_word,
            "word_italic": generic_word,
            "word_underline": generic_word,
            "word_font_up": generic_word,
            "word_font_down": generic_word,
            "word_align_left": generic_word,
            "word_align_center": generic_word,
            "word_align_right": generic_word,
            "word_align_justify": generic_word,
            "word_page_break": generic_word,
            "excel_insert_row": generic_office,
            "excel_insert_column": generic_office,
            "excel_delete_row": generic_office,
            "excel_delete_column": generic_office,
            "excel_freeze_top": generic_office,
            "excel_unfreeze": generic_office,
            "excel_sort_asc": generic_office,
            "excel_sort_desc": generic_office,
            "excel_filter_on": generic_office,
            "excel_filter_off": generic_office,
            "excel_sum": generic_office,
            "excel_currency": generic_office,
            "excel_percent": generic_office,
            "ppt_slideshow": generic_office,
            "ppt_next": generic_office,
            "ppt_previous": generic_office,
            "ppt_first": generic_office,
            "ppt_last": generic_office,
            "email_reply": generic_office,
            "email_forward": generic_office,
            "email_mark_read": generic_office,
            "email_archive": generic_office,
            "search_file": generic_file,
            "create_folder": generic_file,
            "create_text_file": generic_file,
            "rename_file": generic_file,
            "delete_file": generic_file,
            "recycle_file": generic_file,
            "open_recent": generic_file,
            "sort_by_name": generic_file,
            "sort_by_date": generic_file,
            "show_hidden_files": generic_file,
            "hide_hidden_files": generic_file,
            "copy_file_path": generic_file,
            "set_timer": generic_file,
            "set_alarm": generic_file,
            "internet_speed": generic_file,
            "show_ip": generic_file,
            "voice_start": generic_voice,
            "voice_stop": generic_voice,
            "voice_pause": generic_voice,
            "voice_resume": generic_voice,
            "dictation_start": generic_voice,
            "dictation_stop": generic_voice,
            "show_last_transcript": generic_voice,
            "show_commands": generic_voice,
            "search_commands": generic_voice,
            "open_history_log": generic_voice,
            "clear_history": generic_voice,
            "open_start": generic_system,
            "open_search_ui": generic_system,
            "open_action_center": generic_system,
            "open_quick_settings": generic_system,
            "open_notifications_ui": generic_system,
            "text_upper": generic_key,
            "text_lower": generic_key,
            "speak_selection": generic_voice,
            "set_default_browser_chrome": generic_voice,
            "set_default_browser_edge": generic_voice,
            "set_default_browser_brave": generic_voice,
            "set_default_ide_vscode": generic_voice,
            "set_default_ide_pycharm": generic_voice,
            "repeat_last": generic_voice,
        }

    def _app_name(self, command: ParsedCommand) -> str:
        phrase = command.phrase
        if phrase.startswith("open "):
            return phrase[5:]
        if phrase.startswith("close "):
            return phrase[6:]
        return phrase

    def _launch_app(self, command: ParsedCommand) -> ActionResult:
        name = self._app_name(command)
        exe = APP_EXECUTABLES.get(name)
        if self.dry_run or not self.is_windows:
            return ActionResult(True, f"[dry-run] open {name}", action=command.action)
        if exe is None:
            # Start-menu / Store apps: try the fixed name, never user text.
            return ActionResult(False, f"No executable mapping for '{name}'. Add it to config.APP_EXECUTABLES.", action=command.action)
        found = shutil.which(exe)
        if found:
            return self._run_fixed([found])
        return ActionResult(False, f"Program not found on this PC: {exe}. Is {name} installed?", action=command.action)

    def _close_app(self, command: ParsedCommand) -> ActionResult:
        name = self._app_name(command)
        exe = APP_EXECUTABLES.get(name, f"{name}.exe")
        if exe in PROTECTED_PROCESSES or name in ("file explorer", "this pc"):
            return ActionResult(False, f"Refused: '{name}' is a protected system process and cannot be closed.", action=command.action)
        if self.dry_run or not self.is_windows:
            return ActionResult(True, f"[dry-run] close {name}", action=command.action)
        return self._run_fixed(["taskkill", "/IM", exe, "/F"])

    def _open_website(self, command: ParsedCommand) -> ActionResult:
        name = self._app_name(command)
        url = WEBSITES.get(name)
        if url is None:
            return ActionResult(False, f"No website mapping for '{name}'.", action=command.action)
        if self.dry_run:
            return ActionResult(True, f"[dry-run] open {url}", action=command.action)
        webbrowser.open(url, new=2)
        return ActionResult(True, f"Opened {url}", action=command.action)

    def _open_website_typed(self, command: ParsedCommand) -> ActionResult:
        site = command.variables.get("website", "")
        if not site:
            return ActionResult(False, "No website was given.", action=command.action)
        url = site if site.startswith(("http://", "https://")) else f"https://{site}"
        if self.dry_run:
            return ActionResult(True, f"[dry-run] open {url}", action=command.action)
        webbrowser.open(url, new=2)
        return ActionResult(True, f"Opened {url}", action=command.action)

    def _open_settings(self, command: ParsedCommand) -> ActionResult:
        name = self._app_name(command)
        uri = _SETTINGS_URIS.get(name, "ms-settings:")
        if self.dry_run or not self.is_windows:
            return ActionResult(True, f"[dry-run] open settings: {uri}", action=command.action)
        try:
            os.startfile(uri)  # type: ignore[attr-defined]
            return ActionResult(True, f"Opened settings: {uri}", action=command.action)
        except Exception as exc:
            return ActionResult(False, f"Could not open settings: {exc}", action=command.action)

    def _open_folder(self, command: ParsedCommand) -> ActionResult:
        folders = {
            "downloads folder": "Downloads", "downloads": "Downloads",
            "documents folder": "Documents", "documents": "Documents",
            "pictures folder": "Pictures", "pictures": "Pictures",
            "videos folder": "Videos", "videos": "Videos",
            "music folder": "Music", "desktop folder": "Desktop",
            "this pc": "", "recycle bin": "",
        }
        key = self._app_name(command)
        sub = folders.get(key)
        if sub is None:
            return ActionResult(False, f"No folder mapping for '{key}'.", action=command.action)
        if self.dry_run or not self.is_windows:
            return ActionResult(True, f"[dry-run] open folder: {key}", action=command.action)
        path = Path.home() / sub if sub else Path.home()
        try:
            os.startfile(str(path))  # type: ignore[attr-defined]
            return ActionResult(True, f"Opened {path}", action=command.action)
        except Exception as exc:
            return ActionResult(False, f"Could not open folder: {exc}", action=command.action)

    def _generic_browser(self, command: ParsedCommand) -> ActionResult:
        keys = {
            "open_new_tab": ["ctrl", "t"], "close_tab": ["ctrl", "w"],
            "reopen_tab": ["ctrl", "shift", "t"], "next_tab": ["ctrl", "tab"],
            "previous_tab": ["ctrl", "shift", "tab"], "refresh": ["f5"],
            "hard_refresh": ["ctrl", "f5"], "go_back": ["alt", "left"],
            "go_forward": ["alt", "right"], "open_new_window": ["ctrl", "n"],
            "open_private_window": ["ctrl", "shift", "n"],
            "open_history": ["ctrl", "h"], "bookmark_page": ["ctrl", "d"],
            "focus_address_bar": ["ctrl", "l"],
        }
        if command.action in keys:
            return self._hotkey(keys[command.action], command.action)
        return self._dry(f"browser action: {command.action}", command.action)

    def _generic_key(self, command: ParsedCommand) -> ActionResult:
        if self.dry_run or not self.is_windows:
            return ActionResult(True, f"[dry-run] key/scroll action: {command.action}", action=command.action)
        try:
            import pyautogui
        except ImportError:
            return ActionResult(False, "pyautogui is not installed. Run: pip install pyautogui", action=command.action)
        scrolls = {
            "scroll_down": -600, "scroll_up": 600,
            "scroll_down_small": -200, "scroll_up_small": 200,
            "scroll_down_large": -1200, "scroll_up_large": 1200,
        }
        if command.action in scrolls:
            pyautogui.scroll(scrolls[command.action])
            return ActionResult(True, f"Scrolled: {command.action}", action=command.action)
        if command.action in ("scroll_top", "scroll_bottom"):
            pyautogui.hotkey("ctrl", "home" if command.action == "scroll_top" else "end")
            return ActionResult(True, f"Scrolled: {command.action}", action=command.action)
        if command.action == "mouse_click":
            pyautogui.click()
        elif command.action == "mouse_double_click":
            pyautogui.doubleClick()
        elif command.action == "mouse_right_click":
            pyautogui.rightClick()
        else:
            return ActionResult(False, f"Keyboard action '{command.action}' is not mapped to a shortcut yet.", action=command.action)
        return ActionResult(True, f"Done: {command.action}", action=command.action)

    def _generic_word(self, command: ParsedCommand) -> ActionResult:
        if command.action in _WORD_SHORTCUTS:
            return self._hotkey(_WORD_SHORTCUTS[command.action], command.action)
        return self._dry(f"Word action: {command.action}", command.action)

    def _generic_office(self, command: ParsedCommand) -> ActionResult:
        return self._dry(f"Office action: {command.action}", command.action)

    def _generic_file(self, command: ParsedCommand) -> ActionResult:
        return self._dry(f"File action: {command.action}", command.action)

    def _generic_voice(self, command: ParsedCommand) -> ActionResult:
        return ActionResult(True, f"Voice/control request noted: {command.action}. The GUI handles listen, dictation and history display.", action=command.action)

    def _generic_system(self, command: ParsedCommand) -> ActionResult:
        fixed = {
            "lock": ["rundll32.exe", "user32.dll,LockWorkStation"],
            "shutdown": ["shutdown", "/s", "/t", "5"],
            "restart": ["shutdown", "/r", "/t", "5"],
            "cancel_shutdown": ["shutdown", "/a"],
            "sign_out": ["shutdown", "/l"],
            "sleep": ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
        }
        if command.action in fixed:
            return self._run_fixed(fixed[command.action])
        return self._dry(f"System action: {command.action}", command.action)

    def _volume(self, command: ParsedCommand) -> ActionResult:
        if self.dry_run or not self.is_windows:
            return ActionResult(True, f"[dry-run] volume: {command.action} {command.variables}", action=command.action)
        try:
            from comtypes import CLSCTX_ALL
            from ctypes import POINTER, cast
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        except ImportError:
            return ActionResult(False, "pycaw is not installed. Run: pip install pycaw", action=command.action)
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        if command.action == "mute":
            volume.SetMute(1, None)
        elif command.action == "unmute":
            volume.SetMute(0, None)
        elif command.action == "set_volume":
            level = int(command.variables.get("number", 50)) / 100.0
            volume.SetMasterVolumeLevelScalar(level, None)
        elif command.action == "volume_up":
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.1), None)
        elif command.action == "volume_down":
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(max(0.0, current - 0.1), None)
        return ActionResult(True, f"Volume: {command.action}", action=command.action)

    def _search_text(self, command: ParsedCommand) -> ActionResult:
        text = command.variables.get("text", "")
        if self.dry_run:
            return ActionResult(True, f"[dry-run] search for: {text}", action=command.action)
        webbrowser.open(f"https://www.google.com/search?q={text}", new=2)
        return ActionResult(True, f"Searched for: {text}", action=command.action)

    def _type_and_enter(self, command: ParsedCommand) -> ActionResult:
        text = command.variables.get("text", "")
        if self.dry_run or not self.is_windows:
            return ActionResult(True, f"[dry-run] type and enter: {text}", action=command.action)
        try:
            import pyautogui
        except ImportError:
            return ActionResult(False, "pyautogui is not installed. Run: pip install pyautogui", action=command.action)
        pyautogui.write(text, interval=0.01)
        pyautogui.press("enter")
        return ActionResult(True, f"Typed: {text}", action=command.action)

    def _screenshot(self, command: ParsedCommand) -> ActionResult:
        if self.dry_run or not self.is_windows:
            return ActionResult(True, "[dry-run] screenshot saved", action=command.action)
        try:
            import pyautogui
        except ImportError:
            return ActionResult(False, "pyautogui is not installed. Run: pip install pyautogui", action=command.action)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        path = Path.home() / "Pictures" / f"arkAgent-{stamp}.png"
        pyautogui.screenshot(str(path))
        return ActionResult(True, f"Screenshot saved: {path}", action=command.action)

    def _tell_time(self, command: ParsedCommand) -> ActionResult:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return ActionResult(True, f"The time is {now}.", action=command.action)

    def _tell_date(self, command: ParsedCommand) -> ActionResult:
        today = datetime.datetime.now().strftime("%A, %d %B %Y")
        return ActionResult(True, f"Today is {today}.", action=command.action)
