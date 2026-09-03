---
name: oxford-hover-vocab
description: Install, start, configure, export, review, or troubleshoot the Oxford Hover Vocab Windows screen-hover dictionary and local vocabulary system. Use when the user refers to Oxford Hover Vocab, global screen word lookup, its Oxford API setup, saved vocabulary, or spaced-review workflow; do not use for translating text pasted directly into chat.
---

# Oxford Hover Vocab

Help the user operate and maintain the native Windows application in this repository. The Skill does not watch the mouse itself; `hover_translate.py` is the resident screen-hover program.

## Locate the project

Use a path supplied by the user. Otherwise, inspect the current workspace for `hover_translate.py`, `review_app.py`, and `README.md`. If several copies exist, ask which one to use before modifying or launching anything.

Run project commands with `.venv\Scripts\python.exe`. If `.venv` or `dict.db` is missing, guide the user to run `setup.bat`; do not silently install software into global Python.

## Route the request

- Install or repair installation: run `setup.bat`, then verify the project-local environment and `dict.db` exist.
- Start lookup: launch `hover_translate.py` as a hidden background process so the conversation is not blocked.
- Stop lookup: prefer telling the user to press Esc twice or `Ctrl+Alt+Q`. If process termination is explicitly requested, identify the exact process by its command line before stopping it; never stop every Python process.
- Review vocabulary: launch `review_app.py`, or tell the user to double-click `review-vocab.bat`.
- Export vocabulary: run `vocab_cli.py export`, or tell the user to double-click `export-vocab.bat`.
- Change behavior: edit `config.json`, not application constants, unless the user asks for a code change.
- Diagnose: start with targeted, read-only checks; use the unit tests for data logic and `selftest.py` for Windows OCR, speech, popup, hotkey, and single-instance behavior.

## User controls

- Hold `Ctrl`, move the pointer over an English word, and dwell for about 0.4 seconds: lookup.
- Press Esc twice: stop.
- `Ctrl+Alt+H`: pause or resume.
- `Ctrl+Alt+Q`: stop.
- Review window: Space reveals the answer; `1` again, `2` hard, `3` good, `4` easy.

## Oxford and privacy invariants

Oxford is optional. Without credentials, on network failure, or when the quota is exhausted, preserve the local ECDICT result.

- Use only the official Oxford Dictionaries API. Do not scrape Oxford webpages or bypass security checks.
- Send only the normalized English lookup word. Never send screenshots, window titles, the surrounding sentence, or vocabulary history.
- Read credentials only from `OXFORD_APP_ID` and `OXFORD_APP_KEY` user environment variables.
- Never ask the user to paste credentials into chat, print them, log them, store them in project files, or commit them.
- Sandbox English queries are limited to A-initial words. Preserve the guard that skips other letters and the in-memory cache that prevents repeated calls.
- Keep `.env`, `vocabulary.db*`, and `exports/` ignored by Git.
- Warn that `debug: true` can write recognized screen text to `hover_translate.log`; recommend keeping it off around personal or confidential material.

## Vocabulary behavior

`vocabulary.db` is local SQLite data. Entries deduplicate by normalized lemma. A real hover increments `lookup_count`; later Oxford enrichment must not increment it again. The surrounding sentence stays local.

Exports belong in `exports/`:

- `vocabulary-review.md` for reading and printing;
- `vocabulary.csv` with UTF-8 BOM for Excel.

Preserve CSV formula-injection protection for values beginning with `=`, `+`, `-`, or `@`.

## Configuration

Load the existing `config.json` before editing and change only requested fields. Common settings:

- `dwell_ms`: increase to reduce accidental activation.
- `modifier`: `ctrl`, `alt`, `shift`, or `none`; warn that `none` triggers often.
- `use_oxford`: enable or disable optional online enrichment.
- `auto_save_vocabulary`: enable or disable local capture.
- `save_context_sentence`: keep or omit the local reading sentence.
- `speak_english`, `speak_chinese`: speech controls.
- `max_senses`, `max_english_definitions`, `max_synonyms`, `max_examples`: popup limits.
- `debug`: diagnostic logging with the privacy warning above.

Restart the resident program after configuration changes.

## Verification

For ordinary data or provider changes, run:

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_installation.py test_oxford_provider.py test_provider_chain.py test_vocabulary_store.py test_vocab_cli.py test_review_app.py
```

For changes affecting Windows capture, OCR, speech, UI, hotkeys, or startup, also run:

```powershell
.\.venv\Scripts\python.exe selftest.py
```

The full self-test opens temporary UI and reads a test screen region, so explain that behavior before running it. Mock Oxford in routine tests to avoid spending API quota. Run a live API call only when the user explicitly agrees to consume a call.

## Source and release discipline

Preserve upstream MIT attribution and the modification notice. Do not commit downloaded dictionary data, user vocabulary, exports, logs, credentials, or local configuration. Keep ECDICT pinned to a reviewed commit with SHA-256 verification and keep dependency versions pinned. Before a release, confirm tests pass, documentation matches actual network/storage behavior, and the working tree contains no personal data.
