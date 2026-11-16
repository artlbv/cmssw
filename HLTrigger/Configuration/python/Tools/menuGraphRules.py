"""Subsystem definitions and label rules used by triggerMenuGraph.

Each module of the menu is assigned to the first subsystem whose rule matches.
A rule is (subsystem id, label regexes, module kinds, plugin-type regexes): it
matches when a label regex matches the module label, the module kind
(EDProducer, EDFilter, OutputModule, ...) is listed, or a type regex matches the
C++ plugin name. Modules that match no rule end up in "other", and
triggerMenuGraph lists them on stderr so the rules can be extended.

`slot` picks one of the eight categorical colours of the page (1-8);
`None` draws the subsystem with a neutral, dashed style.
The "ext" id (external inputs) and "other" (unclassified) are used by the
extraction and must be kept.
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
    dict(id="alca", name="AlCa, calibration & special", slot=None,
         desc="AlCa streams, calibration and random triggers, PPS, beam halo, cosmics"),
    dict(id="other", name="Unclassified", slot=None,
         desc="Modules no rule in menuGraphRules.py matched"),
]

# (subsystem id, label regexes, module kinds, plugin-type regexes); first match wins
RULES = [
    ("infra", [r"^hltTriggerType$", r"^hltBool", r"^hltBackend$", r"^hltStatusOnGPU", r"^hltPre[A-Z]",
               r"^hltTrigReport$", r"^hltTriggerSummary", r"^hltBunchSpacing", r"^hltOutput", r"^hltDQM",
               r"^hltFEDSelector", r"Scouting", r"^hltScalers", r"^hltPSet", r"^hltDataset", r"^hltMonitorL1TPureRate",
               r"^hltTriggerResultFilter", r"^rawData", r"^rawPrimeData", r"Packer$", r"^hltOnlineMetaData", r"^hltGetRaw"],
     ["OutputModule"],
     [r"^TriggerResultsFilter$", r"^HLTGetRaw$", r"^RawDataCollectorByLabel$", r"^EvFFED", r"^HLTScouting",
      r"^OnlineMetaDataRawToDigi$", r"^HLTPrescaler$", r"^HLTBool"]),
    ("alca", [r"^hltAlCa", r"PPS", r"CTPPS", r"Halo", r"[Cc]osmic", r"^hltCalibrationEvents", r"^hltRandomEvents",
              r"StoppedHSCP", r"^hltPhiSym", r"^hltEcalCalibration", r"^hltHcalCalibration", r"^hltLaser"], [],
     [r"^EcalRecalib", r"^HLTRechitsToDigis$", r"^HLTRegionalEcalResonanceFilter$", r"^HLTPPS", r"^CTPPS", r"^Totem"]),
    ("l1", [r"^hltL1(?!Tk)", r"L1TkMuonFilter$", r"L1TkFilter$", r"^hltEGL1Seeds", r"^hltL1TEGamma",
            r"^hltL1P2GT", r"^hltGtStage2", r"^hltGmtStage2", r"^hltCaloStage2", r"(Omtf|Bmtf|Emtf)Digis$"], [],
     [r"^HLTL1TSeed$", r"^HLTP2GT", r"^L1TRawToDigi$", r"^(Omtf|Bmtf|Emtf)Unpacker$"]),
    ("tau", [r"Tau", r"^hltHps", r"PiZeros"], [], []),
    ("muon", [r"Mu(?!lti)", r"Phase2L3", r"^hltCsc", r"^hltDt\d", r"^hltGem", r"^hltRpc", r"^hltMe0",
              r"^hltTripleMuon", r"^hltDoubleMuon", r"^hltL[23]", r"[Dd]imuon", r"mumu", r"3mu", r"^hltDTCluster",
              r"[Rr]echitCluster", r"^hltCSC", r"^hltDT"], [],
     [r"^HLTMuon", r"^HLTDisplacedmumu", r"^HLTMuonTrkFilter$"]),
    ("egamma", [r"^hltEgamma", r"^hltDiEG", r"^hltEG\d", r"^hltEle", r"^hltDiEle", r"^hltPhoton", r"^hltDiPhoton",
                r"^hltPixelLayerPairs(L1Seeded|Unseeded)", r"EGamma", r"[Ss]uperclustering",
                r"^hltParticleFlowSuperCluster", r"ForEGamma", r"^hltRechitInRegions", r"^hltHybridSuperCluster",
                r"^hltMulti5x5", r"^hltCorrected", r"^hltDoubleEG", r"^hltDoubleEle", r"^hltSingleEle", r"^hltEGL1",
                r"EG\d+", r"Ele\d", r"^hltHighEtaSC", r"3x3Clusters", r"^hltDoublePhoton", r"^hltSinglePhoton"], [],
     [r"^HLTEgamma", r"^EgammaHLT", r"^HLTPMMassFilter$", r"^HLT2PhotonPhoton", r"^HLTElectron", r"^HLTPMDoca"]),
    ("jetmet", [r"BTag", r"^hltDeep", r"ParticleTransformer", r"DeepFlavour", r"ForBtag", r"PrimaryVertexAssociation",
                r"Jet", r"MET", r"HT", r"MHT", r"^hltFixedGridRho", r"RefsForJets", r"JME$", r"^hltAK\d", r"^hltAk\d",
                r"^hltMet", r"^hltMht", r"^hltHtMht", r"PNet", r"Corrector", r"^hltHiFJRho", r"GlobalSums", r"^hltCsAK"], [],
     [r"^HLT1PFJet", r"^HLTPFJet", r"^HLTHtMht", r"^HLTMht", r"^CaloMETProducer$", r"JetCorrector", r"^HLTGlobalSums",
      r"^HLT\w*Jet"]),
    ("pf", [r"^hltParticleFlow", r"^hltPFPuppi(NoLep)?$", r"^hltPfTICL$", r"^hltPfTrack$", r"^hltPFMuonMerging",
            r"^hltLightPFTracks", r"^hltPFlow", r"^hltPFCandidate$"], [], []),
    ("calo", [r"Ecal", r"Hcal", r"^hltHbhe", r"^hltHf", r"^hltHo", r"Hgcal", r"HGCal", r"Ticl", r"LayerClusters",
              r"TowerMaker", r"^hltEs", r"Preshower", r"^hltTowerMaker"], [], [r"^HLTHPDFilter$"]),
    ("trk", [r"Pixel", r"SiPhase2", r"Strip", r"Track", r"Vert", r"BeamSpot", r"LST", r"MkFit", r"InitialStep",
             r"OtRecHits", r"ClusterCheck", r"Seed", r"Triplet", r"Iter\d", r"MeasurementTracker", r"^hltSiStrip",
             r"Seeding", r"[Ss]eedfinder", r"ClustersRefRemoval", r"LayerPairs", r"DeDx", r"^hltTrk\d"], [],
     [r"^TrackClusterRemover", r"^SeedingLayersEDProducer$", r"DeDx"]),
]

# subsystems the page can hide with a toolbar chip
CHIPS = [
    dict(sub="ext", label="External inputs"),
    dict(sub="infra", label="Bookkeeping"),
    dict(sub="alca", label="AlCa & special"),
]

# modules drawn with a dashed border: plugin type matching `types`
FLAG = dict(short="Alpaka", label="Alpaka module (portable CPU/GPU backend)", types=r"@alpaka$|^alpaka_")

# default title
TITLE = None   # "<menu> Dataflow"
