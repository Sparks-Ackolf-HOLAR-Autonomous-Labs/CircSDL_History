#!/usr/bin/env python3
"""Build the time-resolved evidence hypergraph used in the P4 manuscript and
write every number the manuscript quotes from it to record_summary.json.

Reads committed files only (paths relative to the project root):
  p4_tskg/tskg.py                      data model (nodes, event hyperedges, two clocks)
  p4_tskg/results/t3_tskg.json         literature anneal series loaded on the material clock
  p4_tskg/T3_insitu/series.json        the same series with their full records
  p4_tskg/T1_md/out/*.json             MACE-MP-0 MD outputs (hashed on the ledger before analysis)
  p4_tskg/T1_md/t1_result.json         registered O2 reading and crystal-order screen
  p4_tskg/T1_md/o1_result.json         Sn-vacancy binding energy (O1)
  p4_tskg/replay_ledger.py             campaign ledger replay on the campaign clock
  phase_c/ledger_campaign.jsonl        the campaign ledger
Nothing is fitted; the script counts, groups and checks.
Run: python3 build_record.py   (standard library only)
"""
import json, math, os, sys, statistics as st
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
MT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P4 = os.path.join(MT, "p4_tskg")
sys.path.insert(0, P4)
from tskg import TSKG, balanced  # noqa: E402
import replay_ledger  # noqa: E402

out = {}

# ---------------------------------------------------------------- material clock
g = TSKG.load(os.path.join(P4, "results", "t3_tskg.json"))
lit = g.stats()
out["literature_graph"] = {"nodes": lit["nodes"], "events": lit["events"], "max_arity": lit["max_arity"]}

T1 = os.path.join(P4, "T1_md")
res = json.load(open(os.path.join(T1, "t1_result.json")))
o1 = json.load(open(os.path.join(T1, "o1_result.json")))

src = g.node("src:mace-mp-0-md", "source", method="MACE-MP-0 medium MD (this work, CHPC)")
g.node("src:mace-mp-0-static", "source", method="MACE-MP-0 medium static relaxations (this work, CHPC)")
for sp in ("Sn_Ge", "V_Ge", "{Sn_Ge,V_Ge}"):
    g.node(f"sp:{sp}", "species", notation=sp)

n_loaded, n_bal, kinds = 0, 0, Counter()
snsn, snv, vac_hops = {}, {}, {}
for run, r in res["runs"].items():
    d = json.load(open(os.path.join(T1, "out", run + ".json")))
    a = d["args"]
    comp = f"Si{a['si']:.2f}Ge{1 - a['si'] - a['x']:.2f}Sn{a['x']:.2f}" if a["si"] else f"Ge{1 - a['x']:.2f}Sn{a['x']:.2f}"
    st0 = g.node(f"st:md:{run}:start", "state", composition=comp, labels=["random alloy", "2 vacancies", "MACE-MP-0 crystal"])
    proc = g.node(f"proc:md:{run}", "process", step="anneal (MD)", recipe={"T_K": a["T"], "t_ps": d["prod_ps"], "seed": a["seed"]})
    if not r["order"]["crystalline"]:
        # disordered runs: one recorded model-failure event, no defect events
        v = g.node(f"val:md:{run}:order", "claim", observable="crystal order", value="lost",
                   onset_ps=r["order"]["order_lost_at_ps"])
        g.event(f"ev:md:{run}:order", "range_limit", "material", (0.0, d["prod_ps"] * 1e-12), before=[st0], after=[v],
                process=proc, source=src, labels=["outside range of the potential"])
        kinds["range_limit"] += 1
        continue
    for k, e in enumerate(d["events"]):
        t = e["t_ps"] * 1e-12
        if e.get("reaction"):
            lhs, rhs = ([tuple(x) for x in e["reaction"][0]], [tuple(x) for x in e["reaction"][1]])
            n_bal += balanced(lhs, rhs)
            before = [st0] + [f"sp:{s}" for _, s in lhs if f"sp:{s}" in g.nodes] + (["sp:{Sn_Ge,V_Ge}"] if e["name"] == "Sn hop" else [])
            after = ["sp:{Sn_Ge,V_Ge}"] if e["name"] in ("Sn-V pairing", "Sn hop") else ["sp:Sn_Ge", "sp:V_Ge"]
            g.event(f"ev:md:{run}:{k}", "reaction", "material", (t, t), before=sorted(set(before)), after=after,
                    process=proc, source=src, reaction=(lhs, rhs), name=e["name"])
        else:
            g.event(f"ev:md:{run}:{k}", "transition", "material", (t, t), before=[st0, "sp:V_Ge"], after=["sp:V_Ge"],
                    process=proc, source=src, name=e["name"])
        kinds[e["name"]] += 1
        n_loaded += 1
    snsn[run] = [p["n_snsn_pairs"] for p in d["series"]]
    snv[run] = [p["n_snv_pairs"] for p in d["series"]]
    vac_hops[run] = r["vac_hops"]
    n_sites, n_sn, n_vac = d["n_sites"], d["n_sn"], a["nvac"]

