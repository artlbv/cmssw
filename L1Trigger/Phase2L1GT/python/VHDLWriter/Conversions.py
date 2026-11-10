import L1Trigger.Phase2L1GT.VHDLWriter.Conditions as cond
import L1Trigger.Phase2L1GT.VHDLWriter.Writer as writer




def checkFilter(filt):
    """
    takes in a cmssw process object and
    checks if filter is a known menu condition
    converts it to corresponding Condition object defined in 
    Conditions.py
    """
    knownConditions = [cond.SingleObjCond, cond.DoubleObjCond, cond.TripleObjCond,cond.QuadObjCond]
    Condit = None
    for Condition in knownConditions:
        try:
            if filt.type_() == Condition.Label:
                Condit = Condition()
        except Exception as ex:
            pass
    if Condit == None:
        return 0
    collections = Condit.getCollections(filt)
    for idx, col in collections.items():
        knowncuts = Condit._cut_aliases.keys()
        for knowncut in knowncuts:
            if col.hasParameter(knowncut):
                Condit.setCut(knowncut, col.getParameter(knowncut).value(), False, idx, Condit.NumberOfCollections)
                Condit.addResources(knowncut)

    if Condit.Label in ["L1GTTripleObjectCond", "L1GTQuadObjectCond"]:
        # Handle the double correlations
        for idx, col in Condit.getCorrelations(filt).items():
            knowncuts = Condit._cut_aliases.keys()
            for knowncut in knowncuts:
                if col is not None and col.hasParameter(knowncut):
                    Condit.setCut(knowncut, col.getParameter(knowncut).value(), False, idx, Condit.NumberOfCorrelations)
                    Condit.addResources(knowncut)
        # Handle the triple correlations (only for QuadObjectCond)
        if Condit.Label == "L1GTQuadObjectCond":
            for idx, col in Condit.get3BodyCorrelations(filt).items():
                knowncuts = Condit._3bodycut_aliases.keys()
                for knowncut in knowncuts:
                    if col is not None and col.hasParameter(knowncut):
                        Condit.setCut(knowncut, col.getParameter(knowncut).value(), True, idx, Condit.NumberOf3BodyCorrelations)
                        Condit.addResources(knowncut)
    knowncuts = Condit._cut_aliases.keys()
    for knowncut in knowncuts:
        if filt.hasParameter(knowncut):
            if Condit.Label == "L1GTTripleObjectCond" and knowncut in Condit._3bodycut_aliases:
                Condit.setCut(knowncut, filt.getParameter(knowncut).value(), True )
                Condit.addResources(knowncut)
            else:
                Condit.setCut(knowncut, filt.getParameter(knowncut).value())
                Condit.addResources(knowncut)
    for idx, tag in enumerate(Condit._InputTags):
        Condit._setInputObject(idx + 1, tag.productInstanceLabel)
    return Condit

def assignAlgoBits(obj):
    Algobitlist = obj.channelConfig.value().pop().getParameter('algoBits')
    algos = cond.defineAlgoBits()
    for Bititem in Algobitlist:
        name = Bititem.bitPos.value()
        value = Bititem.path.value()
        algos.SetBit(value,name)
    return algos


def getConditionsfromConfig(obj):
    filterdict = {}
    for key,value in obj.filters.items():
        x = checkFilter(value)
        if x != 0:
            filterdict[key] = x 
            addPathsToModule(obj,key,filterdict[key])
    return filterdict

def findPaths(obj,modulename):
    pathlist = []
    for path in obj.paths.values():
        if modulename in path.moduleNames():
            pathlist.append(path.label())
    return pathlist


def getModulesfromPath(menu,algobits):
    modules = {}
    for key,value in algobits.Assignment.items():
        modules[key] = menu.paths[key].moduleNames()
    return modules


def checkiflogicalcombination(filterlist,algobits):
    filterpaths =  [path for filt in filterlist for path in filt.Path]
    combinatorialpath = []
    for algopath in algobits.keys():     
        if algopath not in filterpaths:
            combinatorialpath.append(algopath)
    return combinatorialpath

