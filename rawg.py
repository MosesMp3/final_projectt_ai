import requests
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

RAWG_API_KEY = os.environ["RAWG_API_KEY"]
BASE_URL = "https://api.rawg.io/api"

def search_game(game_name):
    resp = requests.get(f"{BASE_URL}/games", params={
        "key": RAWG_API_KEY,
        "search": game_name,
        "page_size": 5,  # get more results
        "language": "eng"  # English only
    })
    results = resp.json().get("results", [])
    
    # try to find exact name match first
    for result in results:
        if result["name"].lower() == game_name.lower():
            return result
    
    # fall back to first result
    return results[0] if results else None

def get_rawg_data_for_games(games_raw):
    results = {}
    for game in games_raw:
        name = game["name"]
        match = search_game(name)
        if match:
            tags = [t["name"] for t in match.get("tags") or []]
            genres = [g["name"] for g in match.get("genres") or []]

            results[name] = {
                "rawg_id": match.get("id"),
                "rating": match.get("rating"),
                "rating_count": match.get("ratings_count"),
                "metacritic": match.get("metacritic"),
                "playtime": match.get("playtime"),
                "tags": tags,
                "genres": genres,
            }
        else:
            results[name] = None
        time.sleep(0.25)
    return results