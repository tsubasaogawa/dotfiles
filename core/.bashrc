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
alias pd='pushd'
alias ds='dirs -v'
