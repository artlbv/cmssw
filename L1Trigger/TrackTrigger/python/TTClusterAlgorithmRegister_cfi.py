import FWCore.ParameterSet.Config as cms

# official clustering algorithm
TTClusterAlgorithm_official_Phase2TrackerDigi_ = cms.ESProducer("TTClusterAlgorithm_official_Phase2TrackerDigi_",
    WidthCut = cms.int32(4)
)
