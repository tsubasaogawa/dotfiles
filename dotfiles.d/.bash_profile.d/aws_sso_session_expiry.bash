# --- AWS SSO session expiry check ---

[[ $- == *i* ]] || return 0
aws-sso-util >/dev/null 2>&1 || return 0

_AWS_SSO_CACHE_DIR="${HOME}/.aws/sso/cache"
_AWS_SSO_CHECK_INTERVAL=300 # seconds between checks
_AWS_SSO_WARN_MINUTES=60    # warn when remaining minutes fall below this
_aws_sso_last_check=0

_aws_sso_notify() {
  local color=$1 message=$2

  if [[ -t 1 ]]; then
    printf '\e[%sm[aws-sso] %s\e[0m\n' "$color" "$message"
  else
    printf '[aws-sso] %s\n' "$message"
  fi
}

# print the longest remaining minutes across every token cache
# (aws-sso-util and `aws sso login` may keep separate caches; both must be
# expired before we report an expired session). returns 1 when unknown.
_aws_sso_max_remaining_minutes() {
  local now=$1
  local file expires_at expires_epoch remaining max=""

  for file in "$_AWS_SSO_CACHE_DIR"/*.json; do
    [[ -f $file ]] || continue
    # client registration files carry no token
    # `command` guards against user aliases such as sed=sd / grep=rg
    command grep -q '"accessToken"' "$file" || continue

    expires_at=$(command sed -n 's/.*"expiresAt" *: *"\([^"]*\)".*/\1/p' "$file")
    [[ -z $expires_at ]] && continue

    expires_epoch=$(date -d "$expires_at" +%s 2>/dev/null)
    [[ -z $expires_epoch ]] && continue

    remaining=$(( (expires_epoch - now) / 60 ))
    [[ -z $max || $remaining -gt $max ]] && max=$remaining
  done

  [[ -z $max ]] && return 1
  printf '%s\n' "$max"
}

# ask whether to run `aws sso login` right away. falls back to a plain
# notification when stdin is not a terminal (PROMPT_COMMAND can run there too).
_aws_sso_login_prompt() {
  local answer

  if [[ ! -t 0 ]]; then
    _aws_sso_notify 31 'session expired. run: aws sso login'
    return
  fi

  read -r -p $'\e[31m[aws-sso] session expired. run `aws sso login`? [y/N]: \e[0m' answer || {
    printf '\n'
    return
  }

  case $answer in
  [yY] | [yY][eE][sS]) ;;
  *) return ;;
  esac

  if aws sso login; then
    # re-evaluate the remaining time on the next prompt
    _aws_sso_last_check=0
  else
    _aws_sso_notify 31 'aws sso login failed'
  fi
}

_aws_sso_expiry_prompt() {
  local now
  now=$(date +%s)
  (( now - _aws_sso_last_check < _AWS_SSO_CHECK_INTERVAL )) && return
  _aws_sso_last_check=$now

  local remaining
  remaining=$(_aws_sso_max_remaining_minutes "$now") || return

  if (( remaining <= 0 )); then
    _aws_sso_login_prompt
  elif (( remaining <= _AWS_SSO_WARN_MINUTES )); then
    _aws_sso_notify 33 "session expires in ${remaining} min"
  fi
}

if [[ ${PROMPT_COMMAND-} != *_aws_sso_expiry_prompt* ]]; then
  PROMPT_COMMAND="_aws_sso_expiry_prompt${PROMPT_COMMAND:+; $PROMPT_COMMAND}"
fi
