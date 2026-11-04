"""Animated character state machine. No GUI code lives here, so the
animation logic can be unit-tested without a display.

States:
  idle      blinking, calm, waiting
  listening ears up, mouth closed, waiting for speech
  working   gear turning, eyes looking around, task in progress
  speaking  mouth opening and closing in a talking rhythm
  success   happy eyes, small smile
  error     worried eyes, flat mouth

next_frame(state, tick) returns a plain description of one frame.
gui.py turns that description into canvas shapes. Keeping the logic
here means a future web or PySide interface can reuse the same
character without copying animation code.
"""
from __future__ import annotations

from dataclasses import dataclass

STATES = ("idle", "listening", "working", "speaking", "success", "error")


@dataclass(frozen=True)
class CharacterFrame:
    mouth_open: bool
    blinking: bool
    gear_angle: int  # 0-359, only meaningful in "working"
    ears_up: bool
    happy: bool
    worried: bool


def next_frame(state: str, tick: int) -> CharacterFrame:
    if state not in STATES:
        state = "idle"
    return CharacterFrame(
        mouth_open=(state == "speaking" and tick % 2 == 0),
        blinking=(tick % 25 == 0),
        gear_angle=(tick * 15) % 360 if state == "working" else 0,
        ears_up=(state in ("listening", "working")),
        happy=(state == "success"),
        worried=(state == "error"),
    )


def state_message(state: str) -> str:
    return {
        "idle": "Ready. Type a command, or press Listen.",
        "listening": "Listening...",
        "working": "Working on it...",
        "speaking": "Speaking...",
        "success": "Done.",
        "error": "That did not work. Try again, or type it.",
    }.get(state, "Ready.")
