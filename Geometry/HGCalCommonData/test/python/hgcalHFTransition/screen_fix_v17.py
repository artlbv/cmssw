"""v17 (D110): effect of the thermal-screen material on the dead material and on the visible fraction.

The CMSSW mixture caloBase:CEThermalScreen (1.772 g/cm3, 85.5 % by weight materials:Insulation, which is 81 % Fe) fills
the screen volumes. The real screen is a thin aluminium shell around a silica-aerogel blanket (Cryogel Z, 0.16 g/cm3,
SiO2). Interaction / radiation lengths from PDG elemental values (g/cm2):

  CEThermalScreen as defined in CMSSW : lambda_I = 67.3 cm, X0 = 9.23 cm
  Cryogel Z                           : lambda_I = 611 cm,  X0 = 169 cm
  aluminium                           : lambda_I = 39.7 cm, X0 = 8.9 cm

Cases for the thermal-screen volumes (everything else unchanged):
  cmssw    : CEThermalScreen as defined in CMSSW
  fixed    : per wall, a 2 mm aluminium shell and aerogel filling the rest of the wall (upper estimate of the real design)
  fixed10  : per wall, a 2 mm aluminium shell and a 10 mm aerogel blanket, air elsewhere (lower estimate)
The wall thickness is the radial gap at that z between the screen volume's inner radius and the inner radius of the
volume it contains (20 mm, 48.6 mm, 118.6 mm along the inner cylinder, 86.6 mm in the rear section).
"""
import math
import os
import pickle
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import CFI, CMSSW_SRC, WORK  # noqa: E402
import geomodel as GM  # noqa: E402
import silicon as SI  # noqa: E402
import containment_si as CS  # noqa: E402

LAM_AL, X0_AL = 107.2 / 2.699 * 10, 24.01 / 2.699 * 10          # mm
LAM_AERO, X0_AERO = 6110.0, 1690.0                                # mm (SiO2 at 0.16 g/cm3)
CASES = {"cmssw": (673.0, 92.3)}       # fixed lambda / X0 in mm (same as geomodel.MAT)


class ScreenGeometry:
    """Wraps a geomodel.Geometry and replaces the thermal-screen material according to `case`."""

    def __init__(self, g, case):
        self.g, self.case = g, case
        self.blocks = g.blocks

    def _inner_radius(self, vol, z):
        secs = self.g.solids.get(self.g.lmat[vol][0], [])
        for (za, ra, _), (zb, rb, _) in zip(secs[:-1], secs[1:]):
            if zb > za and za <= z < zb:
                return ra + (z - za) / (zb - za) * (rb - ra)
        return None

    def wall(self, vol, z):
        own = self._inner_radius(vol, z)
        inner = [self._inner_radius(c, z) for c in self.g.children.get(vol, [])]
        inner = [x for x in inner if x is not None and own is not None and x > own]
        return (min(inner) - own) if inner else 20.0

    def locate(self, z, r):
        return self.g.locate(z, r)

    def material(self, z, r):
        a, ld, xd = self.g.material(z, r)
        if a or not ld:
            return a, ld, xd
        vol = self.g.locate(z, r)
        if self.g.lmat[vol][1] != "caloBase:CEThermalScreen":
            return a, ld, xd
        if self.case in CASES:
            lam, x0 = CASES[self.case]
            return False, 1.0 / lam, 1.0 / x0
        T = self.wall(vol, z)
        blanket = T - 2.0 if self.case == "fixed" else min(10.0, T - 2.0)
        lam_frac = 2.0 / LAM_AL + blanket / LAM_AERO      # per wall, in interaction lengths
        x0_frac = 2.0 / X0_AL + blanket / X0_AERO
        return False, lam_frac / T, x0_frac / T


def dead_screen(sg, eta, step=2.0):
    sec = 1 / math.cos(2 * math.atan(math.exp(-eta)))
    tot = scr = 0.0
    z = 2900.0
    while z < 5300.0:
        zc = z + 0.5 * step
        r = zc / math.sinh(eta)
        a, ld, _ = sg.material(zc, r)
        if ld and not a:
            tot += ld * step * sec
            if sg.g.lmat[sg.g.locate(zc, r)][1] == "caloBase:CEThermalScreen":
                scr += ld * step * sec
        z += step
    return tot, scr


if __name__ == "__main__":
    g = GM.Geometry(f"{CFI}/cmsExtendedGeometryRun4D110XML_cfi.py", CMSSW_SRC)
    planes = pickle.load(open(f"{WORK}/silicon_planes.pkl", "rb"))["v17"]
    wh, we = SI.block_weight_fn(g, planes, CS.SIG_HAD), SI.block_weight_fn(g, planes, CS.SIG_EM)
    etas = np.round(np.arange(2.60, 4.001, 0.01), 4)
    out = {"etas": etas}
    for case in ("cmssw", "fixed", "fixed10"):
        sg = ScreenGeometry(g, case)
        dead, scr, vis = [], [], []
        for e in etas:
            t, s = dead_screen(sg, e)
            dl, dx, _, h, m = CS.path(sg, e, wh, we)
            hf = e >= CS.ETA_HF
            vis.append((1 - CS.F_EM) * CS.visible(dl, h, CS.HAD, hf) + CS.F_EM * CS.visible(dx, m, CS.EM, hf, conv=9 / 7))
            dead.append(t)
            scr.append(s)
        out[case] = (np.array(dead), np.array(scr), np.array(vis))
        print(case, "  ".join(f"{e:.2f}: dead {out[case][0][i]:.2f} (screen {out[case][1][i]:.2f}) vis {out[case][2][i]:.2f}"
                              for e in (3.0, 3.1, 3.2, 3.3, 3.4) for i in [int(round((e - 2.6) / 0.01))]))
    pickle.dump(out, open(f"{WORK}/screen_fix_v17.pkl", "wb"))
