#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Oxford Dictionaries API 提供者。

只向官方 API 发送规范化后的单词。App ID 和 App Key 从环境变量读取，
不会写入源码、配置文件、日志或返回的 WordEntry。
"""

import json
import os
import re
import threading
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from dictionary_models import WordEntry


SANDBOX_BASE_URL = "https://od-api-sandbox.oxforddictionaries.com/api/v2"
PRODUCTION_BASE_URL = "https://od-api.oxforddictionaries.com/api/v2"
VALID_WORD = re.compile(r"^[A-Za-z][A-Za-z'\-]{0,127}$")


class OxfordProviderError(RuntimeError):
    """Oxford 查询失败，但不包含任何凭据。"""


class OxfordCredentialsMissing(OxfordProviderError):
    pass


class OxfordAuthenticationError(OxfordProviderError):
    pass


class OxfordRateLimitError(OxfordProviderError):
    pass


def _unique(values):
    return tuple(dict.fromkeys(v.strip() for v in values if isinstance(v, str) and v.strip()))


def _label(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("text") or value.get("id") or ""
    return ""


def _walk_senses(senses):
    for sense in senses or ():
        if not isinstance(sense, dict):
            continue
        yield sense
        yield from _walk_senses(sense.get("subsenses"))


class OxfordDictionaryProvider:
    """将 Oxford Words API 响应规范化为 WordEntry。"""

    name = "oxford-dictionaries-api"

    def __init__(self, app_id, app_key, base_url=SANDBOX_BASE_URL,
                 language="en-gb", timeout=8, transport=None):
        if not app_id or not app_key:
            raise OxfordCredentialsMissing(
                "缺少 OXFORD_APP_ID 或 OXFORD_APP_KEY 环境变量")
        self._app_id = app_id
        self._app_key = app_key
        self.base_url = base_url.rstrip("/")
        self.language = language
        self.timeout = timeout
        self._transport = transport or self._request_json
        self._cache = {}
        self._cache_lock = threading.Lock()

    @classmethod
    def from_env(cls, **kwargs):
        """从用户环境变量建立提供者，不接受项目内明文配置。"""
        return cls(
            os.environ.get("OXFORD_APP_ID", "").strip(),
            os.environ.get("OXFORD_APP_KEY", "").strip(),
            base_url=os.environ.get("OXFORD_API_BASE_URL", SANDBOX_BASE_URL).strip(),
            **kwargs,
        )

    def _request_json(self, url, headers, timeout):
        request = Request(url, headers=headers, method="GET")
        try:
            with urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 404:
                return None
            if exc.code == 403:
                raise OxfordAuthenticationError(
                    "Oxford API 拒绝了凭据，请检查 App ID、App Key 和环境地址") from None
            if exc.code == 429:
                raise OxfordRateLimitError("Oxford API 调用额度已用完") from None
            raise OxfordProviderError(f"Oxford API 返回 HTTP {exc.code}") from None
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise OxfordProviderError(f"Oxford API 暂时不可用：{type(exc).__name__}") from None

    def lookup(self, word):
        query = word.strip().lower()
        if not VALID_WORD.fullmatch(query):
            return None
        # Oxford Sandbox 的英文数据只覆盖 A 开头的词。提前拦截可以避免白白消耗额度。
        if "sandbox" in self.base_url.lower() and not query.startswith("a"):
            return None
        with self._cache_lock:
            if query in self._cache:
                return self._cache[query]
            entry = self._lookup_uncached(query)
            self._cache[query] = entry
            return entry

    def _lookup_uncached(self, query):
        params = urlencode({"q": query})
        url = f"{self.base_url}/words/{quote(self.language, safe='-')}?{params}"
        payload = self._transport(
            url,
            {"app_id": self._app_id, "app_key": self._app_key,
             "Accept": "application/json"},
            self.timeout,
        )
        if not payload:
            return None
        return self._parse(query, payload, url)

    def _parse(self, query, payload, source_url):
        definitions, examples, synonyms, antonyms = [], [], [], []
        parts, phonetic_uk, phonetic_us, phonetic = [], "", "", ""
        display, lemma = query, query

        for result in payload.get("results", ()):
            if not isinstance(result, dict):
                continue
            display = result.get("word") or display
            lemma = result.get("id") or display or lemma
            for lexical in result.get("lexicalEntries", ()):
                if not isinstance(lexical, dict):
                    continue
                part = _label(lexical.get("lexicalCategory"))
                if part:
                    parts.append(part)
                for entry in lexical.get("entries", ()):
                    if not isinstance(entry, dict):
                        continue
                    for pron in entry.get("pronunciations", ()):
                        spelling = pron.get("phoneticSpelling", "")
                        if not spelling:
                            continue
                        phonetic = phonetic or spelling
                        dialects = " ".join(_label(x).lower()
                                            for x in pron.get("dialects", ()))
                        if "british" in dialects or "uk" in dialects:
                            phonetic_uk = phonetic_uk or spelling
                        if "american" in dialects or "us" in dialects:
                            phonetic_us = phonetic_us or spelling
                    for sense in _walk_senses(entry.get("senses")):
                        definitions.extend(sense.get("definitions", ()))
                        examples.extend(x.get("text", "") for x in sense.get("examples", ())
                                        if isinstance(x, dict))
                        synonyms.extend(_label(x) for x in sense.get("synonyms", ()))
                        antonyms.extend(_label(x) for x in sense.get("antonyms", ()))

        definitions = _unique(definitions)
        if not definitions and not examples and not synonyms and not phonetic:
            return None
        return WordEntry(
            word=query,
            display=display,
            lemma=lemma,
            part_of_speech=" / ".join(_unique(parts)),
            phonetic=phonetic,
            phonetic_uk=phonetic_uk,
            phonetic_us=phonetic_us,
            definitions_en=definitions,
            synonyms=_unique(synonyms),
            antonyms=_unique(antonyms),
            examples=_unique(examples),
            provider=self.name,
            source_url=source_url,
        )
