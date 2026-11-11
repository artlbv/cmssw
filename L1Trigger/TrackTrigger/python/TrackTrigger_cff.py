import FWCore.ParameterSet.Config as cms

#clusters
from L1Trigger.TrackTrigger.TTClusterAlgorithmRegister_cfi import *
from L1Trigger.TrackTrigger.TTCluster_cfi import *

#stubs
from L1Trigger.TrackTrigger.TTStubAlgorithmRegister_cfi import *
from L1Trigger.TrackTrigger.TTStub_cfi import *

#sequence
TrackTriggerClustersStubs = cms.Sequence(TTClustersFromPhase2TrackerDigis*TTStubsFromPhase2TrackerDigis)

