"""Extract the producer/consumer graph of an HLT menu and render it as an HTML page.

Used by the hltMenuGraph script; see `hltMenuGraph --help`.

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

from HLTrigger.Configuration.Tools import menuGraphRules

TEMPLATE_NAME = "HLTrigger/Configuration/data/hltMenuGraph.html"
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
            namespace = {"__file__": filename, "__name__": "__hltMenuGraph_cfg__"}
            exec(compile(source, filename, "exec"), namespace)
            return namespace["process"]
        process = cms.Process(process_name, *_era_objects(era, modifiers))
        module = types.ModuleType("__hltMenuGraph_menu__")
        module.__file__ = filename
        exec(compile(source, filename, "exec"), module.__dict__)
        process.extend(module)
        return process
    process = cms.Process(process_name, *_era_objects(era, modifiers))
    process.load(config.replace("/", ".").removesuffix(".py"))
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
def _compile_rules():
    return [(sid, re.compile("|".join(rx)) if rx else None, set(kinds)) for sid, rx, kinds in menuGraphRules.RULES]


def classify(label, kind, rules):
    for sid, rx, kinds in rules:
        if kind in kinds or (rx is not None and rx.search(label)):
            return sid
    return "other"


# ---------------------------------------------------------------- extraction
def extract(process, packages=None):
    """Return the page data (a JSON-serialisable dict) for a cms.Process."""
    packages = packages or {}
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
        elif isinstance(value, cms.vstring):
            for i, x in enumerate(value):
                if x in labels:
                    out.append(("%s[%d]" % (name, i), x, "", "", True))

    def walk(pset, prefix, out):
        for n in pset.parameterNames_():
            tags_of(getattr(pset, n), prefix + n, out)

    rules = _compile_rules()
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
        modules.append(dict(
            id=label, type=mtype, kind=kind, package=packages.get(base, "(not found)"),
            containers=state.mod_cont.get(label, []), paths=state.mod_paths.get(label, []),
            subsystem=classify(label, kind, rules),
            alpaka=mtype.endswith("@alpaka") or mtype.startswith("alpaka_")))

    used = {m["subsystem"] for m in modules} | ({"ext"} if ext else set())
    subsystems = [s for s in menuGraphRules.SUBSYSTEMS if s["id"] in used or s["id"] in ("ext", "infra")]
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
        es=[dict(id=k, type=v.type_(), kind=type(v).__name__)
            for k, v in list(process.es_producers_().items()) + list(process.es_sources_().items())],
    )


# ---------------------------------------------------------------- rendering
def find_template():
    for d in os.environ.get("CMSSW_SEARCH_PATH", "").split(":"):
        p = os.path.join(d, TEMPLATE_NAME)
        if d and os.path.isfile(p):
            return p
    here = os.path.dirname(os.path.realpath(__file__))     # .../HLTrigger/Configuration/python/Tools
    p = os.path.join(os.path.dirname(os.path.dirname(here)), "data", "hltMenuGraph.html")
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
