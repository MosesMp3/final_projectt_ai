import requests, time
import os
from dotenv import load_dotenv


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


games = [125764, 242408, 294041]

game_data = pull_games_by_id(games, headers)
print(game_data)
