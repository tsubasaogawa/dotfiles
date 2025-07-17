#!/usr/bin/env python3

import unittest
import os
import shutil
from pathlib import Path
from unittest.mock import patch
import tempfile

# Import the script to be tested
import setup

class TestSetup(unittest.TestCase):

    def setUp(self):
        """Create temporary directories and files before each test."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.home_dir = self.test_dir / "home"
        self.dotfiles_dir = self.test_dir / "dotfiles.d"
        self.home_dir.mkdir()
        self.dotfiles_dir.mkdir()

        # Create dummy dotfiles for testing
        (self.dotfiles_dir / ".bashrc").touch()
        (self.dotfiles_dir / ".zshrc").touch()
        (self.dotfiles_dir / ".gitconfig").touch()
        (self.dotfiles_dir / ".vim.d").mkdir()
        (self.dotfiles_dir / ".vim.d" / "main.vim").touch()
        (self.dotfiles_dir / ".tig.d").mkdir()
        (self.dotfiles_dir / ".tig.d" / "main.tig").touch()


    def tearDown(self):
        """Clean up temporary directories after each test."""
        shutil.rmtree(self.test_dir)

    def test_create_symlink_new(self):
        """Test that a new symlink is created correctly."""
        src = self.dotfiles_dir / ".bashrc"
        dest = self.home_dir / ".bashrc"
        setup.create_symlink(src, dest)
        self.assertTrue(dest.is_symlink())
        self.assertEqual(os.readlink(dest), str(src))

    def test_create_symlink_backup(self):
        """Test that an existing file is backed up."""
        src = self.dotfiles_dir / ".bashrc"
        dest = self.home_dir / ".bashrc"
        dest.write_text("original content")  # Create an existing file
        setup.create_symlink(src, dest)
        backup_file = self.home_dir / ".bashrc.bak"
        self.assertTrue(backup_file.is_file())
        self.assertEqual(backup_file.read_text(), "original content")
        self.assertTrue(dest.is_symlink())
        self.assertEqual(os.readlink(dest), str(src))

    def test_create_symlink_overwrite(self):
        """Test that an existing symlink is overwritten."""
        src = self.dotfiles_dir / ".bashrc"
        dest = self.home_dir / ".bashrc"
        dummy_src = self.test_dir / "dummy"
        dummy_src.touch()
        os.symlink(dummy_src, dest) # Create an existing symlink

        setup.create_symlink(src, dest)
        self.assertTrue(dest.is_symlink())
        self.assertEqual(os.readlink(dest), str(src))
        self.assertFalse((self.home_dir / ".bashrc.bak").exists()) # Ensure no backup is created

    @patch('setup.Path.home')
    @patch('setup.Path.resolve')
    def test_main(self, mock_resolve, mock_home):
        """Test that the main function creates symlinks correctly."""
        # Mock Path.home() and Path.resolve() to point to the test directory
        mock_home.return_value = self.home_dir
        # Mock the parent directory of __file__
        mock_resolve.return_value = self.test_dir

        # Execute the main function of setup.py
        with patch('__main__.__file__', str(self.test_dir / 'setup.py')):
            setup.main()

        # Check if the symlinks were created correctly
        self.assertTrue((self.home_dir / ".bashrc").is_symlink())
        self.assertEqual(os.readlink(self.home_dir / ".bashrc"), str(self.dotfiles_dir / ".bashrc"))

        self.assertTrue((self.home_dir / ".zshrc").is_symlink())
        self.assertEqual(os.readlink(self.home_dir / ".zshrc"), str(self.dotfiles_dir / ".zshrc"))

        self.assertTrue((self.home_dir / ".gitconfig").is_symlink())
        self.assertEqual(os.readlink(self.home_dir / ".gitconfig"), str(self.dotfiles_dir / ".gitconfig"))

        self.assertTrue((self.home_dir / ".vim").is_symlink())
        self.assertEqual(os.readlink(self.home_dir / ".vim"), str(self.dotfiles_dir / ".vim.d" / "main.vim"))

        self.assertTrue((self.home_dir / ".tig").is_symlink())
        self.assertEqual(os.readlink(self.home_dir / ".tig"), str(self.dotfiles_dir / ".tig.d" / "main.tig"))


if __name__ == '__main__':
    unittest.main()
