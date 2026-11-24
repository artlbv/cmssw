#!/usr/bin/env python3
"""
Standalone (no CMSSW runtime needed) reconstruction of the HGCAL inner radius
vs z from the DDD XML description.

It mimics what the DDD algorithms do:
  * DDHGCalSiliconRotatedCassette / DDHGCalSiliconRotatedModule (CE-E, CE-H silicon)
  * DDHGCalMixRotatedCassette / ...FineCassette / ...Layer (CE-H mixed)
For every layer it steps z from `zMinBlock` by `LayerThick`, places the
sub-volumes by `Thickness`/`LayerType`, and evaluates the inner radius with
HGCalGeomTools::radius(z, ZFrontBottom, RMinFront, SlopeBottom) at the back
face of the layer (exactly as the algorithms do: rinB).
If the algorithm carries a WaferIndex list, it also reports the radius of the
innermost wafer centre and the nearest point of the innermost full hexagon.

Usage
  # a full scenario (reads the XML list of a geometry cfi)
  python3 hgcalInnerRadiusVsZ.py --cfi Geometry/CMSCommonData/python/cmsExtendedGeometryRun4D128XML_cfi.py
  # or an explicit list of XML files (constants files first; later files override)
  python3 hgcalInnerRadiusVsZ.py --xml a.xml b.xml ...
  # extra/override files on top of a cfi (e.g. your own hgcal.xml / hgcalEE.xml)
  python3 hgcalInnerRadiusVsZ.py --cfi ...D128XML_cfi.py --replace hgcal/v19/hgcal.xml=/path/my_hgcal.xml
Options: --csv out.csv   --src <CMSSW src dir>   --plot out.png (needs matplotlib)
All lengths are in mm.
"""
import argparse
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

TOL = 0.0001  # HGCalGeomTools::tol_
TOL1 = 0.01   # DDHGCal*Cassette::tol1_

UNITS = {"mm": 1.0, "cm": 10.0, "m": 1000.0, "um": 1e-3, "micron": 1e-3, "nm": 1e-6,
         "deg": math.pi / 180.0, "rad": 1.0, "mrad": 1e-3, "pi": math.pi,
         "g": 1.0, "mg": 1e-3, "kg": 1e3, "cm3": 1e3, "mole": 1.0, "fermi": 1e-12}


def strip_ns(tag):
    return tag.split("}")[-1]


class Constants:
    def __init__(self):
        self.raw = {}     # "ns:name" -> expression string
        self.cache = {}

    def add_file(self, path):
        ns = os.path.splitext(os.path.basename(path))[0]
        root = ET.parse(path).getroot()
        for sec in root.iter():
            if strip_ns(sec.tag) != "ConstantsSection":
                continue
            for c in sec:
                if strip_ns(c.tag) in ("Constant", "Variable"):
                    self.raw[f"{ns}:{c.get('name')}"] = (c.get("value"), ns)
                    self.cache.pop(f"{ns}:{c.get('name')}", None)
        self.cache.clear()

    def value(self, key, stack=()):
        if key in self.cache:
            return self.cache[key]
        if key not in self.raw:
            raise KeyError(key)
        if key in stack:
            raise RuntimeError("circular constant " + key)
        expr, ns = self.raw[key]
        v = self.eval(expr, ns, stack + (key,))
        self.cache[key] = v
        return v

    def eval(self, expr, ns, stack=()):
        expr = expr.strip()

        def rep(m):
            name = m.group(1)
            full = name if ":" in name else f"{ns}:{name}"
            return repr(self.value(full, stack))

        e = re.sub(r"\[([^\]]+)\]", rep, expr)
        e = e.replace("^", "**")
        env = dict(UNITS)
        env.update({k: getattr(math, k) for k in ("sqrt", "sin", "cos", "tan", "atan", "asin",
                                                   "acos", "exp", "log", "fabs", "pow")})
        env["abs"] = abs
        env["min"] = min
        env["max"] = max
        return float(eval(e, {"__builtins__": {}}, env))


def xml_files_from_cfi(cfi, src):
    txt = open(cfi).read()
    files = re.findall(r"['\"](Geometry/[^'\"]+\.xml)['\"]", txt)
    return [os.path.join(src, f) for f in files]


