#!/usr/bin/env python3
"""Generate the fixed-command registry for the ARK laptop agent (no LLM).
Each entry is one canonical spoken/typed phrase. <text>, <number>, <website>
and <file> are spoken variables, filled in at run time - they are NOT free
LLM prompts. The agent only executes entries in this registry.
"""
import pathlib

out = pathlib.Path(__file__).resolve().parent.parent / "commands.md"
commands = []  # (phrase, category, action, risk)

def add(phrase, category, action, risk="safe"):
    commands.append((phrase, category, action, risk))

# --- 1. Open apps (user-named + everyday apps) ---
apps = [
    ("chrome", "launch_app"), ("edge", "launch_app"), ("brave", "launch_app"),
    ("firefox", "launch_app"), ("opera", "launch_app"),
    ("spotify", "launch_app"), ("whatsapp", "launch_app"), ("telegram", "launch_app"),
    ("discord", "launch_app"), ("zoom", "launch_app"), ("microsoft teams", "launch_app"),
    ("vlc media player", "launch_app"), ("windows media player", "launch_app"),
    ("photos", "launch_app"), ("paint", "launch_app"), ("notepad", "launch_app"),
    ("calculator", "launch_app"), ("calendar", "launch_app"), ("clock", "launch_app"),
    ("mail", "launch_app"), ("snipping tool", "launch_app"), ("file explorer", "launch_app"),
    ("task manager", "launch_app"), ("control panel", "launch_app"),
    ("settings", "launch_app"), ("windows security", "launch_app"),
    ("arkmedia", "launch_app"), ("arksnap", "launch_app"), ("arkdownload", "launch_app"),
    ("recycle bin", "launch_app"), ("this pc", "launch_app"),
    ("microsoft store", "launch_app"), ("xbox", "launch_app"),
]
for name, act in apps:
    add(f"open {name}", "Apps", act)

# --- 2. Open IDEs and developer tools ---
dev_tools = [
    "visual studio code", "visual studio", "intellij idea", "pycharm",
    "webstorm", "android studio", "eclipse", "netbeans", "dev c++",
    "code blocks", "sublime text", "notepad++", "python interpreter",
    "python idle", "jupyter notebook", "jupyter lab", "anaconda navigator",
    "git bash", "command prompt", "powershell", "windows terminal",
    "docker desktop", "postman", "mysql workbench", "pgadmin",
    "mongodb compass", "figma", "xampp", "virtualbox", "github desktop",
]
for name in dev_tools:
    add(f"open {name}", "IDEs and Developer Tools", "launch_app")

# --- 3. Open websites and AI assistants (browser targets) ---
sites = [
    ("claude", "open_website"), ("gemini", "open_website"), ("grok", "open_website"),
    ("chatgpt", "open_website"), ("copilot", "open_website"),
    ("youtube", "open_website"), ("github", "open_website"), ("google", "open_website"),
    ("gmail", "open_website"), ("google drive", "open_website"),
    ("linkedin", "open_website"), ("whatsapp web", "open_website"),
    ("stack overflow", "open_website"), ("wikipedia", "open_website"),
    ("google docs", "open_website"), ("google sheets", "open_website"),
    ("notion", "open_website"), ("netflix", "open_website"),
    ("google maps", "open_website"), ("google translate", "open_website"),
    ("weather", "open_website"), ("facebook", "open_website"),
    ("instagram", "open_website"), ("amazon", "open_website"),
    ("daraz", "open_website"), ("spotify web player", "open_website"),
]
for name, act in sites:
    add(f"open {name}", "Websites", act)

# --- 4. Open Windows settings pages ---
settings_pages = [
    "system about", "windows update", "bluetooth settings", "wifi settings",
    "network settings", "sound settings", "display settings",
    "brightness settings", "personalization settings", "theme settings",
    "lock screen settings", "accounts settings", "privacy settings",
    "storage settings", "battery settings", "power settings",
    "date and time settings", "language settings", "keyboard settings",
    "mouse settings", "touchpad settings", "printer settings",
    "apps settings", "default apps settings", "startup apps settings",
    "notifications settings", "focus settings", "accessibility settings",
    "device manager", "disk management", "windows security and update",
]
for name in settings_pages:
    add(f"open {name}", "System Settings", "open_settings")

