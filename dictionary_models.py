#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""词典提供者共享的数据模型与接口。"""

from dataclasses import dataclass
from typing import Optional, Protocol, Tuple, runtime_checkable


@dataclass(frozen=True)
class WordEntry:
    """一个与具体词典供应商无关的规范化词条。"""

    word: str
    display: str
    lemma: str
    part_of_speech: str = ""
    phonetic: str = ""
    phonetic_uk: str = ""
    phonetic_us: str = ""
    meanings_zh_cn: Tuple[str, ...] = ()
    definitions_en: Tuple[str, ...] = ()
    synonyms: Tuple[str, ...] = ()
    antonyms: Tuple[str, ...] = ()
    collocations: Tuple[str, ...] = ()
    examples: Tuple[str, ...] = ()
    provider: str = ""
    source_url: str = ""
    collins: int = 0
    frequency: int = 0
    tags: Tuple[str, ...] = ()
    via: Optional[str] = None

    @property
    def trans(self):
        return "\n".join(self.meanings_zh_cn)

    @property
    def senses(self):
        return self.meanings_zh_cn


@runtime_checkable
class DictionaryProvider(Protocol):
    """所有词典实现都必须遵守的最小接口。"""

    name: str

    def lookup(self, word: str) -> Optional[WordEntry]:
        ...
