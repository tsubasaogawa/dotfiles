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

1.  Files ending in `.rc` directly under `dotfiles.d/` (e.g., `.vimrc`, `.zshrc`).
2.  The `dotfiles.d/.gitconfig` file.
3.  Any file named `main.*` inside a directory ending with `.d` within `dotfiles.d/` (e.g., `.config.d`).
    - In this case, the symbolic link is created with the `.d` suffix removed from the directory name.
    - For example, `dotfiles.d/.config.d/main.vim` will be linked as `~/.config`.

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

### Case 2: Configuration Requiring a Directory (e.g., `~/.config/foo/settings.conf`)

The `setup.py` script gives special treatment to directories ending in `.d` within `dotfiles.d/`.

1.  Create a directory like `.config.d` inside `dotfiles.d/`.
2.  Place your main configuration file, named starting with `main` (e.g., `main.conf`), inside it.
    ```
    dotfiles
    └── dotfiles.d
        └── .config.d      <-- Create this directory
            └── main.conf  <-- This is the main config file
    ```
3.  Run the script.
    ```bash
    $ ./setup.py
    ```
4.  A symbolic link to `dotfiles.d/.config.d/main.conf` will be created as `~/.config`.
