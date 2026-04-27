from encoding import load_games, load_rawg, build_all_positions, find_game_by_id
from recommend import recommend

def batch_test(games_raw, positions, rawg_data):
    test_games = [
        "Guilty Gear: Strive",
        "Elden Ring",
        "Hollow Knight",
        "Stardew Valley",
        "Overwatch",
        "League of Legends",
        "Knightica",
        "Overcooked! All You Can Eat",
        "Resident Evil 4",
        "Genshin Impact"
    ]

    for name in test_games:
        match = None
        for game in games_raw:
            if game["name"].lower() == name.lower():
                match = game
                break

        if match is None:
            print(f"'{name}' not found\n")
            continue

        results = recommend(match["id"], games_raw, positions, rawg_data)
        print(f"Similar to {match['name']}:")
        for i, (rec_name, score) in enumerate(results, 1):
            print(f"  {i}. {rec_name} ({score:.3f})")
        print()

def main():
    games_raw = load_games()
    rawg_data = load_rawg()
    positions = build_all_positions(games_raw)

    print("=== Game Recommender ===")
    print(f"Database: {len(games_raw)} games loaded\n")

    while True:
        user_input = input("Enter a game name (or 'quit' to exit, 'test' to run batch test): ").strip()

        if user_input.lower() == "quit":
            break

        elif user_input.lower() == "test":
            batch_test(games_raw, positions, rawg_data)
            continue

        match = None
        for game in games_raw:
            if game["name"].lower() == user_input.lower():
                match = game
                break

        if match is None:
            print(f"Game '{user_input}' not found. Try another name.\n")
            continue

        results = recommend(match["id"], games_raw, positions, rawg_data)

        print(f"\nSimilar to {match['name']}:")
        for i, (name, score) in enumerate(results, 1):
            print(f"  {i}. {name} (similarity: {score:.3f})")
        print()

if __name__ == "__main__":
    main()