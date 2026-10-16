#!/usr/bin/env python3
"""P4 stage T0: a time-resolved evidence hypergraph (hyper-TSKG) data model.

Nodes
  state    a material state (composition, structure labels such as
           as-grown, annealed, relaxed, amorphous, metastable)
  species  a point defect or defect complex in Kroger-Vink-style site
           notation without charge: "Sn_Ge" (Sn on a Ge site), "V_Ge"
           (vacancy on a Ge site), "Sn_i" (interstitial), complexes as
           "{Sn_Ge,V_Ge}", clusters as "{Sn_Ge*4}"
  process  a dated process step (growth, anneal, implant, laser melt,
           measurement) with its recipe
  source   an evidence source (MD, BTE, literature DOI, database release)
  claim    a statement the campaign holds (a law, a range, a value)

Hyperedges (events): one record linking, at once, the state or claims
before, the state or claims after, the process step, the source and a time
window. Two clocks are kept apart: "material" (the sample's own time during
processing, seconds) and "campaign" (the date the campaign recorded or
decided something, ISO time). Reaction events are checked for balance
(atoms by element and lattice sites conserved).

Pure Python, no dependencies.
"""
import json, re
from collections import Counter, defaultdict

SITE_RE = re.compile(r"^([A-Z][a-z]?|V)_([A-Z][a-z]?|i)$")


def parse_species(s):
    """Return (atoms Counter, sites Counter) for a species string."""
    s = s.strip()
    if s.startswith("{") and s.endswith("}"):
        atoms, sites = Counter(), Counter()
        for part in s[1:-1].split(","):
            n = 1
            if "*" in part:
                part, n = part.split("*")
                n = int(n)
            a, t = parse_species(part)
            for k in a:
                atoms[k] += n * a[k]
            for k in t:
                sites[k] += n * t[k]
        return atoms, sites
    m = SITE_RE.match(s)
    if not m:
        raise ValueError(f"cannot parse species {s!r}")
    occ, site = m.groups()
    atoms = Counter() if occ == "V" else Counter({occ: 1})
    sites = Counter() if site == "i" else Counter({site: 1})
    return atoms, sites


def side(terms):
    """terms: list of (coefficient, species)"""
    A, S = Counter(), Counter()
    for n, sp in terms:
        a, s = parse_species(sp)
        for k in a:
            A[k] += n * a[k]
        for k in s:
            S[k] += n * s[k]
    return A, S


def balanced(lhs, rhs):
    return side(lhs) == side(rhs)


class TSKG:
    def __init__(self):
        self.nodes = {}
        self.events = []

    # ---- nodes
    def node(self, nid, kind, **attrs):
        if nid in self.nodes and self.nodes[nid]["kind"] != kind:
            raise ValueError(f"{nid} already a {self.nodes[nid]['kind']}")
        self.nodes.setdefault(nid, {"id": nid, "kind": kind}).update(attrs)
        return nid

    # ---- hyperedges
    def event(self, eid, kind, clock, window, before=(), after=(), process=None, source=None,
              labels=(), reaction=None, **attrs):
        if clock not in ("material", "campaign"):
            raise ValueError("clock must be 'material' or 'campaign'")
        for n in list(before) + list(after) + [x for x in (process, source) if x]:
            if n not in self.nodes:
                raise KeyError(f"event {eid}: unknown node {n}")
        e = {"id": eid, "kind": kind, "clock": clock, "window": list(window), "before": list(before),
             "after": list(after), "process": process, "source": source, "labels": list(labels)}
        if reaction is not None:
            lhs, rhs = reaction
            if not balanced(lhs, rhs):
                raise ValueError(f"event {eid}: reaction not balanced {lhs} -> {rhs}")
            e["reaction"] = {"lhs": lhs, "rhs": rhs}
        e.update(attrs)
        self.events.append(e)
        return e

    # ---- queries
    def members(self, e):
        return set(e["before"]) | set(e["after"]) | {x for x in (e["process"], e["source"]) if x}

    def in_window(self, t0, t1, clock):
        return [e for e in self.events if e["clock"] == clock and e["window"][0] <= t1 and e["window"][1] >= t0]

    def reach(self, start):
        """Every node downstream of `start`: a node is reached when an event
        has a reached node among its before/process/source members, and all
        its after members are then reached. Returns (nodes, events)."""
        hit, evs = {start}, []
        order = sorted(range(len(self.events)), key=lambda i: (self.events[i]["clock"], self.events[i]["window"][0]))
        changed = True
        while changed:
            changed = False
            for i in order:
                e = self.events[i]
                ins = set(e["before"]) | {x for x in (e["process"], e["source"]) if x}
                if ins & hit and not set(e["after"]) <= hit:
                    hit |= set(e["after"])
                    changed = True
                if ins & hit and e["id"] not in evs:
                    evs.append(e["id"])
        return hit, evs

    def provenance(self, nid):
        """Events (and their members) that produced node `nid`, walking back."""
        want, evs = {nid}, []
        changed = True
        while changed:
            changed = False
            for e in self.events:
                if set(e["after"]) & want and e["id"] not in evs:
                    evs.append(e["id"])
                    new = set(e["before"]) | {x for x in (e["process"], e["source"]) if x}
                    if not new <= want:
                        want |= new
                        changed = True
        return want, evs

    def stats(self):
        ev = Counter(f"{e['clock']}:{e['kind']}" for e in self.events)
        return {"nodes": dict(Counter(n["kind"] for n in self.nodes.values())), "events": dict(ev),
                "max_arity": max((len(self.members(e)) for e in self.events), default=0)}

    def dump(self, path):
        json.dump({"nodes": list(self.nodes.values()), "events": self.events}, open(path, "w"), indent=1)

    @classmethod
    def load(cls, path):
        g = cls()
        d = json.load(open(path))
        g.nodes = {n["id"]: n for n in d["nodes"]}
        g.events = d["events"]
        return g
