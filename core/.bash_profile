# .bash_profile

# Ignoring directories executing __git_ps1
IGNORE_PS1_DIR=()
function __git_ps1_modified() {
  # No ignoring directory
  if [[ -z $IGNORE_PS1_DIR ]]; then
    # Delete space
    __git_ps1 | cut -c 2-
    return 0
  fi

  # Some directories are
  for ig_dir in ${IGNORE_PS1_DIR[@]}; do
    [[ ${PWD} =~ ${ig_dir}.* ]] && return 1
  done

  # Current directory does not match ignore directories
  __git_ps1 | cut -c 2-
  return 0
}

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi

# User specific environment and startup programs
PATH=$PATH:$HOME/bin
PATH="$HOME/.local/lib/shellspec/bin:$PATH"
PATH="$HOME/.ebcli-virtual-env/executables:$PATH"
PATH="$HOME/.anyenv/bin:$PATH"
PATH="$HOME/.slsenv/bin:$PATH"
[[ -e /var/tmp/vscode_dir ]] && PATH="$(cat /var/tmp/vscode_dir | tr -d '\n'):$PATH"
export PATH

eval "$(anyenv init -)"
export PATH="$GOENV_ROOT/shims:$GOPATH/bin:$PATH"

export PIPX_DEFAULT_PYTHON="$(which python)"

# git-completion / git-prompt
source $HOME/git-completion.bash
source $HOME/git-prompt.sh

. "$HOME/.asdf/asdf.sh"
. "$HOME/.asdf/completions/asdf.bash"

GIT_PS1_SHOWDIRTYSTATE=1
GIT_PS1_SHOWUPSTREAM=1
GIT_PS1_SHOWUNTRACKEDFILES=
GIT_PS1_SHOWSTASHSTATE=1

export PS1='\n\[\e[1;32m\]\u\[\e[0;32m\]@\h \[\e[0;33m\]\w\[\e[7;33m\]$(__git_ps1_modified)\[\e[m\]\n\$ '

# remain command history
export HISTSIZE=100000

# terraform
export TF_CLI_ARGS_plan="--parallelism=20"
export TF_CLI_ARGS_apply="--parallelism=20"

complete -C '/usr/local/bin/aws_completer' aws

. "$HOME/.atuin/bin/env"
