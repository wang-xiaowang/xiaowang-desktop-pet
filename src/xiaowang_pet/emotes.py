from __future__ import annotations

import random

from .config import AppConfig
from .states import PetState


EMOTE_TEXT = {
    "heart": "\u2764\ufe0f",
    "note": "\U0001f3b5",
    "question": "\u2753",
    "anger": "\U0001f4a2",
    "sweat": "\U0001f4a6",
    "zzz": "Zzz",
}


def choose_emote(
    state: PetState, config: AppConfig, rng: random.Random | None = None
) -> str:
    if state == PetState.SLEEP:
        return "zzz"
    chooser = rng or random
    return chooser.choice(config.emotes)


def emote_text(name: str) -> str:
    return EMOTE_TEXT.get(name, name)
