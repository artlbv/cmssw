"""Shower-containment estimate at the HGCAL-HF transition for several geometry scenarios.

Material from geomodel.py (caloBase + hgcal volumes, HGCAL layer blocks). Particles follow
straight lines from the origin; after the first interaction (hadrons: lambda; photons: 9/7 X0) the
energy is deposited with a gamma-function longitudinal profile. Energy deposited in crossed HGCAL
active blocks, or leaking into HF beyond |eta| = 3 (assumed fully active, containing), counts as seen;
energy deposited in dead material (supports, thermal screen, moderator, services) is lost.
"""
import math
import sys
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import gamma as G

import os
HERE = os.path.dirname(os.path.abspath(__file__))
CMSSW_SRC = os.environ.get("CMSSW_SRC", os.path.abspath(os.path.join(HERE, *[".."] * 5)))
S = os.path.abspath(os.environ.get("HGCAL_HF_WORKDIR", "hgcal_hf_work"))  # old-geometry XML (fetch_old_geometries.py) and outputs
sys.path.insert(0, HERE)
import geomodel as GM  # noqa: E402

GEOS = [  # key, label, cfi, src
    ("v17", "v17 / D110 (Spring24 samples)", f"{CMSSW_SRC}/Geometry/CMSCommonData/python/cmsExtendedGeometryRun4D110XML_cfi.py", CMSSW_SRC),
    ("v10", "v10 / v11 (L1 / HLT TDR)", f"{S}/D41_cfi.py", f"{S}/v10src"),
    ("v9", "v9 / D35 (HGCAL TDR)", f"{S}/D35_cfi.py", f"{S}/v9src"),
]
F_EM = 0.30
STEP = 4.0
Z0, Z1 = 2900.0, 5300.0
HAD = G(a=2.2, scale=1 / 0.87)   # lambda from first interaction: t_max ~1.4, ~95% within ~6
EM = G(a=3.85, scale=1 / 0.5)    # X0 from conversion: t_max ~5.7


def path(g, eta):
    sec = 1 / math.cos(2 * math.atan(math.exp(-eta)))
    n = int((Z1 - Z0) / STEP)
    dl, dx, act = np.zeros(n), np.zeros(n), np.zeros(n, bool)
    for i in range(n):
        zc = Z0 + (i + 0.5) * STEP
        a, ld, xd = g.material(zc, zc / math.sinh(eta))
        dl[i], dx[i], act[i] = ld * STEP * sec, xd * STEP * sec, a
    return dl, dx, act


def visible(d, act, prof, hf, conv=1.0):
    cum = np.concatenate([[0.0], np.cumsum(d)])
    surv = np.exp(-cum / conv)
    p_int = surv[:-1] - surv[1:]
    vis = 0.0
    for i in np.nonzero(p_int > 1e-7)[0]:
        start = cum[i] + 0.5 * d[i]
        lo = np.clip(cum[i:-1] - start, 0, None)
        hi = np.clip(cum[i + 1:] - start, 0, None)
        dep = prof.cdf(hi) - prof.cdf(lo)
        leak = 1 - prof.cdf(cum[-1] - start)
        vis += p_int[i] * (float(np.sum(dep[act[i:]])) + (leak if hf else 0.0))
    if hf:
        vis += surv[-1]
    return vis


etas = np.arange(2.60, 4.001, 0.01)
curves = {}
for key, label, cfi, src in GEOS:
    t0 = time.time()
    g = GM.Geometry(cfi, src)
    jet, dead = [], []
    for e in etas:
        dl, dx, act = path(g, e)
        hf = e >= 3.0 - 1e-6
        vh = visible(dl, act, HAD, hf)
        ve = visible(dx, act, EM, hf, conv=9 / 7)
        jet.append((1 - F_EM) * vh + F_EM * ve)
        dead.append(float(np.sum(dl[~act])))
    curves[key] = (label, np.array(jet), np.array(dead))
    print(f"{key}: {time.time() - t0:.0f}s, unknown materials {g.unknown}")
    for e in (2.9, 3.0, 3.05, 3.1, 3.15, 3.2, 3.25, 3.3, 3.4, 3.5):
        i = int(round((e - 2.60) / 0.01))
        print(f"   eta {e:.2f}: dead {dead[i]:.2f} lam  visible {jet[i]:.2f}")

