"""Wafer-level silicon coverage at the HGCAL inner edge for cassette-era geometries (v17 D110, v19 D128).

For every sensitive layer: wafer positions from WaferIndex/WaferProperties exactly as the DDD algorithms place them
(DDHGCalSiliconRotatedCassette/Module, DDHGCalMixRotated*), sensitive-silicon outline from CMSSW's own
HGCalWaferMask::waferXY (partials) or the full-hexagon rule of DDHGCalWaferFullRotated, cassette shifts, and the
-30 deg layer rotation for WaferCenterR layers. Lines from the origin at (|eta|, phi) are tested against each layer.
"""
import math
import os
import subprocess
import sys
import numpy as np
from matplotlib.path import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import CMSSW_SRC, WORK, CFI, TOOLS  # noqa: E402
from waferxy_build import ensure_helper  # noqa: E402
sys.path.insert(0, TOOLS)
import hgcalInnerRadiusVsZ as H  # noqa: E402

SQ3 = math.sqrt(3.0)
LAYERTYPE = [0, 1, 2, 3, 4, 5, 6]  # HGCalTypes::layerType: index -> WaferCenter, CenterB, CornerYp, CornerYm, CenterR, CornerXp, CornerXm


def load(cfi, src=CMSSW_SRC):
    files = H.xml_files_from_cfi(cfi, src)
    C = H.Constants()
    for f in files:
        try:
            C.add_file(f)
        except Exception:
            pass
    algos = []
    for f in files:
        if any(f.endswith(x) for x in ("hgcalEE.xml", "hgcalHEsil.xml", "hgcalHEmix.xml")):
            algos += [(f, a) for a in H.parse_algorithms(f, C)]
    sensor_off = C.value("hgcal:SensorSizeOffset")
    wafer_size = C.value("hgcal:WaferSize")
    rot = C.value("hgcal:LayerRotation")
    return algos, sensor_off, wafer_size, rot


def shapes(requests, v17):
    """requests: set of (part, place); returns dict -> polygon (N,2) at the origin."""
    inp = "".join(f"{p} {pl} {SIZE} {OFF} {1 if v17 else 0}\n" for p, pl in sorted(requests))
    out = subprocess.run([ensure_helper()], input=inp, capture_output=True, text=True, check=True).stdout
    res = {}
    for line in out.strip().split("\n"):
        t = line.split()
        p, pl = int(t[0]), int(t[1])
        v = np.array(list(map(float, t[3:]))).reshape(-1, 2)
        res[(p, pl)] = v
    return res


