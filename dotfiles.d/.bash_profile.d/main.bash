# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi

SCRIPT_FILE=$(readlink -f ${BASH_SOURCE[0]})
SCRIPT_DIR=$(dirname $SCRIPT_FILE)

source $SCRIPT_DIR/aws_sso_session_expiry.bash

# Prompt customization
GIT_PS1_SHOWDIRTYSTATE=true
GIT_PS1_SHOWUNTRACKEDFILES=true
GIT_PS1_SHOWSTASHSTATE=true
GIT_PS1_SHOWUPSTREAM=auto

__git_ps1_mod() {
  pwd | grep -q -e 'Obsidian' -e 'obsidian' -e 'Documents' -e 'documents' && return 0 || true
  __git_ps1
}

PS1='\n\[\e[1;32m\]\u\[\e[0;32m\]@\h \[\e[0;33m\]\w\[\e[7;33m\]$(__git_ps1_mod)\[\e[m\]\n\$ '

# remain command history
HISTSIZE=100000
