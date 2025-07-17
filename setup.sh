#!/bin/bash

# .dotfiles.d にあるドットファイルをユーザーのホームディレクトリにシンボリックリンクするスクリプト
#
# シンボリック先とシンボリック元 (対象となるドットファイル)
#  - `.dotfiles.d/.*rc` -> `~/.*rc`
#  - `.dotfiles.d/.gitconfig` -> `~/.gitconfig`
#  - `.dotfiles.d/.<DOTFILE>.d/main.*sh` -> `~/.<DOTFILE>`
#
# シンボリック元ファイルが既に存在する場合、バックアップを作成する
# ただし、元ファイルもシンボリックリンクだった場合はバックアップは作成せず上書きする

set -eu

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)/dotfiles.d"
HOME_DIR="$HOME"

# シンボリックリンクを作成する関数
create_symlink() {
  local src=$1
  local dest=$2

  if [ -L "$dest" ]; then
    # 既存のシンボリックリンクは上書き
    ln -snf "$src" "$dest"
    echo "Updated symlink: $dest -> $src"
  elif [ -e "$dest" ]; then
    # 既存のファイルはバックアップを作成
    mv "$dest" "${dest}.bak"
    echo "Backed up existing file: $dest -> ${dest}.bak"
    ln -sn "$src" "$dest"
    echo "Created symlink: $dest -> $src"
  else
    # 新規作成
    ln -sn "$src" "$dest"
    echo "Created symlink: $dest -> $src"
  fi
}

# .dotfiles.d/.*rc と .gitconfig を処理
for file in "$DOTFILES_DIR"/.*rc "$DOTFILES_DIR"/.gitconfig; do
  if [ -f "$file" ]; then
    filename=$(basename "$file")
    create_symlink "$file" "$HOME_DIR/$filename"
  fi
done

# .dotfiles.d/.*.d/main.*sh を処理
for dir in "$DOTFILES_DIR"/.*.d; do
  if [ -d "$dir" ]; then
    for main_file in "$dir"/main.*; do
      if [ -f "$main_file" ]; then
        dir_basename=$(basename "$dir")
        dest_filename=".${dir_basename%.d}"
        create_symlink "$main_file" "$HOME_DIR/$dest_filename"
        break # 各.dディレクトリにつき1つのmainファイルのみ処理
      fi
    done
  fi
done

echo "Dotfiles setup complete."
