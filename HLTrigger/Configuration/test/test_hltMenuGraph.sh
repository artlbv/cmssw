#!/bin/bash
# Test of hltMenuGraph: build the graph pages of the Phase-2 HLT menu and of the Phase-2 L1T
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

rm -f test_hltMenuGraph*.html test_hltMenuGraph*.json test_hltMenuGraph*.log

hltMenuGraph HLTrigger.Configuration.HLT_75e33_cff \
  --era Phase2C22I13M9 --procModifiers alpaka \
  -o test_hltMenuGraph.html --json test_hltMenuGraph.json &> test_hltMenuGraph.log \
  || die 'Failure running hltMenuGraph' $? test_hltMenuGraph.log

cat > test_hltMenuGraph_check.py <<'@EOF'
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

python3 test_hltMenuGraph_check.py test_hltMenuGraph 400 30 \
  || die 'Failure checking the output of hltMenuGraph (HLT_75e33)' $? test_hltMenuGraph.log

###
### L1 profile: Phase-2 L1T emulation with the default P2GT menu
###
hltMenuGraph --profile l1 --era Phase2C22I13M9 \
  -o test_hltMenuGraph_L1.html --json test_hltMenuGraph_L1.json &> test_hltMenuGraph_L1.log \
  || die 'Failure running hltMenuGraph --profile l1' $? test_hltMenuGraph_L1.log

python3 test_hltMenuGraph_check.py test_hltMenuGraph_L1 150 10 \
  || die 'Failure checking the output of hltMenuGraph --profile l1' $? test_hltMenuGraph_L1.log

python3 - <<'@EOF' || die 'Failure checking the P2GT path decisions' $? test_hltMenuGraph_L1.log
import json, sys
data = json.load(open("test_hltMenuGraph_L1.json"))
decisions = [e for e in data["edges"] if e["kind"] == "pathDecision" and e["target"] == "l1tGTAlgoBlockProducer"]
print("%d path decisions read by l1tGTAlgoBlockProducer" % len(decisions))
sys.exit(0 if len(decisions) >= 10 else 1)
@EOF
