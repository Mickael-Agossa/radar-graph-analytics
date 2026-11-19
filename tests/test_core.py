import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from radar import (
    DOMAINS,
    best_introduction_path,
    detect_coalitions,
    generate_network,
    influence_scores,
    top_k,
)


@pytest.fixture(scope="module")
def graph():
    return generate_network(n=80, seed=7)


def test_graph_size_and_attributes(graph):
    assert graph.number_of_nodes() == 80
    assert graph.number_of_edges() > 0
    for _, _, data in graph.edges(data=True):
        assert all(0.0 <= data[d] <= 1.0 for d in DOMAINS)


def test_generation_is_reproducible():
    a, b = generate_network(n=50, seed=1), generate_network(n=50, seed=1)
    assert sorted(a.edges) == sorted(b.edges)


@pytest.mark.parametrize("domain", DOMAINS)
def test_scores_in_unit_interval(graph, domain):
    scores = influence_scores(graph, domain)
    assert set(scores) == set(graph.nodes)
    assert all(0.0 <= s <= 1.0 for s in scores.values())
    assert max(scores.values()) == pytest.approx(1.0)


def test_top_k_sorted(graph):
    top = top_k(graph, "culture", k=5)
    assert len(top) == 5
    assert [s for _, s in top] == sorted((s for _, s in top), reverse=True)


def test_path_is_valid(graph):
    path, strength = best_introduction_path(graph, "Acteur_001", "Acteur_060", "sante")
    assert path[0] == "Acteur_001" and path[-1] == "Acteur_060"
    assert all(graph.has_edge(u, v) for u, v in zip(path, path[1:]))
    assert 0.0 < strength <= 1.0


def test_partition_covers_all_nodes(graph):
    coalitions, q = detect_coalitions(graph, seed=42)
    covered = [n for c in coalitions for n in c]
    assert sorted(covered) == sorted(graph.nodes)
    assert len(covered) == len(set(covered))
    assert -0.5 <= q <= 1.0
