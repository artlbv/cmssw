"""Generic r-z material model of the CMS endcap calorimeter region from the DDD XML of a scenario.

* Dead material: every Polycone placed under caloBase:CALOEC (caloBase.xml + hgcal.xml), resolved by
  descending the placement tree (all placements are at the origin); the deepest volume containing a
  point gives its material.
* Inside HGCalEE / HGCalHEsil / HGCalHEmix the layer blocks of the DDD algorithms are used: a point is
  'active' if the line is at or above the block's r_min (rinB), otherwise it is in air.
  Per-block interaction / radiation lengths: CE-E fixed to 1.4 lambda / 26 X0 in total (spread evenly
  over its blocks, since v19 keeps the CE-E absorbers in per-cassette volumes); CE-H from the steel /
  copper thicknesses of the layer stack.
"""
import math
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
import hgcalInnerRadiusVsZ as H  # noqa: E402

# (lambda_I, X0) in mm; thermal screen / services are rough
MAT = {
    "materials:Aluminium": (397.0, 89.0),
    "materials:StainlessSteel": (167.7, 17.6),
    "materials:Copper": (153.2, 14.36),
    "materials:Lead": (175.9, 5.61),
    "materials:E_Polythene": (789.0, 503.0),
    "caloBase:CEThermalScreen": (450.0, 250.0),
    "caloBase:CEService": (1660.0, 870.0),
}
CE_E_LAMBDA, CE_E_X0 = 1.4, 26.0
LAYER_VOLS = ("hgcal:HGCalEE", "hgcal:HGCalHEsil", "hgcal:HGCalHEmix")


def _strip(t):
    return t.split("}")[-1]


class Geometry:
    def __init__(self, cfi, src):
        self.files = H.xml_files_from_cfi(cfi, src)
        self.C = H.Constants()
        for f in self.files:
            try:
                self.C.add_file(f)
            except ET.ParseError:
                pass
        self.solids, self.lmat, self.children = {}, {}, {}
        self.subtractions = {}
        for f in self.files:
            if os.path.basename(f) in ("caloBase.xml", "hgcal.xml"):
                self._read_volumes(f)
        for name in self.subtractions:          # resolve chains of subtractions to their base polycone
            base = name
            while base in self.subtractions:
                base = self.subtractions[base]
            if base in self.solids:
                self.solids[name] = self.solids[base]
        self.unknown = set()
        self._read_blocks()

    def _read_volumes(self, f):
        ns = os.path.splitext(os.path.basename(f))[0]
        root = ET.parse(f).getroot()
        q = lambda n: n if ":" in n else f"{ns}:{n}"
        for el in root.iter():
            t = _strip(el.tag)
            if t == "Polycone":
                secs = []
                for zs in el:
                    if _strip(zs.tag) == "ZSection":
                        secs.append(tuple(self.C.eval(zs.get(k), ns) for k in ("z", "rMin", "rMax")))
                self.solids[q(el.get("name"))] = secs
            elif t == "SubtractionSolid":
                # caloBase 2030/v7+ cuts a box-shaped notch out of the moderator polycones at r >= 1 m (x = +-XposNotch);
                # for lines near the inner edge the solid is its base polycone, resolved after the file is read
                base = [c.get("name") for c in el if _strip(c.tag) == "rSolid"][0]
                self.subtractions[q(el.get("name"))] = q(base)
            elif t == "LogicalPart":
                solid = mat = None
                for c in el:
                    if _strip(c.tag) == "rSolid":
                        solid = q(c.get("name"))
                    elif _strip(c.tag) == "rMaterial":
                        mat = c.get("name")
                self.lmat[q(el.get("name"))] = (solid, mat)
            elif t == "PosPart":
                par = chi = rot = None
                for c in el:
                    if _strip(c.tag) == "rParent":
                        par = q(c.get("name"))
                    elif _strip(c.tag) == "rChild":
                        chi = q(c.get("name"))
                    elif _strip(c.tag) == "rRotation":
                        rot = c.get("name")
                if rot and "180D" in rot:
                    continue  # the z- endcap copy
                self.children.setdefault(par, []).append(chi)

    def _read_blocks(self):
        lam_t = {k: v[0] for k, v in MAT.items()}
        x0_t = {k: v[1] for k, v in MAT.items()}
        self.blocks = {}
        for f in self.files:
            base = os.path.basename(f)
            if base not in ("hgcalEE.xml", "hgcalHEsil.xml", "hgcalHEmix.xml"):
                continue
            vol = "hgcal:HGCal" + base[5:-4]
            out = []
            for a in H.parse_algorithms(f, self.C):
                v, n = a["vec"], a["num"]
                mats, th = a["str"].get("MaterialNames", []), v["Thickness"]
                lt = [int(x) for x in v["LayerType"]]
                use_tol = "Silicon" in a["name"]
                zi, lay = n["zMinBlock"], 0
                for nl, lth in zip([int(x) for x in v["Layers"]], v["LayerThick"]):
                    zo = zi + lth
                    if base == "hgcalEE.xml":
                        lam = x0 = None
                    else:
                        lam = sum(th[lt[k]] / lam_t[mats[lt[k]]] for k in range(lay, lay + nl) if mats[lt[k]] in lam_t)
                        x0 = sum(th[lt[k]] / x0_t[mats[lt[k]]] for k in range(lay, lay + nl) if mats[lt[k]] in x0_t)
                    rin = H.radius(zo - (H.TOL1 if use_tol else 0.0), v["ZFrontBottom"], v["RMinFront"], v["SlopeBottom"])
                    out.append([zi, zo, rin, lam, x0])
                    zi = zo
                    lay += nl
            if base == "hgcalEE.xml":
                for b in out:
                    b[3], b[4] = CE_E_LAMBDA / len(out), CE_E_X0 / len(out)
            self.blocks[vol] = [(z0, z1, rin, lam / (z1 - z0), x0 / (z1 - z0)) for z0, z1, rin, lam, x0 in out]

    def _inside(self, solid, z, r):
        secs = self.solids.get(solid)
        if not secs:
            return False
        for (za, ra0, ra1), (zb, rb0, rb1) in zip(secs[:-1], secs[1:]):
            if zb <= za or not (za <= z < zb):
                continue
            t = (z - za) / (zb - za)
            return ra0 + t * (rb0 - ra0) <= r < ra1 + t * (rb1 - ra1)
        return False

    def locate(self, z, r, vol=None):
        if vol is None:  # newer caloBase: CALOEC; old (v9-era) scenarios place HGCal directly in CALO
            vol = "caloBase:CALOEC" if "caloBase:CALOEC" in self.lmat else "caloBase:CALO"
        if not self._inside(self.lmat.get(vol, (None,))[0], z, r):
            return None
        for ch in self.children.get(vol, []):
            hit = self.locate(z, r, ch)
            if hit:
                return hit
        return vol

    def material(self, z, r):
        """-> (active, lambda_per_mm, X0_per_mm)"""
        vol = self.locate(z, r)
        if vol is None:
            return False, 0.0, 0.0
        if vol in LAYER_VOLS:
            for z0, z1, rin, ld, xd in self.blocks.get(vol, []):
                if z0 <= z < z1:
                    return (True, ld, xd) if r >= rin else (False, 0.0, 0.0)
            return False, 0.0, 0.0
        mat = self.lmat[vol][1]
        if mat in MAT:
            return False, 1.0 / MAT[mat][0], 1.0 / MAT[mat][1]
        if mat != "materials:Air":
            self.unknown.add(mat)
        return False, 0.0, 0.0
