"""Extra HLT nano content for the v2 Phase-2 L1+HLT nano (CMSSW_17_0_0_pre6 + cms-sw/cmssw#52124), ML@L1 hackathon 2026.

    from L1TMLHackathon.HLTNanoExtras.customiseP2NanoV2 import customiseP2NanoV2
    process = customiseP2NanoV2(process)

Adds to the HLT nano path (all module labels end in "Table", as the NANOAODSIM keep pattern requires):
  hltGeneralTrack (ext)   IP w.r.t. the leading hltOfflinePrimaryVertex with errors; dxy/dz/pT errors, chi2/ndof, lost
                          inner hits, valid / strip hits, algo, highPurity, px/py/pz
  hltPFCandidate (ext)    trackIdx (int32, collection-checked), PUPPI weight, PV association (index, quality)
  hltAK4PuppiJetPFCand    jet -> constituent links (jetIdx, pfCandIdx)
  hltEgUnseeded/L1Seeded  every variable the Phase-2 Ele/Photon filters cut on, per egamma candidate, plus rho
  hltMuonCand             L3 muon candidates with the IsoMu24 isolations (ECAL, HCAL, HGCAL total/em/had, tracker)
  TrigObj                 trigger objects of the last filter of each HLT path, one bool column per path (from master)
  hltGsfTrack{L1Seeded,Unseeded}  GSF tracks (from master)
  hltAK4PuppiJet (ext)    jecFactor, hadron/parton flavour, nB/nC hadrons, genJetIdx; DeepCSV_prob_b/c/udsg
  hltAK4PuppiJetParT{Cpf,SV}  the HLT ParT AK4 input features from its tag infos (first 50 constituents / 5 SVs per
                          jet, full float), plus hltAK4PuppiJet_ParT_{inputFilled,nCpf,nSV,jet_pt,jet_eta,jet_phi,jet_energy}
  hltPFPuppiMETRaw, hltRho, hltBeamSpot   raw PUPPI MET; JEC and egamma rho; HLT online beam spot
  Generator, genWeight, LHE/PS weights, GenFilter (lumi)   standard MC NanoAOD generator info (+ Generator_qScale)
The secondary vertices now come from hltVertexTable (master HLTVertexTableProducer, doSVs) with dlen, dxy, their
significances and the pointing angle; the separate hltSecondaryVertexTable is removed in HLTNanoProducer_cff.
Every producer the HLT nano tables read, and everything upstream of it, runs in every event, as DST_PFScouting of the
NGTScouting menu does: for each HLT path holding such a module, a path "NanoAllEvents_<path>" with the HLT path's modules up
to the last needed one is scheduled before the nano paths, so the tables are filled in
every event, not only where an HLT path got that far (v2 test: ParT ran in 42/200 tt events, muon isolations for 61% of
the candidates). EDFilters in that chain are wrapped in cms.ignore (they run and make their products, but cannot stop the
path); modules run once per event, so nothing an HLT path already ran is recomputed and the HLT decisions are unchanged.
The HPS tau / DeepTau chain is left out (obsolete; hltHpsPFTau is filled only where its paths ran).
The ECAL barrel TP table is zero-suppressed (encodedEt > 0, 8.7% of the 61,200 crystals in HH).
"""
import FWCore.ParameterSet.Config as cms

