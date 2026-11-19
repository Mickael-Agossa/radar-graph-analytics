"""Coalition detection with the Louvain method."""

from networkx.algorithms.community import louvain_communities, modularity

from .centrality import domain_graph


def detect_coalitions(graph, domain=None, seed=42, resolution=1.0):
    """Return ``(coalitions, modularity)``.

    If ``domain`` is given, communities are computed on that domain's weighted
    graph; otherwise on the unweighted structure. Coalitions are sorted by size.
    """
    if domain is None:
        h, weight = graph, None
    else:
        h, weight = domain_graph(graph, domain), "weight"
    comms = louvain_communities(h, weight=weight, resolution=resolution, seed=seed)
    comms = sorted((set(c) for c in comms), key=len, reverse=True)
    return comms, modularity(h, comms, weight=weight)
