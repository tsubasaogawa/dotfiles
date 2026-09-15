#!/usr/bin/env python3

"""Install dotfiles by linking managed entries into the user's home directory."""

from pathlib import Path
from typing import Iterator


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


def find_rc_files(dotfiles_dir: Path) -> Iterator[Path]:
    """Yield top-level rc files managed directly in the home directory."""
    yield from (path for path in sorted(dotfiles_dir.glob(".*rc")) if path.is_file())


def find_main_files(dotfiles_dir: Path) -> Iterator[tuple[Path, Path]]:
    """Yield source and destination pairs for top-level *.d directories."""
    for app_dir in sorted(dotfiles_dir.glob(".*.d")):
        if not app_dir.is_dir():
            continue
        main_file = next(iter(sorted(app_dir.glob("main.*"))), None)
        if main_file is not None:
            yield main_file, Path(app_dir.name.removesuffix(".d"))


def find_config_dirs(dotfiles_dir: Path) -> Iterator[Path]:
    """Yield managed directories below .config, never standalone files."""
    config_dir = dotfiles_dir / ".config"
    if config_dir.is_dir():
        yield from (path for path in sorted(config_dir.iterdir()) if path.is_dir())


def find_link_dirs(dotfiles_dir: Path) -> Iterator[Path]:
    """Yield top-level *.link directories whose entries are linked individually."""
    yield from (path for path in sorted(dotfiles_dir.glob(".*.link")) if path.is_dir())


def install_dotfiles(dotfiles_dir: Path, home_dir: Path) -> None:
    """Install every managed dotfile into home_dir."""
    create_symlink(dotfiles_dir, home_dir / ".dotfiles.d")

    for rc_file in find_rc_files(dotfiles_dir):
        create_symlink(rc_file, home_dir / rc_file.name)

    for main_file, destination_name in find_main_files(dotfiles_dir):
        create_symlink(main_file, home_dir / destination_name)

    config_entries = list(find_config_dirs(dotfiles_dir))
    if config_entries:
        home_config_dir = home_dir / ".config"
        home_config_dir.mkdir(parents=True, exist_ok=True)
        for config_entry in config_entries:
            create_symlink(config_entry, home_config_dir / config_entry.name)

    for link_dir in find_link_dirs(dotfiles_dir):
        target_dir = home_dir / link_dir.name.removesuffix(".link")
        target_dir.mkdir(parents=True, exist_ok=True)
        for entry in sorted(link_dir.iterdir()):
            create_symlink(entry, target_dir / entry.name)


def main() -> None:
    dotfiles_dir = Path(__file__).parent.resolve() / "dotfiles.d"
    install_dotfiles(dotfiles_dir, Path.home())
    print("Dotfiles setup complete.")


if __name__ == "__main__":
    main()
