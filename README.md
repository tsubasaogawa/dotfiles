# dotfiles

My personal dotfiles.

## Overview

This repository manages my personal configuration files (dotfiles).
Running the `setup.py` script will automatically deploy these configuration files to your home directory by creating symbolic links.

## What `setup.py` does

The `setup.py` script deploys configuration files from the `dotfiles.d` directory to your home directory (`~/`) as symbolic links.

Here's how it works:

- **Creates Symbolic Links:**
  - It creates symbolic links from each configuration file in `dotfiles.d` to the corresponding location in your home directory.
- **Backs Up Existing Files:**
  - If a file or directory with the same name already exists at the destination, it will be backed up with a `.bak` extension before the symlink is created.
  - For example, an existing `~/.vimrc` will be renamed to `~/.vimrc.bak`.
- **Overwrites Existing Symlinks:**
  - If a symbolic link already exists at the destination, it will be removed and a new one will be created.

### Target Files

The script processes files based on the following rules:

1.  Files ending in `rc` directly under `dotfiles.d/` (e.g., `.vimrc`, `.tigrc`).
2.  Any file named `main.*` inside a directory ending with `.d` within `dotfiles.d/` (e.g., `.gitconfig.d`).
    - In this case, the symbolic link is created with the `.d` suffix removed from the directory name.
    - For example, `dotfiles.d/.gitconfig.d/main.gitconfig` will be linked as `~/.gitconfig`.
3.  Directories directly under `dotfiles.d/.config/`.
    - Only the directories themselves are linked, so your existing `~/.config` is never replaced.
    - For example, `dotfiles.d/.config/mise` will be linked as `~/.config/mise`.
    - `~/.config` is created if it does not exist. Files placed directly under `dotfiles.d/.config/` are ignored.
4.  Entries inside a directory ending with `.link` within `dotfiles.d/`.
    - Only the entries inside are linked, so the destination directory itself is never replaced.
    - The destination is the directory name with the `.link` suffix removed.
    - For example, `dotfiles.d/.claude.link/settings.json` will be linked as `~/.claude/settings.json`.
    - The destination directory is created if it does not exist.

## Usage

Run the following command to deploy the dotfiles automatically.

```bash
$ ./setup.py
```

## Optional Commands

The shell configuration detects optional commands and initialization files before using them. If an optional command is not installed, its integration is skipped without a warning. This applies to tools such as `anyenv`, `pyenv`, `direnv`, `mise`, `atuin`, `zoxide`, `gh`, and shell completion helpers.

Some existing startup tasks intentionally remain conditional on their managed files being absent. They can download Git completion files or Vim plugins, and some WSL maintenance scripts can call `sudo`.

## Verification

Run the following checks after changing the repository:

```bash
python3 -m unittest -v

while IFS= read -r file; do
  bash -n "$file"
done < <(
  rg --files --hidden \
    -g '*.bash' -g '*.sh' \
    -g '!node_modules/**' -g '!dist/**' -g '!build/**' \
    -g '!.venv/**' -g '!.terraform/**' -g '!vendor/**'
)
```

The Python test suite also loads `.bashrc.d/main.bash` with a temporary `HOME` and optional commands unavailable. It stubs the existing startup tasks that can use the network or `sudo`, so the verification does not change the host system.

## How to Add Your Own Dotfiles

You can add your own configuration files to the `dotfiles.d/` directory and run `setup.py` to manage them.

### Case 1: A Single File (e.g., `.my_custom_rc`)

1.  Add your configuration file to the `dotfiles.d/` directory.
    ```
    dotfiles
    └── dotfiles.d
        └── .my_custom_rc  <-- Add this file
    ```
2.  Run the script.
    ```bash
    $ ./setup.py
    ```
3.  A symbolic link will be created at `~/.my_custom_rc`.

### Case 2: A File Split Into Multiple Sources (e.g., `~/.gitconfig`)

The `setup.py` script gives special treatment to directories ending in `.d` within `dotfiles.d/`.

1.  Create a directory like `.gitconfig.d` inside `dotfiles.d/`.
2.  Place your main configuration file, named starting with `main` (e.g., `main.gitconfig`), inside it.
    ```
    dotfiles
    └── dotfiles.d
        └── .gitconfig.d         <-- Create this directory
            └── main.gitconfig   <-- This is the main config file
    ```
3.  Run the script.
    ```bash
    $ ./setup.py
    ```
4.  A symbolic link to `dotfiles.d/.gitconfig.d/main.gitconfig` will be created as `~/.gitconfig`.
    - Other files in the directory are not linked, so use them for sources that the main file includes.

#### Machine-Local Settings

Settings that should not be committed (credentials, machine-specific paths) go in a file named `main_local.<ext>` in the same `.d` directory, and the main file includes or sources it.
Everything matching `*_local.*` under `dotfiles.d/` is ignored by Git, so each machine keeps its own copy.

```
dotfiles
└── dotfiles.d
    └── .gitconfig.d
        ├── main.gitconfig         <-- Committed. Includes the file below
        └── main_local.gitconfig   <-- Not committed. Machine-local settings
```

### Case 3: Configuration Under `~/.config` (e.g., `~/.config/mise/config.toml`)

`~/.config` is shared with tools that are not managed here, so the script never replaces it. Instead, it links each directory under `dotfiles.d/.config/` individually.

1.  Create a directory named after the tool inside `dotfiles.d/.config/`.
2.  Place the configuration files inside it.
    ```
    dotfiles
    └── dotfiles.d
        └── .config
            └── mise            <-- Create this directory
                └── config.toml
    ```
3.  Run the script.
    ```bash
    $ ./setup.py
    ```
4.  A symbolic link to `dotfiles.d/.config/mise` will be created as `~/.config/mise`.

### Case 4: A Directory That Also Holds Machine-Local State (e.g., `~/.claude`)

Some tools keep their configuration and their runtime state in the same directory. `~/.claude` holds
committable rules and agent definitions next to credentials, session logs, and conversation history.
Linking the directory itself would pull that state into the repository, so the script links only the
entries inside a `*.link` directory and leaves the destination directory as a real directory.

1.  Create a directory named after the destination plus a `.link` suffix inside `dotfiles.d/`.
2.  Place only the files you want to commit inside it.
    ```
    dotfiles
    └── dotfiles.d
        └── .claude.link        <-- Create this directory
            ├── CLAUDE.md
            ├── settings.json
            └── hooks
                └── hook.py
    ```
3.  Run the script.
    ```bash
    $ ./setup.py
    ```
4.  `~/.claude` stays a real directory, and each entry inside it becomes a symbolic link.
    - Anything the tool writes into `~/.claude` that is not listed above stays out of the repository.
    - Files a linked script writes relative to itself (for example a `hooks/state/` cache) do land in
      the repository, so add them to `.gitignore`.
