"""Best introduction path between two actors."""

import networkx as nx

from .centrality import domain_graph


def best_introduction_path(graph, source, target, domain):
    """Dijkstra on cost = 1 / (strength + 1e-6) in the chosen domain.

    Returns ``(path, mean_strength)``, or ``(None, 0.0)`` if no path exists.
    """
    h = domain_graph(graph, domain)
    try:
        path = nx.dijkstra_path(h, source, target, weight="cost")
    except nx.NetworkXNoPath:
        return None, 0.0
    strengths = [h[u][v]["weight"] for u, v in zip(path, path[1:])]
    mean = sum(strengths) / len(strengths) if strengths else 0.0
    return path, mean
