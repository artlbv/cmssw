"""Plot of screen_fix_v17.py: v17 dead material and visible fraction with the thermal screen as defined in CMSSW and
with the corrected (aluminium shell + aerogel) screen."""
import os
import pickle
import sys
import textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import WORK  # noqa: E402

d = pickle.load(open(f"{WORK}/screen_fix_v17.pkl", "rb"))
etas = d["etas"]
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
BLUE, AQUA, GREY, PURPLE = "#2a78d6", "#1baf7a", "#a3a29c", "#8a3fbf"
EFF = (np.arange(2.625, 4.0, 0.05), [0.979, 0.985, 0.985, 0.979, 0.980, 0.985, 0.970, 0.887, 0.657, 0.592, 0.276, 0.088,
                                      0.134, 0.416, 0.637, 0.850, 0.976, 0.994, 1.0, 0.988] + [1.0] * 8)
L1IN = [(2.6, 2.7, 0.77), (2.7, 2.8, 0.78), (2.8, 2.9, 0.73), (2.9, 3.0, 0.58), (3.0, 3.1, 0.27), (3.1, 3.2, 0.14),
        (3.2, 3.3, 0.19), (3.3, 3.4, 0.51), (3.4, 3.5, 0.84), (3.5, 3.6, 1.00)]
# Full-simulation rerun with modified thermal-screen material (colleague's study, D126 = HGCAL v19): L1puppiJetSC4 with
# assigned p_T >= 20 GeV, GenJet p_T > 50 GeV, one-to-one dR < 0.3; 0.1-wide |eta| bins; values read off the plot (+-0.01).
SC4_ETA = np.arange(2.65, 3.6, 0.1)
SC4_NOM = [0.615, 0.645, 0.58, 0.40, 0.31, 0.065, 0.34, 0.71, 0.92, 1.00]
SC4_CRYO = [0.70, 0.68, 0.515, 0.40, 0.27, 0.165, 0.765, 1.00, 1.00, 0.99]
# statistical error bars read off the same plot (symmetric; clipped at efficiency 1)
SC4_NOM_ERR = [0.05, 0.045, 0.05, 0.05, 0.045, 0.03, 0.065, 0.08, 0.04, 0.01]
SC4_CRYO_ERR = [0.06, 0.04, 0.05, 0.065, 0.05, 0.06, 0.055, 0.03, 0.02, 0.02]


def _yerr(vals, errs):
    return [errs, [min(e, 1.0 - v) for v, e in zip(vals, errs)]]

plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 5.6), facecolor=SURF, gridspec_kw={"wspace": 0.18})
for ax in (a1, a2):
    ax.set_facecolor(SURF); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.axvspan(3.1, 3.4, color="#efeeea", zorder=0)
    ax.axvline(3.0, color="#c3c2b7", lw=0.8, ls="--")
    ax.set_xlim(2.8, 3.6)
    ax.set_xlabel("|η|")

# left: dead material
a1.plot(etas, d["cmssw"][0], color=BLUE, lw=2.4, label="total dead, thermal screen as in CMSSW")
a1.fill_between(etas, d["fixed10"][0], d["fixed"][0], color=AQUA, alpha=0.35, lw=0)
a1.plot(etas, d["fixed"][0], color=AQUA, lw=2.2, label="total dead, corrected screen (Al shell + aerogel)")
a1.plot(etas, d["cmssw"][1], color=BLUE, lw=1.3, ls=(0, (4, 2.5)), label="thermal screen only, CMSSW")
a1.plot(etas, d["fixed"][1], color=AQUA, lw=1.3, ls=(0, (4, 2.5)), label="thermal screen only, corrected")
a1.set_ylim(0, 7.6)
a1.set_ylabel("dead material along the line, λ_I")
a1.set_title("Dead material, v17", loc="left", color=INK, fontsize=11)
l1 = a1.legend(loc="upper left", bbox_to_anchor=(-0.02, -0.13), frameon=False, fontsize=8.2)
for t in l1.get_texts():
    t.set_color(INK)