# variables of the Phase-2 egamma filters: (column, module base name, instance); module = base + Unseeded / L1Seeded
EG_VARS = [
    ("sigmaIEtaIEta5x5", "hltEgammaClusterShape", "sigmaIEtaIEta5x5"),
    ("sigma2uu", "hltEgammaHGCALIDVars", "sigma2uu"),
    ("sigma2vv", "hltEgammaHGCALIDVars", "sigma2vv"),
    ("sigma2ww", "hltEgammaHGCALIDVars", "sigma2ww"),
    ("hgcalRVar", "hltEgammaHGCALIDVars", "rVar"),
    ("hgcalHForHOverE", "hltEgammaHGCALIDVars", "hForHOverE"),
    ("hOverE", "hltEgammaHoverE", ""),
    ("ecalPFClusterIso", "hltEgammaEcalPFClusterIso", ""),
    ("hcalPFClusterIso", "hltEgammaHcalPFClusterIso", ""),
    ("hgcalLayerClusterIso", "hltEgammaHGCalLayerClusterIso", ""),
    ("pixelMatchS2", "hltEgammaPixelMatchVars", "s2"),
    ("gsfDEtaSeed", "hltEgammaGsfTrackVars", "DetaSeed"),
    ("gsfDEta", "hltEgammaGsfTrackVars", "Deta"),
    ("gsfDPhi", "hltEgammaGsfTrackVars", "Dphi"),
    ("gsfOneOESuperMinusOneOP", "hltEgammaGsfTrackVars", "OneOESuperMinusOneOP"),
    ("gsfMissingHits", "hltEgammaGsfTrackVars", "MissingHits"),
    ("gsfValidHits", "hltEgammaGsfTrackVars", "ValidHits"),
    ("bestGsfNLayerIT", "hltEgammaBestGsfTrackVars", "NLayerIT"),
    ("bestGsfChi2", "hltEgammaBestGsfTrackVars", "Chi2"),
    ("bestGsfDEtaSeed", "hltEgammaBestGsfTrackVars", "DetaSeed"),
    ("bestGsfDPhi", "hltEgammaBestGsfTrackVars", "Dphi"),
    ("l1TrkIso", "hltEgammaEleL1TrkIso", ""),
    ("gsfTrackIso", "hltEgammaEleGsfTrackIso", ""),
]

MU_ISO = "hltPhase2L3Muons"
MU_FLOAT_MAPS = [
    ("ecalPFClusterIso", MU_ISO + "EcalIsodR0p3dRVeto0p000", ""),
    ("hcalPFClusterIso", MU_ISO + "HcalIsodR0p3dRVeto0p000", ""),
    ("hgcalLayerClusterIso", MU_ISO + "HgcalLCIsodR0p2dRVetoEM0p00dRVetoHad0p02minEEM0p00minEHad0p00", ""),
    ("hgcalLayerClusterIsoEM", MU_ISO + "HgcalLCIsodR0p2dRVetoEM0p00dRVetoHad0p02minEEM0p00minEHad0p00", "em"),
    ("hgcalLayerClusterIsoHad", MU_ISO + "HgcalLCIsodR0p2dRVetoEM0p00dRVetoHad0p02minEEM0p00minEHad0p00", "had"),
]
MU_DOUBLE_MAPS = [
    ("trkRelIso", MU_ISO + "TrkIsoRegionalNewdR0p3dRVeto0p005dz0p25dr0p20ChisqInfPtMin0p0Cut0p07",
     "combinedRelativeIsoDeposits"),
]


# tables whose inputs are NOT forced to run in every event
NOT_FORCED = {"hltTauTable", "hltTauExtTable"}  # HPS taus + DeepTau


def _consumed(pset):
    """Module labels of every InputTag in a module's parameters (ESInputTags skipped)."""
    for nm in pset.parameterNames_():
        p = getattr(pset, nm)
        t = p.configTypeName()
        if "ESInputTag" in t:
            continue
        if t.endswith("VInputTag"):
            for x in p:
                yield x.getModuleLabel() if hasattr(x, "getModuleLabel") else str(x).split(":")[0]
        elif t.endswith("InputTag"):
            yield p.getModuleLabel()
        elif t.endswith("VPSet"):
            for q in p:
                yield from _consumed(q)
        elif t.endswith("PSet"):
            yield from _consumed(p)


