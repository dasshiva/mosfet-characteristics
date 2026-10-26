#!/usr/bin/env python3
"""Build the MOSFET common-source laboratory report as a PDF."""

from pathlib import Path
import json

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, PageBreak, KeepTogether, HRFlowable, NextPageTemplate,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfgen import canvas

HERE = Path(__file__).parent
FIG = HERE / "figures"
OUT = HERE / "MOSFET_CS_Characteristics_Report.pdf"
details = json.loads((HERE / "details.json").read_text())

# ---------------------------------------------------------------- fonts
FONT_DIR = Path("/usr/share/fonts/truetype/liberation")
pdfmetrics.registerFont(TTFont("LibSerif", FONT_DIR / "LiberationSerif-Regular.ttf"))
pdfmetrics.registerFont(TTFont("LibSerif-Bold", FONT_DIR / "LiberationSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("LibSerif-Italic", FONT_DIR / "LiberationSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("LibSerif-BoldItalic", FONT_DIR / "LiberationSerif-BoldItalic.ttf"))
pdfmetrics.registerFont(TTFont("LibSans", FONT_DIR / "LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("LibSans-Bold", FONT_DIR / "LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("LibSans-Italic", FONT_DIR / "LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("LibMono", "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"))
pdfmetrics.registerFontFamily("LibSerif", normal="LibSerif", bold="LibSerif-Bold",
                              italic="LibSerif-Italic", boldItalic="LibSerif-BoldItalic")
pdfmetrics.registerFontFamily("LibSans", normal="LibSans", bold="LibSans-Bold",
                              italic="LibSans-Italic", boldItalic="LibSans-Bold")
pdfmetrics.registerFontFamily("LibMono", normal="LibMono", bold="LibMono",
                              italic="LibMono", boldItalic="LibMono")

# ---------------------------------------------------------------- palette
NAVY = colors.HexColor("#0b1b33")
NAVY_SOFT = colors.HexColor("#1c3554")
TEAL = colors.HexColor("#0d9488")
TEAL_LIGHT = colors.HexColor("#5eead4")
MUTED = colors.HexColor("#64748b")
LINE = colors.HexColor("#dce4ef")
BG = colors.HexColor("#f7fafd")
AMBER = colors.HexColor("#b45309")

# ---------------------------------------------------------------- styles
styles = getSampleStyleSheet()

Body = ParagraphStyle(
    "Body", parent=styles["BodyText"], fontName="LibSerif", fontSize=10.2,
    leading=14.7, alignment=TA_JUSTIFY, textColor=colors.HexColor("#1b2a3d"),
    spaceAfter=5.5, firstLineIndent=0,
)
BodyNoIndent = ParagraphStyle("BodyNoIndent", parent=Body, firstLineIndent=0)
H1 = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontName="LibSans-Bold", fontSize=15.2,
    leading=18.5, textColor=NAVY, spaceBefore=4, spaceAfter=9,
    keepWithNext=True,
)
H2 = ParagraphStyle(
    "H2", parent=styles["Heading2"], fontName="LibSans-Bold", fontSize=11.3,
    leading=14.5, textColor=NAVY_SOFT, spaceBefore=10, spaceAfter=4,
    keepWithNext=True,
)
FrontHeading = ParagraphStyle(
    "FrontHeading", parent=H1, fontSize=16.5, leading=20, alignment=TA_LEFT,
    spaceBefore=0, spaceAfter=2,
)
Caption = ParagraphStyle(
    "Caption", parent=Body, fontName="LibSans", fontSize=8.4, leading=11,
    alignment=TA_CENTER, textColor=MUTED, spaceBefore=3, spaceAfter=9,
)
Equation = ParagraphStyle(
    "Equation", parent=Body, fontName="LibSerif", fontSize=10.4, leading=15,
    alignment=TA_CENTER, spaceBefore=3, spaceAfter=6,
)
Bullet = ParagraphStyle(
    "Bullet", parent=Body, leftIndent=14, bulletIndent=4, spaceAfter=3,
)
Small = ParagraphStyle(
    "Small", parent=Body, fontName="LibSans", fontSize=8.2, leading=11,
    textColor=MUTED,
)
TableText = ParagraphStyle(
    "TableText", parent=Body, fontName="LibSerif", fontSize=8.5, leading=10.5,
    alignment=TA_LEFT, spaceAfter=0,
)
TableHead = ParagraphStyle(
    "TableHead", parent=TableText, fontName="LibSans-Bold", fontSize=8.0,
    textColor=colors.white,
)
TOCHeading = ParagraphStyle("TOCHeading", parent=FrontHeading, spaceAfter=8)
TOCH1 = ParagraphStyle(
    "TOCH1", fontName="LibSans-Bold", fontSize=10.1, leading=16.2,
    textColor=NAVY, leftIndent=0, firstLineIndent=0, spaceBefore=1,
)
TOCH2 = ParagraphStyle(
    "TOCH2", fontName="LibSans", fontSize=9.2, leading=13.6,
    textColor=NAVY_SOFT, leftIndent=14, firstLineIndent=0,
)
ListHeading = ParagraphStyle(
    "ListHeading", parent=H2, fontSize=10.2, spaceBefore=16, spaceAfter=5,
)
ListText = ParagraphStyle(
    "ListText", parent=Body, fontName="LibSans", fontSize=8.5, leading=11.5,
    leftIndent=10, firstLineIndent=-10, spaceAfter=1.5,
)

# ---------------------------------------------------------------- page furniture
PAGE_W, PAGE_H = A4
ML, MR, MT, MB = 2.2 * cm, 2.2 * cm, 2.35 * cm, 2.25 * cm
CONTENT_W = PAGE_W - ML - MR
CONTENT_H = PAGE_H - MT - MB
HEADER_Y = PAGE_H - 1.42 * cm
FOOTER_Y = 1.15 * cm


def draw_cover(canv: canvas.Canvas, doc):
    canv.saveState()
    # page background
    canv.setFillColor(colors.HexColor("#f4f8fc"))
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # dark upper field
    top_h = 18.2 * cm
    canv.setFillColor(colors.HexColor("#071426"))
    canv.rect(0, PAGE_H - top_h, PAGE_W, top_h, fill=1, stroke=0)

    # subtle grid
    canv.saveState()
    canv.setStrokeColor(colors.HexColor("#16304f"))
    canv.setLineWidth(0.35)
    for x in range(0, int(PAGE_W) + 1, 32):
        canv.line(x, PAGE_H - top_h, x, PAGE_H)
    for y in range(int(PAGE_H - top_h), int(PAGE_H) + 1, 32):
        canv.line(0, y, PAGE_W, y)
    canv.restoreState()

    # decorative characteristic curve, right-hand side
    canv.saveState()
    canv.setStrokeColor(colors.HexColor("#2dd4bf"))
    canv.setLineWidth(2.2)
    p = canv.beginPath()
    p.moveTo(12.4 * cm, PAGE_H - 12.7 * cm)
    p.curveTo(14.0 * cm, PAGE_H - 12.7 * cm, 14.7 * cm, PAGE_H - 17.1 * cm,
              16.1 * cm, PAGE_H - 17.5 * cm)
    p.curveTo(17.4 * cm, PAGE_H - 17.8 * cm, 18.4 * cm, PAGE_H - 17.6 * cm,
              20.8 * cm, PAGE_H - 17.4 * cm)
    canv.drawPath(p, fill=0, stroke=1)

    canv.setStrokeColor(colors.HexColor("#f59e0b"))
    canv.setLineWidth(1.15)
    canv.setDash(5, 4)
    p2 = canv.beginPath()
    p2.moveTo(12.4 * cm, PAGE_H - 13.2 * cm)
    p2.curveTo(14.2 * cm, PAGE_H - 13.5 * cm, 15.6 * cm, PAGE_H - 15.8 * cm,
               20.8 * cm, PAGE_H - 16.3 * cm)
    canv.drawPath(p2, fill=0, stroke=1)
    canv.setDash()
    canv.setFillColor(colors.HexColor("#071426"))
    canv.setStrokeColor(colors.HexColor("#5eead4"))
    canv.setLineWidth(2.2)
    canv.circle(16.1 * cm, PAGE_H - 17.5 * cm, 4.2, fill=1, stroke=1)
    canv.setFillColor(colors.HexColor("#9fb4d8"))
    canv.setFont("LibSans", 7.2)
    canv.drawString(12.4 * cm, PAGE_H - 13.05 * cm, "DRAIN FAMILY")
    canv.drawRightString(20.8 * cm, PAGE_H - 16.05 * cm, "LOAD LINE")
    canv.restoreState()

    # eyebrow
    canv.setFillColor(TEAL_LIGHT)
    canv.setFont("LibSans-Bold", 8.4)
    canv.drawString(ML, PAGE_H - 2.15 * cm, "BASIC ELECTRONICS DEVICES  ·  LABORATORY PROJECT")

    # title
    canv.setFillColor(colors.white)
    canv.setFont("LibSans-Bold", 24.5)
    title_lines = [
        "To Obtain the Drain and Transfer",
        "Characteristics of a MOSFET",
        "Connected in Common-Source",
        "Configuration",
    ]
    y = PAGE_H - 3.55 * cm
    for line in title_lines:
        canv.drawString(ML, y, line)
        y -= 1.08 * cm

    # subtitle and module
    canv.setFillColor(colors.HexColor("#b8c9e1"))
    canv.setFont("LibSerif", 12.2)
    canv.drawString(ML, y - 0.15 * cm, "Interactive visualization and model-based analysis of an NMOS stage")
    canv.setStrokeColor(TEAL)
    canv.setLineWidth(2.4)
    canv.line(ML, y - 0.95 * cm, ML + 3.0 * cm, y - 0.95 * cm)
    canv.setFillColor(colors.HexColor("#8ff1e4"))
    canv.setFont("LibSans-Bold", 8.2)
    canv.drawString(ML, y - 1.56 * cm, "BED LAB  ·  COMMON-SOURCE CHARACTERIZATION  ·  2026")

    # details card
    card_x, card_y, card_w, card_h = ML, 1.75 * cm, CONTENT_W, 10.4 * cm
    canv.setFillColor(colors.HexColor("#dfe8f2"))
    canv.roundRect(card_x + 0.06 * cm, card_y - 0.06 * cm, card_w, card_h, 8, fill=1, stroke=0)
    canv.setFillColor(colors.white)
    canv.roundRect(card_x, card_y, card_w, card_h, 8, fill=1, stroke=0)
    canv.setStrokeColor(colors.HexColor("#dce4ef"))
    canv.setLineWidth(0.7)
    canv.roundRect(card_x, card_y, card_w, card_h, 8, fill=0, stroke=1)

    fields = [
        ("Submitted by", details["student_name"]),
        ("Enrollment No.", details["enrollment"]),
        ("Roll No.", details["roll"]),
        ("Department", details["department"]),
        ("Institution", details["institution"]),
        ("Date of submission", details["date"]),
    ]
    ry = card_y + card_h - 1.25 * cm
    for label, value in fields:
        canv.setFillColor(MUTED)
        canv.setFont("LibSans", 8.4)
        canv.drawString(card_x + 0.9 * cm, ry, label.upper())
        canv.setFillColor(NAVY)
        canv.setFont("LibSans-Bold", 10.0)
        canv.drawString(card_x + 5.0 * cm, ry, str(value))
        canv.setStrokeColor(colors.HexColor("#edf1f7"))
        canv.setLineWidth(0.5)
        canv.line(card_x + 0.9 * cm, ry - 0.42 * cm, card_x + card_w - 0.9 * cm, ry - 0.42 * cm)
        ry -= 1.28 * cm

    canv.setFillColor(MUTED)
    canv.setFont("LibSerif", 7.8)
    canv.drawString(ML, 1.05 * cm, "Submitted in partial fulfilment of the requirements of the Basic Electronics Devices laboratory.")
    canv.restoreState()


def draw_content(canv: canvas.Canvas, doc):
    canv.saveState()
    # header
    canv.setStrokeColor(colors.HexColor("#e1e8f1"))
    canv.setLineWidth(0.55)
    canv.line(ML, PAGE_H - 1.85 * cm, PAGE_W - MR, PAGE_H - 1.85 * cm)
    canv.setFillColor(colors.HexColor("#7b8ca3"))
    canv.setFont("LibSans", 7.1)
    canv.drawString(ML, HEADER_Y, "Drain and Transfer Characteristics of a MOSFET in Common-Source Configuration")
    canv.drawRightString(PAGE_W - MR, HEADER_Y, "BED Laboratory Project")
    # footer
    canv.setStrokeColor(colors.HexColor("#e1e8f1"))
    canv.line(ML, 1.62 * cm, PAGE_W - MR, 1.62 * cm)
    canv.setFillColor(colors.HexColor("#7b8ca3"))
    canv.setFont("LibSans", 7.4)
    canv.drawCentredString(PAGE_W / 2, FOOTER_Y, f"Page {canv.getPageNumber()}")
    canv.restoreState()


class ReportDoc(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        cover_frame = Frame(ML, MB, CONTENT_W, CONTENT_H, id="cover_frame",
                            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        body_frame = Frame(ML, MB, CONTENT_W, CONTENT_H, id="body_frame",
                           leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover),
            PageTemplate(id="content", frames=[body_frame], onPage=draw_content),
        ])

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            name = flowable.style.name
            if name == "H1":
                self.notify("TOCEntry", (0, flowable.getPlainText(), self.page))
            elif name == "H2":
                self.notify("TOCEntry", (1, flowable.getPlainText(), self.page))


# ---------------------------------------------------------------- helpers
def P(text, style=Body):
    return Paragraph(text, style)


def equation(text):
    return Paragraph(text, Equation)


def figure(name, width_cm, caption):
    path = FIG / name
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        iw, ih = im.size
    width = width_cm * cm
    height = width * ih / iw
    return KeepTogether([
        Spacer(1, 3),
        Image(str(path), width=width, height=height, hAlign="CENTER"),
        Paragraph(caption, Caption),
    ])


def styled_table(data, col_widths, header=True, font_size=8.5, align="LEFT"):
    table = Table(data, colWidths=col_widths, repeatRows=1 if header else 0, hAlign="CENTER")
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "LibSerif"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1b2a3d")),
        ("ALIGN", (0, 0), (-1, -1), align),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5ecf4")),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "LibSans-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), font_size - 0.4),
        ]
    table.setStyle(TableStyle(style))
    return table


