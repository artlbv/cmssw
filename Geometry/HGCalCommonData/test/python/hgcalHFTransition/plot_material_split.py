"""Like plot_material_geos.py for one geometry, with the dead material outside HGCAL split into its components:
thermal screen (caloBase CALOECTS*), neutron moderator (CALOECModerator, polyethylene; in caloBase 2030/v7+ also its
aluminium support rings CALOECSup1/2Moderator) and services (CEService). Dead material inside HGCAL as before.

Usage: plot_material_split.py [v17|v10|v9]   (default v17; v10 needs fetch_old_geometries.py, and stands for v10/v11,
which share the same caloBase and inner geometry)"""
import math
import os
import sys
import textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import CMSSW_SRC, CFI, WORK  # noqa: E402
import geomodel as GM  # noqa: E402

GEOS = {
    "v17": dict(cfi=f"{CFI}/cmsExtendedGeometryRun4D110XML_cfi.py", src=CMSSW_SRC, colour="#2a78d6",
                label="v17 / D110 (Spring24)", calo="caloBase 2030/v7 + hgcal v17",
                moderator="neutron moderator (polyethylene + Al support rings)"),
    "v9": dict(cfi=f"{WORK}/D35_cfi.py", src=f"{WORK}/v9src", colour="#e87ba4",
               label="v9 / D35 (HGCAL TDR)", calo="caloBase 2026/v1 + hgcal v9, scenario D35",
               moderator="neutron moderator"),
    "v10": dict(cfi=f"{WORK}/D41_cfi.py", src=f"{WORK}/v10src", colour="#eb6834",
                label="v10 / v11 (L1 / HLT TDR)", calo="caloBase 2026/v2 + hgcal v10, scenario D41; v11/D49 is identical here",
                moderator="neutron moderator (polyethylene)"),
}
KEY = sys.argv[1] if len(sys.argv) > 1 else "v17"
GEO = GEOS[KEY]
STEP = 2.0
Z0, Z1 = 2900.0, 5300.0
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
CATS = [  # key, label, colour
    ("active", f"HGCAL active, {GEO['label']}", GEO["colour"]),
    ("hgcal", "dead, inside HGCAL (supports, back plate)", "#7a7974"),
    ("services", "services (CEService)", "#1baf7a"),
    ("moderator", GEO["moderator"], "#eda100"),
    ("screen", "thermal screen", "#c9c8c1"),
]


def category(g, vol, mat):
    if vol is None:
        return None
    if mat == "caloBase:CEService":
        return "services"
    if vol.startswith("hgcal:"):
        return "hgcal"
    if "Moderator" in vol and not vol.startswith("caloBase:CALOECTS"):
        return "moderator"
    if mat == "caloBase:CEThermalScreen":
        return "screen"
    return "other"


def budget(g, eta):
    sec = 1 / math.cos(2 * math.atan(math.exp(-eta)))
    acc = {k: 0.0 for k, _, _ in CATS}
    acc["other"] = 0.0
    z = Z0
    while z < Z1:
        zc = z + 0.5 * STEP
        r = zc / math.sinh(eta)
        a, ld, _ = g.material(zc, r)
        if ld:
            if a:
                acc["active"] += ld * STEP * sec
            else:
                vol = g.locate(zc, r)
                acc[category(g, vol, g.lmat[vol][1])] += ld * STEP * sec
        z += STEP
    return acc


g = GM.Geometry(GEO["cfi"], GEO["src"])
etas = np.arange(2.60, 4.001, 0.01)
res = [budget(g, e) for e in etas]
cols = {k: np.array([r[k] for r in res]) for k in list(res[0])}
assert cols["other"].max() < 1e-9, "unclassified dead material"
if cols["services"].max() < 0.005:
    CATS = [(k, lab + ": not crossed" if k == "services" else lab, c) for k, lab, c in CATS]
for e in (2.9, 2.95, 3.0, 3.05, 3.1, 3.15, 3.2, 3.25, 3.3, 3.4, 3.5):
    i = int(round((e - 2.60) / 0.01))
    print(f"eta {e:.2f}: " + "  ".join(f"{k} {cols[k][i]:.2f}" for k, _, _ in CATS))

plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2})
fig, ax = plt.subplots(figsize=(10.5, 4.6), facecolor=SURF)
ax.set_facecolor(SURF); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.axvspan(3.1, 3.4, color="#efeeea", zorder=0)
ax.axvline(3.0, color="#c3c2b7", lw=0.8, ls="--")
base = np.zeros_like(etas)
for k, label, col in CATS:
    ax.fill_between(etas, base, base + cols[k], color=col, lw=0, label=label)
    base = base + cols[k]
    ax.plot(etas, base, color=SURF, lw=0.8)
dead = sum(cols[k] for k, _, _ in CATS if k != "active")
ax.plot(etas, dead, color=INK, lw=1.5, ls=(0, (5, 3)), zorder=5, label="total dead material")
ax.set_xlim(2.6, 4.0); ax.set_ylim(0, 11.5); ax.set_yticks([0, 2, 4, 6, 8, 10])
ax.set_xlabel("|η|"); ax.set_ylabel("λ_I along the line")
ax.set_title(f"Material in front of HF, {GEO['label']}: dead material outside HGCAL by component", loc="left",
             color=INK, fontsize=11.5)
ax.text(3.0, 10.4, " HGCAL | HF", color=INK2, fontsize=8.5)
ax.text(3.25, 10.4, "L1 jet hole", color=INK2, ha="center", fontsize=9)
leg = ax.legend(loc="center right", frameon=False, fontsize=8.6)
for t in leg.get_texts():
    t.set_color(INK)
foot = (f"Interaction lengths summed along straight lines from the origin, z = 2.9–5.3 m, from the DDD XML ({GEO['calo']}). "
        + ("Moderator: CALOECModerator (polyethylene) and its aluminium support rings CALOECSup1/2Moderator, whose notches at "
           "r ≥ 1 m are ignored. " if KEY == "v17" else "Moderator: CALOECModerator (polyethylene). ")
        + ("Services (HGCalService, CEService) are not crossed by these lines. " if cols["services"].max() < 0.005 else
           f"Services (HGCalService, CEService): at most {cols['services'].max():.2f} λ. ")
        + "Thermal screen as defined in CMSSW (CEThermalScreen, λ_I = 67 cm).")
fig.canvas.draw()
rr = fig.canvas.get_renderer()
box = ax.get_window_extent(rr)
for w in range(200, 40, -2):
    t = fig.text(box.x0 / fig.bbox.width, -0.04, "\n".join(textwrap.wrap(foot, w)), color=INK2, fontsize=7.8,
                 va="top", ha="left")
    if t.get_window_extent(rr).width <= box.width:
        break
    t.remove()
os.makedirs(WORK, exist_ok=True)
fig.savefig(os.path.join(WORK, f"hgcal_hf_material_{KEY}_split.png"), dpi=200, bbox_inches="tight", facecolor=SURF)
