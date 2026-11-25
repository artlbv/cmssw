"""Containment estimate with wafer-level silicon coverage, for v9, v10, v11, v17, v19.

Same shower model as plot_containment_geos.py. Two changes:
  * an absorber block counts as active in proportion to the (bulk-normalised) silicon coverage, smoothed with the lateral shower size (hadronic 60 mm, EM 25 mm), of its sensor
    planes at the line's radius, instead of all-or-nothing at the layer envelope r_min;
  * HF counts as active for |eta| >= 2.98: below that, lines reaching the HF front face have crossed the muon-endcap
    steel (HE support tube, yoke nose and disks; the endcap bore is a cone at eta ~ 2.98), so HF sees nothing there.
Writes curves for both the envelope model ('env') and the silicon model ('si').
"""
import math
import pickle
import sys
import numpy as np
from scipy.stats import gamma as G

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import CMSSW_SRC, WORK as S, CFI as P  # noqa: E402
import geomodel as GM  # noqa: E402
import silicon as SI  # noqa: E402

GEOS = [("v9", f"{S}/D35_cfi.py", f"{S}/v9src"), ("v10", f"{S}/D41_cfi.py", f"{S}/v10src"),
        ("v11", f"{S}/D49_cfi.py", f"{S}/v11src"),
        ("v17", f"{P}/cmsExtendedGeometryRun4D110XML_cfi.py", CMSSW_SRC),
        ("v19", f"{P}/cmsExtendedGeometryRun4D128XML_cfi.py", CMSSW_SRC)]
V17FLAG = {"v17": True, "v19": False}   # cassette-era wafer XML WaferMode (v17: 1, v19: 0); others use the old rule
F_EM, STEP, Z0, Z1 = 0.30, 4.0, 2900.0, 5300.0
HAD = G(a=2.2, scale=1 / 0.87)
EM = G(a=3.85, scale=1 / 0.5)
ETA_HF = 2.98                          # muon-endcap bore; HF shadowed by the yoke below
SIG_HAD, SIG_EM = 60.0, 25.0          # lateral shower spread (mm): hadronic ~0.35 lambda in steel, EM ~ Moliere radius


def path(g, eta, wfn_had, wfn_em):
    sec = 1 / math.cos(2 * math.atan(math.exp(-eta)))
    n = int((Z1 - Z0) / STEP)
    dl, dx, w_env, w_h, w_e = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)
    for i in range(n):
        zc = Z0 + (i + 0.5) * STEP
        r = zc / math.sinh(eta)
        a, ld, xd = g.material(zc, r)
        dl[i], dx[i] = ld * STEP * sec, xd * STEP * sec
        if a:
            w_env[i] = 1.0
            w_h[i] = wfn_had(zc, r)
            w_e[i] = wfn_em(zc, r)
    return dl, dx, w_env, w_h, w_e


def visible(d, w, prof, hf, conv=1.0):
    """w: fraction of each step's deposit that is seen (0 dead, 1 fully sampled)."""
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
        vis += p_int[i] * (float(np.sum(dep * w[i:])) + (leak if hf else 0.0))
    if hf:
        vis += surv[-1]
    return vis


if __name__ == "__main__":
    cache = f"{S}/silicon_planes.pkl"
    if os.path.exists(cache):
        planes = pickle.load(open(cache, "rb"))
    else:
        planes = {k: SI.planes(k, cfi, src, V17FLAG.get(k)) for k, cfi, src in GEOS}
        pickle.dump(planes, open(cache, "wb"))
    etas = np.round(np.arange(2.60, 4.001, 0.01), 4)
    out = {"etas": etas}
    for key, cfi, src in GEOS:
        g = GM.Geometry(cfi, src)
        wfn_h = SI.block_weight_fn(g, planes[key], SIG_HAD)
        wfn_e = SI.block_weight_fn(g, planes[key], SIG_EM)
        env, si = [], []
        for e in etas:
            dl, dx, we, wh, wm = path(g, e, wfn_h, wfn_e)
            hf = e >= ETA_HF
            env.append((1 - F_EM) * visible(dl, we, HAD, hf) + F_EM * visible(dx, we, EM, hf, conv=9 / 7))
            si.append((1 - F_EM) * visible(dl, wh, HAD, hf) + F_EM * visible(dx, wm, EM, hf, conv=9 / 7))
        out[key] = (np.array(env), np.array(si))
        row = "  ".join(f"{e:.2f}: {out[key][0][i]:.2f}->{out[key][1][i]:.2f}"
                        for e in (2.8, 2.9, 3.0, 3.05, 3.1, 3.15, 3.2, 3.3) for i in [int(round((e - 2.6) / 0.01))])
        print(key, row)
    pickle.dump(out, open(f"{S}/containment_si.pkl", "wb"))
