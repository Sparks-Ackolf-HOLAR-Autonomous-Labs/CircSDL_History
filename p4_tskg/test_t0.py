#!/usr/bin/env python3
"""P4 stage T0 schema tests on the material clock. The GeSn anneal below is a
schema fixture with placeholder numbers, not data: it checks that the model
holds a dated defect reaction as one hyperedge, rejects unbalanced
reactions, keeps the two clocks apart, and answers provenance and reach
queries. Run: python3 test_t0.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tskg import TSKG, balanced  # noqa: E402

ok = []


def check(name, cond):
    ok.append((name, bool(cond)))


g = TSKG()
g.node("st:asgrown", "state", composition="Ge0.88Sn0.12", labels=["as-grown", "metastable"])
g.node("st:ann1", "state", composition="Ge0.88Sn0.12", labels=["annealed"])
for sp in ("Sn_Ge", "V_Ge", "{Sn_Ge,V_Ge}", "{Sn_Ge*2,V_Ge}", "Sn_i"):
    g.node(f"sp:{sp}", "species", notation=sp)
g.node("proc:anneal1", "process", step="anneal", recipe={"T_K": 573, "t_s": 600, "atmosphere": "N2"})
g.node("src:md", "source", method="MACE-MD (schema fixture)")
g.node("src:lit", "source", method="in-situ XRD (schema fixture)")
g.node("val:snsub_0", "claim", observable="substitutional Sn fraction", value=None)
g.node("val:snsub_1", "claim", observable="substitutional Sn fraction", value=None)

g.event("ev:pair", "reaction", "material", (0, 60), before=["st:asgrown", "sp:Sn_Ge", "sp:V_Ge"],
        after=["sp:{Sn_Ge,V_Ge}"], process="proc:anneal1", source="src:md",
        reaction=([(1, "Sn_Ge"), (1, "V_Ge")], [(1, "{Sn_Ge,V_Ge}")]))
g.event("ev:grow", "reaction", "material", (60, 600), before=["sp:{Sn_Ge,V_Ge}", "sp:Sn_Ge"],
        after=["sp:{Sn_Ge*2,V_Ge}", "st:ann1"], process="proc:anneal1", source="src:md",
        reaction=([(1, "{Sn_Ge,V_Ge}"), (1, "Sn_Ge")], [(1, "{Sn_Ge*2,V_Ge}")]))
g.event("ev:meas0", "measurement", "material", (0, 0), before=["st:asgrown"], after=["val:snsub_0"],
        process="proc:anneal1", source="src:lit")
g.event("ev:meas1", "measurement", "material", (600, 600), before=["st:ann1"], after=["val:snsub_1"],
        process="proc:anneal1", source="src:lit")
g.node("rec:decision", "claim", note="campaign decision (schema fixture)")
g.event("ev:decide", "decision", "campaign", ("2026-10-09T00:00:00Z", "2026-10-09T00:00:00Z"),
        before=["val:snsub_1"], after=["rec:decision"], source="src:md")

check("balanced pair formation accepted", any(e["id"] == "ev:pair" for e in g.events))
try:
    g.event("ev:bad", "reaction", "material", (0, 1), before=["sp:Sn_Ge"], after=["sp:V_Ge"],
            process="proc:anneal1", source="src:md", reaction=([(1, "Sn_Ge")], [(1, "V_Ge")]))
    check("unbalanced reaction rejected", False)
except ValueError:
    check("unbalanced reaction rejected", True)
check("Frenkel-type step balances", balanced([(1, "Sn_Ge")], [(1, "Sn_i"), (1, "V_Ge")]))
check("one event links a state, three species, a process step and a source (6 members) with its time window",
      len(g.members(next(e for e in g.events if e["id"] == "ev:pair"))) == 6 and next(e for e in g.events if e["id"] == "ev:pair")["window"] == [0, 60])
check("material window query excludes the campaign clock",
      {e["id"] for e in g.in_window(0, 100, "material")} == {"ev:pair", "ev:grow", "ev:meas0"})
prov, evs = g.provenance("val:snsub_1")
check("provenance of the annealed value reaches the as-grown state and both sources",
      {"st:asgrown", "src:md", "src:lit", "proc:anneal1"} <= prov)
hit, _ = g.reach("src:md")
check("reach of the MD source includes the annealed state, its value and the campaign decision",
      {"st:ann1", "val:snsub_1", "rec:decision"} <= hit)
try:
    g.event("ev:x", "reaction", "geologic", (0, 1))
    check("unknown clock rejected", False)
except ValueError:
    check("unknown clock rejected", True)

for n, c in ok:
    print("PASS" if c else "FAIL", n)
print(f"{sum(c for _, c in ok)}/{len(ok)} pass")
sys.exit(0 if all(c for _, c in ok) else 1)
