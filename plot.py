"""Plot reputation trajectories and accuracy for the spike report."""
import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

with open(os.path.join(OUT, "reputation_log.csv")) as f:
    rows = list(csv.DictReader(f))

scenarios = sorted({r["scenario"] for r in rows}, key=lambda s: ["control", "attack + plain", "reputation-weighted"].index(next(k for k in ["control", "attack + plain", "reputation-weighted"] if k in s)))
colors = {0: "#2e7d32", 1: "#1565c0", 2: "#f9a825", 3: "#c62828"}

fig, axes = plt.subplots(2, len(scenarios), figsize=(13, 7), sharey="row")

for col, sc in enumerate(scenarios):
    srows = sorted([r for r in rows if r["scenario"] == sc], key=lambda r: int(r["round"]))
    rounds = [int(r["round"]) for r in srows]

    # Top row: reputation trajectories
    ax = axes[0][col]
    for n in range(4):
        ax.plot(rounds, [float(r[f"rep_node_{n}"]) for r in srows],
                marker="o", ms=3, color=colors[n],
                label=f"node {n} (malicious)" if n == 3 and "attack" in sc else f"node {n}")
    ax.axhline(0.5, color="gray", ls="--", lw=1)
    ax.set_title(sc, fontsize=10)
    ax.set_xlabel("FL round")
    if col == 0:
        ax.set_ylabel("reputation score")
    ax.legend(fontsize=7)

    # Bottom row: global accuracy
    ax = axes[1][col]
    ax.plot(rounds, [float(r["global_accuracy"]) for r in srows], marker="s", ms=3, color="black")
    ax.set_ylim(0.45, 1.02)
    ax.set_xlabel("FL round")
    if col == 0:
        ax.set_ylabel("global accuracy (held-out)")

fig.suptitle("Node reputation tracking across 10 federated rounds (4 nodes, 1 malicious in attack scenarios)", fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "spike_results.png"), dpi=150)
print("saved", os.path.join(OUT, "spike_results.png"))
