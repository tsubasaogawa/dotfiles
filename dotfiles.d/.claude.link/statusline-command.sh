#!/bin/bash
# Claude Code ステータスライン スクリプト

input=$(cat)

# --- カラーコード定義 (16 色 ANSI) ---
RESET=$'\033[0m'
C_RED=$'\033[31m'
C_GREEN=$'\033[32m'
C_YELLOW=$'\033[33m'
C_CYAN=$'\033[36m'
C_MAGENTA=$'\033[35m'
C_BR_RED=$'\033[91m'
C_BR_MAGENTA=$'\033[95m'

# --- 必要なフィールドを 1 回の jq でまとめて取得 ---
# 1 行 1 値で出力し個別に read（空値でもフィールドがずれないようにする）
{
  read -r model
  read -r effort
  read -r thinking
  read -r fast_mode
  read -r cwd
  read -r ctx_pct
  read -r cost_usd
  read -r week_pct
  read -r week_resets_at
  read -r five_h_pct
} < <(
  jq -r '
    (.model.display_name // "Claude"),
    (.effort.level // ""),
    (.thinking.enabled // false | tostring),
    (.fast_mode // false | tostring),
    (.workspace.current_dir // .cwd // ""),
    (.context_window.used_percentage // ""),
    (.cost.total_cost_usd // 0),
    (.rate_limits.seven_day.used_percentage // ""),
    (.rate_limits.seven_day.resets_at // ""),
    (.rate_limits.five_hour.used_percentage // "")
  ' <<<"$input"
)

# --- モデル名（判別できる範囲で短縮：" context)" → ")"）---
model="${model/ context)/)}"

# --- モデル系統ごとの色分け ---
case "$model" in
  *Opus*)   model="${C_MAGENTA}${model}${RESET}" ;;
  *Sonnet*) model="${C_CYAN}${model}${RESET}" ;;
  *Haiku*)  model="${C_GREEN}${model}${RESET}" ;;
  *Fable*)  model="${C_YELLOW}${model}${RESET}" ;;
esac

# --- 現在のディレクトリ (ディレクトリ名のみ表示) ---
cwd_short="${cwd##*/}"
[[ -z "$cwd_short" ]] && cwd_short="~"

# --- Git ブランチ ---
branch=""
if [[ -n "$cwd" ]] && git -C "$cwd" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
fi

# --- 料金（セッション累計。Claude Code が算出する cost.total_cost_usd をそのまま使用）---
cost=$(awk -v c="$cost_usd" 'BEGIN {
  if (c > 0 && c < 0.01) { printf "<$0.01" } else { printf "$%.2f", c }
}')

# --- コンテキスト使用率 (しきい値で色分け：50% 以上で黄、80% 以上で赤) ---
ctx_str=""
if [[ -n "$ctx_pct" ]]; then
  ctx_color=""
  if awk -v p="$ctx_pct" 'BEGIN{exit !(p>=80)}'; then
    ctx_color="$C_RED"
  elif awk -v p="$ctx_pct" 'BEGIN{exit !(p>=50)}'; then
    ctx_color="$C_YELLOW"
  fi
  ctx_str=$(printf "ctx:%.0f%%" "$ctx_pct")
  [[ -n "$ctx_color" ]] && ctx_str="${ctx_color}${ctx_str}${RESET}"
fi

# --- 組み立て ---
# 配列を区切り文字で連結するヘルパー (join_by SEP ELEM...)
join_by() {
  local sep="$1"; shift
  local out=""
  for x in "$@"; do
    if [[ -z "$out" ]]; then out="$x"; else out="${out}${sep}${x}"; fi
  done
  printf '%s' "$out"
}

# --- レート制限の Usage (5 時間 / 週間) ---
usage_str=""
usage_items=()
[[ -n "$five_h_pct" ]] && usage_items+=("$(printf "5h:%.0f%%" "$five_h_pct")")
week_label="w"
if [[ -n "$week_resets_at" ]]; then
  now_ts=$(date +%s)
  week_label=$(awk -v r="$week_resets_at" -v n="$now_ts" 'BEGIN{
    rem = r - n
    if (rem < 0) rem = 0
    if (rem >= 86400) {
      printf "%dd", int((rem + 86399) / 86400)
    } else {
      h = int((rem + 3599) / 3600)
      if (h < 1) h = 1
      printf "%dh", h
    }
  }')
fi
[[ -n "$week_pct" ]] && usage_items+=("$(printf "%s:%.0f%%" "$week_label" "$week_pct")")
(( ${#usage_items[@]} > 0 )) && usage_str="$(join_by " " "${usage_items[@]}")"

parts=()
parts+=("$cost")
[[ -n "$ctx_str" ]] && parts+=("$ctx_str")
[[ -n "$usage_str" ]] && parts+=("$usage_str")

# モデル / effort / think / fast（カンマ区切りで 1 グループ）
case "$effort" in
  low)    effort="${C_GREEN}${effort}${RESET}" ;;
  medium) effort="${C_YELLOW}${effort}${RESET}" ;;
  high)   effort="${C_RED}${effort}${RESET}" ;;
  xhigh)  effort="${C_BR_RED}${effort}${RESET}" ;;
  max)    effort="${C_BR_MAGENTA}${effort}${RESET}" ;;
esac

mgroup=()
[[ -n "$model" ]] && mgroup+=("$model")
[[ -n "$effort" ]] && mgroup+=("$effort")
[[ "$thinking" == "true" ]] && mgroup+=("think")
[[ "$fast_mode" == "true" ]] && mgroup+=("fast")
(( ${#mgroup[@]} > 0 )) && parts+=("$(join_by "/" "${mgroup[@]}")")

[[ -n "$cwd_short" ]] && parts+=("$cwd_short")
[[ -n "$branch" ]] && parts+=("$branch")

# --- ペット (満腹度に応じて表情が変化。PostToolUse フックで満腹度が回復する) ---
pet_str=$(python3 ~/.claude/scripts/pet_render.py 2>/dev/null)
[[ -n "$pet_str" ]] && parts+=("$pet_str")

join_by " | " "${parts[@]}"
echo