# --- 5. Open folders ---
for name in ["downloads folder", "documents folder", "pictures folder",
             "videos folder", "music folder", "desktop folder"]:
    add(f"open {name}", "Files and Folders", "open_folder")

# --- 6. Close apps by name (same core apps, plus a safe close-all rule) ---
close_apps = [
    "chrome", "edge", "brave", "firefox", "spotify", "whatsapp", "telegram",
    "discord", "zoom", "vlc media player", "notepad", "calculator", "paint",
    "file explorer", "settings", "task manager", "microsoft word",
    "microsoft excel", "microsoft powerpoint", "visual studio code",
    "pycharm", "intellij idea", "android studio", "microsoft teams",
    "arkmedia", "arksnap", "arkdownload",
]
for name in close_apps:
    add(f"close {name}", "Close Apps", "close_app", "confirm")
add("close current window", "Close Apps", "close_window", "confirm")
add("close all browsers", "Close Apps", "close_all_browsers", "confirm")
add("close all apps", "Close Apps", "close_all_apps", "confirm")

# --- 7. Browser control, tabs, search and typing ---
browser_cmds = [
    ("open new tab", "open_new_tab"), ("close tab", "close_tab"),
    ("close current tab", "close_tab"), ("reopen closed tab", "reopen_tab"),
    ("switch to next tab", "next_tab"), ("switch to previous tab", "previous_tab"),
    ("go to first tab", "first_tab"), ("go to last tab", "last_tab"),
    ("refresh page", "refresh"), ("hard refresh page", "hard_refresh"),
    ("go back", "go_back"), ("go forward", "go_forward"),
    ("go to home page", "go_home"), ("open new window", "open_new_window"),
    ("close browser window", "close_window"),
    ("open incognito window", "open_private_window"),
    ("open private window", "open_private_window"),
    ("open history", "open_history"), ("open downloads in browser", "open_browser_downloads"),
    ("open bookmarks", "open_bookmarks"), ("bookmark this page", "bookmark_page"),
    ("search for <text>", "search_text"), ("type <text> and press enter", "type_and_enter"),
    ("type <text> in search box and press enter", "type_search_and_enter"),
    ("open website <website>", "open_website_typed"),
    ("focus address bar", "focus_address_bar"), ("clear address bar", "clear_address_bar"),
]
for phrase, act in browser_cmds:
    add(phrase, "Browser Control", act)

# --- 8. Scrolling, mouse and keyboard ---
scroll_cmds = [
    ("scroll down", "scroll_down"), ("scroll up", "scroll_up"),
    ("scroll down a little", "scroll_down_small"), ("scroll up a little", "scroll_up_small"),
    ("scroll down a lot", "scroll_down_large"), ("scroll up a lot", "scroll_up_large"),
    ("scroll to top of page", "scroll_top"), ("scroll to bottom of page", "scroll_bottom"),
    ("scroll right", "scroll_right"), ("scroll left", "scroll_left"),
    ("page down", "page_down"), ("page up", "page_up"),
    ("scroll down <number> times", "scroll_down_n"), ("scroll up <number> times", "scroll_up_n"),
    ("move mouse up", "mouse_up"), ("move mouse down", "mouse_down"),
    ("move mouse left", "mouse_left"), ("move mouse right", "mouse_right"),
    ("click", "mouse_click"), ("double click", "mouse_double_click"),
    ("right click", "mouse_right_click"), ("press enter", "key_enter"),
    ("press escape", "key_escape"), ("press tab", "key_tab"),
    ("press space", "key_space"), ("select all", "key_select_all"),
    ("copy", "key_copy"), ("paste", "key_paste"), ("cut", "key_cut"),
    ("undo", "key_undo"), ("redo", "key_redo"),
]
for phrase, act in scroll_cmds:
    add(phrase, "Scrolling, Mouse and Keyboard", act)

# --- 9. Volume, media and audio ---
media_cmds = [
    ("mute volume", "mute"), ("unmute volume", "unmute"),
    ("turn sound off", "mute"), ("turn sound on", "unmute"),
    ("volume up", "volume_up"), ("volume down", "volume_down"),
    ("increase volume", "volume_up"), ("decrease volume", "volume_down"),
    ("set volume to <number> percent", "set_volume"),
    ("set volume to <number>", "set_volume"),
    ("play", "media_play"), ("pause", "media_pause"),
    ("play or pause", "media_play_pause"), ("next song", "media_next"),
    ("previous song", "media_previous"), ("next track", "media_next"),
    ("previous track", "media_previous"), ("stop music", "media_stop"),
    ("play music", "play_music"), ("pause music", "media_pause"),
    ("open volume mixer", "open_volume_mixer"),
    ("increase brightness", "brightness_up"), ("decrease brightness", "brightness_down"),
    ("set brightness to <number> percent", "set_brightness"),
]
for phrase, act in media_cmds:
    add(phrase, "Volume, Media and Display", act)