def table_caption(text):
    return Paragraph(text, Caption)


def bullet_list(items):
    out = []
    for item in items:
        out.append(Paragraph(item, Bullet, bulletText="•"))
    return out


# ---------------------------------------------------------------- story
story = []

# ---------- cover ----------
story.append(NextPageTemplate("content"))
story.append(PageBreak())

# ---------- acknowledgment + abstract ----------
story.append(Spacer(1, 0.7 * cm))
story.append(P("ACKNOWLEDGMENT", FrontHeading))
story.append(HRFlowable(width="22%", thickness=2.2, color=TEAL, spaceBefore=3, spaceAfter=10, hAlign="LEFT"))
ack = """
I express my sincere gratitude to my project guide for the valuable guidance, patient review and
constant encouragement extended throughout this laboratory project. I am also thankful to the faculty
members of the <b>{department}</b> for providing the theoretical foundation and the facilities needed
to complete the work. Finally, I thank my family and friends for their support and useful discussions
during the preparation of this report.
""".format(department=details["department"])
story.append(P(ack, ParagraphStyle("FrontBody", parent=Body, fontSize=10.1, leading=14.5, spaceAfter=5)))
story.append(HRFlowable(width="100%", thickness=0.7, color=LINE, spaceBefore=5, spaceAfter=9))
story.append(P("ABSTRACT", FrontHeading))
story.append(HRFlowable(width="22%", thickness=2.2, color=TEAL, spaceBefore=3, spaceAfter=10, hAlign="LEFT"))
abstract = """
The common-source (CS) configuration is the most widely used MOSFET stage for voltage amplification
and is therefore a central experiment in an electronics laboratory. This project presents an
interactive, browser-based visualization of the drain and transfer characteristics of an
enhancement-mode NMOS transistor connected in the CS configuration. A Shichman–Hodges square-law
model with channel-length modulation is used to compute the drain current over the cutoff, triode
and saturation regions. The drain characteristics are obtained by sweeping V<sub>DS</sub> for fixed
values of V<sub>GS</sub>, while the transfer characteristic is obtained by sweeping V<sub>GS</sub> at
a fixed V<sub>DS</sub>. A DC load line is superimposed on the output family and its intersection
with the device curve is solved numerically to locate the quiescent point. The visualization reports
the operating region, transconductance, gate overdrive and power dissipation in real time, and allows
the device parameters to be varied. For the nominal design (V<sub>DD</sub> = 12 V, R<sub>D</sub> = 2.2 kΩ,
V<sub>th</sub> = 2.0 V, k<sub>n</sub> = 0.5 mA/V², λ = 0.02 V<sup>-1</sup>), the quiescent point at
V<sub>GS</sub> = 4.0 V is (9.39 V, 1.19 mA) with g<sub>m</sub> = 1.20 mS. The results reproduce the
expected square-law behaviour and demonstrate how the load line and bias choice control the available
output swing. The work is intended as a compact teaching aid that makes the link between device
equations, measured-style curves and circuit design visible in one place.
"""
story.append(P(abstract, ParagraphStyle("AbstractBody", parent=Body, fontSize=10.0, leading=14.2, spaceAfter=5)))
story.append(Spacer(1, 2))
story.append(P("<b>Keywords:</b> MOSFET, common-source amplifier, drain characteristics, transfer characteristics, quiescent point, transconductance, interactive visualization.", Small))
story.append(PageBreak())

