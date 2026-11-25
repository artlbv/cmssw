"""Silicon coverage of every HGCAL sensor plane vs radius, for cassette-era (v17, v19) and pre-cassette (v9, v10, v11)
geometries, and a block-activity lookup for the containment model.

Cassette era: wafers from WaferIndex/WaferProperties with exact outlines (coverage.build_layers).
Pre-cassette (CMSSW_11_0_0 / 12_0_0 DDHGCalEEAlgo / DDHGCalHEAlgo): full hexagonal wafers on the grid
x = shift + nc*r, y = shift + nr*0.75*R (r = (waferSize+separation)/2, R = 2r/sqrt3), placed only if all six corners
of the r/R hexagon lie inside [r_in, r_out] (HGCalGeomTools::waferCorner, k_CornerSize = 6). Silicon outline: hexagon
of the wafer size. LayerCenter 1/2 = CornerCenterYp/Ym: grid shifted by +-(waferSize+separation)/sqrt3 in y.

coverage(r): fraction of the ring at radius r (all phi) covered by silicon, smoothed with a Gaussian of SMOOTH mm
(lateral shower spread) and divided by its bulk value (mean over r = 600-750 mm), so that the ~1 mm cracks between
wafers do not count as loss; capped at 1.
"""
import math
import os
import sys
import numpy as np
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import TOOLS  # noqa: E402
sys.path.insert(0, TOOLS)
import hgcalInnerRadiusVsZ as H  # noqa: E402
import coverage as CV  # noqa: E402

SQ3 = math.sqrt(3.0)
R_GRID = np.arange(240.0, 900.0, 2.0)
N_PHI = 240
SMOOTH = 20.0
BULK = (600.0, 750.0)


def old_layers(cfi, src):
    files = H.xml_files_from_cfi(cfi, src)
    C = H.Constants()
    for f in files:
        try:
            C.add_file(f)
        except Exception:
            pass
    wsize = C.value("hgcal:WaferSize")
    separ = C.value("hgcal:SensorSeparation")
    r = 0.5 * (wsize + separ)
    R = 2.0 * r / SQ3
    dy = 0.75 * R
    rs = 0.5 * wsize
    Rs = rs * 2.0 / SQ3
    hexs = np.array([[rs, Rs / 2], [0, Rs], [-rs, Rs / 2], [-rs, -Rs / 2], [0, -Rs], [rs, -Rs / 2]])
    cx = np.array([0, -r, -r, 0, r, r])
    cy = np.array([R, 0.5 * R, -0.5 * R, -R, -0.5 * R, 0.5 * R])
    layers = []
    for f in files:
        base = os.path.basename(f)
        if base not in ("hgcalEE.xml", "hgcalHEsil.xml", "hgcalHEmix.xml"):
            continue
        for a in H.parse_algorithms(f, C):
            centers = [int(x) for x in a["vec"].get("LayerCenter", [])]
            rows = [x for x in H.layers_of(a) if x["zSens"] is not None]
            for k, row in enumerate(rows):
                lc = centers[k] if k < len(centers) else 0
                sx, sy = 0.0, {1: (wsize + separ) / SQ3, 2: -(wsize + separ) / SQ3}.get(lc, 0.0)
                rin, rout = row["rMinBack"], 1.0e9
                N = int(0.5 * 1000.0 / r) + 2
                paths = []
                for u in range(-N, N + 1):
                    for v in range(-N, N + 1):
                        x = sx + (-2 * u + v) * r
                        y = sy + 2 * v * dy
                        rc = np.hypot(x + cx, y + cy)
                        if np.all((rc >= rin) & (rc <= rout)) and math.hypot(x, y) < 1000.0:
                            paths.append(Path(hexs + np.array([x, y])))
                layers.append({"det": "CE-E" if base == "hgcalEE.xml" else "CE-H", "z": row["zSens"],
                               "rmin": rin, "rot": 0.0, "paths": paths})
    return layers


def ring_coverage(layer):
    phis = np.linspace(0, 2 * math.pi, N_PHI, endpoint=False)
    Rg, Pg = np.meshgrid(R_GRID, phis, indexing="ij")
    pts = np.column_stack([(Rg * np.cos(Pg)).ravel(), (Rg * np.sin(Pg)).ravel()])
    inside = np.zeros(len(pts), bool)
    for p in layer["paths"]:
        ext = p.get_extents()
        if ext.x1 < -900 or ext.x0 > 900:
            continue
        inside |= p.contains_points(pts)
    raw = inside.reshape(Rg.shape).mean(axis=1)
    # Gaussian smoothing in r
    dr = R_GRID[1] - R_GRID[0]
    k = np.arange(-int(3 * SMOOTH / dr), int(3 * SMOOTH / dr) + 1) * dr
    w = np.exp(-0.5 * (k / SMOOTH) ** 2)
    w /= w.sum()
    sm = np.convolve(np.pad(raw, len(k) // 2, mode="edge"), w, mode="valid")
    bulk = sm[(R_GRID >= BULK[0]) & (R_GRID <= BULK[1])].mean()
    return raw, np.clip(sm / bulk, 0.0, 1.0)


def planes(key, cfi, src, v17=None):
    layers = CV.build_layers(cfi, v17) if v17 is not None else old_layers(cfi, src)
    out = []
    for L in layers:
        raw, cov = ring_coverage(L)
        out.append({"det": L["det"], "z": L["z"], "rmin": L["rmin"], "raw": raw, "cov": cov})
    return out


def smooth(raw, sigma):
    """Gaussian smoothing of a ring-coverage profile in r, normalised to the bulk value, capped at 1."""
    dr = R_GRID[1] - R_GRID[0]
    k = np.arange(-int(3 * sigma / dr), int(3 * sigma / dr) + 1) * dr
    w = np.exp(-0.5 * (k / sigma) ** 2)
    w /= w.sum()
    sm = np.convolve(np.pad(raw, len(k) // 2, mode="edge"), w, mode="valid")
    bulk = sm[(R_GRID >= BULK[0]) & (R_GRID <= BULK[1])].mean()
    return np.clip(sm / bulk, 0.0, 1.0)


def block_weight_fn(geo, plane_list, sigma=SMOOTH):
    """Returns f(z, r) -> activity weight in [0,1] for a point the geometry model calls active."""
    blocks = sorted((z0, z1) for v in geo.blocks.values() for (z0, z1, *_rest) in v)
    by_block = []
    for z0, z1 in blocks:
        ps = [smooth(p["raw"], sigma) for p in plane_list if z0 <= p["z"] < z1]
        by_block.append((z0, z1, ps))

    def f(z, r):
        for z0, z1, ps in by_block:
            if z0 <= z < z1:
                if not ps:
                    return 1.0
                return float(np.mean([np.interp(r, R_GRID, c) for c in ps]))
        return 1.0
    return f