def build_layers(cfi, v17):
    global SIZE, OFF
    algos, OFF, SIZE, rot = load(cfi)
    layers = []
    for f, a in algos:
        v, n = a["vec"], a["num"]
        rows = [r for r in H.layers_of(a) if r["zSens"] is not None]
        first = int(n.get("FirstLayer", n.get("FirstFineLayer", 1)))
        ncas = int(n.get("Cassettes", 1))
        cshift = v.get("CassetteShift", [])
        idx = [int(x) for x in v["WaferIndex"]]
        prop = [int(x) for x in v["WaferProperties"]]
        starts = [int(x) for x in v["WaferLayerStart"]]
        ltypes = [int(x) for x in v.get("LayerTypes", [])]
        wsize = n["waferSize"] + n.get("SensorSeparation", 0.0)
        delx = 0.5 * wsize
        dy = 0.75 * (2.0 * delx / SQ3)
        for k, r in enumerate(rows):
            lay = k  # sensitive-layer index within this algorithm
            lt = LAYERTYPE[ltypes[lay]] if lay < len(ltypes) and 0 <= ltypes[lay] < 7 else 0
            shift = {2: (0, wsize / SQ3), 3: (0, -wsize / SQ3), 5: (wsize / SQ3, 0), 6: (-wsize / SQ3, 0)}.get(lt, (0, 0))
            frontback = 1 if lt == 1 else -1      # WaferCenterB -> front (placement = orient), else orient + 6
            wafers = []
            lo, hi = starts[lay], (starts[lay + 1] if lay + 1 < len(starts) else len(idx))
            for j in range(lo, hi):
                wid = idx[j]
                u = -(wid & 0x1F) if (wid >> 5) & 1 else (wid & 0x1F)
                w = -((wid >> 6) & 0x1F) if (wid >> 11) & 1 else ((wid >> 6) & 0x1F)
                part = (prop[j] // 10) % 100
                orient = (prop[j] // 1000) % 10
                cas = (prop[j] // 10000) % 100
                place = orient if frontback > 0 else orient + 6
                sx = sy = 0.0
                loc = 2 * (ncas * lay + cas - 1)
                if cshift and 0 <= loc + 1 < len(cshift) and cas >= 1:
                    sx, sy = cshift[loc], cshift[loc + 1]
                x = shift[0] - sx + (-2 * u + w) * delx
                y = shift[1] + sy + 2 * w * dy
                if math.hypot(x, y) < 900.0:
                    wafers.append((x, y, part, place))
            layers.append({"det": "CE-E" if f.endswith("hgcalEE.xml") else "CE-H", "z": r["zSens"], "rmin": r["rMinBack"],
                           "rot": rot if lt == 4 else 0.0, "wafers": wafers})
    req = {(p, pl) for L in layers for (_, _, p, pl) in L["wafers"] if p != 0}
    shp = shapes(req, v17)
    r2 = 0.5 * (SIZE - OFF)                       # DDHGCalWaferFullRotated sensitive hexagon
    R2 = r2 / SQ3
    full = np.array([[r2, R2], [0, 2 * R2], [-r2, R2], [-r2, -R2], [0, -2 * R2], [r2, -R2]])
    for L in layers:
        L["paths"] = [Path((full if p == 0 else shp[(p, pl)]) + np.array([x, y])) for x, y, p, pl in L["wafers"]]
    return layers


def hits(layers, etas, phis):
    """-> array [n_eta, n_phi] of active layers crossed, plus envelope count [n_eta]."""
    E, P = np.meshgrid(etas, phis, indexing="ij")
    out = np.zeros(E.shape, int)
    env = np.zeros(len(etas), int)
    for L in layers:
        r = L["z"] / np.sinh(E)
        c, s = math.cos(-L["rot"]), math.sin(-L["rot"])   # global -> local (layer rotated by +rot)
        gx, gy = r * np.cos(P), r * np.sin(P)
        pts = np.column_stack([(c * gx - s * gy).ravel(), (s * gx + c * gy).ravel()])
        inside = np.zeros(len(pts), bool)
        for path in L["paths"]:
            inside |= path.contains_points(pts)
        out += inside.reshape(E.shape)
        env += (L["z"] / np.sinh(etas) >= L["rmin"]).astype(int)
    return out, env


if __name__ == "__main__":
    import pickle
    S = WORK
    etas = np.round(np.arange(2.80, 3.2001, 0.005), 4)
    phis = np.linspace(0, 2 * math.pi, 720, endpoint=False)
    res = {}
    for key, cfi, v17 in (("v17", f"{CFI}/cmsExtendedGeometryRun4D110XML_cfi.py", True),
                          ("v19", f"{CFI}/cmsExtendedGeometryRun4D128XML_cfi.py", False)):
        layers = build_layers(cfi, v17)
        h, env = hits(layers, etas, phis)
        res[key] = (etas, h, env)
        print(key, "layers", len(layers), "wafers near axis", sum(len(L["wafers"]) for L in layers))
        for e in (2.8, 2.9, 2.95, 3.0, 3.05, 3.1, 3.125, 3.15):
            i = int(np.argmin(abs(etas - e)))
            print(f"  eta {e:.3f}: envelope {env[i]:2d}  silicon mean {h[i].mean():5.1f}  min {h[i].min():2d}  max {h[i].max():2d}")
    pickle.dump(res, open(os.path.join(S, "coverage.pkl"), "wb"))
