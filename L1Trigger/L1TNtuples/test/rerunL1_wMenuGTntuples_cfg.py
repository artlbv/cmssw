# Auto generated configuration file
# using:
# Revision: 1.19
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v
# with command line options: step1 --conditions 125X_mcRun4_realistic_v2 -n 2 --era Phase2C17I13M9 --eventcontent FEVTDEBUGHLT -s RAW2DIGI,L1:RUNP2GT --datatier GEN-SIM-DIGI-RAW-MINIAOD --fileout file:test.root --customise SLHCUpgradeSimulations/Configuration/aging.customise_aging_1000,Configuration/DataProcessing/Utils.addMonitoring,L1Trigger/Configuration/customisePhase2.addHcalTriggerPrimitives,L1Trigger/Configuration/customisePhase2FEVTDEBUGHLT.customisePhase2FEVTDEBUGHLT --geometry Extended2026D88 --nThreads 1 --filein file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/00e84477-cac7-4817-9c46-f3fca87c448a.root --mc --inputCommands=keep *, drop l1tPFJets_*_*_* --outputCommands=keep *P2GT*_*_*_*, drop l1tPFJets_*_*_* --python_filename rerunL1_only_cfg.py
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Phase2C17I13M9_cff import Phase2C17I13M9

process = cms.Process('L1',Phase2C17I13M9)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtended2026D88Reco_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.RawToDigi_cff')
process.load('L1Trigger.Phase2L1GT.l1tGTProducer_cff')
process.load('L1Trigger.Phase2L1GT.l1tGTMenu_hadr_metSeeds_cff')
process.load('L1Trigger.Phase2L1GT.l1tGTMenu_lepSeeds_cff')
process.load('L1Trigger.Phase2L1GT.l1tGTAlgoBlockProducer_cff')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')


process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1),
    output = cms.optional.untracked.allowed(cms.int32,cms.PSet)
)

