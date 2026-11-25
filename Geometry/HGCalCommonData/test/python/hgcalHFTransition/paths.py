"""Common locations for the HGCAL-HF transition scripts.

CMSSW_SRC        : CMSSW checkout with the current geometry XML (default: derived from this file's location)
HGCAL_HF_WORKDIR : work directory with the fetched old geometries (fetch_old_geometries.py), caches and plots
                   (default: ./hgcal_hf_work)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CMSSW_SRC = os.environ.get("CMSSW_SRC", os.path.abspath(os.path.join(HERE, *[".."] * 5)))
WORK = os.path.abspath(os.environ.get("HGCAL_HF_WORKDIR", "hgcal_hf_work"))
CFI = os.path.join(CMSSW_SRC, "Geometry", "CMSCommonData", "python")
TOOLS = os.path.abspath(os.path.join(HERE, ".."))   # hgcalInnerRadiusVsZ.py
