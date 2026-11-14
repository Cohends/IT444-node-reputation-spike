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
set_cell(t, 0, 1, "Dylan Cohen")
set_cell(t, 0, 3, "Team 2")
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
    "Windows 11 Pro 64-bit laptop (10.0.26300, build 26300), PowerShell 5.1.26100.9818, "
    "Python 3.14.2, Flower 1.43.0, Ray 2.60.0, NumPy 2.5.4 and Matplotlib 3.11.2. "
    "Versions were recorded after the run in the same virtual environment. Four simulated "
    "nodes trained logistic-regression models for 10 rounds per scenario, using seed 42. "
    "Each node had 300 synthetic samples with 20 features and slightly different data. "
    "In attack scenarios, node 3 submitted sign-flipped, amplified updates with added noise. Simulation isolated "
    "server-side reputation tracking without requiring the full deepfake detector or edge hardware.",
)

# 3. What you did
fill_single(
    tables[4],
    "Clone the repository and install the dependencies in a virtual environment. "
    "The script was tested in a sandbox to fix errors and adjust the synthetic data before "
    "the laptop run; the measures above were used for that run.\n"
    "Run .venv\\Scripts\\python.exe spike.py in PowerShell. Compare all-honest nodes, "
    "an attacker with plain FedAvg, and an attacker with reputation-weighted aggregation.\n"
    "Compare each update with the coordinate-wise median. Calculate its score as "
    "min(1, 2*d_ref/(d_ref + d_i)), where d_i is its distance and d_ref is the median "
    "distance across nodes. Start reputation at 1.0, update it as "
    "0.7*previous reputation + 0.3*current score, and flag reputations below 0.5.\n"
    "Save each node's reputation and flag status across rounds. Run "
    ".venv\\Scripts\\python.exe plot.py, then compare final scores, honest-node false flags "
    "and accuracy with the pass marks. Weighting is an additional test, not a test of "
    "Krum or Trimmed Mean.",
)

# 4. Results
t = tables[5]
for i, r in enumerate(
    [
        (
            "P1: attacker vs. lowest honest final reputation",
            "At least 0.2 lower",
            "Plain: 0.0671 / 0.8045\nWeighted: 0.0668 / 0.8024",
            "Yes",
        ),
        (
            "P2: honest nodes falsely flagged",
            "At most 2/10 rounds per node",
            "0/10, every honest node in both attack scenarios",
            "Yes",
        ),
        (
            "P3 (additional): weighted accuracy",
            "Within 0.05 of control",
            "0.970 vs. 0.997 control; gap 0.027",
            "Yes",
        ),
    ],
    start=1,
):
    for j, v in enumerate(r):
        set_cell(t, i, j, v, size=9)

fill_single(
    tables[6],
    "All three targets passed. The server tracked all four nodes across rounds and flagged "
    "the attacker from round 3 onward in both attack scenarios, with no honest-node flags. "
    "Synthetic-task accuracy was 99.7% for the control, 94.0% with plain FedAvg under attack "
    "and 97.0% with weighting. The D4 reputation answer is yes in this simulation, not a claim "
    "about real deepfake-detection accuracy.\n"
    "Honest scores also fell, so different updates are not automatically malicious. This used "
    "one seed and one attack. The log contains Windows-support warnings and a Ray worker "
    "fatal-exception message. All scenarios completed 10 rounds, but the run was not error-free.",
)

# 5. Decision
fill_single(tables[7], "☒  Keep the design as it is      ☐  Change the design      ☐  Switch to Plan B (from D6)")

fill_single(
    tables[8],
    "Architecture and budget. Keep the planned reputation-tracking design, including the "
    "overall architecture, edge devices and local-training workflow. The additional test "
    "suggests weighting updates by reputation, but this is an implementation recommendation "
    "to validate with the real detector and deepfake data, not an architecture change. "
    "No requirements or budget change is indicated.\n"
    "D4 coverage. The run demonstrates FR-16 reputation tracking and exercises anomaly checks "
    "related to FR-12/FR-13. Node blocking, real device speed and networking were not tested. "
    "I would not lower the security-risk rating. The separate D4 choice between Krum and "
    "Trimmed Mean remains untested and unresolved.\n"
    "First IT 445 test. Use the real detector and deepfake data, then test multiple seeds, "
    "larger differences between nodes, less obvious attacks and reputation recovery. "
    "Compare Krum and Trimmed Mean separately before selecting the final robust method.",
)