def radius(z, zFront, rFront, slope):
    """Port of HGCalGeomTools::radius(z, zFront, rFront, slope)."""
    # std::lower_bound: first element >= z
    ik = len(zFront)
    for i, zf in enumerate(zFront):
        if zf >= z:
            ik = i
            break
    if ik != 0:
        ik -= 1
    if ik + 1 < len(zFront) and abs(z - zFront[ik + 1]) < TOL:
        ik += 1
    return rFront[ik] + (z - zFront[ik]) * slope[ik]


def parse_algorithms(path, consts):
    ns = os.path.splitext(os.path.basename(path))[0]
    root = ET.parse(path).getroot()
    algos = []
    for alg in root.iter():
        if strip_ns(alg.tag) != "Algorithm":
            continue
        name = alg.get("name")
        if "HGCal" not in name:
            continue
        a = {"name": name, "file": path, "num": {}, "vec": {}, "str": {}}
        for p in alg:
            t = strip_ns(p.tag)
            pn = p.get("name")
            if t == "Numeric":
                try:
                    a["num"][pn] = consts.eval(p.get("value"), ns)
                except Exception:
                    pass
            elif t == "Vector":
                body = (p.text or "").replace("\n", " ")
                items = [s.strip() for s in body.split(",") if s.strip()]
                if p.get("type") == "string":
                    a["str"][pn] = items
                else:
                    try:
                        a["vec"][pn] = [consts.eval(s, ns) for s in items]
                    except Exception as ex:
                        print(f"WARNING: cannot evaluate vector {pn} in {path}: {ex}", file=sys.stderr)
            elif t == "rParent":
                a["parent"] = p.get("name")
        need = ("Layers", "LayerThick", "ZFrontBottom", "RMinFront", "SlopeBottom")
        if all(k in a["vec"] for k in need) and "zMinBlock" in a["num"]:
            algos.append(a)
    return algos


