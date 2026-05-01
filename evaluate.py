import json
import numpy as np
from sklearn.neighbors import NearestNeighbors


def load_eval_data():
    data = np.load("cache/embeddings.npz", allow_pickle=True)
    embeddings = data["embeddings"]
    game_ids = data["game_ids"]
    game_names = data["game_names"]

    with open("cache/similar_truth.json") as f:
        truth_raw = json.load(f)
    truth = {int(k): set(v) for k, v in truth_raw.items()}

    return embeddings, game_ids, game_names, truth


def recall_at_k(embeddings, game_ids, truth, k=10):
    catalog_ids = set(int(gid) for gid in game_ids)
    id_to_idx = {int(gid): i for i, gid in enumerate(game_ids)}

    nn_index = NearestNeighbors(n_neighbors=k + 1, metric="cosine")
    nn_index.fit(embeddings)

    recalls = []
    skipped = 0

    for gid in game_ids:
        gid = int(gid)
        true_similars = truth.get(gid, set())
        relevant = true_similars & catalog_ids
        if not relevant:
            skipped += 1
            continue

        idx = id_to_idx[gid]
        _, indices = nn_index.kneighbors(embeddings[idx : idx + 1], n_neighbors=k + 1)
        recommended = {int(game_ids[i]) for i in indices[0][1:]}

        hits = len(recommended & relevant)
        recall = hits / len(relevant)
        recalls.append(recall)

    return {
        "recall_at_k": np.mean(recalls),
        "k": k,
        "n_evaluated": len(recalls),
        "n_skipped": skipped,
    }


def per_game_recall(embeddings, game_ids, game_names, truth, k=10):
    catalog_ids = set(int(gid) for gid in game_ids)
    id_to_idx = {int(gid): i for i, gid in enumerate(game_ids)}

    nn_index = NearestNeighbors(n_neighbors=k + 1, metric="cosine")
    nn_index.fit(embeddings)

    results = []
    for gid in game_ids:
        gid = int(gid)
        relevant = truth.get(gid, set()) & catalog_ids
        if not relevant:
            continue

        idx = id_to_idx[gid]
        _, indices = nn_index.kneighbors(embeddings[idx : idx + 1], n_neighbors=k + 1)
        recommended = [int(game_ids[i]) for i in indices[0][1:]]
        hits = set(recommended) & relevant

        results.append(
            {
                "game": str(game_names[idx]),
                "n_relevant": len(relevant),
                "n_hits": len(hits),
                "recall": len(hits) / len(relevant),
            }
        )

    return sorted(results, key=lambda x: -x["recall"])


embeddings, game_ids, game_names, truth = load_eval_data()

print("=" * 60)
print("Recall@K evaluation (IGDB ground truth)")
print("=" * 60)
for k in [5, 10, 20]:
    result = recall_at_k(embeddings, game_ids, truth, k=k)
    print(
        f"  Recall@{k:2d}: {result['recall_at_k']:.4f}  "
        f"({result['n_evaluated']} evaluated, {result['n_skipped']} skipped)"
    )

print("\n" + "=" * 60)
print("Top 10 best-recalled games:")
print("=" * 60)
per_game = per_game_recall(embeddings, game_ids, game_names, truth, k=10)
for r in per_game[:10]:
    print(f"  {r['recall']:.2f}  {r['game']:<40} ({r['n_hits']}/{r['n_relevant']})")

print("\n" + "=" * 60)
print("Worst-recalled games (where the model fails):")
print("=" * 60)
for r in per_game[-10:]:
    print(f"  {r['recall']:.2f}  {r['game']:<40} ({r['n_hits']}/{r['n_relevant']})")

# ── RAWG evaluation ──
import os
rawg_truth_path = "cache/rawg_similar_truth.json"
if os.path.exists(rawg_truth_path):
    with open(rawg_truth_path) as f:
        rawg_truth_raw = json.load(f)
    rawg_truth = {int(k): set(v) for k, v in rawg_truth_raw.items()}

    print("\n" + "=" * 60)
    print("Recall@K evaluation (RAWG ground truth)")
    print("=" * 60)
    for k in [5, 10, 20]:
        result = recall_at_k(embeddings, game_ids, rawg_truth, k=k)
        print(
            f"  Recall@{k:2d}: {result['recall_at_k']:.4f}  "
            f"({result['n_evaluated']} evaluated, {result['n_skipped']} skipped)"
        )

    print("\n" + "=" * 60)
    print("Top 10 best-recalled games (RAWG):")
    print("=" * 60)
    per_game_rawg = per_game_recall(embeddings, game_ids, game_names, rawg_truth, k=10)
    for r in per_game_rawg[:10]:
        print(f"  {r['recall']:.2f}  {r['game']:<40} ({r['n_hits']}/{r['n_relevant']})")

    print("\n" + "=" * 60)
    print("Worst-recalled games (RAWG):")
    print("=" * 60)
    for r in per_game_rawg[-10:]:
        print(f"  {r['recall']:.2f}  {r['game']:<40} ({r['n_hits']}/{r['n_relevant']})")
else:
    print("\nRAWG truth not found — run rawg_match.py and rawg_similar.py first")