import pickle
import textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import WORK as S  # noqa: E402
d = pickle.load(open(f"{S}/containment_si.pkl", "rb"))
etas = d["etas"]
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
GEO = [("v9", "v9 / D35 (HGCAL TDR)", "#e87ba4"), ("v10", "v10 / D41 (L1 TDR)", "#eb6834"),
       ("v11", "v11 / D49 (HLT TDR)", "#b8521f"), ("v17", "v17 / D110 (Spring24)", "#2a78d6"),
       ("v19", "v19 / D128 (current default)", "#6250d6")]
# measured L1 calo-jet matching efficiencies (read off published plots), as (lo, hi, value) bins or points
DATA = {
    "v9": dict(bins=[(2.29, 2.71, 0.99), (2.71, 3.13, 0.99), (3.13, 3.54, 0.994), (3.54, 3.96, 0.996)],
               label="calo jets, p_T > 100 GeV", short="data: calo jets, p_T > 100 GeV"),
    "v11": dict(bins=[(2.5, 2.75, 1.0), (2.75, 3.0, 0.975), (3.0, 3.25, 0.39), (3.25, 3.5, 0.55), (3.5, 3.75, 1.0)],
                label="calo jets (menu V22), p_T > 100 GeV", short="data: V22 calo jets, p_T > 100"),
    "v17": dict(pts=(np.arange(2.625, 4.0, 0.05),
                     [0.979, 0.985, 0.985, 0.979, 0.980, 0.985, 0.970, 0.887, 0.657, 0.592, 0.276, 0.088, 0.134, 0.416,
                      0.637, 0.850, 0.976, 0.994, 1.0, 0.988] + [1.0] * 8),
                label="calo jets, gen 100–300 GeV", short="data: calo jets, 100–300 GeV"),
}
# L1 calorimeter input energy (HF TPs + HGCAL L1 towers, PU-subtracted, dR < 0.4) / gen p_T, gen jets 100-300 GeV,
# Spring24 (v17) ttbar, 60-file subset, 0.1 bins in |eta| (HF L1-jet investigation page)
L1IN = [(2.6, 2.7, 0.77), (2.7, 2.8, 0.78), (2.8, 2.9, 0.73), (2.9, 3.0, 0.58), (3.0, 3.1, 0.27), (3.1, 3.2, 0.14),
        (3.2, 3.3, 0.19), (3.3, 3.4, 0.51), (3.4, 3.5, 0.84), (3.5, 3.6, 1.00)]
PURPLE = "#8a3fbf"
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2})
fig, axs = plt.subplots(3, 2, figsize=(10.5, 10.2), sharex=True, sharey=True, facecolor=SURF,
                        gridspec_kw={"hspace": 0.2, "wspace": 0.06})
axs = axs.ravel()
for ax in axs:
    ax.set_facecolor(SURF); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.axvspan(3.1, 3.4, color="#efeeea", zorder=0)
    ax.axvline(3.0, color="#c3c2b7", lw=0.8, ls="--")
for ax, (key, label, col) in zip(axs, GEO):
    env, si = d[key]
    ax.plot(etas, env, color=col, lw=1.3, ls=(0, (4, 2.5)), alpha=0.9, label="layer envelope (previous model)")
    ax.plot(etas, si, color=col, lw=2.4, label="wafer-level silicon coverage")
    if key in DATA:
        dd = DATA[key]
        if "bins" in dd:
            for k, (lo, hi, f) in enumerate(dd["bins"]):
                ax.plot([lo, hi], [f, f], color=INK, lw=1.3, solid_capstyle="butt", zorder=5)
                ax.plot([(lo + hi) / 2], [f], "o", color=INK, ms=5, mec=SURF, mew=0.8, zorder=6)
        else:
            ax.plot(dd["pts"][0], dd["pts"][1], "o", color=INK, ms=4.2, mec=SURF, mew=0.7, ls="none", zorder=6)
    if key == "v17":
        ax.plot([(lo + hi) / 2 for lo, hi, _ in L1IN], [f for _, _, f in L1IN], "D", ms=5.5, mfc=SURF, mec=PURPLE,
                mew=1.4, ls="none", zorder=7)
    ax.set_title(label, loc="left", color=INK, fontsize=10.5)
    note = DATA[key]["short"] if key in DATA else "no efficiency data"
    ax.text(1.0, 1.012, note, transform=ax.transAxes, color=INK2, fontsize=8, ha="right", va="bottom")
