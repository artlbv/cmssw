# triggerMenuGraph

`triggerMenuGraph` turns an HLT menu, or the Phase-2 L1T emulation, into a single
interactive HTML page showing which module produces what and which module consumes it.
The page has three views:

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
triggerMenuGraph HLTrigger.Configuration.HLT_75e33_cff --era Phase2C26I13M9 --procModifiers alpaka -o HLT_75e33.html

# a menu fragment given as a file
triggerMenuGraph HLTrigger/Configuration/python/HLT_75e33_cff.py --era Phase2C26I13M9 -o HLT_75e33.html

# a full configuration (defining `process`), e.g. a Run-3 menu from ConfDB
hltGetConfiguration /dev/CMSSW_X_Y_0/GRun --full --offline --unprescale > hlt.py
triggerMenuGraph hlt.py -o GRun.html

# or from stdin
hltGetConfiguration /dev/CMSSW_X_Y_0/GRun --full --offline --unprescale | triggerMenuGraph - -o GRun.html
```

Then open the HTML file in a browser.

### Phase-2 L1T emulation (L1 profile)

```bash
# the L1 steps of cmsDriver (-s L1TrackTrigger,L1,L1P2GT) with the default P2GT menu
triggerMenuGraph --profile l1 --era Phase2C26I13M9 -o L1T_Phase2.html

# another P2GT menu from L1Trigger/Configuration/python/Phase2GTMenus, or none
triggerMenuGraph --profile l1 --era Phase2C26I13M9 --gt-menu step1_2024_explicitSeeds -o L1T_Phase2.html
triggerMenuGraph --profile l1 --era Phase2C26I13M9 --gt-menu none -o L1T_Phase2_noMenu.html

# any full L1 configuration, e.g. one written by cmsDriver.py --no_exec
triggerMenuGraph --profile l1 step1_L1_cfg.py -o L1T_Phase2.html
```

Without a configuration file, `--profile l1` builds the process itself the way
`cmsDriver.py -s L1TrackTrigger,L1,L1P2GT:<menu>` does: the `L1TrackTrigger_step`,
`L1simulation_step`, `Phase2L1GTProducer` and `Phase2L1GTAlgoBlockProducer` paths, and
one path per seed of the P2GT menu.

The P2GT algorithm block reads the decisions of the menu paths through the
`expression` strings of its `algorithms`. These are drawn as dashed *path decision*
edges from each seed filter into `l1tGTAlgoBlockProducer`. The same applies to any
string parameter that names a scheduled path, e.g. the `ReferencePath` of
`hltTrigReport` in HLT menus.

## Profiles

A profile is a python module with the subsystem definitions and rules, the toolbar
chips and the dashed-border flag. Select it with `--profile`:

| Profile | Module | Subsystems | Dashed border |
| --- | --- | --- | --- |
| `hlt` (default) | `python/Tools/menuGraphRules.py` | L1T seeding, tracking, calorimetry, PF, jets/MET, E/gamma, muons, taus, AlCa & special, bookkeeping | Alpaka modules |
| `l1` | `python/Tools/menuGraphRulesL1.py` | Track Trigger, muon TPs and track finders, HGCal TPG, barrel calo & GCT, GTT, GMT, Correlator, Global Trigger, menu seeds, legacy Run-3, MC truth | Legacy Run-3 emulation |

`--profile` also accepts the name of any python module with the same content, for
custom rules.

The `hlt` rules classify every module of the Phase-2 menu `HLT_75e33` and of the
Run-3 menus `GRun`, `HIon`, `PRef` and `Special` in this release.

### Options

| Option | Meaning |
| --- | --- |
| `menu` | Menu fragment as a module name or file, a full configuration file, or `-` for stdin. Optional with `--profile l1` |
| `--profile` | `hlt` (default), `l1`, or a python module with rules |
| `--gt-menu` | P2GT menu of the built-in L1 process (default `step1_2024`, `none` for no menu) |
| `-o, --output` | Output HTML file (default `<menu>_graph.html`) |
| `--json FILE` | Also write the extracted data as JSON |
| `--era` | Era(s) applied when building the process around a menu fragment, comma separated |
| `--procModifiers` | Process modifiers for a menu fragment, comma separated |
| `--process-name` | Name of the process built around a menu fragment (default `HLTX`, or `L1X` for the built-in L1 process) |
| `--title` | Page title (default from the profile, or `<menu> Dataflow`) |
| `--template` | Alternative HTML template |
| `--src DIR` | Source directory to scan for plugin packages; repeatable. Default: `$CMSSW_BASE/src`, then the release `src` |
| `--checkout DIR` | Run without `cmsenv`, importing the python packages of a plain CMSSW checkout |
| `--stub-missing-cfi` | Replace missing generated `*_cfi` modules by empty EDProducers (for `--checkout`) |

The era and process modifiers only apply to menu fragments. A full configuration
keeps the era it was written with.

`Phase2C26I13M9` is the era of the newest Phase-2 workflows (geometries `Run4D126`
and later); older active geometries such as `Run4D121`, `Run4D124` and `Run4D125`
still use `Phase2C22I13M9`. Either gives exactly the same graph for `HLT_75e33` and
for the L1 profile, since no module of those configurations is added or reconfigured
by the difference between the two eras.

### Without a CMSSW release

For a quick look from a plain checkout, without `cmsenv`:

```bash
python3 HLTrigger/Configuration/scripts/triggerMenuGraph HLTrigger.Configuration.HLT_75e33_cff \
  --checkout . --stub-missing-cfi -o HLT_75e33.html
