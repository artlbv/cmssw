"""Extract the producer/consumer graph of a trigger menu (HLT or L1T configuration) and render it as an HTML page.

Used by the triggerMenuGraph script; see `triggerMenuGraph --help`.

The graph is built from the configuration only: an edge A -> B means that a
parameter of B (an InputTag, a VInputTag entry, or a plain string equal to a
module label) names A. Products read through labels hard-coded in C++ are not
seen, and parameters that the C++ ignores still produce edges.
"""
import collections
import datetime
import html
import importlib
import json
import os
import re
import subprocess
import sys
import types

import FWCore.ParameterSet.Config as cms

PROFILES = {
    "hlt": "HLTrigger.Configuration.Tools.menuGraphRules",
    "l1": "HLTrigger.Configuration.Tools.menuGraphRulesL1",
}


def profile_rules(profile):
    """Return the rules module of a profile name ("hlt", "l1") or of a python module name."""
    return importlib.import_module(PROFILES.get(profile, profile))

TEMPLATE_NAME = "HLTrigger/Configuration/data/triggerMenuGraph.html"
PLACEHOLDER_LABEL = re.compile(r"(?i)^(not ?used|default|none|dummy|unused)$")
_SWITCH = getattr(cms, "SwitchProducer", None)   # not available in every CMSSW version
_MODULE_TYPES = (cms.EDProducer, cms.EDFilter, cms.EDAnalyzer, cms.OutputModule) + ((_SWITCH,) if _SWITCH else ())


# ---------------------------------------------------------------- loading
def _era_objects(era, modifiers):
    objs = []
    if era:
        for name in era.split(","):
            mod = importlib.import_module("Configuration.Eras.Era_%s_cff" % name)
            objs.append(getattr(mod, name))
    for name in modifiers:
        mod = importlib.import_module("Configuration.ProcessModifiers.%s_cff" % name)
        objs.append(getattr(mod, name))
    return objs


def load_process(config, era=None, modifiers=(), process_name="HLTX"):
    """Return a cms.Process for `config`.

    `config` is either a python module name of a menu fragment
    (e.g. HLTrigger.Configuration.HLT_75e33_cff), the path of such a file, the
    path of a full configuration defining `process`, or "-" to read a full
    configuration from stdin. The era and process modifiers are applied when
    the process is created by this function, that is for menu fragments; a
    full configuration keeps the era it was written with.
    """
    if config == "-" or os.path.isfile(config):
        source = sys.stdin.read() if config == "-" else open(config).read()
        filename = "<stdin>" if config == "-" else os.path.abspath(config)
        if re.search(r"^\s*process\s*=\s*cms\.Process\(", source, re.M):
            namespace = {"__file__": filename, "__name__": "__triggerMenuGraph_cfg__"}
            exec(compile(source, filename, "exec"), namespace)
            return namespace["process"]
        process = cms.Process(process_name, *_era_objects(era, modifiers))
        module = types.ModuleType("__triggerMenuGraph_menu__")
        module.__file__ = filename
        exec(compile(source, filename, "exec"), module.__dict__)
        process.extend(module)
        return process
    process = cms.Process(process_name, *_era_objects(era, modifiers))
    process.load(config.replace("/", ".").removesuffix(".py"))
    return process


def load_l1_process(era, modifiers=(), gt_menu="step1_2024", process_name="L1X"):
    """Build the Phase-2 L1T emulation as cmsDriver does for `-s L1TrackTrigger,L1,L1P2GT:<gt_menu>`."""
    process = cms.Process(process_name, *_era_objects(era, modifiers))
    process.load("Configuration.StandardSequences.L1TrackTrigger_cff")
    process.load("Configuration.StandardSequences.SimL1Emulator_cff")
    process.load("Configuration.StandardSequences.SimPhase2L1GlobalTriggerEmulator_cff")
    process.L1TrackTrigger_step = cms.Path(process.L1TrackTrigger)
    process.L1simulation_step = cms.Path(process.SimL1Emulator)
    process.Phase2L1GTProducer = cms.Path(process.l1tGTProducerSequence)
    process.Phase2L1GTAlgoBlockProducer = cms.Path(process.l1tGTAlgoBlockProducerSequence)
    schedule = [process.L1TrackTrigger_step, process.L1simulation_step,
                process.Phase2L1GTProducer, process.Phase2L1GTAlgoBlockProducer]
    menu_paths = []
    if gt_menu:
        menu = importlib.import_module("L1Trigger.Configuration.Phase2GTMenus.%s" % gt_menu).menu
        for path_file in menu:
            process.load(path_file)
            module = importlib.import_module(path_file)
            menu_paths += [n for n in dir(module) if type(getattr(module, n)) is cms.Path]
    schedule += [getattr(process, n) for n in sorted(set(menu_paths))]
    process.schedule = cms.Schedule(*schedule)
    return process


