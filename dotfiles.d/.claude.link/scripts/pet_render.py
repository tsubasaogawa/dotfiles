#!/usr/bin/env python3
import json
import os
import random
import time

STATE_PATH = os.path.expanduser("~/.claude/pet-state.json")
SLEEP_THRESHOLD_SEC = 5 * 60
STALE_RUNNING_SEC = 60

CHICK_FRAMES = ["\U0001F424", "\U0001F425"]

FRAMES_NORMAL = CHICK_FRAMES
FRAMES_INVESTIGATING = [c + "\U0001F50D" for c in CHICK_FRAMES]
FRAMES_SLEEPING = [c + "\U0001F4A4" for c in CHICK_FRAMES]


def load():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def main():
    state = load()
    now = time.time()
    running = state.get("running", False)
    running_since = state.get("running_since", 0)
    last_tool_ts = state.get("last_tool_ts", 0)

    if running and (now - running_since) < STALE_RUNNING_SEC:
        frames = FRAMES_INVESTIGATING
    elif not last_tool_ts or (now - last_tool_ts) >= SLEEP_THRESHOLD_SEC:
        frames = FRAMES_SLEEPING
    else:
        frames = FRAMES_NORMAL

    print(random.choice(frames))


if __name__ == "__main__":
    main()