# ---------- table of contents ----------
story.append(P("TABLE OF CONTENTS", TOCHeading))
story.append(HRFlowable(width="100%", thickness=0.8, color=LINE, spaceBefore=0, spaceAfter=10))
toc = TableOfContents()
toc.levelStyles = [TOCH1, TOCH2]
toc.dotsMinLevel = 0
toc.tableStyle = TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
])
story.append(toc)

# lists
story.append(P("LIST OF FIGURES", ListHeading))
fig_lines = [
    ("Figure 1.1", "NMOS common-source test circuit", "5"),
    ("Figure 3.1", "Characterization workflow", "7"),
    ("Figure 4.1", "Interactive visualization dashboard", "8"),
    ("Figure 5.1", "Drain characteristics with DC load line and quiescent point", "9"),
    ("Figure 5.2", "Transfer characteristics and transconductance tangent", "10"),
    ("Figure 5.3", "Transconductance versus gate–source voltage", "11"),
]
for num, text, page_no in fig_lines:
    story.append(Paragraph(f"<b>{num}</b>&nbsp;&nbsp; {text} <font color='#7b8ca3'>— p. {page_no}</font>", ListText))
story.append(P("LIST OF TABLES", ListHeading))
tab_lines = [
    ("Table 3.1", "Nominal model and bias parameters", "6"),
    ("Table 5.1", "Quiescent-point data for the output family", "10"),
    ("Table 5.2", "Summary of extracted performance metrics", "11"),
]
for num, text, page_no in tab_lines:
    story.append(Paragraph(f"<b>{num}</b>&nbsp;&nbsp; {text} <font color='#7b8ca3'>— p. {page_no}</font>", ListText))
