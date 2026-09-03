#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""组合在线 Oxford 数据与本地简体中文词典。"""

import threading

from dictionary_models import WordEntry
from oxford_provider import OxfordProviderError


def merge_entries(online, local):
    """Oxford 负责英英内容，本地词典补充简中释义和离线元数据。"""
    if online is None:
        return local
    if local is None:
        return online
    return WordEntry(
        word=online.word or local.word,
        display=online.display or local.display,
        lemma=online.lemma or local.lemma,
        part_of_speech=online.part_of_speech or local.part_of_speech,
        phonetic=online.phonetic or local.phonetic,
        phonetic_uk=online.phonetic_uk,
        phonetic_us=online.phonetic_us,
        meanings_zh_cn=local.meanings_zh_cn,
        definitions_en=online.definitions_en,
        synonyms=online.synonyms,
        antonyms=online.antonyms,
        collocations=online.collocations,
        examples=online.examples,
        provider=f"{online.provider}+{local.provider}",
        source_url=online.source_url,
        collins=local.collins,
        frequency=local.frequency,
        tags=local.tags,
        via=local.via,
    )


class FallbackDictionaryProvider:
    """查询 Oxford，失败时静默保留本地结果和可检查的错误状态。"""

    name = "oxford-with-local-fallback"

    def __init__(self, online, local):
        self.online = online
        self.local = local
        self.last_error = None
        self._lookup_lock = threading.Lock()

    def lookup(self, word):
        # last_error 与返回值属于同一次查询；串行化可避免后台请求互相覆盖状态。
        with self._lookup_lock:
            local_entry = self.local.lookup(word)
            try:
                online_entry = self.online.lookup(word)
                self.last_error = None
            except OxfordProviderError as exc:
                self.last_error = exc
                return local_entry
            return merge_entries(online_entry, local_entry)
