#!/usr/bin/env python3

import os
from pathlib import Path


def create_symlink(src: Path, dest: Path):
    """
    Creates a symbolic link.

    - If dest is a symlink, it will be overwritten.
    - If dest is a file or directory, a backup will be created before creating the symlink.
    - If dest does not exist, a new symlink will be created.
    """
    if dest.is_symlink():
        # Overwrite existing symlink
        dest.unlink()
        os.symlink(src, dest)
        print(f"Updated symlink: {dest} -> {src}")
    elif dest.exists():
        # Backup existing file
        backup_path = Path(f"{dest}.bak")
        dest.rename(backup_path)
        print(f"Backed up existing file: {dest} -> {backup_path}")
        os.symlink(src, dest)
        print(f"Created symlink: {dest} -> {src}")
    else:
        # Create new symlink
        os.symlink(src, dest)
        print(f"Created symlink: {dest} -> {src}")


def main():
    """
    Executes the dotfiles setup.
    """
    dotfiles_dir = Path(__file__).parent.resolve() / "dotfiles.d"
    home_dir = Path.home()

    create_symlink(dotfiles_dir, home_dir / ".dotfiles.d")

    # Process .dotfiles.d/.*rc
    for f in dotfiles_dir.glob(".*rc"):
        if f.is_file():
            create_symlink(f, home_dir / f.name)

    # Process .dotfiles.d/.*.d/main.*
    for d in dotfiles_dir.glob(".*.d"):
        if d.is_dir():
            try:
                main_file = next(d.glob("main.*"))
                dest_filename = d.name.removesuffix(".d")
                create_symlink(main_file, home_dir / dest_filename)
            except StopIteration:
                # Do nothing if main.* file is not found
                continue

    print("Dotfiles setup complete.")


if __name__ == "__main__":
    main()
