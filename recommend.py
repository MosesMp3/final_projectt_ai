from encoding import load_games, load_rawg, encode_game, build_all_positions, find_game_by_id

def recommend(game_id, games_raw, positions, rawg_data=None, top_n=5):
    input_game = find_game_by_id(game_id, games_raw)

    if input_game is None:
        return []

    a = encode_game(input_game, positions, rawg_data)

    scores = []
    for current_game in games_raw:
        if not current_game.get("genres") or not current_game.get("platforms"):
            continue

        b = encode_game(current_game, positions, rawg_data)

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