# ---------------------------------------------------------------- traversal
def _scheduled(process):
    sched = process.schedule_()
    if sched is not None:
        names = [p.label_() for p in sched]
        tasks = list(getattr(sched, "_tasks", []))
    else:
        names = list(process.paths_()) + list(process.endpaths_())
        if hasattr(process, "finalpaths_"):
            names += list(process.finalpaths_())
        tasks = []
    return names, tasks


class _Visitor(object):
    def __init__(self, state, path):
        self.s, self.path, self.stack = state, path, []

    @staticmethod
    def _is_container(v):
        return isinstance(v, (cms.Sequence, cms.Task)) or type(v).__name__ == "ConditionalTask"

    def enter(self, v):
        s = self.s
        if self._is_container(v):
            label = v.label_() if v.hasLabel_() else None
            if label:
                s.seq_occ[label].add(self.stack[-1] if self.stack else None)
            self.stack.append(label or (self.stack[-1] if self.stack else None))
        elif isinstance(v, _MODULE_TYPES):
            label = v.label_()
            s.mod_obj[label] = v
            if self.path and self.path not in s.mod_paths[label]:
                s.mod_paths[label].append(self.path)
            if self.path and label not in s.path_mods[self.path]:
                s.path_mods[self.path].append(label)
            c = self.stack[-1] if self.stack else None
            if c and c not in s.mod_cont[label]:
                s.mod_cont[label].append(c)

    def leave(self, v):
        if self._is_container(v):
            self.stack.pop()


class _State(object):
    def __init__(self):
        self.mod_obj = {}
        self.mod_paths = collections.defaultdict(list)
        self.mod_cont = collections.defaultdict(list)
        self.seq_occ = collections.defaultdict(set)
        self.path_mods = collections.OrderedDict()


# ---------------------------------------------------------------- packages
def default_source_dirs():
    dirs = []
    for var in ("CMSSW_BASE", "CMSSW_RELEASE_BASE", "CMSSW_FULL_RELEASE_BASE"):
        d = os.environ.get(var)
        if d and os.path.isdir(os.path.join(d, "src")):
            dirs.append(os.path.join(d, "src"))
    here = os.path.realpath(__file__)          # <src>/HLTrigger/Configuration/python/Tools/menuGraph.py
    src = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(here)))))
    if os.path.isdir(os.path.join(src, "FWCore")) and src not in dirs:
        dirs.append(src)
    seen, out = set(), []
    for d in dirs:
        r = os.path.realpath(d)
        if r not in seen:
            seen.add(r)
            out.append(d)
    return out


def plugin_packages(source_dirs):
    """Map plugin name -> Package/Subpackage by scanning DEFINE_*_MODULE macros.

    Earlier directories take precedence (local area before the release)."""
    rx = re.compile(r"^(?:\./)?([^/]+/[^/]+)/.*?:\s*DEFINE_\w*?MODULE\(\s*([\w:]+)")
    pkg = {}
    for d in source_dirs:
        try:
            out = subprocess.run(
                ["grep", "-rEo", "--include=*.cc", "--include=*.cpp", "--include=*.h",
                 r"DEFINE_(FWK|EDM)_[A-Z_]*MODULE\(\s*[A-Za-z0-9_:]+", "."],
                cwd=d, capture_output=True, text=True, check=False).stdout
        except OSError:
            continue
        for line in out.splitlines():
            m = rx.match(line)
            if m:
                pkg.setdefault(m.group(2).split("::")[-1], m.group(1))
    return pkg


# ---------------------------------------------------------------- classification
def _compile_rules(rules_module):
    out = []
    for rule in rules_module.RULES:
        sid, labels, kinds = rule[0], rule[1], rule[2]
        types = rule[3] if len(rule) > 3 else []
        out.append((sid, re.compile("|".join(labels)) if labels else None, set(kinds),
                    re.compile("|".join(types)) if types else None))
    return out