def _allEventsReco(process, tables):
    """Paths that run every HLT-path producer upstream of the given table modules in every event (filters ignored)."""
    mods = dict(process.producers_())
    filt = dict(process.filters_())
    order, state = [], {}

    def visit(l):
        if state.get(l) == 2:
            return
        if state.get(l) == 1:
            raise RuntimeError("dependency cycle at " + l)
        state[l] = 1
        for u in set(_consumed(mods.get(l) or filt[l])):
            if u != l and (u in mods or u in filt):
                visit(u)
        state[l] = 2
        order.append(l)

    tableSet = set(tables)
    for t in tables:
        for u in set(_consumed(getattr(process, t))):
            if u in tableSet or u not in mods and u not in filt:
                continue
            visit(u)
    # One copy per HLT path that holds a needed module: the path up to its last needed module, with every EDFilter
    # wrapped in cms.ignore. A prefix of a valid path keeps its order and all its dependencies, including ones that are
    # not InputTags (bunchSpacingProducer, GEM rec hits for the global muons), so the framework's path-consistency checks
    # hold; merging modules of several paths into one path does not. Copies that add no new module are skipped.
    class _Collect:
        def __init__(self):
            self.labels = []

        def enter(self, v):
            if isinstance(v, (cms.EDProducer, cms.EDFilter)):
                self.labels.append(v.label_())

        def leave(self, v):
            pass

    need = set(order) - tableSet
    covered, newPaths = set(), []
    for p in [p for p in process.schedule if isinstance(p, cms.Path)
              and p.label_().startswith(("HLT_", "MC_", "DQM_", "L1T_"))]:
        c = _Collect()
        p.visit(c)
        last = max((i for i, l in enumerate(c.labels) if l in need), default=-1)
        prefix = list(dict.fromkeys(c.labels[:last + 1]))
        if last < 0 or not (set(prefix) & need) - covered:
            continue
        covered |= set(prefix)
        seq = cms.Sequence()
        for l in prefix:
            m = getattr(process, l)
            seq += cms.ignore(m) if l in filt else m
        label = "NanoAllEvents_" + p.label_()
        setattr(process, label, cms.Path(seq))
        newPaths.append(label)
    return newPaths, sorted(need - covered)


def _vpset(entries):
    return cms.VPSet(*[cms.PSet(name=cms.string(n), src=cms.InputTag(m, i)) for n, m, i in entries])