# Input source
process.source = cms.Source("PoolSource",
                            dropDescendantsOfDroppedBranches = cms.untracked.bool(False),
                            fileNames = cms.untracked.vstring(
                                #'file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/00e84477-cac7-4817-9c46-f3fca87c448a.root'
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/00e84477-cac7-4817-9c46-f3fca87c448a.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/024ccc1b-63c3-4ac7-83d3-255f787645e3.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/0d1a21ba-3b0e-42c6-957a-d4b1f8e41a9e.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/10c96616-9e4d-4b18-a5f7-9d9b2e796bd2.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/1a30cc0f-7793-4cff-909a-124ff5725a5d.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/202fb2eb-35ad-4d85-b6da-f350eb3b00b1.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/20650d9d-36d7-4d96-bed9-f5b5f0c1b88a.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/22277191-52cd-4a54-88f2-76af5103411d.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/24d0b96b-fa01-4fd9-bf76-50701b04bdc3.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/2a523243-d594-4732-963f-c7e75784e8b4.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/2a79ea0f-716c-4d46-aab8-217de921497e.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/2ab6bda8-00e6-4f62-ae87-fd18bffacc50.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/2fb0a5f9-c960-4dcb-b6cc-d97032086539.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/2fb3bff7-546d-4213-9d8c-ac748ba71bfc.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/37159117-8b5c-44cf-8f30-608ab80097cc.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/38055029-af84-4944-ae6b-8aa3703e8c6f.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/38b4c964-d503-473b-8668-2abb50f0c0f7.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/38c4432b-cc3d-4632-be08-81524c7bd79c.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/39d830cc-1f87-4430-a508-cb0bc5cdbf53.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/3defb59f-7a8e-46c1-b2ca-9be6e40856b7.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/3ed24450-878e-459e-8604-c2587b95913a.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/407db8b4-04fa-4078-9fc2-1b8236cdc09e.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/4b61ed52-cf5f-4e14-832c-6bf9a0268b1a.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/4c98ad5e-0c34-4b46-83fd-b90db70bce1b.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/4cd0cc96-9871-430a-911f-197e8fefd192.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/4f4cd52d-60ef-4946-8189-066cbae7f220.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/53818e5c-b920-4940-a256-07fec3abe4e3.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/5cfcd0d7-cf3d-474b-9dcb-ac7145831402.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/6401d7b1-c46b-4d34-b830-60eae7e456bc.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/6596ec72-181a-4cee-a9b5-133866b282fa.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/6c553840-33e5-48a4-9cc2-1e1706e82451.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/7044eb89-0f06-451b-9b05-f008f7fe3c70.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/70e6ac91-8c16-4dfd-af15-efabe2b3de3c.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/711793c0-1197-4b20-b9fc-b2ac90991d38.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/745aaf71-9ad3-4b1d-b564-49635ffec46f.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/7ee7c245-35c0-471d-b557-a60e9f9d04de.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/8e3e39d7-73fb-44e5-9c3c-1ba120dbf6d3.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/8e5a4ef1-987e-4af4-8efb-4519ef9b9049.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/918771a3-7441-4de9-8cb9-2bb0bee8d7f2.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/93daf686-35cc-4609-bb51-d1103816c3ea.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/94e76ff5-a0f7-4ffc-abb0-8e88a4f0ff67.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/95e0c62a-aaf1-49b2-a4e5-d11fbd20f436.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/9604cc3a-8fca-461b-ade3-77c243a479e6.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/96f9ad4a-1c88-48e5-844b-78a70e3dcfc8.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/982d0c30-fb1d-4700-b017-9efeab5d80fe.root",
                                "file:/eos/cms/store/relval/CMSSW_13_1_0/RelValTTbar_14TeV/GEN-SIM-RECO/PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/2590000/99344289-dede-40e3-9803-4690ba7f6e9f.root",
                            ),
                            inputCommands = cms.untracked.vstring(
                                'keep *',
                                'drop l1tPFJets_*_*_*'
                            ),
                            secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(
    FailPath = cms.untracked.vstring(),
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
    SkipEvent = cms.untracked.vstring(),
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
    modulesToIgnoreForDeleteEarly = cms.untracked.vstring(),
    numberOfConcurrentLuminosityBlocks = cms.untracked.uint32(0),
    numberOfConcurrentRuns = cms.untracked.uint32(1),
    numberOfStreams = cms.untracked.uint32(0),
    numberOfThreads = cms.untracked.uint32(1),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False)
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('step1 nevts:2'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.FEVTDEBUGHLToutput = cms.OutputModule("PoolOutputModule",
                                              dataset = cms.untracked.PSet(
                                                  dataTier = cms.untracked.string('GEN-SIM-DIGI-RAW-MINIAOD'),
                                                  filterName = cms.untracked.string('')
                                              ),
                                              fileName = cms.untracked.string('file:test.root'),
                                              outputCommands = process.FEVTDEBUGHLTEventContent.outputCommands,
                                              splitLevel = cms.untracked.int32(0)
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '125X_mcRun4_realistic_v2', '')
process.FEVTDEBUGHLToutput.outputCommands.append('drop *')
process.FEVTDEBUGHLToutput.outputCommands.append('keep *P2GT*_*_*_*')
process.FEVTDEBUGHLToutput.outputCommands.append('drop l1tPFJets_*_*_*')

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.Phase2L1GTProducer = cms.Path(process.l1tGTProducerSequence)
process.pPuppiHT400 = cms.Path(process.PuppiHT400)
process.pPuppiHT450 = cms.Path(process.PuppiHT450)
process.pPuppiMET200 = cms.Path(process.PuppiMET200)
process.pQuadJet70_55_40_40 = cms.Path(process.QuadJet70554040)
process.pSinglePuppiJet230 = cms.Path(process.SinglePuppiJet230)
process.pDoubleEGEle37_24 = cms.Path(process.DoubleEGEle3724)
process.pDoubleIsoTkPho22_12 = cms.Path(process.DoubleIsoTkPho2212)
process.pDoublePuppiTau52_52 = cms.Path(process.DoublePuppiTau5252)
process.pDoubleTkEle25_12 = cms.Path(process.DoubleTkEle2512)
process.pDoubleTkMuon15_7 = cms.Path(process.DoubleTkMuon157)
process.pIsoTkEleEGEle22_12 = cms.Path(process.IsoTkEleEGEle2212)
process.pSingleEGEle51 = cms.Path(process.SingleEGEle51)
process.pSingleIsoTkEle28 = cms.Path(process.SingleIsoTkEle28)
process.pSingleIsoTkPho36 = cms.Path(process.SingleIsoTkPho36)
process.pSingleTkEle36 = cms.Path(process.SingleTkEle36)
process.pSingleTkMuon22 = cms.Path(process.SingleTkMuon22)
process.pTripleTkMuon5_3_3 = cms.Path(process.TripleTkMuon533)
process.Phase2L1GTAlgoBlockProducer = cms.Path(process.l1tGTAlgoBlockProducerSequence)
process.L1simulation_step = cms.Path(process.SimL1Emulator)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.FEVTDEBUGHLToutput_step = cms.EndPath(process.FEVTDEBUGHLToutput)

## GT ntupler
process.load('L1Trigger.Configuration.GTemulator_cff')
process.GTemulation_step = cms.Path(process.GTemulator)

#process.load('L1Trigger.Phase2L1GT.l1tGTMenu_cff')
#from L1Trigger.Phase2L1GT.l1tGTAlgoBlockProducer_cff import collectAlgorithmPaths


process.GToutput = cms.OutputModule("PoolOutputModule",
                                    outputCommands = cms.untracked.vstring('drop *',
                                                                           #'keep *_l1ctLayer2*_*',
                                                                           #'keep *_l1tLayer2EG_*_*',
                                                                           #'keep *l1tLayer2EG*_*_*_L1TEmulation',
                                                                           'keep *P2GT*_*_*_L1',
                                    ),
                                    fileName=cms.untracked.string("l1t_emulation.root")
)

process.pGToutput = cms.EndPath(process.GToutput)


## add menu ntupler
process.load("L1Trigger.L1TNtuples.l1PhaseIITreeStep1Producer_cfi")
process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string('L1NtuplePhaseII_Step1.root')
)

#process.load('PhysicsTools.PatAlgos.slimming.slimmedGenJetsFlavourInfos_cfi')
#process.runmenutree.genTree.jetFlavourInfosToken = process.slimmedGenJetsFlavourInfos



# Schedule definition
process.schedule = cms.Schedule(
    process.raw2digi_step,
    process.L1simulation_step,
    # menu ntuple
    process.runmenutree,
    ## GT
    process.Phase2L1GTProducer,
    process.Phase2L1GTAlgoBlockProducer,
    #process.GTemulation_step,
    ## GT algos
    process.pPuppiHT400,process.pPuppiHT450,
    process.pPuppiMET200,process.pQuadJet70_55_40_40,
    process.pSinglePuppiJet230,process.pDoubleEGEle37_24,
    process.pDoubleIsoTkPho22_12,process.pDoublePuppiTau52_52,
    process.pDoubleTkEle25_12,process.pDoubleTkMuon15_7,process.pIsoTkEleEGEle22_12,
    process.pSingleEGEle51,process.pSingleIsoTkEle28,
    process.pSingleIsoTkPho36,process.pSingleTkEle36,process.pSingleTkMuon22,process.pTripleTkMuon5_3_3,
    ## GT ntuple
    process.pGToutput,
    process.endjob_step,
    #process.FEVTDEBUGHLToutput_step
)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from SLHCUpgradeSimulations.Configuration.aging
from SLHCUpgradeSimulations.Configuration.aging import customise_aging_1000

#call to customisation function customise_aging_1000 imported from SLHCUpgradeSimulations.Configuration.aging
process = customise_aging_1000(process)

# Automatic addition of the customisation function from Configuration.DataProcessing.Utils
from Configuration.DataProcessing.Utils import addMonitoring

#call to customisation function addMonitoring imported from Configuration.DataProcessing.Utils
process = addMonitoring(process)

# Automatic addition of the customisation function from L1Trigger.Configuration.customisePhase2
from L1Trigger.Configuration.customisePhase2 import addHcalTriggerPrimitives

#call to customisation function addHcalTriggerPrimitives imported from L1Trigger.Configuration.customisePhase2
process = addHcalTriggerPrimitives(process)

# Automatic addition of the customisation function from L1Trigger.Configuration.customisePhase2FEVTDEBUGHLT
from L1Trigger.Configuration.customisePhase2FEVTDEBUGHLT import customisePhase2FEVTDEBUGHLT

#call to customisation function customisePhase2FEVTDEBUGHLT imported from L1Trigger.Configuration.customisePhase2FEVTDEBUGHLT
process = customisePhase2FEVTDEBUGHLT(process)

# End of customisation functions


# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
