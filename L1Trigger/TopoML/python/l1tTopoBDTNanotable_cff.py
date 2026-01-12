import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.nano_eras_cff import *
from PhysicsTools.NanoAOD.common_cff import *

from PhysicsTools.NanoAOD.globalVariablesTableProducer_cfi import globalVariablesTableProducer

l1tTopoBDTNanotable = globalVariablesTableProducer.clone(
    name = cms.string("L1Ttopo"),
    variables = cms.PSet(
        bdtScore = ExtVar( cms.InputTag("l1tTopoBDTProducer","score"),"float", doc="BDT score" ),
        # bdt2Score = ExtVar( cms.InputTag("l1tTopoBDTProducerOther","score"),"float", doc="BDT score" ),
    ),
) 