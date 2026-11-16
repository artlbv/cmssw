import FWCore.ParameterSet.Config as cms

from ..modules.hltFilteredLayerClustersCLUE3DHigh_cfi import *
from ..modules.hltHgcalDigis_cfi import *
from ..modules.hltHgcalLayerClustersEE_cfi import *
from ..modules.hltHgcalLayerClustersHSci_cfi import *
from ..modules.hltHgcalLayerClustersHSi_cfi import *
from ..modules.hltMergeLayerClusters_cfi import *
from ..modules.hltHGCalRecHit_cfi import *
from ..modules.hltHGCalUncalibRecHit_cfi import *
from ..modules.hltParticleFlowClusterHGCal_cfi import *
from ..modules.hltParticleFlowRecHitHGC_cfi import *
from ..modules.hltParticleFlowSuperClusterHGCal_cfi import *
from ..modules.hltTiclLayerTileProducer_cfi import *
from ..modules.hltTiclSeedingGlobal_cfi import *
from ..modules.hltTiclTrackstersCLUE3DHigh_cfi import *
# Heterogeneous HGCAL EE layer clusters
from ..modules.hltHgcalSoARecHitsProducer_cfi import *
from ..modules.hltHgcalSoARecHitsLayerClustersProducer_cfi import *
from ..modules.hltHgcalSoALayerClustersProducer_cfi import *
from ..modules.hltHgcalLayerClustersFromSoAProducer_cfi import *
# TICL-barrel
from ..modules.hltBarrelLayerClustersEB_cfi import *
from ..modules.hltBarrelLayerClustersHB_cfi import *
from ..modules.hltTiclLayerTileBarrelProducer_cfi import *
from ..modules.hltTiclTrackstersCLUE3DBarrel_cfi import *

HLTHgcalTiclPFClusteringForEgamma = cms.Sequence((hltHgcalDigis+hltHGCalUncalibRecHit+hltHGCalRecHit+hltParticleFlowRecHitHGC+hltHgcalLayerClustersEE+hltHgcalLayerClustersHSci+hltHgcalLayerClustersHSi+hltMergeLayerClusters+hltFilteredLayerClustersCLUE3DHigh+hltTiclSeedingGlobal+hltTiclLayerTileProducer+hltTiclTrackstersCLUE3DHigh+hltParticleFlowClusterHGCal+hltParticleFlowSuperClusterHGCal))

HLTHgcalTiclPFClusteringForEgamma_barrel = cms.Sequence((
  hltHgcalDigis+
  hltHGCalUncalibRecHit+
  hltHGCalRecHit+
  hltParticleFlowRecHitHGC+
  hltHgcalLayerClustersEE+
  hltHgcalLayerClustersHSci+
  hltHgcalLayerClustersHSi+
  hltBarrelLayerClustersEB+
  hltBarrelLayerClustersHB+
  hltMergeLayerClusters+
  hltFilteredLayerClustersCLUE3DHigh+
  hltTiclSeedingGlobal+
  hltTiclLayerTileProducer+
  hltTiclTrackstersCLUE3DHigh+
  hltParticleFlowClusterHGCal+
  hltParticleFlowSuperClusterHGCal+
  hltTiclLayerTileBarrelProducer+
  hltTiclTrackstersCLUE3DBarrel
))

# with alpaka, the EE layer clusters come from the SoA chain (as in HLTTICLLocalRecoSequence),
# and hltMergeLayerClusters reads hltHgCalLayerClustersFromSoAProducer instead of hltHgcalLayerClustersEE
_HLTHgcalTiclPFClusteringForEgamma_heterogeneous = HLTHgcalTiclPFClusteringForEgamma.copy()
_HLTHgcalTiclPFClusteringForEgamma_heterogeneous.replace(hltHgcalLayerClustersEE,
    hltHgcalSoARecHitsProducer+hltHgcalSoARecHitsLayerClustersProducer+hltHgcalSoALayerClustersProducer+hltHgCalLayerClustersFromSoAProducer)
_HLTHgcalTiclPFClusteringForEgamma_heterogeneous_barrel = HLTHgcalTiclPFClusteringForEgamma_barrel.copy()
_HLTHgcalTiclPFClusteringForEgamma_heterogeneous_barrel.replace(hltHgcalLayerClustersEE,
    hltHgcalSoARecHitsProducer+hltHgcalSoARecHitsLayerClustersProducer+hltHgcalSoALayerClustersProducer+hltHgCalLayerClustersFromSoAProducer)

from Configuration.ProcessModifiers.alpaka_cff import alpaka
from Configuration.ProcessModifiers.ticl_barrel_cff import ticl_barrel
(ticl_barrel & (~alpaka)).toReplaceWith(HLTHgcalTiclPFClusteringForEgamma, HLTHgcalTiclPFClusteringForEgamma_barrel)
(alpaka & (~ticl_barrel)).toReplaceWith(HLTHgcalTiclPFClusteringForEgamma, _HLTHgcalTiclPFClusteringForEgamma_heterogeneous)
(alpaka & ticl_barrel).toReplaceWith(HLTHgcalTiclPFClusteringForEgamma, _HLTHgcalTiclPFClusteringForEgamma_heterogeneous_barrel)

