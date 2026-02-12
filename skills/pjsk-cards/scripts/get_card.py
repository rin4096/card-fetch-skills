#!/usr/bin/env python3
"""PJSK Card Query Tool — search Project Sekai cards by character, prefix, or card ID.

Supports filtering by rarity, attribute, unit, and result limits.
Outputs human-readable text (default) or JSON for programmatic use.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CARDS_URL = (
    "https://raw.githubusercontent.com/"
    "Sekai-World/sekai-master-db-diff/main/cards.json"
)
CACHE_FILE = "/tmp/sekai_cards_cache.json"
CACHE_TTL = 3600  # seconds

ASSET_BASE = "https://storage.sekai.best/sekai-jp-assets/character/member"
DETAIL_BASE = "https://sekai.best/card"

CHARACTER_DATA = {
    1:  {"name": "星乃 一歌",     "unit": "light_sound"},
    2:  {"name": "天馬 咲希",     "unit": "light_sound"},
    3:  {"name": "望月 穂波",     "unit": "light_sound"},
    4:  {"name": "日野森 志歩",   "unit": "light_sound"},
    5:  {"name": "花里 みのり",   "unit": "idol"},
    6:  {"name": "桐谷 遥",       "unit": "idol"},
    7:  {"name": "桃井 愛莉",     "unit": "idol"},
    8:  {"name": "日野森 雫",     "unit": "idol"},
    9:  {"name": "小豆沢 こはね", "unit": "street"},
    10: {"name": "白石 杏",       "unit": "street"},
    11: {"name": "東雲 彰人",     "unit": "street"},
    12: {"name": "青柳 冬弥",     "unit": "street"},
    13: {"name": "天馬 司",       "unit": "theme_park"},
    14: {"name": "鳳 えむ",       "unit": "theme_park"},
    15: {"name": "草薙 寧々",     "unit": "theme_park"},
    16: {"name": "神代 類",       "unit": "theme_park"},
    17: {"name": "宵崎 奏",       "unit": "school_refusal"},
    18: {"name": "朝比奈 まふゆ", "unit": "school_refusal"},
    19: {"name": "東雲 絵名",     "unit": "school_refusal"},
    20: {"name": "暁山 瑞希",     "unit": "school_refusal"},
    21: {"name": "初音 ミク",     "unit": "piapro"},
    22: {"name": "鏡音 リン",     "unit": "piapro"},
    23: {"name": "鏡音 レン",     "unit": "piapro"},
    24: {"name": "巡音 ルカ",     "unit": "piapro"},
    25: {"name": "MEIKO",         "unit": "piapro"},
    26: {"name": "KAITO",         "unit": "piapro"},
}

# Romaji / common aliases → character ID
NAME_ALIASES = {
    "ichika": 1, "saki": 2, "honami": 3, "shiho": 4,
    "minori": 5, "haruka": 6, "airi": 7, "shizuku": 8,
    "kohane": 9, "an": 10, "akito": 11, "toya": 12,
    "tsukasa": 13, "emu": 14, "nene": 15, "rui": 16,
    "kanade": 17, "mafuyu": 18, "ena": 19, "mizuki": 20,
    "miku": 21, "rin": 22, "len": 23, "luka": 24,
    "meiko": 25, "kaito": 26,
    # Common short forms / variants
    "咲希": 2, "穂波": 3, "志歩": 4,
    "みのり": 5, "遥": 6, "愛莉": 7, "雫": 8,
    "こはね": 9, "杏": 10, "彰人": 11, "冬弥": 12,
    "司": 13, "えむ": 14, "寧々": 15, "類": 16,
    "奏": 17, "まふゆ": 18, "絵名": 19, "瑞希": 20,
    "一歌": 1,
    # 繁體中文
    "繪名": 19,
    # Abbreviations / nicknames
    "mfy": 18, "mnr": 5,
    "ick": 1, "khn": 9,
}

# Unit short aliases → internal unit name
UNIT_ALIASES = {
    "leo": "light_sound",
    "mmj": "idol",
    "vbs": "street",
    "ws": "theme_park",
    "n25": "school_refusal",
    "vs": "piapro",
}

RARITY_DISPLAY = {
    "rarity_1": "★",
    "rarity_2": "★★",
    "rarity_3": "★★★",
    "rarity_4": "★★★★",
    "rarity_birthday": "BD ★",
    "rarity_5": "★★★★★",
}

# Normalised rarity input → cardRarityType value
RARITY_ALIASES = {
    "1": "rarity_1", "2": "rarity_2", "3": "rarity_3",
    "4": "rarity_4", "5": "rarity_5",
    "bd": "rarity_birthday", "birthday": "rarity_birthday",
}

UNIT_DISPLAY = {
    "light_sound":     "Leo/need",
    "idol":            "MORE MORE JUMP!",
    "street":          "Vivid BAD SQUAD",
    "theme_park":      "ワンダーランズ×ショウタイム",
    "school_refusal":  "25時、ナイトコードで。",
    "piapro":          "VIRTUAL SINGER",
    "none":            "—",
}

ATTR_DISPLAY = {
    "cute": "キュート",
    "cool": "クール",
    "pure": "ピュア",
    "happy": "ハッピー",
    "mysterious": "ミステリアス",
}

VALID_ATTRS = set(ATTR_DISPLAY.keys())

# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def fetch_cards(*, no_cache: bool = False) -> List[dict]:
    """Load cards.json, using a local cache (TTL = CACHE_TTL seconds)."""
    # Try cache first (skip if --no-cache)
    if not no_cache and os.path.exists(CACHE_FILE):
        try:
            mtime = os.path.getmtime(CACHE_FILE)
            if time.time() - mtime < CACHE_TTL:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except (OSError, json.JSONDecodeError, ValueError):
            pass  # Cache invalid — fall through to fetch

    # Fetch from GitHub
    try:
        req = urllib.request.Request(CARDS_URL, headers={"User-Agent": "pjsk-cards/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw)
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as exc:
        # If cache exists (even stale), use it as fallback
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        raise SystemExit(f"錯誤: 無法獲取卡片數據 — {exc}") from exc

    # Write cache
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except OSError:
        pass  # Non-fatal: cache write failure

    return data

# ---------------------------------------------------------------------------
# Resolvers
# ---------------------------------------------------------------------------

def resolve_character_id(name: str) -> Optional[int]:
    """Resolve a character name/alias/ID string to an integer character ID."""
    key = name.strip().lower()

    # Direct alias hit
    if key in NAME_ALIASES:
        return NAME_ALIASES[key]

    # Check Japanese name fragments (case-insensitive not meaningful for JP,
    # but handles mixed-case romaji + JP input)
    for cid, info in CHARACTER_DATA.items():
        jp = info["name"]
        if key == jp or key in jp or key == jp.replace(" ", ""):
            return cid

    # Numeric ID
    try:
        cid = int(name)
        if cid in CHARACTER_DATA:
            return cid
    except ValueError:
        pass

    return None


def resolve_rarity(value: str) -> Optional[str]:
    """Normalise a rarity input to the cardRarityType enum string."""
    return RARITY_ALIASES.get(value.strip().lower())

# ---------------------------------------------------------------------------
# Card querying
# ---------------------------------------------------------------------------

def query_cards(
    cards: list[dict],
    *,
    character_id: Optional[int] = None,
    prefix: Optional[str] = None,
    card_id: Optional[int] = None,
    rarity: Optional[str] = None,
    attr: Optional[str] = None,
    unit: Optional[str] = None,
) -> List[dict]:
    """Filter and return matching cards, sorted newest-first by releaseAt."""
    results = cards

    if card_id is not None:
        results = [c for c in results if c.get("id") == card_id]
        # card_id is unique — return immediately
        return results

    if character_id is not None:
        results = [c for c in results if c.get("characterId") == character_id]

    if unit is not None:
        # Filter by unit: match characterId whose unit matches
        unit_char_ids = {cid for cid, info in CHARACTER_DATA.items() if info["unit"] == unit}
        results = [c for c in results if c.get("characterId") in unit_char_ids]

    if prefix is not None:
        # Substring match (case-sensitive for JP, but lowercase both for romaji)
        results = [
            c for c in results
            if prefix in c.get("prefix", "") or prefix.lower() in c.get("prefix", "").lower()
        ]

    if rarity is not None:
        results = [c for c in results if c.get("cardRarityType") == rarity]

    if attr is not None:
        results = [c for c in results if c.get("attr") == attr.lower()]

    # Sort newest first
    results.sort(key=lambda c: c.get("releaseAt", 0), reverse=True)
    return results

# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_release_date(timestamp_ms: Optional[int]) -> str:
    """Convert millisecond epoch to YYYY-MM-DD (JST)."""
    if not timestamp_ms:
        return "—"
    jst = timezone(timedelta(hours=9))
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=jst)
    return dt.strftime("%Y-%m-%d")


def card_to_dict(card: dict) -> dict:
    """Build a clean dict for a single card (used by both text and JSON output)."""
    cid = card.get("characterId")
    char_info = CHARACTER_DATA.get(cid, {})
    rarity_raw = card.get("cardRarityType", "")
    asset = card.get("assetbundleName", "")
    card_id = card.get("id")
    attr_raw = card.get("attr", "")

    has_trained = rarity_raw not in ("rarity_1", "rarity_2", "rarity_birthday")
    normal_url = f"{ASSET_BASE}/{asset}/card_normal.png" if asset else None
    trained_url = f"{ASSET_BASE}/{asset}/card_after_training.png" if asset and has_trained else None

    return {
        "id": card_id,
        "prefix": card.get("prefix", ""),
        "character_id": cid,
        "character_name": char_info.get("name", "—"),
        "unit": char_info.get("unit", "none"),
        "unit_name": UNIT_DISPLAY.get(char_info.get("unit", "none"), "—"),
        "attr": attr_raw,
        "attr_name": ATTR_DISPLAY.get(attr_raw, attr_raw),
        "rarity": rarity_raw,
        "rarity_display": RARITY_DISPLAY.get(rarity_raw, rarity_raw),
        "skill_name": card.get("cardSkillName", ""),
        "release_date": format_release_date(card.get("releaseAt")),
        "detail_url": f"{DETAIL_BASE}/{card_id}" if card_id else None,
        "normal_image": normal_url,
        "trained_image": trained_url,
    }


def print_card_text(info: dict, index: Optional[int] = None) -> None:
    """Print a single card in human-readable text format."""
    header = f"── 卡片 #{index} ──" if index is not None else ""
    if header:
        print(header)
    print(f"標題: {info['prefix']}")
    print(f"角色: {info['character_name']}")
    print(f"團隊: {info['unit_name']}")
    print(f"屬性: {info['attr_name']} ({info['attr']})")
    print(f"稀有度: {info['rarity_display']}")
    print(f"技能: {info['skill_name']}")
    print(f"實裝日: {info['release_date']}")
    if info["detail_url"]:
        print(f"詳情: {info['detail_url']}")
    if info["normal_image"]:
        print(f"普通圖: {info['normal_image']}")
    if info["trained_image"]:
        print(f"覺醒圖: {info['trained_image']}")

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="get_card.py",
        description="查詢 Project Sekai 卡片資訊",
    )

    # Main query (positional — character name/ID)
    p.add_argument(
        "character",
        nargs="?",
        default=None,
        help="角色名（英文/日文/ID），如 ena, 絵名, 19",
    )

    # Alternative queries
    p.add_argument("--prefix", "-p", help="按卡片標題搜索（支持子字串）")
    p.add_argument("--card-id", "-c", type=int, help="按卡片 ID 精確查找")

    # Filters
    p.add_argument(
        "--rarity", "-r",
        help="按稀有度篩選: 1, 2, 3, 4, 5, bd/birthday",
    )
    p.add_argument(
        "--attr", "-a",
        choices=sorted(VALID_ATTRS),
        help="按屬性篩選: cute, cool, pure, happy, mysterious",
    )
    p.add_argument(
        "--unit", "-u",
        choices=sorted(UNIT_ALIASES.keys()),
        help="按團隊篩選: leo, mmj, vbs, ws, n25, vs",
    )

    # Result control
    p.add_argument(
        "--limit", "-n",
        type=int,
        default=1,
        help="返回結果數量（預設 1，即最新一張）",
    )
    p.add_argument(
        "--all",
        action="store_true",
        help="返回所有匹配結果（覆蓋 --limit）",
    )

    # Output format
    p.add_argument(
        "--json", "-j",
        action="store_true",
        dest="json_output",
        help="以 JSON 格式輸出（方便程式化使用）",
    )

    # Cache control
    p.add_argument(
        "--no-cache",
        action="store_true",
        help="強制重新從 GitHub 拉取，忽略本地快取",
    )

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Bug 1: validate --limit is a positive integer
    if args.limit is not None and args.limit <= 0:
        raise SystemExit(f"錯誤: --limit 必須為正整數（收到: {args.limit}）")

    # Validate: at least one query dimension required
    has_query = (
        args.character is not None
        or args.prefix is not None
        or args.card_id is not None
        or args.unit is not None
    )
    if not has_query:
        parser.print_help(sys.stderr)
        raise SystemExit("\n錯誤: 請指定角色名、--prefix、--card-id 或 --unit")

    # Bug 2: warn when --card-id is used with filters that will be ignored
    if args.card_id is not None and (args.rarity is not None or args.attr is not None):
        print("注意: --card-id 為精確查找，--rarity/--attr 過濾器已被忽略", file=sys.stderr)

    # Resolve character
    character_id = None
    if args.character is not None:
        character_id = resolve_character_id(args.character)
        if character_id is None:
            msg = f"無法識別角色 '{args.character}'"
            if args.json_output:
                print(json.dumps({"error": msg, "results": []}, ensure_ascii=False))
                sys.exit(1)
            raise SystemExit(f"錯誤: {msg}")

    # Resolve rarity filter
    rarity_filter = None
    if args.rarity is not None:
        rarity_filter = resolve_rarity(args.rarity)
        if rarity_filter is None:
            msg = f"無效稀有度 '{args.rarity}'（可選: 1, 2, 3, 4, 5, bd）"
            if args.json_output:
                print(json.dumps({"error": msg, "results": []}, ensure_ascii=False))
                sys.exit(1)
            raise SystemExit(f"錯誤: {msg}")

    # Resolve unit filter
    unit_filter = None
    if args.unit is not None:
        unit_filter = UNIT_ALIASES.get(args.unit)

    # Fetch data
    cards = fetch_cards(no_cache=args.no_cache)

    # Query
    results = query_cards(
        cards,
        character_id=character_id,
        prefix=args.prefix,
        card_id=args.card_id,
        rarity=rarity_filter,
        attr=args.attr,
        unit=unit_filter,
    )

    # Bug 3: consistent error output in JSON mode
    if not results:
        if args.json_output:
            print(json.dumps({"error": "未找到匹配的卡片", "results": []}, ensure_ascii=False))
            sys.exit(1)
        else:
            raise SystemExit("未找到匹配的卡片。")

    # Apply limit
    if not args.all:
        results = results[: args.limit]

    # Format output
    output = [card_to_dict(c) for c in results]

    if args.json_output:
        # Single card → object; multiple → array
        payload = output[0] if len(output) == 1 else output
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for i, info in enumerate(output, 1):
            idx = i if len(output) > 1 else None
            print_card_text(info, index=idx)
            if i < len(output):
                print()


if __name__ == "__main__":
    main()
