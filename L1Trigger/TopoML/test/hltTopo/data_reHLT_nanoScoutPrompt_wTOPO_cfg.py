# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: myNano --conditions 151X_dataRun3_HLT_v1 --era Run3_2025 -s HLT:GRun,NANO:@ScoutMonitor --datatier NANOAOD --eventcontent NANOAOD --data --scenario pp --process reHLT --customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run3 -n 100 --filein file:/eos/cms/store/data/Run2025G/EphemeralHLTPhysics0/RAW/v1/000/398/183/00000/029d80cb-ade3-472d-8085-4a4d955b3882.root --fileout file:nanoScout_reHLT_data.root --python_filename=data_reHLT_nanoScoutPrompt_cfg.py

import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run3_2025_cff import Run3_2025

process = cms.Process('reHLT',Run3_2025)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
# process.load('HLTrigger.Configuration.HLT_GRun_cff')
process.load('HLTrigger.Configuration.HLT_Mu12HT1b_cff')
process.load('PhysicsTools.NanoAOD.custom_run3scouting_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1),
    output = cms.optional.untracked.allowed(cms.int32,cms.PSet)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        # '/store/mc/Run3Winter25Digi/GluGlutoHHto2B2WtoLNu2Q_Par-c2-0-kl-1-kt-1_TuneCP5_13p6TeV_powheg-pythia8/GEN-SIM-RAW/142X_mcRun3_2025_realistic_v7-v2/140000/04c25b22-2076-4473-8a3b-e156bcab8dc7.root',
        # 'file:/eos/cms/store/data/Run2025G/EphemeralHLTPhysics0/RAW/v1/000/398/183/00000/029d80cb-ade3-472d-8085-4a4d955b3882.root'
        # 'file:/eos/cms/store/data/Run2025G/Muon0/RAW/v1/000/397/954/00000/0f819bfe-edde-4f0c-9ee1-64cbe1c608d4.root',
        # 'file:/eos/cms/store/data/Run2025G/ParkingSingleMuon0/RAW/v1/000/397/954/00000/0cb2bd3c-e745-4f58-bb26-0516d7bb4592.root',
        'file:/eos/cms/store/data/Run2025G/ScoutingPFMonitor/RAW/v1/000/398/012/00000/38acea35-20a6-461c-835a-800abdb0a462.root',
        ),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
    TryToContinue = cms.untracked.vstring(),
    # TryToContinue = cms.untracked.vstring('ProductNotFound'),
    accelerators = cms.untracked.vstring('*'),
    allowUnscheduled = cms.obsolete.untracked.bool,
    canDeleteEarly = cms.untracked.vstring(),
    deleteNonConsumedUnscheduledModules = cms.untracked.bool(True),
    dumpOptions = cms.untracked.bool(False),
    emptyRunLumiMode = cms.obsolete.untracked.string,
    eventSetup = cms.untracked.PSet(
        forceNumberOfConcurrentIOVs = cms.untracked.PSet(
            allowAnyLabel_=cms.required.untracked.uint32
        ),
        numberOfConcurrentIOVs = cms.untracked.uint32(0)
    ),
    fileMode = cms.untracked.string('FULLMERGE'),
    forceEventSetupCacheClearOnNewRun = cms.untracked.bool(False),
    holdsReferencesToDeleteEarly = cms.untracked.VPSet(),
    makeTriggerResults = cms.obsolete.untracked.bool,
    modulesToCallForTryToContinue = cms.untracked.vstring(),
    modulesToIgnoreForDeleteEarly = cms.untracked.vstring(),
    numberOfConcurrentLuminosityBlocks = cms.untracked.uint32(0),
    numberOfConcurrentRuns = cms.untracked.uint32(1),
    numberOfStreams = cms.untracked.uint32(0),
    numberOfThreads = cms.untracked.uint32(1),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(True)
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('myNano nevts:100'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.NANOAODoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAOD'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('file:nanoScout_reHLT_data.root'),
    outputCommands = process.NANOAODEventContent.outputCommands,

    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring("hltMu12HT1501bFilter")
    ),
)

