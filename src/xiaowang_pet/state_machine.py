from __future__ import annotations

from dataclasses import dataclass
import random

from .config import AppConfig
from .states import ACTIVITY_STATES, PetState


@dataclass(frozen=True)
class Transition:
    from_state: PetState
    to_state: PetState
    reason: str


class PetStateMachine:
    """Pure state logic. GUI events call this; this class never imports Qt."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or AppConfig()
        self.state = PetState.IDLE
        self.last_interaction_ms = 0
        self._before_drag: PetState | None = None
        self._last_sleep_double_click_ms: int | None = None
        self._walk_started_ms: int | None = None

    def handle_single_click(self, now_ms: int) -> None:
        self._touch(now_ms)

    def handle_double_click(
        self, now_ms: int, rng: random.Random | None = None
    ) -> Transition | None:
        self._touch(now_ms)

        if self.state == PetState.SLEEP:
            return self._handle_sleep_double_click(now_ms)

        if self.state == PetState.IDLE:
            return self.change_state(
                self._choose_activity(rng or random),
                now_ms,
                reason="idle_double_click_random_activity",
            )

        if self.state in (PetState.READ, PetState.TYPE, PetState.BALL, PetState.WALK):
            return self.change_state(PetState.IDLE, now_ms, reason="double_click_return_idle")

        return None

    def maybe_start_walk(
        self, now_ms: int, rng: random.Random | None = None
    ) -> Transition | None:
        if self.state != PetState.IDLE:
            return None

        inactive_ms = now_ms - self.last_interaction_ms
        threshold_ms = self.config.timing.inactive_walk_seconds * 1000
        if inactive_ms < threshold_ms:
            return None

        chooser = rng or random
        if chooser.random() > self.config.movement.walk_probability_per_check:
            return None

        return self.change_state(PetState.WALK, now_ms, reason="idle_inactive_auto_walk")

    def tick(self, now_ms: int) -> Transition | None:
        if self.state != PetState.WALK or self._walk_started_ms is None:
            return None

        walked_ms = now_ms - self._walk_started_ms
        if walked_ms >= self.config.timing.walk_duration_ms:
            return self.change_state(PetState.IDLE, now_ms, reason="walk_finished")
        return None

    def begin_drag(self, now_ms: int) -> Transition | None:
        self._touch(now_ms)
        if self.state == PetState.DRAG:
            return None

        self._before_drag = self.state
        return self.change_state(PetState.DRAG, now_ms, reason="drag_begin")

    def end_drag(self, now_ms: int) -> Transition | None:
        self._touch(now_ms)
        target = self._before_drag or PetState.IDLE
        self._before_drag = None
        return self.change_state(target, now_ms, reason="drag_release")

    def change_state(self, target: PetState, now_ms: int, reason: str) -> Transition | None:
        if target == self.state:
            return None

        old = self.state
        self.state = target
        self._last_sleep_double_click_ms = None
        self._walk_started_ms = now_ms if target == PetState.WALK else None
        return Transition(old, target, reason)

    def _handle_sleep_double_click(self, now_ms: int) -> Transition | None:
        last = self._last_sleep_double_click_ms
        self._last_sleep_double_click_ms = now_ms
        if last is None:
            return None

        if now_ms - last <= self.config.timing.sleep_wake_window_ms:
            self._last_sleep_double_click_ms = None
            return self.change_state(PetState.IDLE, now_ms, reason="sleep_two_double_clicks")
        return None

    def _choose_activity(self, rng: random.Random) -> PetState:
        weights = self.config.activity_weights
        states = list(ACTIVITY_STATES)
        state_weights = [float(weights.get(state.value, 1.0)) for state in states]
        return rng.choices(states, weights=state_weights, k=1)[0]

    def _touch(self, now_ms: int) -> None:
        self.last_interaction_ms = now_ms
