#!/usr/bin/env python3
"""P4 stage T0, first test: replay the campaign ledger into the hyper-TSKG on
the campaign clock. Each ledger entry becomes a record node and one event
whose inputs are the earlier entries it cites (any payload key ending in
_seq or _seqs) and whose process node is its campaign. Writes
results/ledger_tskg.json and results/t0_checks.json."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
MT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from tskg import TSKG  # noqa: E402


def cited(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if (k.endswith("_seq") or k.endswith("_seqs")) and v is not None:
                for x in (v if isinstance(v, list) else [v]):
                    if isinstance(x, int):
                        out.add(x)
            else:
                cited(v, out)
    elif isinstance(obj, list):
        for v in obj:
            cited(v, out)
    return out


def build():
    E = [json.loads(l) for l in open(os.path.join(MT, "phase_c", "ledger_campaign.jsonl"))]
    g = TSKG()
    g.node("src:agent", "source", name="campaign agent (decisions applied by registered rules or by the agent)")
    refs, by_camp = {}, {}
    for e in E:
        p = e["payload"]
        camp = p.get("campaign") or p.get("action") or (p.get("op_id") or "unnamed").rsplit("-20", 1)[0]
        g.node(f"proc:{camp}", "process", step="campaign", name=camp)
        g.node(f"rec:{e['seq']}", "claim", ledger_kind=e["kind"], op=p.get("op"), op_id=p.get("op_id"),
               labels=[p["label"]] if p.get("label") else [], time=e["time"])
        c = sorted(x for x in cited(p, set()) if x != e["seq"])
        refs[e["seq"]] = c
        implicit = [x for x in by_camp.get(camp, []) if x not in c]
        by_camp.setdefault(camp, []).append(e["seq"])
        before = [f"rec:{x}" for x in c if x < e["seq"]] + [f"rec:{x}" for x in implicit]
        g.event(f"ev:{e['seq']}", e["kind"], "campaign", (e["time"], e["time"]), before=before,
                explicit_inputs=[x for x in c if x < e["seq"]], implicit_inputs=implicit,
                after=[f"rec:{e['seq']}"], process=f"proc:{camp}", source="src:agent",
                labels=[p["label"]] if p.get("label") else [], forward_refs=[x for x in c if x > e["seq"]])
    global by_camp_global
    by_camp_global = by_camp
    return g, E, refs


def main():
    g, E, refs = build()
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    g.dump(os.path.join(HERE, "results", "ledger_tskg.json"))
    times = [e["time"] for e in E]
    reach19, ev19 = g.reach("rec:19")
    prov115, _ = g.provenance("rec:115")
    fwd = {s: r for s, r in refs.items() if any(x > s for x in r)}
    checks = {
        "events_equal_entries": len(g.events) == len(E),
        "campaign_clock_monotone": times == sorted(times),
        "all_cited_entries_exist": all(x in {e["seq"] for e in E} for r in refs.values() for x in r),
        "forward_references": {str(k): v for k, v in fwd.items()},
        "reach_of_ge_corner_registration_19": sorted(int(n.split(":")[1]) for n in reach19 if n.startswith("rec:")),
        "provenance_of_300K_level_decision_115": sorted(int(n.split(":")[1]) for n in prov115 if n.startswith("rec:")),
        "events_with_inputs": sum(1 for e in g.events if e["before"]),
        "events_with_explicit_inputs": sum(1 for e in g.events if e["explicit_inputs"]),
        "events_with_only_implicit_inputs": sum(1 for e in g.events if e["implicit_inputs"] and not e["explicit_inputs"]),
        "campaigns": len(by_camp_global),
        "stats": g.stats(),
    }
    checks["reach_19_contains_26_27"] = {26, 27} <= set(checks["reach_of_ge_corner_registration_19"])
    checks["provenance_115_contains_107_111_113_114"] = {107, 111, 113, 114} <= set(checks["provenance_of_300K_level_decision_115"])
    json.dump(checks, open(os.path.join(HERE, "results", "t0_ledger_checks.json"), "w"), indent=1)
    print(json.dumps(checks, indent=1)[:2500])


if __name__ == "__main__":
    main()
