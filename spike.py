"""
Technical Spike: Can the FL server track per-node reputation across rounds?

Question: Can the Flower server maintain a rolling reputation score for each
edge node, keep a malicious node's score clearly below every honest node's
over 10 federated rounds, and use those scores to protect the global model?

Setup: 4 simulated clients (3 honest, 1 malicious) training a small NumPy
logistic-regression "detector" on synthetic data. Real edge hardware is not
available yet, so this runs in Flower's simulator on a laptop.

Attack simulated: classic model poisoning — the malicious node submits an
honest-looking update that is sign-flipped and amplified 5x.

Reputation rule (defined BEFORE running, per spike rules):
  Each round, the server computes each client's update distance from the
  coordinate-wise MEDIAN of all client updates (a robust consensus reference,
  the same idea behind Krum / trimmed-mean). Round score
  s_i = 2*d_ref / (d_ref + d_i), capped at 1.0, so a node near the consensus
  scores ~1 and a node far from it scores near 0. Reputation is an EMA
  (alpha=0.3) of round scores, starting at 1.0. A node is flagged when its
  reputation falls below 0.5.

Pass marks (set before testing):
  P1: After 10 rounds, the malicious node's reputation is >= 0.2 lower than
      every honest node's (in both attack scenarios).
  P2: No honest node is flagged (rep < 0.5) in more than 2 of 10 rounds.
  P3: With reputation-weighted aggregation, final global accuracy is within
      0.05 of the honest-only control.

Scenarios:
  control  : 4 honest nodes, plain FedAvg (baseline accuracy)
  attack   : 3 honest + 1 malicious, plain FedAvg (reputation observed only)
  defended : 3 honest + 1 malicious, aggregation weighted by reputation
"""

import csv
import os

import flwr as fl
import numpy as np
from flwr.common import ndarrays_to_parameters, parameters_to_ndarrays

SEED = 42
NUM_CLIENTS = 4
NUM_ROUNDS = 10
MALICIOUS_ID = 3
ALPHA = 0.3
FLAG_THRESHOLD = 0.5
N_FEATURES = 20
N_SAMPLES_PER_CLIENT = 300
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


# ---------------------------------------------------------------- data & model
def make_client_data(client_id: int, shift: float = None):
    """Synthetic 'real vs fake' data. Honest clients get a mild distribution
    shift (non-IID), so they legitimately disagree a little."""
    crng = np.random.default_rng(SEED + client_id)
    if shift is None:
        shift = 0.3 * (client_id - 1.5) if client_id < 10 else 0.0
    n = N_SAMPLES_PER_CLIENT // 2
    x0 = crng.normal(-0.55 + shift, 1.0, (n, N_FEATURES))
    x1 = crng.normal(0.55 + shift, 1.0, (n, N_FEATURES))
    X = np.vstack([x0, x1])
    y = np.array([0] * n + [1] * n)
    idx = crng.permutation(len(y))
    return X[idx], y[idx]


def init_params():
    return [np.zeros(N_FEATURES), np.array([0.0])]


def train_logreg(X, y, w, b, epochs=3, lr=0.1, l2=1e-3):
    for _ in range(epochs):
        z = X @ w + b
        p = 1.0 / (1.0 + np.exp(-z))
        err = p - y
        w -= lr * (X.T @ err / len(y) + l2 * w)
        b -= lr * err.mean()
    return w, b


def accuracy(X, y, w, b):
    pred = (X @ w + b) >= 0
    return float((pred == y).mean())


EVAL_X, EVAL_Y = make_client_data(999)  # fixed held-out set for all scenarios

# ------------------------------------------------------------------- clients
class DetectorClient(fl.client.NumPyClient):
    def __init__(self, cid: int, malicious: bool):
        self.cid = cid
        self.malicious = malicious
        self.X, self.y = make_client_data(cid)
        self.noise_rng = np.random.default_rng(SEED + 777)

    def get_parameters(self, config):
        return init_params()

    def fit(self, parameters, config):
        w, b = parameters
        w_new, b_new = train_logreg(self.X, self.y, w, b)
        update_w, update_b = w_new - w, b_new - b
        if self.malicious:
            # Model poisoning: sign-flip and amplify the honest-looking update.
            update_w = -5.0 * update_w + 0.5 * self.noise_rng.normal(size=w.shape)
            update_b = -5.0 * update_b
            w_new, b_new = w + update_w, b + update_b
        return [w_new, b_new], len(self.y), {"cid": float(self.cid)}


