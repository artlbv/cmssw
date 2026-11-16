#!/bin/bash
# Test of hltMenuGraph: build the graph page of the Phase-2 menu and check its content.

function die {
  printf "\n%s: status %s\n" "$1" "$2"
  if [ $# -gt 2 ]; then
    printf "%s\n" "=== Log File =========="
    cat $3
    printf "%s\n" "=== End of Log File ==="
  fi
  exit $2
}

rm -f test_hltMenuGraph.html test_hltMenuGraph.json test_hltMenuGraph.log

hltMenuGraph HLTrigger.Configuration.HLT_75e33_cff \
  --era Phase2C22I13M9 --procModifiers alpaka \
  -o test_hltMenuGraph.html --json test_hltMenuGraph.json &> test_hltMenuGraph.log \
  || die 'Failure running hltMenuGraph' $? test_hltMenuGraph.log

python3 - <<'@EOF' || die 'Failure checking the output of hltMenuGraph' $? test_hltMenuGraph.log
import json, sys
data = json.load(open("test_hltMenuGraph.json"))
page = open("test_hltMenuGraph.html").read()
mods = {m["id"]: m for m in data["modules"]}
errors = []
if len(mods) < 400: errors.append("only %d modules" % len(mods))
if len(data["paths"]) < 30: errors.append("only %d paths" % len(data["paths"]))
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
