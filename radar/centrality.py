"""Per-domain influence scores from weighted centralities."""

import networkx as nx

from .generate import DOMAINS

EPS = 1e-6
DEFAULT_WEIGHTS = {"degree": 0.4, "betweenness": 0.3, "eigenvector": 0.3}


def domain_graph(graph, domain):
    """Project the multi-domain graph onto one domain.

    Edge attribute ``weight`` is the domain strength; ``cost`` is its inverse,
    used as a distance by shortest-path based measures.
    """
    if domain not in DOMAINS:
        raise ValueError(f"Unknown domain: {domain!r}")
    h = nx.Graph()
    h.add_nodes_from(graph.nodes(data=True))
    for u, v, data in graph.edges(data=True):
        w = float(data.get(domain, 0.0))
        if w > 0:
            h.add_edge(u, v, weight=w, cost=1.0 / (w + EPS))
    return h


def _minmax(values):
    lo, hi = min(values.values()), max(values.values())
    if hi - lo < 1e-12:
        return {k: 0.0 for k in values}
    return {k: (v - lo) / (hi - lo) for k, v in values.items()}


def influence_scores(graph, domain, weights=None):
    """Weighted combination of min-max normalised centralities, in [0, 1]."""
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    total = sum(w.values())
    if total <= 0:
        raise ValueError("Centrality weights must sum to a positive value")
    h = domain_graph(graph, domain)
    parts = {
        "degree": _minmax(dict(h.degree(weight="weight"))),
        "betweenness": _minmax(nx.betweenness_centrality(h, weight="cost")),
        "eigenvector": _minmax(
            nx.eigenvector_centrality(h, weight="weight", max_iter=1000)
        ),
    }
    combined = {
        n: sum(w[k] * parts[k][n] for k in parts) / total for n in h.nodes
    }
    return _minmax(combined)


def top_k(graph, domain, k=10, weights=None):
    """Return the ``k`` most influential actors as (actor, score) pairs."""
    scores = influence_scores(graph, domain, weights)
    return sorted(scores.items(), key=lambda x: (-x[1], x[0]))[:k]
