"""Shared JSON and state-file helpers for Claude hooks."""

import json
import os
import sys
from pathlib import Path
from typing import Any


def read_stdin_json(default: dict[str, Any] | None = None) -> dict[str, Any]:
    """Read a JSON object from standard input, returning default on invalid input."""
    try:
        data = json.load(sys.stdin)
    except (OSError, ValueError, json.JSONDecodeError):
        return dict(default or {})
    return data if isinstance(data, dict) else dict(default or {})


def load_json(path: str | Path, default: dict[str, Any]) -> dict[str, Any]:
    """Load a JSON object from path, returning a fresh default when unavailable."""
    try:
        with open(path, encoding="utf-8") as state_file:
            data = json.load(state_file)
    except (OSError, ValueError, json.JSONDecodeError):
        return dict(default)
    return data if isinstance(data, dict) else dict(default)


def load_json_list(path: str | Path) -> list[Any]:
    """Load a JSON list from path, returning an empty list when unavailable."""
    try:
        with open(path, encoding="utf-8") as state_file:
            data = json.load(state_file)
    except (OSError, ValueError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def save_json_atomically(path: str | Path, data: Any) -> None:
    """Replace a JSON file atomically, creating its parent directory when needed."""
    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = state_path.with_name(f"{state_path.name}.tmp")
    with temporary_path.open("w", encoding="utf-8") as state_file:
        json.dump(data, state_file)
    os.replace(temporary_path, state_path)
