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

## Usage

Run the following command to deploy the dotfiles automatically.

```bash
$ ./setup.py
```

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
