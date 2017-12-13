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
alias switch_gcc5='scl enable devtoolset-4 bash'
alias pd='pushd >/dev/null'
alias ds='dirs -v'

function pds() {
  ! which peco >/dev/null 2>&1 && echo 'please install peco' && return 1
  local pushd_number=$(dirs -v | peco | perl -anE 'say $F[0]')
  [[ -z $pushd_number ]] && return 1
  pushd +$pushd_number
  return $?
}
