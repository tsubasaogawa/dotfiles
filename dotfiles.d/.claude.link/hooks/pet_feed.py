#!/usr/bin/env python3
import os
import time

from hook_utils import load_json, read_stdin_json, save_json_atomically

STATE_PATH = os.path.expanduser("~/.claude/pet-state.json")
DEFAULT_STATE = {"last_tool_ts": 0, "running": False, "running_since": 0}


def load():
    return load_json(STATE_PATH, DEFAULT_STATE)


def save(state):
    save_json_atomically(STATE_PATH, state)


def main():
    data = read_stdin_json()
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
