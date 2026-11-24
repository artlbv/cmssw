#!/usr/bin/env python3
"""Download the DDD XML of geometry scenarios that are no longer in CMSSW, for the HGCAL-HF transition study.

  D35 (HGCAL v9,  HGCAL TDR era)  from CMSSW_11_0_0 -> <workdir>/D35_cfi.py + <workdir>/v9src/Geometry/...
  D41 (HGCAL v10, L1 TDR)         from CMSSW_11_0_0 -> <workdir>/D41_cfi.py + <workdir>/v10src/Geometry/...
  D49 (HGCAL v11, HLT TDR)        from CMSSW_12_0_0 -> <workdir>/D49_cfi.py + <workdir>/v11src/Geometry/...

The workdir is $HGCAL_HF_WORKDIR (default ./hgcal_hf_work), the same one the plotting scripts read.
Files come from raw.githubusercontent.com/cms-sw/cmssw; existing files are not downloaded again.
"""
import os
import re
import sys
import urllib.request

RAW = "https://raw.githubusercontent.com/cms-sw/cmssw"
SCENARIOS = [  # (tag, scenario file name, local cfi name, xml dir)
    ("CMSSW_11_0_0", "cmsExtendedGeometry2026D35XML_cfi.py", "D35_cfi.py", "v9src"),
    ("CMSSW_11_0_0", "cmsExtendedGeometry2026D41XML_cfi.py", "D41_cfi.py", "v10src"),
    ("CMSSW_12_0_0", "cmsExtendedGeometry2026D49XML_cfi.py", "D49_cfi.py", "v11src"),
]


def get(url, dest):
    if os.path.exists(dest):
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as r:
        data = r.read()
    with open(dest, "wb") as f:
        f.write(data)


def main():
    work = os.path.abspath(os.environ.get("HGCAL_HF_WORKDIR", "hgcal_hf_work"))
    os.makedirs(work, exist_ok=True)
    failed = 0
    for tag, cfi, local, xmldir in SCENARIOS:
        dest_cfi = os.path.join(work, local)
        get(f"{RAW}/{tag}/Geometry/CMSCommonData/python/{cfi}", dest_cfi)
        files = sorted(set(re.findall(r"['\"](Geometry/[^'\"]+\.xml)['\"]", open(dest_cfi).read())))
        print(f"{local}: {len(files)} XML files from {tag}")
        for f in files:
            try:
                get(f"{RAW}/{tag}/{f}", os.path.join(work, xmldir, f))
            except Exception as ex:  # keep going; the geometry model only needs caloBase + hgcal files
                failed += 1
                print(f"  FAILED {f}: {ex}", file=sys.stderr)
    print(f"done, workdir {work}" + (f", {failed} downloads failed" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
