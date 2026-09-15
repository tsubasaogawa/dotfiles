#!/usr/bin/env python3

from pathlib import Path


def create_symlink(src: Path, dest: Path) -> None:
    """Create or replace dest as a symbolic link to src."""
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
    dotfiles_dir = Path(__file__).parent.resolve() / "dotfiles.d"
    home_dir = Path.home()

    create_symlink(dotfiles_dir, home_dir / ".dotfiles.d")

    for rc_file in sorted(dotfiles_dir.glob(".*rc")):
        if not rc_file.is_file():
            continue
        create_symlink(rc_file, home_dir / rc_file.name)

    for app_dir in sorted(dotfiles_dir.glob(".*.d")):
        if not app_dir.is_dir():
            continue
        main_file = next(iter(sorted(app_dir.glob("main.*"))), None)
        if main_file is None:
            continue
        create_symlink(main_file, home_dir / app_dir.name.removesuffix(".d"))

    config_dir = dotfiles_dir / ".config"
    if config_dir.is_dir():
        home_config_dir = home_dir / ".config"
        home_config_dir.mkdir(parents=True, exist_ok=True)
        for config_entry in sorted(config_dir.iterdir()):
            if not config_entry.is_dir():
                continue
            create_symlink(config_entry, home_config_dir / config_entry.name)

    for link_dir in sorted(dotfiles_dir.glob(".*.link")):
        if not link_dir.is_dir():
            continue
        target_dir = home_dir / link_dir.name.removesuffix(".link")
        target_dir.mkdir(parents=True, exist_ok=True)
        for entry in sorted(link_dir.iterdir()):
            create_symlink(entry, target_dir / entry.name)

    print("Dotfiles setup complete.")


if __name__ == "__main__":
    main()