def sortAlgodictWithIndices(menu):
    algo_dict = {}
    # Extract names and expressions
    for algo in menu.algorithms:
        if hasattr(algo, "name") and algo.name.value():
            algo_str = algo.name.value()
        else:
            algo_str = algo.expression.value()  
        algo_expr = algo.expression.value() if hasattr(algo, "expression") else "N/A"
        algo_dict[algo_str] = algo_expr  
    # Sort the dictionary based on the algorithm name (key)
    sorted_items = sorted(algo_dict.items(), key=lambda item: item[0])
    # Create a new dictionary with index-based sorting while keeping expressions
    sorted_algo_dict = {idx: {"name": name, "expression": expr} for idx, (name, expr) in enumerate(sorted_items)}
    # print("Sorted Algorithm Dictionary:")
    return sorted_algo_dict


# Adjust this for the cases of more filters per expression (and/or/xor)
def getLogicalFilters(menu,knownfilters):
    combinatorialfilters = {} 
    for algo in menu.algorithms:
        for path in menu.paths:
            pathmodules = menu.paths[path].moduleNames()
            for module in pathmodules:
                if path in algo.expression.value():
                    expression = algo.expression.value()
                    containsmodules = getModules(menu,expression)
                    for mod in containsmodules:
                            if mod in knownfilters.keys(): # checks if any of these modules are known filters
                                combinatorialfilters[path] = cond.LogicalFilter(module,expression,containsmodules)
                                break
    return combinatorialfilters

def getModules(obj,expression):
    words = expression.split()
    modulelist = []
    moduleset = {}
    for word in words:
        try:
            moduleset = (obj.paths[word].moduleNames())
        except:
            pass
        if moduleset != set():
            modulelist.append(moduleset.pop())
        if moduleset != set():
            print("warning %s is part of a combinatorial logic and its path contains more than 1 modules, this will lead to undefined behaviour".format(word))
    return modulelist



def associatePathAndModules(menu,knownfilters):
    pathswithmodules = {}    
    for path in menu.paths:
           x = menu.paths[path].moduleNames()
           for module in x:
               for filt in knownfilters.keys():
                   if filt == module:
                        pathswithmodules.setdefault(filt,[]).append(path)
    return pathswithmodules


def addPathsToModule(menu,filtername,filtervalue):    
    for path in menu.paths:
           modules = menu.paths[path].moduleNames()
           for module in modules:
                if filtername == module:
                    filtervalue.addPath(path)



def writeAlgoblocks(conditions,logfilt):
    algodict = cond.Algorithmsdict()
    algodict.addLogicalFilters(logfilt)
    algodict.addConditions(conditions)
    return algodict
        
def distributeAlgos(algodict,numslrs):
    algounits = []
    for i in range(numslrs):
        algounits.append(cond.AlgorithmBlock())
    flip = (numslrs -1) * -1
    count = 0

    addmax = algodict.popMaxalgoblock()
    if(numslrs == 1):
        while(addmax != 0):
            algounits[count].Combineblocks(addmax)
            addmax = algodict.popMaxalgoblock()
        return algounits
    else:
        algounits[numslrs-1 - abs(flip)].Combineblocks(addmax)
        flip += 1

        while(addmax != 0):
            addmax = algodict.popMaxalgoblock()
            if addmax != 0:
                algounits[numslrs-1 - abs(flip)].Combineblocks(addmax)
            if (numslrs-1 - abs(flip) == 0) or (numslrs-1 - abs(flip) == numslrs - 1):
                if addmax != 0:
                    addmax = algodict.popMaxalgoblock()
                    if addmax != 0:
                        algounits[numslrs-1 - abs(flip)].Combineblocks(addmax)
            flip += 1
            if flip == (numslrs -1):
                flip = (numslrs -1) * -1
        return algounits

