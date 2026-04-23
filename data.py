import requests, time
import os
from dotenv import load_dotenv
import json

load_dotenv()

CLIENT_ID = os.environ["IGDB_CLIENT_ID"]
CLIENT_SECRET = os.environ["IGDB_CLIENT_SECRET"]


print(CLIENT_ID)
print(CLIENT_SECRET)


response = requests.post(
    "https://id.twitch.tv/oauth2/token",
    params={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
    },
)

data = response.json()
print(data)

token = data["access_token"]


headers = {
    "Client-ID": CLIENT_ID,
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
}

print(headers)


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


ids = []
with open("games.txt") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):  # skip blanks and comments
            continue
        game_id, name = line.split(",", 1)
        ids.append(int(game_id.strip()))


game_data = pull_games_by_id(ids, headers)
print(game_data)

os.makedirs("cache", exist_ok=True)
with open("cache/games_raw.json", "w") as f:
    json.dump(game_data, f, indent=2)

print("SAVED")

"""
lookups = {}
for endpoint in ["genres", "themes", "game_modes", "player_perspectives", "platforms"]:
    resp = requests.post(
        f"https://api.igdb.com/v4/{endpoint}",
        headers=headers,
        data="fields id, name; limit 500;",
    )
    lookups[endpoint] = {item["id"]: item["name"] for item in resp.json()}
    print(f"{endpoint}: {len(lookups[endpoint])} entries")

serializable = {
    field: {str(k): v for k, v in m.items()} for field, m in lookups.items()
}
with open("cache/lookups.json", "w") as f:
    json.dump(serializable, f, indent=2)

"""
