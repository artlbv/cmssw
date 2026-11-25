"""Offline (MINIAOD) counterparts of the L1 / HLT objects of the Phase-2 menu tools, for the p2nano production.

    from L1TMLHackathon.HLTNanoExtras.customiseP2NanoOffline import customiseP2NanoOffline
    process = customiseP2NanoOffline(process)

The Spring24 inputs are GEN-SIM-DIGI-RAW-MINIAOD, so the offline PAT objects are in the same file as the RAW that the
L1 / HLT re-emulation reads. The tables only read stored MINIAOD content: no Run-3 NanoAOD chain (no VID recomputation,
no jet energy corrections from the global tag, no cross-linking), the IDs / taggers / JECs are those of the Spring24
MINIAOD production (140X_mcRun4_realistic_v4). Collections carry the prefix "off" (next to L1* and hlt*):

  offMuon            slimmedMuons             cut-based IDs, PF / tracker isolation, dxy / dz
  offElectron        slimmedElectrons         barrel only (|eta| < ~1.48): shower shape, H/E, track match, isolations,
                                              cut-based IDs (Run-3 Winter22 and Fall17 V2 WPs, i.e. not tuned for PU 200)
  offElectronHGC     slimmedElectronsHGC      endcap (HGCAL): no ID stored, the hgcElectronID shower variables instead;
                                              H/E, PF and PF-cluster isolations are 0 in the MINIAOD (not stored)
  offPhoton          slimmedPhotons           barrel only
  offPhotonHGC       slimmedPhotonsHGC        endcap (HGCAL), hgcPhotonID shower variables
  offTau             slimmedTaus              HPS taus with DeepTau 2026v2p5 (Phase-2 training) and 2018v2p5 for reference
  offAK4PuppiJet     slimmedJetsPuppi         MINIAOD JECs (L2L3), energy fractions, DeepFlavour / PNet / UParT scores
  offAK8PuppiJet     slimmedJetsAK8           soft-drop mass (-1e5 without subjets), N-subjettiness, PNet X->bb
  offPuppiMET        slimmedMETsPuppi         type-1 and raw PUPPI MET (singleton)
  offPV              offlineSlimmedPrimaryVertices   leading vertex z, ndof, number of vertices (singleton-like, first 1)

Not added: boosted taus (no boosted DeepTau in the Phase-2 MINIAOD), pileup jet ID (not stored; the Run-3 nano
computes it itself), low-pT electrons, PF MET (PU 200: median 100 GeV against 37 for PUPPI), the RECO-step TrigObj.
Note for the input: the PoolSource must keep dropDescendantsOfDroppedBranches = False (cmsDriver sets it together with
--inputCommands): the MINIAOD METs descend from products the production drops, and would silently disappear.
"""
import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import Var, P3Vars, P4Vars, CandVars

ELE_CB = "cutBasedElectronID-RunIIIWinter22-V1"
ELE_CB17 = "cutBasedElectronID-Fall17-94X-V2"
DEEPTAU = "DeepTau2026v2p5"
DEEPTAU18 = "DeepTau2018v2p5"
WPS8 = ("VVVLoose", "VVLoose", "VLoose", "Loose", "Medium", "Tight", "VTight", "VVTight")
WPS_MU = ("VLoose", "Loose", "Medium", "Tight")


def _sum_ids(fmt, wps):
    return " + ".join(fmt.format(w) for w in wps)


def _table(cpp, src, name, doc, cut, variables, singleton=False, maxLen=None):
    pset = dict(src=cms.InputTag(src), name=cms.string(name), doc=cms.string(doc),
                singleton=cms.bool(singleton), extension=cms.bool(False), skipNonExistingSrc=cms.bool(True),
                variables=variables)
    if not singleton:
        pset["cut"] = cms.string(cut)
    if maxLen is not None:
        pset["maxLen"] = cms.uint32(maxLen)
    return cms.EDProducer(cpp, **pset)


