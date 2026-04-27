import json

def load_games():
    with open("cache/games_raw.json") as f:
        return json.load(f)

def load_rawg():
    with open("cache/rawg_data.json") as f:
        return json.load(f)

def load_lookups():
    with open("cache/lookups.json") as f:
        return json.load(f)

def build_positions(games, field_name):
    unique_ids = set()
    for game in games:
        for id_ in game.get(field_name) or []:
            unique_ids.add(id_)
    sorted_ids = sorted(unique_ids)
    return {id_: i for i, id_ in enumerate(sorted_ids)}

def build_all_positions(games):
    fields = ["genres", "themes", "game_modes", "player_perspectives", "platforms"]
    return {field: build_positions(games, field) for field in fields}

def encode_field(game_field_values, vocab_positions):
    vec = [0] * len(vocab_positions)
    for val in game_field_values or []:
        if val in vocab_positions:
            vec[vocab_positions[val]] = 1
    return vec

def encode_game(game, positions, rawg_data=None):
    parts = []

    # genres weighted 3x
    genre_vec = encode_field(game.get("genres"), positions["genres"])
    genre_vec = [x * 3.0 for x in genre_vec]
    parts.append(genre_vec)

    # themes weighted 2x
    theme_vec = encode_field(game.get("themes"), positions["themes"])
    theme_vec = [x * 2.0 for x in theme_vec]
    parts.append(theme_vec)

    # game modes weighted 2x
    game_mode_vec = encode_field(game.get("game_modes"), positions["game_modes"])
    game_mode_vec = [x * 2.0 for x in game_mode_vec]
    parts.append(game_mode_vec)

    # player perspectives normal weight
    parts.append(encode_field(game.get("player_perspectives"), positions["player_perspectives"]))

    # platforms reduced weight
    platform_vec = encode_field(game.get("platforms"), positions["platforms"])
    platform_vec = [x * 0.25 for x in platform_vec]
    parts.append(platform_vec)

    # RAWG ratings only
    if rawg_data:
        name = game.get("name")
        entry = rawg_data.get(name)
        if entry:
            rating = entry.get("rating") or 0
            metacritic = entry.get("metacritic") or 0
            playtime = entry.get("playtime") or 0
            parts.append([rating / 5.0])
            parts.append([metacritic / 100.0])
            parts.append([min(playtime, 200) / 200.0])
        else:
            parts.append([0.7])
            parts.append([0.7])
            parts.append([0.25])

    return sum(parts, [])

def find_game_by_id(game_id, games):
    for game in games:
        if game["id"] == game_id:
            return game
    return None