def classify(label, kind, mtype, rules):
    for sid, rx, kinds, trx in rules:
        if kind in kinds or (rx is not None and rx.search(label)) or (trx is not None and trx.search(mtype)):
            return sid
    return "other"


# ---------------------------------------------------------------- extraction
def extract(process, packages=None, rules_module=None):
    """Return the page data (a JSON-serialisable dict) for a cms.Process."""
    packages = packages or {}
    rules_module = rules_module or profile_rules("hlt")
    state = _State()
    sched, sched_tasks = _scheduled(process)
    all_paths = dict(process.paths_())
    all_paths.update(process.endpaths_())
    if hasattr(process, "finalpaths_"):
        all_paths.update(process.finalpaths_())
    for name in sched:
        state.path_mods[name] = []
        all_paths[name].visit(_Visitor(state, name))
    for task in sched_tasks:
        task.visit(_Visitor(state, None))
    labels = set(state.mod_obj)
    path_names = set(sched)
    seq_parent = {k: next(iter(v)) for k, v in state.seq_occ.items() if len(v) == 1 and None not in v}

    # EDAliases: alias label -> aliased module labels
    aliases = {}
    for name, alias in process.aliases_().items():
        aliases[name] = [p for p in alias.parameterNames_() if p in labels]
    es_labels = set(process.es_producers_()) | set(process.es_sources_())

    def tags_of(value, name, out):
        if isinstance(value, cms.InputTag):
            out.append((name, value.getModuleLabel(), value.getProductInstanceLabel(), value.getProcessName(), False))
        elif isinstance(value, cms.VInputTag):
            for i, x in enumerate(value):
                if isinstance(x, str):
                    p = x.split(":") + ["", ""]
                    out.append(("%s[%d]" % (name, i), p[0], p[1], p[2], False))
                else:
                    tags_of(x, "%s[%d]" % (name, i), out)
        elif isinstance(value, cms.VPSet):
            for i, ps in enumerate(value):
                walk(ps, "%s[%d]." % (name, i), out)
        elif isinstance(value, cms.PSet):
            walk(value, name + ".", out)
        elif isinstance(value, cms.string):
            if value.value() in labels:
                out.append((name, value.value(), "", "", True))
            else:
                for tok in set(re.findall(r"[A-Za-z_]\w*", value.value())) & path_names:
                    out.append((name, tok, "", "", "path"))
        elif isinstance(value, cms.vstring):
            for i, x in enumerate(value):
                if x in labels:
                    out.append(("%s[%d]" % (name, i), x, "", "", True))

    def walk(pset, prefix, out):
        for n in pset.parameterNames_():
            tags_of(getattr(pset, n), prefix + n, out)

    rules = _compile_rules(rules_module)
    flag = getattr(rules_module, "FLAG", {}) or {}
    flag_types = re.compile(flag["types"]) if flag.get("types") else None
    flag_cont = re.compile(flag["containers"]) if flag.get("containers") else None
    flag_labels = re.compile(flag["labels"]) if flag.get("labels") else None
    modules, edges, ext = [], [], collections.OrderedDict()
    seen = set()
    for label, obj in state.mod_obj.items():
        found = []
        if _SWITCH is not None and isinstance(obj, _SWITCH):
            for case in obj.parameterNames_():
                walk(getattr(obj, case), case + ".", found)
            mtype = "SwitchProducer(%s)" % ", ".join(
                "%s: %s" % (c, getattr(obj, c).type_()) for c in obj.parameterNames_())
            kind = "SwitchProducer"
        else:
            walk(obj, "", found)
            mtype, kind = obj.type_(), type(obj).__name__
        for param, src, inst, proc, inferred in found:
            if inferred == "path":
                # path decision: the filters of path `src` feed this module
                members = state.path_mods.get(src, [])
                filters = [x for x in members if type(state.mod_obj[x]).__name__ == "EDFilter"] or members[-1:]
                for s in filters:
                    k = (s, label, "", param)
                    if s != label and k not in seen:
                        seen.add(k)
                        edges.append(dict(source=s, target=label, instance="", param=param, inferred=False,
                                          external=False, kind="pathDecision", path=src))
                continue
            if not src or src == label or PLACEHOLDER_LABEL.match(src) or src in es_labels:
                continue
            if proc == "@currentProcess":
                continue
            sources = aliases.get(src) or [src]
            for s in sources:
                external = s not in labels or proc == "@skipCurrentProcess"
                key = s if not external or s not in labels else s + " (earlier process)"
                if external:
                    e = ext.setdefault(key, {"consumers": [], "instances": set()})
                    if label not in e["consumers"]:
                        e["consumers"].append(label)
                    e["instances"].add(inst)
                k = (key, label, inst, param)
                if k in seen:
                    continue
                seen.add(k)
                edges.append(dict(source=key, target=label, instance=inst, param=param, inferred=inferred,
                                  external=external, kind="inferredString" if inferred else "InputTag"))
        base = mtype.split("@")[0].split("::")[-1]
        conts, paths = state.mod_cont.get(label, []), state.mod_paths.get(label, [])
        flagged = bool((flag_types and flag_types.search(mtype)) or (flag_labels and flag_labels.search(label)) or
                       (flag_cont and any(flag_cont.search(c) for c in conts + paths)))
        modules.append(dict(
            id=label, type=mtype, kind=kind, package=packages.get(base, "(not found)"),
            containers=conts, paths=paths, subsystem=classify(label, kind, mtype, rules), flag=flagged))

    used = {m["subsystem"] for m in modules} | ({"ext"} if ext else set())
    subsystems = [s for s in rules_module.SUBSYSTEMS if s["id"] in used or s["id"] == "ext"]
    # module-label patterns of the products kept by the scheduled output modules
    keeps = set()
    for obj in state.mod_obj.values():
        if isinstance(obj, cms.OutputModule) and hasattr(obj, "outputCommands"):
            for cmd in obj.outputCommands:
                words = cmd.split()
                if len(words) == 2 and words[0] in ("keep", "keepNotUnique"):
                    fields = words[1].split("_")
                    keeps.add("*" if words[1] == "*" or len(fields) < 2 else fields[1])
    children = collections.defaultdict(list)
    for child, parent in seq_parent.items():
        children[parent].append(child)
    return dict(
        subsystems=subsystems,
        modules=sorted(modules, key=lambda m: m["id"]),
        edges=edges,
        external=[dict(id=k, consumers=v["consumers"], instances=sorted(v["instances"])) for k, v in sorted(ext.items())],
        aliases=aliases,
        paths={p: state.path_mods[p] for p in sched},
        endpaths=[p for p in sched if p not in process.paths_()],
        taskChildren=dict(children),
        chips=[c for c in getattr(rules_module, "CHIPS", []) if c["sub"] in used],
        flag=dict(short=flag.get("short", "flagged"), label=flag.get("label", "")),
        outputKeeps=sorted(keeps),
        es=[dict(id=k, type=v.type_(), kind=type(v).__name__)
            for k, v in list(process.es_producers_().items()) + list(process.es_sources_().items())],
    )


