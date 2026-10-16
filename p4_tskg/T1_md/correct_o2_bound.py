#!/usr/bin/env python3
"""Correct the reading of O2 restricted to ordered runs (review, 11 Oct 2026).

The registered rule returns E_a > kB T ln(nu t N) whenever fewer than two
temperatures have three or more net hops. That expression is a lower bound
only when no net hop is seen: it is the barrier at which one escape is
expected in the run. At 500 K, 46 net hops were seen, so 0.444 eV is not a
lower bound; with the same prefactor the observed hops correspond to about
kB T ln(nu t N / 46). Since 91 % of hops reversed within 10 ps, the hops are
back-and-forth jumps next to a vacancy and give no diffusion barrier.
"""
import hashlib, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); MT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(MT, "pilot", "src"))
from ledger import Ledger  # noqa: E402
KB, NU = 8.617333262e-5, 1e13
r = json.load(open(os.path.join(HERE, "t1_result.json")))
s = r["screened"]; n = s["per_T"]["500.0"]["net_sn_hops"]
runs = [v for v in r["runs"].values() if v["si"] == 0 and v["T"] == 500.0 and v["order"]["crystalline"]]
t = sum(v["prod_ps"] for v in runs) * 1e-12; N = sum(v["sn_next_to_vac_start"] for v in runs) / len(runs)
one_event = KB * 500 * math.log(NU * t * N); observed = KB * 500 * math.log(NU * t * N / n)
assert abs(one_event - s["Ea_lower_bound_eV"]) < 2e-3
led = Ledger(os.path.join(MT, "phase_c", "ledger_campaign.jsonl"))
sha = lambda p: hashlib.sha256(open(os.path.join(MT, p), "rb").read()).hexdigest()
fs = ["p4_tskg/T1_md/t1_result.json", "p4_tskg/T1_md/correct_o2_bound.py"]
e = led.append("shard_operation", {"op": "correct", "op_id": "correct-p4-t1-o2-bound", "rests_on": [126, 144],
    "files_sha256": {f: sha(f) for f in fs},
    "claim": "O2 restricted to the runs that kept crystal order: 'Ea > 0.44 eV (lower bound)'",
    "cause": "label error in the registered rule: kB T ln(nu t N) bounds Ea from below only when no net hop is seen; "
             "46 net hops were seen at 500 K",
    "detection": "full-text review of P4, 2026-10-11",
    "corrected_reading": {"one_event_barrier_eV": round(one_event, 3), "observed_hop_rate_barrier_eV": round(observed, 3),
                          "net_hops_500K": n, "cancelled_frac_500K": s["per_T"]["500.0"]["cancelled_frac"],
                          "meaning": "the 500 K hops are back-and-forth jumps next to a vacancy; neither number bounds or "
                                     "estimates the Sn diffusion barrier; no MD constraint on Ea in either direction"},
    "consequence": "O2 stays ungraded (as before); grades unchanged; text that called 0.44 eV a lower bound is corrected in P1 ESI, P2 SI, P4",
    "statement": "0.44 eV relabelled: not a lower bound on the hop activation energy"})
assert led.verify_chain(); print(e["seq"], round(one_event, 3), round(observed, 3))
