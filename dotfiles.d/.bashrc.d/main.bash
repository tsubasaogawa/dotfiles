# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

SCRIPT_FILE=$(readlink -f ${BASH_SOURCE[0]})
SCRIPT_DIR=$(dirname $SCRIPT_FILE)

# User specific environment and startup programs
PATH=$PATH:$HOME/bin
PATH="/usr/local/heroku/bin:$PATH"
PATH="$HOME/.anyenv/bin:$PATH"
PATH="$HOME/.cargo/bin:$PATH"
PATH=$PATH:$HOME/.pulumi/bin
PATH="/opt/go/bin:$GOPATH/bin:$PATH"
PATH="$HOME/.slsenv/bin:$PATH"
PATH="/mnt/c/Program\ Files/Docker/Docker/resources/bin:$PATH"
PATH="/home/t_ogawa/.local/bin:$PATH"
PATH="$HOME/.local/lib/shellspec/bin:$PATH"
[[ -e /var/tmp/vscode_dir ]] && PATH="$(cat /var/tmp/vscode_dir | tr -d '\n'):$PATH"

export PATH

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# https://blog.odaryo.com/2020/01/wsl2-xserver-export-display/
# https://www.beekeeperstudio.io/blog/building-electron-windows-ubuntu-wsl2
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
export LIBGL_ALWAYS_INDIRECT=true

eval "$(anyenv init -)"
eval "$(pyenv virtualenv-init -)"
eval "$(direnv hook bash)"

. "$HOME/.asdf/asdf.sh"
. "$HOME/.asdf/completions/asdf.bash"

# User specific aliases and functions
# alias less='/usr/share/vim/vim74/macros/less.sh'
alias gre@='grep'
alias switch_gcc5='scl enable devtoolset-4 bash'
alias pd='pushd >/dev/null'
alias ds='dirs -v'

alias rsyncp='rsync -C --filter=":- .gitignore" -acv'
source ~/.local/share/bash-abbrev-alias/abbrev-alias.plugin.bash
abbrev-alias -c asu='aws-sso-util login --force-refresh'
abbrev-alias -c gps='git push origin @'
abbrev-alias -c gpl='git pull'
abbrev-alias -ge B='$(git symbolic-ref --short HEAD 2>/dev/null)'
abbrev-alias -c ti='terraform init'

# stop screen lock & enable i-search
stty stop undef
stty start undef

shopt -s histappend

function make() {
  PLAN_FILE="/tmp/tfplan_$(date +%Y%m%d).log"

  if [ "$1" = 'plan' ] || [ "$1" = 'apply' ]; then
    date --iso-8601=seconds >> $PLAN_FILE
    command make "$@" | tee -a $PLAN_FILE
    echo -e "\n\n" >> $PLAN_FILE
    # sed -ire 's/ESC\[[0-9]+m//g' $PLAN_FILE
  else
    command make "$@"
  fi
}
export -f make

function pds() {
  ! which peco >/dev/null 2>&1 && echo 'please install peco' && return 1
  local pushd_number=$(dirs -v | peco | perl -anE 'say $F[0]')
  [[ -z $pushd_number ]] && return 1
  pushd +$pushd_number
  return $?
}

# git-completion
if [ ! -f $SCRIPT_DIR/.git-completion.bash ]; then
  curl -sS -o $SCRIPT_DIR/.git-completion.bash https://raw.githubusercontent.com/git/git/master/contrib/completion/git-completion.bash
fi
if [ ! -f $SCRIPT_DIR/.git-prompt.sh ]; then
  curl -sS -o $SCRIPT_DIR/.git-prompt.sh https://raw.githubusercontent.com/git/git/master/contrib/completion/git-prompt.sh
fi

source $SCRIPT_DIR/.git-completion.bash
source $SCRIPT_DIR/.git-prompt.sh

complete -C '/usr/local/bin/aws_completer' aws

# The next line updates PATH for the Google Cloud SDK.
if [ -f "$HOME/dev/yes/google-cloud-sdk/path.bash.inc" ]; then . "$HOME/dev/yes/google-cloud-sdk/path.bash.inc"; fi

# The next line enables shell command completion for gcloud.
if [ -f "$HOME/dev/yes/google-cloud-sdk/completion.bash.inc" ]; then . "$HOME/dev/yes/google-cloud-sdk/completion.bash.inc"; fi

# Ignoring directories executing __git_ps1
IGNORE_PS1_DIR=()
function __git_ps1_modified() {
  # No ignoring directory
  if [[ -z $IGNORE_PS1_DIR ]]; then
    __git_ps1
    return 0
  fi

  # Some directories are
  for ig_dir in ${IGNORE_PS1_DIR[@]}; do
    [[ ${PWD} =~ ${ig_dir}.* ]] && return 1
  done

  # Current directory does not match ignore directories
  __git_ps1
  return 0
}

# dotenvx
if command -v dotenvx >/dev/null; then
  dotfiles_dir="${SCRIPT_DIR}/.."
  if [[ -n "$dotfiles_dir" ]] && [[ -f "${dotfiles_dir}/.env" ]]; then
    export $(dotenvx get --format shell -f "${dotfiles_dir}/.env")
    export $(dotenvx get --format shell -f "${dotfiles_dir}/.env.secret.encrypted")
    [[ -f "${dotfiles_dir}/.env.local" ]] && export $(dotenvx get --format shell -f "${dotfiles_dir}/.env.local")
  fi
fi

. "$HOME/.atuin/bin/env"

for f in $(ls ${SCRIPT_DIR}/*.*sh | grep -v ${SCRIPT_FILE}); do
  source $f
done

[[ -f ~/.bash-preexec.sh ]] && source ~/.bash-preexec.sh
eval "$(atuin init bash --disable-up-arrow)"
