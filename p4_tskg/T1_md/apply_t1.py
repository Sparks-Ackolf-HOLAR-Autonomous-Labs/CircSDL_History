#!/usr/bin/env python3
"""Ledger the O2 result (analysis) and the scope limit it implies for MACE-MP-0 GeSn MD."""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); MT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(MT, "pilot", "src"))
from ledger import Ledger  # noqa: E402
led = Ledger(os.path.join(MT, "phase_c", "ledger_campaign.jsonl"))
r = json.load(open(os.path.join(HERE, "t1_result.json")))
sha = lambda p: hashlib.sha256(open(os.path.join(MT, p), "rb").read()).hexdigest()
fs = ["p4_tskg/T1_md/analyze_t1.py", "p4_tskg/T1_md/t1_result.json"]
a = led.append("analysis", {"op_id": "p4-t1-o2", "rests_on": [126, 143], "files_sha256": {f: sha(f) for f in fs},
    "registered_reading": {"Ea_eV": r["registered"]["Ea_eV"], "mode": "arrhenius 500-700 K",
                           "grades": {k: v for k, v in r["registered"]["theorists"].items()}},
    "disclosed_addition": "crystal-order screen not in the registration: 600 K and 700 K GeSn runs lost crystal order "
        "(potential energy +0.06 to +0.11 eV/atom above 500 K, vacancy count grows from 2 to up to 26); "
        "restricted to the two 500 K runs, O2 is a lower bound only",
    "screened_reading": {"Ea_lower_bound_eV": r["screened"]["Ea_lower_bound_eV"], "flicker_dominated_500K": True,
                         "categories_refuted": []},
    "statement": "registered O2 value 0.13 eV is a melting/disorder artefact, not a vacancy-hop barrier; reported, not used to grade"})
s = led.append("shard_operation", {"op": "scope_limit", "op_id": "scope-p4-t1-mace-mp0-gesn-T", "rests_on": [143, a["seq"]],
    "claim": "MACE-MP-0 medium MD of Ge0.88Sn0.12 (and Si0.10Ge0.78Sn0.12) with vacancies",
    "scope": "T <= 500 K for 0.5 ns runs of 510 atoms; above that the lattice disorders in the model",
    "cause": "model artefact: MACE-MP-0 lattice constant 5.917 A vs Vegard 5.758 A (+2.8 %); GeSn at x = 0.12 is processed "
             "at 600-700 K in practice without losing crystal order",
    "consequence": "O2 and hypothesis T1 stay open; the defect-event hypergraph keeps only the 500 K runs"})
assert led.verify_chain(); print(a["seq"], s["seq"])