# ---------------------------------------------------------------- lint
def lint(data, rules_module=None):
    """Checks on the extracted graph; returns {"warnings": [...], "info": [...]}.

    Warnings: external inputs that look like they should come from this configuration,
    i.e. labels with the profile's own prefix (LINT["own_labels"]) or near-identical to a
    module label (a likely typo). Info: producers on a path whose products nothing in the
    configuration reads, nor any output module keeps (minus LINT["ignore_unread"])."""
    import difflib
    import fnmatch
    rules_module = rules_module or profile_rules("hlt")
    cfg = getattr(rules_module, "LINT", {}) or {}
    own = re.compile(cfg["own_labels"]) if cfg.get("own_labels") else None
    expected = re.compile(cfg["expected_inputs"]) if cfg.get("expected_inputs") else None
    ignore = re.compile(cfg["ignore_unread"]) if cfg.get("ignore_unread") else None
    live = [m for m in data["modules"] if m.get("diff") != "removed"]
    lower = {m["id"].lower(): m["id"] for m in live}
    warnings, info = [], []
    for e in data["external"]:
        if e.get("diff") == "removed" or e["id"].endswith("(earlier process)"):
            continue
        close = difflib.get_close_matches(e["id"].lower(), list(lower), n=1, cutoff=0.9)
        suggestion = lower[close[0]] if close else None
        reasons = []
        if own and own.search(e["id"]):
            reasons.append("uses this configuration's label prefix")
        if suggestion and not (expected and expected.search(e["id"])):
            reasons.append("close to %s" % suggestion)
        if reasons:
            warnings.append(dict(check="suspicious-input", id=e["id"], consumers=e["consumers"], suggestion=suggestion,
                                 message="%s is read by %s but no module produces it (%s)"
                                         % (e["id"], ", ".join(e["consumers"]), "; ".join(reasons))))
    read = {e["source"] for e in data["edges"] if not e["external"] and e.get("diff") != "removed"}
    keeps = data.get("outputKeeps", [])
    for m in live:
        if m["kind"] not in ("EDProducer", "SwitchProducer") or not m["paths"] or m["id"] in read:
            continue
        if ignore and ignore.search(m["id"]):
            continue
        if any(fnmatch.fnmatchcase(m["id"], k) for k in keeps):
            continue
        info.append(dict(check="unread-product", id=m["id"], paths=m["paths"],
                         message="%s (%s) runs in %d path(s) but nothing in this configuration reads its products"
                                 % (m["id"], m["type"], len(m["paths"]))))
    notes = []
    if not any(m["kind"] == "OutputModule" for m in live):
        notes.append("This configuration has no output module, so products meant only for the output "
                     "(final objects, ntuple inputs) are also listed as unread products.")
    stubs = sum(1 for m in live if m["kind"] == "Stub")
    if stubs:
        notes.append("%d module(s) are empty stubs for generated cfi files (--stub-missing-cfi): their inputs are "
                     "unknown and the unread-products check skips them, so it under-reports." % stubs)
    return dict(warnings=warnings, info=info, notes=notes)


