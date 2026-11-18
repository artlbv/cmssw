import FWCore.ParameterSet.Config as cms

from ..modules.hltMuonCSCDigis_cfi import *
from ..modules.hltCsc2DRecHits_cfi import *
from ..modules.hltCscSegments_cfi import *

HLTCsclocalrecoSequence = cms.Sequence(hltMuonCSCDigis+hltCsc2DRecHits+hltCscSegments)
