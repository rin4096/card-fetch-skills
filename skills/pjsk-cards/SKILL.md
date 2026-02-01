---
name: pjsk-cards
description: "Fetch character card data, rarity, attributes, and high-quality image URLs for Project Sekai: Colorful Stage! (PJSK). Supports searching by character name, card ID, or title prefix."
---

# PJSK Cards Skill 🎀

A specialized OpenClaw skill for retrieving card data and assets from Project Sekai. 

## 🌟 Features
- **Search by Name**: Find cards for any character (e.g., Ena, Mizuki, Kanade).
- **Search by ID**: Get specific card details using the Bestdori/Sekai.best ID.
- **Search by Title**: Find cards by their prefix/title (e.g., "夕暮れの窓辺").
- **Automatic Formatting**: Outputs standardized Chinese labels for attributes, rarity, and unit names.
- **Image URLs**: Provides direct links to normal and trained (after-training) card art.

## 🛠 Usage

### Command Line
Run the Python script directly from the skill folder:

```bash
# Search by character name
python3 scripts/get_card.py "Ena"

# Search by card title (prefix)
python3 scripts/get_card.py --prefix "夕暮れの窓辺"
```

## 📋 Standard Operating Procedure (SOP)
To ensure the best experience for Ena, follow these steps:
1. **Details First**: Always output the full text information returned by the script (Title, Character, Unit, Attribute, Rarity, URLs).
2. **Standard Labels**: Ensure all labels are in Chinese (标题, 角色, 属性, etc.).
3. **Image Delivery**: Send the card images *after* the text details.

---
*Created with love by Mizuki for Ena.*
