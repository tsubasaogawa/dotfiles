import json
import os
import re
import sys
import tempfile
import time

PLAN_FILES_DIR = os.path.normpath(os.path.expanduser("~/.claude/plans"))

AGENT_NAME = "format-rule-fixer"
PAYLOAD_DIR = os.path.join(tempfile.gettempdir(), "claude_format_rule_payloads")
EXCERPT_RADIUS = 30

FULLWIDTH_OPEN = chr(0xFF08)
FULLWIDTH_CLOSE = chr(0xFF09)

CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
QUOTE_LINE_RE = re.compile(r"^\s*>.*$", re.MULTILINE)

EMOJI_RANGES = (
    (0x1F300, 0x1F5FF),
    (0x1F600, 0x1F64F),
    (0x1F680, 0x1F6FF),
    (0x1F700, 0x1F77F),
    (0x1F780, 0x1F7FF),
    (0x1F800, 0x1F8FF),
    (0x1F900, 0x1F9FF),
    (0x1FA00, 0x1FAFF),
    (0x2600, 0x26FF),
    (0x2700, 0x2794),
    (0x2796, 0x27BF),
)
EMOJI_RE = re.compile(
    "[" + "".join(chr(lo) + "-" + chr(hi) for lo, hi in EMOJI_RANGES) + "]"
)

JP = "[぀-ヿ㐀-䶿一-鿿豈-﫿]"
ALNUM = r"[A-Za-z0-9]"
SPACING_RE = re.compile(JP + ALNUM + "|" + ALNUM + JP)
FULLWIDTH_PAREN_RE = re.compile("[" + FULLWIDTH_OPEN + FULLWIDTH_CLOSE + "]")

FULLWIDTH_PAREN_MESSAGE = (
    "全角カッコ" + FULLWIDTH_OPEN + FULLWIDTH_CLOSE
    + "の使用が検出されました。"
    "半角カッコ () を使用してください"
)
EMOJI_MESSAGE = (
    "絵文字の使用が検出されました。"
    "絵文字は使用しないでください"
)
SPACING_MESSAGE = (
    "日本語と半角英数字の間に"
    "スペースがありません。"
    "日本語テキストと英単語・数字の間には"
    "半角スペースを入れてください"
    " (例: \"GitHub リポジトリ 1\")"
)

AGENT_MESSAGE_TEMPLATE = (
    "修正は自分で行わず、Agent ツールで subagent_type=\"{agent}\" を起動してください。"
    "拒否されたツール呼び出しの内容は {payload} に JSON で保存済みです。"
    "上の違反一覧とこのパスをエージェントに渡すと、修正したうえで"
    "元のツール呼び出しを実行し直します。"
)


def is_plan_file(file_path: str) -> bool:
    if not file_path:
        return False
    normalized = os.path.normpath(os.path.abspath(os.path.expanduser(file_path)))
    return normalized == PLAN_FILES_DIR or normalized.startswith(PLAN_FILES_DIR + os.sep)


def collect_texts(tool_name: str, tool_input: dict) -> list[str]:
    if tool_name == "Write":
        return [tool_input.get("content", "")]
    if tool_name == "Edit":
        return [tool_input.get("new_string", "")]
    if tool_name == "MultiEdit":
        return [e.get("new_string", "") for e in tool_input.get("edits", [])]
    if tool_name == "NotebookEdit":
        return [tool_input.get("new_source", "")]
    return []


def blank_out(match: re.Match) -> str:
    return re.sub(r"[^\n]", " ", match.group(0))


def strip_code_spans(text: str) -> str:
    text = CODE_FENCE_RE.sub(blank_out, text)
    text = INLINE_CODE_RE.sub(blank_out, text)
    return text


def strip_quote_lines(text: str) -> str:
    return QUOTE_LINE_RE.sub(blank_out, text)


def locate(text: str, pos: int) -> str:
    line = text.count("\n", 0, pos) + 1
    col = pos - text.rfind("\n", 0, pos)
    return "L{0}:{1}".format(line, col)


def excerpt(text: str, start: int, end: int) -> str:
    head = max(0, start - EXCERPT_RADIUS)
    tail = min(len(text), end + EXCERPT_RADIUS)
    return text[head:tail].replace("\n", "\\n")


def find_violations(text: str) -> list[tuple[str, list[str]]]:
    quoted_stripped = strip_quote_lines(text)
    checked = strip_code_spans(quoted_stripped)

    found = []
    for message, pattern, target in (
        (FULLWIDTH_PAREN_MESSAGE, FULLWIDTH_PAREN_RE, quoted_stripped),
        (EMOJI_MESSAGE, EMOJI_RE, checked),
        (SPACING_MESSAGE, SPACING_RE, checked),
    ):
        spots = [
            "{0} {1}".format(locate(text, m.start()), excerpt(text, m.start(), m.end()))
            for m in pattern.finditer(target)
        ]
        if spots:
            found.append((message, spots))
    return found


def dump_payload(data: dict) -> str:
    os.makedirs(PAYLOAD_DIR, exist_ok=True)
    name = "{0}_{1}.json".format(int(time.time() * 1000), os.getpid())
    path = os.path.join(PAYLOAD_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {"tool_name": data.get("tool_name", ""), "tool_input": data.get("tool_input", {})},
            f,
            ensure_ascii=False,
        )
    return path


def main() -> None:
    try:
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if is_plan_file(tool_input.get("file_path", "")):
        sys.exit(0)

    texts = collect_texts(tool_name, tool_input)
    grouped: dict[str, list[str]] = {}
    for index, text in enumerate(texts):
        prefix = "" if len(texts) == 1 else "edits[{0}] ".format(index)
        for message, spots in find_violations(text):
            grouped.setdefault(message, []).extend(prefix + s for s in spots)

    if not grouped:
        sys.exit(0)

    for message, spots in grouped.items():
        print("{0} ({1} 件)".format(message, len(spots)), file=sys.stderr)
        for spot in spots:
            print("  - " + spot, file=sys.stderr)

    payload = dump_payload(data)
    print(
        AGENT_MESSAGE_TEMPLATE.format(agent=AGENT_NAME, payload=payload),
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