def _lint_key(item):
    return (item["check"], item["id"])


# ---------------------------------------------------------------- diff
def diff(old, new):
    """Annotate `new` (page data) with the differences from `old`; return the diff summary.

    Modules, edges and external inputs get diff="added"/"removed"/"changed"; removed ones
    are appended from `old` so the page can draw them as ghosts."""
    mo = {m["id"]: m for m in old["modules"]}
    mn = {m["id"]: m for m in new["modules"]}
    ekey = lambda e: (e["source"], e["target"], e["instance"], e["param"], e.get("kind", "InputTag"))
    eo = {ekey(e): e for e in old["edges"]}
    en = {ekey(e): e for e in new["edges"]}
    xo = {e["id"]: e for e in old["external"]}
    xn = {e["id"]: e for e in new["external"]}
    summary = dict(added=sorted(set(mn) - set(mo)), removed=sorted(set(mo) - set(mn)),
                   changed=[dict(id=k, old=mo[k]["type"], new=mn[k]["type"])
                            for k in sorted(set(mo) & set(mn)) if mo[k]["type"] != mn[k]["type"]],
                   edgesAdded=len(set(en) - set(eo)), edgesRemoved=len(set(eo) - set(en)),
                   externalAdded=sorted(set(xn) - set(xo)), externalRemoved=sorted(set(xo) - set(xn)))
    for k, m in mn.items():
        if k not in mo:
            m["diff"] = "added"
        elif mo[k]["type"] != m["type"]:
            m["diff"], m["oldType"] = "changed", mo[k]["type"]
    for k in summary["removed"]:
        new["modules"].append(dict(mo[k], diff="removed"))
    for k, e in en.items():
        if k not in eo:
            e["diff"] = "added"
    for k in set(eo) - set(en):
        new["edges"].append(dict(eo[k], diff="removed"))
    for k, e in xn.items():
        if k not in xo:
            e["diff"] = "added"
    for k in summary["externalRemoved"]:
        new["external"].append(dict(xo[k], diff="removed"))
    po, pn = old["paths"], new["paths"]
    summary["paths"] = [dict(path=p, status="added" if p not in po else "removed" if p not in pn else "changed",
                             added=sorted(set(pn.get(p, [])) - set(po.get(p, []))),
                             removed=sorted(set(po.get(p, [])) - set(pn.get(p, []))))
                        for p in list(pn) + [p for p in po if p not in pn]
                        if p not in po or p not in pn or set(po[p]) != set(pn[p])]
    summary["edges"] = [dict(e, diff=e.get("diff")) for e in new["edges"] if e.get("diff")]
    new["diff"] = summary
    return summary


def mark_new_lint(lint_new, lint_old):
    """Flag the findings of lint_new that lint_old does not have; return the number of new warnings."""
    old = {_lint_key(i) for i in lint_old["warnings"] + lint_old["info"]}
    current = {_lint_key(i) for i in lint_new["warnings"] + lint_new["info"]}
    for item in lint_new["warnings"] + lint_new["info"]:
        item["new"] = _lint_key(item) not in old
    lint_new["resolved"] = [dict(i, resolved=True) for i in lint_old["warnings"] + lint_old["info"]
                            if _lint_key(i) not in current]
    return sum(1 for i in lint_new["warnings"] if i["new"])


