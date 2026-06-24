from __future__ import annotations

from pathlib import Path
import random
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from xiaowang_pet.config import AppConfig, MovementConfig, TimingConfig  # noqa: E402
from xiaowang_pet.state_machine import PetStateMachine  # noqa: E402
from xiaowang_pet.states import ACTIVITY_STATES, PetState  # noqa: E402


class PetStateMachineTests(unittest.TestCase):
    def test_idle_double_click_enters_random_activity(self) -> None:
        machine = PetStateMachine()

        transition = machine.handle_double_click(1000, random.Random(1))

        self.assertIsNotNone(transition)
        self.assertEqual(transition.from_state, PetState.IDLE)
        self.assertIn(machine.state, ACTIVITY_STATES)

    def test_activity_double_click_returns_idle(self) -> None:
        machine = PetStateMachine()
        machine.change_state(PetState.READ, 1000, reason="test")

        transition = machine.handle_double_click(1200, random.Random(1))

        self.assertIsNotNone(transition)
        self.assertEqual(transition.to_state, PetState.IDLE)
        self.assertEqual(machine.state, PetState.IDLE)

    def test_sleep_needs_two_double_click_groups(self) -> None:
        machine = PetStateMachine()
        machine.change_state(PetState.SLEEP, 1000, reason="test")

        first = machine.handle_double_click(1500, random.Random(1))
        second = machine.handle_double_click(3200, random.Random(1))

        self.assertIsNone(first)
        self.assertIsNotNone(second)
        self.assertEqual(second.to_state, PetState.IDLE)

    def test_drag_returns_to_previous_state(self) -> None:
        machine = PetStateMachine()
        machine.change_state(PetState.BALL, 1000, reason="test")

        started = machine.begin_drag(1100)
        ended = machine.end_drag(1200)

        self.assertEqual(started.to_state, PetState.DRAG)
        self.assertEqual(ended.to_state, PetState.BALL)
        self.assertEqual(machine.state, PetState.BALL)

    def test_idle_timeout_can_trigger_walk(self) -> None:
        config = AppConfig(
            timing=TimingConfig(inactive_walk_seconds=1),
            movement=MovementConfig(walk_probability_per_check=1.0),
        )
        machine = PetStateMachine(config)
        machine.handle_single_click(0)

        transition = machine.maybe_start_walk(1500, random.Random(1))

        self.assertIsNotNone(transition)
        self.assertEqual(transition.to_state, PetState.WALK)

    def test_walk_finishes_after_duration(self) -> None:
        config = AppConfig(timing=TimingConfig(walk_duration_ms=500))
        machine = PetStateMachine(config)
        machine.change_state(PetState.WALK, 1000, reason="test")

        transition = machine.tick(1600)

        self.assertIsNotNone(transition)
        self.assertEqual(transition.to_state, PetState.IDLE)


if __name__ == "__main__":
    unittest.main()
