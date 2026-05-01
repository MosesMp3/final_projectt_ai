from encoding import load_games, build_all_positions
from recommend import recommend, build_index
import numpy as np
import ollama

FIELDS = ["genres", "themes", "game_modes", "player_perspectives", "platforms"]

data = np.load("cache/embeddings.npz", allow_pickle=True)
embeddings = data["embeddings"]
game_ids = data["game_ids"]
game_names = data["game_names"]

id_to_idx = {int(gid): i for i, gid in enumerate(game_ids)}
nn_index = build_index(embeddings)

def similarity_label(score):
    if score >= 0.95:
        return "Extremely similar"
    elif score >= 0.85:
        return "Very similar"
    elif score >= 0.75:
        return "Similar"
    else:
        return "Somewhat similar"

def find_game(user_input, game_names, id_to_idx):
    # exact match first
    for gid, idx in id_to_idx.items():
        if str(game_names[idx]).lower() == user_input.lower():
            return gid, str(game_names[idx])

    # partial match fallback
    matches = []
    for gid, idx in id_to_idx.items():
        if user_input.lower() in str(game_names[idx]).lower():
            matches.append((gid, str(game_names[idx])))

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        print(f"\nMultiple matches found:")
        for i, (gid, name) in enumerate(matches[:5]):
            print(f"  {i+1}. {name}")
        choice = input("Pick a number (or press Enter to cancel): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(matches[:5]):
            return matches[int(choice) - 1]

    return None, None

def get_llm_explanation(input_game, traits, recommendations):
    rec_list = "\n".join([f"- {r['name']} (similarity: {r['similarity']:.3f})"
                          for r in recommendations])
    rec_names = [r['name'] for r in recommendations]

    prompt = f"""Here is a list of exactly {len(rec_names)} games. Discuss ONLY these games, nothing else:
{rec_list}

The user likes "{input_game}" and wants: {traits}

Go through each of the {len(rec_names)} games one by one and explain in one sentence how it relates to "{input_game}" and whether it has "{traits}". Use the exact game names from the list. Do not add any other games."""

    response = ollama.chat(
        model="gamerecommender",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

while True:
    print("\n=== Game Recommender ===")
    user_input = input("Enter a game you like (or 'quit'): ").strip()

    if user_input.lower() == "quit":
        break

    match_id, matched_name = find_game(user_input, game_names, id_to_idx)

    if match_id is None:
        print(f"Game '{user_input}' not found in catalog.")
        continue

    traits = input("What traits are you looking for? (e.g. multiplayer, open world, story-driven): ").strip()

    n = input("How many recommendations? (default 5): ").strip()
    k = int(n) if n.isdigit() else 5

    recs = recommend(match_id, nn_index, embeddings, game_ids, game_names, id_to_idx, k=k)

    print(f"\nTop {k} recommendations for {matched_name}:")
    for r in recs:
        label = similarity_label(r['similarity'])
        print(f"  {r['similarity']:.3f}  {r['name']} — {label}")

    use_llm = input("\nWant an explanation? (y/n): ").strip().lower()
    if use_llm == "y":
        print("\nWhy these games match your request:")
        explanation = get_llm_explanation(matched_name, traits, recs)
        print(explanation)