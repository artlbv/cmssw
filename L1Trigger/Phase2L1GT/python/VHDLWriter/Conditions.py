from ast import Mod
from modulefinder import Module
from queue import Empty
from L1Trigger.Phase2L1GT.l1tGTScales import scale_parameter
from libL1TriggerPhase2L1GT import L1GTScales as CppScales
l1tGTScales = CppScales(*[param.value() for param in scale_parameter.parameters_().values()])

class Condition:
    """
    Base Class for all EDFilters that correspond to an P2GT condition
    Contains: Cuts, The VHDL Resource usage, Paths corresponding to the Modules in the config
    """
    _ObjectNameConversions = {
        "GTTPromptJets"       : "GTT_PROMPT_JETS_SLOT",
        "GTTDisplacedJets"    : "GTT_DISPLACED_JETS_SLOT",
        "GTTPromptHtSum"      : "GTT_HT_MISS_PROMPT_SLOT",
        "GTTDisplacedHtSum"   : "GTT_HT_MISS_DISPLACED_SLOT",
        "GTTEtSum"            : "GTT_ET_MISS_SLOT",
        "GTTTaus"             : "GTT_TAUS_SLOT",
        "GTTPhiCandidates"    : "GTT_PHI_CANDIDATE_SLOT",
        "GTTRhoCandidates"    : "GTT_RHO_CANDIDATE_SLOT",
        "GTTBsCandidates"     : "GTT_BS_CANDIDATE_SLOT",
        "GTTPrimaryVert"      : "GTT_PRIM_VERT_SLOT",
        "CL2Jets"             : "CL2_JET_SLOT",
        "CL2HtSum"            : "CL2_HT_MISS_SLOT",
        "CL2EtSum"            : "CL2_ET_MISS_SLOT",
        "CL2Taus"             : "CL2_TAU_SLOT",
        "CL2Electrons"        : "CL2_ELECTRON_SLOT",
        "CL2Photons"          : "CL2_PHOTON_SLOT",
        "GCTNonIsoEg"         : "GCT_NON_ISO_EG_SLOT",
        "GCTIsoEg"            : "GCT_ISO_EG_SLOT",
        "GCTJets"             : "GCT_JETS_SLOT",
        "GCTTaus"             : "GCT_TAUS_SLOT",
        "GCTHtSum"            : "GCT_HT_MISS_SLOT",
        "GCTEtSum"            : "GCT_ET_MISS_SLOT",
        "GMTSaPromptMuons"    : "GMT_SA_PROMPT_SLOT",
        "GMTSaDisplacedMuons" : "GMT_SA_DISPLACED_SLOT",
        "GMTTkMuons"          : "GMT_TK_MUON_SLOT",
        "GMTTopo"             : "GMT_TOPO_SLOT"        
    }

    def __init__(self):
        self.Cuts = {}
        self.InputObjects = {}
        self._InputTags = []
        self.Paths = []
        self.ResourceUseage = CutResources()
        self.ResourcesperCut = {
            ('minPt') : CutResources(bram = 0 , dsp = 0, lut = 110),
            ('minEta','maxEta') : CutResources(bram = 0 , dsp = 0, lut = 120),
            ('minPhi','maxPhi') : CutResources(bram = 0 , dsp = 0, lut = 123),
            ('minZ0','maxZ0') : CutResources(bram = 0 , dsp = 0, lut = 123),
            ('qual') : CutResources(bram = 0 , dsp = 0, lut = 40),
            ('iso') : CutResources(bram = 0 , dsp = 0, lut = 40)

        }
        self._HWConversionFunctions = {
            # SingleCollectionCuts
            'minPt'          : l1tGTScales.to_hw_pT_floor,
            'maxPt'          : l1tGTScales.to_hw_pT_ceil,
            'minEta'         : l1tGTScales.to_hw_eta_floor,
            'maxEta'         : l1tGTScales.to_hw_eta_ceil,
            'minPhi'         : l1tGTScales.to_hw_phi_floor,
            'maxPhi'         : l1tGTScales.to_hw_phi_ceil,
            'minZ0'          : l1tGTScales.to_hw_z0_floor,
            'maxZ0'          : l1tGTScales.to_hw_z0_ceil,
            'minScalarSumPt' : l1tGTScales.to_hw_pT_floor,
            'maxScalarSumPt' : l1tGTScales.to_hw_pT_ceil,
            'minIsolationPt' : l1tGTScales.to_hw_isolationPT_floor,
            'maxIsolationPt' : l1tGTScales.to_hw_isolationPT_ceil,
            'minAbsEta'      : l1tGTScales.to_hw_eta_floor,
            'maxAbsEta'      : l1tGTScales.to_hw_eta_ceil,
            'minRelIsolationPt'        : l1tGTScales.to_hw_relative_isolationPT_floor,
            'maxRelIsolationPt'        : l1tGTScales.to_hw_relative_isolationPT_ceil,
            'minPrimVertDz'            : l1tGTScales.to_hw_z0_floor,
            'maxPrimVertDz'            : l1tGTScales.to_hw_z0_ceil,
            'regionsAbsEtaLowerBounds' : l1tGTScales.to_hw_eta_ceil,
            'regionsMinPt'             : l1tGTScales.to_hw_pT_floor,
            'regionsMaxRelIsolationPt' : l1tGTScales.to_hw_relative_isolationPT_ceil,
            'minPtMultiplicityCut'     : l1tGTScales.to_hw_pT_floor,
            # CorrelationalCuts
            'os'           : self.booltostring,
            'ss'           : self.booltostring,
            'minCombPt'    : l1tGTScales.to_hw_PtSquared,
            'maxCombPt'    : l1tGTScales.to_hw_PtSquared,
            'minDEta'      : l1tGTScales.to_hw_eta_floor,
            'maxDEta'      : l1tGTScales.to_hw_eta_ceil,
            'minDPhi'      : l1tGTScales.to_hw_phi_floor,
            'maxDPhi'      : l1tGTScales.to_hw_phi_ceil,
            'minDz'        : l1tGTScales.to_hw_z0_floor,
            'maxDz'        : l1tGTScales.to_hw_z0_ceil,
            'minDR'        : l1tGTScales.to_hw_dRSquared_floor,
            'maxDR'        : l1tGTScales.to_hw_dRSquared_ceil,
            'minInvMass'   : l1tGTScales.to_hw_InvMassSqrDiv2,
            'maxInvMass'   : l1tGTScales.to_hw_InvMassSqrDiv2,
            'minTransMass' : l1tGTScales.to_hw_TransMassSqrDiv2,
            'maxTransMass' : l1tGTScales.to_hw_TransMassSqrDiv2,
            'minInvMassOverDR'     : l1tGTScales.to_hw_InvMassSqrOver2DR,
            'maxInvMassOverDR'     : l1tGTScales.to_hw_InvMassSqrOver2DR,
            # 3BodyCuts
            'minInvMass'    : l1tGTScales.to_hw_InvMassSqrDiv2,
            'maxInvMass'    : l1tGTScales.to_hw_InvMassSqrDiv2,
            'minTransMass'  : l1tGTScales.to_hw_TransMassSqrDiv2,
            'maxTransMass'  : l1tGTScales.to_hw_TransMassSqrDiv2,

            # the following are included here as a confirmation of inclusion to the VHDL Writter
            # 'primVertex'          :   # returned as is
            # 'regionsQualityFlags' :   # returned as is
            # 'minPtMultiplicityN'  :   # returned as is
            # 'minQualityScore'     :   # returned as is
            # 'maxQualityScore'     :   # returned as is
            # 'minQualityScoreSum'  :   # returned as is
            # 'maxQualityScoreSum'  :   # returned as is
            # 'qualityFlags'        :   # returned as is
        }

        self._cut_aliases = {
        }
        self._3bodycut_aliases = {
        }


    def booltostring(self,x):
        if x == True:
            return True
        else: 
            return False

    def addResources(self,knowncut):
        for k in list(self.ResourcesperCut.keys()):
            if knowncut in k:
                if k in self.ResourcesperCut.keys():
                    self.ResourceUseage.addCutResources(self.ResourcesperCut.pop(k))

    def _setInputObject(self,condition,value):
        self.InputObjects[condition] = value

    def setCut(self, key, physvalue, is_3body=False, collection="", numberofparameters=0):
        """
        Sets a cut value, ensuring the correct type propagation for hardware (hwcut) 
        and physics (physcut) values.
        """
        needs_conversion = key in self._HWConversionFunctions
        if isinstance(physvalue, list):
            if needs_conversion:
                hwvalue = [self._HWConversionFunctions[key](v) for v in physvalue]
            else:
                hwvalue = physvalue  # No conversion needed
        else:
            hwvalue = self._HWConversionFunctions[key](physvalue) if needs_conversion else physvalue
        if collection != "":
            if self.getHWCut(key, "", is_3body) not in self.Cuts.keys():
                cut = _Cut()
                cut.setNumberofvalues(numberofparameters, physvalue, hwvalue)  
                if needs_conversion and key in ['ss', 'os']: 
                    cut.setforBooleanCut(numberofparameters)
                cut.setCutat(hwvalue, physvalue, collection)
                self.Cuts[self.getHWCut(key, "", is_3body)] = cut
            else:
                self.Cuts[self.getHWCut(key, "", is_3body)].setCutat(hwvalue, physvalue, collection)
        else:
            cut = _Cut()
            cut.setNumberofvalues(numberofparameters, physvalue, hwvalue) 
            cut.setCut(hwvalue, physvalue)
            self.Cuts[self.getHWCut(key, "", is_3body)] = cut

    def setName(self,name):
        self.Name = name
    def addPath(self,path):
        self.Paths.append(path)

    def getHWCut(self, cut, collection = "", is_3body=False):
        if cut in self._cut_aliases and is_3body==False:
            return self._cut_aliases[cut].format(collection)
        elif cut in self._3bodycut_aliases and is_3body==True:
            return self._3bodycut_aliases[cut].format(collection)
        return cut

    def getCollections(self, object):
        return {}

    def setInputObjects(self, **inobjs):
        for name, value in inobjs.items():
            if name in self._InputTags:
                self.InputObjects[name] = value
    def _setHWConversionFunctions(self,indict):
           self._HWConversionFunctions = indict

