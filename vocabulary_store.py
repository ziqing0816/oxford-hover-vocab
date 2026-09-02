#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""本地生词库：去重、查询历史与间隔复习状态。"""

import json
import sqlite3
import threading
from datetime import datetime, timedelta, timezone


REVIEW_INTERVAL_DAYS = (1, 3, 7, 14, 30, 60, 120)


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def _iso(value):
    return value.isoformat().replace("+00:00", "Z")


def _json(values):
    return json.dumps(list(values), ensure_ascii=False)


class VocabularyStore:
    """线程安全的本地 SQLite 生词库。"""

    def __init__(self, path):
        self.path = path
        self._lock = threading.RLock()
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self._create_schema()

    def _create_schema(self):
        with self.db:
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS vocabulary (
                    lemma TEXT PRIMARY KEY,
                    word TEXT NOT NULL,
                    part_of_speech TEXT NOT NULL DEFAULT '',
                    phonetic TEXT NOT NULL DEFAULT '',
                    meanings_zh_cn TEXT NOT NULL DEFAULT '[]',
                    definitions_en TEXT NOT NULL DEFAULT '[]',
                    synonyms TEXT NOT NULL DEFAULT '[]',
                    antonyms TEXT NOT NULL DEFAULT '[]',
                    examples TEXT NOT NULL DEFAULT '[]',
                    provider TEXT NOT NULL DEFAULT '',
                    source_url TEXT NOT NULL DEFAULT '',
                    context_sentence TEXT NOT NULL DEFAULT '',
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    lookup_count INTEGER NOT NULL DEFAULT 1,
                    review_stage INTEGER NOT NULL DEFAULT 0,
                    next_review_at TEXT NOT NULL,
                    mastery_status TEXT NOT NULL DEFAULT 'learning'
                )
            """)
            self.db.execute("""
                CREATE INDEX IF NOT EXISTS idx_vocabulary_due
                ON vocabulary(mastery_status, next_review_at)
            """)

    @staticmethod
    def _values(entry):
        return {
            "lemma": (entry.lemma or entry.word).strip().lower(),
            "word": entry.display or entry.word,
            "part_of_speech": entry.part_of_speech,
            "phonetic": entry.phonetic,
            "meanings_zh_cn": _json(entry.meanings_zh_cn),
            "definitions_en": _json(entry.definitions_en),
            "synonyms": _json(entry.synonyms),
            "antonyms": _json(entry.antonyms),
            "examples": _json(entry.examples),
            "provider": entry.provider,
            "source_url": entry.source_url,
        }

    def record_lookup(self, entry, context_sentence="", now=None):
        """保存一次真实划词；同一 lemma 更新并把查询次数加一。"""
        if entry is None:
            return
        values = self._values(entry)
        if not values["lemma"]:
            return
        stamp = _iso(now or _now())
        values.update(context_sentence=context_sentence or "", stamp=stamp)
        with self._lock, self.db:
            self.db.execute("""
                INSERT INTO vocabulary (
                    lemma, word, part_of_speech, phonetic, meanings_zh_cn,
                    definitions_en, synonyms, antonyms, examples, provider,
                    source_url, context_sentence, first_seen_at, last_seen_at,
                    lookup_count, next_review_at
                ) VALUES (
                    :lemma, :word, :part_of_speech, :phonetic, :meanings_zh_cn,
                    :definitions_en, :synonyms, :antonyms, :examples, :provider,
                    :source_url, :context_sentence, :stamp, :stamp, 1, :stamp
                )
                ON CONFLICT(lemma) DO UPDATE SET
                    word=excluded.word,
                    part_of_speech=CASE WHEN excluded.part_of_speech != ''
                                        THEN excluded.part_of_speech ELSE part_of_speech END,
                    phonetic=CASE WHEN excluded.phonetic != ''
                                  THEN excluded.phonetic ELSE phonetic END,
                    meanings_zh_cn=CASE WHEN excluded.meanings_zh_cn != '[]'
                                        THEN excluded.meanings_zh_cn ELSE meanings_zh_cn END,
                    definitions_en=CASE WHEN excluded.definitions_en != '[]'
                                        THEN excluded.definitions_en ELSE definitions_en END,
                    synonyms=CASE WHEN excluded.synonyms != '[]'
                                  THEN excluded.synonyms ELSE synonyms END,
                    antonyms=CASE WHEN excluded.antonyms != '[]'
                                  THEN excluded.antonyms ELSE antonyms END,
                    examples=CASE WHEN excluded.examples != '[]'
                                  THEN excluded.examples ELSE examples END,
                    provider=CASE WHEN excluded.provider != ''
                                  THEN excluded.provider ELSE provider END,
                    source_url=CASE WHEN excluded.source_url != ''
                                    THEN excluded.source_url ELSE source_url END,
                    context_sentence=CASE WHEN excluded.context_sentence != ''
                                          THEN excluded.context_sentence ELSE context_sentence END,
                    last_seen_at=excluded.last_seen_at,
                    lookup_count=lookup_count + 1
            """, values)

    def enrich(self, entry):
        """补充 Oxford 内容，不增加查询次数或改变复习进度。"""
        if entry is None:
            return
        values = self._values(entry)
        with self._lock, self.db:
            self.db.execute("""
                UPDATE vocabulary SET
                    part_of_speech=:part_of_speech,
                    phonetic=:phonetic,
                    meanings_zh_cn=:meanings_zh_cn,
                    definitions_en=:definitions_en,
                    synonyms=:synonyms,
                    antonyms=:antonyms,
                    examples=:examples,
                    provider=:provider,
                    source_url=:source_url
                WHERE lemma=:lemma
            """, values)

    def get(self, lemma):
        with self._lock:
            row = self.db.execute(
                "SELECT * FROM vocabulary WHERE lemma=?", (lemma.lower(),)).fetchone()
        return dict(row) if row else None

    def count(self):
        with self._lock:
            return self.db.execute("SELECT COUNT(*) FROM vocabulary").fetchone()[0]

    def due(self, now=None, limit=50):
        stamp = _iso(now or _now())
        with self._lock:
            rows = self.db.execute("""
                SELECT * FROM vocabulary
                WHERE mastery_status != 'mastered' AND next_review_at <= ?
                ORDER BY next_review_at, lookup_count DESC LIMIT ?
            """, (stamp, max(1, int(limit)))).fetchall()
        return [dict(row) for row in rows]

    def all(self):
        with self._lock:
            rows = self.db.execute("""
                SELECT * FROM vocabulary
                ORDER BY last_seen_at DESC, lemma
            """).fetchall()
        return [dict(row) for row in rows]

    def review(self, lemma, rating, now=None):
        """记录 again/hard/good/easy，并计算下次复习时间。"""
        if rating not in {"again", "hard", "good", "easy"}:
            raise ValueError("rating 必须是 again、hard、good 或 easy")
        current = self.get(lemma)
        if current is None:
            raise KeyError(lemma)
        stage = int(current["review_stage"])
        if rating == "again":
            stage, days = 0, 0
        elif rating == "hard":
            days = 1 if stage == 0 else REVIEW_INTERVAL_DAYS[min(stage - 1, 6)]
        else:
            stage = min(7, stage + (2 if rating == "easy" else 1))
            days = REVIEW_INTERVAL_DAYS[stage - 1]
        base = now or _now()
        next_review = base + (timedelta(minutes=10) if days == 0 else timedelta(days=days))
        status = "mastered" if stage >= 7 and rating == "easy" else "learning"
        with self._lock, self.db:
            self.db.execute("""
                UPDATE vocabulary
                SET review_stage=?, next_review_at=?, mastery_status=?
                WHERE lemma=?
            """, (stage, _iso(next_review), status, lemma.lower()))
        return self.get(lemma)

    def close(self):
        with self._lock:
            self.db.close()
