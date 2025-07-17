# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi

# Prompt customization
GIT_PS1_SHOWDIRTYSTATE=true
GIT_PS1_SHOWUNTRACKEDFILES=true
GIT_PS1_SHOWSTASHSTATE=true
GIT_PS1_SHOWUPSTREAM=auto

PS1='\n\[\e[1;32m\]\u\[\e[0;32m\]@\h \[\e[0;33m\]\w\[\e[7;33m\]$(__git_ps1_modified)\[\e[m\]\n\$ '

# remain command history
HISTSIZE=100000