# Additional output definition

# Other statements
from HLTrigger.Configuration.CustomConfigs import ProcessName
process = ProcessName(process)

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '151X_dataRun3_HLT_v1', '')

# Path and EndPath definitions
process.path = cms.Path(
    process.hltPFJetForBtagSelector
)
process.nanoAOD_step = cms.Path(process.scoutingNanoSequence)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)

# Schedule definition
# process.schedule imported from cff in HLTrigger.Configuration
process.schedule.extend([process.nanoAOD_step,process.endjob_step,process.NANOAODoutput_step])
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from Configuration.DataProcessing.RecoTLR
from Configuration.DataProcessing.RecoTLR import customisePostEra_Run3 

#call to customisation function customisePostEra_Run3 imported from Configuration.DataProcessing.RecoTLR
process = customisePostEra_Run3(process)

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.custom_run3scouting_cff
from PhysicsTools.NanoAOD.custom_run3scouting_cff import customiseScoutingNano,customiseScoutingNanoForScoutingPFMonitor 

#call to customisation function customiseScoutingNano imported from PhysicsTools.NanoAOD.custom_run3scouting_cff
process = customiseScoutingNano(process)

#call to customisation function customiseScoutingNanoForScoutingPFMonitor imported from PhysicsTools.NanoAOD.custom_run3scouting_cff
process = customiseScoutingNanoForScoutingPFMonitor(process)

# End of customisation functions


# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion

### Make my path

## taking Mu12+HT+1btag as example
# HLT_Mu12_IsoVVL_PFHT150_PNetBTag0p53_v7 = cms.Path(
# 	process.HLTBeginSequence +
# 	process.hltL1sMu12HTT150er +
# 	process.hltPreMu12IsoVVLPFHT150PNetBTag0p53 +
# 	cms.ignore(
# 	process.hltL1sSingleMuOpenObjectMap
# ) +
# 	process.HLTAK4CaloJetsSequence +
# 	process.hltHtMhtJet30 +
# 	process.hltHT100Jet30 +
# 	process.hltL1fL1sSingleMuOpenCandidateL1Filtered0 +
# 	process.HLTL2muonrecoSequence +
# 	cms.ignore(
# 	process.hltL2fL1sSingleMuOpenCandidateL1f0L2Filtered0Q
# ) +
# 	process.HLTL3muonrecoSequence +
# 	cms.ignore(
# 	process.hltL1fForIterL3L1fL1sSingleMuOpenCandidateL1Filtered0
# ) +
# 	process.hltL3fL1sSingleMuOpenCandidateL1f0L2f3QL3Filtered12Q +
# 	process.HLTMu12IsoVVLSequence +
# 	process.hltL3crIsoL1sMu12L1f0L2f3QL3f12QL3trkIsoFilteredVVL +
# 	process.HLTAK4PFJetsSequence +
# 	process.hltPFHTJet30 +
# 	process.hltPFHT150Jet30 +
# 	process.HLTJetFlavourTagParticleNetSequencePF +
# 	process.hltBTagPFPNet0p53Single +
# 	process.HLTEndSequence
# )

from L1Trigger.TopoML.l1tTopoBDTProducer_cff import l1tTopoBDTProducer

process.l1tTopoBDTProducerHH1muMuHT  = l1tTopoBDTProducer.clone(
    model_path = cms.FileInPath("L1Trigger/TopoML/data/winter25/HH2b2W1L/Jan26_L1_conif_model_HH2b2W1L_1mu_Mu0_pt-qual_HT.json"),
    # debug = cms.bool(True),
)

## BDT score to probability mapping (logit function):
# prob = 1 / (1 + exp(-score))
# score = -log(1/prob - 1)
# 0.1 -2.1972245773362196
# 0.2 -1.3862943611198906
# 0.3 -0.8472978603872034
# 0.4 -0.4054651081081644
# 0.5 0.0
# 0.6 0.4054651081081642
# 0.7 0.8472978603872034
# 0.8 1.3862943611198908
# 0.9 2.1972245773362196 

