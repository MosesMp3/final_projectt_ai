import json
import os
from rawg import get_rawg_data_for_games
from encoding import load_games

# load only your handpicked game IDs
handpicked_ids = []
with open("games.txt") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        game_id, name = line.split(",", 1)
        handpicked_ids.append(int(game_id.strip()))

# filter games_raw to only handpicked games
games_raw = load_games()
handpicked_games = [g for g in games_raw if g["id"] in handpicked_ids]

print(f"Fetching RAWG data for {len(handpicked_games)} handpicked games...")
rawg_data = get_rawg_data_for_games(handpicked_games)

os.makedirs("cache", exist_ok=True)
with open("cache/rawg_data.json", "w") as f:
    json.dump(rawg_data, f, indent=2)

print(f"Done! {len(rawg_data)} games saved.")