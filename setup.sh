#!/bin/bash

function showmsg() {
  echo "$1" 1>&2
}

showmsg 'set git-completion / git-prompt'
for file in 'git-completion.bash' 'git-prompt.sh'; do
  # skip if file exists
  [[ -f ~/${file} ]] && showmsg "~/${file} exists" && continue

  # get path from the result of head
  local fullpath=$(sudo find / -name ${file} | head -1)

  # copy
  cp -pr ${fullpath} ~
  showmsg "copied ${fullpath} to ~"
done

showmsg 'create symbolic links'
for file in ls 'core/*'; do
  # get basename
  local filename=$(basename ${file})
  
  # skip if symbolic link exists
  [[ -f ~/${filename} ]] && showmsg "~/${filename} exists" && continue

  ln -s ${file} ~/${filename}
  showmsg "created symbolic link ~/${filename}"
done

showmsg 'done.'
exit 0
