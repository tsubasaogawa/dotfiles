#!/usr/bin/env python3
import json
import os
import sys
import time

STATE_PATH = os.path.expanduser("~/.claude/pet-state.json")
DEFAULT_STATE = {"last_tool_ts": 0, "running": False, "running_since": 0}


def load():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return dict(DEFAULT_STATE)


def save(state):
    tmp_path = STATE_PATH + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(state, f)
    os.replace(tmp_path, STATE_PATH)


def main():
    try:
        data = json.load(sys.stdin)
    except (OSError, json.JSONDecodeError, ValueError):
        data = {}

    event = data.get("hook_event_name", "")
    state = load()
    now = time.time()

    if event == "PreToolUse":
        state["running"] = True
        state["running_since"] = now
    else:
        state["running"] = False
        state["last_tool_ts"] = now

    save(state)


if __name__ == "__main__":
    main()
