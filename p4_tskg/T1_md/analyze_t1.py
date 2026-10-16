#!/usr/bin/env python3
"""Apply the O2 rule registered at ledger 126 to the T1 MD outputs committed at ledger 143.

Registered part: persistence-based Sn hops, reversal cancellation within 10 ps,
rate per temperature, Arrhenius slope or lower bound, vibration check.
Disclosed addition (not in the registration, labelled in the output): a
crystal-order screen. The registration assumed the GeSn lattice stays
crystalline; the runs show a jump in potential energy per atom and in the
vacancy count at 600 and 700 K, so the screen reports when and where order
was lost, and the O2 reading is given both as registered and restricted to
runs that kept their order.
"""
import glob, hashlib, json, math, os, sys
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); MT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(MT, "pilot", "src"))
from ledger import Ledger  # noqa: E402
led = Ledger(os.path.join(MT, "phase_c", "ledger_campaign.jsonl"))
raw = next(e for e in led.entries if e["kind"] == "batch_commitment" and e["payload"].get("op_id") == "p4-t1-md-raw")
for f, h in raw["payload"]["raw_sha256"].items():
    assert hashlib.sha256(open(os.path.join(MT, f), "rb").read()).hexdigest() == h, f
KB = 8.617333e-5; WIN = 10.0; NU = 1e13

def net_hops(events):
    hops = [e for e in events if e["name"] == "Sn hop"]
    hops.sort(key=lambda e: e["t_ps"]); alive = [True] * len(hops)
    last = {}  # atom -> index of its last uncancelled hop
    for i, e in enumerate(hops):
        a = e["atoms"][0]; j = last.get(a)
        if j is not None and alive[j] and e["t_ps"] - hops[j]["t_ps"] <= WIN \
           and e["from_site"] == hops[j]["to_site"] and e["to_site"] == hops[j]["from_site"]:
            alive[i] = alive[j] = False; last.pop(a); continue
        last[a] = i
    return len(hops), sum(alive)

def order_screen(d):
    s = d["series"]; e0 = sum(p["epot_eV_atom"] for p in s[:5]) / 5
    onset = next((p["t_ps"] for p in s if p["epot_eV_atom"] - e0 > 0.03), None)
    return {"epot_start_eV_atom": round(e0, 4), "epot_end_eV_atom": round(s[-1]["epot_eV_atom"], 4),
            "n_vac_start": s[0]["n_vac"], "n_vac_end": s[-1]["n_vac"], "max_disp_end_A": round(s[-1]["max_disp_A"], 2),
            "order_lost_at_ps": onset, "crystalline": onset is None and s[-1]["n_vac"] == d["args"]["nvac"]}

runs = {}
for f in sorted(glob.glob(os.path.join(HERE, "out", "*es*_T*.json"))):
    d = json.load(open(f)); n, m = net_hops(d["events"])
    runs[os.path.basename(f)[:-5]] = {"T": d["args"]["T"], "si": d["args"]["si"], "prod_ps": d["prod_ps"],
        "n_sn": d["n_sn"], "sn_hops": n, "net_sn_hops": m, "cancelled_frac": round(1 - m / n, 3) if n else None,
        "vac_hops": d["counts"]["vac_hops"], "order": order_screen(d),
        "sn_next_to_vac_start": d["series"][0]["n_snv_pairs"]}

def o2(sel, label):
    byT = defaultdict(list)
    for k, r in runs.items():
        if r["si"] == 0 and sel(r): byT[r["T"]].append(r)
    rows = {}
    for T, rs in sorted(byT.items()):
        net = sum(r["net_sn_hops"] for r in rs); t_s = sum(r["prod_ps"] for r in rs) * 1e-12
        rows[T] = {"runs": len(rs), "net_sn_hops": net, "rate_per_s": net / t_s if net else 0.0,
                   "cancelled_frac": round(1 - net / max(1, sum(r["sn_hops"] for r in rs)), 3)}
    use = [T for T, r in rows.items() if r["net_sn_hops"] >= 3]
    out = {"label": label, "per_T": rows}
    flicker = bool(rows) and all(r["cancelled_frac"] > 0.9 for r in rows.values())
    out["vibration_check"] = {"cancelled_frac_by_T": {T: r["cancelled_frac"] for T, r in rows.items()}, "flicker_dominated": flicker}
    if len(use) >= 2:
        xs = [1 / (KB * T) for T in use]; ys = [math.log(rows[T]["rate_per_s"]) for T in use]
        ws = [rows[T]["net_sn_hops"] for T in use]; W = sum(ws)
        mx = sum(w * x for w, x in zip(ws, xs)) / W; my = sum(w * y for w, y in zip(ws, ys)) / W
        slope = sum(w * (x - mx) * (y - my) for w, x, y in zip(ws, xs, ys)) / sum(w * (x - mx) ** 2 for w, x in zip(ws, xs))
        out.update(mode="arrhenius", Ea_eV=round(-slope, 3), temperatures=use)
    else:
        Tm = max(rows); rs = [r for r in runs.values() if r["si"] == 0 and r["T"] == Tm and sel(r)]
        ttot = sum(r["prod_ps"] for r in rs) * 1e-12; nsv = sum(r["sn_next_to_vac_start"] for r in rs) / len(rs)
        out.update(mode="lower_bound", Ea_lower_bound_eV=round(KB * Tm * math.log(NU * ttot * max(nsv, 1)), 3), T_max=Tm)
    return out

def cat(ea):
    return "below 1.1 eV" if ea < 1.1 else ("close to the low-temperature metastable-film value (1.1 to 1.8 eV)" if ea <= 1.8 else
           ("between 1.8 and 2.9 eV" if ea < 2.9 else "close to the bulk Ge value (2.9 to 3.3 eV)" if ea <= 3.3 else "above 3.3 eV"))

res = {"registered": o2(lambda r: True, "all GeSn runs, as registered"),
       "screened": o2(lambda r: r["order"]["crystalline"], "GeSn runs that kept crystal order (disclosed addition)"),
       "runs": runs}
AT = os.path.join(MT, "ai_theorist", "answers"); grades = {}
for key in ("registered", "screened"):
    o = res[key]; g = {}
    for f in sorted(os.listdir(AT)):
        a = json.load(open(os.path.join(AT, f))); a = a.get("answers", a).get("O2")
        if not a: continue
        if o["mode"] == "arrhenius":
            c = cat(o["Ea_eV"]); v = a.get("value")
            g[f] = {"category": a["category"], "cat_hit": int(a["category"] == c),
                    "value": v, "value_hit": None if v is None else int(abs(v - o["Ea_eV"]) <= 0.15)}
        else:
            lb = o["Ea_lower_bound_eV"]
            hi = {"below 1.1 eV": 1.1, "close to the low-temperature metastable-film value (1.1 to 1.8 eV)": 1.8,
                  "close to the bulk Ge value (2.9 to 3.3 eV)": 3.3}.get(a["category"])
            g[f] = {"category": a["category"], "refuted": None if hi is None else int(hi < lb), "partly_graded": True}
    o["theorists"] = g
json.dump(res, open(os.path.join(HERE, "t1_result.json"), "w"), indent=1, default=str)
for k in ("registered", "screened"):
    print(k, json.dumps({kk: v for kk, v in res[k].items() if kk != "per_T"}, default=str))
    print("  per_T", res[k]["per_T"])
for k, r in runs.items(): print(k, r["net_sn_hops"], r["sn_hops"], r["vac_hops"], r["order"])
