#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest


BASE = os.path.dirname(os.path.abspath(__file__))


def read(name):
    with open(os.path.join(BASE, name), encoding="utf-8") as file:
        return file.read()


class InstallationContractTests(unittest.TestCase):
    def test_installer_creates_and_uses_project_venv(self):
        source = read("install.py")
        self.assertIn('"-m", "venv", VENV', source)
        self.assertIn('VENV_PYTHON, "-m", "pip"', source)
        self.assertIn('"-r", "requirements.txt"', source)
        self.assertIn('[VENV_PYTHON, "build_dict.py"]', source)
        self.assertIn('[VENV_PYTHON, "make_shortcut.py"]', source)

    def test_all_launchers_use_the_same_venv(self):
        for name in ("run.bat", "啟動.bat", "review-vocab.bat", "export-vocab.bat"):
            with self.subTest(name=name):
                self.assertIn(".venv\\Scripts\\python", read(name))

    def test_shortcuts_cover_lookup_and_review(self):
        source = read("make_shortcut.py")
        self.assertIn('"Oxford 划词助手"', source)
        self.assertIn('"hover_translate.py"', source)
        self.assertIn('"生词复习"', source)
        self.assertIn('"review_app.py"', source)

    def test_credentials_and_personal_data_are_gitignored(self):
        ignored = read(".gitignore")
        for pattern in (".env", "vocabulary.db", "exports/"):
            self.assertIn(pattern, ignored)


if __name__ == "__main__":
    unittest.main(verbosity=2)
