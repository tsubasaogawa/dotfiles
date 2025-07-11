#!/bin/bash

# Provisioning script for dotfiles
# No args required

readonly DOTFILES_DIR_LIST=('.bashrc.d' '.bash_profile.d')

echo '# create symbolic links'
readonly core_dir="$(cd $(dirname $0) && pwd)/dotfiles.d"
for core_rcfile in $DOTFILES_DIR_LIST; do
  # get basename
  rcfilename=$(basename "$core_rcfile")
  destination_rcfile=~/$rcfilename

  # if symbolic link exists
  if [[ -e "$destination_rcfile" ]]; then
    read -p "$destination_rcfile exists. replace? (Y/n)" ans
    [[ "x$ans" != 'xY' ]] && continue
    # create backup
    mv $destination_rcfile{,.$(date +%Y%m%d)}
    echo "created backup ${destination_rcfile}.$(date +%Y%m%d)"
  # if broken symbolic link exists
  elif ls "$rcfilename" >/dev/null 2>&1 && find ~/ -maxdepth 1 -name "$rcfilename" -xtype l >/dev/null 2>&1; then
    rm -f $destination_rcfile
    echo "deleted broken symbolic link $destination_rcfile"
  fi

  ln -s "$core_rcfile" "$destination_rcfile"
  [[ $? -eq 0 ]] && echo "created symbolic link $rcfilename to your home directory"
done

echo '# install NeoBundle'
curl --silent https://raw.githubusercontent.com/Shougo/neobundle.vim/master/bin/install.sh > /tmp/install.sh
sh /tmp/install.sh | tee "/tmp/NeoBundle.log.$(date +%Y%m%d%H%M)" | grep 'Complete setup NeoBundle'
[[ $? -ne 0 ]] && echo "error occured. please refer to /tmp/NeoBundle.log.$(date +%Y%m%d%H%M)" && exit 1

echo 'setup done.'
exit 0