l1_300 = [(2.9, 3.0, 0.58), (3.0, 3.1, 0.32), (3.1, 3.2, 0.12), (3.2, 3.3, 0.20), (3.3, 3.4, 0.53),
          (3.4, 3.5, 0.86), (3.5, 3.7, 1.01)]
l1_60 = [(2.6, 2.7, 0.77), (2.7, 2.8, 0.78), (2.8, 2.9, 0.73), (2.9, 3.0, 0.58), (3.0, 3.1, 0.27),
         (3.1, 3.2, 0.14), (3.2, 3.3, 0.19), (3.3, 3.4, 0.51), (3.4, 3.5, 0.84), (3.5, 3.6, 1.00),
         (3.6, 3.7, 0.97), (3.7, 3.8, 1.00), (3.8, 3.9, 1.05), (3.9, 4.0, 1.14)]
for key in curves:
    jet = curves[key][1]
    avg = [(lo, round(float(np.mean(jet[(etas >= lo - 1e-9) & (etas < hi - 1e-9)])), 2)) for lo, hi, _ in l1_60]
    print(key, "bin averages:", avg)

BLUE, ORANGE, AQUA, PURPLE, INK, INK2, GRID, SURF = ("#2a78d6", "#eb6834", "#1baf7a", "#6250d6",
                                                     "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb")
COL = {"v17": BLUE, "v10": ORANGE, "v9": "#e87ba4"}
STY = {"v19": dict(lw=2.4), "v17": dict(lw=2.4), "v10": dict(lw=2.0), "v9": dict(lw=1.8)}
plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2})
fig, ax = plt.subplots(figsize=(10.5, 5.9), facecolor=SURF)
ax.set_facecolor(SURF); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.axvspan(3.1, 3.4, color="#efeeea", zorder=0)
ax.axvline(3.0, color="#c3c2b7", lw=0.8, ls="--")
for key in ("v9", "v10", "v17"):
    label, jet, _ = curves[key]
    ax.plot(etas, jet, color=COL[key], label=f"Visible fraction, {label}", **STY[key])
# L1 jet matching efficiency (dR < 0.35) of gen jets 100-300 GeV vs gen |eta|, read off the HF-page plot
# jet_hf_transition_TT_pt100to300 (0.05 bins, centres 2.625 ... 3.975)
eff_eta = np.arange(2.625, 4.0, 0.05)
eff_sc = [0.976, 0.985, 0.973, 0.963, 0.966, 0.963, 0.938, 0.903, 0.897, 0.787, 0.355, 0.140, 0.142, 0.380,
          0.665, 0.842, 0.973, 0.996] + [1.0] * 10
eff_calo = [0.979, 0.985, 0.985, 0.979, 0.980, 0.985, 0.970, 0.887, 0.657, 0.592, 0.276, 0.088, 0.134, 0.416,
            0.637, 0.850, 0.976, 0.994, 1.0, 0.988] + [1.0] * 8
ax.plot(eff_eta, eff_calo, "D", color=BLUE, ms=5.5, mec=SURF, mew=0.8, ls="none", zorder=7,
        label="v17 L1 calo jet matching eff. (gen 100–300 GeV)")
# v9: CaloJet (green) matching efficiency, p_T > 100 GeV, ~0.42-wide bins, read off the middle panel of the
# red-box slide (both eta sides averaged)
v9_bins = [(2.29, 2.71, 0.99), (2.71, 3.13, 0.99), (3.13, 3.54, 0.994), (3.54, 3.96, 0.996)]
for k, (lo, hi, f) in enumerate(v9_bins):
    ax.plot([lo, hi], [f, f], color=COL["v9"], lw=1.6, solid_capstyle="butt", zorder=6)
    ax.plot([(lo + hi) / 2], [f], "o", ms=6.5, color=COL["v9"], mec=SURF, mew=0.9, zorder=7,
            label="v9 L1 calo jet matching eff. (p_T > 100 GeV)" if k == 0 else None)