# import numpy as np
# for thr in np.arange(0.1,1.0,0.1):
#     score_thr = -1.0 * np.log(1.0/thr - 1.0)
#     # print(f"prob {thr:.1f} -> score {score_thr:.6f}")

#     print(f"Adding filter for BDT score > {score_thr:.3f} (prob>{thr:.1f})")
#     print(f'hltL1TopoBDTHH1Mu{str(thr)[:3].replace(".", "p")}')

#     process.__setattr__(f'hltL1TopoBDTHH1Mu{str(thr)[:3].replace(".", "p")}', cms.EDFilter("HLTFloatThresholdFilter",
#         src = cms.InputTag("l1tTopoBDTProducerHH1muMuHT","score"),
#         threshold = cms.double(score_thr),
#         greaterThan = cms.bool(True),
#     ))

# exit()

# ## filter for the L1 BDT score
process.hltL1TopoBDTHH1Mu1p35 = cms.EDFilter("HLTFloatThresholdFilter",
    src = cms.InputTag("l1tTopoBDTProducerHH1muMuHT","score"),
    threshold = cms.double(1.35),  # 0.8 prob score
    greaterThan = cms.bool(True),
)

## HLT TOPO

## copied from the scouting pf sequence
process.HLTMuIsolationSequence = cms.Sequence( 
    process.HLTL3muonEcalPFisorecoSequenceNoBoolsForMuons + 
    process.HLTL3muonHcalPFisorecoSequenceNoBoolsForMuons + 
    process.HLTTrackReconstructionForIsoL3MuonIter02 + 
    # process.hltMuonTkRelIsolationCut0p14Map 
    process.hltMuonTkRelIsolationCut0p3Map
    )

from L1Trigger.TopoML.hltTopoBDTProducer_cff import hltTopoMuonBDTProducer

process.hltTopoMuonHTBDTProducer = hltTopoMuonBDTProducer.clone(
    modelPath = cms.string("L1Trigger/TopoML/data/Jan26_HLT_conif_model_HH2b2W1L_1mu_L1MuTOPOMuHT_Mu_pt-iso.json"),
    l1tTopoScore = cms.InputTag("l1tTopoBDTProducerHH1muMuHT", "score"),
    TrackIsoMap = cms.InputTag("hltMuonTkRelIsolationCut0p3Map", "combinedRelativeIsoDeposits"), # from Mu12Isolation sequence
    #TrackIsoMap = cms.InputTag("hltMuonTkRelIsolationCut0p14Map", "combinedRelativeIsoDeposits"), # from scouting MuonIsolation sequence
    debug = cms.bool(True),
)

# ## filter for the HLT BDT score
process.hltTopoBDTHH1MuProb0p8 = cms.EDFilter("HLTFloatThresholdFilter",
    src = cms.InputTag("hltTopoMuonHTBDTProducer","score"),
    threshold = cms.double(1.35),  # 0.8 prob score
    greaterThan = cms.bool(True),
)

process.hltTopoBDTHH1MuProb0p9 = cms.EDFilter("HLTFloatThresholdFilter",
    src = cms.InputTag("hltTopoMuonHTBDTProducer","score"),
    threshold = cms.double(2.19),  # 0.9 prob score
    greaterThan = cms.bool(True),
)

## model with PNet
from L1Trigger.TopoML.hltTopoBDTProducer_cff import hltTopoMuonHTPNetBXGBProducer

