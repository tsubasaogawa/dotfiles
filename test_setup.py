#!/usr/bin/env python3

import unittest
import os
import shutil
from pathlib import Path
from unittest.mock import patch
import tempfile

# テスト対象のスクリプトをインポート
import setup

class TestSetup(unittest.TestCase):

    def setUp(self):
        """テストの前に一時的なディレクトリとファイルを作成する"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.home_dir = self.test_dir / "home"
        self.dotfiles_dir = self.test_dir / "dotfiles.d"
        self.home_dir.mkdir()
        self.dotfiles_dir.mkdir()

        # テスト用のdotfilesを作成
        (self.dotfiles_dir / ".bashrc").touch()
        (self.dotfiles_dir / ".zshrc").touch()
        (self.dotfiles_dir / ".gitconfig").touch()
        (self.dotfiles_dir / ".vim.d").mkdir()
        (self.dotfiles_dir / ".vim.d" / "main.vim").touch()
        (self.dotfiles_dir / ".tig.d").mkdir()
        (self.dotfiles_dir / ".tig.d" / "main.tig").touch()


    def tearDown(self):
        """テストの後に一時的なディレクトリをクリーンアップする"""
        shutil.rmtree(self.test_dir)

    def test_create_symlink_new(self):
        """新しいシンボリックリンクが正しく作成されることをテストする"""
        src = self.dotfiles_dir / ".bashrc"
        dest = self.home_dir / ".bashrc"
        setup.create_symlink(src, dest)
        self.assertTrue(dest.is_symlink())
        self.assertEqual(os.readlink(dest), str(src))

    def test_create_symlink_backup(self):
        """既存のファイルがバックアップされることをテストする"""
        src = self.dotfiles_dir / ".bashrc"
        dest = self.home_dir / ".bashrc"
        dest.write_text("original content")  # 既存のファイルを作成
        setup.create_symlink(src, dest)
        backup_file = self.home_dir / ".bashrc.bak"
        self.assertTrue(backup_file.is_file())
        self.assertEqual(backup_file.read_text(), "original content")
        self.assertTrue(dest.is_symlink())
        self.assertEqual(os.readlink(dest), str(src))

    def test_create_symlink_overwrite(self):
        """既存のシンボリックリンクが上書きされることをテストする"""
        src = self.dotfiles_dir / ".bashrc"
        dest = self.home_dir / ".bashrc"
        dummy_src = self.test_dir / "dummy"
        dummy_src.touch()
        os.symlink(dummy_src, dest) # 既存のシンボリックリンクを作成

        setup.create_symlink(src, dest)
        self.assertTrue(dest.is_symlink())
        self.assertEqual(os.readlink(dest), str(src))
        self.assertFalse((self.home_dir / ".bashrc.bak").exists()) # バックアップが作成されないこと

    @patch('setup.Path.home')
    @patch('setup.Path.resolve')
    def test_main(self, mock_resolve, mock_home):
        """main関数が正しくシンボリックリンクを作成することをテストする"""
        # Path.home() と Path.resolve() をモックして、テストディレクトリを指すようにする
        mock_home.return_value = self.home_dir
        # __file__ の親ディレクトリをモック
        mock_resolve.return_value = self.test_dir

        # setup.pyのmain関数を実行
        with patch('__main__.__file__', str(self.test_dir / 'setup.py')):
            setup.main()

        # シンボリックリンクが正しく作成されたか確認
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
