import FWCore.ParameterSet.Config as cms

############################################################
# Common objects for P2GT L1 seeds
############################################################

from L1Trigger.Phase2L1GT.l1tGTObject_constants import *

############################################################
# Muons
############################################################

l1tGTtkMuonLoose = cms.PSet(
    tag = cms.InputTag("l1tGTProducer", "GMTTkMuons"),
    minEta = cms.double(-2.4),
    maxEta = cms.double(2.4),
    regionsAbsEtaLowerBounds = get_object_etalowbounds("GMTTkMuons"),
    qualityFlags = get_object_ids("GMTTkMuons","Loose"),
)

l1tGTtkMuonLooseNoRegion = cms.PSet(
    tag = cms.InputTag("l1tGTProducer", "GMTTkMuons"),
    minPt = cms.double(0),
    minEta = cms.double(-2.4),
    maxEta = cms.double(2.4),
    qualityFlags = get_object_ids("GMTTkMuons","Loose"),
)

############################################################
# Jets
############################################################

############################################################
# Taus
############################################################

############################################################
# Electrons
############################################################

############################################################
# Photons
############################################################