class DoubleObjCond(Condition):
    """
    Class for the L1GTDoubleObjectCond 
    """
    Label = "L1GTDoubleObjectCond"
    Template = "double.template"
    NumberOfCollections = 2 
    NumberOfCorrelations = 2
    # NumberOfCorrelations = 1
    NumberOf3BodyCorrelations = 0
    def __init__(self):
        Condition.__init__(self)

        self._cut_aliases.update({ 
            'minPt'  : 'minPT_cuts',
            'maxPt'  : 'maxPT_cuts',
            'minEta' : 'minEta_cuts',
            'maxEta' : 'maxEta_cuts',
            'minPhi' : 'minPhi_cuts',
            'maxPhi' : 'maxPhi_cuts',
            'minZ0'  : 'minZ0_cuts',
            'maxZ0'  : 'maxZ0_cuts',
            'minScalarSumPt'    : 'minScalarSumPT_cuts',
            'maxScalarSumPt'    : 'maxScalarSumPT_cuts',
            'minQualityScore'   : 'minQualityScore_cuts',
            'maxQualityScore'   : 'maxQualityScore_cuts',
            'minQualityScoreSum': 'minQualityScoreSum_cut',
            'maxQualityScoreSum': 'maxQualityScoreSum_cut',
            'qualityFlags'      : 'qualityFlags_cuts',
            'minIsolationPt'    : 'minIsolationPT_cuts',
            'maxIsolationPt'    : 'maxIsolationPT_cuts',
            'minAbsEta'         : 'minAbsEta_cuts',
            'maxAbsEta'         : 'maxAbsEta_cuts',
            'minRelIsolationPt' : 'minRelIsolationPT_cuts',
            'maxRelIsolationPt' : 'maxRelIsolationPT_cuts',
            'primVertex'        : 'primVertIdcs',
            'minPrimVertDz'     : 'minPrimVertDz_cuts',
            'maxPrimVertDz'     : 'maxPrimVertDz_cuts',
            'regionsAbsEtaLowerBounds' : 'regionsAbsEtaLowerBounds',
            'regionsMinPt'             : 'regionsMinPt_cuts',
            'regionsMaxRelIsolationPt' : 'regionsMaxRelIsolationPT_cuts',
            'regionsQualityFlags'      : 'regionsQualityFlags_cuts',
            'minPtMultiplicityN'       : 'minPtMultiplicityNs',
            'minPtMultiplicityCut'     : 'minPtMultiplicity_cuts',
            'os'           : 'os_cut',
            'ss'           : 'ss_cut',
            'minCombPt'    : 'minPTSqr_cut',
            'maxCombPt'    : 'maxPTSqr_cut',
            'minDEta'      : 'minDEta_cut',
            'maxDEta'      : 'maxDEta_cut',
            'minDPhi'      : 'minDPhi_cut',
            'maxDPhi'      : 'maxDPhi_cut',
            'minDz'        : 'minDZ_cut',
            'maxDz'        : 'maxDZ_cut',
            'minDR'        : 'minDRSquared_cut',
            'maxDR'        : 'maxDRSquared_cut',
            'minInvMass'   : 'minInvMassSqrDiv2_cut',
            'maxInvMass'   : 'maxInvMassSqrDiv2_cut',
            'minTransMass' : 'minTransMassSqrDiv2_cut',
            'maxTransMass' : 'maxTransMassSqrDiv2_cut',
            'minInvMassOverDR' : 'minInvMassSqrOver2DRSqr_cut',
            'maxInvMassOverDR' : 'maxInvMassSqrOver2DRSqr_cut'
        })
        self.ResourcesperCut.update({
            ('minDEta','maxDEta') : CutResources(bram = 0 , dsp = 0, lut = 800),
            ('minDPhi','maxDPhi') : CutResources(bram = 0 , dsp = 0, lut = 800),
            ('minDR','maxDR') : CutResources(bram = 0 , dsp = 24, lut = 1800),
            ('minInvMass','maxInvMass') : CutResources(bram = 24 , dsp = 36, lut = 2000),
            ('minTransMass','maxTransMass') : CutResources(bram = 24 , dsp = 36, lut = 2000)
        })


    def getCollections(self, object):
        collections = {1: object.getParameter('collection1'), 2: object.getParameter('collection2')}
        for col in collections.values():
            self._InputTags += [col.getParameter("tag")]
        return collections

