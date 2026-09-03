#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生词库导出与复习命令。"""

import argparse
import csv
import json
import os
from datetime import datetime

from vocabulary_store import VocabularyStore


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB = os.path.join(BASE_DIR, "vocabulary.db")
DEFAULT_EXPORT_DIR = os.path.join(BASE_DIR, "exports")
RATING_ALIASES = {
    "1": "again", "again": "again", "不认识": "again",
    "2": "hard", "hard": "hard", "困难": "hard",
    "3": "good", "good": "good", "认识": "good",
    "4": "easy", "easy": "easy", "简单": "easy",
}


def _list(row, field):
    try:
        value = json.loads(row[field])
        return value if isinstance(value, list) else []
    except (TypeError, ValueError, json.JSONDecodeError):
        return []


def _md(text):
    return str(text or "").replace("|", "\\|").replace("\n", "<br>")


def _csv_safe(value):
    """阻止 Excel 将词条或原句解释为公式。"""
    text = str(value if value is not None else "")
    return "'" + text if text.startswith(("=", "+", "-", "@")) else text


def export_markdown(rows, path):
    """生成适合直接阅读和打印的 Markdown 复习文档。"""
    generated = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# 我的英语生词复习",
        "",
        f"> 生成时间：{generated}　共 {len(rows)} 个词",
        "",
    ]
    if not rows:
        lines.append("还没有保存生词。运行划词工具后再生成一次即可。")
    for index, row in enumerate(rows, 1):
        zh = "；".join(_list(row, "meanings_zh_cn")) or "—"
        definitions = _list(row, "definitions_en")
        synonyms = _list(row, "synonyms")
        examples = _list(row, "examples")
        lines.extend([
            f"## {index}. {_md(row['word'])}",
            "",
            f"- 原形：`{_md(row['lemma'])}`",
            f"- 词性：{_md(row['part_of_speech']) or '—'}",
            f"- 音标：/{_md(row['phonetic'])}/" if row["phonetic"] else "- 音标：—",
            f"- 简体释义：{_md(zh)}",
        ])
        if definitions:
            lines.append("- 英英释义：" + _md("；".join(definitions)))
        if synonyms:
            lines.append("- 同义词：" + _md(", ".join(synonyms)))
        if examples:
            lines.append("- 例句：" + _md("；".join(examples)))
        if row["context_sentence"]:
            lines.append("- 我的原句：" + _md(row["context_sentence"]))
        lines.extend([
            f"- 查询次数：{row['lookup_count']}　复习阶段：{row['review_stage']}",
            f"- 下次复习：{_md(row['next_review_at'])}",
            "",
        ])
    with open(path, "w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(lines))


CSV_FIELDS = (
    "word", "lemma", "part_of_speech", "phonetic", "meanings_zh_cn",
    "definitions_en", "synonyms", "examples", "context_sentence",
    "lookup_count", "first_seen_at", "last_seen_at", "review_stage",
    "next_review_at", "mastery_status", "provider", "source_url",
)


def export_csv(rows, path):
    """生成 Excel 可直接打开的 UTF-8 BOM CSV。"""
    with open(path, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            item = dict(row)
            for field in ("meanings_zh_cn", "definitions_en", "synonyms", "examples"):
                item[field] = " | ".join(_list(row, field))
            for field in CSV_FIELDS:
                item[field] = _csv_safe(item.get(field, ""))
            writer.writerow(item)


def export_all(store, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    rows = store.all()
    markdown_path = os.path.join(output_dir, "vocabulary-review.md")
    csv_path = os.path.join(output_dir, "vocabulary.csv")
    export_markdown(rows, markdown_path)
    export_csv(rows, csv_path)
    return markdown_path, csv_path, len(rows)


def build_parser():
    parser = argparse.ArgumentParser(description="导出并复习本地英语生词")
    parser.add_argument("--db", default=DEFAULT_DB, help="生词数据库路径")
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export", help="生成 Markdown 和 CSV")
    export.add_argument("--output", default=DEFAULT_EXPORT_DIR, help="导出文件夹")
    due = sub.add_parser("due", help="查看当前到期单词")
    due.add_argument("--limit", type=int, default=20)
    review = sub.add_parser("review", help="记录一次复习结果")
    review.add_argument("word", help="单词或原形")
    review.add_argument("rating", help="1不认识 / 2困难 / 3认识 / 4简单")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    store = VocabularyStore(args.db)
    try:
        if args.command == "export":
            md, csv_path, count = export_all(store, args.output)
            print(f"已导出 {count} 个词：\n  {md}\n  {csv_path}")
        elif args.command == "due":
            rows = store.due(limit=args.limit)
            if not rows:
                print("当前没有到期单词。")
            for row in rows:
                zh = "；".join(_list(row, "meanings_zh_cn"))
                print(f"{row['lemma']:<20} {zh}")
        elif args.command == "review":
            rating = RATING_ALIASES.get(args.rating.lower())
            if rating is None:
                raise SystemExit("评分只能是：1不认识 / 2困难 / 3认识 / 4简单")
            row = store.review(args.word, rating)
            print(f"已记录 {row['lemma']}，下次复习：{row['next_review_at']}")
    finally:
        store.close()


if __name__ == "__main__":
    main()
