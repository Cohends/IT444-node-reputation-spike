"""Fill the IT 444 spike report template and export Cohen_Dylan_Spike.docx."""
from docx import Document
from docx.shared import Pt

SRC = "/home/user/workspace/spike-reputation/Cohen_Dylan_Spike.docx"
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
set_cell(t, 1, 1, "LEE2-B")
set_cell(t, 1, 3, "FR-16 (per-node reputation), FR-12/FR-13 (update anomaly checks)")

# 1. The question
fill_single(
    tables[1],
    "Can the federated learning server accurately track and update the reputation of individual "
    "edge nodes across multiple training rounds to identify potentially malicious model updates?",
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
            "Additional test: final accuracy with reputation weighting vs. honest-only control",
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
    "I ran the spike on my Windows laptop in PowerShell using a Python virtual environment "
    "inside Downloads\\spike-reputation. My setup was Windows 11 Pro 64-bit "
    "(version 10.0.26300, build 26300), PowerShell 5.1.26100.9818, Python 3.14.2, "
    "Flower 1.43.0, Ray 2.60.0, NumPy 2.5.4, and Matplotlib 3.11.2. "
    "I recorded these versions after the run using the same virtual environment.\n"
    "The test used four simulated nodes over 10 rounds. Each node had 300 synthetic samples "
    "with 20 features and trained a small logistic-regression model. The data differed slightly "
    "between nodes. Node 3 was set up to submit a sign-flipped, amplified update with "
    "added noise. I used simulation instead of our edge devices and synthetic data instead "
    "of real deepfake clips. This let me test the reputation logic without building the full "
    "detector, but it does not test real device speed, networking, or deepfake-detection accuracy.",
)

# 3. What you did
fill_single(
    tables[4],
    "I cloned the repository, installed "
    "the dependencies in a virtual environment, and ran spike.py on my laptop. I compared "
    "three setups: all honest nodes, one attacker with plain FedAvg, and one attacker with "
    "reputation-weighted aggregation. The main test was whether the server could keep and "
    "update a separate score for each node across rounds. Reputation weighting was an "
    "additional test, not a comparison of Krum and Trimmed Mean. I then ran plot.py.\n"
    "The server compares each update with the coordinate-wise median of all updates. "
    "A node farther from that reference gets a lower score. The score is "
    "min(1, 2*d_ref/(d_ref + d_i)), where d_i is the node's distance and d_ref is the median "
    "distance across nodes. Reputation starts at 1.0 and updates as "
    "0.7*previous reputation + 0.3*current score. Scores below 0.5 are flagged.\n"
    "The measures above were used for my laptop run. The script was first tested in a "
    "sandbox to fix errors and adjust the synthetic data before I ran it on my laptop. "
    "To repeat it in PowerShell: "
    ".venv\\Scripts\\python.exe spike.py, then .venv\\Scripts\\python.exe plot.py.",
)

