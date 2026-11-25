import pickle, textwrap, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import WORK as S  # noqa: E402
res = pickle.load(open(f"{S}/coverage.pkl", "rb"))
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
COL = {"v17": "#2a78d6", "v19": "#6250d6"}
LAB = {"v17": "v17 / D110 (Spring24)", "v19": "v19 / D128 (current default)"}
plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.8), sharey=True, facecolor=SURF, gridspec_kw={"wspace": 0.06})
for ax, key in zip(axs, ("v17", "v19")):
    etas, h, env = res[key]
    ax.set_facecolor(SURF); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.axvspan(3.1, 3.4, color="#efeeea", zorder=0); ax.axvline(3.0, color="#c3c2b7", lw=0.8, ls="--")
    p10, p90 = np.percentile(h, 10, axis=1), np.percentile(h, 90, axis=1)
    ax.fill_between(etas, p10, p90, color=COL[key], alpha=0.18, lw=0, label="silicon, 10–90 % range over φ")
    ax.plot(etas, h.mean(axis=1), color=COL[key], lw=2.4, label="silicon layers crossed, mean over φ")
    ax.step(etas, env, where="mid", color=INK, lw=1.3, ls=(0, (5, 3)), label="layer envelope (previous count)")
    ax.set_xlim(2.8, 3.2); ax.set_ylim(0, 52)
    ax.set_xticks([2.8, 2.9, 3.0, 3.1, 3.2] if ax is axs[1] else [2.8, 2.9, 3.0, 3.1])
    ax.text(0.98, 0.97, LAB[key], transform=ax.transAxes, ha="right", va="top", color=INK, fontsize=10.5)
    ax.set_xlabel("|η|")
axs[0].set_ylabel("HGCAL layers crossed")
leg = axs[0].legend(loc="lower left", frameon=False, fontsize=8.6)
for t in leg.get_texts(): t.set_color(INK)
fig.suptitle("Active silicon layers crossed at the HGCAL inner edge: wafer-level count vs layer envelope", x=0.125, ha="left", color=INK, fontsize=11.5, y=0.99)
foot = ("Silicon: every wafer placed as in the DDD algorithms (WaferIndex/WaferProperties, cassette shifts, −30° rotation of "
        "WaferCenterR layers) with its sensitive-silicon outline from CMSSW's HGCalWaferMask::waferXY (partial wafers) or the "
        "full-hexagon rule; lines from the origin at 720 φ values per |η|. Envelope: layer counted when the line is at or "
        "outside the layer's r_min. Shaded: L1 jet hole.")
fig.canvas.draw(); r = fig.canvas.get_renderer()
x0, x1 = axs[0].get_window_extent(r).x0, axs[1].get_window_extent(r).x1
for w in range(200, 40, -2):
    t = fig.text(x0 / fig.bbox.width, -0.03, "\n".join(textwrap.wrap(foot, w)), color=INK2, fontsize=7.8, va="top", ha="left")
    if t.get_window_extent(r).width <= x1 - x0: break
    t.remove()
fig.savefig(f"{S}/hgcal_silicon_coverage.png", dpi=200, bbox_inches="tight", facecolor=SURF)
