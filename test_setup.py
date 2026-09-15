#!/usr/bin/env python3

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import setup


class TestSetup(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.home_dir = self.test_dir / "home"
        self.dotfiles_dir = self.test_dir / "dotfiles.d"
        self.home_dir.mkdir()
        self.dotfiles_dir.mkdir()

        (self.dotfiles_dir / ".bashrc").touch()
        (self.dotfiles_dir / ".zshrc").touch()
        (self.dotfiles_dir / ".vim.d").mkdir()
        (self.dotfiles_dir / ".vim.d" / "main.vim").touch()
        (self.dotfiles_dir / ".tig.d").mkdir()
        (self.dotfiles_dir / ".tig.d" / "main.tig").touch()
        (self.dotfiles_dir / ".config").mkdir()
        (self.dotfiles_dir / ".config" / "mise").mkdir()
        (self.dotfiles_dir / ".config" / "mise" / "config.toml").touch()
        (self.dotfiles_dir / ".config" / "starship.toml").touch()
        (self.dotfiles_dir / ".tool.link").mkdir()
        (self.dotfiles_dir / ".tool.link" / "settings.json").touch()
        (self.dotfiles_dir / ".tool.link" / "hooks").mkdir()
        (self.dotfiles_dir / ".tool.link" / "hooks" / "hook.py").touch()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_create_symlink_new(self):
        src = self.dotfiles_dir / ".bashrc"
        dest = self.home_dir / ".bashrc"
        setup.create_symlink(src, dest)
        self.assertTrue(dest.is_symlink())
        self.assertEqual(os.readlink(dest), str(src))

    def test_create_symlink_backup(self):
        src = self.dotfiles_dir / ".bashrc"
        dest = self.home_dir / ".bashrc"
        dest.write_text("original content")
        setup.create_symlink(src, dest)
        backup_file = self.home_dir / ".bashrc.bak"
        self.assertTrue(backup_file.is_file())
        self.assertEqual(backup_file.read_text(), "original content")
        self.assertTrue(dest.is_symlink())
        self.assertEqual(os.readlink(dest), str(src))

    def test_create_symlink_overwrite(self):
        src = self.dotfiles_dir / ".bashrc"
        dest = self.home_dir / ".bashrc"
        dummy_src = self.test_dir / "dummy"
        dummy_src.touch()
        os.symlink(dummy_src, dest)

        setup.create_symlink(src, dest)
        self.assertTrue(dest.is_symlink())
        self.assertEqual(os.readlink(dest), str(src))
        self.assertFalse(
            (self.home_dir / ".bashrc.bak").exists()
        )

    def test_create_symlink_already_linked(self):
        src = self.dotfiles_dir / ".bashrc"
        dest = self.home_dir / ".bashrc"
        setup.create_symlink(src, dest)
        original_ino = dest.lstat().st_ino

        with patch.object(setup.Path, "unlink") as mock_unlink:
            setup.create_symlink(src, dest)
            mock_unlink.assert_not_called()

        self.assertTrue(dest.is_symlink())
        self.assertEqual(os.readlink(dest), str(src))
        self.assertEqual(dest.lstat().st_ino, original_ino)
        self.assertFalse((self.home_dir / ".bashrc.bak").exists())

    def test_install_dotfiles(self):
        setup.install_dotfiles(self.dotfiles_dir, self.home_dir)

        self.assertTrue((self.home_dir / ".bashrc").is_symlink())
        self.assertEqual(
            os.readlink(self.home_dir / ".bashrc"), str(self.dotfiles_dir / ".bashrc")
        )

        self.assertTrue((self.home_dir / ".zshrc").is_symlink())
        self.assertEqual(
            os.readlink(self.home_dir / ".zshrc"), str(self.dotfiles_dir / ".zshrc")
        )

        self.assertTrue((self.home_dir / ".vim").is_symlink())
        self.assertEqual(
            os.readlink(self.home_dir / ".vim"),
            str(self.dotfiles_dir / ".vim.d" / "main.vim"),
        )

        self.assertTrue((self.home_dir / ".tig").is_symlink())
        self.assertEqual(
            os.readlink(self.home_dir / ".tig"),
            str(self.dotfiles_dir / ".tig.d" / "main.tig"),
        )

        home_config = self.home_dir / ".config"
        self.assertTrue(home_config.is_dir())
        self.assertFalse(home_config.is_symlink())

        self.assertTrue((home_config / "mise").is_symlink())
        self.assertEqual(
            os.readlink(home_config / "mise"),
            str(self.dotfiles_dir / ".config" / "mise"),
        )

        self.assertFalse((home_config / "starship.toml").exists())

        home_tool = self.home_dir / ".tool"
        self.assertTrue(home_tool.is_dir())
        self.assertFalse(home_tool.is_symlink())

        self.assertTrue((home_tool / "settings.json").is_symlink())
        self.assertEqual(
            os.readlink(home_tool / "settings.json"),
            str(self.dotfiles_dir / ".tool.link" / "settings.json"),
        )
        self.assertTrue((home_tool / "hooks").is_symlink())
        self.assertEqual(
            os.readlink(home_tool / "hooks"),
            str(self.dotfiles_dir / ".tool.link" / "hooks"),
        )

        self.assertFalse((self.home_dir / ".tool.link").exists())

    def test_main_uses_the_standard_dotfiles_directory(self):
        with (
            patch.object(setup, "__file__", str(self.test_dir / "setup.py")),
            patch.object(setup.Path, "home", return_value=self.home_dir),
        ):
            setup.main()

        self.assertEqual(
            os.readlink(self.home_dir / ".bashrc"),
            str(self.dotfiles_dir / ".bashrc"),
        )

    def test_install_dotfiles_preserves_existing_config_dir(self):
        home_config = self.home_dir / ".config"
        unmanaged_file = home_config / "other_tool" / "settings.json"
        unmanaged_file.parent.mkdir(parents=True)
        unmanaged_file.write_text("keep me")

        setup.install_dotfiles(self.dotfiles_dir, self.home_dir)

        self.assertFalse(home_config.is_symlink())
        self.assertEqual(unmanaged_file.read_text(), "keep me")
        self.assertTrue((home_config / "mise").is_symlink())
        self.assertFalse((self.home_dir / ".config.bak").exists())

    def test_install_dotfiles_preserves_unmanaged_files_in_link_dir(self):
        home_tool = self.home_dir / ".tool"
        credentials = home_tool / ".credentials.json"
        credentials.parent.mkdir(parents=True)
        credentials.write_text("secret")

        setup.install_dotfiles(self.dotfiles_dir, self.home_dir)

        self.assertFalse(home_tool.is_symlink())
        self.assertEqual(credentials.read_text(), "secret")
        self.assertTrue((home_tool / "settings.json").is_symlink())
        self.assertFalse((self.home_dir / ".tool.bak").exists())

    def test_discovery_rules_protect_config_files_and_link_directories(self):
        self.assertEqual(
            list(setup.find_config_dirs(self.dotfiles_dir)),
            [self.dotfiles_dir / ".config" / "mise"],
        )
        self.assertEqual(
            list(setup.find_link_dirs(self.dotfiles_dir)),
            [self.dotfiles_dir / ".tool.link"],
        )


if __name__ == "__main__":
    unittest.main()
