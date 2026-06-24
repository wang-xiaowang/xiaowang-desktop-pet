from __future__ import annotations


def main() -> int:
    try:
        from .window import run_app
    except ModuleNotFoundError as exc:
        if exc.name == "PySide6":
            raise SystemExit(
                "PySide6 is not installed. Run `python -m pip install -r requirements.txt` "
                "inside the project, then start again with `python -m xiaowang_pet`."
            ) from exc
        raise

    return run_app()
