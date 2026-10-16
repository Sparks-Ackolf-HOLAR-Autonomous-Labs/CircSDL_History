"""Compare SRIM-2013 (sparksone) and RustBCA (DGX) ion ranges on identical recipes.

Reads srim/raw/<case>_RANGE_3D.txt and rustbca/run/smoke_ranges.json and
writes code_crosscheck.json with mean projected range Rp, straggle dRp and
the relative difference. Ions with depth <= 0 (backscattered) are excluded
from SRIM, matching RustBCA's deposited list.
"""
import json, pathlib, numpy as np
H = pathlib.Path(__file__).parent
rb = json.loads((H / "rustbca/run/smoke_ranges.json").read_text())
out = {}
for case, r in rb.items():
    rows = []
    for line in (H / f"srim/raw/{case}_RANGE_3D.txt").read_text(errors="ignore").splitlines():
        p = line.split()
        if len(p) == 4 and p[0].isdigit():
            rows.append(float(p[1]))
    x = np.array(rows) / 10.0  # Angstrom -> nm
    x = x[x > 0]
    s = {"ions_stopped": int(len(x)), "Rp_nm": round(float(x.mean()), 1),
         "dRp_nm": round(float(x.std()), 1)}
    out[case] = {"SRIM-2013": s, "RustBCA": r,
                 "Rp_diff_pct": round(100 * (r["Rp_nm"] - s["Rp_nm"]) / s["Rp_nm"], 1),
                 "dRp_diff_pct": round(100 * (r["dRp_nm"] - s["dRp_nm"]) / s["dRp_nm"], 1)}
    print(case, out[case])
(H / "code_crosscheck.json").write_text(json.dumps(out, indent=1))
