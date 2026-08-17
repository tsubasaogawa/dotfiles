if [ -n "$CLAUDECODE" ]; then
  shopt -s expand_aliases

  alias grep='rg'
  alias cat='bat'
  alias find='fd'
  alias sed='sd'
  # alias ls='eza'
fi
