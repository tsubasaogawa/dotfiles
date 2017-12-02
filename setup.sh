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
sh /tmp/install.sh | tee "/tmp/NeoBundle.log.$(date +%Y%m%d%H%M)" | grep 'Complete setup NeoBundle'
[[ $? -ne 0 ]] && showmsg "error occured. please refer to /tmp/NeoBundle.log.$(date +%Y%m%d%H%M)" && exit 1

showmsg 'setup done.'
exit 0
