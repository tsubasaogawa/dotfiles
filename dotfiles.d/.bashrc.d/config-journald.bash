#!/bin/bash
set -eu

# journald.conf の MaxLevelKMsg を notice に設定し、INFO レベルのカーネルメッセージを journald に記録させない

if [[ ! -f /etc/systemd/journald.conf.d/suppress-kmsg-info.conf ]]; then
  sudo mkdir -p /etc/systemd/journald.conf.d
  printf "[Journal]\nMaxLevelKMsg=notice\n" | sudo tee /etc/systemd/journald.conf.d/suppress-kmsg-info.conf >/dev/null
fi