# right: visible fraction
a2.plot(etas, d["cmssw"][2], color=BLUE, lw=2.4, label="screen as in CMSSW (what the samples simulate)")
a2.fill_between(etas, d["fixed"][2], d["fixed10"][2], color=AQUA, alpha=0.35, lw=0)
a2.plot(etas, d["fixed"][2], color=AQUA, lw=2.2, label="corrected screen (real detector)")
a2.plot(EFF[0], EFF[1], "o", color=INK, ms=4.2, mec=SURF, mew=0.7, ls="none", zorder=6,
        label="L1 calo-jet matching eff. (Spring24)")
a2.plot([(lo + hi) / 2 for lo, hi, _ in L1IN], [f for _, _, f in L1IN], "D", ms=5.5, mfc=SURF, mec=PURPLE, mew=1.4,
        ls="none", zorder=7, label="L1 input energy / gen p_T (Spring24)")
a2.errorbar(SC4_ETA - 0.008, SC4_NOM, yerr=_yerr(SC4_NOM, SC4_NOM_ERR), fmt="s", ms=5.0, mfc=SURF, mec=INK2, mew=1.2,
             ecolor=INK2, elinewidth=1.0, capsize=0, zorder=7, label="L1 PUPPI SC4 jet eff., full sim. D126, CMSSW screen")
a2.errorbar(SC4_ETA + 0.008, SC4_CRYO, yerr=_yerr(SC4_CRYO, SC4_CRYO_ERR), fmt="s", ms=5.0, color=AQUA, mec=INK,
             mew=0.6, ecolor="#12805a", elinewidth=1.0, capsize=0, zorder=8,
             label="L1 PUPPI SC4 jet eff., full sim. D126, Cryogel screen")
a2.set_ylim(0, 1.08)
a2.set_ylabel("visible fraction / efficiency")
a2.set_title("Visible fraction (wafer-level silicon), v17", loc="left", color=INK, fontsize=11)
l2 = a2.legend(loc="upper left", bbox_to_anchor=(-0.02, -0.13), frameon=False, fontsize=8.2)
for t in l2.get_texts():
    t.set_color(INK)
fig.suptitle("v17: effect of correcting the thermal-screen material (CEThermalScreen → Al shell + Cryogel Z aerogel)",
             x=0.125, ha="left", color=INK, fontsize=11.5, y=1.0)
foot = ("Thermal screen: CMSSW mixture CEThermalScreen (1.772 g/cm³, mostly 'Insulation' = 81 % Fe): λ_I = 67 cm, X0 = 9.2 cm. "
        "Corrected: per wall a 2 mm aluminium shell and Cryogel Z aerogel (SiO2, 0.16 g/cm³, λ_I = 6.1 m, X0 = 1.7 m) filling "
        "the rest of the wall (line) or only a 10 mm blanket with air elsewhere (band edge); wall thickness taken from the "
        "CMSSW envelopes (20–119 mm). All other materials unchanged. Visible fraction: wafer-level silicon model, HF from |η| = "
        "2.98. Spring24 points (circles, diamonds): samples with the CMSSW screen. Squares: full-simulation rerun (D126 = v19) "
        "with the nominal and with a Cryogel-proxy screen, L1 PUPPI SC4 jets with p_T ≥ 20 GeV matched to GenJets with p_T > 50 "
        "GeV; their plateau below |η| = 3 is ≈ 0.65, so compare the two square series with each other. Square error bars: statistical, "
        "read off the source plot; points offset by ±0.008 in |η| for visibility (bins are 0.1 wide).")
fig.canvas.draw()
rr = fig.canvas.get_renderer()
ybot = min(l1.get_window_extent(rr).y0, l2.get_window_extent(rr).y0) / fig.bbox.height - 0.02
x0, x1 = a1.get_window_extent(rr).x0, a2.get_window_extent(rr).x1
for w in range(220, 40, -2):
    t = fig.text(x0 / fig.bbox.width, ybot, "\n".join(textwrap.wrap(foot, w)), color=INK2, fontsize=7.8, va="top", ha="left")
    if t.get_window_extent(rr).width <= x1 - x0:
        break
    t.remove()
fig.savefig(os.path.join(WORK, "hgcal_screen_fix_v17.png"), dpi=200, bbox_inches="tight", facecolor=SURF)