def _ele_vars(hgc):
    v = cms.PSet(CandVars,
        scEta=Var("superCluster().eta()", float, doc="supercluster eta", precision=10),
        scEnergy=Var("superCluster().energy()", float, doc="supercluster energy", precision=10),
        dEtaIn=Var("deltaEtaSuperClusterTrackAtVtx()", float, doc="delta eta (SC, track at vertex)", precision=10),
        dEtaSeed=Var("deltaEtaSeedClusterTrackAtVtx()", float, doc="delta eta (seed cluster, track at vertex)", precision=10),
        dPhiIn=Var("deltaPhiSuperClusterTrackAtVtx()", float, doc="delta phi (SC, track at vertex)", precision=10),
        eInvMinusPInv=Var("(1-eSuperClusterOverP())/ecalEnergy()", float, doc="1/E_SC - 1/p_trk", precision=10),
        lostHits=Var("gsfTrack.hitPattern.numberOfLostHits('MISSING_INNER_HITS')", "uint8", doc="missing inner hits"),
        dxy=Var("dB('PV2D')", float, doc="dxy w.r.t. the first PV, cm", precision=10),
        dz=Var("dB('PVDZ')", float, doc="dz w.r.t. the first PV, cm", precision=10),
        trkIso03=Var("dr03TkSumPt()", float, doc="track isolation dR=0.3 (absolute)", precision=10),
    )
    if hgc:  # H/E, PF and PF-cluster isolations are 0 for every HGCAL electron in the Spring24 MINIAOD
        for n in ("sigmaUU", "sigmaVV", "sigmaEE", "sigmaPP", "e4oEtot", "layerEfrac10", "layerEfrac90",
                  "measuredDepth", "expectedDepth", "depthCompatibility", "caloIsoRing0", "caloIsoRing1",
                  "caloIsoRing2", "caloIsoRing3", "caloIsoRing4", "ecEnergy", "ecEt"):
            setattr(v, n, Var(f"userFloat('hgcElectronID:{n}')", float, doc=f"hgcElectronID {n}", precision=10))
        for n in ("nLayers", "firstLayer", "lastLayer"):
            setattr(v, n, Var(f"userFloat('hgcElectronID:{n}')", "int16", doc=f"hgcElectronID {n}"))
    else:
        v.hoe = Var("hadronicOverEm()", float, doc="H over E", precision=8)
        v.pfRelIso03_all = Var("(pfIsolationVariables().sumChargedHadronPt + max(pfIsolationVariables().sumNeutralHadronEt"
                               " + pfIsolationVariables().sumPhotonEt - pfIsolationVariables().sumPUPt/2, 0.0))/pt", float,
                               doc="PF relative isolation dR=0.3, delta-beta corrected", precision=10)
        v.pfRelIso03_chg = Var("pfIsolationVariables().sumChargedHadronPt/pt", float, doc="PF charged relative isolation dR=0.3", precision=10)
        v.ecalPFClusterIso = Var("ecalPFClusterIso()", float, doc="ECAL PF cluster isolation (absolute)", precision=10)
        v.hcalPFClusterIso = Var("hcalPFClusterIso()", float, doc="HCAL PF cluster isolation (absolute)", precision=10)
        v.sieie = Var("full5x5_sigmaIetaIeta()", float, doc="full 5x5 sigma_ietaieta", precision=10)
        v.r9 = Var("full5x5_r9()", float, doc="full 5x5 R9", precision=10)
        v.cutBased = Var(_sum_ids("electronID('%s-{}')" % ELE_CB, ("veto", "loose", "medium", "tight")), "uint8",
                         doc=f"cut-based ID {ELE_CB} (0 fail, 1 veto, 2 loose, 3 medium, 4 tight; Run-3 tuning)")
        v.cutBasedFall17V2 = Var(_sum_ids("electronID('%s-{}')" % ELE_CB17, ("veto", "loose", "medium", "tight")), "uint8",
                                 doc=f"cut-based ID {ELE_CB17} (0-4)")
        v.mvaIsoRun3 = Var("userFloat('ElectronMVAEstimatorRun2RunIIIWinter22IsoV1Values')", float,
                           doc="stored Run-3 Winter22 iso MVA value (not tuned for PU 200)", precision=10)
    return v