story.append(PageBreak())

# ---------- 1 introduction ----------
story.append(P("1. Introduction", H1))
story.append(P("1.1 Background and motivation", H2))
story.append(P("""
The metal–oxide–semiconductor field-effect transistor (MOSFET) is the dominant active device in
modern analog and digital integrated circuits. Its insulated gate draws almost no steady-state
current, so the device can be controlled by voltage rather than current. When the source terminal
is shared by the input and output loops, the transistor is said to be in the common-source (CS)
configuration. The gate–source voltage sets the channel conductivity, the drain–source voltage
determines the operating region, and a drain resistor converts the drain current into an output
voltage. This is the basic building block of voltage amplifiers, active loads, current sources,
switches and many sensor front ends.
"""))
story.append(P("""
Characterizing the device is therefore an essential first step in analog design. The <i>drain</i> or
<i>output</i> characteristic plots I<sub>D</sub> against V<sub>DS</sub> for several fixed values of
V<sub>GS</sub>, while the <i>transfer</i> characteristic plots I<sub>D</sub> against V<sub>GS</sub>
at a fixed V<sub>DS</sub>. Together they reveal the threshold voltage, the transconductance
parameter, the onset of saturation, the output resistance and the effect of channel-length
modulation. In a conventional laboratory these curves are traced point by point using two supplies
and a pair of meters, or with a semiconductor parameter analyzer. The measurement is instructive but
time-consuming, and the resulting plots are usually static.
"""))
story.append(P("""
This project addresses that limitation by combining the standard device equations with an interactive
web visualization. The user can change the gate bias, supply voltage, load resistor, threshold
voltage, transconductance parameter and channel-length modulation, and immediately see the curves,
the load line and the quiescent point respond. The same model is then used to produce a compact
laboratory report with reproducible figures and tabulated results.
"""))
story.append(P("1.2 Objectives", H2))
for item in bullet_list([
    "Model an enhancement-mode NMOS transistor operating in the common-source configuration using the Shichman–Hodges square-law equations.",
    "Obtain the drain characteristics (I<sub>D</sub> versus V<sub>DS</sub>) for a family of gate–source voltages.",
    "Obtain the transfer characteristic (I<sub>D</sub> versus V<sub>GS</sub>) at a fixed drain–source voltage in saturation.",
    "Locate the quiescent point from the intersection of the device curve and the DC load line, and extract V<sub>th</sub>, k<sub>n</sub> and g<sub>m</sub>.",
    "Build an interactive visualization and document the method, results and limitations in a laboratory report.",
]):
    story.append(item)
story.append(P("1.3 Problem statement and scope", H2))
story.append(P("""
The problem is to characterize a MOSFET in the CS configuration and to make the relationship between
the device equations, the measured-style curves and the circuit bias easy to explore. The scope of
this work is limited to a single enhancement-mode NMOS device under DC bias at room temperature. The
model includes the square-law channel, channel-length modulation and a resistive drain load, but it
does not include subthreshold conduction, mobility degradation, temperature dependence, parasitic
capacitances or high-frequency effects. The numerical values are representative of a small-signal
NMOS and are intended for teaching and visualization rather than for predicting a specific part.
"""))
story.append(P("1.4 Relevant theory and circuit", H2))
story.append(P("""
Figure 1.1 shows the test circuit. The source is grounded, the gate is biased at V<sub>GS</sub> and
the drain is connected to the supply through R<sub>D</sub>. The drain current is measured in the
drain branch and the drain–source voltage is measured across the device. Depending on the terminal
voltages, the MOSFET operates in cutoff, triode or saturation.
"""))
story.append(figure("fig1_circuit.png", 15.4,
                    "Figure 1.1. NMOS common-source test circuit and the three regions of operation."))
