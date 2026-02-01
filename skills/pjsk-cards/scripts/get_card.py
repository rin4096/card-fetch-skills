#!/usr/bin/env python3
import sys
import json
import subprocess
import time
import os

# Static Character Data (ID -> Name, Unit) to avoid fetching gameCharacters.json
# Unit codes: light_sound (L/n), idol (MMJ), street (VBS), theme_park (WxS), school_refusal (25ji)
CHARACTER_DATA = {
    1: {"name": "星乃 一歌", "unit": "light_sound"},
    2: {"name": "天馬 咲希", "unit": "light_sound"},
    3: {"name": "望月 穂波", "unit": "light_sound"},
    4: {"name": "日野森 志歩", "unit": "light_sound"},
    5: {"name": "花里 みのり", "unit": "idol"},
    6: {"name": "桐谷 遥", "unit": "idol"},
    7: {"name": "桃井 愛莉", "unit": "idol"},
    8: {"name": "日野森 雫", "unit": "idol"},
    9: {"name": "小豆沢 こはね", "unit": "street"},
    10: {"name": "白石 杏", "unit": "street"},
    11: {"name": "東雲 彰人", "unit": "street"},
    12: {"name": "青柳 冬弥", "unit": "street"},
    13: {"name": "天馬 司", "unit": "theme_park"},
    14: {"name": "鳳 えむ", "unit": "theme_park"},
    15: {"name": "草薙 寧々", "unit": "theme_park"},
    16: {"name": "神代 類", "unit": "theme_park"},
    17: {"name": "宵崎 奏", "unit": "school_refusal"},
    18: {"name": "朝比奈 まふゆ", "unit": "school_refusal"},
    19: {"name": "東雲 絵名", "unit": "school_refusal"},
    20: {"name": "暁山 瑞希", "unit": "school_refusal"},
    21: {"name": "初音 ミク", "unit": "piapro"},
    22: {"name": "鏡音 リン", "unit": "piapro"},
    23: {"name": "鏡音 レン", "unit": "piapro"},
    24: {"name": "巡音 ルカ", "unit": "piapro"},
    25: {"name": "MEIKO", "unit": "piapro"},
    26: {"name": "KAITO", "unit": "piapro"},
}

def get_cards_json():
    """Fetch cards.json with local caching (1 hour)"""
    cache_file = "/tmp/sekai_cards_cache.json"
    url = "https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/main/cards.json"
    
    # Check cache
    if os.path.exists(cache_file):
        mtime = os.path.getmtime(cache_file)
        if time.time() - mtime < 3600:  # 1 hour cache
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass # Fallback to fetch if cache invalid

    # Fetch new
    try:
        cmd = f"curl -s {url}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        
        # Save cache
        with open(cache_file, 'w') as f:
            json.dump(data, f)
        
        return data
    except Exception:
        return None

def get_latest_card(character_id, cards_data):
    try:
        # Filter in Python instead of jq for speed if data is loaded
        filtered = [c for c in cards_data if c.get('characterId') == character_id]
        if not filtered:
            return None, "No card data found for this ID."
        
        # Sort by releaseAt (timestamp)
        # releaseAt might be int or str, usually reliable
        filtered.sort(key=lambda x: x.get('releaseAt', 0))
        return filtered[-1], None
    except Exception as e:
        return None, str(e)

def get_card_by_prefix(prefix, cards_data):
    try:
        # Simple substring search or exact match
        for c in cards_data:
            if c.get('prefix') == prefix:
                return c, None
        return None, "No card data found for this prefix."
    except Exception as e:
        return None, str(e)

def rarity_to_stars(rarity):
    mapping = {
        "rarity_1": "★",
        "rarity_2": "★★",
        "rarity_3": "★★★",
        "rarity_4": "★★★★",
        "rarity_birthday": "BD",
        "rarity_5": "★★★★★",
    }
    return mapping.get(rarity, rarity)


def unit_to_jp(unit_code):
    mapping = {
        "light_sound": "Leo/need",
        "idol": "MORE MORE JUMP!",
        "street": "Vivid BAD SQUAD",
        "theme_park": "ワンダーランズ×ショウタイム",
        "school_refusal": "25時、ナイトコードで。",
        "piapro": "VIRTUAL SINGER",
        "none": "—",
    }
    return mapping.get(unit_code, unit_code)

def main():
    if len(sys.argv) < 2:
        print("Usage: get_card.py <character_id_or_name> | --prefix <card_prefix>")
        sys.exit(1)

    # 1. Load Data (Cached)
    cards_data = get_cards_json()
    if not cards_data:
        print("Error: Failed to fetch cards data.")
        sys.exit(1)

    card = None
    error = None

    if sys.argv[1] == "--prefix":
        if len(sys.argv) < 3:
            print("Usage: get_card.py --prefix <card_prefix>")
            sys.exit(1)
        prefix_input = sys.argv[2]
        card, error = get_card_by_prefix(prefix_input, cards_data)
    else:
        char_input = sys.argv[1].lower()
        
        # Name Mapping
        char_map = {
            "ichika": 1, "saki": 2, "honami": 3, "shiho": 4,
            "minori": 5, "haruka": 6, "airi": 7, "shizuku": 8,
            "kohane": 9, "an": 10, "akito": 11, "toya": 12,
            "tsukasa": 13, "emu": 14, "nene": 15, "rui": 16,
            "kanade": 17, "mafuyu": 18, "ena": 19, "mizuki": 20,
            "miku": 21, "rin": 22, "len": 23, "luka": 24, "meiko": 25, "kaito": 26
        }

        char_id = char_map.get(char_input)
        if not char_id:
            try:
                char_id = int(char_input)
            except ValueError:
                print(f"Unknown character: {sys.argv[1]}")
                sys.exit(1)

        card, error = get_latest_card(char_id, cards_data)

    if error:
        print(f"Error: {error}")
        sys.exit(1)
    
    if not card:
        print("No card found.")
        sys.exit(1)

    asset = card.get("assetbundleName")
    prefix = card.get("prefix")
    rarity = card.get("cardRarityType")
    card_id = card.get("id")
    char_id_from_card = card.get("characterId")
    
    # Use Static Data
    char_info = CHARACTER_DATA.get(char_id_from_card, {})
    jp_name = char_info.get("name")
    unit = char_info.get("unit")
    
    unit_jp = unit_to_jp(unit) if unit else None
    stars = rarity_to_stars(rarity)
    
    base_url = "https://storage.sekai.best/sekai-jp-assets/character/member"
    detail_url = f"hxxps://sekai.best/card/{card_id}" if card_id else ""

    # Output
    print(f"标题: {prefix}")
    if jp_name:
        print(f"角色(日文): {jp_name}")
    if unit_jp:
        print(f"团队: {unit_jp}")
    print(f"属性: {card.get('attr')}")
    print(f"稀有度: {stars}")
    if detail_url:
        print(f"详情: {detail_url}")
    print(f"普通图: {base_url}/{asset}/card_normal.png")
    if rarity != "rarity_birthday":
        print(f"觉醒图: {base_url}/{asset}/card_after_training.png")

if __name__ == "__main__":
    main()
