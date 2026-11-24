"""Single-panel comparison of the total dead material (inside + outside HGCAL) along straight lines from the
origin for v9, v10/v11, v17 and v19. Same material model and z range as plot_material_geos.py."""
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
src = open(os.path.join(HERE, "plot_material_geos.py")).read()
src = src[:src.index("etas = np.arange(")]   # GEOS, budget(), colours
ns = {"__name__": "x", "__file__": os.path.join(HERE, "plot_material_geos.py")}
exec(src, ns)
GEOS, budget, GM = ns["GEOS"], ns["budget"], ns["GM"]
INK, INK2, GRID, SURF = ns["INK"], ns["INK2"], ns["GRID"], ns["SURF"]

etas = np.arange(2.60, 4.001, 0.01)
LAB = {"v9": "v9 / D35 (HGCAL TDR)", "v10": "v10 / v11 (L1 / HLT TDR)", "v17": "v17 / D110 (Spring24)",
       "v19": "v19 / D128 (current default)"}
STY = {"v9": dict(lw=2.0), "v10": dict(lw=2.2), "v17": dict(lw=2.6), "v19": dict(lw=1.8, ls=(0, (5, 3)))}
dead = {}
for key, label, cfi, srcdir, col in GEOS:
    g = GM.Geometry(cfi, srcdir)
    b = np.array([budget(g, e) for e in etas])
    dead[key] = (b[:, 1] + b[:, 2], col)
    i = int(np.argmax(dead[key][0]))
    print(f"{key}: peak {dead[key][0][i]:.2f} lambda at |eta| {etas[i]:.2f}")

plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2})
fig, ax = plt.subplots(figsize=(10.5, 5.2), facecolor=SURF)
ax.set_facecolor(SURF); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.axvspan(3.1, 3.4, color="#efeeea", zorder=0)
ax.axvline(3.0, color="#c3c2b7", lw=0.8, ls="--")
for key in ("v9", "v10", "v17", "v19"):
    y, col = dead[key]
    ax.plot(etas, y, color=col, label=LAB[key], zorder=3, **STY[key])
    i = int(np.argmax(y))
    if y[i] > 0.5:
        ax.plot([etas[i]], [y[i]], "o", color=col, ms=6, mec=SURF, mew=1, zorder=4)
ax.set_xlim(2.6, 4.0); ax.set_ylim(0, 8)
ax.set_xlabel("|η|"); ax.set_ylabel("dead material along the line, λ_I")
ax.set_title("Dead material in front of HF at the HGCAL–HF transition, per geometry", loc="left", color=INK, fontsize=11.5)
ax.text(3.0, 7.55, " HGCAL | HF", color=INK2, fontsize=8.5)
ax.text(3.25, 7.55, "L1 jet hole", color=INK2, ha="center", fontsize=9)
leg = ax.legend(loc="upper right", frameon=False, fontsize=9)
for t in leg.get_texts():
    t.set_color(INK)

foot = ["Total dead material = HGCAL inner supports (Al, steel) + caloBase thermal screen, moderator and services, in interaction "
        "lengths along straight lines from the origin, z = 2.9–5.3 m, from the DDD XML of each scenario. Dots mark each curve's peak. "
        "Thermal screen λ ≈ 45 cm assumed (rough). v9 (D35) has none of this material modelled. v19 (dashed) lies almost on v17."]
fig.canvas.draw()
r = fig.canvas.get_renderer()
abox = ax.get_window_extent(r)
for width in range(200, 40, -2):
    t = fig.text(abox.x0 / fig.bbox.width, -0.01, "\n".join(textwrap.wrap(foot[0], width)), color=INK2, fontsize=7.8,
                 va="top", ha="left")
    if t.get_window_extent(r).width <= abox.width:
        break
    t.remove()
fig.savefig(f"{S}/hgcal_hf_dead_compare.png", dpi=200, bbox_inches="tight", facecolor=SURF)
