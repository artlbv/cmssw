# hltMenuGraph

`hltMenuGraph` turns an HLT menu into a single interactive HTML page showing which
module produces what and which module consumes it. The page has three views:

- **Modules**: every scheduled module and the products it reads, grouped by
  subsystem, CMSSW package or sequence. You can pick one path, search for a module,
  and trace its full upstream and downstream chain.
- **Paths & shared blocks**: the top-level sequences used by two or more paths,
  laid out in dataflow order, with the paths that run them in the last column.
  Path filters and sequences used by only one path are folded into the path.
- **Path × block matrix**: for every path, how many modules it runs from each
  shared block.

The data is embedded in the page. The page loads `cytoscape` and `elkjs` from public
CDNs (cdnjs, jsDelivr) and the IBM Plex fonts from Google Fonts, so it needs network
access when opened.

## Usage

Inside a CMSSW area, after `cmsenv` and `scram b`:

```bash
# Phase-2 menu, with the era and process modifiers of the Phase-2 HLT workflows
hltMenuGraph HLTrigger.Configuration.HLT_75e33_cff --era Phase2C22I13M9 --procModifiers alpaka -o HLT_75e33.html

# a menu fragment given as a file
hltMenuGraph HLTrigger/Configuration/python/HLT_75e33_cff.py --era Phase2C22I13M9 -o HLT_75e33.html

# a full configuration (defining `process`), e.g. a Run-3 menu from ConfDB
hltGetConfiguration /dev/CMSSW_X_Y_0/GRun --full --offline --unprescale > hlt.py
hltMenuGraph hlt.py -o GRun.html

# or from stdin
hltGetConfiguration /dev/CMSSW_X_Y_0/GRun --full --offline --unprescale | hltMenuGraph - -o GRun.html
```

Then open the HTML file in a browser.

### Options

| Option | Meaning |
| --- | --- |
| `menu` | Menu fragment as a module name or file, a full configuration file, or `-` for stdin |
| `-o, --output` | Output HTML file (default `<menu>_graph.html`) |
| `--json FILE` | Also write the extracted data as JSON |
| `--era` | Era(s) applied when building the process around a menu fragment, comma separated |
| `--procModifiers` | Process modifiers for a menu fragment, comma separated |
| `--process-name` | Name of the process built around a menu fragment (default `HLTX`) |
| `--title` | Page title (default `<menu> Dataflow`) |
| `--template` | Alternative HTML template |
| `--src DIR` | Source directory to scan for plugin packages; repeatable. Default: `$CMSSW_BASE/src`, then the release `src` |
| `--checkout DIR` | Run without `cmsenv`, importing the python packages of a plain CMSSW checkout |
| `--stub-missing-cfi` | Replace missing generated `*_cfi` modules by empty EDProducers (for `--checkout`) |

The era and process modifiers only apply to menu fragments. A full configuration
keeps the era it was written with.

### Without a CMSSW release

For a quick look from a plain checkout, without `cmsenv`:

```bash
python3 HLTrigger/Configuration/scripts/hltMenuGraph HLTrigger.Configuration.HLT_75e33_cff \
  --checkout . --stub-missing-cfi -o HLT_75e33.html
```

The cfi files generated from `fillDescriptions` at build time do not exist in a
plain checkout. `--stub-missing-cfi` replaces them with empty modules, which is fine
when the menu only uses them as templates for `clone()`. The stubbed modules are
listed on stderr and in the page header.

## What the graph shows, and its limits

- An edge A → B means that a parameter of B names A: an `InputTag`, an entry of a
  `VInputTag`, or a plain string equal to a module label (drawn dotted). Parameters
  inside nested `PSet`/`VPSet` are included.
- Only the modules on scheduled paths and end-paths are shown. Without a schedule,
  all paths and end-paths are used.
- Labels that no module of the menu produces become **external inputs**, as does
  anything read with `@skipCurrentProcess`. Placeholders such as `NotUsed` and
  event-setup labels are ignored.
- Products read through labels hard-coded in C++ are not visible. Parameters that the
  C++ code ignores still produce edges, so some external inputs can be leftovers in
  the configuration.
- The C++ package of each plugin comes from scanning the `DEFINE_*_MODULE` macros in
  the source directories. In a local area the local packages take precedence over the
  release.
- Modules marked as Alpaka (`@alpaka` or an explicit `alpaka_*` backend) get a dashed
  border.

## Subsystems

Modules are assigned to subsystems (L1T seeding, tracking, calorimetry, PF, jets/MET,
E/gamma, muons, taus, bookkeeping) from their labels. The rules are in
[`python/Tools/menuGraphRules.py`](python/Tools/menuGraphRules.py): each rule is a list
of regular expressions, and the first matching rule wins. Modules that match no rule
go to *Unclassified* and are listed on stderr, so the rules can be extended for new
menus. The `ext` and `infra` subsystem ids are used by the page and must be kept.

## Files

| File | Content |
| --- | --- |
| `scripts/hltMenuGraph` | Command-line tool |
| `python/Tools/menuGraph.py` | Menu loading, graph extraction, package lookup, rendering |
| `python/Tools/menuGraphRules.py` | Subsystem definitions and label rules |
| `data/hltMenuGraph.html` | Page template; the script fills the title, header, and data placeholders |
| `test/test_hltMenuGraph.sh` | Unit test: builds the page of `HLT_75e33` and checks its content |

Run the unit test with:

```bash
scram b runtests_test_hltMenuGraph
```