story.append(P("In cutoff, V<sub>GS</sub> ≤ V<sub>th</sub> and no inversion channel is formed:"))
story.append(equation("I<sub>D</sub> = 0 &nbsp;&nbsp;&nbsp;&nbsp; (V<sub>GS</sub> ≤ V<sub>th</sub>) &nbsp;&nbsp;&nbsp;&nbsp; (1)"))
story.append(P("In triode, the channel is continuous and the device behaves as a voltage-controlled resistor:"))
story.append(equation("I<sub>D</sub> = k<sub>n</sub>[(V<sub>GS</sub> − V<sub>th</sub>)V<sub>DS</sub> − ½V<sub>DS</sub>²](1 + λV<sub>DS</sub>) &nbsp;&nbsp;&nbsp;&nbsp; (V<sub>DS</sub> &lt; V<sub>GS</sub> − V<sub>th</sub>) &nbsp;&nbsp;&nbsp;&nbsp; (2)"))
story.append(P("In saturation, the channel pinches off near the drain and the current is approximately independent of V<sub>DS</sub>:"))
story.append(equation("I<sub>D</sub> = ½k<sub>n</sub>(V<sub>GS</sub> − V<sub>th</sub>)²(1 + λV<sub>DS</sub>) &nbsp;&nbsp;&nbsp;&nbsp; (V<sub>DS</sub> ≥ V<sub>GS</sub> − V<sub>th</sub>) &nbsp;&nbsp;&nbsp;&nbsp; (3)"))
story.append(P("""
The small-signal transconductance in saturation is the slope of the transfer characteristic:
g<sub>m</sub> = ∂I<sub>D</sub>/∂V<sub>GS</sub> = k<sub>n</sub>(V<sub>GS</sub> − V<sub>th</sub>)(1 + λV<sub>DS</sub>).
The external circuit imposes the DC load line I<sub>D</sub> = (V<sub>DD</sub> − V<sub>DS</sub>)/R<sub>D</sub>,
and its intersection with the device curve is the quiescent point Q.
"""))

# ---------- 2 literature ----------
story.append(P("2. Literature Review", H1))
story.append(P("2.1 Device modelling", H2))
story.append(P("""
The square-law MOSFET model originates from the gradual-channel approximation and was popularized
for circuit simulation by Shichman and Hodges in 1968. It expresses the drain current in terms of the
gate overdrive and the drain–source voltage using a small number of parameters: threshold voltage,
transconductance parameter and channel-length modulation. The model is the basis of the Level-1
MOSFET model in SPICE and remains the first model taught in most electronics courses because it gives
closed-form expressions for the operating point, transconductance and output resistance. More advanced
models such as BSIM add short-channel effects, subthreshold conduction, mobility degradation and
charge conservation, but they obscure the basic device behaviour that a first laboratory is intended
to demonstrate.
"""))
story.append(P("2.2 Characterization practice", H2))
story.append(P("""
Traditional characterization uses a curve tracer or a source-measure unit to sweep one terminal while
holding the others fixed. The resulting family of curves is read manually to extract V<sub>th</sub>,
k<sub>n</sub> and the saturation slope. Modern automated setups use LabVIEW or Python to control the
instrument and plot the data. Circuit simulators such as LTspice, ngspice and Multisim are widely used
for pre-lab work, and educational web applets such as Falstad's circuit simulator provide immediate
visual feedback. These tools are powerful, but the full simulators have a steep learning curve for a
first-year student, while many applets show only a single curve or hide the underlying equations.
"""))
story.append(P("2.3 Gap addressed by this work", H2))
story.append(P("""
There is a useful middle ground between a full SPICE deck and a static textbook plot: a small,
transparent model that exposes the equations and lets the student manipulate the bias directly. The
present work fills that gap with a dependency-free web page that plots the drain and transfer
characteristics, superimposes the load line, solves for the quiescent point and reports the small-signal
parameters. The same equations are used to generate the figures in this report, so the visualization
and the written analysis remain consistent.
"""))

