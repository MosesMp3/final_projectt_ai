import json

with open("cache/games_raw.json") as f:
    games_raw = json.load(f)

with open("cache/lookups.json") as d:
    lookups = json.load(d)
print(len(games_raw))


def build_positions(games, field_name):
    unique_ids = set()
    for game in games:
        for id_ in game.get(field_name) or []:
            unique_ids.add(id_)
    sorted_ids = sorted(unique_ids)
    return {id_: i for i, id_ in enumerate(sorted_ids)}


def encode_field(game_field_values, vocab_positions):
    vec = [0] * len(vocab_positions)
    for val in game_field_values or []:
        if val in vocab_positions:
            vec[vocab_positions[val]] = 1
    return vec


fields = ["genres", "themes", "game_modes", "player_perspectives", "platforms"]
positions = {field: build_positions(games_raw, field) for field in fields}


for field, pos in positions.items():
    print(f"{field}: {len(pos)} unique values")


def encode_game(game, positions):
    """Encode one game's categorical fields into a single concatenated vector."""
    parts = []
    for field in ["genres", "themes", "game_modes", "player_perspectives", "platforms"]:
        parts.append(encode_field(game.get(field), positions[field]))
    return sum(parts, [])  # flatten list of lists


"""
for game in games_raw:
    encoded = encode_game(game, positions)
    print(f"Feature length: {len(encoded)}")
    print(f"Active features: {sum(encoded)}")
    print(encoded)

"""


encoded = encode_game(games_raw[1], positions)
print(f"name:{games_raw[1].get('name')}")
print(f"Feature length: {len(encoded)}")
print(f"Active features: {sum(encoded)}")
print(encoded)
