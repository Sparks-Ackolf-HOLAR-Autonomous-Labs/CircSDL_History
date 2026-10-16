#!/usr/bin/env python3
"""Ledger entry for the P4 T1 design (before any production output)."""
import hashlib, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); MT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(MT, "pilot", "src"))
from ledger import Ledger  # noqa: E402
sha = lambda p: hashlib.sha256(open(os.path.join(HERE, p), "rb").read()).hexdigest()
files = ["t1_design.json", "md_events.py", "o1_binding.py", "sbatch_md.sh", "sbatch_o1.sh",
         "bench/bench_rep4.json", "bench/bench_rep5.json",
         "smoke_v2_cpu_62atoms_0p4ps.json", "smoke_o1_cpu_x006_rep2_fmax01.json"]
led = Ledger(os.path.join(MT, "phase_c", "ledger_campaign.jsonl"))
e = led.append("commitment", {
    "op_id": "p4-t1-design", "rests_on": [122, 123, 125],
    "files_sha256": {f"p4_tskg/T1_md/{f}": sha(f) for f in files},
    "tests_open_predictions": ["O1", "O2"],
    "statement": "P4 T1 MACE-MP-0 MD of GeSn/SiGeSn with vacancies and the O1 static check, design and grading rules fixed before any production output; smoke outputs disclosed",
})
assert led.verify_chain(); print("seq", e["seq"], e["entry_hash"])
