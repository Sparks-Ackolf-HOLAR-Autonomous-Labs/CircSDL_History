#!/usr/bin/env python3
"""Load the T3 literature series into the hyper-TSKG on the material clock.
One state node per (source, material), one process node per (series,
process recipe), one source node per DOI, and one measurement hyperedge per
data point linking the as-grown state, the process step, the source and a
value node. Time windows: anneal time in seconds where the series is
isothermal, otherwise 0 (the window is then the stated hold time, or 0 if
none) with the temperature kept on the value. Writes results/t3_tskg.json."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tskg import TSKG  # noqa: E402

S = json.load(open(os.path.join(HERE, "T3_insitu", "series.json")))
g = TSKG()
n_ev = 0
for s in S:
    src = g.node(f"src:{s['doi']}", "source", doi=s["doi"])
    m = s["material"]
    st = g.node(f"st:{s['doi']}:{m.get('composition')}:{m.get('film_thickness_nm')}", "state",
                composition=m.get("composition"), labels=["as-received"], substrate=m.get("substrate"))
    pr = s["process"]
    proc = g.node(f"proc:{s['series_id']}", "process", step=pr.get("mode"), recipe=pr)
    xq = (s.get("x_quantity") or "").lower()
    timed = "time" in xq or pr.get("mode") == "isothermal"
    hold = (pr.get("times_s") or [0])[0] or 0
    for k, p in enumerate(s["points"]):
        x = p[0]
        win = (float(x) * (60 if "min" in xq else 3600 if xq.endswith("(h)") else 1), ) * 2 if timed and isinstance(x, (int, float)) else (0.0, float(hold))
        v = g.node(f"val:{s['series_id']}:{k}", "claim", observable=s["observable"], unit=s["unit"], x=x, x_quantity=s.get("x_quantity"),
                   value=p[1], uncertainty=p[2] if len(p) > 2 else None, extraction=s["extraction_method"])
        g.event(f"ev:{s['series_id']}:{k}", "measurement", "material", win, before=[st], after=[v], process=proc, source=src,
                labels=[s["extraction_method"]])
        n_ev += 1
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
g.dump(os.path.join(HERE, "results", "t3_tskg.json"))
st = g.stats()
st["series"] = len(S)
json.dump(st, open(os.path.join(HERE, "results", "t3_tskg_stats.json"), "w"), indent=1)
print(json.dumps(st))