def customiseP2NanoV2(process):
    from HLTrigger.NGTScouting.hltTriggerObjects_cff import hltTriggerObjP4Table
    from HLTrigger.NGTScouting.hltGsfTracks_cfi import hltGsfTracksL1SeededTable, hltGsfTracksUnseededTable

    process.hltGeneralTrackPVExtTable = cms.EDProducer("HLTTrackPVExtTableProducer",
        tracks=cms.InputTag("hltGeneralTracks"), vertices=cms.InputTag("hltOfflinePrimaryVertices"),
        name=cms.string("hltGeneralTrack"), precision=cms.int32(10))

    process.hltPFCandidateExtTable = cms.EDProducer("HLTPFCandidateExtTableProducer",
        candidates=cms.InputTag("hltParticleFlowTmp"), tracks=cms.InputTag("hltGeneralTracks"),
        puppiWeights=cms.InputTag("hltPFPuppi"), vertexAssociation=cms.InputTag("hltPrimaryVertexAssociation", "original"),
        name=cms.string("hltPFCandidate"))

    process.hltJetConstituentTable = cms.EDProducer("HLTJetConstituentTableProducer",
        name=cms.string("hltAK4PuppiJetPFCand"), candIdxName=cms.string("pfCandIdx"),
        candIdxDoc=cms.string("Index in the hltPFCandidate table (-1: not in that collection)"),
        jets=cms.InputTag("hltAK4PFPuppiJets"), candidates=cms.InputTag("hltParticleFlowTmp"),
        jetCut=cms.string(""), jetConstCut=cms.string(""), skipNonExistingSrc=cms.bool(True))

    for seed in ("Unseeded", "L1Seeded"):
        setattr(process, f"hltEg{seed}Table", cms.EDProducer("HLTEgammaVarMapTableProducer",
            src=cms.InputTag(f"hltEgammaCandidates{seed}"), name=cms.string(f"hltEg{seed}"),
            doc=cms.string(f"HLT egamma candidates ({seed}) with the variables of the Phase-2 egamma filters"),
            precision=cms.int32(12),
            floatMaps=_vpset([(n, m + seed, i) for n, m, i in EG_VARS]), doubleMaps=cms.VPSet(),
            rho=cms.InputTag("hltFixedGridRhoFastjetAllCaloForEGamma")))

    process.hltMuonCandTable = cms.EDProducer("HLTMuonVarMapTableProducer",
        src=cms.InputTag("hltPhase2L3MuonCandidates"), name=cms.string("hltMuonCand"),
        doc=cms.string("HLT L3 muon candidates with the HLT_IsoMu24_FromL1TkMuon isolations"), precision=cms.int32(12),
        floatMaps=_vpset(MU_FLOAT_MAPS), doubleMaps=_vpset(MU_DOUBLE_MAPS),
        rho=cms.InputTag(""))

    process.hltTriggerObjP4Table = hltTriggerObjP4Table.clone(
        triggerEvent=cms.InputTag("hltTriggerSummaryAOD", "", process.name_()))
    process.hltGsfTracksL1SeededTable = hltGsfTracksL1SeededTable.clone()
    process.hltGsfTracksUnseededTable = hltGsfTracksUnseededTable.clone()

    # (1) HLT JEC factor, (4) HLT jet flavour and gen-jet index: one extension table on hltAK4PuppiJet.
    #     Flavour: JetFlavourClustering on the PUPPI jets (PUPPI weights for the reclustering), with the B/C hadrons and
    #     partons already selected for the gen-jet flavour table; gen-jet index into the GenJet table (slimmedGenJets,
    #     pt > 10, as genJetTable).
    from PhysicsTools.JetMCAlgos.AK4PFJetsMCFlavourInfos_cfi import ak4JetFlavourInfos
    _had = "selectedHadronsAndPartonsForGenJetsFlavourInfos"
    process.hltAK4PuppiJetFlavourInfos = ak4JetFlavourInfos.clone(
        jets="hltAK4PFPuppiJets", weights=cms.InputTag("hltPFPuppi"),
        bHadrons=cms.InputTag(_had, "bHadrons"), cHadrons=cms.InputTag(_had, "cHadrons"),
        partons=cms.InputTag(_had, "physicsPartons"), leptons=cms.InputTag(_had, "leptons"))
    process.hltJetExtTable = cms.EDProducer("HLTJetExtTableProducer",
        jets=cms.InputTag("hltAK4PFPuppiJets"), corrector=cms.InputTag("hltAK4PFPuppiJetCorrector"),
        flavourInfos=cms.InputTag("hltAK4PuppiJetFlavourInfos"), genJets=cms.InputTag("slimmedGenJets"),
        genJetCut=cms.string("pt > 10"), maxDR=cms.double(0.4), name=cms.string("hltAK4PuppiJet"))

    # (2) MET: the fixed hltSums_cfi (TypeOne PUPPI MET with pt/phi/px/py/sumEt; v1 stored sumEt as "pt") plus the raw
    #     PUPPI MET with the same variables.
    process.hltPFPuppiMETRawTable = process.METTable.clone(src="hltPFPuppiMET", name="hltPFPuppiMETRaw",
                                                           doc="HLT PUPPI MET, raw (no Type-1 correction)")

    # (8) event-level: rho of the JEC (L1FastJet) and of the egamma isolation, the HLT beam spot
    from PhysicsTools.NanoAOD.globalVariablesTableProducer_cfi import globalVariablesTableProducer
    from PhysicsTools.NanoAOD.common_cff import ExtVar
    process.hltRhoTable = globalVariablesTableProducer.clone(
        name=cms.string("hltRho"),
        variables=cms.PSet(
            fixedGridRhoFastjetAll=ExtVar(cms.InputTag("hltFixedGridRhoFastjetAll"), "double",
                                          doc="rho used by the HLT AK4 PUPPI JEC (L1FastJet)"),
            fixedGridRhoFastjetAllCaloForEGamma=ExtVar(cms.InputTag("hltFixedGridRhoFastjetAllCaloForEGamma"), "double",
                                                       doc="rho of the egamma isolation filters"),
        ))
    from PhysicsTools.NanoAOD.globals_cff import beamSpotTable
    process.hltBeamSpotTable = beamSpotTable.clone(src="hltOnlineBeamSpot", name="hltBeamSpot",
                                                   doc="HLT online beam spot")

    # (9) the HLT ParT AK4 tagger's input features, read from its tag infos (exactly what the ONNX model is fed), so
    #     that the stored ParT scores can be reproduced and the tagger retrained on the nano:
    #     hltAK4PuppiJetParTCpf (first 50 constituents per jet, 28 features), hltAK4PuppiJetParTSV (first 5 SVs per
    #     jet, 16 features), and hltAK4PuppiJet_ParT_{inputFilled,nCpf,nSV,jet_pt,jet_eta,jet_phi,jet_energy}.
    process.hltParTFeatureTable = cms.EDProducer("HLTParTFeatureTableProducer",
        tagInfos=cms.InputTag("hltParticleTransformerAK4TagInfos"), name=cms.string("hltAK4PuppiJetParT"),
        jetName=cms.string("hltAK4PuppiJet"), maxCpf=cms.uint32(50), maxSV=cms.uint32(5), precision=cms.int32(-1))

    # (10) generator info, as in standard MC NanoAOD, for pT-hat stitching and weights: Generator_* (binvar = the
    #      generator binning value, pT-hat for binned pythia samples, -1 if none; qScale = pythia hard scale, = pT-hat
    #      for 2->2 QCD; weight; PDF x/id/scale), genWeight, and the LHE/PS weights when present (~0.3 kB/ev);
    #      GenFilter_* per luminosity block (generator filter efficiency, for normalising filtered samples).
    from PhysicsTools.NanoAOD.globals_cff import genTable as _genTable, genFilterTable as _genFilterTable
    from PhysicsTools.NanoAOD.genWeightsTable_cfi import genWeightsTable as _genWeightsTable
    from PhysicsTools.NanoAOD.common_cff import Var
    process.generatorTable = _genTable.clone()
    process.generatorTable.variables.qScale = Var("qScale()", float, doc="generator hard-process scale (pythia: pT-hat)",
                                                  precision=14)
    process.genWeightsTable = _genWeightsTable.clone()
    process.genFilterTable = _genFilterTable.clone()

    process.hltNanoExtraTables = cms.Sequence(
        process.hltGeneralTrackPVExtTable + process.hltPFCandidateExtTable + process.hltJetConstituentTable
        + process.hltEgUnseededTable + process.hltEgL1SeededTable + process.hltMuonCandTable
        + process.hltTriggerObjP4Table + process.hltGsfTracksL1SeededTable + process.hltGsfTracksUnseededTable
        + process.hltAK4PuppiJetFlavourInfos + process.hltJetExtTable + process.hltPFPuppiMETRawTable
        + process.hltRhoTable + process.hltBeamSpotTable + process.hltParTFeatureTable
        + process.generatorTable + process.genWeightsTable + process.genFilterTable)
    process.nanoAOD_step0 += process.hltNanoExtraTables
    # DeepCSV, as cut on by the DeepCSV b-tag paths (probb includes bb), next to the stored DeepFlavour and ParT scores
    from PhysicsTools.NanoAOD.common_cff import ExtVar as _EV
    for o in ("probb", "probc", "probudsg"):
        setattr(process.hltJetTable.externalVariables, "DeepCSV_" + o.replace("prob", "prob_"),
                _EV(cms.InputTag("hltDeepCombinedSecondaryVertexBJetTagsPFPuppi", o), float,
                    doc="DeepCSV " + o + (" (b + bb)" if o == "probb" else ""), precision=10))
    # run everything the HLT nano tables read in every event (see the module docstring)
    tables = [m for m in process.nanoAOD_step0.moduleNames() if m.endswith("Table") or m.endswith("Tables")]
    tables = [m for m in tables if m not in NOT_FORCED and hasattr(process, m)]
    _paths, _notOnPath = _allEventsReco(process, tables)
    _at = list(process.schedule).index(process.nanoAOD_step0)
    for k, l in enumerate(_paths):
        process.schedule.insert(_at + k, getattr(process, l))

    # (5) generator vertex: GenPart production vertex (as in CMSSW master's HLT nano) and the event's gen origin
    #     (GenVtx, from the TPNano tables below)
    process.genParticleTable.variables.vx = cms.PSet(process.genParticleTable.variables.pt.clone(
        expr="vx", doc="x coordinate of the production vertex (cm)", precision=10))
    process.genParticleTable.variables.vy = cms.PSet(process.genParticleTable.variables.pt.clone(
        expr="vy", doc="y coordinate of the production vertex (cm)", precision=10))
    process.genParticleTable.variables.vz = cms.PSet(process.genParticleTable.variables.pt.clone(
        expr="vz", doc="z coordinate of the production vertex (cm)", precision=16))

    # (6) L1 trigger-primitive inputs (EmyrClement/cmssw TPNano, commit 701f63da26, copied into
    #     DPGAnalysis/Phase2L1TNanoAOD): L1 TTTracks, ECAL barrel / HCAL / HF TPs, HGCal L1 clusters and towers, L1
    #     vertices, GenVtx. Attached to the L1 nano path.
    process.load("DPGAnalysis.Phase2L1TNanoAOD.tpNanotables_cff")
    process.nanoAOD_step1.associate(process.tpTablesTask)
    process.ecalEBTable.cut = cms.string("encodedEt() > 0")  # zero suppression: 40 -> ~4 kB/event
    return process
