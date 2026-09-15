#!/bin/bash

command -v jq >/dev/null 2>&1 || exit 0
input=$(< /dev/stdin)

RESET=$'\033[0m'
C_RED=$'\033[31m'
C_GREEN=$'\033[32m'
C_YELLOW=$'\033[33m'
C_CYAN=$'\033[36m'
C_MAGENTA=$'\033[35m'
C_BR_RED=$'\033[91m'
C_BR_MAGENTA=$'\033[95m'

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

model="${model/ context)/)}"

case "$model" in
  *Opus*)   model="${C_MAGENTA}${model}${RESET}" ;;
  *Sonnet*) model="${C_CYAN}${model}${RESET}" ;;
  *Haiku*)  model="${C_GREEN}${model}${RESET}" ;;
  *Fable*)  model="${C_YELLOW}${model}${RESET}" ;;
esac

cwd_short="${cwd##*/}"
[[ -z "$cwd_short" ]] && cwd_short="~"

branch=""
if [[ -n "$cwd" ]] && git -C "$cwd" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
fi

cost=$(awk -v c="$cost_usd" 'BEGIN {
  if (c > 0 && c < 0.01) { printf "<$0.01" } else { printf "$%.2f", c }
}')

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

join_by() {
  local separator="$1"
  local result="$2"
  shift 2

  for value; do
    result+="${separator}${value}"
  done
  printf '%s' "$result"
}

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

pet_script="$HOME/.claude/scripts/pet_render.py"
if command -v python3 >/dev/null 2>&1 && [[ -f "$pet_script" ]]; then
  pet_str=$(python3 "$pet_script" 2>/dev/null)
else
  pet_str=""
fi
[[ -n "$pet_str" ]] && parts+=("$pet_str")

join_by " | " "${parts[@]}"
echo
