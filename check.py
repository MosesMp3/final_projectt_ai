import json

with open("cache/rawg_data.json") as f:
    rawg_data = json.load(f)

# show first 5 games
for name, data in list(rawg_data.items())[:5]:
    print(f"{name}: {data}")