def wafer_info(a, layer_idx):
    """Innermost wafer centre radius and nearest full-hexagon point for one layer (0-based)."""
    v = a["vec"]
    if "WaferIndex" not in v or "WaferLayerStart" not in v:
        return None
    idx = [int(x) for x in v["WaferIndex"]]
    prop = [int(x) for x in v.get("WaferProperties", [0] * len(idx))]
    starts = [int(x) for x in v["WaferLayerStart"]]
    if layer_idx >= len(starts):
        return None
    first = starts[layer_idx]
    last = starts[layer_idx + 1] if layer_idx + 1 < len(starts) else len(idx)
    wsize = a["num"].get("waferSize", 167.44) + a["num"].get("SensorSeparation", 0.0)
    delx = 0.5 * wsize
    dely = 2.0 * delx / math.sqrt(3.0)
    dy = 0.75 * dely
    ltypes = [int(x) for x in v.get("LayerTypes", [])]
    lt = ltypes[layer_idx] if layer_idx < len(ltypes) else 0
    shift = {2: (0, wsize / math.sqrt(3)), 3: (0, -wsize / math.sqrt(3)),
             5: (wsize / math.sqrt(3), 0), 6: (-wsize / math.sqrt(3), 0)}.get(lt, (0, 0))
    rc_min, redge_min, rc_full = 1e9, 1e9, 1e9
    for k in range(first, last):
        wid = idx[k]
        iu = wid & 0x1F
        u = -iu if (wid >> 5) & 1 else iu
        iv = (wid >> 6) & 0x1F
        w = -iv if (wid >> 11) & 1 else iv
        nr, nc = 2 * w, -2 * u + w
        x = shift[0] + nc * delx
        y = shift[1] + nr * dy
        rc = math.hypot(x, y)
        part = (prop[k] // 10) % 100  # HGCalProperty::waferPartial
        rc_min = min(rc_min, rc)
        if part == 0:  # full wafer: exact nearest point of the hexagon (pointy-top in local frame)
            rc_full = min(rc_full, rc)
            verts = [(x + dely * math.cos(math.radians(90 + 60 * j)),
                      y + dely * math.sin(math.radians(90 + 60 * j))) for j in range(6)]
            redge_min = min(redge_min, seg_dist_min(verts))
    return {"rCentreMin": rc_min, "rCentreFullMin": rc_full, "rEdgeFullMin": redge_min,
            "nWafers": last - first}


def seg_dist_min(verts):
    best = 1e9
    n = len(verts)
    for i in range(n):
        (x1, y1), (x2, y2) = verts[i], verts[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        t = max(0.0, min(1.0, -(x1 * dx + y1 * dy) / (dx * dx + dy * dy)))
        best = min(best, math.hypot(x1 + t * dx, y1 + t * dy))
    return best


def layers_of(a):
    v, n = a["vec"], a["num"]
    mix = "Mix" in a["name"]
    zFB, rMF, sB = v["ZFrontBottom"], v["RMinFront"], v["SlopeBottom"]
    zFT, rMT, sT = v.get("ZFrontTop"), v.get("RMaxFront"), v.get("SlopeTop")
    thick = v.get("Thickness", [])
    ltype = [int(x) for x in v.get("LayerType", [])]
    lsense = [int(x) for x in v.get("LayerSense", [])]
    nlay = [int(x) for x in v["Layers"]]
    first = int(n.get("FirstLayer", 1))
    zi = n["zMinBlock"]
    laymin = 0
    out = []
    for i, (nl, lthick) in enumerate(zip(nlay, v["LayerThick"])):
        zo = zi + lthick
        # Silicon algos evaluate at zo - tol1, Mix algos at zo
        rinB = radius(zo if mix else zo - TOL1, zFB, rMF, sB)
        rinF = radius(zi + TOL1, zFB, rMF, sB)
        routF = radius(zi, zFT, rMT, sT) if zFT else float("nan")
        zz = zi
        zsens = None
        for ly in range(laymin, laymin + nl):
            if ly < len(ltype) and ltype[ly] < len(thick):
                h = thick[ltype[ly]]
                if ly < len(lsense) and lsense[ly] > 0 and zsens is None:
                    zsens = zz + 0.5 * h
                zz += h
        rec = {"det": "CE-E" if "EE" in os.path.basename(a["file"]) else "CE-H",
               "algo": a["name"].split(":")[-1], "layer": first + i, "zFront": zi, "zBack": zo,
               "zSens": zsens, "rMinFront": rinF, "rMinBack": rinB, "rMaxFront": routF,
               "rMinSens": (radius(zsens, zFB, rMF, sB) if zsens is not None else float("nan"))}
        wi = wafer_info(a, i)
        if wi:
            rec.update(wi)
        out.append(rec)
        zi = zo
        laymin += nl
    return out


def polycones(path, consts):
    ns = os.path.splitext(os.path.basename(path))[0]
    root = ET.parse(path).getroot()
    res = {}
    for pc in root.iter():
        if strip_ns(pc.tag) != "Polycone":
            continue
        secs = []
        for zs in pc:
            if strip_ns(zs.tag) == "ZSection":
                try:
                    secs.append(tuple(consts.eval(zs.get(k), ns) for k in ("z", "rMin", "rMax")))
                except Exception:
                    secs.append(None)
        res[pc.get("name")] = secs
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cfi", help="geometry XML cfi (list of XML files)")
    ap.add_argument("--xml", nargs="*", default=[], help="explicit XML files (appended after cfi files)")
    ap.add_argument("--replace", nargs="*", default=[],
                    help="substring=path : replace a cfi file whose path contains substring by path")
    ap.add_argument("--src", default=None, help="CMSSW src dir (default: guessed from this script)")
    ap.add_argument("--csv", help="write per-layer table to this CSV file")
    ap.add_argument("--plot", help="write r_min(z) plot (needs matplotlib)")
    args = ap.parse_args()

    src = args.src or os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 4))
    files = xml_files_from_cfi(args.cfi, src) if args.cfi else []
    for r in args.replace:
        key, new = r.split("=", 1)
        files = [new if key in f else f for f in files]
    files += args.xml
    files = [f for f in files if os.path.exists(f) or print(f"WARNING: missing {f}", file=sys.stderr)]

    consts = Constants()
    for f in files:
        try:
            consts.add_file(f)
        except ET.ParseError as ex:
            print(f"WARNING: cannot parse {f}: {ex}", file=sys.stderr)

    hg = [f for f in files if re.search(r"/hgcal(EE|HEsil|HEmix)?\.xml$", f)]
    print("# Files used for HGCAL:")
    for f in hg:
        print("#   " + os.path.relpath(f, src) if f.startswith(src) else "#   " + f)

    # ---- envelopes
    for f in hg:
        if os.path.basename(f) != "hgcal.xml":
            continue
        print("\n# Envelope polycones in", os.path.basename(f), "(z, rMin, rMax) [mm]")
        for name, secs in polycones(f, consts).items():
            print(f"  {name}:")
            for s in secs:
                print("     " + ("  (unresolved)" if s is None else f"z={s[0]:9.2f}  rMin={s[1]:8.2f}  rMax={s[2]:8.2f}"))

    # ---- per-layer
    rows = []
    for f in hg:
        for a in parse_algorithms(f, consts):
            if "ZFrontBottom" in a["vec"]:
                print(f"\n# {os.path.basename(f)} {a['name']}: ZFrontBottom={['%.2f' % x for x in a['vec']['ZFrontBottom']]}"
                      f" RMinFront={['%.2f' % x for x in a['vec']['RMinFront']]} SlopeBottom={a['vec']['SlopeBottom']}")
            rows += layers_of(a)
    order = {"CE-E": 0, "CE-H": 1}
    rows.sort(key=lambda r: (order[r["det"]], r["zFront"]))
    for i, r in enumerate(rows):
        r["globalLayer"] = i + 1

    hdr = ["globalLayer", "det", "layer", "zFront", "zSens", "zBack", "rMinFront", "rMinSens", "rMinBack",
           "rMaxFront", "nWafers", "rCentreMin", "rCentreFullMin", "rEdgeFullMin"]
    print("\n# Per-layer inner radius [mm]; rMin* = envelope (HGCalGeomTools::radius with ZFrontBottom/RMinFront);")
    print("# rCentreMin = innermost wafer centre (any type), rEdgeFullMin = nearest point of an innermost FULL hexagon")
    print("# eta at rMinSens: eta = asinh(z/r)")
    print(" gL det  lay   zFront    zSens    zBack  rMinF  rMinS  rMinB  eta(rMinS)  nWaf  rCtrMin rEdgeFull")
    for r in rows:
        zs = r["zSens"] if r["zSens"] is not None else r["zFront"]
        eta = math.asinh(zs / r["rMinSens"]) if r["rMinSens"] == r["rMinSens"] else float("nan")
        print(f"{r['globalLayer']:3d} {r['det']} {r['layer']:3d} {r['zFront']:8.2f} {zs:8.2f} {r['zBack']:8.2f} "
              f"{r['rMinFront']:6.1f} {r['rMinSens']:6.1f} {r['rMinBack']:6.1f}  {eta:8.3f}   "
              f"{r.get('nWafers', 0):4d}  {r.get('rCentreMin', float('nan')):7.1f}  {r.get('rEdgeFullMin', float('nan')):7.1f}")

    if args.csv:
        with open(args.csv, "w") as fo:
            fo.write(",".join(hdr) + "\n")
            for r in rows:
                fo.write(",".join("" if r.get(k) is None else str(r.get(k, "")) for k in hdr) + "\n")
        print("# wrote", args.csv)
    if args.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.step([r["zFront"] for r in rows] + [rows[-1]["zBack"]],
                [r["rMinFront"] for r in rows] + [rows[-1]["rMinBack"]], where="post", label="r_min envelope")
        ax.plot([r["zSens"] for r in rows if r["zSens"]], [r["rMinSens"] for r in rows if r["zSens"]], "o",
                label="r_min at sensor plane")
        if any("rEdgeFullMin" in r for r in rows):
            ax.plot([r["zSens"] for r in rows if "rEdgeFullMin" in r and r["zSens"]],
                    [r["rEdgeFullMin"] for r in rows if "rEdgeFullMin" in r and r["zSens"]], "x",
                    label="innermost full-wafer edge")
        ax.set_xlabel("z [mm]")
        ax.set_ylabel("r [mm]")
        ax.legend()
        ax.grid(alpha=0.3)
        fig.savefig(args.plot, dpi=150, bbox_inches="tight")
        print("# wrote", args.plot)


if __name__ == "__main__":
    main()