# ---------- 3 methodology ----------
story.append(P("3. Methodology", H1))
story.append(P("3.1 Device model and parameter selection", H2))
story.append(P("""
The NMOS device is represented by the Shichman–Hodges equations (1)–(3). The nominal parameters were
chosen to resemble a small enhancement-mode NMOS suitable for a 12 V laboratory supply. The threshold
voltage is 2.0 V, the transconductance parameter is 0.5 mA/V² and the channel-length modulation
coefficient is 0.02 V<sup>-1</sup>. The drain resistor is 2.2 kΩ and the supply is 12 V. These values
place the quiescent point comfortably inside saturation at V<sub>GS</sub> = 4 V and allow the entire
output family to be displayed on a single graph. Table 3.1 lists the parameters.
"""))
param_data = [
    [P("Parameter", TableHead), P("Symbol", TableHead), P("Value", TableHead), P("Unit", TableHead)],
    [P("Threshold voltage", TableText), P("V<sub>th</sub>", TableText), P("2.0", TableText), P("V", TableText)],
    [P("Transconductance parameter", TableText), P("k<sub>n</sub>", TableText), P("0.50", TableText), P("mA/V²", TableText)],
    [P("Channel-length modulation", TableText), P("λ", TableText), P("0.020", TableText), P("V<sup>-1</sup>", TableText)],
    [P("Supply voltage", TableText), P("V<sub>DD</sub>", TableText), P("12", TableText), P("V", TableText)],
    [P("Drain resistor", TableText), P("R<sub>D</sub>", TableText), P("2.2", TableText), P("kΩ", TableText)],
    [P("Gate–source bias at Q", TableText), P("V<sub>GS</sub>", TableText), P("4.0", TableText), P("V", TableText)],
    [P("Drain–source voltage for transfer", TableText), P("V<sub>DS</sub>", TableText), P("10", TableText), P("V", TableText)],
]
story.append(KeepTogether([
    styled_table(param_data, [7.2 * cm, 3.0 * cm, 3.0 * cm, 3.4 * cm]),
    table_caption("Table 3.1. Nominal model and bias parameters used throughout the work."),
]))
story.append(P("3.2 Drain characteristics", H2))
story.append(P("""
For the output family, V<sub>GS</sub> is held at each of eight values from 2.5 V to 6.0 V in 0.5 V
steps. For every value, V<sub>DS</sub> is swept from 0 V to V<sub>DD</sub> in small increments and
I<sub>D</sub> is evaluated from equations (1)–(3). The resulting curves are plotted on a common set
of axes. A DC load line is drawn from (0, V<sub>DD</sub>/R<sub>D</sub>) to (V<sub>DD</sub>, 0). The
quiescent point for the selected gate bias is found by solving
I<sub>D</sub>(V<sub>GS</sub>, V<sub>DS</sub>) = (V<sub>DD</sub> − V<sub>DS</sub>)/R<sub>D</sub>
with a bisection search. Because the device current increases with V<sub>DS</sub> in saturation while
the load-line current decreases, the root is unique.
"""))
story.append(P("3.3 Transfer characteristics", H2))
story.append(P("""
For the transfer characteristic, V<sub>DS</sub> is fixed at 10 V, which keeps the device in
saturation for all gate voltages above threshold. V<sub>GS</sub> is swept from 0 V to 6 V and
I<sub>D</sub> is evaluated from the saturation equation. The threshold voltage is read from the
turn-on point, and k<sub>n</sub> is obtained from the square-law fit. The transconductance is computed
by a central difference of the transfer curve, which avoids relying on the analytic derivative and
therefore provides an independent numerical check. Figure 3.1 summarizes the workflow.
"""))
story.append(figure("fig3_flow.png", 15.4,
                    "Figure 3.1. Characterization workflow from model definition to visualization and reporting."))

# ---------- 4 implementation ----------
story.append(P("4. Implementation", H1))
story.append(P("4.1 Circuit and numerical implementation", H2))
story.append(P("""
The test circuit follows the standard CS topology: the source is grounded, the gate is driven by a
variable DC source and the drain is connected to V<sub>DD</sub> through R<sub>D</sub>. The model is
implemented as a small JavaScript function that returns the drain current for any pair of terminal
voltages. The output characteristics are produced by evaluating this function on a dense grid of
V<sub>DS</sub> values, and the transfer characteristic is produced by evaluating it on a dense grid
of V<sub>GS</sub> values. The quiescent point is found with 70 bisection iterations, which is more
than sufficient for the precision displayed in the interface.
"""))
code = """<font face="LibMono" size="7.6">function drainCurrent(vgs, vds) {
  const vov = vgs - vth;
  if (vov &lt;= 0) return 0;                 // cutoff
  const f = 1 + lambda * vds;
  if (vds &lt; vov)                          // triode
    return kn * (vov * vds - 0.5 * vds * vds) * f;
  return 0.5 * kn * vov * vov * f;          // saturation
}</font>"""
code_table = Table([[Paragraph(code, ParagraphStyle("Code", parent=Body, fontName="LibMono",
                                                   fontSize=7.6, leading=11.5, alignment=TA_LEFT))]],
                   colWidths=[CONTENT_W])
code_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4f7fb")),
    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#dce4ef")),
    ("LEFTPADDING", (0, 0), (-1, -1), 9),
    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
]))
story.append(KeepTogether([Spacer(1, 2), code_table, table_caption("Listing 1. Core of the square-law NMOS model used by the visualization.")]))
story.append(P("4.2 Interactive visualization", H2))
story.append(P("""
The front end is a single-page application built with HTML, CSS and vanilla JavaScript. The
characteristic curves are drawn as SVG paths, so they remain sharp at any zoom level and can be
styled with the rest of the design. The control panel exposes V<sub>GS</sub>, V<sub>DD</sub>,
R<sub>D</sub>, V<sub>th</sub>, k<sub>n</sub> and λ. Changing any slider re-computes the curves, the
load line, the quiescent point, the operating region and the tabulated data immediately. A tab
switches between the drain and transfer views; a sweep button animates V<sub>GS</sub>; a tooltip
reads out the current at the cursor; and the table can be copied or exported as CSV. Figure 4.1 shows
the main workspace.
"""))
story.append(figure("fig4_dashboard.png", 15.6,
                    "Figure 4.1. Interactive visualization dashboard: bias controls, characteristic plot and live operating-point readout."))
story.append(P("4.3 Report generation", H2))
story.append(P("""
The figures in this report are produced by a Python script using NumPy and Matplotlib, and the
document itself is assembled with ReportLab. A single parameter set is shared by the web application
and the figure generator, so the numerical values in the text, tables and plots agree. The report is
built from the same model rather than from manually transcribed numbers, which reduces the risk of
inconsistency between the visualization and the written analysis.
"""))
story.append(P("4.4 Challenges and solutions", H2))
story.append(P("""
Three practical difficulties arose during implementation. First, the SVG chart is re-rendered on every
slider movement; drawing the full family at a high sampling density made the interaction sluggish, so
the number of samples was reduced and the curves are clipped to the plot area. Second, the load-line
intersection must be found even when the operating point moves from saturation into triode; a simple
analytic solution is not valid across all regions, so a bracketed bisection search was used instead.
Third, the chart labels must remain readable when the device parameters change the current scale; the
axis maximum is chosen from the data with a small headroom and the ticks are generated from a
"nice number" rule. These choices keep the interface responsive and the plots well scaled.
"""))