process.hltTopoMuonHTPNetBXGBProducer = hltTopoMuonHTPNetBXGBProducer.clone(
    modelPath = cms.string("L1Trigger/TopoML/data/HLT_xgb_model_HH2b2W1L_1mu_HLTHT_Mu_pt-iso_PNetB.json"),
    # l1tTopoScore = cms.InputTag("l1tTopoBDTProducerHH1muMuHT", "score"),
    TrackIsoMap = cms.InputTag("hltMuonTkRelIsolationCut0p3Map", "combinedRelativeIsoDeposits"), # from Mu12Isolation sequence
    #TrackIsoMap = cms.InputTag("hltMuonTkRelIsolationCut0p14Map", "combinedRelativeIsoDeposits"), # from scouting MuonIsolation sequence
    debug = cms.bool(True),
)

process.hltTopoBDTHH1MuHTBProb0p5 = cms.EDFilter("HLTFloatThresholdFilter",
    src = cms.InputTag("hltTopoMuonHTPNetBXGBProducer","score"),
    threshold = cms.double(0.5 ),  # XGB gives probability directly, 
    greaterThan = cms.bool(True),
)

## change hltPFJetForBtagSelector to not filter events

# process.hltPFJetForBtagSelector.MinN = cms.int32(0)

## TOPO path with producer only
process.HLT_TopoHH1Mu_NoFilter = cms.Path(
	process.HLTBeginSequence +
    process.l1tTopoBDTProducerHH1muMuHT + ## replaces L1 seed in GT for now   
	# cms.ignore(
    # 	process.hltL1sSingleMuOpenObjectMap
    # ) +
	# process.hltL1fL1sSingleMuOpenCandidateL1Filtered0 +
    process.HLTL2muonrecoSequence +
	process.HLTL3muonrecoSequence +
	# process.hltL3fL1sSingleMuOpenCandidateL1f0L2f3QL3Filtered12Q + # pt > 12 cut
	# process.HLTMu12IsoVVLSequence +
    process.HLTMuIsolationSequence +
	# process.hltL3crIsoL1sMu12L1f0L2f3QL3f12QL3trkIsoFilteredVVL +
    ## adding HLT TOPO
    process.hltTopoMuonHTBDTProducer +  
    ## add jet and btagging sequences
    process.HLTAK4PFJetsSequence +
	process.hltPFHTJet30 +
	process.HLTJetFlavourTagParticleNetSequencePF +
    ## run HLT TOPO with Mu+HT+1b
    process.hltTopoMuonHTPNetBXGBProducer +
	process.HLTEndSequence
)

## add my path to the schedule
process.schedule.append(process.HLT_TopoHH1Mu_NoFilter)


## TOPO path with filters
process.HLT_TopoHH1Mu_L1Tprob0p8_HLTprob0p9_Mu12_IsoVVL = cms.Path(
	process.HLTBeginSequence +
    process.l1tTopoBDTProducerHH1muMuHT + ## replaces L1 seed in GT for now   
    
    # # filter for different BDT score thresholds
    # process.hltL1TopoBDTHH1Mu0p2 +
    # process.hltL1TopoBDTHH1Mu0p3 +
    # process.hltL1TopoBDTHH1Mu0p4 +
    # process.hltL1TopoBDTHH1Mu0p5 +
    # process.hltL1TopoBDTHH1Mu0p6 +
    # process.hltL1TopoBDTHH1Mu0p7 +
    # process.hltL1TopoBDTHH1Mu0p8 +
    # process.hltL1TopoBDTHH1Mu0p9 +

    process.hltL1TopoBDTHH1Mu1p35 + ## equivalent to prob>0.8
    
# 	process.hltL1sMu12HTT150er +
# 	process.hltPreMu12IsoVVLPFHT150PNetBTag0p53 +
	cms.ignore(
    	process.hltL1sSingleMuOpenObjectMap
    ) +
	process.hltL1fL1sSingleMuOpenCandidateL1Filtered0 +

# 	process.HLTAK4CaloJetsSequence +
# 	process.hltHtMhtJet30 +
# 	process.hltHT100Jet30 +
	
    process.HLTL2muonrecoSequence +
    cms.ignore(
        process.hltL2fL1sSingleMuOpenCandidateL1f0L2Filtered0Q
    ) +
	process.HLTL3muonrecoSequence +
    cms.ignore(
        process.hltL1fForIterL3L1fL1sSingleMuOpenCandidateL1Filtered0
    ) +
	process.hltL3fL1sSingleMuOpenCandidateL1f0L2f3QL3Filtered12Q +
	# process.HLTMu12IsoVVLSequence +
    process.HLTMuIsolationSequence +
	# process.hltL3crIsoL1sMu12L1f0L2f3QL3f12QL3trkIsoFilteredVVL +
    ## adding HLT TOPO
    process.hltTopoMuonHTBDTProducer +   
    # process.hltTopoBDTHH1MuProb0p8 +
    # process.hltTopoBDTHH1MuProb0p9 + 


    ## add jet and btagging sequences
	process.HLTAK4PFJetsSequence +
	process.hltPFHTJet30 +
	process.hltPFHT150Jet30 + # filter only if no nanoaod score needed (otherwise product not found!)
	process.HLTJetFlavourTagParticleNetSequencePF +

    ## run HLT TOPO with Mu+HT+1b
    process.hltTopoMuonHTPNetBXGBProducer +
    process.hltTopoBDTHH1MuHTBProb0p5 + 

# 	process.hltBTagPFPNet0p53Single +
	process.HLTEndSequence
)