# --- 10. System, power, network and display ---
system_cmds = [
    ("lock computer", "lock", "confirm"), ("lock screen", "lock", "confirm"),
    ("sleep computer", "sleep", "confirm"), ("restart computer", "restart", "confirm"),
    ("shut down computer", "shutdown", "confirm"), ("sign out", "sign_out", "confirm"),
    ("cancel shutdown", "cancel_shutdown"),
    ("show desktop", "show_desktop"), ("minimize all windows", "minimize_all"),
    ("restore all windows", "restore_all"), ("switch window", "alt_tab"),
    ("switch to next window", "alt_tab"), ("open task view", "task_view"),
    ("turn wifi on", "wifi_on"), ("turn wifi off", "wifi_off"),
    ("turn bluetooth on", "bluetooth_on"), ("turn bluetooth off", "bluetooth_off"),
    ("turn airplane mode on", "airplane_on"), ("turn airplane mode off", "airplane_off"),
    ("show wifi networks", "show_wifi"), ("disconnect wifi", "wifi_off"),
    ("enable dark mode", "dark_mode_on"), ("enable light mode", "dark_mode_off"),
    ("take screenshot", "screenshot"), ("take screenshot of window", "screenshot_window"),
    ("open clipboard history", "clipboard_history"), ("clear clipboard", "clear_clipboard"),
    ("empty recycle bin", "empty_recycle_bin", "confirm"),
    ("what time is it", "tell_time"), ("what is the date", "tell_date"),
    ("show battery status", "battery_status"), ("show system info", "system_info"),
]
for item in system_cmds:
    phrase, act = item[0], item[1]
    risk = item[2] if len(item) > 2 else "safe"
    add(phrase, "System, Power and Network", act, risk)

# --- 11. Microsoft Office and documents ---
office_cmds = [
    ("open microsoft word", "launch_app"), ("open microsoft excel", "launch_app"),
    ("open microsoft powerpoint", "launch_app"), ("open microsoft outlook", "launch_app"),
    ("open microsoft onenote", "launch_app"),
    ("create new word document", "new_word_doc"),
    ("open new blank document in word", "new_word_doc"),
    ("save document", "save_doc"), ("save document as", "save_doc_as", ),
    ("close word document", "close_doc", ),
    ("type <text> in word", "type_in_word"),
    ("type <text> in document", "type_in_word"),
    ("bold selected text in word", "word_bold"),
    ("italic selected text in word", "word_italic"),
    ("underline selected text in word", "word_underline"),
    ("increase font size in word", "word_font_up"),
    ("decrease font size in word", "word_font_down"),
    ("align text left in word", "word_align_left"),
    ("align text center in word", "word_align_center"),
    ("align text right in word", "word_align_right"),
    ("align text justify in word", "word_align_justify"),
    ("insert page break in word", "word_page_break"),
    ("insert table in word", "word_insert_table"),
    ("find text in document", "word_find"),
    ("replace text in document", "word_replace"),
    ("print document", "print_doc", ),
    ("zoom in document", "word_zoom_in"), ("zoom out document", "word_zoom_out"),
    ("check spelling in document", "word_spellcheck"),
    ("create new excel workbook", "new_excel_workbook"),
    ("create new powerpoint presentation", "new_ppt"),
    ("open new email", "new_email"), ("send email", "send_email", "confirm"),
]
for item in office_cmds:
    phrase, act = item[0], item[1]
    risk = item[2] if len(item) > 2 else "safe"
    add(phrase, "Office and Documents", act, risk)

