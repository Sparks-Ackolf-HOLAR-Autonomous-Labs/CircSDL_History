#!/usr/bin/env python3
"""Hash the T1 MD outputs onto the ledger before the O2 rule (ledger 126) is applied."""
import glob, hashlib, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); MT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(MT, "pilot", "src"))
from ledger import Ledger  # noqa: E402
fs = sorted(glob.glob(os.path.join(HERE, "out", "gesn_*.json")) + glob.glob(os.path.join(HERE, "out", "sigesn_*.json")))
assert fs, "no MD outputs"
led = Ledger(os.path.join(MT, "phase_c", "ledger_campaign.jsonl"))
e = led.append("batch_commitment", {"op_id": "p4-t1-md-raw", "prereg_seq": [126], "placement_seq": [127],
    "raw_sha256": {os.path.relpath(f, MT): hashlib.sha256(open(f, "rb").read()).hexdigest() for f in fs},
    "statement": f"{len(fs)} of 7 T1 MD outputs committed before the O2 rule is applied"})
assert led.verify_chain(); print("seq", e["seq"], len(fs), "files")
