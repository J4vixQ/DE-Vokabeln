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

- One merged deck covering four groups, each drawn equally often:
  - Nomen – Objekte / Personen
  - Verben
  - Adjektive – Steigerung
  - Phrasen – Verben / Adverbien
- Two study modes from the home page: **Ansehen** (flip-only) or **Quiz** (multiple choice)
- **Sätze**: random hand-picked example sentences from my notes, with Chinese translation
- Weighted random cards — words you get wrong or haven't seen show up more often (familiarity level per card)
- Review page: the words you answered wrong — choose to look through them first (**Ansehen**) or answer them (**Quiz**); **Ausblenden** hides a word you don't need for good (undo for 5 s, restore on the Daten page)
- Stats page: green / red / grey stacked bars (correct / wrong / just-viewed) per day
- Automatic dark mode, responsive, colored underline for grammatical gender
- Example sentences from hand-picked notes, with OpenSubtitles v.2024 as fallback
- Chinese translation of example sentences via a local LLM (Ollama)

All progress (wrong list, familiarity, daily stats, hidden words) is stored in the browser's
localStorage — per device, nothing synced. The **Daten** page clears any of it
(per category or all at once). Internal details in [CLAUDE.md](CLAUDE.md).



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
From B1 on, every level's notes folder has the same layout: one `Vokabeln.xlsx` with the
words copied from DW plus my own 意思, and a `sentences.docx`. So when a new level is added
the only edit is `NOTES_DIRS` at the top of `build.py`, e.g. `NOTES_DIRS = ["_B1", "_B2"]`.

| sheet | columns | example cell |
|---|---|---|
| `Nomen` | `名词` `意思` | `Gegenteil, -e (n.)` |
| `Personen` | `男` `女` `意思` | `Lehrer, - (m.)` / `Lehrerin, -nen (f.)` |
| `Verben` | `原型` `现在` `过去` `完成` `意思` | `jemanden aus\|bilden` |
| `Adjektive` | `形容词` `意思` | `geduldig` |
| `Phrasen` | `词组` `意思` | `sich an etwas beteiligen` |

The build turns DW notation into full forms (das Gegenteil / die Gegenteile, bilden aus) and prints any cell it
can't parse, any same-name rows, and plurals it couldn't expand. The A1/A2 folders use the older three-Excel layout and are
still readable. Then:

```bash
pip install pandas openpyxl requests   # one-time
ollama serve                           # for the translation step

python build.py                        # full pipeline
python build.py --only sentences       # or a single step: sentences / excel / examples / translation
python build.py --skip translation
python build.py --sentence-mode new_example  # re-search a fresh example for every word; keep the old one if none found
python build.py --sentence-mode upgrade      # replace existing examples with the sentences.json versions only
```

The example-filling mode also has a default in `build.py` (`SENTENCE_MODE`); the flag just overrides it for one run.

Pipeline steps (`step1/2/3_*.py` are libraries called by `build.py`):

1. **sentences** – reads `sentences.docx` from every `NOTES_DIRS` folder and **merges** the lines into `public/data/sentences.json` (dedup, existing lines kept), then translates the new ones. Sentences already translated in a word json are copied instead of sent to Ollama.
2. **excel** – `<notes>/*.xlsx` → `public/data/*.json` for every folder in `NOTES_DIRS` (adds new entries only, never overwrites existing 例句/翻译)
3. **examples** – fills empty `例句`, preferring `sentences.json` (its 翻译 is copied along), falling back to `resource/OpenSubtitles` (翻译 left empty)
4. **translation** – fills the remaining empty `翻译`: copied from `sentences.json` when the sentence is there, otherwise sent to a local Ollama model (`OLLAMA_MODEL` in `build.py`)

`sentences from the internet.docx` is no longer read. To (re)build `sentences.json` from older notes, point the sentences step at specific files:

```bash
python build.py --only sentences --docx "_A2/sentences.docx" "_A2/sentences from the internet.docx"
```

```bash
ollama list
ollama pull qwen2.5:14b
```


