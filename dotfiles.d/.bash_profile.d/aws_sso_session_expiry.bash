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

# print the newest SSO token cache file (client registration files are skipped)
_aws_sso_token_cache_file() {
  local file newest=""

  for file in "$_AWS_SSO_CACHE_DIR"/*.json; do
    [[ -f $file ]] || continue
    command grep -q '"accessToken"' "$file" || continue
    [[ -z $newest || $file -nt $newest ]] && newest=$file
  done

  [[ -n $newest ]] && printf '%s\n' "$newest"
}

_aws_sso_expiry_prompt() {
  local now
  now=$(date +%s)
  (( now - _aws_sso_last_check < _AWS_SSO_CHECK_INTERVAL )) && return
  _aws_sso_last_check=$now

  local cache_file
  cache_file=$(_aws_sso_token_cache_file)
  [[ -z $cache_file ]] && return

  local expires_at
  # `command` guards against user aliases such as sed=sd / grep=rg
  expires_at=$(command sed -n 's/.*"expiresAt" *: *"\([^"]*\)".*/\1/p' "$cache_file")
  [[ -z $expires_at ]] && return

  local expires_epoch
  expires_epoch=$(date -d "$expires_at" +%s 2>/dev/null)
  [[ -z $expires_epoch ]] && return

  local remaining=$(( (expires_epoch - now) / 60 ))

  if (( remaining <= 0 )); then
    _aws_sso_notify 31 'session expired. run: aws-sso-util login --force-refresh'
  elif (( remaining <= _AWS_SSO_WARN_MINUTES )); then
    _aws_sso_notify 33 "session expires in ${remaining} min"
  fi
}

if [[ ${PROMPT_COMMAND-} != *_aws_sso_expiry_prompt* ]]; then
  PROMPT_COMMAND="_aws_sso_expiry_prompt${PROMPT_COMMAND:+; $PROMPT_COMMAND}"
fi