class SingleObjCond(Condition):
    """
    Class for the L1GTSingleObjectCond 
    """
    def __init__(self):
        Condition.__init__(self)

        self._cut_aliases.update({ 
            'minPt'  : 'minPT_cut',
            'maxPt'  : 'maxPT_cut',
            'minEta' : 'minEta_cut',
            'maxEta' : 'maxEta_cut',
            'minPhi' : 'minPhi_cut',
            'maxPhi' : 'maxPhi_cut',
            'minZ0'  : 'minZ0_cut',
            'maxZ0'  : 'maxZ0_cut',
            # 'qual'   : 'qual_cut',
            # 'iso'    : 'iso_cut',
            # 'non existent' : 'minDz_cut',
            # 'non existent' : 'maxDz_cut',
            'minScalarSumPt'    : 'minScalarSumPT_cut',
            'maxScalarSumPt'    : 'maxScalarSumPT_cut',
            'minQualityScore'   : 'minQualityScore_cut',
            'maxQualityScore'   : 'maxQualityScore_cut',
            'minQualityScoreSum': 'minQualityScoreSum_cut',
            'maxQualityScoreSum': 'maxQualityScoreSum_cut',
            'qualityFlags'      : 'qualityFlags_cut',
            'minIsolationPt'    : 'minIsolationPT_cut',
            'maxIsolationPt'    : 'maxIsolationPT_cut',
            'minAbsEta'         : 'minAbsEta_cut',
            'maxAbsEta'         : 'maxAbsEta_cut',
            'minRelIsolationPt' : 'minRelIsolationPT_cut',
            'maxRelIsolationPt' : 'maxRelIsolationPT_cut',
            'primVertex'        : 'primVertIdx',
            'minPrimVertDz'     : 'minPrimVertDz_cut',
            'maxPrimVertDz'     : 'maxPrimVertDz_cut',
            'regionsMinPt'      : 'regionsMinPt_cut',
            'regionsAbsEtaLowerBounds' : 'regionsAbsEtaLowerBounds',
            'regionsMaxRelIsolationPt' : 'regionsMaxRelIsolationPT_cut',
            'regionsQualityFlags'      : 'regionsQualityFlags_cut',
            'minPtMultiplicityN'       : 'minPtMultiplicityN',
            'minPtMultiplicityCut'     : 'minPtMultiplicity_cut',
        })
    Label = "L1GTSingleObjectCond"
    Template = "single.template"


    def getCollections(self, object):
        self._InputTags += [object.getParameter("tag")]
        return {}