# random-arrangement expectations on the diamond lattice (4 first neighbours per site)
bonds = n_sites * 4 // 2
exp_snsn = bonds * n_sn * (n_sn - 1) / (n_sites * (n_sites - 1))
exp_snv = n_vac * 4 * n_sn / (n_sites - 1)
out["md_500K_events"] = {
    "events_loaded": n_loaded, "by_kind": dict(kinds), "reaction_events_balanced": n_bal,
    "sites": n_sites, "sn_atoms": n_sn, "vacancies": n_vac,
    "snsn_pairs_time_mean": {k: round(st.mean(v), 2) for k, v in snsn.items()},
    "snsn_pairs_range": {k: [min(v), max(v)] for k, v in snsn.items()},
    "snsn_pairs_random_expectation": round(exp_snsn, 2),
    "sn_next_to_vacancy_time_mean": {k: round(st.mean(v), 2) for k, v in snv.items()},
    "sn_next_to_vacancy_random_expectation": round(exp_snv, 2),
}

# excess potential energy above the 500 K crystal, harmonic 3/2 kB T per atom removed
KB = 8.617333e-5
e500 = st.mean(p["epot_eV_atom"] for p in json.load(open(os.path.join(T1, "out", "gesn_x012_T500_s1.json")))["series"][:5])
exc = {}
for run, r in res["runs"].items():
    if r["si"]:
        continue
    ser = json.load(open(os.path.join(T1, "out", run + ".json")))["series"]
    late = [p["epot_eV_atom"] for p in ser if p["t_ps"] > 250]
    exc[run] = round(1000 * (st.mean(late) - e500 - 1.5 * KB * (r["T"] - 500.0)), 1)
out["excess_energy_last_250ps_meV_per_atom"] = exc

# O1 as a computed claim on the graph
v = g.node("val:o1", "claim", observable="Sn-vacancy binding energy", unit="eV",
           value=round(o1["E_b_mean_eV"], 3), sd=round(o1["E_b_sd_eV"], 3), n=o1["n_converged"])
g.node("st:o1", "state", composition="Ge0.88Sn0.12", labels=["random alloy", "0 K relaxed", "MACE-MP-0 crystal"])
g.node("proc:o1", "process", step="static relaxation", recipe={"fmax_eV_per_A": 0.01, "cell": "4x4x4 cubic"})
g.event("ev:o1", "computation", "material", (0.0, 0.0), before=["st:o1", "sp:Sn_Ge", "sp:V_Ge"], after=[v],
        process="proc:o1", source="src:mace-mp-0-static")

s = g.stats()
out["material_clock_graph"] = {"nodes": s["nodes"], "events": s["events"], "max_arity": s["max_arity"],
                               "total_nodes": sum(s["nodes"].values()), "total_events": sum(s["events"].values())}

