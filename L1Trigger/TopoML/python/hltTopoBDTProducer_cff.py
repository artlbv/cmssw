import FWCore.ParameterSet.Config as cms

# process.hltScoutingMuonPackerVtx = cms.EDProducer( "HLTTopoMuonBDTProducer",
#     ChargedCandidates = cms.InputTag( "hltIterL3MuonCandidates" ),
#     InputMuons = cms.InputTag( "hltIterL3Muons" ),
#     InputLinks = cms.InputTag( "hltL3MuonsIterL3Links" ),
#     Tracks = cms.InputTag( "hltIterL3MuonAndMuonFromL1Merged" ),
#     EcalPFClusterIsoMap = cms.InputTag( "hltMuonEcalMFPFClusterIsoForMuons" ),
#     HcalPFClusterIsoMap = cms.InputTag( "hltMuonHcalRegPFClusterIsoForMuons" ),
#     TrackIsoMap = cms.InputTag( 'hltMuonTkRelIsolationCut0p14Map','combinedRelativeIsoDeposits' ),
#     muonPtCut = cms.double( 0.0 ),
#     muonEtaCut = cms.double( 2.4 ),
#     minVtxProbCut = cms.double( 0.001 )
# )

hltTopoMuonBDTProducer = cms.EDProducer('HLTTopoMuonHTConiferBDTProducer', #cms.EDProducer('HLTTopoMuonHTPNetBConiferBDTProducer',
    # first feature: external float from another producer
    l1tTopoScore = cms.InputTag("l1tTopoBDTProducer", "score"),

    # muon candidates (used to pick leading muon)
    ChargedCandidates = cms.InputTag("hltIterL3MuonCandidates"),
    # isolation maps keyed to ChargedCandidates refs
    EcalPFClusterIsoMap = cms.InputTag("hltMuonEcalMFPFClusterIsoForMuons"),
    HcalPFClusterIsoMap = cms.InputTag("hltMuonHcalRegPFClusterIsoForMuons"),
    TrackIsoMap = cms.InputTag("hltMuonTkRelIsolationCut0p3Map", "combinedRelativeIsoDeposits"),

    # conifer JSON path (must be reachable via edm::FileInPath)
    modelPath = cms.string("L1Trigger/TopoML/data/Jan26_HLT_conif_model_HH2b2W1L_1mu_L1MuTOPOMuHT_Mu_pt-iso.json"),

    # selection cuts for the leading muon used as input to the BDT
    muonPtCut  = cms.double(8.0),
    muonEtaCut = cms.double(2.4),

    debug = cms.bool(False),
)

# l1tTopoBDTProducer = cms.EDProducer('L1TTopoBDTProducer',
#     muToken    = cms.InputTag("gmtStage2Digis:Muon"),
#     egToken    = cms.InputTag("caloStage2Digis:EGamma"),
#     tauToken   = cms.InputTag("caloStage2Digis:Tau"),
#     jetToken   = cms.InputTag("caloStage2Digis:Jet"),
#     etSumToken = cms.InputTag("caloStage2Digis:EtSum"),
#     bx = cms.int32(0),
#     model_path = cms.FileInPath("L1Trigger/TopoML/data/conifer_model_HH2b2t_2recotauh.json"),
#     debug = cms.bool(False),
# )

hltTopoMuonHTPNetBXGBProducer = cms.EDProducer('HLTTopoMuonHTPNetBXGBProducer',
    # first feature: external float from another producer
    # l1tTopoScore = cms.InputTag("l1tTopoBDTProducer", "score"),

    # PFHT (from HLTHtMhtProducer)
    PFHT = cms.InputTag("hltPFHTJet30"),

    # ParticleNet B-tag
    PNetBscore = cms.InputTag("hltParticleNetDiscriminatorsJetTags","BvsAll"),

    # muon candidates (used to pick leading muon)
    ChargedCandidates = cms.InputTag("hltIterL3MuonCandidates"),
    # isolation maps keyed to ChargedCandidates refs
    EcalPFClusterIsoMap = cms.InputTag("hltMuonEcalMFPFClusterIsoForMuons"),
    HcalPFClusterIsoMap = cms.InputTag("hltMuonHcalRegPFClusterIsoForMuons"),
    TrackIsoMap = cms.InputTag("hltMuonTkRelIsolationCut0p3Map", "combinedRelativeIsoDeposits"),

    # conifer JSON path (must be reachable via edm::FileInPath)
    modelPath = cms.string("L1Trigger/TopoML/data/HLT_xgb_model_HH2b2W1L_1mu_HLTHT_Mu_pt-iso_PNetB.json"),

    # selection cuts for the leading muon used as input to the BDT
    muonPtCut  = cms.double(8.0),
    muonEtaCut = cms.double(2.4),

    debug = cms.bool(False),
)
