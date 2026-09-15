# AGENTS

## 基本

@"~/.claude/AGENTS_BASE.md"

## Claude 独自のルール

- コードのコメントは必要最低限とする
- **コミットメッセージは複数行を許可** (リポジトリの CLAUDE.md よりもこちらを優先)
- Bash でファイルを読むときは絶対パスで指定
  - 正: `sed -n '1,10p' /tmp/foo.log`
  - 誤: `cd /tmp && sed -n '1,10p' foo.log`
  - 注意: `terraform` コマンドを実行するときは例外とする
