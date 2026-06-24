from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "defaults.json"
DEFAULT_ASSET_DIR = PROJECT_ROOT / "assets"


@dataclass(frozen=True)
class TimingConfig:
    frame_ms: int = 420
    click_window_ms: int = 280
    emote_ms: int = 1200
    inactive_walk_seconds: int = 45
    sleep_wake_window_ms: int = 2000
    walk_duration_ms: int = 6000
    behavior_check_ms: int = 1000


@dataclass(frozen=True)
class MovementConfig:
    walk_speed_px: int = 4
    walk_probability_per_check: float = 0.06


@dataclass(frozen=True)
class AppConfig:
    initial_anchor: str = "bottom_right"
    temp_quit_key: str = "Esc"
    enable_emotes: bool = False
    pet_size: int = 180
    asset_dir: Path = DEFAULT_ASSET_DIR
    timing: TimingConfig = field(default_factory=TimingConfig)
    movement: MovementConfig = field(default_factory=MovementConfig)
    activity_weights: dict[str, float] = field(
        default_factory=lambda: {"read": 1.0, "type": 1.0, "ball": 1.0, "sleep": 1.0}
    )
    emotes: tuple[str, ...] = ("heart", "note", "question", "anger", "sweat")


def load_config(path: str | Path | None = None) -> AppConfig:
    data: dict[str, Any] = {}
    if DEFAULT_CONFIG_PATH.exists():
        data = _read_json(DEFAULT_CONFIG_PATH)
    if path is not None:
        data = _deep_merge(data, _read_json(Path(path)))

    timing = {**TimingConfig().__dict__, **data.get("timing", {})}
    movement = {**MovementConfig().__dict__, **data.get("movement", {})}
    asset_dir = Path(data.get("asset_dir", DEFAULT_ASSET_DIR))
    if not asset_dir.is_absolute():
        asset_dir = PROJECT_ROOT / asset_dir

    return AppConfig(
        initial_anchor=data.get("initial_anchor", AppConfig.initial_anchor),
        temp_quit_key=data.get("temp_quit_key", AppConfig.temp_quit_key),
        enable_emotes=bool(data.get("enable_emotes", AppConfig.enable_emotes)),
        pet_size=int(data.get("pet_size", AppConfig.pet_size)),
        asset_dir=asset_dir,
        timing=TimingConfig(**timing),
        movement=MovementConfig(**movement),
        activity_weights=dict(data.get("activity_weights", AppConfig().activity_weights)),
        emotes=tuple(data.get("emotes", AppConfig().emotes)),
    )


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
