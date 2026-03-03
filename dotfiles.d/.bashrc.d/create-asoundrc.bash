#!/bin/bash -eu

# Sound play in WSL2

# Please install the following:
#   sudo apt install alsa-utils libasound2-plugins libpulse0

test -f ~/.asoundrc && exit 0

cat << EOC > ~/.asoundrc
pcm.!default {
    type pulse
    fallback "sysdefault"
}
ctl.!default {
    type pulse
}
EOC