def distributeAlgosWithoutopt(algodict,numslrs):
    algounits = []
    for i in range(numslrs):
        algounits.append(cond.AlgorithmBlock())
    flip = (numslrs -1) * -1
    count = 0

    addmax = algodict.algoblocks.pop()
    if(numslrs == 1):
        while(algodict.algoblocks != []):
            algounits[count].Combineblocks(addmax)
            addmax = algodict.algoblocks.pop()
        return algounits
    else:
        algounits[numslrs-1 - abs(flip)].Combineblocks(addmax)
        flip += 1

        while(algodict.algoblocks != []):
            addmax = algodict.algoblocks.pop()
            algounits[numslrs-1 - abs(flip)].Combineblocks(addmax)
            if (numslrs-1 - abs(flip) == 0) or (numslrs-1 - abs(flip) == numslrs - 1):
                if algodict.algoblocks != []:
                    addmax = algodict.algoblocks.pop()
                    if algodict.algoblocks != []:
                        algounits[numslrs-1 - abs(flip)].Combineblocks(addmax)
            flip += 1
            if flip == (numslrs -1):
                flip = (numslrs -1) * -1
        return algounits

def distributeAlgosAtRandom(algodict,numslrs,seed = 2):
    import random as rand
    rand.seed = seed

    algounits = []
    for i in range(numslrs):
        algounits.append(cond.AlgorithmBlock())
    addalgo = algodict.algoblocks.pop()
    while(algodict.algoblocks != []):
        algounits[rand.randint(0,(numslrs - 1))].Combineblocks(addalgo)
        addalgo = algodict.algoblocks.pop()
    return algounits

def assignAlgostoSlrs(knownfilters,logicalcombinations,numslrs):
    algoblocks = WriteAlgoDict(knownfilters,logicalcombinations)
    distributedAlgos = distributealgos(algoblocks,numslrs)
    return distributedAlgos

def writeAlgounits(distributedAlgos,algomap,knownfilters,logcomb):
    for index,value in enumerate(distributedAlgos):
        modules = dict()
        paths = dict()
        condtext = ""
        algounittext = ""
        bits = {}
        tdistributedAlgos = {}
        logicalcombinations = dict()
        for mod in value.Modules:
            condtext += writer.conditionwriter(mod,knownfilters[mod])
            tdistributedAlgos[mod] = knownfilters[mod]
        if(value.LogicalPath != set()):
            for log in value.LogicalPath:
                logicalcombinations[log] = logcomb[log]
        algounittext = writer.algounitWriter(algomap,condtext,tdistributedAlgos,logicalcombinations,index)
        writer.writeAlgounitToFile("p2gt_algos_slr{}.vhd".format(index),algounittext)


def getAlgobits(algomap,distributedalgos,Outputchans):
    chans = Outputchans
    print(f"chans: {chans}")
    algosdict = {}
    for block in distributedalgos: 
        algochan = chans.pop(0)
        print(f"algochan: {algochan}")
        algodict = {}
        for key,conf in algomap.items():
            name_in_paths = conf['name'] in block.Paths or conf['name'] in block.LogicalPath
            # if " and " in conf['expression'] or " or " in conf['expression'] or " xor " in conf['expression']:
            #     expression_components = conf['expression'].replace(" and ", " ").replace(" or ", " ").split().replace(" xor ", " ").split()
            if " and " in conf['expression'] or " or " in conf['expression'] or " xor " in conf['expression']:
                expr = conf['expression'].replace(" and ", " ").replace(" or ", " ").replace(" xor ", " ")
                expression_components = expr.split()
            else:
                expression_components = [conf['expression']]
            expression_in_paths = any(comp in block.Paths or comp in block.LogicalPath for comp in expression_components)
            if name_in_paths or expression_in_paths:
                algodict[key] = conf['expression']
                print(f"\talgodict[{key:<2}]: {algodict[key]}")
        algosdict[algochan] = algodict
    return algosdict