# ---------------------------------------------------------------- which values conflict, and why
S = json.load(open(os.path.join(P4, "T3_insitu", "series.json")))
ea_rows = []
for s_ in S:
    if s_["observable"] not in ("activation_energy_Sn_diffusion", "activation_energy_Sn_diffusion_computed"):
        continue
    m = s_["material"]
    sid = s_["series_id"]
    if sid.startswith("lieten2014"):
        continue  # quotes the implanted-Ge value of Kringhoj 1994; same number, not a second measurement
    si = m.get("si_fraction")
    if sid.startswith("kringhoj"):
        comp = m["composition"]
        si = 0.0 if "bulk" in comp else float(comp.split("fraction")[1].split()[0])
        state, kind = "implanted bulk crystal", "measured"
    elif "_highT_" in sid:
        state, kind = "metastable film, anneals above about 650 C", "measured"
    elif "_lowT_" in sid:
        state, kind = "metastable film, anneals below about 650 C", "measured"
    else:
        state, kind = "computed (DFT, Sn-vacancy pairs in Ge)", "computed"
    for p in s_["points"]:
        ea_rows.append({"series": sid, "doi": s_["doi"], "si_fraction": si, "sn_fraction": m.get("sn_fraction"),
                        "state": state, "kind": kind, "Ea_eV": p[1], "unc_eV": p[2]})
ge_rich = [r for r in ea_rows if r["kind"] == "measured" and (r["si_fraction"] or 0) <= 0.1]
groups = {}
for r in ge_rich:
    groups.setdefault(r["state"], []).append(r["Ea_eV"])
out["activation_energy_conflict"] = {
    "rows": ea_rows,
    "ge_rich_measured_span_eV": [min(r["Ea_eV"] for r in ge_rich), max(r["Ea_eV"] for r in ge_rich)],
    "ge_rich_by_state_span_eV": {k: [min(v), max(v)] for k, v in groups.items()},
    "md_registered_slope_eV": res["registered"]["Ea_eV"],
    # the registered rule labelled this a lower bound; it is the one-event barrier, and 46 net hops were seen
    # at 500 K, so it bounds nothing (correction, ledger 150); the hop count itself corresponds to:
    "md_500K_one_event_eV": res["screened"]["Ea_lower_bound_eV"],
    "md_500K_observed_hops_eV": round(res["screened"]["Ea_lower_bound_eV"]
                                      - 8.617333262e-5 * 500 * math.log(res["screened"]["per_T"]["500.0"]["net_sn_hops"]), 3),
}

# diffusivity of Sn: measured film at 500 C against the implanted-bulk law, and both extrapolated to 400 C
import math
ser = {s_["series_id"]: s_ for s_ in S}
d_film_500 = next(p[1] for p in ser["vdd2020_DSn_GeSn_1"]["points"] if p[0] == 500)
ea_low = next(p[1] for p in ser["vdd2020_EA_Sn_GeSn_lowT_6"]["points"])
ea_bulk, d0_bulk = 3.05, 70.0  # quoted law 70 exp(-3.05 eV/kT) cm2/s (series lieten2014_EaSnGe_1, from Kringhoj 1994)
def d_bulk(tc):
    return d0_bulk * math.exp(-ea_bulk / (KB * (tc + 273.15)))