# ---------------------------------------------------------------- text reports
def format_lint(result, only_new=False):
    lines = ["Note: " + n for n in result.get("notes", [])]
    for title, items in (("Warnings", result["warnings"]), ("Info", result["info"]),
                         ("Resolved since the compared version", result.get("resolved", []))):
        items = [i for i in items if i.get("new", True) or not only_new]
        if items:
            lines.append("%s (%d)" % (title, len(items)))
            lines += ["  %s%s" % ("[new] " if i.get("new") else "", i["message"]) for i in items]
    return "\n".join(lines) if (result["warnings"] or result["info"] or result.get("resolved")) else "\n".join(lines + ["no findings"])


def format_diff(summary, label_old="old", label_new="new"):
    def edge(e):
        src = e["source"] + (":" + e["instance"] if e["instance"] else "")
        note = " [external]" if e["external"] else (" [path decision]" if e.get("kind") == "pathDecision" else "")
        return "%s -> %s  (%s)%s" % (src, e["target"], e["param"], note)
    out = []
    def section(title, rows):
        if rows:
            out.append("%s (%d)" % (title, len(rows)))
            out.extend("  " + r for r in rows)
    section("Modules added", ["+ " + k for k in summary["added"]])
    section("Modules removed", ["- " + k for k in summary["removed"]])
    section("Plugin type changed", ["~ %s  %s -> %s" % (c["id"], c["old"], c["new"]) for c in summary["changed"]])
    section("Dependencies added", ["+ " + edge(e) for e in summary["edges"] if e["diff"] == "added"])
    section("Dependencies removed", ["- " + edge(e) for e in summary["edges"] if e["diff"] == "removed"])
    section("External inputs added", ["+ " + k for k in summary["externalAdded"]])
    section("External inputs removed", ["- " + k for k in summary["externalRemoved"]])
    section("Paths", ["%s %s%s%s" % ({"added": "+", "removed": "-", "changed": "~"}[p["status"]], p["path"],
                                     (": " if p["added"] or p["removed"] else ""),
                                     " ".join(["+" + x for x in p["added"]] + ["-" + x for x in p["removed"]]))
                      for p in summary["paths"]])
    return ("%s -> %s\n" % (label_old, label_new)) + ("\n".join(out) if out else "no differences")


# ---------------------------------------------------------------- rendering
def find_template():
    for d in os.environ.get("CMSSW_SEARCH_PATH", "").split(":"):
        p = os.path.join(d, TEMPLATE_NAME)
        if d and os.path.isfile(p):
            return p
    here = os.path.dirname(os.path.realpath(__file__))     # .../HLTrigger/Configuration/python/Tools
    p = os.path.join(os.path.dirname(os.path.dirname(here)), "data", "triggerMenuGraph.html")
    if os.path.isfile(p):
        return p
    raise IOError("cannot find %s (searched CMSSW_SEARCH_PATH and next to %s); use --template" % (TEMPLATE_NAME, __file__))


def git_commit(path):
    try:
        out = subprocess.run(["git", "-C", path, "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, check=False)
        return out.stdout.strip() or None
    except OSError:
        return None


def render(data, template, title, menu, era=None, modifiers=(), commit=None, notes=()):
    """Fill the HTML template with the extracted data and the header metadata."""
    e = html.escape
    meta = ["<span><code>%s</code>%s</span>" % (e(menu), " @ <code>%s</code>" % e(commit) if commit else "")]
    setup = [os.environ.get("CMSSW_VERSION") or "no CMSSW release"]
    setup.append("era <code>%s</code>" % e(era) if era else "no era")
    if modifiers:
        setup.append("modifiers <code>%s</code>" % e(",".join(modifiers)))
    meta.append("<span>%s</span>" % ", ".join(setup))
    meta.append("<span>generated %s</span>" % datetime.date.today().isoformat())
    meta += ["<span>%s</span>" % e(n) for n in notes]
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    out = template
    for key, value in (("@@TITLE@@", e(title)), ("@@MENU@@", e(menu)), ("@@META@@", "\n      ".join(meta))):
        if key not in out:
            raise ValueError("template has no %s placeholder" % key)
        out = out.replace(key, value)
    if "/*@@DATA@@*/null" not in out:
        raise ValueError("template has no /*@@DATA@@*/null placeholder")
    return out.replace("/*@@DATA@@*/null", payload)
