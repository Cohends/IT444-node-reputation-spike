# Technical Spike: Server-side node-reputation tracking in federated learning

IT 444 Capstone (Team 2, Lee-2) — Dylan Cohen's individual technical spike.

**Question:** Can the Flower server maintain a rolling reputation score for each edge node, keep a malicious node's score clearly below every honest node's over 10 federated rounds, and use those scores to protect the global model?

## What this is

Four simulated edge nodes (three honest, one malicious) train a small NumPy
logistic-regression "detector" on synthetic real-vs-fake data using Flower's
simulator. The malicious node runs a classic model-poisoning attack: it
submits an honest-looking update that is sign-flipped and amplified 5x.

A custom `ReputationFedAvg` strategy extends FedAvg:

- Each round, the server computes every client's update distance from the
  coordinate-wise **median** of all updates (the robust-consensus idea behind
  Krum / trimmed-mean).
- Round score `s = 2*d_ref/(d_ref + d_i)` capped at 1.0; reputation is an EMA
  (alpha = 0.3); a node is flagged when reputation < 0.5.
- Optionally, updates are aggregated **weighted by reputation** instead of
  plain averaging.

## Pass marks (set before running)

- P1: malicious node's final reputation >= 0.2 below every honest node's
- P2: no honest node flagged in more than 2 of 10 rounds
- P3: with reputation-weighted aggregation, final accuracy within 0.05 of the
  honest-only control

## Results (all passed)

| Scenario | Final accuracy | Malicious rep | Min honest rep |
|---|---|---|---|
| Control (no attacker) | 0.997 | — | 0.854 |
| Attack + plain FedAvg | 0.940 | 0.067 | 0.804 |
| Attack + reputation-weighted | 0.970 | 0.067 | 0.802 |

The malicious node was flagged from round 3 onward; honest nodes were never
flagged. Poisoning cost plain FedAvg 5.7 accuracy points; reputation
weighting recovered 3 of them.

## Run it

```bash
pip install -r requirements.txt
python3 spike.py      # runs all three scenarios, ~30 s, writes out/reputation_log.csv
python3 plot.py       # writes out/spike_results.png
```

Everything is seeded (SEED = 42), so runs are reproducible.

## Files

- `spike.py` — the experiment (clients, attack, reputation strategy, scenarios)
- `plot.py` — generates the results figure
- `out/reputation_log.csv` — per-round reputation, distances, flags, accuracy
- `out/run_log.txt` — full console output of a run
- `out/spike_results.png` — figure used in the report

## Limits (honest substitution notes)

- Ran on a laptop in Flower's simulator — the Pi 5 / Orin edge devices are not
  purchased yet, so no real network, no device heterogeneity, no timing data.
- Synthetic Gaussian data and a logistic-regression model, not real
  AV-Deepfake1M frames and not the team's real detector.
- One attack type (sign-flip amplification). Stealthier attacks (e.g.,
  scaled-but-honest-looking updates) are untested.
