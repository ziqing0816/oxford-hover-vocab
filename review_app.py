#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""本地生词卡片复习界面。"""

import json
import os
import tkinter as tk
from tkinter import messagebox

from vocabulary_store import VocabularyStore


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VOCAB_PATH = os.path.join(BASE_DIR, "vocabulary.db")


def _items(row, field):
    try:
        value = json.loads(row.get(field, "[]"))
        return tuple(value) if isinstance(value, list) else ()
    except (TypeError, ValueError, json.JSONDecodeError):
        return ()


def review_content(row):
    """把数据库记录转成适合卡片显示的纯文本字段。"""
    meanings = _items(row, "meanings_zh_cn")
    definitions = _items(row, "definitions_en")
    synonyms = _items(row, "synonyms")
    examples = _items(row, "examples")
    return {
        "word": row.get("word") or row.get("lemma") or "",
        "lemma": row.get("lemma", ""),
        "phonetic": f"/{row['phonetic']}/" if row.get("phonetic") else "",
        "part_of_speech": row.get("part_of_speech", ""),
        "meaning": "\n".join(meanings) or "暂无简体释义",
        "definition": "\n".join(f"• {item}" for item in definitions),
        "synonyms": ", ".join(synonyms),
        "examples": "\n".join(examples),
        "context": row.get("context_sentence", ""),
    }


class ReviewApp:
    BG = "#171a20"
    CARD = "#20242c"
    FG = "#f2f4f7"
    MUTED = "#9aa3b2"
    GREEN = "#7fd6a2"
    BLUE = "#82b7ff"

    def __init__(self, db_path=VOCAB_PATH):
        self.store = VocabularyStore(db_path)
        self._closed = False
        self.rows = self.store.due(limit=200)
        self.index = 0

        self.root = tk.Tk()
        self.root.title("Oxford Hover Vocab · 生词复习")
        self.root.geometry("760x620")
        self.root.minsize(620, 500)
        self.root.configure(bg=self.BG)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.progress = tk.Label(
            self.root, bg=self.BG, fg=self.MUTED,
            font=("Microsoft YaHei UI", 11), anchor="w")
        self.progress.pack(fill="x", padx=28, pady=(22, 10))

        self.card = tk.Frame(self.root, bg=self.CARD)
        self.card.pack(fill="both", expand=True, padx=28, pady=(0, 18))

        self.word = tk.Label(
            self.card, bg=self.CARD, fg=self.FG,
            font=("Segoe UI Semibold", 30), anchor="w")
        self.word.pack(fill="x", padx=28, pady=(26, 0))
        self.meta = tk.Label(
            self.card, bg=self.CARD, fg=self.MUTED,
            font=("Segoe UI", 13), anchor="w")
        self.meta.pack(fill="x", padx=28, pady=(4, 18))

        self.answer = tk.Frame(self.card, bg=self.CARD)
        self.meaning = self._answer_label(self.GREEN, 17)
        self.definition = self._answer_label(self.FG, 12)
        self.synonyms = self._answer_label(self.BLUE, 11)
        self.examples = self._answer_label(self.MUTED, 11, italic=True)
        self.context = self._answer_label(self.MUTED, 11)

        self.reveal = tk.Button(
            self.root, text="显示答案", command=self.show_answer,
            bg="#39745a", fg="white", activebackground="#4b8c6e",
            activeforeground="white", relief="flat", bd=0,
            font=("Microsoft YaHei UI", 13, "bold"), padx=24, pady=10)
        self.reveal.pack(pady=(0, 22))

        self.ratings = tk.Frame(self.root, bg=self.BG)
        for text, rating, color in (
                ("1  不认识", "again", "#9d4b4b"),
                ("2  困难", "hard", "#8b663b"),
                ("3  认识", "good", "#39745a"),
                ("4  简单", "easy", "#3f6596")):
            tk.Button(
                self.ratings, text=text,
                command=lambda value=rating: self.rate(value),
                bg=color, fg="white", activeforeground="white",
                relief="flat", bd=0, font=("Microsoft YaHei UI", 11),
                padx=16, pady=9).pack(side="left", padx=5)

        self.root.bind("<space>", lambda _event: self.show_answer())
        for key, rating in (("1", "again"), ("2", "hard"),
                            ("3", "good"), ("4", "easy")):
            self.root.bind(key, lambda _event, value=rating: self.rate(value))
        self.load_card()

    def _answer_label(self, color, size, italic=False):
        font = ("Segoe UI", size, "italic") if italic else ("Microsoft YaHei UI", size)
        label = tk.Label(
            self.answer, bg=self.CARD, fg=color, justify="left", anchor="w",
            wraplength=650, font=font)
        label.pack(fill="x", padx=28, pady=(0, 10))
        return label

    def load_card(self):
        self.answer.pack_forget()
        self.ratings.pack_forget()
        if self.index >= len(self.rows):
            self.progress.config(text="今日复习完成")
            self.word.config(text="做得很好！", font=("Microsoft YaHei UI", 28, "bold"))
            self.meta.config(text="当前没有更多到期单词。")
            self.reveal.pack_forget()
            return
        item = review_content(self.rows[self.index])
        self.progress.config(text=f"今日待复习：{self.index + 1} / {len(self.rows)}")
        self.word.config(text=item["word"], font=("Segoe UI Semibold", 30))
        meta = "  ·  ".join(x for x in (item["phonetic"], item["part_of_speech"])
                            if x)
        self.meta.config(text=meta)
        self.reveal.pack(pady=(0, 22))

    def show_answer(self):
        if self.index >= len(self.rows) or self.answer.winfo_ismapped():
            return
        item = review_content(self.rows[self.index])
        self.meaning.config(text=item["meaning"])
        self.definition.config(
            text=("英英释义\n" + item["definition"]) if item["definition"] else "")
        self.synonyms.config(
            text=("同义词：" + item["synonyms"]) if item["synonyms"] else "")
        self.examples.config(
            text=("例句：" + item["examples"]) if item["examples"] else "")
        self.context.config(
            text=("我的原句：" + item["context"]) if item["context"] else "")
        self.answer.pack(fill="both", expand=True)
        self.reveal.pack_forget()
        self.ratings.pack(pady=(0, 22))

    def rate(self, rating):
        if self.index >= len(self.rows) or not self.answer.winfo_ismapped():
            return
        self.store.review(self.rows[self.index]["lemma"], rating)
        self.index += 1
        self.load_card()

    def close(self):
        if not self._closed:
            self.store.close()
            self._closed = True
        self.root.destroy()

    def run(self):
        try:
            self.root.mainloop()
        finally:
            if not self._closed:
                self.store.close()
                self._closed = True


def main():
    app = ReviewApp()
    if not app.rows:
        messagebox.showinfo("生词复习", "当前没有到期单词。\n先使用划词工具积累一些生词吧。")
    app.run()


if __name__ == "__main__":
    main()
