import FWCore.ParameterSet.Config as cms

from L1Trigger.Phase2L1GT.l1tObjectScalings import scalings
from L1Trigger.Phase2L1GT.l1tObjectIDs import objectIDs

def off2onl_thresholds(thr, obj, id, region, scalings = scalings):
    offset = scalings[obj][id][region]["offset"]
    slope = scalings[obj][id][region]["slope"]
    new_thr = round((thr - offset)/slope, 1)

    if "Jet" in obj:
        # safety cut
        return max(25, new_thr)
    else:
        return max(0, new_thr)

def getObjectThrs(thr, obj, id):
    regions = scalings[obj][id].keys()
    if "overlap" in regions:
        # fix order for the case of overlap region as the alphabetic sorting messes up the order
        regions = ["barrel","overlap","endcap"]
    if len(regions) > 1:
        return cms.vdouble(tuple(off2onl_thresholds(thr, obj, id, region) for region in regions))
    else:
        return cms.double([off2onl_thresholds(thr, obj, id, region) for region in regions][0])

def getObjectIDs(obj, id, objDict = objectIDs):
    values = objDict[obj][id]["qual"]
    if isinstance(values, dict):
        return cms.vuint32(tuple(values.values()))
    else:
        return cms.uint32(values)
    
def getObjectISOs(obj, id, objDict = objectIDs):
    values = objDict[obj][id]["iso"]
    if isinstance(values, dict):
        return cms.vdouble(tuple(values.values()))
    else:
        return cms.double(values)