# Technical Spike: Server-side node-reputation tracking in federated learning

IT 444 Capstone (Team 2, LEE2-B): Dylan Cohen's individual technical spike.

**D4 question:** Can the federated learning server accurately track and update the reputation of individual edge nodes across multiple training rounds to identify potentially malicious model updates?

Repository: [IT444-node-reputation-spike](https://github.com/Cohends/IT444-node-reputation-spike).
The final submission is [Cohen_Dylan_Spike.pdf](Cohen_Dylan_Spike.pdf);
[Cohen_Dylan_Spike.docx](Cohen_Dylan_Spike.docx) is the editable copy.

## What this is

Four simulated edge nodes train small NumPy logistic-regression models on
synthetic binary-classification data using Flower's simulator. The control
has four honest nodes; each attack scenario has three honest nodes and one
malicious node. The attacker sign-flips and amplifies its weight update 5x
and adds noise. Each scenario runs for 10 rounds.

A custom `ReputationFedAvg` strategy extends FedAvg:

- Each round, the server computes every client's update distance from the
  coordinate-wise median of all updates as a reference for anomaly scoring.
- Round score `s = 2*d_ref/(d_ref + d_i)` capped at 1.0; reputation is an EMA
  (alpha = 0.3); a node is flagged when reputation < 0.5.
- Optionally, updates are aggregated **weighted by reputation** instead of
  plain averaging.

Reputation tracking across rounds is the main test. Weighting updates by
reputation is an additional experiment. Neither Krum nor Trimmed Mean was
implemented or compared; choosing between them remains a separate D4 task.

## Pass marks used for the laptop run

Exploratory sandbox runs were used to fix errors and adjust the synthetic
data before the laptop run. These criteria were used for the laptop
evaluation; the experiment was not free of preliminary testing.

- P1: malicious node's final reputation at least 0.2 below every honest
  node's, in both attack scenarios.
- P2: no honest node flagged in more than 2 of 10 rounds, in either attack
  scenario.
- P3 (additional): with reputation-weighted aggregation, final accuracy within 0.05 of the
  honest-only control

## Results (all passed)

| Scenario | Final accuracy | Malicious rep | Min honest rep |
|---|---|---|---|
| Control (no attacker) | 0.9967 | Not applicable | 0.8535 |
| Attack + plain FedAvg | 0.9400 | 0.0671 | 0.8045 |
| Attack + reputation-weighted | 0.9700 | 0.0668 | 0.8024 |

These are the recorded Windows laptop results. In both attack scenarios,
the malicious node was flagged from round 3 onward; no honest nodes were
flagged. Weighting improved synthetic-task accuracy by 3 percentage points
over plain FedAvg under attack, but stayed below the honest-only control.
These numbers are not real deepfake-detection accuracy.

## Design choice

Keep the planned reputation-tracking design and the overall architecture.
Reputation weighting is an implementation recommendation to validate with
the real detector and deepfake data, not an architecture change. This test
does not justify changing the requirements or budget, lowering the
security-risk rating, selecting Krum or Trimmed Mean, or claiming that node
blocking was tested.

## Run it

PowerShell, from a new clone:

```powershell
git clone https://github.com/Cohends/IT444-node-reputation-spike.git
Set-Location IT444-node-reputation-spike
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe spike.py
.\.venv\Scripts\python.exe plot.py
```

On Linux or macOS, use a virtual environment, install `requirements.txt`,
then run `python spike.py` and `python plot.py`. New runs write to `out/`
which is generated locally and ignored by Git; the preserved laptop evidence
is under `evidence/windows/`. Run `spike.py` before `plot.py` to create its
input CSV. The experiment uses seed 42, but exact results
may vary across environments. Only Flower is pinned in `requirements.txt`;
the laptop's recorded versions are in `evidence/windows/software_versions.txt`.

## Files

- `Cohen_Dylan_Spike.pdf` and `Cohen_Dylan_Spike.docx`: updated two-page report
  reflecting the successful Windows laptop run.
- `Windows_Run_Evidence.png`: laptop PowerShell screenshot showing all checks
  passed and confirming that `plot.py` generated the results figure.
- `spike.py`: the experiment (clients, attack, reputation strategy, scenarios).
- `plot.py`: generates the results figure from `out/reputation_log.csv`.
- `requirements.txt`: Python dependencies for running the spike and plot.
- `evidence/windows/`: preserved laptop logs, CSV, figure and version record.

## Evidence provenance

The final evidence is the uploaded Windows laptop run in `evidence/windows/`.
Earlier sandbox outputs were removed from the current submission tree to
avoid confusing them with the laptop evidence; they remain in Git history.

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

The repository is private. The reviewer needs repository access to open
the evidence links in the PDF.

## Limits (honest substitution notes)

- The initial trials ran in a cloud sandbox; the user then ran the spike
  successfully on a Windows laptop using Flower's simulator. Neither run
  measures real edge-device networking, device heterogeneity, or timing.
- Synthetic Gaussian data and a logistic-regression model, not real
  AV-Deepfake1M frames and not the team's real detector.
- One attack type (sign-flip amplification). Stealthier attacks (e.g.,
  scaled-but-honest-looking updates) are untested.
