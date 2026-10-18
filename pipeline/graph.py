from __future__ import annotations
import pandas as pd
import numpy as np
import networkx as nx
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

FEATURES = ["avg_duration", "avg_calories", "avg_heart_rate", "avg_sleep",
            "avg_steps", "avg_stress", "avg_fitness_level"]

def build_similarity_graph(profiles: pd.DataFrame, neighbors: int = 4):
    """Build sparse similarity edges within dominant-activity groups."""
    p = profiles.copy()
    for c in FEATURES:
        p[c] = pd.to_numeric(p[c], errors="coerce")
        p[c] = p[c].replace([np.inf, -np.inf], np.nan)
        p[c] = p[c].fillna(p[c].median())
    p["dominant_activity"] = p["dominant_activity"].fillna("Unknown")
    pairs = {}
    for activity, group in p.groupby("dominant_activity"):
        if len(group) < 2:
            continue
        X = StandardScaler().fit_transform(group[FEATURES])
        k = min(neighbors + 1, len(group))
        model = NearestNeighbors(n_neighbors=k, metric="euclidean").fit(X)
        distances, indices = model.kneighbors(X)
        ids = group["participant_id"].astype(int).tolist()
        for i, neighbors_idx in enumerate(indices):
            for distance, j in zip(distances[i][1:], neighbors_idx[1:]):
                a, b = sorted((ids[i], ids[int(j)]))
                weight = float(1.0 / (1.0 + distance))
                key = (a, b)
                if key not in pairs or weight > pairs[key]["weight"]:
                    pairs[key] = {"source": a, "target": b, "weight": weight,
                                  "shared_activity": str(activity)}
    edges = pd.DataFrame(pairs.values(), columns=["source", "target", "weight", "shared_activity"])
    graph = nx.Graph()
    for row in p.to_dict(orient="records"):
        graph.add_node(int(row["participant_id"]), activity=str(row["dominant_activity"]))
    for edge in pairs.values():
        graph.add_edge(edge["source"], edge["target"], weight=edge["weight"])
    degree = nx.degree_centrality(graph)
    # Betweenness on 3,000 nodes can be expensive; approximate deterministically.
    between = nx.betweenness_centrality(graph, k=min(100, graph.number_of_nodes()), seed=42, weight="weight")
    metrics = pd.DataFrame({
        "participant_id": list(graph.nodes()),
        "degree_centrality": [degree[n] for n in graph.nodes()],
        "betweenness_centrality": [between[n] for n in graph.nodes()],
    })
    try:
        communities = nx.community.louvain_communities(graph, weight="weight", seed=42)
        community_map = {node: i + 1 for i, community in enumerate(communities) for node in community}
    except Exception:
        community_map = {node: 1 for node in graph.nodes()}
    metrics["community_id"] = metrics["participant_id"].map(community_map).fillna(1).astype(int)
    return edges, metrics, graph
