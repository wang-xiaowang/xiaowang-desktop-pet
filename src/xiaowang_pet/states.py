from __future__ import annotations

from enum import Enum


class PetState(str, Enum):
    IDLE = "idle"
    READ = "read"
    TYPE = "type"
    BALL = "ball"
    SLEEP = "sleep"
    WALK = "walk"
    DRAG = "drag"


ACTIVITY_STATES: tuple[PetState, ...] = (
    PetState.READ,
    PetState.TYPE,
    PetState.BALL,
    PetState.SLEEP,
)
