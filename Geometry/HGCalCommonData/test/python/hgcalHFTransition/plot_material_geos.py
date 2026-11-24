"""Companion plot to hgcal_hf_containment_geos.png: interaction lengths along straight lines from the origin
for v9, v10/v11, v17 and v19, split into HGCAL active material, dead material inside HGCAL (supports) and dead
material outside HGCAL (caloBase thermal screen, moderator, services). Same material model (geomodel.py) and
same z range as the containment estimate."""
import math
import sys
import textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import os
HERE = os.path.dirname(os.path.abspath(__file__))
CMSSW_SRC = os.environ.get("CMSSW_SRC", os.path.abspath(os.path.join(HERE, *[".."] * 5)))
S = os.path.abspath(os.environ.get("HGCAL_HF_WORKDIR", "hgcal_hf_work"))  # old-geometry XML (fetch_old_geometries.py) and outputs
sys.path.insert(0, HERE)
import geomodel as GM  # noqa: E402

GEOS = [  # key, label, cfi, src, colour
    ("v9", "v9 / D35 (HGCAL TDR)", f"{S}/D35_cfi.py", f"{S}/v9src", "#e87ba4"),
    ("v10", "v10 / v11 (D41 / D49; L1 / HLT TDR)", f"{S}/D41_cfi.py", f"{S}/v10src", "#eb6834"),
    ("v17", "v17 / D110 (Spring24 samples)", f"{CMSSW_SRC}/Geometry/CMSCommonData/python/cmsExtendedGeometryRun4D110XML_cfi.py",
     CMSSW_SRC, "#2a78d6"),
    ("v19", "v19 / D128 (current default)", f"{CMSSW_SRC}/Geometry/CMSCommonData/python/cmsExtendedGeometryRun4D128XML_cfi.py",
     CMSSW_SRC, "#6250d6"),
]
STEP = 2.0
Z0, Z1 = 2900.0, 5300.0
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
DEAD_HG, DEAD_CB = "#7a7974", "#c9c8c1"


def budget(g, eta):
    sec = 1 / math.cos(2 * math.atan(math.exp(-eta)))
    act = dhg = dcb = 0.0
    z = Z0
    while z < Z1:
        zc = z + 0.5 * STEP
        r = zc / math.sinh(eta)
        a, ld, _ = g.material(zc, r)
        if ld:
            l = ld * STEP * sec
            if a:
                act += l
            elif (g.locate(zc, r) or "").startswith("hgcal:"):
                dhg += l
            else:
                dcb += l
        z += STEP
    return act, dhg, dcb


etas = np.arange(2.60, 4.001, 0.01)
res = {}
for key, label, cfi, src, col in GEOS:
    g = GM.Geometry(cfi, src)
    res[key] = np.array([budget(g, e) for e in etas])
    for e in (2.9, 3.0, 3.1, 3.15, 3.2, 3.25, 3.3, 3.4):
        i = int(round((e - 2.60) / 0.01))
        a, h, c = res[key][i]
        print(f"{key} eta {e:.2f}: active {a:.2f}  dead HGCAL {h:.2f}  dead caloBase {c:.2f}")

plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2})
fig, axs = plt.subplots(4, 1, figsize=(10.5, 9.8), sharex=True, facecolor=SURF,
                        gridspec_kw={"hspace": 0.12})
for ax, (key, label, _, _, col) in zip(axs, GEOS):
    a, h, c = res[key].T
    ax.set_facecolor(SURF); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.axvspan(3.1, 3.4, color="#efeeea", zorder=0)
    ax.axvline(3.0, color="#c3c2b7", lw=0.8, ls="--")
    ax.fill_between(etas, 0, a, color=col, lw=0, label="HGCAL active layers crossed")
    ax.fill_between(etas, a, a + h, color=DEAD_HG, lw=0, label="dead, inside HGCAL (supports)")
    ax.fill_between(etas, a + h, a + h + c, color=DEAD_CB, lw=0,
                    label="dead, outside HGCAL (thermal screen, moderator, services)")
    for y in (a, a + h):
        ax.plot(etas, y, color=SURF, lw=0.9)
    ax.plot(etas, h + c, color=INK, lw=1.5, ls=(0, (5, 3)), zorder=5)
    ax.set_ylim(0, 11.5); ax.set_yticks([0, 2, 4, 6, 8, 10])
    ax.text(0.995, 0.93, label, transform=ax.transAxes, ha="right", va="top", color=INK, fontsize=10.5)
    ax.set_ylabel("λ_I along the line")
axs[0].set_title("Material in front of HF at the HGCAL–HF transition: active vs dead, per geometry", loc="left",
                 color=INK, fontsize=11.5)
# one shared legend: geometry colour stands for "active"; dead categories are common
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
LEG = {"v9": "HGCAL active, v9 / D35 (HGCAL TDR)", "v10": "HGCAL active, v10 / v11 (L1 / HLT TDR)",
       "v17": "HGCAL active, v17 / D110 (Spring24)", "v19": "HGCAL active, v19 / D128 (current default)"}
handles = [Patch(color=c, label=LEG[k]) for k, lab, _, _, c in GEOS]
handles += [Patch(color=DEAD_HG, label="dead, inside HGCAL (supports)"),
            Patch(color=DEAD_CB, label="dead, outside HGCAL (thermal screen, moderator, services)"),
            Line2D([], [], color=INK, lw=1.5, ls=(0, (5, 3)), label="total dead material (inside + outside HGCAL)")]
leg = axs[0].legend(handles=handles, loc="upper left", bbox_to_anchor=(0.36, 1.02), ncol=1, frameon=False,
                    fontsize=8.0, labelspacing=0.35)
for t in leg.get_texts():
    t.set_color(INK)
axs[-1].set_xlabel("|η|")
axs[-1].set_xlim(2.6, 4.0)
axs[-1].text(3.0, 10.4, " HGCAL | HF", color=INK2, fontsize=8.5)
axs[-1].text(3.25, 10.4, "L1 jet hole", color=INK2, ha="center", fontsize=9)

foot = [
    "Interaction lengths λ_I summed along straight lines from the origin, z = 2.9–5.3 m, per |η| (0.01 steps), from the DDD XML of "
    "each scenario: polycone volumes of caloBase + hgcal (deepest volume containing the point) and the HGCAL layer blocks of the "
    "geometry algorithms, active where the line is at or above the block's inner radius. CE-E set to 1.4 λ in total, CE-H from its "
    "steel/copper thicknesses; thermal screen λ ≈ 45 cm assumed (rough). v9 (D35) has no supports, thermal screen or moderator "
    "modelled. HF (beyond z ≈ 11 m) not shown.",
]
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
abox = axs[-1].get_window_extent(renderer)
x0 = abox.x0 / fig.bbox.width
for width in range(200, 40, -2):
    txt = "\n".join("\n".join(textwrap.wrap(par, width)) for par in foot)
    t = fig.text(x0, 0.0, txt, color=INK2, fontsize=7.8, va="top", ha="left")
    if t.get_window_extent(renderer).width <= abox.width:
        break
    t.remove()
fig.savefig(f"{S}/hgcal_hf_material_geos.png", dpi=200, bbox_inches="tight", facecolor=SURF)