## add my path to the schedule
process.schedule.append(process.HLT_TopoHH1Mu_L1Tprob0p8_HLTprob0p9_Mu12_IsoVVL)

# ## add score to the nanoAOD
process.load('L1Trigger.TopoML.l1tTopoBDTNanotable_cff')
from PhysicsTools.NanoAOD.common_cff import ExtVar

process.l1tTopoBDTNanotable.variables = cms.PSet(
    # process.l1tTopoBDTNanotable.variables,
    l1tBdtScore_HH1mu_MuHT = ExtVar( cms.InputTag("l1tTopoBDTProducerHH1muMuHT","score"),"float", doc="L1 Topo BDT score (model: HH 1mu, Mu+HT)" ),
    # l1tBdtScore_HH1mu_AllFeat = ExtVar( cms.InputTag("l1tTopoBDTProducerHH1muAllFeat","score"),"float", doc="L1 Topo BDT score (model: HH 1mu, Mu+HT+EG+JET+Tau)" ),
    hltBdtScore_HH1mu_MuHT = ExtVar( cms.InputTag("hltTopoMuonHTBDTProducer","score"),"float", doc="HLT Topo BDT score (model: HH 1mu, Mu+HT)" ),
    hltBdtScore_HH1mu_MuHTPNetB = ExtVar( cms.InputTag("hltTopoMuonHTPNetBXGBProducer","score"),"float", doc="HLT Topo BDT score (model: HH 1mu, Mu+HT+PNetB)" ),
)

# add l1tTopoBDTNanotable to the scouting nano sequence and event content
process.scoutingNanoSequence.insert(-1, process.l1tTopoBDTNanotable)
# process.scoutingNanoTaskCommon.add(process.l1tTopoBDTNanotable)

# process.scoutingNanoSequence = cms.Sequence(process.l1tTopoBDTNanotable)

process.NANOAODoutput.outputCommands.append("keep nanoaodFlatTable_l1tTopoBDTNanotable_*_*")


## filter events at input

# -------------------------------------------------------------------
# HLT Trigger Filter
# -------------------------------------------------------------------
## HLT FILTER
import HLTrigger.HLTfilters.hltHighLevel_cfi
process.skimHLTFilter = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
process.skimHLTFilter.TriggerResultsTag = cms.InputTag("TriggerResults", "", "HLT") # explicity specify the process name
process.skimHLTFilter.throw=cms.bool(False) # otherwise will throw if it cant match to a hlt path, depends on whether you want to silently ignore unmatched paths

