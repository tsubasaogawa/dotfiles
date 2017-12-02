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
  fullpath=$(sudo find / -name $file | head -1)
  [[ $fullpath = '' ]] && showmsg "no $file exists" && continue
  showmsg "finding ${file}..."

  # copy
  cp -pr $fullpath ~
  showmsg "copied $fullpath to ~"
  showmsg "copied $fullpath to your home directory"
done

showmsg '# create symbolic links'
readonly core_dir="$(dirname $0)/core"
for file in $(ls -A $core_dir); do
  # get basename
  filename=$(basename $file)
  
  # if symbolic link exists
  if [[ -f ~/$filename ]]; then
    read -p "~/$filename exists. replace? (Y/n)" ans
    [[ $ans != 'Y' ]] && continue
    # create backup
    mv ~/$filename{,.$(date +%Y%m%d)}
    showmsg "created backup ~/$filename.$(date +%Y%m%d)"
  fi

  ln -s "${core_dir}/$file" ~/$filename
  [[ $? -eq 0 ]] && showmsg "created symbolic link $rcfilename to your home directory"
done

showmsg '# install NeoBundle'
curl --silent https://raw.githubusercontent.com/Shougo/neobundle.vim/master/bin/install.sh > /tmp/install.sh
sh /tmp/install.sh

showmsg 'setup done.'
exit 0
