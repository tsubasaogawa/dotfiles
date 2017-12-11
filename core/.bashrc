# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User specific aliases and functions
alias histless='history | less'
alias histgrep='history | grep'
alias less='/usr/share/vim/vim74/macros/less.sh'
alias gre@='grep'
alias cd='pushd >/dev/null'
alias ds='dirs -v'

function pds() {
  ! which peco >/dev/null 2>&1 && echo 'please install peco' && return 1
  local pushd_number=$(dirs -v | peco | perl -anE 'say $F[0]')
  [[ "x$pushd_number" = "x" ]] && return 1
  pushd +$pushd_number
  return $?
}
