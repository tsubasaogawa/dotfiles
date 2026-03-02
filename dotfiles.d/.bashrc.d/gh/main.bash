#!/bin/bash -eu

SCRIPT_FILE=$(readlink -f ${BASH_SOURCE[0]})
SCRIPT_DIR=$(dirname $SCRIPT_FILE)

which gh || exit 0
test $(SCRIPT_DIR)/alias.yml || exit 0

diff <(gh alias list) <(cat $(SCRIPT_DIR)/alias.yml) >/dev/null 2>&1 && exit 0

gh alias import $(SCRIPT_DIR)/alias.yml