class QuadObjCond(Condition):
    """
    Class for the L1GTQuadObjectCond 
    """
    def __init__(self):
        Condition.__init__(self)

        self._cut_aliases.update({
            'minPt'  : 'minPT_cuts',
            'maxPt'  : 'maxPT_cuts',
            'minEta' : 'minEta_cuts',
            'maxEta' : 'maxEta_cuts',
            'minPhi' : 'minPhi_cuts',
            'maxPhi' : 'maxPhi_cuts',
            'minZ0'  : 'minZ0_cuts',
            'maxZ0'  : 'maxZ0_cuts',
            'minScalarSumPt'    : 'minScalarSumPT_cuts',
            'maxScalarSumPt'    : 'maxScalarSumPT_cuts',
            'minQualityScore'   : 'minQualityScore_cuts',
            'maxQualityScore'   : 'maxQualityScore_cuts',
            'minQualityScoreSum': 'minQualityScoreSum_cut',
            'maxQualityScoreSum': 'maxQualityScoreSum_cut',
            'qualityFlags'      : 'qualityFlags_cuts',
            'minIsolationPt'    : 'minIsolationPT_cuts',
            'maxIsolationPt'    : 'maxIsolationPT_cuts',
            'minAbsEta'         : 'minAbsEta_cuts',
            'maxAbsEta'         : 'maxAbsEta_cuts',
            'minRelIsolationPt' : 'minRelIsolationPT_cuts',
            'maxRelIsolationPt' : 'maxRelIsolationPT_cuts',
            'primVertex'        : 'primVertIdcs',
            'minPrimVertDz'     : 'minPrimVertDz_cuts',
            'maxPrimVertDz'     : 'maxPrimVertDz_cuts',
            'regionsAbsEtaLowerBounds' : 'regionsAbsEtaLowerBounds',
            'regionsMinPt'             : 'regionsMinPt_cuts',
            'regionsMaxRelIsolationPt' : 'regionsMaxRelIsolationPT_cuts',
            'regionsQualityFlags'      : 'regionsQualityFlags_cuts',
            'minPtMultiplicityN'       : 'minPtMultiplicityNs',
            'minPtMultiplicityCut'     : 'minPtMultiplicity_cuts',
            'os'           : 'os_cuts',
            'ss'           : 'ss_cuts',
            'minCombPt'    : 'minPTSqr_cuts',
            'maxCombPt'    : 'maxPTSqr_cuts',
            'minDEta'      : 'minDEta_cuts',
            'maxDEta'      : 'maxDEta_cuts',
            'minDPhi'      : 'minDPhi_cuts',
            'maxDPhi'      : 'maxDPhi_cuts',
            'minDz'        : 'minDZ_cuts',
            'maxDz'        : 'maxDZ_cuts',
            'minDR'        : 'minDRSquared_cuts',
            'maxDR'        : 'maxDRSquared_cuts',
            'minInvMass'   : 'minInvMassSqrDiv2_cuts',
            'maxInvMass'   : 'maxInvMassSqrDiv2_cuts',
            'minTransMass' : 'minTransMassSqrDiv2_cuts',
            'maxTransMass' : 'maxTransMassSqrDiv2_cuts',
            'minInvMassOverDR'    : 'minInvMassSqrOver2DRSqr_cuts',
            'maxInvMassOverDR'    : 'maxInvMassSqrOver2DRSqr_cuts',
        })
        self._3bodycut_aliases.update({
            'minInvMass'   : 'min3BodyInvMassSqrDiv2_cuts',
            'maxInvMass'   : 'max3BodyInvMassSqrDiv2_cuts',
            'minTransMass' : 'min3BodyTransMassSqrDiv2_cuts',
            'maxTransMass' : 'max3BodyTransMassSqrDiv2_cuts',
        })


    Label = "L1GTQuadObjectCond"
    Template = "quad.template"
    NumberOfCollections = 4
    NumberOfCorrelations = 6
    NumberOf3BodyCorrelations = 4
    def getCollections(self, object):
        collections = {1: object.getParameter('collection1'), 2: object.getParameter('collection2'),3: object.getParameter('collection3'),4: object.getParameter('collection4')}
        for col in collections.values():
            self._InputTags += [col.getParameter("tag")]
        return collections


    # def getCollections(self, object):
    #     collections = {1: object.getParameter('collection1'), 2: object.getParameter('collection2'),3: object.getParameter('collection3'),4: object.getParameter('collection4')}
    #     for col in collections.values():
    #         self._InputTags += [col.getParameter("tag")]
    #     return collections
    
    def getCorrelations(self, object):
        correlations = { 1: object.getParameter('correl12'), 2: object.getParameter('correl13'), 3 : object.getParameter('correl23'),4: object.getParameter('correl14'), 5: object.getParameter('correl24'), 6 : object.getParameter('correl34')}
        return correlations

    def get3BodyCorrelations(self, object):
        correlations = { 1: object.getParameter('correl123'), 2: object.getParameter('correl124'), 3 : object.getParameter('correl134'),4: object.getParameter('correl234')}
        return correlations