#process.skimHLTFilter.HLTPaths = cms.vstring("HLT_Mu12_IsoVVL_PFHT150_PNetBTag0p53*")  # the * allows us to match all version, you could also other wild card expressions
process.skimHLTFilter.HLTPaths = cms.vstring("HLT_IsoMu24*")  # the * allows us to match all version, you could also other wild card expressions
process.HLTskim_step = cms.Path(process.skimHLTFilter)
process.NANOAODoutput.SelectEvents = cms.untracked.PSet(SelectEvents = cms.vstring("HLTskim_step"))

# Schedule definition
process.schedule.insert(0, process.HLTskim_step)  # insert the skim step at the beginning of the schedule so it runs first

process.nanoAOD_step = cms.Path(process.skimHLTFilter*process.scoutingNanoSequence)

# insert the skim filter at the beginning of the HLT begin sequence so that it runs before any other HLT module, this way we can skip all the HLT processing for events that don't pass the skim
process.HLTBeginSequence.insert(0, process.skimHLTFilter)



### add hltJets with btagging to nano


process.HLTTauVertexSequencePF = cms.Sequence(
    process.hltVerticesPF
    + process.hltVerticesPFSelector
    + cms.ignore(process.hltVerticesPFFilter)
    + process.hltDeepInclusiveVertexFinderPF
    + process.hltDeepInclusiveSecondaryVerticesPF
)

process.HLTJetFlavourTagParticleNetSequencePFMod = cms.Sequence(
    process.hltVerticesPF
    + process.hltVerticesPFSelector
    + cms.ignore(process.hltVerticesPFFilter)
    + cms.ignore(process.hltPFJetForBtagSelector)
    + process.hltPFJetForBtag
    + process.hltDeepBLifetimeTagInfosPF
    + process.hltDeepInclusiveVertexFinderPF
    + process.hltDeepInclusiveSecondaryVerticesPF
    + process.hltDeepTrackVertexArbitratorPF
    + process.hltDeepInclusiveMergedVerticesPF
    + process.hltPrimaryVertexAssociation
    + process.hltParticleNetJetTagInfos
    + process.hltParticleNetONNXJetTags
    + process.hltParticleNetDiscriminatorsJetTags
)

# ## change defaults
# process.hltPFJetForBtagSelector.MinPt = 15
# process.hltPFJetForBtagSelector.MaxEta = 2.7
# process.hltParticleNetJetTagInfos.min_jet_pt = 15
# process.hltParticleNetJetTagInfos.max_jet_eta = 2.7

#process.scoutingNanoSequence.add(
process.nanoAOD_step = cms.Path(
    process.HLTL1UnpackerSequence
    + process.HLTBeamSpot
    # + process.HLTL2TauTagNNSequence
    # + process.HLTGlobalPFTauHPSSequence
    # + process.HLTHPSDeepTauPFTauSequenceForVBFIsoTau
    + process.HLTAK4PFJetsSequence
    + process.HLTJetFlavourTagParticleNetSequencePFMod
    # + process.HLTTauVertexSequencePF
    # + process.l1bits
    + process.scoutingNanoSequence
)


