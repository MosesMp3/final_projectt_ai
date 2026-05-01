import matplotlib.pyplot as plt

games = ['Guilty Gear', 'Elden Ring', 'Hollow Knight', 'Overwatch', 'RE4']
cosine = [0.853, 0.879, 0.972, 0.878, 0.798]
neural = [0.978, 0.999, 0.999, 0.990, 0.991]

x = range(len(games))
plt.figure(figsize=(10, 5))
plt.bar([i - 0.2 for i in x], cosine, width=0.4, label='Cosine Similarity', color='steelblue')
plt.bar([i + 0.2 for i in x], neural, width=0.4, label='Neural Autoencoder', color='teal')
plt.xticks(x, games, rotation=15)
plt.ylabel('Top-1 Similarity Score')
plt.title('Cosine vs Neural Autoencoder: Top-1 Similarity Scores')
plt.legend()
plt.ylim(0, 1.1)
plt.tight_layout()
plt.savefig('method_comparison.png')
plt.show()