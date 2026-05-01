import requests, time
import os
from dotenv import load_dotenv
import json

load_dotenv()

CLIENT_ID = os.environ["IGDB_CLIENT_ID"]
CLIENT_SECRET = os.environ["IGDB_CLIENT_SECRET"]

response = requests.post(
    "https://id.twitch.tv/oauth2/token",
    params={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
    },
)

token = response.json()["access_token"]

headers = {
    "Client-ID": CLIENT_ID,
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
}

def pull_games_by_id(game_ids, headers):
    fields = (
        "id,name,genres,themes,game_modes,player_perspectives,"
        "platforms,keywords,summary,storyline,first_release_date,"
        "total_rating,total_rating_count,similar_games,category"
    )
    ids_str = ",".join(str(i) for i in game_ids)
    body = f"fields {fields}; where id = ({ids_str}); limit 500;"
    resp = requests.post("https://api.igdb.com/v4/games", headers=headers, data=body)
    return resp.json()

def pull_games_bulk(headers, limit=500, offset=0):
    fields = (
        "id,name,genres,themes,game_modes,player_perspectives,"
        "platforms,keywords,summary,storyline,first_release_date,"
        "total_rating,total_rating_count,similar_games,category"
    )
    body = (
        f"fields {fields}; "
        f"limit {limit}; "
        f"offset {offset}; "
        f"sort total_rating_count desc; "
        f"where total_rating_count > 50 & genres != null & platforms != null;"
    )
    resp = requests.post("https://api.igdb.com/v4/games", headers=headers, data=body)
    return resp.json()

# read handpicked IDs
ids = []
with open("games.txt") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        game_id, name = line.split(",", 1)
        ids.append(int(game_id.strip()))

# pull handpicked games
your_games = pull_games_by_id(ids, headers)

# pull bulk games
bulk_games = []
for offset in range(0, 5000, 500):
    batch = pull_games_bulk(headers, limit=500, offset=offset)
    if not batch:
        break
    bulk_games.extend(batch)
    time.sleep(0.25)

# combine and remove duplicates
all_ids_seen = set()
combined = []
for game in your_games + bulk_games:
    if game["id"] not in all_ids_seen:
        all_ids_seen.add(game["id"])
        combined.append(game)

# save combined
os.makedirs("cache", exist_ok=True)
with open("cache/games_raw.json", "w") as f:
    json.dump(combined, f, indent=2)