#!/bin/bash
set -eu

cd /usr/share/doc/git/contrib/diff-highlight

sudo make
sudo ln -fs /usr/share/doc/git/contrib/diff-highlight/diff-highlight /usr/local/bin/diff-highlight
