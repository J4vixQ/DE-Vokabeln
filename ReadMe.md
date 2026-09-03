# DE-Vokabeln

自用

👉 [DE-Vokabeln-Demo](https://j4vixq.github.io/DE-Vokabeln/)



## Stack

- Node.js
- Vue 3
- Vite
- JavaScript
- HTML
- CSS
- GitHub Pages



## Features

- Categorized vocabulary decks:
  - Nomen – Objekte / Personen
  - Verben – Grundformen / Redewendungen
  - Adjektive – Allgemein / Steigerung
- Random card display
- Automatic dark mode
- Responsive layout for mobile and desktop
- Colored underline for grammatical gender
- example sentences from hand-picked notes, with OpenSubtitles v.2024 as fallback
- Chinese translation of example sentences via a local LLM (Ollama)



### Initialize

```bash
npm install
```

### Test

```bash
npm run dev
```

### Build and Deploy

Every push to `main` is built and published to GitHub Pages automatically by
`.github/workflows/deploy.yml` (one-time setup: repo **Settings → Pages → Source → GitHub Actions**).

Manual deploy (fallback, publishes to the `gh-pages` branch):
```bash
npm run build
npm run deploy
```

### Update vocabulary data

All data lives in `public/data/*.json` and is (re)generated from my notes by one script.
Every level's notes folder has the same layout (same `.xlsx` names, sheet names and
`sentences.docx` names), so when a new level is added the only edit is `NOTES_DIRS`
at the top of `build.py`, e.g. `NOTES_DIRS = ["_A2", "_B1"]`. Then:

```bash
pip install pandas openpyxl requests   # one-time
ollama serve                           # for the translation step

python build.py                        # full pipeline
python build.py --only sentences       # or a single step: excel / sentences / examples / translation
python build.py --skip translation
python build.py --sentence-mode new_example  # re-search a fresh example for every word; keep the old one if none found
python build.py --sentence-mode upgrade      # replace existing examples with the sentences.docx versions only
```

The example-filling mode also has a default in `build.py` (`SENTENCE_MODE`); the flag just overrides it for one run. Any entry whose 例句 changes gets its 翻译 cleared, so run the translation step afterwards.

Pipeline steps (`step1/2/3_*.py` are libraries called by `build.py`):

1. **excel** – `<notes>/*.xlsx` → `public/data/*.json` for every folder in `NOTES_DIRS` (adds new entries only, never overwrites existing 例句/翻译)
2. **sentences** – reads `sentences.docx` (+ `sentences from the internet.docx`) from every `NOTES_DIRS` folder and **merges** the lines into `public/data/sentences.txt` (dedup, existing lines kept — so a future `_B1/sentences.docx` just adds on top)
3. **examples** – fills empty `例句`, preferring `sentences.txt`, falling back to `resource/OpenSubtitles`
4. **translation** – fills empty `翻译` by sending each `例句` to a local Ollama model (`OLLAMA_MODEL` in `build.py`)

```bash
ollama list
ollama pull qwen2.5:14b
```


