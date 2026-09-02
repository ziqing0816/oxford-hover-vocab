#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""不消耗 Oxford API 额度的连接器单元测试。"""

import os
import unittest
from unittest.mock import patch

from dictionary_models import DictionaryProvider, WordEntry
from oxford_provider import (OxfordCredentialsMissing,
                             OxfordDictionaryProvider, SANDBOX_BASE_URL)


FIXTURE = {
    "results": [{
        "id": "apple",
        "word": "apple",
        "lexicalEntries": [{
            "lexicalCategory": {"id": "noun", "text": "Noun"},
            "entries": [{
                "pronunciations": [
                    {"dialects": ["British English"], "phoneticSpelling": "ˈap(ə)l"},
                    {"dialects": ["American English"], "phoneticSpelling": "ˈæpəl"},
                ],
                "senses": [{
                    "definitions": ["The round fruit of a tree of the rose family."],
                    "examples": [{"text": "An apple a day is a familiar saying."}],
                    "synonyms": [{"text": "fruit"}, {"text": "fruit"}],
                    "antonyms": [{"text": "vegetable"}],
                    "subsenses": [{"definitions": ["The tree bearing apples."]}],
                }],
            }],
        }],
    }],
}


class OxfordProviderTests(unittest.TestCase):
    def test_credentials_are_required(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(OxfordCredentialsMissing):
                OxfordDictionaryProvider.from_env()

    def test_words_request_and_normalisation(self):
        captured = {}

        def transport(url, headers, timeout):
            captured.update(url=url, headers=headers, timeout=timeout)
            return FIXTURE

        provider = OxfordDictionaryProvider("test-id", "test-secret", transport=transport)
        entry = provider.lookup("Apple")
        self.assertIsInstance(provider, DictionaryProvider)
        self.assertIsInstance(entry, WordEntry)
        self.assertEqual(entry.lemma, "apple")
        self.assertEqual(entry.part_of_speech, "Noun")
        self.assertEqual(len(entry.definitions_en), 2)
        self.assertEqual(entry.synonyms, ("fruit",))
        self.assertEqual(entry.phonetic_uk, "ˈap(ə)l")
        self.assertEqual(entry.phonetic_us, "ˈæpəl")
        self.assertTrue(captured["url"].startswith(SANDBOX_BASE_URL + "/words/en-gb?"))
        self.assertIn("q=apple", captured["url"])
        self.assertNotIn("test-secret", captured["url"])
        self.assertEqual(captured["headers"]["app_key"], "test-secret")

    def test_invalid_input_never_reaches_network(self):
        def fail_transport(*_args):
            self.fail("无效输入不应调用网络")

        provider = OxfordDictionaryProvider("id", "key", transport=fail_transport)
        self.assertIsNone(provider.lookup("two words"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