# 6. Evidence
t = tables[9]
for i, r in enumerate(
    [
        ("Repository", "IT444-node-reputation-spike", "Code, report and evidence; private."),
        ("Laptop screenshot", "Windows_Run_Evidence.png", "PowerShell verdict and plot output."),
        ("Laptop output", "my_run_log.txt / reputation_log.csv", "Original log and 30 round records."),
        ("Figure", "spike_results.png", "Laptop reputation and accuracy plots."),
    ],
    start=1,
):
    for j, v in enumerate(r):
        set_cell(t, i, j, v, size=9)

# Match Christopher's report: Arial, numbered procedure, labeled conclusions and page footer.
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import RGBColor
from docx.enum.table import WD_ROW_HEIGHT_RULE, WD_CELL_VERTICAL_ALIGNMENT
for section in d.sections:
    section.top_margin = Pt(48)
    section.bottom_margin = Pt(48)
    section.footer_distance = Pt(24)
normal = d.styles["Normal"]
normal.font.name = "Arial"
normal.font.size = Pt(10)
for table in d.tables:
    table.autofit = False
    for row in table.rows:
        row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
        props = row._tr.get_or_add_trPr()
        if props.find(qn("w:cantSplit")) is None:
            props.append(OxmlElement("w:cantSplit"))
        for cell in row.cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_before = Pt(0)
                paragraph.paragraph_format.space_after = Pt(4)
                paragraph.paragraph_format.line_spacing = 1.0
                for run in paragraph.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(10)
                    run.font.color.rgb = RGBColor.from_string("151219")
for paragraph in d.paragraphs:
    paragraph.paragraph_format.space_after = Pt(6)
    for run in paragraph.runs:
        run.font.name = "Arial"
    if paragraph.text[:2] in ("1.", "2.", "3.", "4.", "5.", "6."):
        paragraph.paragraph_format.space_before = Pt(10)
        for run in paragraph.runs:
            run.font.size = Pt(12)
            run.bold = True
            run.font.color.rgb = RGBColor.from_string("340061")
    elif paragraph.text == "Technical Spike Report":
        for run in paragraph.runs:
            run.font.size = Pt(16)
            run.bold = True
    elif not paragraph.text:
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(1)
        paragraph.paragraph_format.line_spacing = Pt(2)
        paragraph.paragraph_format.line_spacing = 1
        for run in paragraph.runs:
            run.font.size = Pt(3)
    for br in list(paragraph._p.findall(".//" + qn("w:br"))):
        if br.get(qn("w:type")) == "page":
            br.getparent().remove(br)
    if paragraph.text == "4. Results":
        paragraph.paragraph_format.page_break_before = True
