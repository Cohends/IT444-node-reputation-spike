"""Fill the IT 444 spike report template and export Cohen_Dylan_Spike.docx."""
from docx import Document
from docx.shared import Pt

SRC = "/home/user/.perplexity/attachments/2c26166b14904e80992d79e0156d3818/Spike_Report_Template.docx"
DST = "/home/user/workspace/spike-reputation/Cohen_Dylan_Spike.docx"

d = Document(SRC)
tables = d.tables

# Remove the grey hint paragraph ("Two pages maximum...")
for p in list(d.paragraphs):
    if "Two pages maximum" in p.text:
        p._element.getparent().remove(p._element)
        break


def set_cell(t, r, c, text, size=None, bold=False):
    cell = t.rows[r].cells[c]
    for p in cell.paragraphs[1:]:
        p._element.getparent().remove(p._element)
    p = cell.paragraphs[0]
    for run in list(p.runs):
        run._element.getparent().remove(run._element)
    run = p.add_run(text)
    run.bold = bold
    if size:
        run.font.size = Pt(size)


def fill_single(t, text, size=9):
    set_cell(t, 0, 0, text, size=size)


# Header
t = tables[0]
set_cell(t, 0, 1, "Dylan Cohen", bold=True)
set_cell(t, 0, 3, "2 (Lee-2)")
set_cell(t, 1, 1, "Federated deepfake detection")
set_cell(t, 1, 3, "FR-16 (per-node reputation), FR-12/FR-13 (update anomaly checks)")

# 1. The question
fill_single(
    tables[1],
    "Can the Flower server maintain a rolling reputation score for each edge node, keep a "
    "malicious node's score clearly below every honest node's over 10 federated rounds, and "
    "use those scores to protect the global model from a poisoned update?",
)

# Measures / pass marks
t = tables[2]
for i, (m, p) in enumerate(
    [
        (
            "Malicious node's final reputation vs. every honest node's (both attack scenarios)",
            "at least 0.2 lower",
        ),
        (
            "Honest nodes flagged (reputation < 0.5) per 10-round attack scenario",
            "at most 2 of 10 rounds, per node",
        ),
        (
            "Final global accuracy with reputation-weighted aggregation vs. honest-only control",
            "within 0.05 of control",
        ),
    ],
    start=1,
):
    set_cell(t, i, 0, m, size=9)
    set_cell(t, i, 1, p, size=9)

# 2. Setup
fill_single(
    tables[3],
    "Dell XPS 15 laptop, Ubuntu Linux, Python 3.14, Flower (flwr) 1.43.0 with the Ray "
    "simulation backend, NumPy 2.5, matplotlib. Four simulated edge nodes each train a small "
    "NumPy logistic-regression \"detector\" (20 features, 300 samples) on synthetic real-vs-"
    "fake data with a mild per-node shift, for 10 federated rounds. Node 3 is malicious: it "
    "submits a model-poisoning update (its honest update, sign-flipped and amplified 5x). "
    "Substitutions: our Pi 5 / Orin devices are not purchased yet, so I ran Flower's simulator "
    "on my laptop — this drops real network latency and device heterogeneity, but the "
    "reputation logic under test runs server-side, which the simulator exercises fully. I used "
    "synthetic data and a logistic-regression stand-in instead of AV-Deepfake1M and our real "
    "detector to stay inside the spike time box; this tests the reputation mechanism, not "
    "detector accuracy.",
)

# 3. What you did
fill_single(
    tables[4],
    "1) Before running, defined the reputation rule: each round the server computes every "
    "client's update distance from the coordinate-wise median of all updates (the robust-"
    "consensus idea behind Krum / trimmed-mean), scores each node s = 2*d_ref/(d_ref + d_i) "
    "capped at 1.0, keeps an EMA reputation (alpha = 0.3), and flags nodes below 0.5. "
    "2) Wrote spike.py: a ReputationFedAvg strategy extending Flower's FedAvg that tracks "
    "reputation per node in aggregate_fit, plus four NumPy clients, one poisoned. 3) Ran "
    "three seeded scenarios: no-attacker control; attack with plain FedAvg (reputation "
    "observed only); attack with reputation-weighted aggregation. 4) Logged per-round "
    "reputations, distances, flags, and accuracy to CSV and plotted them. Repeat with: "
    "pip install -r requirements.txt; python3 spike.py; python3 plot.py (~30 s).",
)

# 4. Results
t = tables[5]
for i, r in enumerate(
    [
        (
            "P1: malicious vs. honest final reputation",
            ">= 0.2 lower than every honest node",
            "malicious 0.067 vs. min honest 0.804 / 0.802; gap ~0.74",
            "Yes",
        ),
        (
            "P2: honest nodes falsely flagged",
            "at most 2 of 10 rounds per node",
            "0 of 10 rounds, all honest nodes, both attack scenarios",
            "Yes",
        ),
        (
            "P3: defended final accuracy vs. control",
            "within 0.05 of control (0.997)",
            "0.970 weighted vs. 0.997 control; difference 0.027",
            "Yes",
        ),
    ],
    start=1,
):
    for j, v in enumerate(r):
        set_cell(t, i, j, v, size=9)

fill_single(
    tables[6],
    "What worked: the median-distance score separated the malicious node immediately — its "
    "update distance was ~2.3 every round versus ~0.01-0.03 for honest nodes, so its "
    "reputation fell below the 0.5 flag threshold by round 3 and hit 0.067 by round 10, while "
    "no honest node was ever flagged, including in the control. What did not / surprised me: "
    "plain FedAvg under attack only dropped 0.997 to 0.940, so the attack is visible to the "
    "tracker but its damage on this small model was modest — I should not oversell poisoning "
    "impact on the real system. Honest nodes also drift down slowly (node 0 reached ~0.80) "
    "because non-IID updates sit slightly off the median; the threshold has headroom, but on "
    "noisier real data it and the EMA alpha will need tuning. Stealthier attacks (scaled but "
    "honest-looking updates) are untested.",
)

# 5. Decision
fill_single(tables[7], "☐  Keep the design as it is      ☒  Change the design      ☐  Switch to Plan B (from D6)")

fill_single(
    tables[8],
    "FR-16 is feasible — server-side reputation tracking works, so the requirement stays. "
    "The change: the security layer should not only log reputation but use it as aggregation "
    "weights or to exclude flagged nodes — plain observation did not stop the poisoned update "
    "from costing 5.7 accuracy points, while weighting recovered most of that loss. This "
    "also informs my Krum-vs-trimmed-mean question: both sit in the same robust-consensus "
    "family as the median-distance score that worked here, so either is a reasonable fit. "
    "Requirements and budget are unchanged; risk 6 (security) drops in severity. IT 445 "
    "first step: port the reputation logic onto our real Flower server with real clients and "
    "the AV-Deepfake1M subset, then tune the threshold and alpha on noisier real updates.",
)

# 6. Evidence
t = tables[9]
for i, r in enumerate(
    [
        ("Repository", "github.com/dylanscohen/spike-reputation (to be pushed)", "spike.py, plot.py, README, commits"),
        ("Run log", "out/run_log.txt", "Console output of all three scenarios and the pass/fail verdict"),
        ("Data log", "out/reputation_log.csv", "Per-round reputation, distances, flags, accuracy (30 rounds)"),
        ("Figure", "out/spike_results.png", "Reputation and accuracy plots"),
    ],
    start=1,
):
    for j, v in enumerate(r):
        set_cell(t, i, j, v, size=9)

d.save(DST)
print("saved", DST)
