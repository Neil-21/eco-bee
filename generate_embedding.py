# generate_embeddings.py
import networkx as nx
from node2vec import Node2Vec
import json

# Seed actions (same as your TS actions)
actions = [
    {"id": "a1", "domain": "swap"},
    {"id": "a2", "domain": "repair"},
    {"id": "a3", "domain": "veggie"},
    {"id": "a4", "domain": "transport"},
]

# Build graph
G = nx.Graph()
for a in actions:
    G.add_node(a["id"], domain=a["domain"])

# Connect nodes of same domain
for i in range(len(actions)):
    for j in range(i+1, len(actions)):
        if actions[i]["domain"] == actions[j]["domain"]:
            G.add_edge(actions[i]["id"], actions[j]["id"])

# Node2Vec
node2vec = Node2Vec(G, dimensions=8, walk_length=10, num_walks=50, workers=1)
model = node2vec.fit(window=5, min_count=1, batch_words=4)

# Save embeddings
embeddings = {node: model.wv[node].tolist() for node in G.nodes()}
with open("embeddings.json", "w") as f:
    json.dump(embeddings, f, indent=2)

print("Embeddings saved to embeddings.json")
