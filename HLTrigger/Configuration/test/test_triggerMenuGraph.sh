#!/bin/bash
# Test of triggerMenuGraph: build the graph pages of the Phase-2 HLT menu and of the Phase-2 L1T
# emulation (L1 profile), and check their content.

function die {
  printf "\n%s: status %s\n" "$1" "$2"
  if [ $# -gt 2 ]; then
    printf "%s\n" "=== Log File =========="
    cat $3
    printf "%s\n" "=== End of Log File ==="
  fi
  exit $2
}

rm -f test_triggerMenuGraph*.html test_triggerMenuGraph*.json test_triggerMenuGraph*.log test_triggerMenuGraph*.txt test_triggerMenuGraph*_cfg.py

triggerMenuGraph HLTrigger.Configuration.HLT_75e33_cff \
  --era Phase2C26I13M9 --procModifiers alpaka \
  -o test_triggerMenuGraph.html --json test_triggerMenuGraph.json &> test_triggerMenuGraph.log \
  || die 'Failure running triggerMenuGraph' $? test_triggerMenuGraph.log

cat > test_triggerMenuGraph_check.py <<'@EOF'
import json, sys
prefix, min_modules, min_paths = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
data = json.load(open(prefix + ".json"))
page = open(prefix + ".html").read()
mods = {m["id"]: m for m in data["modules"]}
errors = []
if len(mods) < min_modules: errors.append("only %d modules" % len(mods))
if len(data["paths"]) < min_paths: errors.append("only %d paths" % len(data["paths"]))
for e in data["edges"]:
    if e["kind"] == "pathDecision" and e["path"] not in data["paths"]: errors.append("decision of unknown path %s" % e["path"])
unclassified = [m["id"] for m in data["modules"] if m["subsystem"] == "other"]
if unclassified: errors.append("unclassified modules: %s" % " ".join(unclassified))
for p, labels in data["paths"].items():
    missing = [l for l in labels if l not in mods]
    if missing: errors.append("path %s lists unknown modules %s" % (p, missing))
for e in data["edges"]:
    if e["target"] not in mods: errors.append("edge to unknown module %s" % e["target"])
    if not e["external"] and e["source"] not in mods: errors.append("internal edge from unknown module %s" % e["source"])
if "@@" in page: errors.append("unfilled placeholder in the HTML page")
if "const D = {" not in page: errors.append("data not embedded in the HTML page")
for e in errors: print("ERROR:", e)
print("%d modules, %d edges, %d paths" % (len(mods), len(data["edges"]), len(data["paths"])))
sys.exit(1 if errors else 0)
@EOF

python3 test_triggerMenuGraph_check.py test_triggerMenuGraph 400 30 \
  || die 'Failure checking the output of triggerMenuGraph (HLT_75e33)' $? test_triggerMenuGraph.log

###
### L1 profile: Phase-2 L1T emulation with the default P2GT menu
###
triggerMenuGraph --profile l1 --era Phase2C26I13M9 \
  -o test_triggerMenuGraph_L1.html --json test_triggerMenuGraph_L1.json &> test_triggerMenuGraph_L1.log \
  || die 'Failure running triggerMenuGraph --profile l1' $? test_triggerMenuGraph_L1.log

python3 test_triggerMenuGraph_check.py test_triggerMenuGraph_L1 150 10 \
  || die 'Failure checking the output of triggerMenuGraph --profile l1' $? test_triggerMenuGraph_L1.log

python3 - <<'@EOF' || die 'Failure checking the P2GT path decisions' $? test_triggerMenuGraph_L1.log
import json, sys
data = json.load(open("test_triggerMenuGraph_L1.json"))
decisions = [e for e in data["edges"] if e["kind"] == "pathDecision" and e["target"] == "l1tGTAlgoBlockProducer"]
print("%d path decisions read by l1tGTAlgoBlockProducer" % len(decisions))
sys.exit(0 if len(decisions) >= 10 else 1)
@EOF

###
### --diff, lint and --strict on a small configuration
###
cat > test_triggerMenuGraph_base_cfg.py <<'@EOF'
import FWCore.ParameterSet.Config as cms
process = cms.Process("TEST")
process.hltPixelClustersA = cms.EDProducer("SiPixelClusterProducer", src = cms.InputTag("rawDataCollector"))
process.hltPixelTracksA = cms.EDProducer("PixelTrackProducer", clusters = cms.InputTag("hltPixelClustersA"))
process.hltPixelTrackFilterA = cms.EDFilter("HLTPixelTrackFilter", pixelTracks = cms.InputTag("hltPixelTracksA"))
process.p = cms.Path(process.hltPixelClustersA + process.hltPixelTracksA + process.hltPixelTrackFilterA)
@EOF
# the same configuration with a typo in an input label
sed -e 's/InputTag("hltPixelClustersA")/InputTag("hltPixelClusterA")/' \
  test_triggerMenuGraph_base_cfg.py > test_triggerMenuGraph_typo_cfg.py

triggerMenuGraph test_triggerMenuGraph_base_cfg.py -o test_triggerMenuGraph_base.html \
  --json test_triggerMenuGraph_base.json &> test_triggerMenuGraph_base.log \
  || die 'Failure running triggerMenuGraph on the small configuration' $? test_triggerMenuGraph_base.log

# no differences with itself, and --strict passes
triggerMenuGraph test_triggerMenuGraph_base_cfg.py -o test_triggerMenuGraph_self.html \
  --diff test_triggerMenuGraph_base.json --strict &> test_triggerMenuGraph_self.log \
  || die 'Failure running triggerMenuGraph --diff --strict on an unchanged configuration' $? test_triggerMenuGraph_self.log
grep -q "0 modules added, 0 removed, 0 changed, 0 dependencies added, 0 removed" test_triggerMenuGraph_self.log \
  || die 'Unexpected differences between a configuration and itself' 1 test_triggerMenuGraph_self.log

# the typo is a new lint warning: --strict must fail with status 2
triggerMenuGraph test_triggerMenuGraph_typo_cfg.py -o test_triggerMenuGraph_typo.html \
  --diff test_triggerMenuGraph_base.json --strict --report test_triggerMenuGraph_typo.txt &> test_triggerMenuGraph_typo.log
STATUS=$?
[ $STATUS -eq 2 ] || die "triggerMenuGraph --strict should exit with status 2 on a new lint warning (got $STATUS)" 1 test_triggerMenuGraph_typo.log
grep -q "\\[new\\] hltPixelClusterA is read by hltPixelTracksA" test_triggerMenuGraph_typo.txt \
  || die 'The typo is not reported as a new lint warning' 1 test_triggerMenuGraph_typo.txt
grep -q "+ hltPixelClusterA -> hltPixelTracksA" test_triggerMenuGraph_typo.txt \
  || die 'The changed dependency is not in the --diff report' 1 test_triggerMenuGraph_typo.txt
grep -q '"diff"' test_triggerMenuGraph_typo.html \
  || die 'The --diff data is not embedded in the page' 1 test_triggerMenuGraph_typo.log
echo "diff, lint and --strict checks passed"
