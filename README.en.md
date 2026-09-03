# Oxford Hover Vocab

A Windows screen-hover vocabulary assistant with optional Oxford Dictionaries API enrichment, Simplified Chinese support, local vocabulary capture, and spaced review.

This project is forked from [AFA7777/hover-translate](https://github.com/AFA7777/hover-translate). It retains the original Windows OCR, cursor positioning, speech, and offline ECDICT fallback, while adding:

- Oxford English definitions, pronunciations, synonyms, antonyms, and examples;
- Simplified Chinese as the default Chinese experience;
- automatic local vocabulary capture and lemma-based deduplication;
- Markdown and Excel-compatible CSV exports;
- a local spaced-review card interface;
- background online enrichment with automatic offline fallback.

## Quick start

1. Install Python 3.8+ on Windows 10/11.
2. Download and extract this repository.
3. Double-click `setup.bat`.
4. Start **Oxford Hover Vocab** from the desktop.
5. Hold `Ctrl`, move the pointer over an English word, and dwell for about 0.4 seconds.

The installer creates an isolated `.venv`, installs pinned dependencies, builds the local dictionary, and creates desktop shortcuts.

## Privacy

- Screen pixels are processed by Windows OCR locally and are not saved.
- If Oxford is enabled, only the normalized English word is sent to the official Oxford API.
- The surrounding sentence, vocabulary database, and review history remain local.
- Oxford credentials are read from `OXFORD_APP_ID` and `OXFORD_APP_KEY`; they are not stored in the repository or vocabulary database.
- The app does not record keystroke content, continuously record the screen, or configure autostart.

Oxford access is optional. Without credentials or when offline, the app continues to use the local ECDICT database.

## Vocabulary and review

- Double-click `review-vocab.bat` for local review cards.
- Double-click `export-vocab.bat` to generate `vocabulary-review.md` and `vocabulary.csv`.
- Vocabulary data is stored locally in `vocabulary.db`, which is ignored by Git.

## Documentation

The primary documentation is the [Simplified Chinese README](README.md). See also:

- [Architecture and privacy](docs/ARCHITECTURE.zh-CN.md)
- [Oxford API setup](docs/OXFORD_SETUP.zh-CN.md)
- [Third-party notices](NOTICE)

## License

Source code is MIT licensed and retains upstream attribution. This repository does not bundle or redistribute ECDICT or Oxford dictionary content.