# ---------- 5 results ----------
story.append(P("5. Results", H1))
story.append(P("5.1 Drain characteristics", H2))
story.append(P("""
Figure 5.1 shows the output family for V<sub>GS</sub> = 2.5 V to 6.0 V. Each curve rises almost
linearly for small V<sub>DS</sub>, bends over at V<sub>DS</sub> ≈ V<sub>GS</sub> − V<sub>th</sub>,
and then becomes nearly horizontal. The nearly flat region is saturation; its small positive slope is
caused by channel-length modulation. The curve for V<sub>GS</sub> = 2.5 V has the smallest overdrive
and therefore the lowest saturation current, while the curve for V<sub>GS</sub> = 6.0 V has the
largest. The dashed red line is the DC load line for R<sub>D</sub> = 2.2 kΩ; its intersection with
the V<sub>GS</sub> = 4.0 V curve is the quiescent point Q = (9.39 V, 1.19 mA). At this bias the
transistor is in saturation, as required for a linear amplifier.
"""))
story.append(figure("fig5_output.png", 15.2,
                    "Figure 5.1. Drain characteristics for VGS = 2.5 V to 6.0 V, with the DC load line and the quiescent point at VGS = 4.0 V."))
story.append(P("5.2 Transfer characteristics", H2))
story.append(P("""
The transfer characteristic in Figure 5.2 was obtained at V<sub>DS</sub> = 10 V. The current is
essentially zero below V<sub>th</sub> = 2.0 V and follows a square law above threshold. The extracted
threshold voltage is 2.0 V and the curve passes through 1.20 mA at V<sub>GS</sub> = 4.0 V. The
dashed amber line is the tangent at the quiescent point; its slope is the transconductance,
g<sub>m</sub> = 1.20 mS. The tangent is a good local approximation for small signals around the bias
point, but it deviates from the curve for large excursions because the transfer characteristic is
quadratic rather than linear.
"""))
story.append(figure("fig5_transfer.png", 15.2,
                    "Figure 5.2. Transfer characteristic at VDS = 10 V, showing the threshold voltage and the tangent used to extract gm."))

story.append(P("5.3 Quiescent points and transconductance", H2))
story.append(P("""
Table 5.1 lists the quiescent point for each gate voltage in the family. As V<sub>GS</sub> increases,
the drain current rises and the drain voltage falls along the load line. For V<sub>GS</sub> = 6.0 V,
the operating point moves into the triode region because the required current is larger than the
saturation current available at the resulting drain voltage. This is a useful design observation: a
larger gate drive does not always keep the device in saturation when a resistive load is present.
"""))
q_data = [
    [P("V<sub>GS</sub> (V)", TableHead), P("V<sub>DS,Q</sub> (V)", TableHead),
     P("I<sub>D,Q</sub> (mA)", TableHead), P("Region", TableHead), P("g<sub>m</sub> (mS)", TableHead)],
]
q_rows = [
    ("2.5", "11.83", "0.08", "Saturation", "0.31"),
    ("3.0", "11.33", "0.31", "Saturation", "0.61"),
    ("3.5", "10.50", "0.68", "Saturation", "0.91"),
    ("4.0", "9.39", "1.19", "Saturation", "1.19"),
    ("4.5", "8.01", "1.81", "Saturation", "1.45"),
    ("5.0", "6.41", "2.54", "Saturation", "1.69"),
    ("5.5", "4.64", "3.35", "Saturation", "1.91"),
    ("6.0", "3.11", "4.04", "Triode", "1.65"),
]
for row in q_rows:
    q_data.append([P(cell, TableText) for cell in row])
story.append(KeepTogether([
    styled_table(q_data, [2.8 * cm, 3.3 * cm, 3.3 * cm, 3.2 * cm, 3.2 * cm], align="CENTER"),
    table_caption("Table 5.1. Quiescent-point data for the output family (VDD = 12 V, RD = 2.2 kΩ)."),
]))
story.append(P("""
Figure 5.3 plots the transconductance in saturation against gate–source voltage. In the square-law
model g<sub>m</sub> is proportional to the gate overdrive, so the plot is a straight line that starts
at V<sub>th</sub>. The value at the quiescent point is 1.20 mS. The numerical derivative used for
this plot agrees with the analytic expression to the precision shown, which confirms that the
implementation and the small-signal interpretation are consistent.
"""))
story.append(figure("fig5_gm.png", 15.2,
                    "Figure 5.3. Transconductance versus gate–source voltage in saturation; the quiescent point is marked."))
story.append(P("5.4 Summary of extracted metrics", H2))
summary_data = [
    [P("Metric", TableHead), P("Value", TableHead), P("How obtained", TableHead)],
    [P("Threshold voltage, V<sub>th</sub>", TableText), P("2.0 V", TableText), P("Turn-on point of the transfer curve", TableText)],
    [P("Transconductance parameter, k<sub>n</sub>", TableText), P("0.50 mA/V²", TableText), P("Square-law fit above threshold", TableText)],
    [P("Quiescent current, I<sub>D,Q</sub>", TableText), P("1.19 mA", TableText), P("Load-line intersection at V<sub>GS</sub> = 4 V", TableText)],
    [P("Quiescent voltage, V<sub>DS,Q</sub>", TableText), P("9.39 V", TableText), P("Load-line intersection at V<sub>GS</sub> = 4 V", TableText)],
    [P("Transconductance at Q, g<sub>m</sub>", TableText), P("1.20 mS", TableText), P("Slope of transfer curve at Q", TableText)],
    [P("Output resistance, r<sub>o</sub> = 1/(λI<sub>D</sub>)", TableText), P("≈ 42 kΩ", TableText), P("Channel-length modulation parameter", TableText)],
]
story.append(KeepTogether([
    styled_table(summary_data, [6.7 * cm, 4.1 * cm, 5.2 * cm]),
    table_caption("Table 5.2. Summary of the extracted device and bias metrics at the nominal operating point."),
]))
story.append(P("""
The results are internally consistent: the same threshold voltage, transconductance parameter and
channel-length modulation coefficient reproduce the output family, the transfer curve and the
quiescent points. The small difference between the analytic g<sub>m</sub> and the numerical slope is
below the display precision. The output resistance is approximate because λ is treated as a constant
in the model, whereas in a real device it varies with bias.
"""))

