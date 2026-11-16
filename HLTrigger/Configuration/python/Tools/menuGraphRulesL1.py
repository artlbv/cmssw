"""Subsystem definitions and label rules of the triggerMenuGraph L1 profile (Phase-2 L1T emulation).

Same format as menuGraphRules.py; selected with `triggerMenuGraph --profile l1`.
"""

SUBSYSTEMS = [
    dict(id="ext", name="External inputs", slot=None,
         desc="Products read from the event (digis, GEN, earlier processes) but not produced in this configuration"),
    dict(id="truth", name="MC truth association", slot=None,
         desc="Tracking-particle association for clusters, stubs and tracks"),
    dict(id="tt", name="Track Trigger", slot=1, desc="Clusters and stubs, DTC, tracklet track finding"),
    dict(id="muon", name="Muon TPs & track finders", slot=5, desc="DT/CSC/GEM/RPC trigger primitives, BMTF/OMTF/EMTF"),
    dict(id="hgcal", name="HGCal TPG", slot=3, desc="HGCal VFE, concentrator, back-end layers and towers"),
    dict(id="gct", name="Barrel calo & GCT", slot=4, desc="Barrel EG clusters, tower calibration, GCT jets and taus"),
    dict(id="gtt", name="GTT", slot=2, desc="Global Track Trigger: track selection, vertexing, track jets and sums"),
    dict(id="gmt", name="GMT", slot=7, desc="Global Muon Trigger: stubs, standalone and track muons"),
    dict(id="corr", name="Correlator", slot=6, desc="PF/PUPPI layer 1, layer 2 EG, jets, taus and MET"),
    dict(id="gt", name="Global Trigger", slot=8, desc="P2GT object conversion and algorithm block"),
    dict(id="gtmenu", name="Menu seeds", slot=8, desc="P2GT condition filters, one per menu path"),
    dict(id="legacy", name="Legacy Run-3 emulation", slot=None,
         desc="Stage-2 calo, uGMT, uGT and ZDC emulators kept alongside Phase-2"),
    dict(id="infra", name="Framework & bookkeeping", slot=None,
         desc="Output modules and DQM/EDM bookkeeping, e.g. the end-paths cmsDriver adds"),
    dict(id="other", name="Unclassified", slot=None, desc="Modules no rule in menuGraphRulesL1.py matched"),
]

# (subsystem id, label regexes, module kinds, plugin-type regexes); first match wins
RULES = [
    ("infra", [r"^MEtoEDMConverter$", r"^dqmEnv$", r"^dqmSaver", r"^DQM\w*output$"], ["OutputModule"], []),
    ("gtmenu", [], ["EDFilter"], []),
    ("truth", [r"Associator"], [], []),
    ("legacy", [r"Stage2", r"^l1tZDC", r"^simGmtCaloSum", r"^simGmtShower", r"^simGtExtFake"], [], []),
    ("gt", [r"^l1tGT(?!T)"], [], [r"^L1GT(?!T)", r"^P2GT"]),
    ("gmt", [r"^l1t\w*Gmt$", r"Gmt$"], [], []),
    ("muon", [r"^simDt", r"^simCsc", r"^simRpc", r"^simGem", r"^simMuon", r"^simBmtf", r"^simKBmtf", r"^simOmtf",
              r"^simEmtf", r"^simTwinMux", r"^dtTrigger", r"^CalibratedDigis$", r"^ge0Trigger", r"^me0Trigger",
              r"^gemRecHits$", r"^gemSegments$", r"^rpcRecHits", r"Emtf", r"Omtf", r"Bmtf"], [], []),
    ("hgcal", [r"^l1tHGCal", r"^hgcalTrigger"], [], []),
    ("gct", [r"^l1tCaloJet", r"^l1tEGammaCluster", r"^l1tNNCaloTau", r"^l1tPhase2Calo", r"^l1tPhase2GCT",
             r"^l1tPhase2L1CaloEGamma", r"^l1tTowerCalibration", r"^l1tPhase2CaloJet", r"^l1tPhase2CaloPFCluster"], [], []),
    ("gtt", [r"^l1tGTTInput", r"^l1tTrack(Fast)?Jets", r"^l1tTrackSelection", r"^l1tTrackTriplet",
             r"^l1tTrackVertexAssociation", r"^l1tTrackerEmu", r"^l1tTrackerEtMiss", r"^l1tTrackerHTMiss",
             r"^l1tVertex", r"DisplacedVertex"], [], []),
    ("tt", [r"^TTClusters", r"^TTStubs", r"^ProducerDTC", r"^l1tTTTracks", r"^TTTracks", r"Tracklet",
            r"^offlineBeamSpot$"], [], []),
    ("corr", [r"^l1tLayer[12]", r"^l1tPF", r"^l1tSC\d", r"^l1tMET", r"^l1tBJet", r"^l1tHPSPFTau", r"^l1tNNTau",
              r"^l1tPhase1Jet", r"^l1tTOoLLiP", r"Puppi", r"Deregionizer"], [], []),
]

# subsystems the page can hide with a toolbar chip
CHIPS = [
    dict(sub="ext", label="External inputs"),
    dict(sub="legacy", label="Legacy Run-3"),
    dict(sub="truth", label="MC truth"),
]

# modules drawn with a dashed border: label matching `labels`, or in a path or sequence/task whose
# name matches `containers` (e.g. a separate L1simulationLegacy_step)
FLAG = dict(short="legacy", label="Module of the legacy Run-3 emulation",
            labels=r"Stage2|^l1tZDC|^simBmtf|^simKBmtf|^simOmtfDigis$|^simEmtfDigis$|^simEmtfShowers$|^simTwinMux"
                   r"|Run3$|^simGmtCaloSum|^simGmtShower|^simGtExtFake",
            containers=r"Legacy")

# default title and process name
TITLE = "L1T Phase-2 Dataflow"

# lint settings (triggerMenuGraph --lint), see menuGraphRules.py
LINT = dict(
    own_labels=r"^l1t",
    expected_inputs=r"^(sim\w+|mix|g4SimHits|rpcRecHits|gtStage2Digis|ak4GenJets\w*|genParticles\w*|generator\w*)$",
    ignore_unread=r"^l1tGTAlgoBlockProducer$",
)
