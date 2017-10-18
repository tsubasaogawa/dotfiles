# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi

# User specific environment and startup programs
PATH=$PATH:$HOME/bin
PATH="/home/vagrant/.pyenv/bin:$PATH"
PATH="/usr/local/heroku/bin:$PATH"
export PATH
export PYTHONPATH=/home/vagrant/work/chainer:$PYTHONPATH

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

export PS1='\n\[\e[1;32m\]\u\[\e[0;32m\]@\h \[\e[0;33m\]\w\[\e[7;33m\]$(__git_ps1)\[\e[m\]\n\$ '

# remain command history
export HISTSIZE=100000
