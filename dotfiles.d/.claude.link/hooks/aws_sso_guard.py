"""PreToolUse hook: AWS SSO のセッション切れを検知し、AWS を使うコマンドの前で止める。

Bash / PowerShell ツールのコマンドに `aws <subcommand>` か `terraform <subcommand>` が含まれるとき、
WSL の aws_sso_session_expiry.bash を source して `_aws_sso_max_remaining_minutes` で残り分数を得る。
判定は SSO トークンキャッシュの期限を読むだけで、AWS API は呼ばない。
残りが 0 分以下なら拒否し、ログイン手順をメッセージで渡す。
判定できないとき (キャッシュ無し、WSL 停止など) は素通しし、systemMessage で知らせる。

- `aws sso ...` / `aws configure ...` / `terraform fmt` などの認証不要なコマンドは検査しない
- 残り分数から期限の時刻を記録し、その時刻までは WSL を呼ばない
- 内蔵ブラウザは組織ポリシーで awsapps.com がブロックされる (2026-10-19 確認)。承認ページは既定ブラウザで開く

背景: aws_sso_session_expiry.bash は PROMPT_COMMAND で動くため、Claude Code の非対話シェルでは発火しない。
判定ロジックを二重に持たないよう、関数だけを借りる (2026-10-19)。
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

from hook_utils import load_json, read_stdin_json, save_json_atomically

LOGIN_PROFILE = "openwork-jp-dev-member"
EXPIRY_SCRIPT = "/home/t_ogawa/.dotfiles.d/.bash_profile.d/aws_sso_session_expiry.bash"
CHECK_TIMEOUT = 15
STATE_PATH = Path.home() / ".claude" / "aws-sso-guard.json"

INVOCATION_RE = re.compile(r"(?<![\w.-])(aws|terraform)(?:\.exe)?\s+([\w-]+)", re.IGNORECASE)
EXEMPT_SUBCOMMANDS = {
    "aws": {"sso", "configure", "help", "--version"},
    "terraform": {"fmt", "validate", "version", "-version", "--version", "-help", "--help"},
}

DENY_MESSAGE = f"""AWS SSO のセッションが切れています。次の手順でログインしてから元のコマンドを再実行してください。

1. Bash ツールで `aws sso login --profile {LOGIN_PROFILE} --no-browser` を run_in_background で起動する
2. 出力ファイルを Read し、`user_code=` 付きの URL とコードを取り出す
3. PowerShell ツールで `Start-Process '<URL>'` を実行し、ユーザーの既定ブラウザで承認ページを開く。内蔵ブラウザは組織ポリシーで awsapps.com がブロックされるので使わない
4. ユーザーに、既定ブラウザでコードを確かめて承認するよう伝える。IdP のログインや MFA が出たらユーザーに入力してもらう。パスワード入力と承認クリックは AI が代行しない
5. バックグラウンドタスクの完了通知を待つ。`Successfully logged into Start URL` が出たら成功
6. 元のコマンドを再実行する。ブラウザのタブはユーザーが閉じる"""


def needs_check(command: str) -> bool:
    for match in INVOCATION_RE.finditer(command):
        tool, subcommand = match.group(1).lower(), match.group(2).lower()
        if subcommand not in EXEMPT_SUBCOMMANDS[tool]:
            return True
    return False


def remaining_minutes(now: int) -> tuple[int | None, str]:
    """(残り分数, 判定できなかった理由) を返す。"""
    command = [
        "wsl.exe", "-d", "Ubuntu1804", "-e", "bash", "-c",
        'source "$1" && _aws_sso_max_remaining_minutes "$2"', "aws-sso-guard", EXPIRY_SCRIPT, str(now),
    ]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=CHECK_TIMEOUT, stdin=subprocess.DEVNULL,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return None, str(error)
    output = result.stdout.strip()
    if result.returncode == 0 and re.fullmatch(r"-?\d+", output):
        return int(output), ""
    if result.returncode == 1 and not output and not result.stderr.strip():
        return None, "SSO トークンのキャッシュがありません"
    return None, (result.stderr.strip() or output or f"exit {result.returncode}")


def emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def main() -> None:
    payload = read_stdin_json()
    if payload.get("tool_name") not in ("Bash", "PowerShell"):
        return
    command = (payload.get("tool_input") or {}).get("command") or ""
    if not needs_check(command):
        return

    now = int(time.time())
    if now < load_json(STATE_PATH, {"valid_until": 0}).get("valid_until", 0):
        return

    minutes, reason = remaining_minutes(now)
    if minutes is None:
        emit({"systemMessage": f"aws-sso-guard: SSO の状態を判定できなかったので素通しにしました ({reason[:200]})"})
        return
    if minutes > 0:
        save_json_atomically(STATE_PATH, {"valid_until": now + minutes * 60})
        return
    emit({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": DENY_MESSAGE,
        }
    })


if __name__ == "__main__":
    main()
    sys.exit(0)