class TripleObjCond(Condition):
    """
    Class for the L1GTTripleObjectCond 
    """
    Label = "L1GTTripleObjectCond"
    Template = "triple.template"
    NumberOfCollections = 3
    NumberOfCorrelations = 3
    NumberOf3BodyCorrelations = 1

    def __init__(self):
        Condition.__init__(self)
        
        
        self._cut_aliases.update({ 
            'minPt'  : 'minPT_cuts',
            'maxPt'  : 'maxPT_cuts',
            'minEta' : 'minEta_cuts',
            'maxEta' : 'maxEta_cuts',
            'minPhi' : 'minPhi_cuts',
            'maxPhi' : 'maxPhi_cuts',
            'minZ0'  : 'minZ0_cuts',
            'maxZ0'  : 'maxZ0_cuts',
            'minScalarSumPt'    : 'minScalarSumPT_cuts',
            'maxScalarSumPt'    : 'maxScalarSumPT_cuts',
            'minQualityScore'   : 'minQualityScore_cuts',
            'maxQualityScore'   : 'maxQualityScore_cuts',
            'minQualityScoreSum': 'minQualityScoreSum_cut',
            'maxQualityScoreSum': 'maxQualityScoreSum_cut',
            'qualityFlags'      : 'qualityFlags_cuts',
            'minIsolationPt'    : 'minIsolationPT_cuts',
            'maxIsolationPt'    : 'maxIsolationPT_cuts',
            'minAbsEta'         : 'minAbsEta_cuts',
            'maxAbsEta'         : 'maxAbsEta_cuts',
            'minRelIsolationPt' : 'minRelIsolationPT_cuts',
            'maxRelIsolationPt' : 'maxRelIsolationPT_cuts',
            'primVertex'        : 'primVertIdcs',
            'minPrimVertDz'     : 'minPrimVertDz_cuts',
            'maxPrimVertDz'     : 'maxPrimVertDz_cuts',
            'regionsAbsEtaLowerBounds' : 'regionsAbsEtaLowerBounds',
            'regionsMinPt'             : 'regionsMinPt_cuts',
            'regionsMaxRelIsolationPt' : 'regionsMaxRelIsolationPT_cuts',
            'regionsQualityFlags'      : 'regionsQualityFlags_cuts',
            'minPtMultiplicityN'       : 'minPtMultiplicityNs',
            'minPtMultiplicityCut'     : 'minPtMultiplicity_cuts',
            'os'           : 'os_cuts',
            'ss'           : 'ss_cuts',
            'minCombPt'    : 'minPTSqr_cuts',
            'maxCombPt'    : 'maxPTSqr_cuts',
            'minDEta'      : 'minDEta_cuts',
            'maxDEta'      : 'maxDEta_cuts',
            'minDPhi'      : 'minDPhi_cuts',
            'maxDPhi'      : 'maxDPhi_cuts',
            'minDz'        : 'minDZ_cuts',
            'maxDz'        : 'maxDZ_cuts',
            'minDR'        : 'minDRSquared_cuts',
            'maxDR'        : 'maxDRSquared_cuts',
            'minInvMass'   : 'minInvMassSqrDiv2_cuts',
            'maxInvMass'   : 'maxInvMassSqrDiv2_cuts',
            'minTransMass' : 'minTransMassSqrDiv2_cuts',
            'maxTransMass' : 'maxTransMassSqrDiv2_cuts',
            'minInvMassOverDR'    : 'minInvMassSqrOver2DRSqr_cuts',
            'maxInvMassOverDR'    : 'maxInvMassSqrOver2DRSqr_cuts',
        })
        self._3bodycut_aliases.update({
            'minInvMass'   : 'min3BodyInvMassSqrDiv2_cut',
            'maxInvMass'   : 'max3BodyInvMassSqrDiv2_cut',
            'minTransMass' : 'min3BodyTransMassSqrDiv2_cut',
            'maxTransMass' : 'max3BodyTransMassSqrDiv2_cut',
        })

        self.ResourcesperCut.update({
            ('minDEta','maxDEta') : CutResources(bram = 0 , dsp = 0, lut = 800),
            ('minDPhi','maxDPhi') : CutResources(bram = 0 , dsp = 0, lut = 800),
            ('minDR','maxDR') : CutResources(bram = 0 , dsp = 24, lut = 1800),
            ('minInvMass','maxInvMass') : CutResources(bram = 24 , dsp = 36, lut = 2000),
            ('minTransMass','maxTransMass') : CutResources(bram = 24 , dsp = 36, lut = 2000)
        })


    def getCollections(self, object):
        collections = {1: object.getParameter('collection1'), 2: object.getParameter('collection2'),3: object.getParameter('collection3')}
        for col in collections.values():
            self._InputTags += [col.getParameter("tag")]
        return collections
    
    def getCorrelations(self, object):
        correlations = { 1: object.getParameter('correl12'), 2: object.getParameter('correl13'), 3 : object.getParameter('correl23')}
        return correlations

