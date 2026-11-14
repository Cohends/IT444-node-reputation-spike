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

The files committed under `out/` are the original sandbox outputs.
The uploaded Windows laptop evidence is stored separately in `evidence/windows/`:

- `my_run_log.txt`: original PowerShell log, preserved in UTF-16.
- `my_run_log_utf8.txt`: the same log converted to UTF-8 for easier reading.
- `reputation_log.csv`: all 30 scenario-round records from the laptop.
- `spike_results.png`: the laptop-generated results figure.
- `software_versions.txt`: versions transcribed from the user's PowerShell output
  after the experiment, using the same virtual environment.

`Windows_Run_Evidence.png` at the repository root is the laptop screenshot.
The uploaded CSV confirms final accuracies of 0.9967, 0.9400, and 0.9700,
with all checks passing. Both attack scenarios first flag the malicious node
in round 3; no honest nodes are flagged.

The full laptop log includes experimental Windows-support and deprecation
warnings, plus a Ray worker "Windows fatal exception" message. All three
scenarios nevertheless report 10 completed rounds and the final verdict is
printed. These runtime messages are retained, not removed or treated as proof
of an error-free run; the underlying worker issue has not been diagnosed.

The versions reported after the laptop run were Windows 11 Pro 64-bit
(10.0.26300, build 26300), PowerShell 5.1.26100.9818, Python 3.14.2,
Flower 1.43.0, Ray 2.60.0, NumPy 2.5.4, and Matplotlib 3.11.2.
These were collected afterward, not captured automatically during the run.
The experiment used synthetic data and does not establish accuracy or
security performance on real deepfake media.

## Limits (honest substitution notes)

- The initial trials ran in a cloud sandbox; the user then ran the spike
  successfully on a Windows laptop using Flower's simulator. Neither run
  measures real edge-device networking, device heterogeneity, or timing.
- Synthetic Gaussian data and a logistic-regression model, not real
  AV-Deepfake1M frames and not the team's real detector.
- One attack type (sign-flip amplification). Stealthier attacks (e.g.,
  scaled-but-honest-looking updates) are untested.
