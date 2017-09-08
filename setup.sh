#!/bin/bash

function showmsg() {
  echo "$1" 1>&2
}

showmsg '# set git-completion / git-prompt'
for file in 'git-completion.bash' 'git-prompt.sh'; do
  # skip if file exists
  [[ -f ~/$file ]] && showmsg "~/$file exists" && continue

  # get path from the result of head
  showmsg "find ${file}..."
  fullpath=$(sudo find / -name $file | head -1)
  [[ $fullpath = '' ]] && showmsg "no $file exists" && continue

  # copy
  cp -pr $fullpath ~
  showmsg "copied $fullpath to ~"
done

showmsg '# create symbolic links'
readonly core_dir="${PWD}/core"
for file in $(ls -A $core_dir); do
  # get basename
  filename=$(basename $file)
  
  # skip if symbolic link exists
  [[ -f ~/$filename ]] && showmsg "~/$filename exists" && continue

  ln -s "${core_dir}/$file" ~/$filename
  showmsg "created symbolic link ~/$filename"
done

showmsg 'done.'
exit 0
