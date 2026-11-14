# Node-reputation tracking spike

IT 444 Capstone, Team 2 (LEE2-B): Dylan Cohen.

## Question and targets

Can the federated learning server accurately track and update the reputation
of individual edge nodes across multiple training rounds to identify
potentially malicious model updates?

In both attack scenarios, the malicious node's final reputation had to be
at least **0.2 below every honest node's**, with no honest node flagged in
more than **2 of 10 rounds**. An additional test checked whether
reputation-weighted aggregation kept accuracy within **5 percentage points**
of the honest-only control.

## How the test was run

The Windows laptop run used Flower to simulate four nodes training
logistic-regression models for 10 rounds, with 300 synthetic samples per
node, 20 features and seed 42. The three scenarios were an honest-only
control, an attack with plain FedAvg, and an attack with reputation-weighted
aggregation. In the attack scenarios, node 3 sign-flipped and amplified its
update 5x, then added noise.

The server compared updates with the coordinate-wise median and smoothed
scores across rounds, flagging nodes below 0.5 reputation. Earlier sandbox
trials were used to fix errors and adjust the synthetic data before the
laptop run.

The [round records](results/reputation_log.csv), [results figure](results/spike_results.png)
and [terminal screenshot](results/Windows_Run_Evidence.png) preserve the laptop
results. The [original log](results/my_run_log.txt) includes Windows-support
warnings and a Ray worker fatal-exception message; all three scenarios
completed 10 rounds, but the run was not error-free.
[Software versions](results/software_versions.txt) were recorded afterward
in the same environment.

To rerun from a cloned repository in PowerShell:

```powershell
cd code
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe spike.py
.\.venv\Scripts\python.exe plot.py
```

New output goes to `code/out/`, leaving the saved evidence unchanged.

## Results

The laptop run met all three targets.

| Measure | Pass target | Run result | Outcome |
|---|---|---|---|
| Final reputation separation | Attacker at least 0.2 below every honest node | Plain: 0.0671 vs 0.8045 minimum honest; weighted: 0.0668 vs 0.8024 | Pass |
| Honest-node flags | At most 2/10 rounds per honest node | 0/10 for every honest node in both attack scenarios | Pass |
| Weighted accuracy (additional) | Within 5 percentage points of control | 97.0% vs 99.67%; gap 2.67 points | Pass |

Both attack scenarios flagged the attacker from round 3 onward. Accuracy
was **94.0% with plain FedAvg** and **97.0% with reputation weighting**.

This supports keeping the planned reputation-tracking design. These are
synthetic-task results, not real deepfake-detection accuracy or edge-hardware
measurements. Krum and Trimmed Mean were not tested; that choice remains
unresolved. The next IT 445 test should use the real detector and deepfake
data, multiple seeds and less obvious attacks.

The [final two-page report](results/Cohen_Dylan_Spike.pdf) provides the full
findings and design implications.