process.AK4PFJetsTable = cms.EDProducer("SimplePFJetFlatTableProducer",
    src = cms.InputTag( "hltAK4PFJetsCorrected" ),
    cut = cms.string("pt > 10"),
    name= cms.string("hltAK4Jet"),
    doc = cms.string("HLT AK4 PF Jets"),
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(False), # this is the main table
    variables = cms.PSet(
      P4Vars,
      chargedHadronEnergy = Var("chargedHadronEnergy", float, doc = "chargedHadronEnergy"),
      chargedHadronEnergyFraction = Var("chargedHadronEnergyFraction", float, doc = "chargedHadronEnergyFraction"),
      neutralHadronEnergy = Var("neutralHadronEnergy", float, doc = "neutralHadronEnergy"),
      neutralHadronEnergyFraction = Var("neutralHadronEnergyFraction", float, doc = "neutralHadronEnergyFraction"),
      photonEnergy = Var("photonEnergy", float, doc = "photonEnergy"),
      photonEnergyFraction = Var("photonEnergyFraction", float, doc = "photonEnergyFraction"),
      muonEnergy = Var("muonEnergy", float, doc = "muonEnergy"),
      muonEnergyFraction = Var("muonEnergyFraction", float, doc = "muonEnergyFraction"),
      HFHadronEnergy = Var("HFHadronEnergy", float, doc = "HFHadronEnergy"),
      HFHadronEnergyFraction = Var("HFHadronEnergyFraction", float, doc = "HFHadronEnergyFraction"),
      HFEMEnergy = Var("HFEMEnergy", float, doc = "HFEMEnergy"),
      HFEMEnergyFraction = Var("HFEMEnergyFraction", float, doc = "HFEMEnergyFraction"),
      chargedHadronMultiplicity = Var("chargedHadronMultiplicity", float, doc = "chargedHadronMultiplicity"),
      neutralHadronMultiplicity = Var("neutralHadronMultiplicity", float, doc = "neutralHadronMultiplicity"),
      photonMultiplicity = Var("photonMultiplicity", float, doc = "photonMultiplicity"),
      muonMultiplicity = Var("muonMultiplicity", float, doc = "muonMultiplicity"),
      HFHadronMultiplicity = Var("HFHadronMultiplicity", float, doc = "HFHadronMultiplicity"),
      HFEMMultiplicity = Var("HFEMMultiplicity", float, doc = "HFEMMultiplicity"),
      chargedMuEnergy = Var("chargedMuEnergy", float, doc = "chargedMuEnergy"),
      chargedMuEnergyFraction = Var("chargedMuEnergyFraction", float, doc = "chargedMuEnergyFraction"),
      neutralEmEnergy = Var("neutralEmEnergy", float, doc = "neutralEmEnergy"),
      neutralEmEnergyFraction = Var("neutralEmEnergyFraction", float, doc = "neutralEmEnergyFraction"),
      chargedMultiplicity = Var("chargedMultiplicity", float, doc = "chargedMultiplicity"),
      neutralMultiplicity = Var("neutralMultiplicity", float, doc = "neutralMultiplicity"),
      nConstituents = Var("nConstituents", int, doc = "nConstituents"),
      etaetaMoment =  Var("etaetaMoment", float, doc = " eta-eta second moment, ET weighted " ),
      phiphiMoment =  Var("phiphiMoment", float, doc = " phi-phi second moment, ET weighted " ),
      etaphiMoment =  Var("etaphiMoment", float, doc = " eta-phi second moment, ET weighted " ),
      maxDistance =  Var("maxDistance", float, doc = " maximum distance from jet to constituent " ),
      constituentPtDistribution =  Var("constituentPtDistribution", float, doc = " jet structure variables: constituentPtDistribution is the pT distribution among the jet constituents (ptDistribution = 1 if jet made by one constituent carrying all its momentum,  ptDistribution = 0 if jet made by infinite constituents carrying an infinitesimal fraction of pt) "    ),
      constituentEtaPhiSpread =  Var("constituentEtaPhiSpread", float, doc = " the rms of the eta-phi spread of the jet's constituents wrt the jet axis " ),
      jetArea =  Var("jetArea", float, doc = " get jet area " ),
    )
)

pnet_discriminator_names = ["BvsAll", "CvsAll", "CvsL", "TauhvsAll"]
pnet_score_names = ["probb","probc","probuds","probg","probtauhp","probtauhm","ptcorr"]

