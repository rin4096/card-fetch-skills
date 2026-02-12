---
name: pjsk-cards
description: "Fetch character card data, rarity, attributes, and high-quality image URLs for Project Sekai: Colorful Stage! (PJSK). Supports searching by character name, card ID, or title prefix, with filtering by rarity and attribute."
---

# PJSK Cards Skill 🎀

A specialized OpenClaw skill for retrieving card data and assets from Project Sekai.

## 🌟 Features
- **Search by Name**: Find cards for any character (e.g., Ena, Mizuki, 絵名, 19).
- **Search by Card ID**: Get specific card details using the card ID (`--card-id`).
- **Search by Title**: Find cards by prefix/title substring (`--prefix`).
- **Filter by Unit**: Filter cards by team/unit (`--unit`: leo, mmj, vbs, ws, n25, vs).
- **Filter by Rarity**: Show only ★1–★5 or Birthday cards (`--rarity`).
- **Filter by Attribute**: cute, cool, pure, happy, mysterious (`--attr`).
- **Multi-card Output**: Return latest N cards (`--limit N`) or all (`--all`).
- **JSON Mode**: Machine-readable JSON output (`--json`), errors also in JSON format.
- **Cache Control**: Force fresh data fetch with `--no-cache`.
- **Automatic Formatting**: Chinese labels, JP unit names, star display, release dates.
- **Image URLs**: Direct links to normal and trained (after-training) card art.

## 🛠 Usage

```bash
# Latest card for a character
python3 scripts/get_card.py ena

# All ★4 cards for a character
python3 scripts/get_card.py ena --rarity 4 --all

# Latest 5 cards (any rarity)
python3 scripts/get_card.py ena --limit 5

# Filter by attribute
python3 scripts/get_card.py ena --attr cool --rarity 4 --all

# Birthday cards
python3 scripts/get_card.py ena --rarity bd --all

# Search by card title (substring match)
python3 scripts/get_card.py --prefix "夕暮れ"

# Look up specific card by ID
python3 scripts/get_card.py --card-id 1316

# JSON output for programmatic use
python3 scripts/get_card.py ena --rarity 4 -n 3 --json

# Filter by unit (team)
python3 scripts/get_card.py ena --unit n25 --all
python3 scripts/get_card.py --unit mmj --rarity 4 --all

# Force fresh data fetch (ignore cache)
python3 scripts/get_card.py ena --no-cache
```

## 📋 Standard Operating Procedure (SOP)
1. **Details First**: Always output the full text information (标题, 角色, 团队, 属性, 稀有度, 技能, 实装日, URLs).
2. **Standard Labels**: All labels in Chinese.
3. **Image Delivery**: Send card images *after* text details.
4. **Multiple Results**: When showing multiple cards, include index numbers for clarity.
5. **JSON Error Handling**: In `--json` mode, all errors are returned as JSON:
   ```json
   {"error": "錯誤訊息", "results": []}
   ```

## 📝 補充說明

### Cache 機制
- 資料快取路徑：`/tmp/sekai_cards_cache.json`
- 快取 TTL：1 小時
- 使用 `--no-cache` 可強制重新從 GitHub 拉取資料

### 其他別名
- `--rarity birthday` 與 `bd` 效果相同
- 角色別名支援：繪名（繁體）、mfy、ick、khn、mnr 等

### Trained Image 注意事項
- `trained_image`（覺醒圖）僅適用於 ★3 以上卡片
- ★1、★2 及 Birthday 卡片沒有覺醒圖

### 注意事項
- `--card-id` 與 `--rarity` / `--attr` 同時使用時會顯示警告（card-id 優先）
- `--limit` 只接受正整數（0 或負數會報錯）

## 🔧 CLI Reference

| Flag | Short | Description |
|------|-------|-------------|
| `character` | — | Positional: character name (romaji/JP/ID) |
| `--prefix` | `-p` | Search by card title (substring) |
| `--card-id` | `-c` | Look up exact card ID |
| `--unit` | `-u` | Filter by unit: leo, mmj, vbs, ws, n25, vs |
| `--rarity` | `-r` | Filter: 1, 2, 3, 4, 5, bd/birthday |
| `--attr` | `-a` | Filter: cute, cool, pure, happy, mysterious |
| `--limit` | `-n` | Max results, must be positive integer (default: 1) |
| `--all` | — | Return all matches |
| `--json` | `-j` | JSON output |
| `--no-cache` | — | Force fresh data fetch from GitHub |

---
*Created with love by Mizuki for Ena.*
