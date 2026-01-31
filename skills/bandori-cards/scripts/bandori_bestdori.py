#!/usr/bin/env python3
import sys
import requests
import json
import argparse
import os
import time

# Bestdori API Endpoints
CARDS_API = "https://bestdori.com/api/cards/all.5.json"
CHARACTERS_API = "https://bestdori.com/api/characters/all.2.json"
SKILLS_API = "https://bestdori.com/api/skills/all.5.json"
ASSETS_BASE_URL = "https://bestdori.com/assets"
CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")

def _cache_path(name: str):
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{name}.json")


def _load_cache(name: str, max_age_hours: float):
    try:
        path = _cache_path(name)
        if not os.path.exists(path):
            return None
        if max_age_hours is not None:
            age = time.time() - os.path.getmtime(path)
            if age > max_age_hours * 3600:
                return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _save_cache(name: str, data):
    try:
        path = _cache_path(name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass


def get_character_map(cache_hours=24):
    cached = _load_cache("characters", cache_hours)
    if cached:
        return cached
    try:
        resp = requests.get(CHARACTERS_API)
        data = resp.json()
        _save_cache("characters", data)
        return data
    except Exception as e:
        print(f"Error fetching characters: {e}", file=sys.stderr)
    return {}


def get_skills_map(cache_hours=24):
    cached = _load_cache("skills", cache_hours)
    if cached:
        return cached
    try:
        resp = requests.get(SKILLS_API)
        data = resp.json()
        _save_cache("skills", data)
        return data
    except Exception as e:
        print(f"Error fetching skills: {e}", file=sys.stderr)
    return {}


def get_cards_map(cache_hours=24):
    cached = _load_cache("cards", cache_hours)
    if cached:
        return cached
    try:
        resp = requests.get(CARDS_API)
        data = resp.json()
        _save_cache("cards", data)
        return data
    except Exception as e:
        print(f"Error fetching cards: {e}", file=sys.stderr)
    return {}


def apply_skill_level(desc: str, durations, level: int):
    if not desc or not durations or not level:
        return desc
    try:
        idx = max(1, min(level, len(durations))) - 1
        return desc.replace("{0}", str(durations[idx]))
    except Exception:
        return desc


def expand_skill_levels(desc: str, durations):
    if not desc or not durations:
        return None
    expanded = {}
    for i in range(1, len(durations) + 1):
        expanded[str(i)] = apply_skill_level(desc, durations, i)
    return expanded


def format_card_text(card_info):
    # Title: JP prefix + JP name (no CN)
    title = f"{card_info.get('prefixJp','')}｜{card_info.get('characterNameJp','')}".strip("｜")
    lines = [f"**{title}**"]
    lines.append(f"- 稀有度：{'★'*card_info.get('rarity',0)}")
    lines.append(f"- 属性：{card_info.get('attribute')}")
    lines.append(f"- 类型：{card_info.get('type')}")
    lines.append("\n**卡面：**")
    urls = card_info.get('urls', {})
    if urls.get('normal'):
        lines.append(f"- 普通：{urls['normal']}")
    if urls.get('trained'):
        lines.append(f"- 特训后：{urls['trained']}")
    skill = card_info.get('skill', {})
    lines.append("\n**技能（ID: {}）**".format(skill.get('id')))
    if skill.get('simpleDescription'):
        lines.append(f"- 简述：{skill.get('simpleDescription')}")
    if skill.get('descriptionByLevel'):
        lines.append("- 详细（按技能等级）：")
        for lv in sorted(skill['descriptionByLevel'].keys(), key=lambda x: int(x)):
            lines.append(f"  - Lv{lv}：{skill['descriptionByLevel'][lv]}")
    return "\n".join(lines)


def fetch_cards(character_query=None, rarity=None, server="jp", skill_level=None, cache_hours=24,
               limit=None, latest=False, fields=None, skill_id=None, skill_keyword=None, output_format="json"):
    try:
        char_map = get_character_map(cache_hours)
        skills_map = get_skills_map(cache_hours)
        target_char_id = None
        
        if character_query:
            # Smart matching: prioritize exact match in English or Japanese names
            # names is a list [JP, EN, TW, CN, KR]
            candidates = []
            for cid, info in char_map.items():
                names = info.get("characterName", [])
                # Check for exact matches first
                if any(n and character_query.lower() == n.lower() for n in names):
                    target_char_id = int(cid)
                    candidates = [] # Clear any partial matches
                    break
                # Check for partial matches (as fallback)
                # But for names like "Anon", we want to avoid "Kanon"
                # So we check word boundaries if possible, or just be more strict
                if any(n and character_query.lower() in n.lower().split() for n in names):
                    candidates.append(int(cid))
            
            if target_char_id is None and candidates:
                target_char_id = candidates[0]
            
            if target_char_id is None:
                print(f"Character '{character_query}' not found.", file=sys.stderr)
                return

        # Fetch all cards (cached)
        all_cards = get_cards_map(cache_hours)

        results = []
        # Sort logic
        if latest:
            sorted_keys = sorted(all_cards.keys(), key=lambda x: (all_cards[x].get("releasedAt", 0), int(x)), reverse=True)
        else:
            sorted_keys = sorted(all_cards.keys(), key=lambda x: (all_cards[x].get("rarity", 0), int(x)), reverse=True)

        for card_id in sorted_keys:
            card = all_cards[card_id]
            
            # Filters
            if target_char_id is not None and card.get("characterId") != target_char_id:
                continue
            if rarity and card.get("rarity") != rarity:
                continue
            if skill_id and card.get("skillId") != skill_id:
                continue
            
            res_set = card.get("resourceSetName")
            if not res_set:
                continue

            # Bestdori structure: /assets/{server}/characters/resourceset/{res_set}_rip/card_normal.png
            base_path = f"{ASSETS_BASE_URL}/{server}/characters/resourceset/{res_set}_rip"
            
            # Get character name for display
            char_info = char_map.get(str(card.get("characterId")), {})
            char_names = char_info.get("characterName", ["Unknown"])
            
            # Prefix selection: 3 (CN), 1 (EN), 0 (JP)
            prefixes = card.get("prefix", [])
            display_prefix = "Unknown"
            if len(prefixes) > 3 and prefixes[3]: display_prefix = prefixes[3]
            elif len(prefixes) > 1 and prefixes[1]: display_prefix = prefixes[1]
            elif len(prefixes) > 0 and prefixes[0]: display_prefix = prefixes[0]
            # JP prefix/name for display
            prefix_jp = prefixes[0] if len(prefixes) > 0 else None
            char_name_jp = char_names[0] if len(char_names) > 0 else None

            # Skill info (Chinese - index 3)
            skill_id = card.get("skillId")
            skill = skills_map.get(str(skill_id), {}) if skill_id else {}
            skill_desc_cn = None
            skill_simple_cn = None
            skill_durations = None
            desc_list = []
            simple_list = []
            if skill:
                desc_list = skill.get("description", [])
                simple_list = skill.get("simpleDescription", [])
                skill_desc_cn = desc_list[3] if len(desc_list) > 3 else None
                skill_simple_cn = simple_list[3] if len(simple_list) > 3 else None
                skill_durations = skill.get("duration")

            # Apply skill level to replace {0}
            if skill_level:
                skill_desc_cn = apply_skill_level(skill_desc_cn, skill_durations, skill_level)
                skill_simple_cn = apply_skill_level(skill_simple_cn, skill_durations, skill_level)

            # Expand skill levels (1-5) using template desc (before optional single-level replacement)
            expanded_desc = expand_skill_levels(desc_list[3] if skill else None, skill_durations)
            expanded_simple = expand_skill_levels(simple_list[3] if skill else None, skill_durations)

            card_info = {
                "id": int(card_id),
                "characterId": card.get("characterId"),
                "characterName": char_names[1] if len(char_names) > 1 else char_names[0],
                "characterNameJp": char_name_jp,
                "rarity": card.get("rarity"),
                "prefix": display_prefix,
                "prefixJp": prefix_jp,
                "attribute": card.get("attribute"),
                "type": card.get("type"),
                "skill": {
                    "id": skill_id,
                    "simpleDescription": skill_simple_cn,
                    "description": skill_desc_cn,
                    "duration": skill_durations,
                    "simpleDescriptionByLevel": expanded_simple,
                    "descriptionByLevel": expanded_desc
                },
                "urls": {
                    "normal": f"{base_path}/card_normal.png",
                    "trained": f"{base_path}/card_after_training.png" if card.get("rarity") >= 3 else None
                }
            }

            # keyword filter on CN description
            if skill_keyword:
                if not skill_desc_cn or skill_keyword not in skill_desc_cn:
                    continue

            # field filtering
            if fields:
                card_info = {k: v for k, v in card_info.items() if k in fields}

            results.append(card_info)
            if limit and len(results) >= limit:
                break

        if output_format == "text":
            for card in results:
                print(format_card_text(card))
                print("\n---\n")
        else:
            print(json.dumps(results, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Error fetching cards: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Bandori cards from Bestdori")
    parser.add_argument("--character", help="Character name (e.g. Anon, Tomori)")
    parser.add_argument("--rarity", type=int, help="Rarity (1-5)")
    parser.add_argument("--server", default="jp", help="Server (jp, en, cn, etc.)")
    parser.add_argument("--skill-level", type=int, help="Skill level (1-5) to resolve {0} in skill descriptions")
    parser.add_argument("--cache-hours", type=float, default=24, help="Cache hours for API responses")
    parser.add_argument("--limit", type=int, help="Limit number of cards")
    parser.add_argument("--latest", action="store_true", help="Sort by latest release first")
    parser.add_argument("--fields", help="Comma-separated fields to keep (e.g., id,prefix,skill,urls)")
    parser.add_argument("--skill-id", type=int, help="Filter by skill id")
    parser.add_argument("--skill-keyword", help="Filter by keyword in CN skill description")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")
    
    args = parser.parse_args()
    fields = [f.strip() for f in args.fields.split(',')] if args.fields else None
    fetch_cards(args.character, args.rarity, args.server, args.skill_level, args.cache_hours,
                args.limit, args.latest, fields, args.skill_id, args.skill_keyword, args.format)