class CutResources:
    def __init__(self,bram = 0,dsp = 0,lut = 0):
        self.bram = bram
        self.dsp = dsp
        self.lut = lut
    def addCutResources(self,cutResources):
        self.bram = self.bram + cutResources.bram
        self.dsp = self.dsp + cutResources.dsp
        self.lut = self.lut + cutResources.lut
    def printResources(self):
        print("bram:{}".format(self.bram))
        print("dsp:{}".format(self.dsp))
        print("lut:{}".format(self.lut))
        return 0

class DefineAlgoBits:
    def __init__(self):
        self.Assignment = {}
    def SetBit(self,Name,Algobit):
        self.Assignment[Name] = Algobit
    
class _Cut:
    def __init__(self):
        self.hwcut = []
        self.physcut = []
        self.enablecut = []
    def setCut(self,hwcut,physcut):
        self.hwcut.append(hwcut)
        self.physcut.append(physcut)
        self.enablecut.append(True)        
 
    def setNumberofvalues(self, numparam, physvalue, hwvalue):  
        """
        Ensures that self.hwcut and self.physcut match the types of hwvalue and physvalue respectively.
        Handles lists, booleans, and single values correctly. Mode can be either "phys" or "hw" in order 
        to facilitate the (others => 0) for hwvalue or list of zeros for physvalue. Jinja template replaces
        the quotes for others.
        """
        # Initialize default values based on input type
        def get_default(v, mode):
            if isinstance(v, bool):
                return False
            elif isinstance(v, float):
                return 0.0
            elif isinstance(v, list) and mode == "hw":
                return '(others => 0)' if v else []
            elif isinstance(v, list) and mode == "phys":
                return [get_default(v[0], "phys")] * len(v) if v else []
            else:
                return 0  # Default to int
        self.hwcut = [get_default(hwvalue, "hw")] * numparam
        self.physcut = [get_default(physvalue, "phys")] * numparam
        self.enablecut = [False] * numparam  # Enable cut flags (always boolean)

    def setforBooleanCut(self,value):
        self.hwcut = [False] * (value)
    def setCutat(self, hwcut, physcut, position):
        self.hwcut[position - 1] = hwcut
        self.physcut[position - 1] = physcut
        self.enablecut[position - 1] = True
        
    def __str__(self) -> str:
        pass

