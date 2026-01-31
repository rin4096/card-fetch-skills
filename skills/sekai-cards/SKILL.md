---
name: sekai-cards
description: Fetch the latest card data and image URLs for Project Sekai characters (especially Ena and Mizuki). Use when requested to get card info or images from sekai.best.
---

# Sekai Cards

Fetch latest card information and images from the Sekai Viewer data sources.

## Usage

Use the provided script to fetch the latest card for a character.

### Fetch Latest Card

Run the script with the character name (ena or mizuki) or a character ID.

```bash
python3 scripts/get_card.py <character_name_or_id>
```

Or fetch a card directly by its title (prefix):

```bash
python3 scripts/get_card.py --prefix "夕暮れの窓辺"
```

The script will output (fixed format, Chinese labels):
- 标题
- 角色(日文)
- 团队 (JP)
- 属性
- 稀有度 (星数)
- 详情 (hxxps 脱链接)
- 普通图 URL
- 觉醒图 URL（非生日卡）

### Important Note on URLs
The script uses the `sekai-jp-assets` path which is the most reliable for latest JP server cards.
If a link fails, check if the asset bundle name exists in the `sekai-master-db-diff` repository.

### Output Standard
Always output the raw text output from the script (Title, Character, Unit, Attribute, Rarity, Detail, URLs) before sending the image. This SOP is mandatory for Ena.