# Split procedure and conclusions into native paragraphs rather than dense blocks.
for index in (4, 8):
    cell = tables[index].cell(0, 0)
    lines = cell.text.split("\n")
    cell.text = ""
    for i, line in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.0
        if index == 4:
            # Use real Word numbering with a dedicated list, not text-only numbers.
            numbering = d.part.numbering_part.element
            if i == 0:
                ids = [int(x.get(qn("w:abstractNumId"))) for x in numbering.findall(qn("w:abstractNum"))]
                aid = max(ids, default=-1) + 1
                abstract = OxmlElement("w:abstractNum")
                abstract.set(qn("w:abstractNumId"), str(aid))
                lvl = OxmlElement("w:lvl")
                lvl.set(qn("w:ilvl"), "0")
                for tag, value in (("start", "1"), ("numFmt", "decimal"), ("lvlText", "%1."), ("suff", "space")):
                    el = OxmlElement("w:" + tag)
                    el.set(qn("w:val"), value)
                    lvl.append(el)
                abstract.append(lvl)
                numbering.append(abstract)
                num = numbering.add_num(aid)
                procedure_num_id = num.numId
            np = p._p.get_or_add_pPr().get_or_add_numPr()
            np.get_or_add_ilvl().val = 0
            np.get_or_add_numId().val = procedure_num_id
            p.paragraph_format.left_indent = Pt(12)
            p.paragraph_format.first_line_indent = Pt(-12)
            p.add_run(line)
        else:
            label, body = line.split(". ", 1)
            p.add_run(label + ". ").bold = True
            p.add_run(body)
        for run in p.runs:
            run.font.name = "Arial"
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor.from_string("151219")
# Footer fields stay editable and update when Word repaginates.
for section in d.sections:
    p = section.footer.paragraphs[0]
    p.clear()
    p.paragraph_format.space_after = Pt(0)
    p.add_run("IT 444 Technical Spike Report | LEE2-B | ")
    for field, suffix in (("PAGE", " of "), ("NUMPAGES", "")):
        el = OxmlElement("w:fldSimple")
        el.set(qn("w:instr"), field)
        field_run = OxmlElement("w:r")
        field_props = OxmlElement("w:rPr")
        for tag, value in (("sz", "17"), ("color", "340061")):
            prop = OxmlElement("w:" + tag)
            prop.set(qn("w:val"), value)
            field_props.append(prop)
        field_run.append(field_props)
        value = OxmlElement("w:t")
        value.text = "1" if field == "PAGE" else "2"
        field_run.append(value)
        el.append(field_run)
        p._p.append(el)
        p.add_run(suffix)
    for run in p.runs:
        run.font.name = "Arial"
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor.from_string("340061")
    border = OxmlElement("w:pBdr")
    top = OxmlElement("w:top")
    for key, value in (("val", "single"), ("sz", "4"), ("space", "6"), ("color", "B18BFF")):
        top.set(qn("w:" + key), value)
    border.append(top)
    props = p._p.get_or_add_pPr()
    for existing in list(props.findall(qn("w:pBdr"))):
        props.remove(existing)
    props.append(border)
# Give results sufficient room for numeric comparisons, as in the reference.
for index, widths in ((5, (150, 108, 150, 60)), (9, (90, 202, 176))):
    table = tables[index]
    for column, width in zip(table.columns, widths):
        column.width = Pt(width)
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            cell.width = Pt(width)
d.core_properties.author = "Dylan Cohen"
d.core_properties.title = "IT 444 Technical Spike Report"
# Native evidence hyperlinks, with filenames rather than long URLs in the table.
from docx.opc.constants import RELATIONSHIP_TYPE as RT
repo = "https://github.com/Cohends/IT444-node-reputation-spike"
def add_link(paragraph, label, url):
    hyperlink = OxmlElement("w:hyperlink")
    rid = d.part.relate_to(url, RT.HYPERLINK, is_external=True)
    hyperlink.set(qn("r:id"), rid)
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    for tag, value in (("sz", "20"), ("color", "641BC1"), ("u", "single")):
        el = OxmlElement("w:" + tag)
        el.set(qn("w:val"), value)
        props.append(el)
    run.append(props)
    text = OxmlElement("w:t")
    text.text = label
    run.append(text)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)
for row, links in (
    (1, [("IT444-node-reputation-spike", repo)]),
    (2, [("Windows_Run_Evidence.png", repo + "/blob/main/Windows_Run_Evidence.png")]),
    (3, [("my_run_log.txt", repo + "/blob/main/evidence/windows/my_run_log.txt"),
         ("reputation_log.csv", repo + "/blob/main/evidence/windows/reputation_log.csv")]),
    (4, [("spike_results.png", repo + "/blob/main/evidence/windows/spike_results.png")]),
):
    p = tables[9].cell(row, 1).paragraphs[0]
    p.clear()
    for i, (label, url) in enumerate(links):
        if i:
            p.add_run(" / ").font.size = Pt(10)
        add_link(p, label, url)
# Drop unused pre-rename hyperlinks after replacing the evidence cells.
used_hyperlinks = set(d.element.xpath(".//w:hyperlink/@r:id"))
for rid, rel in list(d.part.rels.items()):
    if rel.reltype == RT.HYPERLINK and rid not in used_hyperlinks:
        d.part.drop_rel(rid)
d.save(DST)
print("saved", DST)
