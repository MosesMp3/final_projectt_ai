import json
import os
from datetime import datetime

import numpy as np


def load_games(path="cache/games_raw.json"):
    with open(path) as f:
        return json.load(f)


def load_lookups(path="cache/lookups.json"):
    with open(path) as f:
        return json.load(f)


def build_positions(games, field_name):
    unique_ids = set()
    for game in games:
        for id_ in game.get(field_name) or []:
            unique_ids.add(id_)
    return {id_: i for i, id_ in enumerate(sorted(unique_ids))}


def build_all_positions(games, fields):
    return {field: build_positions(games, field) for field in fields}


def encode_field(values, vocab_positions):
    vec = [0] * len(vocab_positions)
    for val in values or []:
        if val in vocab_positions:
            vec[vocab_positions[val]] = 1
    return vec


def encode_categorical(game, positions, fields):
    parts = []
    for field in fields:
        parts.append(encode_field(game.get(field), positions[field]))
    return sum(parts, [])


def encode_scalars(game):
    rating = (game.get("total_rating") or 0) / 100.0
    ts = game.get("first_release_date")
    year = datetime.fromtimestamp(ts).year if ts else 2000
    year_norm = (max(1980, min(2026, year)) - 1980) / 46.0
    return [rating, year_norm]


def encode_game(game, positions, fields):
    return encode_categorical(game, positions, fields) + encode_scalars(game)


def build_feature_matrix(games, positions, fields):
    matrix = np.array(
        [encode_game(g, positions, fields) for g in games],
        dtype=np.float32,
    )
    ids = np.array([g["id"] for g in games], dtype=np.int64)
    names = np.array([g["name"] for g in games])
    return matrix, ids, names


def extract_similar_truth(games):
    return {g["id"]: (g.get("similar_games") or []) for g in games}


def save_outputs(matrix, ids, names, similar_truth, out_dir="cache"):
    os.makedirs(out_dir, exist_ok=True)
    np.savez(
        f"{out_dir}/features.npz",
        feature_matrix=matrix,
        game_ids=ids,
        game_names=names,
    )
    with open(f"{out_dir}/similar_truth.json", "w") as f:
        json.dump({str(k): v for k, v in similar_truth.items()}, f)

def find_game_by_id(game_id, games):
    for game in games:
        if game["id"] == game_id:
            return game
    return None


FIELDS = ["genres", "themes", "game_modes", "player_perspectives", "platforms"]

games = load_games()
positions = build_all_positions(games, FIELDS)
matrix, ids, names = build_feature_matrix(games, positions, FIELDS)
truth = extract_similar_truth(games)
save_outputs(matrix, ids, names, truth)

print(f"Saved {matrix.shape[0]} games × {matrix.shape[1]} features")
