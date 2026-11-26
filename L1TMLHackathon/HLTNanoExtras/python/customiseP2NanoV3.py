"""Phase-2 L1+HLT nano v3 (ML@L1 hackathon 2026): v2 + offline tables + HLT ParT up to |eta| < 3.

    from L1TMLHackathon.HLTNanoExtras.customiseP2NanoV3 import customiseP2NanoV3
    process = customiseP2NanoV3(process)   # after customiseP2NanoV2

- customiseP2NanoOffline: offline (MINIAOD) counterparts of the L1 / HLT objects, prefix "off". Needs
  dropDescendantsOfDroppedBranches = False on the source, or the MINIAOD METs silently disappear.
- HLT ParticleTransformer AK4 evaluated for jets with |eta| < 3 (menu: 2.1), for the hltAK4PuppiJet_ParT_* scores
  and the ParT input-feature tables. Its only HLT consumer, HLT_DoubleMediumPFPuppiParTTauh30_eta2p1
  (TauTagFilter, maxEta = 2.1), cuts on the jet eta itself, so the HLT decisions are unchanged. Between 2.1 and 3
  the model (trained within |eta| < 2.1) extrapolates.
"""
import FWCore.ParameterSet.Config as cms

PART_MAX_JET_ETA = 3.0


def customiseP2NanoV3(process):
    from L1TMLHackathon.HLTNanoExtras.customiseP2NanoOffline import customiseP2NanoOffline

    assert not process.source.dropDescendantsOfDroppedBranches.value(), \
        "offline tables need dropDescendantsOfDroppedBranches = False"
    process = customiseP2NanoOffline(process)
    process.hltParticleTransformerAK4TagInfos.max_jet_eta = cms.double(PART_MAX_JET_ETA)
    return process
