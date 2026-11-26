# HGCAL–HF transition: dead material and the L1 forward-jet hole

Standalone scripts (no CMSSW runtime needed) that build a straight-line material model of the
endcap calorimeter region from the DDD XML of several geometry scenarios and compare the energy
that can reach active material with measured Phase-2 L1 calo-jet matching efficiencies at
3 < |η| < 3.5.

Full write-up with figures: https://claude.ai/artifact/RKRtArkqjbkPLJUn7nADvn (private; ask the owner for access).

| HGCAL | Scenario | Samples |
|---|---|---|
| v9  | D35  | HGCAL TDR era (pre-L1-TDR samples) |
| v10 | D41  | L1 TDR (`PhaseIITDRSpring19`) |
| v11 | D49  | HLT TDR (inner geometry identical to v10 at the transition) |
| v17 | D110 | Spring24 |
| v19 | D128 | current default |

## Files

- `geomodel.py` – r–z material model: caloBase + `hgcal.xml` polycones (innermost volume containing
  the point) and the HGCAL layer blocks of the DDD algorithms (active where the line is at or above the
  block's inner radius). Uses `../hgcalInnerRadiusVsZ.py` to parse the XML.
- `fetch_old_geometries.py` – downloads the D35, D41 and D49 XML (removed from current CMSSW) from
  `cms-sw/cmssw` tags CMSSW_11_0_0 / CMSSW_12_0_0.
- `plot_material_geos.py` – active vs dead interaction lengths per geometry (v9, v10/v11, v17, v19).
- `plot_dead_compare.py` – total dead material of all geometries on one plot.
- `plot_material_split.py [v17|v10|v9]` – material of one geometry with the dead material outside HGCAL split into
  thermal screen, neutron moderator and services (v10 stands for v10/v11).
- `plot_layers_crossed.py` – number of HGCAL sensor layers a straight line crosses vs |η| (outer and
  inner edge), per geometry.
- `plot_containment_geos.py` – visible energy fraction (shower-containment estimate) for v9, v10/v11
  and v17, overlaid with L1 calo-jet matching efficiencies read off published plots.

Wafer-level silicon coverage (replaces the layer envelope as the definition of "active"):

- `paths.py` – common locations (`CMSSW_SRC`, `HGCAL_HF_WORKDIR`).
- `waferxy_build.py` – compiles CMSSW's own `HGCalWaferMask::waferXY` (copied from this checkout's
  `src/HGCalWaferMask.cc`) into a small helper in the work directory; used for exact partial-wafer outlines.
  Needs a C++17 compiler (`g++`, or set `CXX`).
- `coverage.py` – places every wafer of v17 (D110) and v19 (D128) as the DDD algorithms do (wafer lists,
  partial-wafer outlines, cassette shifts, layer rotation) and counts the silicon layers a line crosses vs (|η|, φ).
- `plot_silicon_coverage.py` – silicon layers crossed vs the layer-envelope count, v17 and v19.
- `silicon.py` – per sensor plane, the fraction of the ring at radius r covered by silicon, for v17/v19 (wafer lists)
  and v9–v11 (old rule: full hexagonal wafers only, placed when all six corners lie inside the layer annulus,
  as in `DDHGCalEEAlgo`/`DDHGCalHEAlgo`).
- `containment_si.py` – containment estimate with an absorber block's deposit counted in proportion to that
  coverage, smoothed by the lateral shower size (hadronic 60 mm, EM 25 mm); HF active for |η| ≥ 2.98 (below that
  the muon-endcap steel shadows it). Writes both the envelope and the silicon curves for v9, v10, v11, v17, v19.
- `screen_fix_v17.py` / `plot_screen_fix_v17.py` – v17 dead material and visible fraction with the thermal screen as
  defined in CMSSW (`CEThermalScreen`, 1.77 g/cm3, mostly iron-loaded "Insulation": λ_I = 67 cm, X0 = 9.2 cm) and with the
  real design (2 mm Al shell + Cryogel Z aerogel, 0.16 g/cm3), plus the rough λ = 45 cm used in the other plots.
