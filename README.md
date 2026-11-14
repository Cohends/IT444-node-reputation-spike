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

- `Cohen_Dylan_Spike.pdf` and `Cohen_Dylan_Spike.docx`: updated two-page report
  reflecting the successful Windows laptop run.
- `Windows_Run_Evidence.png`: laptop PowerShell screenshot showing all checks
  passed and confirming that `plot.py` generated the results figure.
- `spike.py` — the experiment (clients, attack, reputation strategy, scenarios)
- `plot.py` — generates the results figure
- `out/reputation_log.csv` — per-round reputation, distances, flags, accuracy
- `out/run_log.txt` — full console output of a run
- `out/spike_results.png` — figure used in the report

## Evidence provenance

The files currently committed under `out/` are the original sandbox outputs,
not files collected from the Windows laptop. The laptop screenshot confirms
the same rounded final accuracies (0.997, 0.940, 0.970) and passing checks.
The actual laptop `my_run_log.txt`, `out/reputation_log.csv`, and
`out/spike_results.png` have not yet been uploaded to this repository.
They should be stored separately from the sandbox outputs when available.

The exact Windows, Python, and installed package versions for the laptop run
have not yet been recorded here. The experiment used synthetic data and does
not establish accuracy or security performance on real deepfake media.

## Limits (honest substitution notes)

- The initial trials ran in a cloud sandbox; the user then ran the spike
  successfully on a Windows laptop using Flower's simulator. Neither run
  measures real edge-device networking, device heterogeneity, or timing.
- Synthetic Gaussian data and a logistic-regression model, not real
  AV-Deepfake1M frames and not the team's real detector.
- One attack type (sign-flip amplification). Stealthier attacks (e.g.,
  scaled-but-honest-looking updates) are untested.
