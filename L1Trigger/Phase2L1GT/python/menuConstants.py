from os import environ
import json

# print(os.path.exists("./scalings_v44.json"))
scalings_fname = environ["CMSSW_BASE"] + "/src/L1Trigger/Phase2L1GT/python/scalings_v44.json"
with open(scalings_fname, 'r') as file:
    scalings = json.load(file)

def off2onl(thr, obj, id, region, scalings = scalings):
    offset = scalings[obj][id][region]["offset"]
    slope = scalings[obj][id][region]["slope"]
    return (thr - offset)/slope

def getObjectThrs(thr, obj, id):
    return tuple(off2onl(thr, obj, id, region) for region in scalings[obj][id].keys())

objectIDs = {
    "L1nnPuppiTau": {
        "default": {
            "qual" : 225
        }
    },
    "L1tkPhoton":{
        "Iso": {
            "qual": {
                "barrel": 0b0010,
                "endcap": 0b0100,
            },
            "iso": {
                "barrel": 0.25,
                "endcap": 0.205,
            }
        }
    },
    "L1tkElectron":{
        "Iso": {
            # "qual": {
            #     "barrel": 0b0010,
            #     "endcap": 0b0010,
            # },
            "iso": {
                "barrel": 0.13,
                "endcap": 0.28,
            }
        },
        "NoIso": {
            "qual": {
                "barrel": 0b0010,
                "endcap": 0b0010,
            },
        },
        "NoIsoLowPt": {
            "qual": {
                "barrel": 0b0010,
                "endcap": 0b0000,
            },
        }
    },
    "L1gmtTkMuon":{
        "VLoose": {
            "qual": 0b0001,
        },
        "Loose": {
            "qual": 0b0010,
        },
        "Medium": {
            "qual": 0b0100,
        },
        "Tight": {
            "qual": 0b1000,
        },
    }
}

def getObjectIDs(obj, id, objDict = objectIDs):
    values = objDict[obj][id]["qual"]
    if isinstance(values, dict):
        return tuple(values.values())
    else:
        return values
    

def getObjectISOs(obj, id, objDict = objectIDs):
    values = objDict[obj][id]["iso"]
    if isinstance(values, dict):
        return tuple(values.values())
    else:
        return values