ax = axs[5]
for key, label, col in GEO:
    ax.plot(etas, d[key][1], color=col, lw=2.2 if key != "v11" else 1.8, ls="-" if key != "v19" else (0, (5, 3)), label=key)
ax.set_title("all geometries, silicon coverage", loc="left", color=INK, fontsize=10.5)
leg = ax.legend(loc="lower left", frameon=False, fontsize=8.2, handlelength=1.8, labelspacing=0.3)
for t in leg.get_texts():
    t.set_color(INK)
from matplotlib.lines import Line2D
hs = [Line2D([], [], color=INK2, lw=2.4, label="wafer-level silicon coverage (this update)"),
      Line2D([], [], color=INK2, lw=1.3, ls=(0, (4, 2.5)), label="layer envelope (previous model)"),
      Line2D([], [], color=INK, marker="o", ms=5, lw=1.3, label="measured L1 calo-jet matching efficiency"),
      Line2D([], [], color=PURPLE, marker="D", ms=5, mfc=SURF, mew=1.4, ls="none", label="L1 input energy / gen p_T (v17)")]
fig.subplots_adjust(top=0.865)
fl = fig.legend(handles=hs, loc="upper left", bbox_to_anchor=(0.12, 0.952), ncol=2, frameon=False, fontsize=8.6,
                columnspacing=2.0)
for t in fl.get_texts():
    t.set_color(INK)
for ax in axs[4:]:
    ax.set_xlabel("|η|")
for ax in axs[::2]:
    ax.set_ylabel("visible fraction / efficiency")
axs[0].set_xlim(2.6, 3.6); axs[0].set_ylim(0, 1.08)
fig.suptitle("Energy reaching active material at the HGCAL–HF transition: wafer-level silicon vs layer envelope",
             x=0.125, ha="left", color=INK, fontsize=11.5, y=0.975)
foot = ("Model: straight lines from the origin, shower profiles as before (hadronic 70 %, EM 30 %). Silicon coverage: every wafer "
        "placed as in the DDD algorithms (v17/v19: wafer lists with exact partial-wafer outlines from HGCalWaferMask::waferXY; "
        "v9–v11: full hexagons only, placed when all six corners lie inside the layer's annulus, as in DDHGCalEEAlgo/HEAlgo), "
        "averaged over φ, smoothed radially by the lateral shower size (hadronic 60 mm, EM 25 mm) and normalised to the bulk "
        "coverage so wafer cracks do not count. An absorber block's deposit counts in proportion to that coverage. HF active "
        "for |η| ≥ 2.98 (below that the muon-endcap steel shadows it). Measured points are L1 calo-jet matching efficiencies (any L1 jet within "
        "ΔR, no p_T cut): a jet keeping 30–50 % of its energy is usually still matched, and the 0.4 jet cone averages over "
        "±0.2 in η, so efficiency is not expected to follow the visible fraction one-to-one. Purple diamonds (v17 panel): energy of the "
        "raw L1 calorimeter inputs (HF trigger primitives + HGCAL L1 towers, pileup-subtracted, ΔR < 0.4) over gen p_T, gen jets "
        "100–300 GeV, Spring24 tt̄ (60-file subset), an energy measure directly comparable to the visible fraction.")
fig.canvas.draw()
r = fig.canvas.get_renderer()
x0, x1 = axs[4].get_window_extent(r).x0, axs[5].get_window_extent(r).x1
for w in range(220, 40, -2):
    t = fig.text(x0 / fig.bbox.width, 0.04, "\n".join(textwrap.wrap(foot, w)), color=INK2, fontsize=7.6, va="top", ha="left")
    if t.get_window_extent(r).width <= x1 - x0:
        break
    t.remove()
fig.savefig(f"{S}/hgcal_containment_silicon.png", dpi=200, bbox_inches="tight", facecolor=SURF)
