#!/usr/bin/env python3

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).parent
HOOKS_DIR = ROOT / "dotfiles.d" / ".claude.link" / "hooks"
SCRIPTS_DIR = ROOT / "dotfiles.d" / ".claude.link" / "scripts"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestClaudeHooks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(HOOKS_DIR))
        cls.hook_utils = __import__("hook_utils")
        cls.check_format_rules = load_module(
            "test_check_format_rules", HOOKS_DIR / "check_format_rules.py"
        )
        cls.karpathy_script_guard = load_module(
            "test_karpathy_script_guard", HOOKS_DIR / "karpathy_script_guard.py"
        )
        cls.pet_feed = load_module("test_pet_feed", HOOKS_DIR / "pet_feed.py")
        cls.pet_render = load_module("test_pet_render", SCRIPTS_DIR / "pet_render.py")

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(str(HOOKS_DIR))

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_path = Path(self.temp_dir.name) / "claude" / "pet-state.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_format_rule_hook_parses_write_input_and_reports_to_stderr(self):
        payload = {
            "tool_name": "Write",
            "tool_input": {"content": "日本語English"},
        }
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch.object(self.check_format_rules.sys, "stdin", io.StringIO(json.dumps(payload))),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            with self.assertRaises(SystemExit) as exit_info:
                self.check_format_rules.main()

        self.assertEqual(exit_info.exception.code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("スペースがありません", stderr.getvalue())

    def test_pet_feed_uses_default_state_for_missing_or_invalid_input(self):
        with (
            patch.object(self.pet_feed, "STATE_PATH", str(self.state_path)),
            patch.object(self.hook_utils.sys, "stdin", io.StringIO("invalid json")),
            patch.object(self.pet_feed.time, "time", return_value=123.0),
        ):
            self.pet_feed.main()

        self.assertEqual(
            json.loads(self.state_path.read_text()),
            {"last_tool_ts": 123.0, "running": False, "running_since": 0},
        )

    def test_pet_renderer_uses_default_state_for_corrupt_file(self):
        self.state_path.parent.mkdir(parents=True)
        self.state_path.write_text("{not json")

        with (
            patch.object(self.pet_render, "STATE_PATH", str(self.state_path)),
            patch.object(self.pet_render.random, "choice", return_value="sleeping"),
            patch.object(self.pet_render.time, "time", return_value=123.0),
            contextlib.redirect_stdout(io.StringIO()) as stdout,
        ):
            self.pet_render.main()

        self.assertEqual(stdout.getvalue(), "sleeping\n")

    def test_karpathy_guard_writes_expected_pre_tool_use_output(self):
        guidelines_path = Path(self.temp_dir.name) / "guidelines.md"
        guidelines_path.write_text("Follow the guideline.")
        guard_state_dir = Path(self.temp_dir.name) / "state"
        payload = {
            "session_id": "session-1",
            "tool_input": {"file_path": "/tmp/example.py"},
        }
        stdout = io.StringIO()

        with (
            patch.object(self.karpathy_script_guard, "GUIDELINES", str(guidelines_path)),
            patch.object(self.karpathy_script_guard, "STATE_DIR", str(guard_state_dir)),
            patch.object(self.karpathy_script_guard.sys, "stdin", io.StringIO(json.dumps(payload))),
            contextlib.redirect_stdout(stdout),
        ):
            self.karpathy_script_guard.main()

        output = json.loads(stdout.getvalue())
        hook_output = output["hookSpecificOutput"]
        self.assertEqual(hook_output["hookEventName"], "PreToolUse")
        self.assertEqual(hook_output["permissionDecision"], "deny")
        self.assertIn("Follow the guideline.", hook_output["permissionDecisionReason"])
        self.assertEqual(
            json.loads((guard_state_dir / "session-1.json").read_text()),
            ["/tmp/example.py"],
        )

    def test_karpathy_guard_treats_corrupt_state_as_unseen(self):
        guidelines_path = Path(self.temp_dir.name) / "guidelines.md"
        guidelines_path.write_text("Follow the guideline.")
        guard_state_dir = Path(self.temp_dir.name) / "state"
        guard_state_dir.mkdir()
        (guard_state_dir / "session-1.json").write_text("{not json")
        payload = {
            "session_id": "session-1",
            "tool_input": {"file_path": "/tmp/example.py"},
        }

        with (
            patch.object(self.karpathy_script_guard, "GUIDELINES", str(guidelines_path)),
            patch.object(self.karpathy_script_guard, "STATE_DIR", str(guard_state_dir)),
            patch.object(self.karpathy_script_guard.sys, "stdin", io.StringIO(json.dumps(payload))),
            contextlib.redirect_stdout(io.StringIO()) as stdout,
        ):
            self.karpathy_script_guard.main()

        self.assertEqual(
            json.loads(stdout.getvalue())["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_bashrc_loads_with_a_temporary_home_and_missing_optional_commands(self):
        bashrc_dir = Path(self.temp_dir.name) / ".bashrc.d"
        shutil.copytree(ROOT / "dotfiles.d" / ".bashrc.d", bashrc_dir)
        (bashrc_dir / ".git-completion.bash").touch()
        (bashrc_dir / ".git-prompt.sh").touch()

        home_dir = Path(self.temp_dir.name) / "home"
        (home_dir / ".vim" / "bundle" / "neobundle.vim").mkdir(parents=True)
        bin_dir = Path(self.temp_dir.name) / "bin"
        bin_dir.mkdir()
        for command in ("curl", "sudo", "diff-highlight"):
            path = bin_dir / command
            path.write_text("#!/bin/sh\nexit 0\n")
            path.chmod(0o755)

        environment = os.environ | {
            "HOME": str(home_dir),
            "PATH": f"{bin_dir}:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        }
        result = subprocess.run(
            [
                "bash",
                "--noprofile",
                "--norc",
                "-c",
                f'source "{bashrc_dir / "main.bash"}"',
            ],
            capture_output=True,
            check=False,
            env=environment,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_statusline_preserves_its_plain_text_output_format(self):
        payload = {
            "model": {"display_name": "Claude"},
            "cost": {"total_cost_usd": 1.2},
        }
        home_dir = Path(self.temp_dir.name) / "status-home"
        result = subprocess.run(
            ["bash", str(ROOT / "dotfiles.d" / ".claude.link" / "statusline-command.sh")],
            capture_output=True,
            check=False,
            env=os.environ | {"HOME": str(home_dir)},
            input=json.dumps(payload),
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "$1.20 | Claude | ~\n")


if __name__ == "__main__":
    unittest.main()
