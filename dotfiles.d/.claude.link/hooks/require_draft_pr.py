"""PreToolUse hook: PR は Draft でしか作らせず、PR への書き込みは人間に任せる。

Bash / PowerShell ツールのコマンドを検査し、次の操作を拒否する。

- `gh pr create` で `--draft` (または `-d`) が無いもの
- `gh pr ready` で `--undo` が無いもの (Draft 解除)。Ready にするかどうかは人間が決める
- `gh pr comment` / `gh pr review` / `gh pr edit` (PR へのコメント・レビュー・編集)
- `gh issue comment` / `gh issue edit` (PR 番号を渡すと PR にも書き込めるため)
- `gh api` で `repos/{owner}/{repo}/pulls` / `issues` 配下へ GET 以外を送るもの、
  および PR、コメント、レビューを操作する GraphQL mutation

`gh.exe` やパス付きの呼び出し、`bash -c "..."` のようにクオートで包んだコマンドも検査する。
`$GH pr create` のような変数経由の呼び出しや、curl で API を直接叩く経路は検出できない。

背景: Open で PR を作ると CODEOWNERS によってレビュアーが自動アサインされ、
作成者本人が内容を確認する前にチームへレビュー依頼が飛ぶため (2026-10-07、INF-5626 の Stacked PR で発生)。
コメントや編集も、チームから見える場所に本人の確認前の文章が出る点で同じなので止める (2026-10-09 追加)。
"""

import json
import re
import shlex
import sys

from hook_utils import read_stdin_json

SEPARATORS = {"&&", "||", ";", "|", "&", "\n", "(", ")"}
QUOTES = "\"'"
MAX_DEPTH = 3

CREATE_MESSAGE = (
    "gh pr create は --draft を付けて実行してください。"
    "Open で作ると CODEOWNERS でレビュアーが自動アサインされ、"
    "本人の確認前にレビュー依頼が飛びます。Ready for review にするのは人間が行います"
)
READY_MESSAGE = (
    "gh pr ready (Draft 解除) は AI からは実行しません。"
    "レビュー依頼を出すタイミングは人間が決めます (gh pr ready --undo は可)"
)
WRITE_MESSAGE = (
    "PR へのコメント・レビュー・編集は AI からは実行しません。"
    "書き込みたい文面はチャットで提示し、投稿は人間が行います"
)
API_MESSAGE = (
    "gh api で PR / Issue を作成・コメント・編集する操作は AI からは実行しません (GET による読み取りは可)。"
    "PR は gh pr create --draft で作り、コメントや編集の文面はチャットで提示してください"
)

PR_WRITE_ACTIONS = {"comment", "review", "edit"}
ISSUE_WRITE_ACTIONS = {"comment", "edit"}
DRAFT_FLAGS = {"--draft", "-d", "--draft=true"}

API_FIELD_FLAGS = {"-f", "-F", "--field", "--raw-field", "--input"}
API_VALUE_FLAGS = {"-H", "--header", "-q", "--jq", "-t", "--template", "--hostname", "-p", "--preview", "--cache"}
API_REST_WRITE_RE = re.compile(r"^repos/[^/]+/[^/]+/(?:pulls|issues)(?:/|$)")
GRAPHQL_MUTATION_RE = re.compile(r"\bmutation\b")
GRAPHQL_TARGET_RE = re.compile(r"PullRequest|Comment|Review")


def _unquote(token: str) -> str:
    return token.strip(QUOTES)


def _lex(command: str) -> list[str]:
    """クオートを保ったままトークンに分ける。区切り記号と改行は独立したトークンにする。"""
    lexer = shlex.shlex(command, posix=False, punctuation_chars="();<>|&\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError:
        return command.split()


def _segments(tokens: list[str]) -> list[list[str]]:
    segments: list[list[str]] = [[]]
    for token in tokens:
        if token in SEPARATORS:
            segments.append([])
        else:
            segments[-1].append(token)
    return [segment for segment in segments if segment]


def _is_gh(token: str) -> bool:
    name = re.split(r"[\\/]", _unquote(token))[-1].lower()
    return name in ("gh", "gh.exe")


def _check_api(args: list[str]) -> str | None:
    method = None
    has_fields = False
    endpoint = None
    index = 0
    while index < len(args):
        arg = args[index]
        if arg in ("-X", "--method"):
            if index + 1 < len(args):
                method = _unquote(args[index + 1]).upper()
            index += 2
            continue
        if arg.startswith("--method="):
            method = _unquote(arg.split("=", 1)[1]).upper()
        elif arg.startswith("-X") and len(arg) > 2:
            method = _unquote(arg[2:]).upper()
        elif arg in API_FIELD_FLAGS:
            has_fields = True
            index += 2
            continue
        elif arg.startswith(("--field=", "--raw-field=", "--input=")) or (arg[:2] in ("-f", "-F") and len(arg) > 2):
            has_fields = True
        elif arg in API_VALUE_FLAGS:
            index += 2
            continue
        elif not arg.startswith("-") and endpoint is None:
            endpoint = _unquote(arg)
        index += 1

    if endpoint is None:
        return None
    if method is None:
        method = "POST" if has_fields else "GET"
    if method == "GET":
        return None

    path = endpoint.lstrip("/").split("?", 1)[0]
    if path == "graphql":
        text = " ".join(args)
        if "--input" in text or (GRAPHQL_MUTATION_RE.search(text) and GRAPHQL_TARGET_RE.search(text)):
            return API_MESSAGE
        return None
    if API_REST_WRITE_RE.match(path):
        return API_MESSAGE
    return None


def _check_gh(args: list[str]) -> str | None:
    """gh より後ろの引数を検査する。gh より前の `-d` (wsl.exe -d など) は見ない。"""
    if not args:
        return None
    group = _unquote(args[0])
    action = _unquote(args[1]) if len(args) > 1 else ""
    rest = args[2:]
    if group == "pr":
        if action == "create" and not DRAFT_FLAGS.intersection(rest):
            return CREATE_MESSAGE
        if action == "ready" and "--undo" not in rest:
            return READY_MESSAGE
        if action in PR_WRITE_ACTIONS:
            return WRITE_MESSAGE
    if group == "issue" and action in ISSUE_WRITE_ACTIONS:
        return WRITE_MESSAGE
    if group == "api":
        return _check_api(args[1:])
    return None


def find_violation(command: str, depth: int = 0) -> str | None:
    """コマンド文字列を検査し、違反があればメッセージを返す。

    `bash -c "gh pr create"` のようにクオートの中に別のコマンドがある場合に備えて、
    空白を含むクオート済みトークンは中身を再帰的に検査する。
    """
    for segment in _segments(_lex(command)):
        for index, token in enumerate(segment):
            if depth < MAX_DEPTH and token[:1] in QUOTES and re.search(r"\s", token):
                message = find_violation(_unquote(token), depth + 1)
                if message is not None:
                    return message
            if _is_gh(token):
                message = _check_gh(segment[index + 1 :])
                if message is not None:
                    return message
    return None


def main() -> None:
    payload = read_stdin_json()
    if payload.get("tool_name") not in ("Bash", "PowerShell"):
        return
    command = (payload.get("tool_input") or {}).get("command") or ""
    if "gh" not in command.lower():
        return
    message = find_violation(command)
    if message is None:
        return
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": message,
                }
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
    sys.exit(0)
