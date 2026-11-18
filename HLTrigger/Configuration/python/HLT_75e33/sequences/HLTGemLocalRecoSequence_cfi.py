import FWCore.ParameterSet.Config as cms

from ..modules.hltMuonGEMDigis_cfi import *
from ..modules.hltGemRecHits_cfi import *
from ..modules.hltGemSegments_cfi import *

HLTGemLocalRecoSequence = cms.Sequence(hltMuonGEMDigis+hltGemRecHits+hltGemSegments)
