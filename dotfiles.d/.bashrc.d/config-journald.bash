#!/bin/bash
set -eu

# Set MaxLevelKMsg to notice so journald ignores INFO-level kernel messages

if [[ ! -f /etc/systemd/journald.conf.d/suppress-kmsg-info.conf ]]; then
  sudo mkdir -p /etc/systemd/journald.conf.d
  printf "[Journal]\nMaxLevelKMsg=notice\n" | sudo tee /etc/systemd/journald.conf.d/suppress-kmsg-info.conf >/dev/null
fi
