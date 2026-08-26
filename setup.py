#!/usr/bin/env python3

from pathlib import Path


def create_symlink(src: Path, dest: Path) -> None:
    """
    Creates a symbolic link.

    - If dest already points to src, nothing is done.
    - If dest is a symlink, it will be overwritten.
    - If dest is a file or directory, a backup will be created before creating the symlink.
    - If dest does not exist, a new symlink will be created.
    """
    if dest.is_symlink():
        if dest.readlink() == src:
            print(f"Already linked: {dest} -> {src}")
            return
        dest.unlink()
        action = "Updated symlink"
    else:
        if dest.exists():
            backup_path = dest.with_name(f"{dest.name}.bak")
            dest.rename(backup_path)
            print(f"Backed up existing file: {dest} -> {backup_path}")
        action = "Created symlink"

    dest.symlink_to(src)
    print(f"{action}: {dest} -> {src}")


def main() -> None:
    """
    Executes the dotfiles setup.
    """
    dotfiles_dir = Path(__file__).parent.resolve() / "dotfiles.d"
    home_dir = Path.home()

    create_symlink(dotfiles_dir, home_dir / ".dotfiles.d")

    # Process .dotfiles.d/.*rc
    for f in sorted(dotfiles_dir.glob(".*rc")):
        if not f.is_file():
            continue
        create_symlink(f, home_dir / f.name)

    # Process .dotfiles.d/.*.d/main.*
    for d in sorted(dotfiles_dir.glob(".*.d")):
        if not d.is_dir():
            continue
        main_file = next(iter(sorted(d.glob("main.*"))), None)
        if main_file is None:
            # Do nothing if main.* file is not found
            continue
        create_symlink(main_file, home_dir / d.name.removesuffix(".d"))

    # Process .dotfiles.d/.config/*/
    # Only the directories under it are linked, so ~/.config itself is left intact
    config_dir = dotfiles_dir / ".config"
    if config_dir.is_dir():
        home_config_dir = home_dir / ".config"
        home_config_dir.mkdir(parents=True, exist_ok=True)
        for d in sorted(config_dir.iterdir()):
            if not d.is_dir():
                continue
            create_symlink(d, home_config_dir / d.name)

    print("Dotfiles setup complete.")


if __name__ == "__main__":
    main()