def _pho_vars(hgc):
    v = cms.PSet(P3Vars,
        scEta=Var("superCluster().eta()", float, doc="supercluster eta", precision=10),
        hasPixelSeed=Var("hasPixelSeed()", bool, doc="has a pixel seed"),
    )
    if hgc:  # H/E and all isolations are 0 for every HGCAL photon in the Spring24 MINIAOD
        for n in ("sigmaUU", "sigmaVV", "sigmaEE", "sigmaPP", "e4oEtot", "layerEfrac10", "layerEfrac90",
                  "measuredDepth", "expectedDepth", "depthCompatibility", "caloIsoRing0", "caloIsoRing1",
                  "caloIsoRing2", "caloIsoRing3", "caloIsoRing4", "seedEt"):
            setattr(v, n, Var(f"userFloat('hgcPhotonID:{n}')", float, doc=f"hgcPhotonID {n}", precision=10))
        for n in ("nLayers", "firstLayer", "lastLayer"):
            setattr(v, n, Var(f"userFloat('hgcPhotonID:{n}')", "int16", doc=f"hgcPhotonID {n}"))
    else:
        v.hoe = Var("hadronicOverEm()", float, doc="H over E", precision=8)
        v.pfChargedIso = Var("chargedHadronIso()", float, doc="PF charged isolation (absolute)", precision=10)
        v.pfPhotonIso = Var("photonIso()", float, doc="PF photon isolation (absolute)", precision=10)
        v.pfNeutralIso = Var("neutralHadronIso()", float, doc="PF neutral hadron isolation (absolute)", precision=10)
        v.trkIso03 = Var("trkSumPtHollowConeDR03()", float, doc="hollow-cone track isolation dR=0.3", precision=10)
        v.ecalPFClusterIso = Var("ecalPFClusterIso()", float, doc="ECAL PF cluster isolation (absolute)", precision=10)
        v.hcalPFClusterIso = Var("hcalPFClusterIso()", float, doc="HCAL PF cluster isolation (absolute)", precision=10)
        v.sieie = Var("full5x5_sigmaIetaIeta()", float, doc="full 5x5 sigma_ietaieta", precision=10)
        v.r9 = Var("full5x5_r9()", float, doc="full 5x5 R9", precision=10)
        v.mvaIDRun3 = Var("userFloat('PhotonMVAEstimatorRunIIIWinter22v1Values')", float,
                          doc="stored Run-3 Winter22 photon MVA value (not tuned for PU 200)", precision=10)
    return v


