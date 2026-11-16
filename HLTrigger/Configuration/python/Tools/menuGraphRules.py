"""Subsystem definitions and label rules used by hltMenuGraph.

Each module of the menu is assigned to the first subsystem whose rule matches.
A rule is a list of regular expressions tested against the module label; the
module kind (EDProducer, EDFilter, OutputModule, ...) is available to the
optional `kinds` entry. Modules that match no rule end up in "other", and
hltMenuGraph lists them on stderr so the rules can be extended.

`slot` picks one of the eight categorical colours of the page (1-8);
`None` draws the subsystem with a neutral, dashed style.
The "ext" and "infra" ids are used by the page itself (toolbar chips) and
must be kept.
"""

SUBSYSTEMS = [
    dict(id="ext", name="External inputs", slot=None,
         desc="Products read from the event (RAW, L1T, GEN, earlier processes) but not produced by this menu"),
    dict(id="infra", name="Framework & bookkeeping", slot=None,
         desc="Trigger type, prescalers, GPU status, path ends, trigger summary, report and output"),
    dict(id="l1", name="L1T seeding", slot=8,
         desc="L1T unpacking and seed filters, and the L1 objects passed to HLT reconstruction"),
    dict(id="trk", name="Tracking & vertexing", slot=1,
         desc="Pixel/strip/OT local reco, pixel tracks, tracking iterations, primary vertices, beam spot"),
    dict(id="calo", name="Calorimetry & HGCal/TICL", slot=2,
         desc="ECAL, HCAL, HGCal rec-hits, layer clusters, TICL tracksters, calo towers"),
    dict(id="pf", name="Particle Flow & PUPPI", slot=3,
         desc="PF rec-hits, clusters, blocks, PF candidates, PUPPI and CHS"),
    dict(id="jetmet", name="Jets, MET & b-tagging", slot=4,
         desc="Jets and corrections, HT/MET/MHT, secondary vertices and b-tag discriminators"),
    dict(id="egamma", name="E/gamma", slot=5,
         desc="Super-clusters, E/gamma candidates, pixel matching, GSF tracking, ID and isolation"),
    dict(id="muon", name="Muons", slot=7,
         desc="Muon local reco, L2 standalone, L3 tracking, isolation"),
    dict(id="tau", name="Taus", slot=6,
         desc="Tau reconstruction (HPS, pi0s) and tau discriminators"),
    dict(id="other", name="Unclassified", slot=None,
         desc="Modules no rule in menuGraphRules.py matched"),
]

# (subsystem id, label regexes, optional module kinds); first match wins
RULES = [
    ("infra", [r"^hltTriggerType$", r"^hltBool", r"^hltBackend$", r"^hltStatusOnGPU", r"^hltPre[A-Z]",
               r"^hltTrigReport$", r"^hltTriggerSummary", r"^hltBunchSpacing", r"^hltOutput", r"^hltDQM",
               r"^hltFEDSelector", r"Scouting", r"^hltScalers", r"^hltPSet"], ["OutputModule"]),
    ("l1", [r"^hltL1(?!Tk)", r"L1TkMuonFilter$", r"L1TkFilter$", r"^hltEGL1Seeds", r"^hltL1TEGamma",
            r"^hltL1P2GT", r"^hltGtStage2", r"^hltGmtStage2", r"^hltCaloStage2"], []),
    ("tau", [r"Tau", r"^hltHps", r"PiZeros"], []),
    ("muon", [r"Mu(?!lti)", r"Phase2L3", r"^hltCsc", r"^hltDt\d", r"^hltGem", r"^hltRpc", r"^hltMe0",
              r"^hltTripleMuon", r"^hltDoubleMuon", r"^hltL[23]"], []),
    ("egamma", [r"^hltEgamma", r"^hltDiEG", r"^hltEG\d", r"^hltEle", r"^hltDiEle", r"^hltPhoton", r"^hltDiPhoton",
                r"^hltPixelLayerPairs(L1Seeded|Unseeded)", r"EGamma", r"[Ss]uperclustering",
                r"^hltParticleFlowSuperCluster", r"ForEGamma", r"^hltRechitInRegions", r"^hltHybridSuperCluster",
                r"^hltMulti5x5", r"^hltCorrected"], []),
    ("jetmet", [r"BTag", r"^hltDeep", r"ParticleTransformer", r"DeepFlavour", r"ForBtag", r"PrimaryVertexAssociation",
                r"Jet", r"MET", r"HT", r"MHT", r"^hltFixedGridRho", r"RefsForJets", r"JME$", r"^hltAK\d", r"^hltAk\d"], []),
    ("pf", [r"^hltParticleFlow", r"^hltPFPuppi(NoLep)?$", r"^hltPfTICL$", r"^hltPfTrack$", r"^hltPFMuonMerging",
            r"^hltLightPFTracks", r"^hltPFlow"], []),
    ("calo", [r"Ecal", r"Hcal", r"^hltHbhe", r"^hltHf", r"^hltHo", r"Hgcal", r"HGCal", r"Ticl", r"LayerClusters",
              r"TowerMaker", r"^hltEs", r"Preshower", r"^hltTowerMaker"], []),
    ("trk", [r"Pixel", r"SiPhase2", r"Strip", r"Track", r"Vert", r"BeamSpot", r"LST", r"MkFit", r"InitialStep",
             r"OtRecHits", r"ClusterCheck", r"Seed", r"Triplet", r"Iter\d", r"MeasurementTracker", r"^hltSiStrip"], []),
]
