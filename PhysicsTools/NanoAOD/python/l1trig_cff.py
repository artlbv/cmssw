import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.nano_eras_cff import *
from PhysicsTools.NanoAOD.common_cff import *

l1ObjVars = cms.PSet(
    P3Vars,
#    hwPt = Var("hwPt()","int8",precision=10,doc="hardware pt"),
#    hwEta = Var("hwEta()","int8",precision=10,doc="hardware eta"),
#    hwPhi = Var("hwPhi()","int8",precision=10,doc="hardware phi"),
#    hwQual = Var("hwQual()","int8",precision=10,doc="hardware qual"),
#    hwIso = Var("hwIso()","int8",precision=10,doc="hardware iso")
)


l1MuTable = cms.EDProducer("SimpleTriggerL1MuonFlatTableProducer",
    src = cms.InputTag("gmtStage2Digis","Muon"),
    minBX = cms.int32(0),
    maxBX = cms.int32(0),
    cut = cms.string(""),
    name= cms.string("L1Mu"),
    doc = cms.string(""),
    extension = cms.bool(False), # this is the main table for L1 EGs
    variables = cms.PSet(l1ObjVars,
                         hwCharge = Var("hwCharge()","int8",precision=10,doc=""),
                         hwChargeValid = Var("hwChargeValid()","int8",precision=10,doc=""),
                         tfMuonIndex = Var("tfMuonIndex()","int8",precision=10,doc=""),
                         hwTag = Var("hwTag()","int8",precision=10,doc=""),
                         hwEtaAtVtx = Var("hwEtaAtVtx()","int8",precision=10,doc=""),
                         hwPhiAtVtx = Var("hwPhiAtVtx()","int8",precision=10,doc=""),
                         etaAtVtx = Var("etaAtVtx()",float,precision=10,doc=""),
                         phiAtVtx = Var("phiAtVtx()",float,precision=10,doc=""),
                         hwIsoSum = Var("hwIsoSum()","int8",precision=10,doc=""),
                         hwDPhiExtra = Var("hwDPhiExtra()","int8",precision=10,doc=""),
                         hwDEtaExtra = Var("hwDEtaExtra()","int8",precision=10,doc=""),
                         hwRank = Var("hwRank()","int8",precision=10,doc=""),
                         hwPtUnconstrained = Var("hwPtUnconstrained()","int8",precision=10,doc=""),
                         ptUnconstrained = Var("ptUnconstrained()",float,precision=10,doc=""),
                         hwDXY = Var("hwDXY()","int8",precision=10,doc=""),
                     )
)


l1JetTable = cms.EDProducer("SimpleTriggerL1JetFlatTableProducer",
    src = cms.InputTag("caloStage2Digis","Jet"),
    minBX = cms.int32(0),
    maxBX = cms.int32(0),
    cut = cms.string("pt > 20"),
    name= cms.string("L1Jet"),
    doc = cms.string(""),
    extension = cms.bool(False), # this is the main table for L1 EGs
    variables = cms.PSet(l1ObjVars,
                         towerIEta = Var("towerIEta()","int8",precision=10,doc=""),
                         towerIPhi = Var("towerIPhi()","int8",precision=10,doc=""),
                         rawEt = Var("rawEt()","int8",precision=10,doc=""),
                         seedEt = Var("seedEt()","int8",precision=10,doc=""),
                         puEt = Var("puEt()","int8",precision=10,doc=""),
                         puDonutEt0 = Var("puDonutEt(0)","int8",precision=10,doc=""),
                         puDonutEt1 = Var("puDonutEt(1)","int8",precision=10,doc=""),
                         puDonutEt2 = Var("puDonutEt(2)","int8",precision=10,doc=""),
                         puDonutEt3 = Var("puDonutEt(3)","int8",precision=10,doc=""),
                     )
)

l1TauTable = cms.EDProducer("SimpleTriggerL1TauFlatTableProducer",
    src = cms.InputTag("caloStage2Digis","Tau"),
    minBX = cms.int32(0),
    maxBX = cms.int32(0),
    cut = cms.string("pt > 20"),
    name= cms.string("L1Tau"),
    doc = cms.string(""),
    extension = cms.bool(False), # this is the main table for L1 EGs
    variables = cms.PSet(l1ObjVars,
                         towerIEta = Var("towerIEta()","int8",precision=10,doc=""),
                         towerIPhi = Var("towerIPhi()","int8",precision=10,doc=""),
                         rawEt = Var("rawEt()","int8",precision=10,doc=""),
                         isoEt = Var("isoEt()","int8",precision=10,doc=""),
                         nTT = Var("nTT()","int8",precision=10,doc=""),
                         hasEM = Var("hasEM()","int8",precision=10,doc=""),
                         isMerged = Var("isMerged()","int8",precision=10,doc=""),

                     )
)

l1EtSumTable = cms.EDProducer("SimpleTriggerL1EtSumFlatTableProducer",
    src = cms.InputTag("caloStage2Digis","EtSum"),
    minBX = cms.int32(0),
    maxBX = cms.int32(0),
    cut = cms.string(""),
    name= cms.string("L1EtSum"),
    doc = cms.string(""),
    extension = cms.bool(False), # this is the main table for L1 EGs
    variables = cms.PSet(PTVars,
                         hwPt = Var("hwPt()","int8",precision=10,doc="hardware pt"),
                         hwPhi = Var("hwPhi()","int8",precision=10,doc="hardware phi"),
                         etSumType = Var("getType()","int8",precision=10,doc=""),
                     )
)

l1EGTable = cms.EDProducer("SimpleTriggerL1EGFlatTableProducer",
    src = cms.InputTag("caloStage2Digis","EGamma"),
    minBX = cms.int32(0),
    maxBX = cms.int32(0),
    cut = cms.string("pt > 10"),
    name= cms.string("L1EG"),
    doc = cms.string(""),
    extension = cms.bool(False), # this is the main table for L1 EGs
    variables = cms.PSet(l1ObjVars,
                         towerIEta = Var("towerIEta()","int8",precision=10,doc="tower ieta"),
                         towerIPhi = Var("towerIPhi()","int8",precision=10,doc="tower iphi"),
                         rawEt = Var("rawEt()","int8",precision=10,doc="raw et"),
                         isoEt = Var("isoEt()","int8",precision=10,doc="iso et"),
                         footprintEt = Var("footprintEt()","int8",precision=10,doc=" footprint et"),
                         nTT = Var("nTT()","int8",precision=10,doc="nr trig towers"),
                         shape = Var("shape()","int8",precision=10,doc="shape"),
                         towerHoE = Var("towerHoE()","int8",precision=10,doc="tower H/E"),
                     )
)

l1TablesTask = cms.Task(l1EGTable,l1EtSumTable,l1TauTable,l1JetTable,l1MuTable)