# ------------------------------------------------- strategy with reputation
class ReputationFedAvg(fl.server.strategy.FedAvg):
    """FedAvg plus per-node reputation tracking. If use_reputation_weights is
    True, client updates are aggregated weighted by current reputation."""

    def __init__(self, *args, use_reputation_weights=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_reputation_weights = use_reputation_weights
        self.current = [np.zeros(N_FEATURES), np.array([0.0])]
        self.reputation = {i: 1.0 for i in range(NUM_CLIENTS)}
        self.flagged = {i: 0 for i in range(NUM_CLIENTS)}
        self.history = []

    def aggregate_fit(self, server_round, results, failures):
        if not results:
            return None, {}
        # 1) Updates relative to the current global model.
        updates = {}
        for _proxy, fit_res in results:
            cid = int(fit_res.metrics.get("cid", -1)) if fit_res.metrics else -1
            params = parameters_to_ndarrays(fit_res.parameters)
            updates[cid] = [p - g for p, g in zip(params, self.current)]

        # 2) Robust consensus reference: coordinate-wise median of updates.
        flat = {c: np.concatenate([u.ravel() for u in ups]) for c, ups in updates.items()}
        stack = np.vstack([flat[c] for c in sorted(flat)])
        median_upd = np.median(stack, axis=0)
        dist = {c: float(np.linalg.norm(flat[c] - median_upd)) for c in flat}
        d_ref = float(np.median(list(dist.values())))

        # 3) Round score -> EMA reputation -> flag.
        for cid in sorted(self.reputation):
            if cid in dist:
                s = min(1.0, 2.0 * d_ref / (d_ref + dist[cid])) if dist[cid] > 0 else 1.0
                self.reputation[cid] = ALPHA * s + (1 - ALPHA) * self.reputation[cid]
                if self.reputation[cid] < FLAG_THRESHOLD:
                    self.flagged[cid] += 1

        # 4) Aggregate: plain FedAvg or reputation-weighted.
        if self.use_reputation_weights:
            weights = {c: max(self.reputation[c], 1e-3) for c in updates}
            total = sum(weights.values())
            agg = [
                sum(weights[c] / total * updates[c][i] for c in sorted(updates))
                for i in range(len(self.current))
            ]
        else:
            agg = [
                np.mean([updates[c][i] for c in sorted(updates)], axis=0)
                for i in range(len(self.current))
            ]
        self.current = [g + a for g, a in zip(self.current, agg)]

        row = {"round": server_round}
        for c in sorted(self.reputation):
            row[f"rep_node_{c}"] = round(self.reputation[c], 4)
            row[f"dist_node_{c}"] = round(dist.get(c, float("nan")), 4)
            row[f"flag_node_{c}"] = int(self.reputation[c] < FLAG_THRESHOLD)
        self.history.append(row)
        return ndarrays_to_parameters(self.current), {}

    def evaluate(self, server_round, parameters):
        if server_round == 0:
            return None
        w, b = parameters_to_ndarrays(parameters)
        acc = accuracy(EVAL_X, EVAL_Y, w, b)
        self.history[-1]["global_accuracy"] = round(acc, 4)
        return float(1.0 - acc), {"accuracy": acc}


# --------------------------------------------------------------------- run
def client_fn_factory(malicious_id):
    def client_fn(cid: str):
        cid = int(cid)
        return DetectorClient(cid, malicious=(cid == malicious_id)).to_client()
    return client_fn


def run_scenario(name, malicious_id, use_reputation_weights):
    strategy = ReputationFedAvg(
        fraction_fit=1.0,
        min_fit_clients=NUM_CLIENTS,
        min_available_clients=NUM_CLIENTS,
        initial_parameters=ndarrays_to_parameters(init_params()),
        use_reputation_weights=use_reputation_weights,
    )
    client_app = fl.client.ClientApp(client_fn=client_fn_factory(malicious_id))
    server_app = fl.server.ServerApp(
        config=fl.server.ServerConfig(num_rounds=NUM_ROUNDS), strategy=strategy
    )
    fl.simulation.run_simulation(
        server_app=server_app, client_app=client_app,
        num_supernodes=NUM_CLIENTS, backend_name="ray",
    )

    final = strategy.reputation
    honest = [c for c in final if c != malicious_id] if malicious_id is not None else list(final)
    row = {
        "scenario": name,
        "final_accuracy": strategy.history[-1]["global_accuracy"],
        "malicious_final_rep": final.get(malicious_id, None),
        "min_honest_final_rep": min(final[c] for c in honest),
        "max_honest_flagged_rounds": max(strategy.flagged[c] for c in honest),
        "malicious_flagged_rounds": strategy.flagged.get(malicious_id, 0),
    }
    print(f"\n--- scenario {name} ---")
    print(f"final reputation: " + " ".join(f"n{c}={final[c]:.3f}" for c in sorted(final)))
    print(f"final accuracy on held-out data: {row['final_accuracy']:.3f}")
    for r in strategy.history:
        print(f"  round {r['round']:2d}: acc={r.get('global_accuracy', float('nan')):.3f} "
              + " ".join(f"rep{n}={r[f'rep_node_{n}']:.2f}" for n in sorted(strategy.reputation)))
    return row, strategy.history


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    summary, all_logs = [], []
    for name, mid, weighted in [
        ("control (no attacker)", None, False),
        ("attack + plain FedAvg", MALICIOUS_ID, False),
        ("attack + reputation-weighted", MALICIOUS_ID, True),
    ]:
        row, history = run_scenario(name, mid, weighted)
        summary.append(row)
        for h in history:
            h["scenario"] = name
        all_logs.extend(history)

    with open(os.path.join(OUT_DIR, "reputation_log.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_logs[0].keys()))
        w.writeheader()
        w.writerows(all_logs)

    acc = {r["scenario"]: r["final_accuracy"] for r in summary}
    attack = next(r for r in summary if "plain" in r["scenario"])
    defended = next(r for r in summary if "reputation-weighted" in r["scenario"])

    print("\n=== SPIKE VERDICT ===")
    for r in summary:
        print(f"{r['scenario']:30s} final acc={r['final_accuracy']:.3f} "
              f"malicious rep={r['malicious_final_rep']} "
              f"min honest rep={r['min_honest_final_rep']}")

    def check(label, ok):
        print(f"{label}: {'PASS' if ok else 'FAIL'}")

    for r in [attack, defended]:
        check(f"P1 ({r['scenario']}): malicious >= 0.2 below every honest node",
              r["malicious_final_rep"] is not None
              and r["malicious_final_rep"] <= r["min_honest_final_rep"] - 0.2)
    check("P2: no honest node flagged more than 2/10 rounds (attack scenarios)",
          max(attack["max_honest_flagged_rounds"], defended["max_honest_flagged_rounds"]) <= 2)
    check("P3: defended final accuracy within 0.05 of control",
          abs(defended["final_accuracy"] - acc["control (no attacker)"]) <= 0.05)
    print("log saved to out/reputation_log.csv")


if __name__ == "__main__":
    main()
