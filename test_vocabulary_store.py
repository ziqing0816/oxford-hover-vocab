#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone

from dictionary_models import WordEntry
from vocabulary_store import VocabularyStore


LOCAL = WordEntry(
    word="apples", display="apples", lemma="apple", phonetic="æpl",
    meanings_zh_cn=("n. 苹果",), provider="local-ecdict",
)
ENRICHED = WordEntry(
    word="apples", display="apple", lemma="apple", part_of_speech="Noun",
    phonetic="ˈap(ə)l", meanings_zh_cn=("n. 苹果",),
    definitions_en=("A round fruit.",), synonyms=("fruit",),
    examples=("She ate an apple.",), provider="oxford+local",
    source_url="https://example.invalid?q=apple",
)


class VocabularyStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = VocabularyStore(os.path.join(self.tmp.name, "vocabulary.db"))
        self.now = datetime(2026, 9, 3, 12, 0, tzinfo=timezone.utc)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_lookup_is_deduplicated_by_lemma(self):
        self.store.record_lookup(LOCAL, "I bought apples.", self.now)
        self.store.record_lookup(LOCAL, "Apples are fruit.", self.now)
        self.assertEqual(self.store.count(), 1)
        row = self.store.get("apple")
        self.assertEqual(row["lookup_count"], 2)
        self.assertEqual(row["context_sentence"], "Apples are fruit.")
        self.assertEqual(json.loads(row["meanings_zh_cn"]), ["n. 苹果"])

    def test_oxford_enrichment_does_not_increment_count(self):
        self.store.record_lookup(LOCAL, "I bought apples.", self.now)
        self.store.enrich(ENRICHED)
        row = self.store.get("apple")
        self.assertEqual(row["lookup_count"], 1)
        self.assertEqual(json.loads(row["definitions_en"]), ["A round fruit."])
        self.assertEqual(json.loads(row["synonyms"]), ["fruit"])

    def test_due_and_review_schedule(self):
        self.store.record_lookup(LOCAL, now=self.now)
        self.assertEqual(len(self.store.due(self.now)), 1)
        reviewed = self.store.review("apple", "good", self.now)
        self.assertEqual(reviewed["review_stage"], 1)
        self.assertIn("2026-09-04T12:00:00", reviewed["next_review_at"])
        self.assertEqual(len(self.store.due(self.now)), 0)
        again = self.store.review("apple", "again", self.now)
        self.assertEqual(again["review_stage"], 0)
        self.assertIn("12:10:00", again["next_review_at"])

    def test_credentials_are_not_schema_fields(self):
        columns = {row[1] for row in self.store.db.execute("PRAGMA table_info(vocabulary)")}
        self.assertNotIn("app_id", columns)
        self.assertNotIn("app_key", columns)


if __name__ == "__main__":
    unittest.main(verbosity=2)
