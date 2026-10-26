#!/usr/bin/env python3
"""Generate the figures used in the MOSFET common-source report."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle, Rectangle
from matplotlib.lines import Line2D

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)

# ---------------- device model ----------------
VTH = 2.0
KN = 0.5          # mA/V^2
LAMBDA = 0.02     # 1/V
VDD = 12.0
RD = 2.2          # kohm
VGS_FAMILY = np.arange(2.5, 6.01, 0.5)
VDS_TRANSFER = 10.0

TEAL = "#0d9488"
TEAL_LIGHT = "#5eead4"
NAVY = "#0b1b33"
MUTED = "#64748b"
CORAL = "#ef6f6c"
AMBER = "#f59e0b"
GRID = "#dce4ef"
PALETTE = ["#9fe8e1", "#7ddcd5", "#5bcec9", "#45bfc1",
           "#55a8d8", "#6a8ee6", "#7b73e0", "#8b5cf6"]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9.5,
    "axes.titlesize": 11,
    "axes.labelsize": 9.5,
    "axes.edgecolor": "#9fb0c5",
    "axes.linewidth": 0.8,
    "axes.labelcolor": "#33465e",
    "xtick.color": "#5b6b80",
    "ytick.color": "#5b6b80",
    "grid.color": GRID,
    "grid.linewidth": 0.7,
    "legend.frameon": False,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.06,
})


def drain_current(vgs, vds):
    vov = vgs - VTH
    if vov <= 0:
        return 0.0
    lam = 1.0 + LAMBDA * vds
    if vds < vov:
        return KN * (vov * vds - 0.5 * vds * vds) * lam
    return 0.5 * KN * vov * vov * lam


def quiescent(vgs):
    if vgs <= VTH:
        return VDD, 0.0
    f = lambda v: drain_current(vgs, v) - (VDD - v) / RD
    lo, hi = 0.0, VDD
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    vds = 0.5 * (lo + hi)
    return vds, drain_current(vgs, vds)


# ---------------- Figure 1: circuit ----------------
def circuit_diagram():
    fig, ax = plt.subplots(figsize=(6.4, 3.7))
    ax.set_xlim(0, 11.8)
    ax.set_ylim(0, 6.7)
    ax.axis("off")
    lw = 1.55
    wire = "#213a59"

    def line(x1, y1, x2, y2, **kw):
        width = kw.pop("lw", lw)
        ax.plot([x1, x2], [y1, y2], color=wire, lw=width,
                solid_capstyle="round", **kw)

    # VDD rail and drain resistor
    line(9.0, 6.15, 9.0, 5.55)
    ax.text(9.18, 6.25, r"$+V_{DD}$", fontsize=10, color=NAVY,
            fontweight="bold", ha="left")
    ys = np.linspace(5.55, 4.65, 7)
    xs = [9.0, 8.78, 9.22, 8.78, 9.22, 8.78, 9.0]
    ax.plot(xs, ys, color=wire, lw=lw, solid_capstyle="round")
    ax.text(9.24, 5.10, r"$R_D$", fontsize=9.5, color=NAVY, va="center")
    line(9.0, 4.65, 9.0, 4.32)

    # ammeter in drain branch
    ax.add_patch(Circle((9.0, 4.08), 0.23, facecolor="white",
                        edgecolor=wire, lw=lw, zorder=3))
    ax.text(9.0, 4.08, "A", ha="center", va="center", fontsize=8.6,
            color=NAVY, zorder=4)
    line(9.0, 3.85, 9.0, 3.62)
    ax.annotate("", xy=(9.0, 3.92), xytext=(9.0, 3.56),
                arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=1.25))
    ax.text(9.15, 3.74, r"$I_D$", fontsize=9, color=TEAL, fontweight="bold")

    # NMOS: drain lead, channel, source lead
    line(9.0, 3.62, 9.38, 3.62)
    line(9.38, 3.62, 9.38, 3.30)
    line(9.38, 3.30, 9.38, 2.30, lw=1.8)
    line(9.38, 2.30, 9.38, 1.94)
    line(9.38, 1.94, 9.02, 1.94)
    line(9.02, 1.94, 9.02, 1.30)

    # gate plate and gate lead
    line(8.86, 3.26, 8.86, 2.34, lw=1.8)
    line(8.86, 2.80, 6.95, 2.80)
    line(6.95, 2.80, 6.95, 2.58)

    # source ground
    for w, y in [(0.42, 1.05), (0.30, 0.90), (0.18, 0.75)]:
        line(9.02 - w, y, 9.02 + w, y, lw=1.4)
    ax.text(9.52, 1.10, r"$S$", fontsize=9, color=NAVY)
    ax.text(9.52, 3.40, r"$D$", fontsize=9, color=NAVY)
    ax.text(8.68, 3.12, r"$G$", fontsize=9, color=NAVY)

    # gate bias source between gate and ground
    ax.add_patch(Circle((6.95, 2.34), 0.24, facecolor="white",
                        edgecolor=wire, lw=lw, zorder=3))
    line(6.95, 2.34, 6.95, 1.05)
    ax.text(6.70, 2.42, "+", fontsize=9, color=NAVY, ha="center")
    ax.text(6.70, 2.18, "−", fontsize=9, color=NAVY, ha="center")
    for w, y in [(0.42, 1.05), (0.30, 0.90), (0.18, 0.75)]:
        line(6.95 - w, y, 6.95 + w, y, lw=1.4)
    ax.text(6.58, 2.68, r"$V_{GS}$", fontsize=9, color=NAVY, ha="right")

    # voltmeter across drain-source
    vx, vy = 11.05, 2.98
    line(9.62, 3.62, 10.72, 3.62)
    line(10.72, 3.62, 10.72, 3.22)
    line(9.62, 1.94, 10.72, 1.94)
    line(10.72, 1.94, 10.72, 2.74)
    ax.add_patch(Circle((vx, vy), 0.25, facecolor="white",
                        edgecolor=wire, lw=lw, zorder=3))
    ax.text(vx, vy, "V", ha="center", va="center", fontsize=8.6,
            color=NAVY, zorder=4)
    ax.text(10.98, 3.34, r"$V_{DS}$", fontsize=9, color=NAVY, va="bottom")

    # device equations panel on the left
    eq = (
        "Device relations\n"
        "Cut-off:  $V_{GS} \\leq V_{th}$,  $I_D = 0$\n"
        "Triode:  $I_D = k_n[(V_{GS}-V_{th})V_{DS}-V_{DS}^2/2]$\n"
        "Saturation:  $I_D = \\frac{1}{2}k_n(V_{GS}-V_{th})^2(1+\\lambda V_{DS})$"
    )
    ax.text(0.18, 4.86, eq, fontsize=8.0, color=NAVY, va="top", linespacing=1.7,
            bbox=dict(boxstyle="round,pad=0.42", facecolor="#f8fbfe",
                      edgecolor="#dce4ef", lw=0.8))

    ax.text(0.15, 6.25, "NMOS common-source test circuit", fontsize=10.5,
            color=NAVY, fontweight="bold")
    ax.text(0.15, 5.92, "Source grounded  ·  drain loaded by $R_D$  ·  gate biased by $V_{GS}$",
            fontsize=8.2, color=MUTED)
    ax.text(0.15, 0.35, "Nominal bias: $V_{DD}=12$ V, $R_D=2.2$ k$\\Omega$, $V_{GS}=4$ V",
            fontsize=8.2, color=MUTED)
    ax.annotate("Q1", xy=(8.92, 2.78), xytext=(7.72, 3.52), fontsize=9,
                color=NAVY, arrowprops=dict(arrowstyle="-", color="#aab8ca", lw=0.9))
    fig.savefig(OUT / "fig1_circuit.png", dpi=220)
    plt.close(fig)


# ---------------- Figure 2: output characteristics ----------------
def output_characteristics():
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    vds = np.linspace(0, VDD, 500)
    for i, vgs in enumerate(VGS_FAMILY):
        ids = np.array([drain_current(vgs, v) for v in vds])
        selected = abs(vgs - 4.0) < 1e-9
        ax.plot(vds, ids, color=TEAL if selected else PALETTE[i],
                lw=2.35 if selected else 1.35,
                alpha=1.0 if selected else 0.82,
                label=r"$V_{GS}=4.0$ V" if selected else None,
                zorder=4 if selected else 2)
    # DC load line
    ax.plot([0, VDD], [VDD / RD, 0], ls=(0, (5, 4)), color=CORAL, lw=1.6,
            label="DC load line", zorder=3)
    qv, qi = quiescent(4.0)
    ax.plot([qv], [qi], "o", ms=7, mfc=NAVY, mec=TEAL_LIGHT, mew=2.4, zorder=8)
    ax.plot([0, qv], [qi, qi], ls=":", color="#9fb4d8", lw=1.0, zorder=5)
    ax.plot([qv, qv], [0, qi], ls=":", color="#9fb4d8", lw=1.0, zorder=5)
    ax.annotate(f"Q ({qv:.2f} V, {qi:.2f} mA)", xy=(qv, qi), xytext=(7.15, 1.82),
                fontsize=8.4, color=TEAL, fontweight="bold", ha="left",
                arrowprops=dict(arrowstyle="-", color=TEAL, lw=0.9))
    # region shading and labels
    ax.axvspan(0, 2.0, color="#fff7e6", alpha=0.55, lw=0, zorder=0)
    ax.text(1.0, 5.35, "triode", fontsize=8.2, color="#a16207", ha="center")
    ax.text(7.4, 5.35, "saturation", fontsize=8.2, color="#0b7e72", ha="center")
    ax.axvline(2.0, color="#cbd5e1", ls=(0, (3, 4)), lw=0.9)
    ax.set_xlim(0, VDD)
    ax.set_ylim(0, 6.0)
    ax.set_xlabel(r"Drain–source voltage, $V_{DS}$ (V)")
    ax.set_ylabel(r"Drain current, $I_D$ (mA)")
    ax.set_title("Drain characteristics  ·  $V_{GS}$ stepped from 2.5 V to 6.0 V",
                 loc="left", color=NAVY, pad=10)
    ax.grid(True, which="major", alpha=0.85)
    ax.set_axisbelow(True)
    handles = [
        Line2D([0], [0], color=TEAL, lw=2.4, label=r"$V_{GS}=4.0$ V (selected)"),
        Line2D([0], [0], color=PALETTE[0], lw=1.4, label=r"$V_{GS}$ family"),
        Line2D([0], [0], color=CORAL, lw=1.6, ls=(0, (5, 4)), label="DC load line"),
        Line2D([0], [0], marker="o", color="none", mfc=NAVY, mec=TEAL_LIGHT,
               mew=2.0, ms=6, label="Quiescent point Q"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.19),
              fontsize=7.8, ncol=4, handlelength=2.1, columnspacing=1.3)
    fig.savefig(OUT / "fig5_output.png", dpi=220)
    plt.close(fig)


# ---------------- Figure 3: transfer characteristics ----------------
def transfer_characteristics():
    fig, ax = plt.subplots(figsize=(6.4, 3.75))
    vgs = np.linspace(0, 6, 500)
    ids = np.array([drain_current(v, VDS_TRANSFER) for v in vgs])
    ax.axvspan(0, VTH, color="#eef2f8", alpha=0.9, lw=0, zorder=0)
    ax.plot(vgs, ids, color=TEAL, lw=2.4, zorder=4)
    ax.axvline(VTH, color="#b9c6d8", ls=(0, (3, 4)), lw=1.0)
    ax.text(VTH + 0.08, 4.72, r"$V_{th}=2.0$ V", fontsize=8.4, color="#7a8ca3")
    ax.text(1.0, 4.72, "cut-off", fontsize=8.2, color="#7a8ca3", ha="center")

    qi = drain_current(4.0, VDS_TRANSFER)
    gm = KN * (4.0 - VTH) * (1 + LAMBDA * VDS_TRANSFER)
    # tangent at Q
    tx = np.array([3.35, 4.65])
    ty = qi + gm * (tx - 4.0)
    ax.plot(tx, ty, color=AMBER, lw=1.4, ls=(0, (4, 3)), zorder=5,
            label=r"slope $= g_m$")
    ax.plot([0, 4.0], [qi, qi], ls=":", color="#9fb4d8", lw=1.0)
    ax.plot([4.0, 4.0], [0, qi], ls=":", color="#9fb4d8", lw=1.0)
    ax.plot([4.0], [qi], "o", ms=7, mfc=NAVY, mec=TEAL_LIGHT, mew=2.4, zorder=7)
    ax.annotate(f"Q ({4.0:.1f} V, {qi:.2f} mA)", xy=(4.0, qi), xytext=(3.15, 2.02),
                fontsize=8.4, color=TEAL, fontweight="bold", ha="right",
                arrowprops=dict(arrowstyle="-", color=TEAL, lw=0.9))
    ax.text(4.54, 0.53, rf"$g_m={gm:.2f}$ mS", fontsize=8.3,
            color="#a16207")
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 5.2)
    ax.set_xlabel(r"Gate–source voltage, $V_{GS}$ (V)")
    ax.set_ylabel(r"Drain current, $I_D$ (mA)")
    ax.set_title(r"Transfer characteristics  ·  $V_{DS}=10$ V", loc="left",
                 color=NAVY, pad=10)
    ax.grid(True, alpha=0.85)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", fontsize=8.0, bbox_to_anchor=(0.02, 0.90))
    fig.savefig(OUT / "fig5_transfer.png", dpi=220)
    plt.close(fig)


# ---------------- Figure 4: transconductance ----------------
def transconductance():
    fig, ax = plt.subplots(figsize=(6.4, 3.05))
    vgs = np.linspace(VTH, 6.0, 300)
    gm = KN * (vgs - VTH) * (1 + LAMBDA * VDS_TRANSFER)
    ax.plot(vgs, gm, color="#7c5cff", lw=2.2)
    ax.fill_between(vgs, 0, gm, color="#7c5cff", alpha=0.08)
    ax.plot([4.0], [1.2], "o", ms=6.5, mfc=NAVY, mec=TEAL_LIGHT, mew=2.2, zorder=5)
    ax.annotate(r"$V_{GS}=4$ V, $g_m=1.20$ mS", xy=(4.0, 1.2), xytext=(4.35, 0.62),
                fontsize=8.4, color=TEAL, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=TEAL, lw=0.9))
    ax.set_xlim(0, 6.2)
    ax.set_ylim(0, 2.35)
    ax.set_xlabel(r"Gate–source voltage, $V_{GS}$ (V)")
    ax.set_ylabel(r"$g_m$ (mS)")
    ax.set_title(r"Transconductance in saturation  ·  $V_{DS}=10$ V",
                 loc="left", color=NAVY, pad=9)
    ax.grid(True, alpha=0.85)
    ax.set_axisbelow(True)
    ax.axvspan(0, VTH, color="#eef2f8", alpha=0.8, lw=0)
    ax.text(1.0, 2.05, "cut-off", fontsize=8.0, color="#7a8ca3", ha="center")
    fig.savefig(OUT / "fig5_gm.png", dpi=220)
    plt.close(fig)


# ---------------- Figure 5: workflow ----------------
def workflow():
    fig, ax = plt.subplots(figsize=(6.4, 3.05))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.2)
    ax.axis("off")
    steps = [
        ("1", "Define the NMOS\nmodel and bias", "#e8fbf7", TEAL),
        ("2", "Sweep $V_{DS}$ for\neach fixed $V_{GS}$", "#eef4ff", "#3b82f6"),
        ("3", "Sweep $V_{GS}$ at\nfixed $V_{DS}$", "#f3f0ff", "#7c5cff"),
        ("4", "Extract $V_{th}$, $k_n$,\n$g_m$ and Q point", "#fff7e6", "#b45309"),
        ("5", "Visualize and\nreport the data", "#fdf2f2", "#dc5f5c"),
    ]
    w, h = 1.78, 1.30
    gap = 0.15
    for i, (num, text, face, edge) in enumerate(steps):
        x = 0.12 + i * (w + gap)
        y = 2.55
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.12",
                             facecolor=face, edgecolor=edge, lw=1.1)
        ax.add_patch(box)
        ax.text(x + 0.14, y + h - 0.25, num, fontsize=9.5, color=edge, fontweight="bold")
        ax.text(x + w / 2, y + h / 2 - 0.12, text, ha="center", va="center",
                fontsize=7.4, color=NAVY, linespacing=1.35)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + w + gap - 0.03, y + h / 2),
                        xytext=(x + w + 0.03, y + h / 2),
                        arrowprops=dict(arrowstyle="-|>", color="#9fb0c5", lw=1.2))
    ax.annotate("", xy=(8.7, 1.82), xytext=(1.05, 1.82),
                arrowprops=dict(arrowstyle="-|>", color="#cbd5e1", lw=1.0,
                                connectionstyle="arc3,rad=0.18"))
    ax.text(4.9, 1.12, "iterate model parameters until the simulated curves match the measured trend",
            fontsize=7.6, color=MUTED, ha="center", style="italic")
    ax.text(0.18, 4.62, "Characterization workflow", fontsize=10.5, color=NAVY, fontweight="bold")
    fig.savefig(OUT / "fig3_flow.png", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    circuit_diagram()
    output_characteristics()
    transfer_characteristics()
    transconductance()
    workflow()
    print("Figures written to", OUT)
    for vgs in VGS_FAMILY:
        v, i = quiescent(vgs)
        print(f"VGS={vgs:4.1f} V -> VDS={v:6.2f} V, ID={i:5.2f} mA")
    print(f"Transfer: ID(4V,10V)={drain_current(4,10):.3f} mA, gm={KN*2*(1+LAMBDA*10):.3f} mS")
