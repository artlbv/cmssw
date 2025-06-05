import FWCore.ParameterSet.Config as cms

l1tTopoBDTProducer = cms.EDProducer('L1TTopoBDTProducer',
    muToken    = cms.InputTag("gmtStage2Digis:Muon"),
    egToken    = cms.InputTag("caloStage2Digis:EGamma"),
    tauToken   = cms.InputTag("caloStage2Digis:Tau"),
    jetToken   = cms.InputTag("caloStage2Digis:Jet"),
    etSumToken = cms.InputTag("caloStage2Digis:EtSum"),
    useHT = cms.bool(True),
    nJet = cms.uint32(0),
    nMu = cms.uint32(0),
    nEg = cms.uint32(0),
    nTau = cms.uint32(6),
    model_path = cms.FileInPath("L1Trigger/TopoML/data/conifer_model_HH2b2t_2recotauh.json"),
    # name = cms.string("L1TTopoBDT"),
)