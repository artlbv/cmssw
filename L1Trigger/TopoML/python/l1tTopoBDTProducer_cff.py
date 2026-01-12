import FWCore.ParameterSet.Config as cms

l1tTopoBDTProducer = cms.EDProducer('L1TTopoBDTProducer',
    muToken    = cms.InputTag("gmtStage2Digis:Muon"),
    egToken    = cms.InputTag("caloStage2Digis:EGamma"),
    tauToken   = cms.InputTag("caloStage2Digis:Tau"),
    jetToken   = cms.InputTag("caloStage2Digis:Jet"),
    etSumToken = cms.InputTag("caloStage2Digis:EtSum"),
    bx = cms.int32(0),
    model_path = cms.string("L1Trigger/TopoML/data/conifer_model_HH2b2t_2recotauh.json"),
)