def customiseP2NanoOffline(process, path="nanoAOD_step1"):
    t = {}

    t["offMuonTable"] = _table("SimplePATMuonFlatTableProducer", "slimmedMuons", "offMuon",
        "offline muons (slimmedMuons)", "pt > 3 && abs(eta) < 3",
        cms.PSet(CandVars,
            looseId=Var("passed('CutBasedIdLoose')", bool, doc="cut-based ID, loose"),
            mediumId=Var("passed('CutBasedIdMedium')", bool, doc="cut-based ID, medium"),
            tightId=Var("passed('CutBasedIdTight')", bool, doc="cut-based ID, tight"),
            isGlobal=Var("isGlobalMuon", bool), isTracker=Var("isTrackerMuon", bool),
            isStandalone=Var("isStandAloneMuon", bool), isPFcand=Var("isPFMuon", bool),
            dxy=Var("dB('PV2D')", float, doc="dxy w.r.t. the first PV, cm", precision=10),
            dz=Var("dB('PVDZ')", float, doc="dz w.r.t. the first PV, cm", precision=10),
            pfRelIso04_all=Var("(pfIsolationR04().sumChargedHadronPt + max(pfIsolationR04().sumNeutralHadronEt"
                               " + pfIsolationR04().sumPhotonEt - pfIsolationR04().sumPUPt/2, 0.0))/pt", float,
                               doc="PF relative isolation dR=0.4, delta-beta corrected", precision=10),
            pfRelIso03_all=Var("(pfIsolationR03().sumChargedHadronPt + max(pfIsolationR03().sumNeutralHadronEt"
                               " + pfIsolationR03().sumPhotonEt - pfIsolationR03().sumPUPt/2, 0.0))/pt", float,
                               doc="PF relative isolation dR=0.3, delta-beta corrected", precision=10),
            pfRelIso03_chg=Var("pfIsolationR03().sumChargedHadronPt/pt", float, doc="PF charged relative isolation dR=0.3", precision=10),
            tkRelIso=Var("isolationR03().sumPt/pt", float, doc="tracker relative isolation dR=0.3", precision=10),
        ))

    t["offElectronTable"] = _table("SimplePATElectronFlatTableProducer", "slimmedElectrons", "offElectron",
        "offline barrel electrons (slimmedElectrons)", "pt > 5", _ele_vars(False))
    t["offElectronHGCTable"] = _table("SimplePATElectronFlatTableProducer", "slimmedElectronsHGC", "offElectronHGC",
        "offline HGCAL electrons (slimmedElectronsHGC)", "pt > 5", _ele_vars(True))
    t["offPhotonTable"] = _table("SimplePATPhotonFlatTableProducer", "slimmedPhotons", "offPhoton",
        "offline barrel photons (slimmedPhotons)", "pt > 10", _pho_vars(False))
    t["offPhotonHGCTable"] = _table("SimplePATPhotonFlatTableProducer", "slimmedPhotonsHGC", "offPhotonHGC",
        "offline HGCAL photons (slimmedPhotonsHGC)", "pt > 10", _pho_vars(True))

    tau = cms.PSet(CandVars,
        decayMode=Var("decayMode()", "int16", doc="HPS decay mode"),
        idDecayModeNewDMs=Var("tauID('decayModeFindingNewDMs')", bool, doc="new decay mode finding"),
        dxy=Var("?leadChargedHadrCand.isNonnull()?leadChargedHadrCand().dxy():0", float,
                doc="dxy of the leading track w.r.t. the PV, cm", precision=10, lazyEval=True),
        dz=Var("?leadChargedHadrCand.isNonnull()?leadChargedHadrCand().dz():0", float,
               doc="dz of the leading track w.r.t. the PV, cm", precision=14, lazyEval=True),
        chargedIso=Var("tauID('chargedIsoPtSum')", float, doc="charged isolation", precision=10),
        neutralIso=Var("tauID('neutralIsoPtSum')", float, doc="neutral isolation", precision=10),
    )
    for tag, wps_e in ((DEEPTAU, WPS8), (DEEPTAU18, WPS8)):
        for vs, wps in (("jet", WPS8), ("e", wps_e), ("mu", WPS_MU)):
            setattr(tau, f"raw{tag}VS{vs}", Var(f"tauID('by{tag}VS{vs}raw')", float, doc=f"{tag} raw score vs {vs}", precision=10))
            setattr(tau, f"id{tag}VS{vs}", Var(_sum_ids("tauID('by{}%sVS%s')" % (tag, vs), wps), "uint8",
                    doc=f"{tag} vs {vs} WPs passed: " + ", ".join(f"{i + 1} = {w}" for i, w in enumerate(wps))))
    t["offTauTable"] = _table("SimplePATTauFlatTableProducer", "slimmedTaus", "offTau",
        "offline HPS taus (slimmedTaus)", "pt > 18 && tauID('decayModeFindingNewDMs')", tau)

    pn, up = "pfParticleNetFromMiniAODAK4PuppiCentral", "pfUnifiedParticleTransformerAK4"
    jet = cms.PSet(P4Vars,
        rawFactor=Var("1.-jecFactor('Uncorrected')", float, doc="1 - (raw pt / pt)", precision=6),
        area=Var("jetArea()", float, precision=10),
        chHEF=Var("chargedHadronEnergyFraction()", float, precision=6),
        neHEF=Var("neutralHadronEnergyFraction()", float, precision=6),
        chEmEF=Var("chargedEmEnergyFraction()", float, precision=6),
        neEmEF=Var("neutralEmEnergyFraction()", float, precision=6),
        muEF=Var("muonEnergyFraction()", float, precision=6),
        nConstituents=Var("numberOfDaughters()", "uint8"),
        chMultiplicity=Var("chargedMultiplicity()", "uint8"),
        neMultiplicity=Var("neutralMultiplicity()", "uint8"),
        hadronFlavour=Var("hadronFlavour()", "uint8"),
        partonFlavour=Var("partonFlavour()", "int16"),
        btagDeepFlavB=Var("bDiscriminator('pfDeepFlavourJetTags:probb')+bDiscriminator('pfDeepFlavourJetTags:probbb')"
                          "+bDiscriminator('pfDeepFlavourJetTags:problepb')", float, doc="DeepFlavour b+bb+lepb", precision=10),
        btagPNetB=Var(f"bDiscriminator('{pn}DiscriminatorsJetTags:BvsAll')", float, doc="PNet b vs all (|eta| < 2.5)", precision=10),
        btagPNetTauVJet=Var(f"bDiscriminator('{pn}DiscriminatorsJetTags:TauVsJet')", float, doc="PNet tau vs jet", precision=10),
        PNetRegPtRawCorr=Var(f"bDiscriminator('{pn}JetTags:ptcorr')", float, doc="PNet pt regression (on raw pt)", precision=10),
        btagUParTAK4B=Var(f"bDiscriminator('{up}DiscriminatorsJetTags:BvsAll')", float, doc="UParT b vs all", precision=10),
        btagUParTAK4TauVJet=Var(f"bDiscriminator('{up}DiscriminatorsJetTags:TauVsJet')", float, doc="UParT tau vs jet", precision=10),
        UParTAK4RegPtRawCorr=Var(f"bDiscriminator('{up}JetTags:ptcorr')", float, doc="UParT pt regression (on raw pt)", precision=10),
    )
    t["offAK4PuppiJetTable"] = _table("SimplePATJetFlatTableProducer", "slimmedJetsPuppi", "offAK4PuppiJet",
        "offline AK4 PUPPI jets (slimmedJetsPuppi), MINIAOD JECs", "pt > 15", jet)

    ak8 = cms.PSet(P4Vars,
        rawFactor=Var("1.-jecFactor('Uncorrected')", float, doc="1 - (raw pt / pt)", precision=6),
        msoftdrop=Var("userFloat('ak8PFJetsPuppiSoftDropMass')", float, doc="soft-drop mass", precision=10),
        tau1=Var("userFloat('NjettinessAK8Puppi:tau1')", float, precision=10),
        tau2=Var("userFloat('NjettinessAK8Puppi:tau2')", float, precision=10),
        tau3=Var("userFloat('NjettinessAK8Puppi:tau3')", float, precision=10),
        nConstituents=Var("numberOfDaughters()", "uint8"),
        PNetXbbVsQCD=Var("bDiscriminator('pfMassDecorrelatedParticleNetDiscriminatorsJetTags:XbbvsQCD')", float,
                         doc="mass-decorrelated PNet Xbb vs QCD", precision=10),
        PNetHbbVsQCD=Var("bDiscriminator('pfParticleNetFromMiniAODAK8DiscriminatorsJetTags:HbbvsQCD')", float,
                         doc="PNet (from MINIAOD) Hbb vs QCD", precision=10),
    )
    t["offAK8PuppiJetTable"] = _table("SimplePATJetFlatTableProducer", "slimmedJetsAK8", "offAK8PuppiJet",
        "offline AK8 PUPPI jets (slimmedJetsAK8)", "pt > 100", ak8)

    t["offPuppiMETTable"] = _table("SimplePATMETFlatTableProducer", "slimmedMETsPuppi", "offPuppiMET",
        "offline PUPPI MET (slimmedMETsPuppi, type-1)", "", cms.PSet(
            pt=Var("pt", float, precision=10), phi=Var("phi", float, precision=10),
            sumEt=Var("sumEt", float, precision=10),
            rawPt=Var("uncorPt", float, doc="raw PUPPI MET", precision=10),
            rawPhi=Var("uncorPhi", float, doc="raw PUPPI MET phi", precision=10)), singleton=True)

    t["offPVTable"] = _table("SimpleVertexFlatTableProducer", "offlineSlimmedPrimaryVertices", "offPV",
        "leading offline primary vertex (offlineSlimmedPrimaryVertices[0])", "", cms.PSet(
            x=Var("x", float, precision=10), y=Var("y", float, precision=10), z=Var("z", float, precision=16),
            ndof=Var("ndof", float, precision=8), chi2=Var("normalizedChi2", float, precision=8)), maxLen=1)

    task = cms.Task()
    for label, mod in t.items():
        setattr(process, label, mod)
        task.add(mod)
    process.offlineNanoTablesTask = task
    getattr(process, path).associate(process.offlineNanoTablesTask)
    return process