- `plot_containment_silicon.py` – envelope vs silicon per geometry with the measured L1 calo-jet efficiencies,
  and all geometries on one panel.

## Inner radius vs z

`../hgcalInnerRadiusVsZ.py` (one level up) reconstructs, per sensor plane, the HGCAL inner radius,
layer z positions and innermost wafers from the DDD XML of any scenario, for both the current
cassette algorithms (v17–v19) and the older pre-cassette ones (v9–v11). `geomodel.py` uses its XML
parser and radius lookup.

```bash
python3 Geometry/HGCalCommonData/test/python/hgcalInnerRadiusVsZ.py \
    --cfi Geometry/CMSCommonData/python/cmsExtendedGeometryRun4D128XML_cfi.py --csv D128.csv
```

For an old scenario, point it at the fetched files: `--cfi $HGCAL_HF_WORKDIR/D41_cfi.py --src $HGCAL_HF_WORKDIR/v10src`.

## Running

Needs Python 3 with numpy, matplotlib and scipy. From any directory:

```bash
export HGCAL_HF_WORKDIR=$PWD/hgcal_hf_work      # default: ./hgcal_hf_work
python3 Geometry/HGCalCommonData/test/python/hgcalHFTransition/fetch_old_geometries.py
python3 Geometry/HGCalCommonData/test/python/hgcalHFTransition/plot_material_geos.py
python3 Geometry/HGCalCommonData/test/python/hgcalHFTransition/plot_dead_compare.py
python3 Geometry/HGCalCommonData/test/python/hgcalHFTransition/plot_material_split.py v17
python3 Geometry/HGCalCommonData/test/python/hgcalHFTransition/plot_material_split.py v10
python3 Geometry/HGCalCommonData/test/python/hgcalHFTransition/plot_containment_geos.py
python3 Geometry/HGCalCommonData/test/python/hgcalHFTransition/plot_layers_crossed.py
python3 Geometry/HGCalCommonData/test/python/hgcalHFTransition/coverage.py
python3 Geometry/HGCalCommonData/test/python/hgcalHFTransition/plot_silicon_coverage.py
python3 Geometry/HGCalCommonData/test/python/hgcalHFTransition/containment_si.py
python3 Geometry/HGCalCommonData/test/python/hgcalHFTransition/plot_containment_silicon.py
python3 Geometry/HGCalCommonData/test/python/hgcalHFTransition/screen_fix_v17.py
python3 Geometry/HGCalCommonData/test/python/hgcalHFTransition/plot_screen_fix_v17.py
```

The current-geometry XML (D110, D128) is read from this checkout; set `CMSSW_SRC` to use another one.
Plots are written to the work directory.

## Model and caveats

- The silicon model is pessimistic for partial losses (no jet cone, narrow lateral spread), the envelope model is
  optimistic; L1 matching efficiencies (any L1 jet within ΔR, no p_T cut) saturate for partial losses and are not
  expected to follow the visible fraction one-to-one.

- Straight lines from the origin, z = 2.9–5.3 m; no vertex spread, magnetic field, lateral shower spread
  or jet cone.
- Hadrons (70 %): first interaction in λ, gamma longitudinal profile Γ(2.2, 0.87/λ). Photons (30 %):
  conversion after 9/7 X0, profile Γ(3.85, 0.5/X0). Energy in crossed active HGCAL blocks, or leaking into
  HF beyond |η| = 3 (assumed fully active), counts as seen; energy in dead material is lost.
- CE-E fixed at 1.4 λ / 26 X0; CE-H from its steel/copper thicknesses; thermal screen λ ≈ 45 cm,
  X0 ≈ 25 cm assumed.
- The L1 efficiencies in `plot_containment_geos.py` were read off plot images (±0.01–0.03) and are not
  like-for-like: v9 calo jets not firmware-emulated; p_T > 100 GeV (v9, v10/v11) vs 100–300 GeV (v17);
  |η| bins ≈ 0.42, 0.25 and 0.05.
