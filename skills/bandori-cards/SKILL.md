---
name: bandori-cards
description: Fetch character card data, skill info (Chinese), and image URLs for BanG Dream! (Bandori) using the Bestdori API.
---

# Bandori Cards Skill (Bestdori version)

Fetch character card data, skill info (Chinese), and image URLs for BanG Dream! (Bandori) using the Bestdori API.

## Usage

Use the python script to fetch cards. You can filter by character name, rarity, and server.

```bash
python3 ./scripts/bandori_bestdori.py --character "Anon" --rarity 5
```

### Options
- `--character`: Partial match of character name (e.g., "Anon", "Tomori", "Sayo").
- `--rarity`: Card rarity (1-5).
- `--server`: Asset server (default: `jp`). Options: `jp`, `en`, `cn`, `tw`, `kr`.
- `--skill-level`: Skill level (1-5). Replaces `{0}` in skill descriptions with the proper seconds.

### Skill Output
Each card now includes:
- `skill.descriptionByLevel`: Chinese description expanded for levels 1-5
- `skill.simpleDescriptionByLevel`: Chinese simple description expanded for levels 1-5

### Character ID Cheat Sheet
- **Poppin'Party**: 1-5
- **Afterglow**: 6-10
- **Hello, Happy World!**: 11-15
- **Pastel*Palettes**: 16-20
- **Roselia**: 21-25
- **Morfonica**: 26-30
- **RAISE A SUILEN**: 31-35
- **MyGO!!!!!**: 36-40 (Tomori: 36, Anon: 37, Rana: 38, Soyo: 39, Taki: 40)

## API Reference
- Characters: `https://bestdori.com/api/characters/all.2.json`
- Cards: `https://bestdori.com/api/cards/all.5.json`
- Assets: `https://bestdori.com/assets/`