# --- 12. Files, search and productivity ---
file_cmds = [
    ("search for file <file>", "search_file"),
    ("search files for <text>", "search_file"),
    ("create new folder", "create_folder"),
    ("create new text file", "create_text_file"),
    ("rename file", "rename_file", "confirm"),
    ("delete file", "delete_file", "confirm"),
    ("move file to recycle bin", "recycle_file", "confirm"),
    ("open downloads", "open_folder"), ("open documents", "open_folder"),
    ("open pictures", "open_folder"), ("open videos", "open_folder"),
    ("open recent files", "open_recent"),
    ("sort files by name", "sort_by_name"), ("sort files by date", "sort_by_date"),
    ("show hidden files", "show_hidden_files"), ("hide hidden files", "hide_hidden_files"),
    ("copy file path", "copy_file_path"),
    ("open calculator", "launch_app"), ("open sticky notes", "launch_app"),
    ("set timer for <number> minutes", "set_timer"),
    ("set alarm", "set_alarm"), ("open alarm", "launch_app"),
    ("check internet speed", "internet_speed"),
    ("show ip address", "show_ip"),
]
for item in file_cmds:
    phrase, act = item[0], item[1]
    risk = item[2] if len(item) > 2 else "safe"
    add(phrase, "Files, Search and Productivity", act, risk)

# --- 13. Extra MS Word commands (user-requested expansion) ---
word_extra = [
    ("insert header in word", "word_insert_header"),
    ("insert footer in word", "word_insert_footer"),
    ("insert page number in word", "word_insert_page_number"),
    ("add bullet list in word", "word_bullet_list"),
    ("add numbered list in word", "word_numbered_list"),
    ("remove bullet list in word", "word_remove_list"),
    ("increase indent in word", "word_indent_up"),
    ("decrease indent in word", "word_indent_down"),
    ("insert image in word", "word_insert_image"),
    ("insert hyperlink in word", "word_insert_hyperlink"),
    ("insert date in word", "word_insert_date"),
    ("insert time in word", "word_insert_time"),
    ("change line spacing to single in word", "word_spacing_single"),
    ("change line spacing to double in word", "word_spacing_double"),
    ("set line spacing to 1.5 in word", "word_spacing_1_5"),
    ("save document as pdf", "save_doc_as_pdf"),
    ("export document as pdf", "save_doc_as_pdf"),
    ("open recent document in word", "word_open_recent"),
    ("close all word documents", "close_all_word_docs"),
    ("select paragraph in word", "word_select_paragraph"),
    ("select line in word", "word_select_line"),
    ("go to start of document", "doc_start"),
    ("go to end of document", "doc_end"),
    ("insert comment in word", "word_insert_comment"),
    ("track changes on in word", "word_track_on"),
    ("track changes off in word", "word_track_off"),
    ("show word count", "word_count"),
    ("insert horizontal line in word", "word_insert_line"),
    ("clear formatting in word", "word_clear_formatting"),
    ("change text color to red in word", "word_color_red"),
    ("change text color to blue in word", "word_color_blue"),
    ("change text color to black in word", "word_color_black"),
    ("highlight selected text in word", "word_highlight"),
    ("create table of contents in word", "word_toc_create"),
    ("update table of contents in word", "word_toc_update"),
    ("insert cover page in word", "word_cover_page"),
    ("set margins to narrow in word", "word_margins_narrow"),
    ("set margins to normal in word", "word_margins_normal"),
    ("change page orientation to portrait in word", "word_portrait"),
    ("change page orientation to landscape in word", "word_landscape"),
    ("insert section break in word", "word_section_break"),
    ("insert footnote in word", "word_footnote"),
    ("insert endnote in word", "word_endnote"),
    ("change font size to <number> in word", "word_font_size"),
    ("insert new paragraph in word", "word_new_paragraph"),
]
for phrase, act in word_extra:
    risk = "confirm" if act == "close_all_word_docs" else "safe"
    add(phrase, "MS Word Extra", act, risk)

# --- 14. Extra daily Office commands ---
daily_office = [
    ("insert new row in excel", "excel_insert_row"),
    ("insert new column in excel", "excel_insert_column"),
    ("delete row in excel", "excel_delete_row"),
    ("delete column in excel", "excel_delete_column"),
    ("freeze top row in excel", "excel_freeze_top"),
    ("unfreeze panes in excel", "excel_unfreeze"),
    ("sort ascending in excel", "excel_sort_asc"),
    ("sort descending in excel", "excel_sort_desc"),
    ("apply filter in excel", "excel_filter_on"),
    ("remove filter in excel", "excel_filter_off"),
    ("sum selected cells in excel", "excel_sum"),
    ("format cells as currency in excel", "excel_currency"),
    ("format cells as percentage in excel", "excel_percent"),
    ("start slideshow in powerpoint", "ppt_slideshow"),
    ("next slide", "ppt_next"), ("previous slide", "ppt_previous"),
    ("go to first slide", "ppt_first"), ("go to last slide", "ppt_last"),
    ("reply to email", "email_reply"), ("forward email", "email_forward"),
    ("mark email as read", "email_mark_read"),
    ("archive email", "email_archive"),
]
for phrase, act in daily_office:
    risk = "confirm" if act in ("excel_delete_row", "excel_delete_column") else "safe"
    add(phrase, "Daily Office", act, risk)