# Menu V22 (HLT TDR samples, D49 / HGCAL v11) and V29 (125X, D88 / HGCAL v16) calo jet matching efficiency,
# gen p_T > 100 GeV, 0.25 bins, read off the V29-vs-V22 comparison plot (+-eta averaged, +-0.03)
menu = {"V22": ([(2.5, 2.75, 1.0), (2.75, 3.0, 0.975), (3.0, 3.25, 0.39), (3.25, 3.5, 0.55), (3.5, 3.75, 1.0)],
                ORANGE, "v10 / v11 L1 calo jet matching eff. (p_T > 100 GeV)"),
}
for key, (bins, col, lab) in menu.items():
    for k, (lo, hi, f) in enumerate(bins):
        ax.plot([lo, hi], [f, f], color=col, lw=1.6, solid_capstyle="butt", zorder=6)
        ax.plot([(lo + hi) / 2], [f], "o", ms=6.5, color=col, mec=SURF, mew=0.9, zorder=7,
                label=lab if k == 0 else None)
ax.set_xlim(2.6, 4.0); ax.set_ylim(0, 1.45); ax.set_yticks(np.arange(0, 1.21, 0.2))
ax.set_xlabel("|η|"); ax.set_ylabel("visible energy fraction  /  matching efficiency")
ax.set_title("HGCAL–HF transition: containment (v9, v10/v11, v17) vs L1 jet matching efficiency", loc="left",
             color=INK, fontsize=11.5)
ax.text(3.0, 0.02, " HGCAL | HF", color=INK2, fontsize=8.5)
ax.text(3.25, 0.02, "L1 jet hole", color=INK2, ha="center", fontsize=9)
# legend: left column visible fractions, right column efficiencies, both in geometry order v9, v10/v11, v17
hs, ls_ = ax.get_legend_handles_labels()
geo_rank = lambda l: 0 if "v9" in l else (1 if "v10" in l else 2)
order = sorted(range(len(ls_)), key=lambda i: (0 if ls_[i].startswith("Visible") else 1, geo_rank(ls_[i])))
leg = ax.legend([hs[i] for i in order], [ls_[i] for i in order], loc="upper center", bbox_to_anchor=(0.5, 1.0),
                ncol=2, frameon=False, fontsize=8.4, columnspacing=1.6)
for t in leg.get_texts():
    t.set_color(INK)
import textwrap
foot = [
    "Model: straight lines from the origin through the caloBase + hgcal volumes of each scenario (z 2.9–5.3 m). Hadrons (70%): first "
    "interaction in λ, profile Γ(2.2, 0.87/λ); photons (30%): conversion at 9/7 X0, profile Γ(3.85, 0.5/X0). Energy in crossed HGCAL "
    "active blocks or leaking into HF (|η| > 3, assumed fully active) counts as seen; energy in supports, thermal screen, moderator "
    "and services is lost. Thermal screen λ ≈ 45 cm, X0 ≈ 25 cm assumed; CE-E set to 1.4 λ / 26 X0. No lateral spread, vertex spread, "
    "field or ΔR = 0.4 cone.",
    "Efficiencies: v9 calo jets read off the L1 validation slide; v10/v11 calo jets (D49 samples) read off the menu V22 comparison; "
    "v17 calo jets (Spring24 D110 tt̄, PU 200, ΔR < 0.35) read off the HF-page plot; all vs gen η, both sides averaged.",
    "Not like-for-like: v9 calo jets not firmware-emulated, v10/v11 and v17 emulated; p_T > 100 GeV for v9 and v10/v11, 100–300 GeV for "
    "v17; |η| bins ≈ 0.42 (v9), 0.25 (v10/v11), 0.05 (v17).",
]
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
abox = ax.get_window_extent(renderer)
x0 = abox.x0 / fig.bbox.width
for width in range(200, 40, -2):  # widest wrap whose rendered text fits within the axes width
    txt = "\n".join("\n".join(textwrap.wrap(par, width)) for par in foot)
    t = fig.text(x0, -0.01, txt, color=INK2, fontsize=7.8, va="top", ha="left")
    if t.get_window_extent(renderer).width <= abox.width:
        break
    t.remove()
fig.savefig(f"{S}/hgcal_hf_containment_geos.png", dpi=200, bbox_inches="tight", facecolor=SURF)
