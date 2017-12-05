#!/bin/bash

# Provisioning script for dotfiles
# No args required

function showmsg() {
  echo "$1" 1>&2
}

showmsg '# set git-completion / git-prompt'
for file in 'git-completion.bash' 'git-prompt.sh'; do
  # skip if file exists
  [[ -f ~/$file ]] && showmsg "~/$file exists" && continue

  # get path from the result of head
  showmsg "finding ${file}..."
  fullpath=$(sudo find / -name "$file" | head -1)
  [[ -z $fullpath ]] && showmsg "no $file exists" && continue

  # copy
  cp -p "$fullpath" ~
  showmsg "copied $fullpath to your home directory"
done

showmsg '# create symbolic links'
readonly core_dir="$(cd $(dirname $0) && pwd)/core"
for core_rcfile in $(find "$core_dir" -name '.*' -type f); do
  # get basename
  rcfilename=$(basename "$core_rcfile")
  destination_rcfile=~/$rcfilename

  # if symbolic link exists
  if [[ -e "$destination_rcfile" ]]; then
    read -p "$destination_rcfile exists. replace? (Y/n)" ans
    [[ "x$ans" != 'xY' ]] && continue
    # create backup
    mv $destination_rcfile{,.$(date +%Y%m%d)}
    showmsg "created backup ${destination_rcfile}.$(date +%Y%m%d)"
  # if broken symbolic link exists
  elif ls "$rcfilename" >/dev/null 2>&1 && find ~/ -maxdepth 1 -name "$rcfilename" -xtype l >/dev/null 2>&1; then
    rm -f $destination_rcfile
    showmsg "deleted broken symbolic link $destination_rcfile"
  fi

  ln -s "$core_rcfile" "$destination_rcfile"
  [[ $? -eq 0 ]] && showmsg "created symbolic link $rcfilename to your home directory"
done

showmsg '# install NeoBundle'
curl --silent https://raw.githubusercontent.com/Shougo/neobundle.vim/master/bin/install.sh > /tmp/install.sh
sh /tmp/install.sh | tee "/tmp/NeoBundle.log.$(date +%Y%m%d%H%M)" | grep 'Complete setup NeoBundle'
[[ $? -ne 0 ]] && showmsg "error occured. please refer to /tmp/NeoBundle.log.$(date +%Y%m%d%H%M)" && exit 1

showmsg 'setup done.'
exit 0