# --- 15. Daily voice control and everyday computer use ---
daily_cmds = [
    ("start listening", "voice_start"), ("stop listening", "voice_stop"),
    ("pause listening", "voice_pause"), ("resume listening", "voice_resume"),
    ("start dictation", "dictation_start"), ("stop dictation", "dictation_stop"),
    ("what did you hear", "show_last_transcript"),
    ("show command list", "show_commands"), ("search commands for <text>", "search_commands"),
    ("open command history", "open_history_log"),
    ("clear command history", "clear_history"),
    ("open start menu", "open_start"), ("open taskbar search", "open_search_ui"),
    ("open action center", "open_action_center"),
    ("open quick settings", "open_quick_settings"),
    ("open notification center", "open_notifications_ui"),
    ("convert text to uppercase", "text_upper"),
    ("convert text to lowercase", "text_lower"),
    ("speak selected text", "speak_selection"),
    ("set default browser to chrome", "set_default_browser_chrome"),
    ("set default browser to edge", "set_default_browser_edge"),
    ("set default browser to brave", "set_default_browser_brave"),
    ("set default ide to visual studio code", "set_default_ide_vscode"),
    ("set default ide to pycharm", "set_default_ide_pycharm"),
    ("repeat last command", "repeat_last"),
]
for phrase, act in daily_cmds:
    risk = "confirm" if act == "clear_history" else "safe"
    add(phrase, "Daily Use and Voice Control", act, risk)

# Deduplicate by phrase, keeping first occurrence
seen = set()
unique = []
for entry in commands:
    if entry[0] not in seen:
        seen.add(entry[0])
        unique.append(entry)
commands = unique

lines = []
lines.append("# ARK Laptop Agent — Fixed Command Registry (v1, No LLM)")
lines.append("")
lines.append("This is the command list for the small, fast, fixed-command laptop agent.")
lines.append("The agent only executes phrases in this file. Anything else gets the reply")
lines.append("'I do not recognise that command' and does nothing. That is intentional:")
lines.append("it is what keeps the agent fast, small, and safe without an LLM.")
lines.append("")
lines.append("- **Voice and text share one parser.** A typed command and the same spoken")
lines.append("  command must produce the same action.")
lines.append("- **<text>, <number>, <website> and <file> are spoken variables**, not free")
lines.append("  prompts. Example: 'set volume to 50 percent' fills <number> with 50.")
lines.append("- **Risk: confirm** means the agent must ask 'Are you sure?' and wait for a")
lines.append("  clear yes before acting. Safe commands run immediately.")
lines.append("- **Custom ARK apps** (arkmedia, arksnap, arkdownload) are placeholders here:")
lines.append("  their real .exe paths go in the app registry when those apps are installed.")
lines.append("- **'Open notebook'** from the user's list is mapped to Jupyter Notebook.")
lines.append("  'INTELLIGI' is mapped to IntelliJ IDEA.")
lines.append("")
lines.append(f"## Total commands: {len(commands)}")
lines.append("")
current_cat = None
for i, (phrase, category, action, risk) in enumerate(commands, start=1):
    if category != current_cat:
        current_cat = category
        lines.append(f"### {category}")
        lines.append("")
    lines.append(f"{i}. {phrase} — action: {action} | risk: {risk}")
lines.append("")
lines.append("## How to add a command later")
lines.append("")
lines.append("1. Add one line above, in the right category.")
lines.append("2. Add the matching handler in the code (one function, one action).")
lines.append("3. Add it to the voice grammar list, so the speech recogniser can hear it.")
lines.append("4. Test it by typing it first, then by voice. Never ship a voice-only command.")
lines.append("")

out.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {out} with {len(commands)} commands")
