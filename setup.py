#!/usr/bin/env python3

import os
from pathlib import Path

def create_symlink(src: Path, dest: Path):
    """
    シンボリックリンクを作成する。

    - dest がシンボリックリンクの場合は上書きする。
    - dest がファイルまたはディレクトリの場合はバックアップを作成してから作成する。
    - dest が存在しない場合は新規に作成する。
    """
    if dest.is_symlink():
        # 既存のシンボリックリンクは上書き
        dest.unlink()
        os.symlink(src, dest)
        print(f"Updated symlink: {dest} -> {src}")
    elif dest.exists():
        # 既存のファイルはバックアップを作成
        backup_path = Path(f"{dest}.bak")
        dest.rename(backup_path)
        print(f"Backed up existing file: {dest} -> {backup_path}")
        os.symlink(src, dest)
        print(f"Created symlink: {dest} -> {src}")
    else:
        # 新規作成
        os.symlink(src, dest)
        print(f"Created symlink: {dest} -> {src}")

def main():
    """
    dotfilesのセットアップを実行する。
    """
    dotfiles_dir = Path(__file__).parent.resolve() / "dotfiles.d"
    home_dir = Path.home()

    # .dotfiles.d/.*rc と .gitconfig を処理
    for f in dotfiles_dir.glob(".*rc"):
        if f.is_file():
            create_symlink(f, home_dir / f.name)

    gitconfig_path = dotfiles_dir / ".gitconfig"
    if gitconfig_path.is_file():
        create_symlink(gitconfig_path, home_dir / ".gitconfig")

    # .dotfiles.d/.*.d/main.* を処理
    for d in dotfiles_dir.glob(".*.d"):
        if d.is_dir():
            try:
                main_file = next(d.glob("main.*"))
                dest_filename = d.name.removesuffix('.d')
                create_symlink(main_file, home_dir / dest_filename)
            except StopIteration:
                # main.* ファイルが見つからない場合は何もしない
                continue

    print("Dotfiles setup complete.")

if __name__ == "__main__":
    main()