class LogicalFilter:
    def __init__(self,pathname,expression,modulenames):
        self.pathname = pathname 
        self.expression = expression
        self.modulenames = modulenames

class AlgorithmBlock:
    """
    Class that groups the algorithms in a way that all codependent conditions are grouped   
    """
    def __init__(self):
        self.ResourceUseage = CutResources(0,0,0)
        self.Modules = set()
        self.Paths  = set()
        self.Collections = set()
        self.LogicalPath = set()

    def addlogical(self,paths,modules):
        self.Modules.update(modules.modulenames)
        self.LogicalPath.add(paths)
    def checklogical(self,modules):
        """
        checks if a module in a logical combination is already present in modules
        """
        if(self.Modules.intersection(modules.modulenames) == set()):
            return 0
        else:
            return 1
    def Combineblocks(self,algoblock):
        self.ResourceUseage.addCutResources(algoblock.ResourceUseage) 
        self.Modules.update(algoblock.Modules) 
        self.Paths.update(algoblock.Paths)  
        self.LogicalPath.update(algoblock.LogicalPath)
        self.Collections.update(set(algoblock.Collections))

    def addCondition(self,knownfilterkey,knownfiltervalue):
        self.Modules.add(knownfilterkey)
        self.Paths.update(knownfiltervalue.Paths)
        self.ResourceUseage.addCutResources(knownfiltervalue.ResourceUseage)
        self.Collections.update(set(knownfiltervalue.InputObjects.values()))
    def checkCondition(self,knownfilterkey):
        """
        checks if module is already present in modules, needed to combine logical filters and conditions
        """
        if  knownfilterkey in self.Modules:
            return 1
        else:
            return 0 

