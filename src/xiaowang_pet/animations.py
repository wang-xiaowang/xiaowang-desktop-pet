from __future__ import annotations

from dataclasses import dataclass, field

from .states import PetState


STATE_LOOPS: dict[PetState, tuple[str, ...]] = {
    PetState.IDLE: ("idle_01", "idle_02"),
    PetState.READ: ("read_01", "read_02"),
    PetState.TYPE: ("type_01", "type_02", "type_03"),
    PetState.BALL: ("ball_01", "ball_02", "ball_03"),
    PetState.SLEEP: ("sleep_01", "sleep_02"),
    PetState.WALK: ("walk_01", "walk_02"),
    PetState.DRAG: ("drag",),
}

TRANSITIONS: dict[tuple[PetState, PetState], tuple[str, ...]] = {
    (PetState.IDLE, PetState.READ): ("t_idle_read_01", "t_idle_read_02"),
    (PetState.IDLE, PetState.TYPE): ("t_idle_type_01", "t_idle_type_02"),
    (PetState.IDLE, PetState.BALL): ("t_idle_ball_01", "t_idle_ball_02"),
    (PetState.IDLE, PetState.SLEEP): ("t_idle_sleep_01", "t_idle_sleep_02"),
    (PetState.IDLE, PetState.WALK): ("t_idle_walk_01", "t_idle_walk_02"),
}


def loop_frames(state: PetState) -> tuple[str, ...]:
    return STATE_LOOPS.get(state, STATE_LOOPS[PetState.IDLE])


def transition_frames(from_state: PetState, to_state: PetState) -> tuple[str, ...]:
    direct = TRANSITIONS.get((from_state, to_state))
    if direct:
        return direct

    reverse = TRANSITIONS.get((to_state, from_state))
    if reverse:
        return tuple(reversed(reverse))

    return ()


@dataclass
class SequencePlayer:
    state: PetState = PetState.IDLE
    _sequence: tuple[str, ...] = field(default_factory=lambda: loop_frames(PetState.IDLE))
    _index: int = 0
    _then_loop: PetState | None = None

    def set_loop(self, state: PetState) -> None:
        self.state = state
        self._sequence = loop_frames(state)
        self._index = 0
        self._then_loop = None

    def play_transition(self, from_state: PetState, to_state: PetState) -> None:
        frames = transition_frames(from_state, to_state)
        if not frames:
            self.set_loop(to_state)
            return

        self.state = to_state
        self._sequence = frames
        self._index = 0
        self._then_loop = to_state

    def next_frame(self) -> str:
        if not self._sequence:
            self.set_loop(self.state)

        frame = self._sequence[self._index]
        self._index += 1

        if self._index >= len(self._sequence):
            if self._then_loop is None:
                self._index = 0
            else:
                self.set_loop(self._then_loop)

        return frame
