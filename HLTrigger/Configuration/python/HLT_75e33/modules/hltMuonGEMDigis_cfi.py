import FWCore.ParameterSet.Config as cms

hltMuonGEMDigis = cms.EDProducer("GEMRawToDigiModule",
    InputLabel = cms.InputTag("rawDataCollector"),
    mightGet = cms.optional.untracked.vstring,
    readMultiBX = cms.bool(True),
    useDBEMap = cms.bool(False)
)
