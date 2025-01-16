"""
Module for handling L1 trigger menu constants and conversions.
"""

import FWCore.ParameterSet.Config as cms
from L1Trigger.Phase2L1GT.l1tGTObject_scalings import scalings
from L1Trigger.Phase2L1GT.l1tGTObject_ids import objectIDs

obj_regions_abseta_lowbounds = {
    "CL2Photons": { "barrel": 0, "endcap": 1.479 },
    "CL2Electrons": { "barrel": 0, "endcap": 1.479 },

    "CL2Taus": { "barrel": 0, "endcap": 1.5 },
    "CL2Jets": { "barrel": 0, "endcap": 1.5, "forward": 2.4 },

    "GMTTkMuons": { "barrel": 0, "overlap": 0.83, "endcap": 1.24 },
    "GMTMuons": { "barrel": 0, "overlap": 0.83, "endcap": 1.24 },
}

def off2onl_thresholds(thr, obj, id, region, scalings=scalings):
    """
    Convert offline thresholds to online thresholds.

    Args:
        thr (float): The offline threshold.
        obj (str): The object type.
        id (str): The object ID.
        region (str): The region.
        scalings (dict): The scalings dictionary.

    Returns:
        float: The online threshold.
    """
    offset = scalings[obj][id][region]["offset"]
    slope = scalings[obj][id][region]["slope"]
    new_thr = round((thr - offset) / slope, 1)

    if "Jet" in obj:
        # Safety cut
        return max(25, new_thr)
    else:
        return max(0, new_thr)

def get_object_thrs(thr, obj, id, regions=None, scalings=scalings):
    """
    Get object thresholds for specified regions.

    Args:
        thr (float): The threshold.
        obj (str): The object type.
        id (str): The object ID.
        regions (list, optional): The regions. Defaults to None.

    Returns:
        cms.vdouble or cms.double: The thresholds for the regions.
    """
    if regions is None:
        # dict_regions = sorted(scalings[obj][id].keys())
        # obj_regions = list(obj_regions_abseta_lowbounds[obj].keys())

        # if sorted(dict_regions) == sorted(obj_regions):
        #     regions = sorted(obj_regions)
        # else:
        #     print(f"Regions for {obj} not found in scalings file. Using all regions.")
        #     print(f"Regions in scalings file: {dict_regions}")
        #     print(f"Regions for {obj}: {obj_regions}")
        #     exit(1)
        regions = scalings[obj][id].keys()

        if "overlap" in regions:
            # Fix order for the case of overlap region as the alphabetic sorting messes up the order
            regions = ["barrel", "overlap", "endcap"]

    thresholds = [off2onl_thresholds(thr, obj, id, region) for region in regions]
    if len(thresholds) > 1:
        return cms.vdouble(tuple(thresholds))
    else:
        return cms.double(thresholds[0])

def get_object_ids(obj, id, obj_dict=objectIDs):
    """
    Get object IDs.

    Args:
        obj (str): The object type.
        id (str): The object ID.
        obj_dict (dict): The object dictionary.

    Returns:
        cms.vuint32 or cms.uint32: The object IDs.
    """
    values = obj_dict[obj][id]["qual"]
    if isinstance(values, dict):
        return cms.vuint32(tuple(values.values()))
    else:
        return cms.uint32(values)

def get_object_isos(obj, id, obj_dict=objectIDs):
    """
    Get object isolation values.

    Args:
        obj (str): The object type.
        id (str): The object ID.
        obj_dict (dict): The object dictionary.

    Returns:
        cms.vuint32 or cms.uint32: The object isolation threshold values.
    """
    values = obj_dict[obj][id]["iso"]
    if isinstance(values, dict):
        return cms.vdouble(tuple(values.values()))
    else:
        return cms.double(values)