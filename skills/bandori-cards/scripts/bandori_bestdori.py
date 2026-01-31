#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests

# Bestdori API Endpoints
CARDS_API = "https://bestdori.com/api/cards/all.5.json"
CARD_DETAIL_API = "https://bestdori.com/api/cards/{card_id}.json"
CHARACTERS_API = "https://bestdori.com/api/characters/all.2.json"
SKILLS_API = "https://bestdori.com/api/skills/all.5.json"
ASSETS_BASE_URL = "https://bestdori.com/assets"
CACHE_DIR = Path(__file__).resolve().parent / ".cache"
SUPPORTED_SERVERS = {"jp", "en", "cn", "tw", "kr"}


def _cache_path(name: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{name}.json"


def _load_cache(name: str, max_age_hours: Optional[float]):
    try:
        path = _cache_path(name)
        if not path.exists():
            return None
        if max_age_hours is not None:
            age = time.time() - path.stat().st_mtime
            if age > max_age_hours * 3600:
                return None
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _save_cache(name: str, data):
    try:
        path = _cache_path(name)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass


def _get_json(url: str, timeout: int = 10):
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def get_character_map(cache_hours=24):
    cached = _load_cache("characters", cache_hours)
    if cached:
        return cached
    try:
        data = _get_json(CHARACTERS_API)
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
        data = _get_json(SKILLS_API)
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
        data = _get_json(CARDS_API)
        _save_cache("cards", data)
        return data
    except Exception as e:
        print(f"Error fetching cards: {e}", file=sys.stderr)
    return {}


def get_card_detail(card_id: int, cache_hours=24) -> dict:
    cache_key = f"card_{card_id}"
    cached = _load_cache(cache_key, cache_hours)
    if cached:
        return cached
    try:
        data = _get_json(CARD_DETAIL_API.format(card_id=card_id))
        _save_cache(cache_key, data)
        return data
    except Exception as e:
        print(f"Error fetching card detail {card_id}: {e}", file=sys.stderr)
    return {}


def apply_skill_level(desc: Optional[str], durations, level: int):
    if not desc or not durations or not level:
        return desc
    try:
        idx = max(1, min(level, len(durations))) - 1
        dur = str(durations[idx])
        # If {1} exists, it's usually duration; keep {0} as-is
        if "{1}" in desc:
            return desc.replace("{1}", dur)
        # Otherwise, use {0} for duration
        return desc.replace("{0}", dur)
    except Exception:
        return desc


def expand_skill_levels(desc: Optional[str], durations):
    if not desc or not durations:
        return None
    expanded = {}
    for i in range(1, len(durations) + 1):
        expanded[str(i)] = apply_skill_level(desc, durations, i)
    return expanded


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


KEYWORD_ALIASES = {
    "sanrio": ["kitty", "キティ", "キティちゃん", "hello kitty"],
}


def keyword_variants(keyword: str) -> List[str]:
    key = normalize_text(keyword)
    if not key:
        return []
    variants = [key]
    for alias in KEYWORD_ALIASES.get(key, []):
        norm_alias = normalize_text(alias)
        if norm_alias:
            variants.append(norm_alias)
    return variants


def keyword_in_texts(keyword: str, texts: List[Optional[str]]) -> bool:
    variants = keyword_variants(keyword)
    if not variants:
        return False
    for text in texts:
        if not text:
            continue
        normalized = normalize_text(text)
        for key in variants:
            if key and key in normalized:
                return True
    return False


def match_character_id(character_query: str, char_map: Dict[str, dict]) -> Optional[int]:
    query = normalize_text(character_query)
    if not query:
        return None

    # Exact match (case-insensitive) across all locales
    for cid, info in char_map.items():
        names = [n for n in info.get("characterName", []) if n]
        if any(normalize_text(n) == query for n in names):
            return int(cid)

    # Word boundary match (avoids Anon vs Kanon)
    for cid, info in char_map.items():
        names = [n for n in info.get("characterName", []) if n]
        for n in names:
            words = normalize_text(n).split()
            if query in words:
                return int(cid)

    # Fallback: contains
    for cid, info in char_map.items():
        names = [n for n in info.get("characterName", []) if n]
        if any(query in normalize_text(n) for n in names):
            return int(cid)

    return None


def format_skill_levels(desc_by_level: Optional[Dict[str, str]]) -> List[str]:
    if not desc_by_level:
        return []
    lines = []
    for level in sorted(desc_by_level.keys(), key=lambda x: int(x)):
        lines.append(f"- Lv{level}: {desc_by_level[level]}")
    return lines


def format_card_text(card_info: dict) -> str:
    title = f"{card_info.get('prefixJp','')}｜{card_info.get('characterNameJp','')}".strip("｜")
    lines = [f"标题: {title}"]
    lines.append(f"稀有度: {'★' * card_info.get('rarity', 0)}")
    lines.append(f"属性: {card_info.get('attribute')}")
    lines.append(f"类型: {card_info.get('type')}")
    gacha_text = card_info.get("gachaText")
    if gacha_text:
        lines.append("招募台词:")
        for t in gacha_text:
            if t:
                lines.append(f"- {t}")
    lines.append("卡面:")
    urls = card_info.get("urls", {})
    if urls.get("normal"):
        lines.append(f"- 普通: {urls['normal']}")
    if urls.get("trained"):
        lines.append(f"- 特训后: {urls['trained']}")
    skill = card_info.get("skill", {})
    lines.append(f"技能 (ID: {skill.get('id')}):")
    if skill.get("simpleDescription"):
        lines.append(f"- 简述: {skill.get('simpleDescription')}")
    for line in format_skill_levels(skill.get("descriptionByLevel")):
        lines.append(line)
    return "\n".join(lines)


def fetch_cards(character_query=None, rarity=None, server="jp", skill_level=None, cache_hours=24,
               limit=None, latest=False, fields=None, skill_id=None, skill_keyword=None, prefix_keyword=None,
               output_format="json"):
    try:
        if server not in SUPPORTED_SERVERS:
            raise ValueError(f"Unsupported server: {server}. Choose from {sorted(SUPPORTED_SERVERS)}")

        char_map = get_character_map(cache_hours)
        skills_map = get_skills_map(cache_hours)
        target_char_id = None

        if character_query:
            target_char_id = match_character_id(character_query, char_map)
            if target_char_id is None:
                print(f"Character '{character_query}' not found.", file=sys.stderr)
                return

        all_cards = get_cards_map(cache_hours)
        results = []

        # Sort logic
        if latest:
            def _rel_key(x):
                r = all_cards[x].get("releasedAt")
                try:
                    r = int(r) if r is not None else 0
                except Exception:
                    r = 0
                return (r, int(x))
            sorted_keys = sorted(all_cards.keys(), key=_rel_key, reverse=True)
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

            base_path = f"{ASSETS_BASE_URL}/{server}/characters/resourceset/{res_set}_rip"

            char_info = char_map.get(str(card.get("characterId")), {})
            char_names = char_info.get("characterName", ["Unknown"])

            prefixes = card.get("prefix", [])
            display_prefix = "Unknown"
            if len(prefixes) > 3 and prefixes[3]:
                display_prefix = prefixes[3]
            elif len(prefixes) > 1 and prefixes[1]:
                display_prefix = prefixes[1]
            elif len(prefixes) > 0 and prefixes[0]:
                display_prefix = prefixes[0]

            card_detail = None
            gacha_texts = []
            skill_name_texts = []

            if prefix_keyword:
                if not keyword_in_texts(prefix_keyword, [p for p in prefixes if p]):
                    # Only fetch details if prefix doesn't match
                    card_detail = get_card_detail(int(card_id), cache_hours)
                    gacha_texts = card_detail.get("gachaText") or []
                    skill_name_texts = card_detail.get("skillName") or []
                    if not keyword_in_texts(prefix_keyword, gacha_texts + skill_name_texts):
                        continue

            prefix_jp = prefixes[0] if len(prefixes) > 0 else None
            char_name_jp = char_names[0] if len(char_names) > 0 else None

            # Skill info (Chinese - index 3)
            skill_id_local = card.get("skillId")
            skill = skills_map.get(str(skill_id_local), {}) if skill_id_local else {}
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

            if skill_level:
                skill_desc_cn = apply_skill_level(skill_desc_cn, skill_durations, skill_level)
                skill_simple_cn = apply_skill_level(skill_simple_cn, skill_durations, skill_level)

            expanded_desc = expand_skill_levels(desc_list[3] if len(desc_list) > 3 else None, skill_durations)
            expanded_simple = expand_skill_levels(simple_list[3] if len(simple_list) > 3 else None, skill_durations)

            needs_detail = bool(fields and any(f in {"gachaText", "skillName", "episodes"} for f in fields))
            if needs_detail and card_detail is None:
                card_detail = get_card_detail(int(card_id), cache_hours)
                gacha_texts = card_detail.get("gachaText") or []
                skill_name_texts = card_detail.get("skillName") or []

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
                "gachaText": gacha_texts if gacha_texts else None,
                "skillName": skill_name_texts if skill_name_texts else None,
                "episodes": card_detail.get("episodes") if card_detail else None,
                "skill": {
                    "id": skill_id_local,
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

            if skill_keyword:
                if not skill_desc_cn or skill_keyword not in skill_desc_cn:
                    continue

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
    parser.add_argument("--server", default="jp", help="Server (jp, en, cn, tw, kr)")
    parser.add_argument("--skill-level", type=int, help="Skill level (1-5) to resolve {0} in skill descriptions")
    parser.add_argument("--cache-hours", type=float, default=24, help="Cache hours for API responses")
    parser.add_argument("--limit", type=int, help="Limit number of cards")
    parser.add_argument("--latest", action="store_true", help="Sort by latest release first")
    parser.add_argument("--fields", help="Comma-separated fields to keep (e.g., id,prefix,skill,urls)")
    parser.add_argument("--skill-id", type=int, help="Filter by skill id")
    parser.add_argument("--skill-keyword", help="Filter by keyword in CN skill description")
    parser.add_argument("--prefix", help="Filter by card prefix keyword (any language)")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")

    args = parser.parse_args()
    fields = [f.strip() for f in args.fields.split(",")] if args.fields else None
    fetch_cards(args.character, args.rarity, args.server, args.skill_level, args.cache_hours,
                args.limit, args.latest, fields, args.skill_id, args.skill_keyword, args.prefix, args.format)
