# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User specific aliases and functions
alias pd='pushd >/dev/null'
alias ds='dirs -v'
source ~/.local/share/bash-abbrev-alias/abbrev-alias.plugin.bash
abbrev-alias -c asu='aws-sso-util login --force-refresh'
abbrev-alias -c gps='git push origin @'
abbrev-alias -c gpl='git pull'
abbrev-alias -ge B='$(git symbolic-ref --short HEAD 2>/dev/null)'
abbrev-alias -c ti='terraform init'

# stop screen lock & enable i-search
stty stop undef
stty start undef

function pds() {
  ! which peco >/dev/null 2>&1 && echo 'please install peco' && return 1
  local pushd_number=$(dirs -v | peco | perl -anE 'say $F[0]')
  [[ -z $pushd_number ]] && return 1
  pushd +$pushd_number
  return $?
}
# append to .bash_history
shopt -s histappend

# The next line updates PATH for the Google Cloud SDK.
if [ -f "$HOME/dev/yes/google-cloud-sdk/path.bash.inc" ]; then . "$HOME/dev/yes/google-cloud-sdk/path.bash.inc"; fi

# The next line enables shell command completion for gcloud.
if [ -f "$HOME/dev/yes/google-cloud-sdk/completion.bash.inc" ]; then . "$HOME/dev/yes/google-cloud-sdk/completion.bash.inc"; fi

# Created by `pipx` on 2022-04-13 06:45:06
export PATH="$PATH:$HOME/.local/bin"
# source $HOME/.local/share/aws-sso-util/aws-sso-util-completion.sh
sed -ie 's/"credsStore": "desktop.exe"/"credsStore": ""/' ~/.docker/config.json