# ---------- 6 discussion ----------
story.append(P("6. Discussion", H1))
story.append(P("6.1 Interpretation", H2))
story.append(P("""
The curves show the three expected regions of MOSFET operation. In the triode region the channel
behaves as a voltage-controlled resistor, so the current rises with V<sub>DS</sub>. As V<sub>DS</sub>
approaches the overdrive voltage, the channel pinches off near the drain and the current saturates.
The residual slope in saturation is the channel-length modulation, which gives the device a finite
output resistance and therefore limits the maximum voltage gain of a simple CS stage. The load line
makes the bias choice explicit: the quiescent point is fixed by both the device and the external
circuit, not by the gate voltage alone.
"""))
story.append(P("6.2 Comparison with expected behaviour", H2))
story.append(P("""
The square-law model predicts that the saturation current should scale with the square of the gate
overdrive. The values in Table 5.1 follow this trend closely: doubling the overdrive from 0.5 V to
1.0 V increases the current by roughly a factor of four, and the same scaling is visible in the
transfer curve. The transconductance is linear in the overdrive, as expected from
g<sub>m</sub> = k<sub>n</sub>(V<sub>GS</sub> − V<sub>th</sub>)(1 + λV<sub>DS</sub>). These trends match
the textbook treatment of the Level-1 MOSFET model and the behaviour of a real device at moderate
current levels, although real short-channel devices show a softer turn-on and a more pronounced
output conductance.
"""))
story.append(P("6.3 Limitations", H2))
for item in bullet_list([
    "The model is generic and is not fitted to a measured device; the numerical values are representative rather than commercial.",
    "Subthreshold conduction, mobility degradation, temperature effects and parasitic capacitances are not included.",
    "The DC analysis does not predict bandwidth, slew rate or high-frequency gain.",
    "The load is a single resistor; active loads and current-source biasing are outside the scope of this experiment.",
]):
    story.append(item)
story.append(P("6.4 Potential improvements", H2))
story.append(P("""
Future versions could import measured I–V data and fit V<sub>th</sub>, k<sub>n</sub> and λ directly
from the measurements, add a temperature-dependent mobility model, and include a small-signal AC
analysis so that the gain and bandwidth of the CS stage can be explored. A graphical load-line tool
that lets the user drag R<sub>D</sub> and V<sub>DD</sub> while watching the available output swing
would make the design trade-off even more intuitive. Finally, the visualization could be extended to
a PMOS device and to a CMOS inverter, which would connect the experiment to digital circuit design.
"""))

# ---------- 7 conclusion ----------
story.append(P("7. Conclusion", H1))
story.append(P("""
This project set out to obtain and visualize the drain and transfer characteristics of an NMOS
transistor connected in the common-source configuration. A Shichman–Hodges model was implemented in
an interactive web application and used to generate the output family, the transfer curve, the DC
load line and the quiescent point. For the nominal design, the device turns on at 2.0 V, delivers
1.19 mA at V<sub>DS</sub> = 9.39 V when V<sub>GS</sub> = 4.0 V, and has a transconductance of
1.20 mS at that bias. The extracted trends follow the expected square-law behaviour, and the load
line explains why the operating point moves from saturation to triode as the gate drive is increased.
The objectives of the experiment were therefore met. The main open questions concern real-device
effects: fitting the model to measured data and extending the analysis to temperature, short-channel
effects and high-frequency behaviour would make the tool more useful for practical design.
"""))

# ---------- 8 references ----------
story.append(P("8. References", H1))
refs = [
    "S. M. Sze and K. K. Ng, <i>Physics of Semiconductor Devices</i>, 3rd ed. Hoboken, NJ, USA: Wiley, 2007.",
    "H. Shichman and D. A. Hodges, “Modeling and simulation of insulated-gate field-effect transistor switching circuits,” <i>IEEE Journal of Solid-State Circuits</i>, vol. SC-3, no. 3, pp. 285–289, Sep. 1968.",
    "A. S. Sedra and K. C. Smith, <i>Microelectronic Circuits</i>, 8th ed. New York, NY, USA: Oxford University Press, 2019.",
    "B. Razavi, <i>Fundamentals of Microelectronics</i>, 3rd ed. Hoboken, NJ, USA: Wiley, 2021.",
    "R. L. Boylestad and L. Nashelsky, <i>Electronic Devices and Circuit Theory</i>, 11th ed. Boston, MA, USA: Pearson, 2013.",
    "M. H. Rashid, <i>Microelectronic Circuits: Analysis and Design</i>, 3rd ed. Boston, MA, USA: Cengage Learning, 2016.",
    "Analog Devices, “MOSFET characterization using the 4200A-SCS parameter analyzer,” Application Note, 2020.",
    "Analog Devices, “LTspice simulator,” 2024. [Online]. Available: https://www.analog.com/ltspice",
]
for i, ref in enumerate(refs, 1):
    story.append(Paragraph(f"[{i}]&nbsp;&nbsp; {ref}", ParagraphStyle(
        "Ref", parent=Body, fontSize=8.8, leading=12.0, leftIndent=18,
        firstLineIndent=-18, spaceAfter=3.5, alignment=TA_LEFT)))

# ---------------------------------------------------------------- build
doc = ReportDoc(
    str(OUT),
    pagesize=A4,
    leftMargin=ML,
    rightMargin=MR,
    topMargin=MT,
    bottomMargin=MB,
    title="Drain and Transfer Characteristics of a MOSFET in Common-Source Configuration",
    author=details["student_name"],
    subject="Basic Electronics Devices Laboratory Project",
    creator="ReportLab",
)
doc.multiBuild(story, maxPasses=4)
print("Wrote", OUT)
