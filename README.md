# PJSK Cards Skill for OpenClaw 🎀

A specialized [OpenClaw](https://github.com/openclaw/openclaw) skill for fetching **Project Sekai: Colorful Stage!** character card data, attributes, and high-quality card art.

## ✨ Features

- **Character Search** — by romaji (`ena`), Japanese (`絵名`), traditional Chinese (`繪名`), or ID (`19`)
- **Card ID Lookup** — exact card by `--card-id`
- **Title Search** — substring match via `--prefix`
- **Filter by Unit** — `--unit` (leo / mmj / vbs / ws / n25 / vs)
- **Filter by Rarity** — `--rarity` (1–5, bd/birthday)
- **Filter by Attribute** — `--attr` (cute, cool, pure, happy, mysterious)
- **Multi-card Output** — `--limit N` or `--all`
- **JSON Mode** — `--json` for programmatic use (errors also in JSON)
- **Cache Control** — `--no-cache` to force fresh fetch from GitHub
- **Chinese Labels** — all output in Traditional Chinese with JP unit names
- **Card Art URLs** — direct links to normal and trained (覺醒) images

## 🚀 Installation

Tell your OpenClaw agent:

> Install the pjsk-cards skill from https://github.com/rin4096/pjsk-cards-skill

Or manually copy `skills/pjsk-cards/` into your OpenClaw skills directory.

## 📦 Requirements

- Python 3.10+
- No external dependencies (uses only stdlib)

## 🛠 Usage

```bash
# Latest card for a character
python3 scripts/get_card.py ena

# All ★4 cards
python3 scripts/get_card.py ena --rarity 4 --all

# Latest 5 cards (any rarity)
python3 scripts/get_card.py ena --limit 5

# Filter by attribute
python3 scripts/get_card.py ena --attr cool --rarity 4 --all

# Birthday cards
python3 scripts/get_card.py ena --rarity bd --all

# Search by card title
python3 scripts/get_card.py --prefix "夕暮れ"

# Look up by card ID
python3 scripts/get_card.py --card-id 1316

# JSON output
python3 scripts/get_card.py ena --rarity 4 -n 3 --json

# Filter by unit (team)
python3 scripts/get_card.py --unit n25 --rarity 4 --all

# Force fresh data fetch
python3 scripts/get_card.py ena --no-cache
```

## 📋 CLI Reference

| Flag | Short | Description |
|------|-------|-------------|
| `character` | — | Positional: character name (romaji/JP/ID) |
| `--prefix` | `-p` | Search by card title (substring match) |
| `--card-id` | `-c` | Look up exact card ID |
| `--unit` | `-u` | Filter by unit: `leo`, `mmj`, `vbs`, `ws`, `n25`, `vs` |
| `--rarity` | `-r` | Filter by rarity: `1`, `2`, `3`, `4`, `5`, `bd`/`birthday` |
| `--attr` | `-a` | Filter by attribute: `cute`, `cool`, `pure`, `happy`, `mysterious` |
| `--limit` | `-n` | Max results (positive integer, default: 1) |
| `--all` | — | Return all matches (overrides `--limit`) |
| `--json` | `-j` | JSON output |
| `--no-cache` | — | Force fresh fetch, ignore local cache |

## 📝 Notes

- **Cache**: Data is cached at `/tmp/sekai_cards_cache.json` with a 1-hour TTL
- **Trained images**: Only available for ★3 and above (★1, ★2, Birthday cards have no trained art)
- **`--card-id` priority**: When used with `--rarity`/`--attr`, a warning is shown and card-id takes priority
- **Character aliases**: Supports romaji, Japanese, traditional Chinese, and common abbreviations (`mfy`, `ick`, `khn`, `mnr`)
- **Data source**: [Sekai-World/sekai-master-db-diff](https://github.com/Sekai-World/sekai-master-db-diff)

## 📂 Structure

```
skills/pjsk-cards/
├── SKILL.md              # Skill definition for OpenClaw
└── scripts/
    └── get_card.py       # Card query engine
```

## 📄 License

MIT

---

*Created with 💕 by Mizuki & Ena — 25時、ナイトコードで。*
