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

The script will output:
- Card prefix (name)
- Rarity
- Image URL for Normal (Untrained)
- Image URL for After Training (Trained)

### Important Note on URLs
The script uses the `sekai-jp-assets` path which is the most reliable for latest JP server cards.
If a link fails, check if the asset bundle name exists in the `sekai-master-db-diff` repository.