process.hltPFJetForBtagPAT = cms.EDProducer("PATJetProducer",
    jetSource = cms.InputTag("hltPFJetForBtag"),  # Input HLT jets
    addJetCorrFactors = cms.bool(False),  # No JEC applied
    addBTagInfo = cms.bool(True),
    discriminatorSources = cms.VInputTag(
        # cms.InputTag("hltParticleNetDiscriminatorsJetTags", "BvsAll"),
        # cms.InputTag("hltParticleNetDiscriminatorsJetTags", "CvsAll"),
        # cms.InputTag("hltParticleNetDiscriminatorsJetTags", "CvsL"),
        # cms.InputTag("hltParticleNetDiscriminatorsJetTags", "TauhvsAll"),
        # ## raw scores
        # cms.InputTag("hltParticleNetONNXJetTags", "probb"),
        # cms.InputTag("hltParticleNetONNXJetTags", "probc"),
        # cms.InputTag("hltParticleNetONNXJetTags", "probuds"),
        # cms.InputTag("hltParticleNetONNXJetTags", "probg"),
        # cms.InputTag("hltParticleNetONNXJetTags", "probtauhp"),
        # cms.InputTag("hltParticleNetONNXJetTags", "probtauhm"),
        # cms.InputTag("hltParticleNetONNXJetTags", "ptcorr"),
        
        # compact form
        *[cms.InputTag("hltParticleNetDiscriminatorsJetTags", name) for name in pnet_discriminator_names],
        *[cms.InputTag("hltParticleNetONNXJetTags", name) for name in pnet_score_names],

    ),
    addDiscriminators = cms.bool(True),
    addJetCharge = cms.bool(False),
    addGenPartonMatch = cms.bool(False),
    addAssociatedTracks = cms.bool(False),
    addGenJetMatch = cms.bool(False),
    getJetMCFlavour = cms.bool(False),
    addJetFlavourInfo = cms.bool(False),
)

process.hltPFJetForBtagTable = cms.EDProducer("SimplePATJetFlatTableProducer",
    src = cms.InputTag( "hltPFJetForBtagPAT" ),
    name= cms.string("hltAK4JetPNet"),
    doc = cms.string("HLT AK4 PF Jets w PNet"),
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(False), # this is the main table
    variables = cms.PSet(
        process.AK4PFJetsTable.variables,
        btagPNetB = Var("bDiscriminator('hltParticleNetDiscriminatorsJetTags:BvsAll')",float, doc="BvsAll"),
        btagPNetC = Var("bDiscriminator('hltParticleNetDiscriminatorsJetTags:CvsAll')",float, doc="CvsAll"),
        btagPNetCvsL = Var("bDiscriminator('hltParticleNetDiscriminatorsJetTags:CvsL')",float, doc="CvsL"),
        btagPNetTauVJet = Var("bDiscriminator('hltParticleNetDiscriminatorsJetTags:TauhvsAll')",float, doc="TauVsJet"),
        # raw scores
        btagPNet_probb = Var("bDiscriminator('hltParticleNetONNXJetTags:probb')",float, doc="probb"),
        btagPNet_probc = Var("bDiscriminator('hltParticleNetONNXJetTags:probc')",float, doc="probc"),
        btagPNet_probuds = Var("bDiscriminator('hltParticleNetONNXJetTags:probuds')",float, doc="probuds"),
        btagPNet_probg = Var("bDiscriminator('hltParticleNetONNXJetTags:probg')",float, doc="probg"),
        btagPNet_probtauhp = Var("bDiscriminator('hltParticleNetONNXJetTags:probtauhp')",float, doc="probtauhp"),
        btagPNet_probtauhm = Var("bDiscriminator('hltParticleNetONNXJetTags:probtauhm')",float, doc="probtauhm"),
        btagPNet_ptcorr = Var("bDiscriminator('hltParticleNetONNXJetTags:ptcorr')",float, doc="ptcorr"),

        # compact form - wip
        # **{f"btagPNet{name}": Var( f"bDiscriminator('hltParticleNetDiscriminatorsJetTags:{name}')",
        #                           float, doc = f"ParticleNet {name} discriminator", precision = 10,
        #                           ) for name in pnet_discriminator_names},

        # **{f"btagPNet_{name}": Var( f"bDiscriminator('hltParticleNetONNXJetTags:{name}')", 
        #                            float, doc = f"ParticleNet {name} discriminator", precision = 10,
        #                            ) for name in pnet_score_names},
    ),
)
