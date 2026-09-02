#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
import tempfile
import unittest
from datetime import datetime, timezone

from dictionary_models import WordEntry
from vocab_cli import export_all
from vocabulary_store import VocabularyStore


class VocabCliTests(unittest.TestCase):
    def test_export_markdown_and_excel_friendly_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            store = VocabularyStore(os.path.join(folder, "vocabulary.db"))
            entry = WordEntry(
                word="apples", display="apple", lemma="apple",
                part_of_speech="Noun", phonetic="ˈap(ə)l",
                meanings_zh_cn=("n. 苹果",), definitions_en=("A round fruit.",),
                synonyms=("fruit",), examples=("She ate an apple.",),
                provider="test",
            )
            store.record_lookup(
                entry, "=HYPERLINK(\"unsafe\")",
                datetime(2026, 9, 3, 12, 0, tzinfo=timezone.utc))
            md, csv_path, count = export_all(store, os.path.join(folder, "exports"))
            store.close()

            self.assertEqual(count, 1)
            with open(md, encoding="utf-8") as file:
                markdown = file.read()
            self.assertIn("# 我的英语生词复习", markdown)
            self.assertIn("n. 苹果", markdown)
            self.assertIn("A round fruit.", markdown)

            with open(csv_path, "rb") as file:
                self.assertEqual(file.read(3), b"\xef\xbb\xbf")
            with open(csv_path, encoding="utf-8-sig", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(rows[0]["lemma"], "apple")
            self.assertEqual(rows[0]["meanings_zh_cn"], "n. 苹果")
            self.assertTrue(rows[0]["context_sentence"].startswith("'="))


if __name__ == "__main__":
    unittest.main(verbosity=2)