class Algorithmsdict:
    def __init__(self):
        self.algoblocks = []

    def addLogicalFilters(self,logicalcombinations):
        for key, value in logicalcombinations.items():
            for algoblock in self.algoblocks:
                # if algoblock.checklogical(key, value):
                if algoblock.checklogical(value):
                    break
            else:
                newblock  = AlgorithmBlock()
                newblock.addlogical(key, value)
                self.algoblocks.append(newblock)
    def addConditions(self,conditions):
        for key in conditions.keys():
            for algoblock in self.algoblocks:
                if algoblock.checkCondition(key) == 1:
                    algoblock.addCondition(key,conditions[key])
                    break
            else:
                newblock  = AlgorithmBlock()
                newblock.addCondition(key,conditions[key])
                self.algoblocks.append(newblock)

    def popMaxalgoblock(self):

        if self.algoblocks == []:
            return 0
        else:
           brammax = max(item.ResourceUseage.bram for item in self.algoblocks)

           if brammax!=0 :
                for item, value in enumerate(self.algoblocks):
                    if value.ResourceUseage.bram == brammax:
                        return self.algoblocks.pop(item)

           dspmax = max(item.ResourceUseage.dsp for item in self.algoblocks)
           if dspmax!=0 :
                for item, value in enumerate(self.algoblocks):
                    if value.ResourceUseage.dsp == dspmax:
                        return self.algoblocks.pop(item)
           lutmax = max(item.ResourceUseage.lut for item in self.algoblocks)
           for item, value in enumerate(self.algoblocks):
                if value.ResourceUseage.lut == lutmax:
                    return self.algoblocks.pop(item)