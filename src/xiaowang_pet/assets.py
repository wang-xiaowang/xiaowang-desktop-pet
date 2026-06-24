from __future__ import annotations

from pathlib import Path


SEARCH_SUBDIRS = ("body", "transitions", "emotes")


def find_asset(asset_dir: Path, frame_name: str) -> Path | None:
    for subdir in SEARCH_SUBDIRS:
        path = asset_dir / subdir / f"{frame_name}.png"
        if path.exists():
            return path
    return None


def expected_body_assets() -> tuple[str, ...]:
    return (
        "idle_01.png",
        "idle_02.png",
        "read_01.png",
        "read_02.png",
        "type_01.png",
        "type_02.png",
        "type_03.png",
        "ball_01.png",
        "ball_02.png",
        "ball_03.png",
        "ball_prop.png",
        "sleep_01.png",
        "sleep_02.png",
        "walk_01.png",
        "walk_02.png",
        "drag.png",
    )