# 4. Results
t = tables[5]
for i, r in enumerate(
    [
        (
            "P1: malicious vs. honest final reputation",
            ">= 0.2 lower than every honest node",
            "Plain: 0.0671 vs. 0.8045. Weighted: 0.0668 vs. 0.8024.",
            "Yes",
        ),
        (
            "P2: honest nodes falsely flagged",
            "at most 2 of 10 rounds per node",
            "0 of 10 rounds, all honest nodes, both attack scenarios",
            "Yes",
        ),
        (
            "P3 (additional): weighted accuracy vs. control",
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
    "The answer to my D4 question is yes in this simulated test. The server recorded and "
    "updated separate reputation scores for all four nodes in every round. The malicious "
    "node finished near 0.067, while every honest node stayed above 0.80. The laptop CSV "
    "shows the attacker was flagged from round 3 onward, with no honest nodes flagged. "
    "Both main reputation checks passed.\n"
    "The additional weighting check also passed. Accuracy on the synthetic data was 99.7% "
    "with no attacker, 94.0% with the attacker and plain FedAvg, and 97.0% with reputation "
    "weighting. Using reputation scores improved accuracy by 3 percentage points, but it "
    "was still below the result with no attacker.\n"
    "One thing I noticed was that an honest node's score could also decrease because its "
    "updates were different from the others. That matters because a different update is not "
    "automatically a malicious one. This test only used one seed and one attack setup, so "
    "it does not show how the rule handles stronger data differences or less obvious attacks. "
    "The laptop log also contains Windows-support warnings and a Ray worker fatal-exception "
    "message. All three scenarios still completed 10 rounds and printed the final verdict, "
    "but I would not describe the run as error-free.",
)

# 5. Decision
fill_single(tables[7], "☐  Keep the design as it is      ☒  Change the design      ☐  Switch to Plan B (from D6)")

fill_single(
    tables[8],
    "We are keeping the same overall design. Reputation tracking was already part of D4, "
    "and this test gives us a working example for FR-16. The main change I am suggesting "
    "is that the server use reputation scores when combining model updates, instead of only "
    "recording or flagging suspicious behavior. This is a focused change to the server's "
    "aggregation logic, not a redesign of the edge devices or local-training workflow. "
    "The additional test showed that weighting helped in simulation, but it does not prove "
    "that the system can identify every malicious update. I would not lower our security-risk "
    "rating yet.\n"
    "The first step in IT 445 should be to test the same logic with our real detector and "
    "deepfake data, then try multiple seeds, larger differences between clients, and less "
    "obvious attacks. We also need to check how nodes recover their reputation after a bad "
    "round. D4 also assigns me the separate question of whether to use Krum or Trimmed Mean "
    "as the final robust aggregation method. I did not test either method in this spike, so "
    "I still need to compare them before choosing one. Blocking nodes was not tested either. "
    "Based on this test, I do not think we need to change our requirements or budget.",
)

# 6. Evidence
t = tables[9]
for i, r in enumerate(
    [
        ("Repository", "https://github.com/Cohends/spike-reputation", "Code, report, and evidence. Private; reviewer needs access."),
        ("Laptop screenshot", "Windows_Run_Evidence.png", "PowerShell verdict: all checks passed; plot.py saved the figure."),
        ("Laptop output", "evidence/windows/my_run_log.txt; evidence/windows/reputation_log.csv", "Original laptop log and all 30 round records. UTF-8 log copy also included."),
        ("Figure", "evidence/windows/spike_results.png", "Reputation and accuracy plots generated on my laptop."),
    ],
    start=1,
):
    for j, v in enumerate(r):
        set_cell(t, i, j, v, size=9)

# Keep the existing template and make the two-page layout readable in Word and PDF.
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
for section in d.sections:
    section.top_margin = Pt(36)
    section.bottom_margin = Pt(36)
for table in d.tables:
    for row in table.rows:
        props = row._tr.get_or_add_trPr()
        if props.find(qn("w:cantSplit")) is None:
            props.append(OxmlElement("w:cantSplit"))
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_before = Pt(0)
                paragraph.paragraph_format.space_after = Pt(3)
                paragraph.paragraph_format.line_spacing = 1.0
                for run in paragraph.runs:
                    run.font.name = "Calibri"
                    run.font.size = Pt(9)
                    run.font.color.rgb = __import__("docx").shared.RGBColor(0, 0, 0)
for paragraph in d.paragraphs:
    paragraph.paragraph_format.space_after = Pt(3)
    for br in list(paragraph._p.findall(".//" + qn("w:br"))):
        if br.get(qn("w:type")) == "page":
            br.getparent().remove(br)
    if paragraph.text == "4. Results":
        paragraph.paragraph_format.page_break_before = True
d.core_properties.author = "Dylan Cohen"
d.core_properties.title = "IT 444 Technical Spike Report"
# Native hyperlink for the actual evidence repository.
from docx.opc.constants import RELATIONSHIP_TYPE as RT
repo_paragraph = tables[9].rows[1].cells[1].paragraphs[0]
repo_paragraph.clear()
hyperlink = OxmlElement("w:hyperlink")
rid = d.part.relate_to("https://github.com/Cohends/spike-reputation", RT.HYPERLINK, is_external=True)
hyperlink.set(qn("r:id"), rid)
run = OxmlElement("w:r")
props = OxmlElement("w:rPr")
size = OxmlElement("w:sz")
size.set(qn("w:val"), "18")
props.append(size)
run.append(props)
text = OxmlElement("w:t")
text.text = "https://github.com/Cohends/spike-reputation"
run.append(text)
hyperlink.append(run)
repo_paragraph._p.append(hyperlink)
d.save(DST)
print("saved", DST)
