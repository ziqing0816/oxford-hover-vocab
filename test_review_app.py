#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from review_app import review_content


class ReviewContentTests(unittest.TestCase):
    def test_database_row_becomes_simplified_chinese_card(self):
        row = {
            "word": "apple", "lemma": "apple", "phonetic": "ˈap(ə)l",
            "part_of_speech": "Noun", "meanings_zh_cn": '["n. 苹果"]',
            "definitions_en": '["A round fruit."]',
            "synonyms": '["fruit", "pome"]',
            "examples": '["She ate an apple."]',
            "context_sentence": "Apples are nutritious.",
        }
        card = review_content(row)
        self.assertEqual(card["meaning"], "n. 苹果")
        self.assertIn("A round fruit", card["definition"])
        self.assertEqual(card["synonyms"], "fruit, pome")
        self.assertEqual(card["phonetic"], "/ˈap(ə)l/")

    def test_invalid_json_is_treated_as_empty(self):
        card = review_content({"word": "test", "meanings_zh_cn": "broken"})
        self.assertEqual(card["meaning"], "暂无简体释义")
        self.assertEqual(card["definition"], "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
