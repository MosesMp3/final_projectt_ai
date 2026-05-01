from encoding import load_games, build_all_positions, find_game_by_id, encode_game

FIELDS = ["genres", "themes", "game_modes", "player_perspectives", "platforms"]

def cosine_recommend(game_id, games_raw, positions, top_n=5):
    input_game = find_game_by_id(game_id, games_raw)
    if input_game is None:
        return []
    a = encode_game(input_game, positions, FIELDS)  # added FIELDS
    scores = []
    for current_game in games_raw:
        if not current_game.get("genres") or not current_game.get("platforms"):
            continue
        b = encode_game(current_game, positions, FIELDS)  # added FIELDS
        dot = sum(x*y for x, y in zip(a, b))
        mag_a = sum(x**2 for x in a) ** 0.5
        mag_b = sum(x**2 for x in b) ** 0.5
        if mag_a == 0 or mag_b == 0:
            continue
        similarity = dot / (mag_a * mag_b)
        scores.append((current_game, similarity))
    if not scores:
        return []
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    scores = [s for s in scores if s[0]["id"] != game_id]
    return [(s[0]["name"], s[1]) for s in scores[:top_n]]

# test
games_raw = load_games()
positions = build_all_positions(games_raw, FIELDS)

test_ids = [
    (125764, "Guilty Gear: Strive"),
    (119133, "Elden Ring"),
    (14593,  "Hollow Knight"),
    (17000,  "Stardew Valley"),
    (125174, "Overwatch"),
    (115,    "League of Legends"),
    (135915, "Overcooked! All You Can Eat"),
    (132181, "Resident Evil 4"),
    (119277, "Genshin Impact"),
    (339698, "Dead by Daylight"),
]

for game_id, name in test_ids:
    results = cosine_recommend(game_id, games_raw, positions, top_n=5)
    print(f"\nSimilar to {name}:")
    for rec_name, score in results:
        print(f"  {score:.3f}  {rec_name}")