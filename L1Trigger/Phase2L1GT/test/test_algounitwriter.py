# python3 L1Trigger/Phase2L1GT/test/test_algounitwriter.py -i ${MENU} -n ${NUMBER_OF_SLR} [-o ${OUTPUT_DIR}]
# ${MENU} is a menu file or python module name, either a GT menu cff or a configuration fragment that contains
# the menu (e.g. the standalone Phase-2 L1 configuration).
# example command for Step-1 menu configuration, using VU13P:
# python3 L1Trigger/Phase2L1GT/test/test_algounitwriter.py -i L1Trigger/Configuration/python/Phase2GTMenus/SeedDefinitions/step1_2024/l1tGTMenu_cff.py -n 4
# or equivalently
# python3 L1Trigger/Phase2L1GT/test/test_algounitwriter.py -i L1Trigger.Configuration.Phase2GTMenus.SeedDefinitions.step1_2024.l1tGTMenu_cff -n 4


import L1Trigger.Phase2L1GT.VHDLWriter.Conversions as conversions
import FWCore.ParameterSet.Config as cms
import importlib.util
import os, sys
import argparse

def options():
    parser = argparse.ArgumentParser(usage=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", nargs="+", help="Input menu files or python modules (space separated)")
    parser.add_argument("-n", help="Number of SLRs", default="4")
    parser.add_argument("-o", help="Output directory for the VHDL files", default=".")
    # parser.add_argument("-b", help="Board number", default="1") # inclusion in the future
    args = parser.parse_args()
    return args

def load_menu_module(menu, filepath):
    modulename = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(modulename, filepath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[modulename] = module
    spec.loader.exec_module(module)
    menu.extend(sys.modules[modulename])

def validate_existence(ops):
    if not ops.i:
        raise ValueError("Please provide a menu file or module using -i.")
    for file in ops.i:
        if not os.path.isfile(file) and importlib.util.find_spec(file) is None:
            raise FileNotFoundError(f"Neither a file nor a python module: {file}")
    if ops.n:
        try:
            int(ops.n)
        except ValueError:
            raise ValueError(f"Invalid input for -n: '{ops.n}' is not an integer.")
    if not os.path.isdir(ops.o):
        raise FileNotFoundError(f"Output directory does not exist: {ops.o}")
    # if ops.b:
    #     try:
    #         int(ops.b)
    #     except ValueError:
    #         raise ValueError(f"Invalid input for -b: '{ops.b}' is not an integer.")

ops = options()
validate_existence(ops)

# Create a dummy process, to be able to retrieve algorithms, moduleNames, filters
menu = cms.Process('VHDLWriter')

for input_file in ops.i:
    if os.path.isfile(input_file):
        load_menu_module(menu, input_file)
    else:
        menu.load(input_file)

# They must be deleted to avoid unnecessary objects in the menu process
# (the menu cffs define them, a configuration fragment does not)
for template in ("l1tGTSingleObjectCond", "l1tGTDoubleObjectCond", "l1tGTTripleObjectCond", "l1tGTQuadObjectCond"):
    if hasattr(menu, template):
        delattr(menu, template)

# the algorithms are taken from the algo block producer, the menu cffs also define them as a top-level VPSet
if hasattr(menu, "l1tGTAlgoBlockProducer"):
    algorithms = menu.l1tGTAlgoBlockProducer.algorithms
elif hasattr(menu, "algorithms"):
    algorithms = menu.algorithms
else:
    raise RuntimeError("No algorithms found: the input must define l1tGTAlgoBlockProducer or an 'algorithms' VPSet")

knownfilters = dict()
logicalcombinations = dict()
distributedalgos = dict()

if int(ops.n) == 4:
    algobit_channels = [0, 24, 32, 48]
elif int(ops.n) == 3:
    algobit_channels = [0, 28, 46]
else:
    raise ValueError(f"Unsupported value for ops.n: {ops.n}")

# loops over all algos, extract the expression, remove the '_',
# saves them in a dict (original, modified), sort the dictionary
# assigns an algobit to each algo.
algobitmap = conversions.sortAlgodictWithIndices(algorithms)

# takes in a cmssw process object and checks if filter
# is a known gt condition converts it to corresponding
# Condition object defined in Conditions.py
knownfilters = conversions.getConditionsfromConfig(menu)

# For each module in a path:
# Check if it's a filter and of type "PathStatusFilter". Retrieve its logical expression.
# Analyze the modules, If any of these modules are in knownfilters, update combinatorialfilters.
# Return a dictionary summarizing the combinatorial filters for each path.
logicalcombinations = conversions.getLogicalFilters(menu, algorithms, knownfilters)

algoblocks = conversions.writeAlgoblocks(knownfilters, logicalcombinations)

distributedalgos = conversions.distributeAlgos(algoblocks, int(ops.n))  # 4 is the number of slrs. Distributes algos in all slrs

# handles the writing of the algos in vhdl file
conversions.writeAlgounits(distributedalgos, algobitmap, knownfilters, logicalcombinations, ops.o)

distributed_algomap = conversions.getAlgobits(algobitmap, distributedalgos, algobit_channels)
