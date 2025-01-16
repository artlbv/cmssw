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

############################################################
# Taus
############################################################

############################################################
# Electrons
############################################################

############################################################
# Photons
############################################################
