#!/usr/bin/env python3
import sys
import json
import subprocess

def get_latest_card(character_id):
    try:
        # Get cards JSON from Sekai-World master db diff
        cmd = f"curl -s https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/main/cards.json | jq -c '.[] | select(.characterId == {character_id})' | jq -s 'sort_by(.releaseAt) | last'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return None, "Failed to fetch or parse cards data."
        
        if not result.stdout.strip():
            return None, "No card data found for this ID."

        card = json.loads(result.stdout)
        return card, None
    except Exception as e:
        return None, str(e)

def main():
    if len(sys.argv) < 2:
        print("Usage: get_card.py <character_id_or_name>")
        sys.exit(1)

    char_input = sys.argv[1].lower()
    
    # Official Mapping based on gameCharacters.json
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

    card, error = get_latest_card(char_id)
    if error:
        print(f"Error: {error}")
        sys.exit(1)

    if not card:
        print("No card found.")
        sys.exit(1)

    asset = card.get("assetbundleName")
    prefix = card.get("prefix")
    rarity = card.get("cardRarityType")
    
    # Correct base URL discovered: sekai-jp-assets
    base_url = "https://storage.sekai.best/sekai-jp-assets/character/member"
    
    print(f"Latest Card for Character {char_id}: {prefix}")
    print(f"Rarity: {rarity}")
    print(f"Normal: {base_url}/{asset}/card_normal.png")
    # Birthday cards don't have after_training
    if rarity != "rarity_birthday":
        print(f"After Training: {base_url}/{asset}/card_after_training.png")

if __name__ == "__main__":
    main()
