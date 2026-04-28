import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar
import recommend
import encoding
import numpy as np
from sklearn.neighbors import NearestNeighbors

class GameRecommenderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Game Recommender")
        self.root.geometry("550x650")
        self.load_data()

        tk.Label(root, text="What are some games you have played in the past? (one per line): ", font=("Comic")).pack(pady=10)
        self.text_entry = tk.Text(root, height=10, width=60)
        self.text_entry.pack(pady=5)

        tk.Button(root, text="Recommend similar games", command=self.get_recommendations,bg="#d61c1c", fg="white").pack(pady=10)

        self.unknown_label = tk.Label(root, text="", fg="black", wraplength=500)
        self.unknown_label.pack()

        tk.Label(root, text="Recommended Games: ", font=("Comic", 12, "bold")).pack(pady=5)
        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = Listbox(frame, yscrollcommand=scrollbar.set, height=12,font=("Comic"))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

    def load_data(self):
       self.games_raw = encoding.load_games()
       self.positions = encoding.build_all_positions(self.games_raw)

       self.name_to_id = {game["name"].lower(): game["id"] for game in self.games_raw}
       self.rawg_data = None
       data = np.load("cache/embeddings.npz", allow_pickle=True)
       self.embeddings = data["embeddings"]
       self.game_ids = data["game_ids"].tolist()

       self.id_to_embedding_idx = {game_id: idx for idx, game_id in enumerate(self.game_ids)}

       # the model
       self.nn = NearestNeighbors(metric="cosine", algorithm="brute")
       self.nn.fit(self.embeddings)

        
    def get_recommendations(self):
       self.listbox.delete(0, tk.END)
       self.unknown_label.config(text="")

       raw_input = self.text_entry.get("1.0", tk.END).strip()
       if not raw_input:
           messagebox.showwarning("Input Error", "Please enter at least one game.")
           return
       played_games = [line.strip().lower() for line in raw_input.splitlines() if line.strip()]

       valid_ids = []
       unknown_games = []
       for game_name in played_games:
           game_id = self.name_to_id.get(game_name)
           if game_id:
               valid_ids.append(game_id)
           else:
               unknown_games.append(game_name)

       if unknown_games:
           self.unknown_label.config(text="Unknown games: (skipped) " + ", ".join(unknown_games))
       else:
           self.unknown_label.config(text="")

       if not valid_ids:
           self.listbox.insert(tk.END, "No valid games found... maybe check spelling or try different games?")
           return
       all_recommendations = []
       for game_id in valid_ids:
           recs = recommend.recommend(
               game_id,
               self.games_raw,
               self.positions,
               self.rawg_data,
               top_n=20,
           )
           all_recommendations.extend(recs)

       seen = {}
       for name, score in all_recommendations:
           if name not in seen or score > seen[name]:
               seen[name] = score
       played_names = {game["name"] for game in self.games_raw if game["id"] in valid_ids}
       final_recs = [(name,score) for name, score in seen.items() if name not in played_names]
       
       final_recs.sort(key=lambda x: x[1], reverse=True)
       final_recs = final_recs[:20]

       if final_recs:
           for name, score in final_recs:
               self.listbox.insert(tk.END, f"{name} (similarity: {score:.3f})")
       else:
           self.listbox.insert(tk.END, "No recommendations found... maybe try other games?")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameRecommenderGUI(root)
    root.mainloop()