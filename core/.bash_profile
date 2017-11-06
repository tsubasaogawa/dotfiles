# .bash_profile

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

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi

# User specific environment and startup programs
PATH=$PATH:$HOME/bin:$HOME/.pyenv/bin
export PATH
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# git-completion / git-prompt
source ./git-completion.bash
source ./git-prompt.sh

# プロンプトに各種情報を表示
GIT_PS1_SHOWDIRTYSTATE=1
GIT_PS1_SHOWUPSTREAM=1
GIT_PS1_SHOWUNTRACKEDFILES=
GIT_PS1_SHOWSTASHSTATE=1

export PS1='\n\[\e[1;32m\]\u\[\e[0;32m\]@\h \[\e[0;33m\]\w\[\e[7;33m\]$(__git_ps1_modified)\[\e[m\]\n\$ '

# remain command history
export HISTSIZE=100000
