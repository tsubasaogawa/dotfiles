if [ -n "$CLAUDECODE" ]; then
  shopt -s expand_aliases

  alias grep='rg'
  alias cat='bat'
  alias find='fd'
  alias sed='sd'
  # alias ls='eza'

  # cd は組み込みコマンドのため alias ではなく zoxide の cd 統合を使う
  if command -v zoxide >/dev/null 2>&1; then
    eval "$(zoxide init bash --cmd cd)"
  fi
fi
