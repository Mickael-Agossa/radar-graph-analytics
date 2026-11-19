"""End-to-end demo on a synthetic network."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from radar import (
    DOMAINS,
    best_introduction_path,
    detect_coalitions,
    generate_network,
    top_k,
)

OUT = ROOT / "outputs"


def main():
    g = generate_network(n=200, seed=42)
    print(f"Network: {g.number_of_nodes()} actors, {g.number_of_edges()} ties\n")

    for domain in DOMAINS:
        print(f"Top 10 - {domain}")
        for rank, (actor, score) in enumerate(top_k(g, domain, k=10), 1):
            print(f"  {rank:2d}. {actor}  {score:.3f}")
        print()

    src, dst, dom = "Acteur_001", "Acteur_150", "economie"
    path, strength = best_introduction_path(g, src, dst, dom)
    print(f"Best introduction path {src} -> {dst} ({dom}):")
    print("  " + " -> ".join(path) if path else "  no path")
    print(f"  mean strength: {strength:.3f}\n")

    coalitions, q = detect_coalitions(g, seed=42)
    print(f"Coalitions (Louvain): {len(coalitions)}, modularity = {q:.3f}")
    for i, c in enumerate(coalitions):
        print(f"  C{i + 1}: {len(c)} actors")

    OUT.mkdir(exist_ok=True)
    membership = {n: i for i, c in enumerate(coalitions) for n in c}
    pos = nx.spring_layout(g, seed=42)
    fig, ax = plt.subplots(figsize=(9, 9))
    nx.draw_networkx_edges(g, pos, ax=ax, alpha=0.15, width=0.5)
    nx.draw_networkx_nodes(
        g,
        pos,
        ax=ax,
        node_size=40,
        node_color=[membership[n] for n in g.nodes],
        cmap="tab10",
    )
    ax.set_title(f"Synthetic network coloured by coalition (Q = {q:.2f})")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT / "network_coalitions.png", dpi=150)
    plt.close(fig)

    top = top_k(g, dom, k=10)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh([a for a, _ in top][::-1], [s for _, s in top][::-1], color="#2b4c7e")
    ax.set_xlabel("Influence score")
    ax.set_xlim(0, 1)
    ax.set_title(f"Top 10 influence - {dom}")
    fig.tight_layout()
    fig.savefig(OUT / f"top10_{dom}.png", dpi=150)
    plt.close(fig)
    print(f"\nFigures saved to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
