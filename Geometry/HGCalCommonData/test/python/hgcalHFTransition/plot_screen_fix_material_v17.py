"""v17 material budget along straight lines from the origin, stacked by component (as plot_material_split.py), for the
thermal screen as defined in CMSSW (CEThermalScreen: lambda_I = 67 cm, X0 = 9.2 cm) and for the real design
(2 mm aluminium shell + Cryogel Z aerogel, see screen_fix_v17.py). Material budget only: no containment model."""
import math
import os
import sys
import textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import CFI, CMSSW_SRC, WORK  # noqa: E402
import geomodel as GM  # noqa: E402
from screen_fix_v17 import ScreenGeometry  # noqa: E402

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
CATS = [("active", "HGCAL active", "#2a78d6"),
        ("hgcal", "dead, inside HGCAL (supports, back plate)", "#7a7974"),
        ("moderator", "neutron moderator (polyethylene + Al support rings)", "#eda100"),
        ("screen", "thermal screen", "#c9c8c1")]
STEP, Z0, Z1 = 2.0, 2900.0, 5300.0


def budget(sg, eta):
    sec = 1 / math.cos(2 * math.atan(math.exp(-eta)))
    acc = {k: 0.0 for k, _, _ in CATS}
    acc["x0_dead"] = 0.0
    z = Z0
    while z < Z1:
        zc = z + 0.5 * STEP
        r = zc / math.sinh(eta)
        a, ld, xd = sg.material(zc, r)
        if ld:
            if a:
                acc["active"] += ld * STEP * sec
            else:
                vol = sg.locate(zc, r)
                mat = sg.g.lmat[vol][1]
                k = ("hgcal" if vol.startswith("hgcal:") else "screen" if mat == "caloBase:CEThermalScreen"
                     else "moderator" if "Moderator" in vol else None)
                assert k, (vol, mat)
                acc[k] += ld * STEP * sec
                acc["x0_dead"] += xd * STEP * sec
        z += STEP
    return acc


g = GM.Geometry(f"{CFI}/cmsExtendedGeometryRun4D110XML_cfi.py", CMSSW_SRC)
etas = np.arange(2.60, 4.001, 0.01)
res = {}
for case in ("cmssw", "fixed", "fixed10"):
    sg = ScreenGeometry(g, case)
    rows = [budget(sg, e) for e in etas]
    res[case] = {k: np.array([r[k] for r in rows]) for k in rows[0]}
print(" eta   dead lambda: CMSSW -> real (screen CMSSW -> real)      dead X0: CMSSW -> real")
for e in (2.9, 3.0, 3.05, 3.1, 3.15, 3.2, 3.25, 3.3, 3.4, 3.5):
    i = int(round((e - 2.60) / 0.01))
    dc = sum(res["cmssw"][k][i] for k in ("hgcal", "moderator", "screen"))
    df = sum(res["fixed"][k][i] for k in ("hgcal", "moderator", "screen"))
    d10 = sum(res["fixed10"][k][i] for k in ("hgcal", "moderator", "screen"))
    print(f"{e:.2f}   {dc:5.2f} -> {d10:4.2f}-{df:4.2f}   ({res['cmssw']['screen'][i]:4.2f} -> "
          f"{res['fixed10']['screen'][i]:4.2f}-{res['fixed']['screen'][i]:4.2f})      "
          f"{res['cmssw']['x0_dead'][i]:5.1f} -> {res['fixed10']['x0_dead'][i]:4.1f}-{res['fixed']['x0_dead'][i]:4.1f}")

plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2})
fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.8), sharey=True, facecolor=SURF, gridspec_kw={"wspace": 0.05})
dead_c = sum(res["cmssw"][k] for k in ("hgcal", "moderator", "screen"))
for ax, case, title in ((axs[0], "cmssw", "thermal screen as in CMSSW (CEThermalScreen)"),
                        (axs[1], "fixed", "real design (2 mm Al shell + Cryogel Z aerogel)")):
    ax.set_facecolor(SURF); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.axvline(3.0, color="#c3c2b7", lw=0.8, ls="--")
    base = np.zeros_like(etas)
    for k, label, col in CATS:
        ax.fill_between(etas, base, base + res[case][k], color=col, lw=0, label=label)
        base = base + res[case][k]
        ax.plot(etas, base, color=SURF, lw=0.8)
    dead = sum(res[case][k] for k in ("hgcal", "moderator", "screen"))
    ax.plot(etas, dead, color=INK, lw=1.5, ls=(0, (5, 3)), zorder=5, label="total dead material")
    if case == "fixed":
        ax.plot(etas, dead_c, color=INK, lw=1.0, ls=(0, (1, 1.5)), zorder=5, label="total dead material, CMSSW screen")
    ax.set_xlim(2.8, 3.6); ax.set_ylim(0, 11.0)
    ax.set_xlabel("|η|")
    ax.set_title(title, loc="left", color=INK, fontsize=10.5)
axs[0].set_ylabel("λ_I along the line")
axs[0].set_xticks([2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5])
axs[1].set_xticks([2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6])
h, l = axs[1].get_legend_handles_labels()
leg = fig.legend(h, l, loc="upper left", bbox_to_anchor=(0.12, 0.02), ncol=3, frameon=False, fontsize=8.4)
for t in leg.get_texts():
    t.set_color(INK)
fig.suptitle("v17 material in front of HF: effect of the real thermal-screen material", x=0.125, ha="left",
             color=INK, fontsize=11.5, y=1.0)
foot = ("Interaction lengths summed along straight lines from the origin, z = 2.9–5.3 m, D110 geometry; only the thermal-screen "
        "material differs between the panels. CMSSW: CEThermalScreen (1.772 g/cm³, mostly 'Insulation' = 81 % Fe), λ_I = 67 cm, "
        "X0 = 9.2 cm. Real design: per wall a 2 mm aluminium shell and Cryogel Z aerogel (SiO2, 0.16 g/cm³, λ_I = 6.1 m) filling "
        "the rest of the wall (20–119 mm thick in the CMSSW envelopes); a 10 mm blanket with air elsewhere lowers the screen "
        "further by up to half.")
fig.canvas.draw()
rr = fig.canvas.get_renderer()
x0, x1 = axs[0].get_window_extent(rr).x0, axs[1].get_window_extent(rr).x1
ybot = leg.get_window_extent(rr).y0 / fig.bbox.height - 0.02
for w in range(220, 40, -2):
    t = fig.text(x0 / fig.bbox.width, ybot, "\n".join(textwrap.wrap(foot, w)), color=INK2, fontsize=7.8, va="top", ha="left")
    if t.get_window_extent(rr).width <= x1 - x0:
        break
    t.remove()
fig.savefig(os.path.join(WORK, "hgcal_screen_fix_material_v17.png"), dpi=200, bbox_inches="tight", facecolor=SURF)
