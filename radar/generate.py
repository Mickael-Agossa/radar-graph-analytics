"""Synthetic relationship network generator (stochastic block model)."""

import random

import networkx as nx

DOMAINS = ("economie", "securite", "culture", "sante", "education")
ACTOR_TYPES = ("organisation", "entreprise", "association", "expert", "collectivite")


def generate_network(n=200, n_communities=5, p_in=0.15, p_out=0.01, seed=42):
    """Build an undirected graph of ``n`` actors grouped into communities.

    Each edge carries one strength in [0, 1] per domain. Every community has a
    dominant domain in which its internal ties tend to be stronger.
    """
    rng = random.Random(seed)
    sizes = [n // n_communities] * n_communities
    for i in range(n % n_communities):
        sizes[i] += 1
    probs = [
        [p_in if i == j else p_out for j in range(n_communities)]
        for i in range(n_communities)
    ]
    g = nx.stochastic_block_model(sizes, probs, seed=seed)
    g = nx.relabel_nodes(g, {i: f"Acteur_{i + 1:03d}" for i in g.nodes})

    for _, data in g.nodes(data=True):
        data["type"] = rng.choice(ACTOR_TYPES)

    for u, v, data in g.edges(data=True):
        same = g.nodes[u]["block"] == g.nodes[v]["block"]
        dominant = g.nodes[u]["block"] % len(DOMAINS)
        for k, domain in enumerate(DOMAINS):
            base = 0.65 if (same and k == dominant) else 0.25
            data[domain] = round(min(1.0, max(0.0, rng.gauss(base, 0.15))), 3)
    return g
