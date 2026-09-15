#!/bin/bash -eu

SCRIPT_FILE=$(readlink -f "${BASH_SOURCE[0]}")
SCRIPT_DIR=$(dirname "$SCRIPT_FILE")

command -v gh >/dev/null 2>&1 || exit 0
[[ -f "$SCRIPT_DIR/alias.yml" ]] || exit 0

diff <(gh alias list) "$SCRIPT_DIR/alias.yml" >/dev/null 2>&1 && exit 0

gh alias import --clobber "$SCRIPT_DIR/alias.yml"
