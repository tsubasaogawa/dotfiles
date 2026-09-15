#!/usr/bin/env python3
"""PreToolUse hook: inject Karpathy coding guidelines on the first script edit."""

import json
import os
import sys
import time

from hook_utils import load_json_list, read_stdin_json, save_json_atomically

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
GUIDELINES = os.path.join(HOOKS_DIR, "karpathy_guidelines.md")
STATE_DIR = os.path.join(HOOKS_DIR, "state", "karpathy_guard")
STATE_MAX_AGE = 7 * 24 * 60 * 60

SCRIPT_EXTS = {
    ".py", ".pyi", ".php", ".sh", ".bash", ".zsh",
    ".js", ".mjs", ".cjs", ".ts", ".rb", ".pl", ".lua",
}

AGENT_NAME = "script-craft"
REMINDER = (
    "This is a script file. Keep following the Karpathy guidelines already in context: "
    "state assumptions, minimum code, surgical changes, verifiable success criteria."
)
FOOTER = (
    "\n\n---\n\n"
    "This edit was blocked once so you would read the guidelines above.\n"
    "Review your change against them, then re-run the same edit, "
    "or delegate the work to the `{agent}` subagent."
).format(agent=AGENT_NAME)


def emit(payload):
    print(json.dumps(payload, ensure_ascii=False))


def state_path(session_id):
    safe = "".join(c for c in str(session_id) if c.isalnum() or c in "-_") or "unknown"
    return os.path.join(STATE_DIR, safe + ".json")


def prune_state():
    cutoff = time.time() - STATE_MAX_AGE
    for name in os.listdir(STATE_DIR):
        path = os.path.join(STATE_DIR, name)
        if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
            os.remove(path)


def main():
    data = read_stdin_json()
    if not data:
        return

    if data.get("agent_type") == AGENT_NAME:
        return

    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path")
    if not file_path:
        return

    if os.path.splitext(file_path)[1].lower() not in SCRIPT_EXTS:
        return

    path = state_path(data.get("session_id"))
    notified = set(load_json_list(path))

    if file_path in notified:
        emit({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": REMINDER,
        }})
        return

    with open(GUIDELINES, encoding="utf-8") as f:
        guidelines = f.read()

    notified.add(file_path)
    save_json_atomically(path, sorted(notified))

    emit({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": guidelines + FOOTER,
    }})


if __name__ == "__main__":
    try:
        prune_state()
    except OSError:
        pass
    try:
        main()
    except Exception:
        sys.exit(0)