```

The cfi files generated from `fillDescriptions` at build time do not exist in a
plain checkout. `--stub-missing-cfi` replaces them with empty modules, which is fine
when the menu only uses them as templates for `clone()`. Parameters set through
`clone()` or era modifiers on a stub are kept when they can be converted to CMS types.
The stubbed modules are listed on stderr and in the page header. Their own inputs
are mostly missing, so some edges are absent in this mode.

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
- The profile's flag marks some modules with a dashed border: Alpaka modules
  (`@alpaka` or an explicit `alpaka_*` backend) for `hlt`, the legacy Run-3 emulators
  for `l1`.

## Subsystem rules

Each profile module defines:

- `SUBSYSTEMS`: id, name, colour slot (1-8, or `None` for a neutral dashed style) and
  description. Keep the `ext` id, which the page uses for external inputs, and `other`
  for unclassified modules.
- `RULES`: `(subsystem id, label regexes, module kinds, plugin-type regexes)`. A rule
  matches when a label regex matches the module label, the module kind (`EDProducer`,
  `EDFilter`, `OutputModule`, ...) is listed, or a type regex matches the C++ plugin
  name. The first matching rule wins.
- `CHIPS`: subsystems the toolbar can hide.
- `FLAG`: which modules get a dashed border, by plugin type (`types`), label
  (`labels`) or the name of a path or sequence/task they are in (`containers`).
- `TITLE`: default page title, or `None` for `<menu> Dataflow`.

Modules that match no rule go to *Unclassified* and are listed on stderr. The unit
test fails if any module of the tested configurations is unclassified, so new menus or
new modules show up there and the rules can be extended.

## Files

| File | Content |
| --- | --- |
| `scripts/triggerMenuGraph` | Command-line tool |
| `python/Tools/menuGraph.py` | Menu loading, graph extraction, package lookup, rendering |
| `python/Tools/menuGraphRules.py` | Subsystem rules of the `hlt` profile |
| `python/Tools/menuGraphRulesL1.py` | Subsystem rules of the `l1` profile |
| `data/triggerMenuGraph.html` | Page template; the script fills the title, header, and data placeholders |
| `test/test_triggerMenuGraph.sh` | Unit test: builds the pages of `HLT_75e33` and of the Phase-2 L1T emulation and checks their content |

Run the unit test with:

```bash
scram b runtests_test_triggerMenuGraph
```