d_film_400 = d_film_500 * math.exp(-ea_low / KB * (1 / 673.15 - 1 / 773.15))
out["sn_diffusivity_film_vs_bulk"] = {
    "film": "Ge0.94Sn0.06 (von den Driesch 2020, figure-read)", "D_film_500C_cm2_s": d_film_500,
    "D_bulk_law_500C_cm2_s": d_bulk(500), "ratio_500C": round(d_film_500 / d_bulk(500), 1),
    "D_film_400C_extrapolated_Ea_lowT_cm2_s": d_film_400, "D_bulk_law_400C_cm2_s": d_bulk(400),
    "ratio_400C": round(d_film_400 / d_bulk(400)),
    "diffusion_length_film_400C_20min_nm": round(1e7 * math.sqrt(d_film_400 * 1200), 2),
    "diffusion_length_bulk_400C_20min_nm": round(1e7 * math.sqrt(d_bulk(400) * 1200), 3),
}
# Wang 2016 measured Ge-Sn interdiffusion in Ge/Ge0.9Sn0.1 MQWs inside 380-450 C, so 400 C needs no extrapolation
ea_w, d0_w = 1.21, 2.9e-7  # cm2/s, law quoted by Xia (arXiv:1901.10105, eq. 11) from Wang 2016
d_w_400 = d0_w * math.exp(-ea_w / (KB * 673.15))
out["sn_diffusivity_film_vs_bulk"].update({
    "film_measured_400C": "Ge/Ge0.9Sn0.1 MQW (Wang 2016, law fitted over 380-450 C)",
    "D_wang_400C_cm2_s": d_w_400, "ratio_wang_400C": round(d_w_400 / d_bulk(400)),
    "ratio_wang_to_vdd_extrapolated_400C": round(d_w_400 / d_film_400, 1),
    "diffusion_length_wang_400C_20min_nm": round(1e7 * math.sqrt(d_w_400 * 1200), 2),
})

on = []
for s_ in S:
    o = s_["observable"].lower()
    if not ("onset" in o and ("segregation" in o or "precipitation" in o or "expulsion" in o or "particle" in o)):
        continue
    if "surface" in o or "indiffusion" in o:
        continue
    m, pr = s_["material"], s_["process"]
    start = "amorphous film" if "amorphous" in (m.get("composition") or "") else "epitaxial crystalline film"
    for p in s_["points"]:
        on.append({"series": s_["series_id"], "doi": s_["doi"], "sn_fraction": m.get("sn_fraction"),
                   "si_fraction": m.get("si_fraction"), "start": start, "mode": pr.get("mode"),
                   "hold_s": (pr.get("times_s") or [None])[0], "onset_C": p[1], "unc_C": p[2]})
out["segregation_onsets"] = on

att = [s_ for s_ in S if s_["series_id"] in ("attiaoui2026_E2shift_1", "attiaoui2026_E2shift_6")]
out["insitu_550C"] = {s_["series_id"]: {"composition": s_["material"]["composition"],
                                        "max_shift_meV": max(p[1] for p in s_["points"]),
                                        "duration_s": max(p[0] for p in s_["points"]),
                                        "cap": s_["process"].get("other") or s_["material"].get("substrate")}
                      for s_ in att}

# ---------------------------------------------------------------- campaign clock
def cited(obj, acc):
    """Earlier entries an entry names as its inputs: keys ending in _seq or _seqs
    (the T0 replay rule) and the key rests_on (used by later entries)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if (k.endswith("_seq") or k.endswith("_seqs") or k == "rests_on") and v is not None:
                for x in (v if isinstance(v, list) else [v]):
                    if isinstance(x, int):
                        acc.add(x)
            else:
                cited(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            cited(v, acc)
    return acc


replay_ledger.cited = cited
cg, E, refs = replay_ledger.build()
last = max(e["seq"] for e in E)
def rec_ids(nodes):
    return sorted(int(n.split(":")[1]) for n in nodes if n.startswith("rec:"))
prov_range = rec_ids(cg.provenance("rec:145")[0])
prov_o1 = rec_ids(cg.provenance("rec:132")[0])
reach_reg = rec_ids(cg.reach("rec:126")[0])
cs = cg.stats()
out["campaign_clock_graph"] = {"entries": len(E), "first_seq": E[0]["seq"], "last_seq": last,
                               "events": cs["events"], "max_arity": cs["max_arity"],
                               "provenance_of_range_limit_145": prov_range,
                               "reach_of_t1_registration_126": reach_reg,
                               "provenance_of_o1_grade_132": prov_o1,
                               "events_with_explicit_inputs": sum(1 for e in cg.events if e["explicit_inputs"]),
                               "campaign_clock_monotone": [e["time"] for e in E] == sorted(e["time"] for e in E)}

json.dump(out, open(os.path.join(HERE, "record_summary.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("segregation_onsets",)}, indent=1)[:6000])
