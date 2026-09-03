#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from dictionary_models import DictionaryProvider, WordEntry
from oxford_provider import OxfordProviderError
from provider_chain import FallbackDictionaryProvider, merge_entries


LOCAL = WordEntry(
    word="apple", display="apple", lemma="apple", phonetic="æpl",
    meanings_zh_cn=("n. 苹果",), provider="local-ecdict", collins=5,
    tags=("toefl",),
)
ONLINE = WordEntry(
    word="apple", display="apple", lemma="apple", part_of_speech="Noun",
    phonetic="ˈap(ə)l", definitions_en=("A round fruit.",),
    synonyms=("fruit",), examples=("She ate an apple.",),
    provider="oxford-dictionaries-api", source_url="https://example.invalid/apple",
)


class StubProvider:
    name = "stub"

    def __init__(self, result=None, error=None):
        self.result, self.error = result, error

    def lookup(self, _word):
        if self.error:
            raise self.error
        return self.result


class ProviderChainTests(unittest.TestCase):
    def test_merge_preserves_each_sources_role(self):
        entry = merge_entries(ONLINE, LOCAL)
        self.assertEqual(entry.definitions_en, ONLINE.definitions_en)
        self.assertEqual(entry.synonyms, ONLINE.synonyms)
        self.assertEqual(entry.meanings_zh_cn, LOCAL.meanings_zh_cn)
        self.assertEqual(entry.collins, LOCAL.collins)
        self.assertEqual(entry.source_url, ONLINE.source_url)

    def test_network_failure_falls_back_to_local(self):
        provider = FallbackDictionaryProvider(
            StubProvider(error=OxfordProviderError("offline")), StubProvider(LOCAL))
        self.assertIsInstance(provider, DictionaryProvider)
        self.assertEqual(provider.lookup("apple"), LOCAL)
        self.assertIsInstance(provider.last_error, OxfordProviderError)

    def test_online_miss_still_returns_local(self):
        provider = FallbackDictionaryProvider(StubProvider(None), StubProvider(LOCAL))
        self.assertEqual(provider.lookup("apple"), LOCAL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
