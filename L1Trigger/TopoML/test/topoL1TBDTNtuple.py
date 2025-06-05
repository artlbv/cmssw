# argparsing
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('python')
options.register('signal', True, VarParsing.multiplicity.singleton, VarParsing.varType.bool)
options.parseArguments()

# import of standard configurations
import FWCore.ParameterSet.Config as cms
from Configuration.Eras.Era_Run3_2024_cff import Run3_2024

process = cms.Process("l1tTopoBDT", Run3_2024)

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)

process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.Geometry.GeometryDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

NEvents = options.maxEvents
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(NEvents)
)

filelist = 'files_signal.txt' if options.signal else 'files_background.txt'
input_files = open(filelist).readlines()

process.source = cms.Source (
    "PoolSource",
    fileNames = cms.untracked.vstring(input_files),
)

from Configuration.AlCa.GlobalTag import GlobalTag
#process.GlobalTag = GlobalTag(process.GlobalTag, '133X_mcRun3_2024_realistic_v9', '')
process.GlobalTag = GlobalTag(process.GlobalTag, '142X_mcRun3_2025_realistic_v7', '')

process.load('L1Trigger.TopoML.l1tTopoBDTProducer_cff')

## different instance of the BDT producer for testing separate model
# process.l1tTopoBDTProducerOther  = process.l1tTopoBDTProducer.clone(
#     model_path = cms.FileInPath("L1Trigger/TopoML/data/conifer_model_HH2b2t_2recotauh.json"),
# )

## filter for the BDT score
process.hltL1TopoBDTFilter = cms.EDFilter("HLTFloatThresholdFilter",
    src = cms.InputTag("l1tTopoBDTProducer","score"),
    threshold = cms.double(1)  # your threshold
)


process.myTopoPath = cms.Path(
    process.l1tTopoBDTProducer
    # + process.l1tTopoBDTProducerOther 
    + process.hltL1TopoBDTFilter
)

# # create an EDM output file to store the score
# process.load('Configuration.EventContent.EventContent_cff')
# process.output = cms.OutputModule("PoolOutputModule",
#     fileName = cms.untracked.string('l1tTopoBDT.root'),
#     outputCommands = process.FEVTDEBUGEventContent.outputCommands + cms.untracked.vstring(
#         'keep *_l1tTopoBDTProducer_*_*',
#     )
# )
process.output = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string("output.root"),
    outputCommands = cms.untracked.vstring(
        # "keep *_l1tTopoBDTProducer_*_*",
        "keep *_l1tTopoBDTProducer*_*_*",
        # "drop nanoaodFlatTable_*_*_*",
    ),
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring("myTopoPath")
    )
)
process.out = cms.EndPath(process.output)

# create a NanoAOD output file to store the score
# process.load('PhysicsTools.NanoAOD.nano_cff')
# process.nanoSequenceMC = cms.Sequence(process.nanoAODCommonTask)
# process.nanoAODCommonTask.remove(process.nanoTableTaskCommon)  # remove the common task to avoid conflicts
# process.nanoAODCommonTask.add(process.l1tTopoBDTProducer)  # add the BDT producer to the common task    

signal_ext = '_signal' if options.signal else '_backgroud'
oname = 'L1TMLDemo_NanoAOD' + signal_ext + '.root'

process.outnano = cms.OutputModule("NanoAODOutputModule",
    fileName = cms.untracked.string(oname),
    outputCommands = cms.untracked.vstring("drop *", "keep nanoaodFlatTable_*_*_*"),
    compressionLevel = cms.untracked.int32(4),
    compressionAlgorithm = cms.untracked.string("ZLIB"),
)
process.end = cms.EndPath(process.outnano)

## Add L1 nano

process.load('DPGAnalysis.L1TNanoAOD.l1tNano_cff')
process.user_step = cms.Path(process.l1tNanoTask)

## add nano score table
process.load('L1Trigger.TopoML.l1tTopoBDTNanotable_cff')
# from L1Trigger.TopoML.l1tTopoBDTNanotable_cff import l1tTopoBDTNanotable
# process.l1tTopoBDTNanotable = l1tTopoBDTNanotable
#process.l1tNanoTask.add(cms.Task(l1tTopoBDTNanotable)) 
process.l1tNanoTask.add(process.l1tTopoBDTNanotable)


process.schedule = cms.Schedule(
    process.user_step, # l1 nano
    process.myTopoPath, # my producer
    process.end, # nano
    process.out, # raw/fevt
)

### Add FULL NANO

# process.load('PhysicsTools.NanoAOD.nano_cff')
# process.nanoAOD_step = cms.Path(process.nanoSequenceMC)
# process.schedule = cms.Schedule(process.path, process.nanoAOD_step, process.end)

# # Automatic addition of the customisation function from PhysicsTools.NanoAOD.nano_cff
# from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeCommon 

# #call to customisation function nanoAOD_customizeCommon imported from PhysicsTools.NanoAOD.nano_cff
# process = nanoAOD_customizeCommon(process)

# from PhysicsTools.NanoAOD.l1trig_cff import *
# process = 
# # Automatic addition of the customisation function from PhysicsTools.NanoAOD.l1trig_cff
# from PhysicsTools.NanoAOD.l1trig_cff import nanoL1TrigObjCustomizeFull 

# #call to customisation function nanoL1TrigObjCustomizeFull imported from PhysicsTools.NanoAOD.l1trig_cff
# process = nanoL1TrigObjCustomizeFull(process)

# # process.nanoSequenceMC.remove(process.boostedTauTable) 
# process.nanoTableTaskCommon = cms.Task(process.l1TablesTask)
