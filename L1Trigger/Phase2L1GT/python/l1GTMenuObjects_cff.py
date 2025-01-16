import FWCore.ParameterSet.Config as cms

############################################################
# Common objects for P2GT L1 seeds
############################################################

from L1Trigger.Phase2L1GT.l1tGTObject_constants import *

############################################################
# Muons
############################################################

l1tGTtkMuon = cms.PSet(
    tag = cms.InputTag("l1tGTProducer", "GMTTkMuons"),
    minEta = cms.double(-2.4),
    maxEta = cms.double(2.4),
    regionsAbsEtaLowerBounds = get_object_etalowbounds("GMTTkMuons"),
)
l1tGTtkMuonLoose = l1tGTtkMuon.clone(
    qualityFlags = get_object_ids("GMTTkMuons","Loose"),
)
l1tGTtkMuonVLoose = l1tGTtkMuonLoose.clone(
    qualityFlags = get_object_ids("GMTTkMuons","VLoose"),
)

############################################################
# Jets
############################################################

l1tGTsc4Jet = cms.PSet(
    tag = cms.InputTag("l1tGTProducer", "CL2JetsSC4"),
    minEta = cms.double(-2.4),
    maxEta = cms.double( 2.4),
    regionsAbsEtaLowerBounds = get_object_etalowbounds("CL2JetsSC4"),
    # minPt = cms.double(25), # safety cut - can be enabled everywhere (for now done in the get_threshold function)
)

l1tGTsc4Jet_er5 = l1tGTsc4Jet.clone(
    minEta = cms.double(-5),
    maxEta = cms.double(5),
)

############################################################
# Taus
############################################################
l1tGTnnTau = cms.PSet(
    tag = cms.InputTag("l1tGTProducer", "CL2Taus"),
    minEta = cms.double(-2.172),
    maxEta = cms.double(2.172),
    regionsAbsEtaLowerBounds = get_object_etalowbounds("CL2Taus"),
    minQualityScore = get_object_ids("CL2Taus","default")
)

############################################################
# Electrons
############################################################

############################################################
# Photons
############################################################
