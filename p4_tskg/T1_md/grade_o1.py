#!/usr/bin/env python3
"""Apply the O1 rule registered at ledger 126 to the raw output committed at 131 and grade the theorists."""
import hashlib, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); MT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(MT, "pilot", "src"))
from ledger import Ledger  # noqa: E402
led = Ledger(os.path.join(MT, "phase_c", "ledger_campaign.jsonl"))
for f, h in led.entries[131]["payload"]["raw_sha256"].items():
    assert hashlib.sha256(open(os.path.join(MT, f), "rb").read()).hexdigest() == h, f
d = json.load(open(os.path.join(HERE, "out", "o1_x012_rep4.json")))
eb = [s["E_b_eV"] for s in d["samples"] if all(s["converged"])]
n = len(eb)
res = {"n_samples": len(d["samples"]), "n_converged": n, "E_b_per_sample_eV": [round(x, 4) for x in eb],
       "E_b_mean_eV": d["E_b_mean_eV"], "E_b_sd_eV": d["E_b_sd_eV"],
       "dilute_Ge_E_b_eV": d["dilute_Ge"]["E_b_eV"] if d.get("dilute_Ge") else None,
       "a0_mace_A": d["a0_mace_A"], "a0_Ge_mace_A": d["a0_Ge_mace_A"]}
if n < 5:
    res["graded"] = False
else:
    m = d["E_b_mean_eV"]
    cat = "bound by more than 0.3 eV" if m > 0.3 else ("bound by 0 to 0.3 eV" if m >= 0 else "unbound")
    res.update(graded=True, category=cat)
    AT = os.path.join(MT, "ai_theorist", "answers")
    g = {}
    for f in sorted(os.listdir(AT)):
        a = json.load(open(os.path.join(AT, f)))
        a = a.get("answers", a)["O1"]
        v = a.get("value")
        vh = None if v is None else int(abs(v - m) <= 0.10 or (v > 0 and m > 0 and abs(math.log(v / m)) <= 0.3))
        g[f] = {"category": a.get("category"), "cat_hit": None if a.get("category") is None else int(a["category"] == cat),
                "value": v, "value_hit": vh}
    res["theorists"] = g
json.dump(res, open(os.path.join(HERE, "o1_result.json"), "w"), indent=1)
print(json.dumps(res, indent=1))
