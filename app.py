from flask import Flask, render_template, request, jsonify
from recommend import recommend, build_index
import numpy as np
import ollama

app = Flask(__name__)

# load embeddings
data = np.load("cache/embeddings.npz", allow_pickle=True)
embeddings = data["embeddings"]
game_ids = data["game_ids"]
game_names = data["game_names"]

id_to_idx = {int(gid): i for i, gid in enumerate(game_ids)}
nn_index = build_index(embeddings)

def find_game(user_input):
    for gid, idx in id_to_idx.items():
        if str(game_names[idx]).lower() == user_input.lower():
            return gid, str(game_names[idx])
    matches = []
    for gid, idx in id_to_idx.items():
        if user_input.lower() in str(game_names[idx]).lower():
            matches.append((gid, str(game_names[idx])))
    return matches[0] if matches else (None, None)

def similarity_label(score):
    if score >= 0.95:
        return "Extremely similar"
    elif score >= 0.85:
        return "Very similar"
    elif score >= 0.75:
        return "Similar"
    else:
        return "Somewhat similar"

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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def get_recommendations():
    body = request.json
    game_name = body.get("game", "")
    game_name2 = body.get("game2", "")
    traits = body.get("traits", "")
    k = int(body.get("k", 5))
    use_llm = body.get("use_llm", False)

    match_id, matched_name = find_game(game_name)
    if match_id is None:
        return jsonify({"error": f"Game '{game_name}' not found"}), 404

    recs1 = recommend(match_id, nn_index, embeddings, game_ids, game_names, id_to_idx, k=20)

    # if second game provided find intersection
    if game_name2:
        match_id2, matched_name2 = find_game(game_name2)
        if match_id2:
            recs2 = recommend(match_id2, nn_index, embeddings, game_ids, game_names, id_to_idx, k=20)

            recs1_map = {r['name']: r for r in recs1}
            recs2_map = {r['name']: r for r in recs2}
            common = set(recs1_map.keys()) & set(recs2_map.keys())

            if common:
                combined = []
                for name in common:
                    avg_score = (recs1_map[name]['similarity'] + recs2_map[name]['similarity']) / 2
                    combined.append({
                        'name': name,
                        'id': recs1_map[name]['id'],
                        'similarity': round(avg_score, 3)
                    })
                recs = sorted(combined, key=lambda x: x['similarity'], reverse=True)[:k]
                matched_name = f"{matched_name} + {matched_name2}"
            else:
                recs = recs1[:k]
                matched_name = f"{matched_name} (no overlap found with {matched_name2})"
        else:
            recs = recs1[:k]
    else:
        recs = recs1[:k]

    results = []
    for r in recs:
        results.append({
            "name": r["name"],
            "similarity": round(r["similarity"], 3),
            "label": similarity_label(r["similarity"])
        })

    explanation = None
    if use_llm and traits:
        explanation = get_llm_explanation(matched_name, traits, recs)

    return jsonify({
        "input_game": matched_name,
        "recommendations": results,
        "explanation": explanation
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)