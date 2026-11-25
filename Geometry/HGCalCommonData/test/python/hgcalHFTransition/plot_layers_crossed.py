"""Number of HGCAL sensor layers crossed by a straight line from the origin vs |eta|, for v9, v10/v11, v17 and v19.

A layer counts as crossed when the line passes its sensor plane between the layer's inner radius (the r_min the
simulation uses for that layer block) and its outer radius. Per-layer tables come from ../hgcalInnerRadiusVsZ.py.
Two panels: the outer edge (small |eta|, lines leaving through the outer radius) and the inner edge (HGCAL-HF
transition). Between them every layer is crossed.
"""
import csv
import math
import os
import subprocess
import sys
import textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
CMSSW_SRC = os.environ.get("CMSSW_SRC", os.path.abspath(os.path.join(HERE, *[".."] * 5)))
S = os.path.abspath(os.environ.get("HGCAL_HF_WORKDIR", "hgcal_hf_work"))
TOOL = os.path.join(HERE, "..", "hgcalInnerRadiusVsZ.py")
PY = f"{CMSSW_SRC}/Geometry/CMSCommonData/python"

GEOS = [  # key, label, cfi, src, colour, style
    ("v9", "v9 / D35 (HGCAL TDR)", f"{S}/D35_cfi.py", f"{S}/v9src", "#e87ba4", dict(lw=2.0)),
    ("v10", "v10 / v11 (L1 / HLT TDR)", f"{S}/D41_cfi.py", f"{S}/v10src", "#eb6834", dict(lw=2.2)),
    ("v17", "v17 / D110 (Spring24)", f"{PY}/cmsExtendedGeometryRun4D110XML_cfi.py", CMSSW_SRC, "#2a78d6", dict(lw=2.6)),
    ("v19", "v19 / D128 (current default)", f"{PY}/cmsExtendedGeometryRun4D128XML_cfi.py", CMSSW_SRC, "#6250d6",
     dict(lw=1.8, ls=(0, (5, 3)))),
]
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"


def layer_table(key, cfi, src):
    out = os.path.join(S, f"layers_{key}.csv")
    subprocess.run([sys.executable, "-I", TOOL, "--cfi", cfi, "--src", src, "--csv", out], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return [(float(r["zSens"]), float(r["rMinBack"]), float(r["rMaxFront"]), r["det"]) for r in csv.DictReader(open(out))]


def crossed(rows, eta, det=None):
    sh = math.sinh(eta)
    return sum(1 for z, rmin, rmax, d in rows if (det is None or d == det) and rmin <= z / sh <= rmax)


os.makedirs(S, exist_ok=True)
tables = {k: layer_table(k, cfi, src) for k, _, cfi, src, _, _ in GEOS}
lo = np.arange(1.35, 1.6501, 0.0025)
hi = np.arange(2.75, 3.3001, 0.0025)
for k, rows in tables.items():
    print(k, "total", len(rows), "| eta 3.00:", crossed(rows, 3.0), "3.10:", crossed(rows, 3.1), "3.15:", crossed(rows, 3.15))

plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 5.0), sharey=True, facecolor=SURF,
                             gridspec_kw={"width_ratios": [0.3, 0.55], "wspace": 0.06})
for ax in (a1, a2):
    ax.set_facecolor(SURF); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
a2.spines["left"].set_visible(False)
a2.tick_params(axis="y", length=0)
a2.axvspan(3.1, 3.4, color="#efeeea", zorder=0)
a2.axvline(3.0, color="#c3c2b7", lw=0.8, ls="--")
for key, label, _, _, col, sty in GEOS:
    rows = tables[key]
    for ax, et in ((a1, lo), (a2, hi)):
        ax.step(et, [crossed(rows, e) for e in et], where="mid", color=col, label=label if ax is a2 else None,
                zorder=3, **sty)
a1.set_xlim(1.35, 1.65); a2.set_xlim(2.75, 3.3)
a1.set_ylim(0, 58); a1.set_yticks(range(0, 56, 10))
a1.set_ylabel("HGCAL layers crossed")
a1.set_title("outer edge", color=INK2, fontsize=9.5, loc="left")
a2.set_title("inner edge (HGCAL–HF transition)", color=INK2, fontsize=9.5, loc="left")
fig.supxlabel("|η|", color=INK2, fontsize=10, y=0.0)
fig.suptitle("HGCAL sensor layers crossed by a straight line from the interaction point", x=0.125, ha="left",
             color=INK, fontsize=11.5, y=0.99)
a2.text(3.0, 2.0, " HGCAL | HF", color=INK2, fontsize=8.5)
a2.text(3.29, 2.0, "L1 jet hole", color=INK2, ha="right", fontsize=9)
leg = a2.legend(loc="upper right", frameon=False, fontsize=9)
for t in leg.get_texts():
    t.set_color(INK)

foot = ("A layer counts as crossed when the line passes its sensor plane between the layer's inner radius (the r_min "
        "the simulation uses for that layer block) and its outer radius. Partial wafers at the edges count as active; "
        "CE-H outer layers include the scintillator section. Between |η| ≈ 1.55 and 2.85 every layer is crossed "
        "(v9: 52, v10/v11: 50, v17/v19: 47). v19 (dashed) lies on v17 at the inner edge.")
fig.canvas.draw()
r = fig.canvas.get_renderer()
x0 = a1.get_window_extent(r).x0
x1 = a2.get_window_extent(r).x1
for width in range(200, 40, -2):
    t = fig.text(x0 / fig.bbox.width, -0.03, "\n".join(textwrap.wrap(foot, width)), color=INK2, fontsize=7.8,
                 va="top", ha="left")
    if t.get_window_extent(r).width <= (x1 - x0):
        break
    t.remove()
fig.savefig(os.path.join(S, "hgcal_layers_crossed.png"), dpi=200, bbox_inches="tight", facecolor=SURF)
