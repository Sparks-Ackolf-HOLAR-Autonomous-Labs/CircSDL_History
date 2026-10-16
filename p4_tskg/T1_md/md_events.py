#!/usr/bin/env python3
"""P4 stage T1: MACE-MP-0 MD of Ge(1-x)Sn(x) with vacancies at anneal
temperatures, with defect events detected while the run goes and written as
hyper-TSKG material-clock events.

Version 2 (session 92). The session-90 smoke run counted thermal vibration
as events (first-shell cutoff crossings). Version 2 replaces the cutoff with
a Wigner-Seitz site analysis and adds a persistence rule:
  * every atom is assigned to its nearest site of the perfect diamond lattice
    (periodic KD-tree); a site with no atom is a vacancy;
  * an atom's site, and the set of vacant sites, change only when the new
    value has held for K consecutive snapshots (K fixed in the design);
  * the cell is set to the MACE zero-temperature lattice parameter of the
    vacancy-free alloy (scanned first), positions are relaxed, and the run
    is equilibrated for --eq-ps before any event is recorded.
Events (from the persistent state only):
  Sn hop            a Sn atom's site changes (the quantity behind question O2)
  vacancy hop       the vacant-site set changes
  Sn-V pairing      a Sn atom gains a vacant first-neighbour site
  Sn-V separation   the reverse
  Sn-Sn pairing     two Sn atoms on first-neighbour sites (counted, with and
                    without a vacancy next to the pair)
Usage: md_events.py --x 0.12 --nvac 2 --T 600 --ps 1000 --rep 4 --seed 1 --out run.json
       add --bench N to run N MD steps after equilibration and report s/step only.
"""
import argparse, json, os, time
import numpy as np
from ase.build import bulk
from ase.md.langevin import Langevin
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.optimize import FIRE
from ase import units
from scipy.spatial import cKDTree

ap = argparse.ArgumentParser()
ap.add_argument("--x", type=float, default=0.12)
ap.add_argument("--si", type=float, default=0.0, help="Si fraction (SiGeSn)")
ap.add_argument("--nvac", type=int, default=2)
ap.add_argument("--T", type=float, default=600)
ap.add_argument("--ps", type=float, default=10.0, help="production length after equilibration")
ap.add_argument("--eq-ps", type=float, default=5.0)
ap.add_argument("--every", type=int, default=50, help="steps between snapshots")
ap.add_argument("--K", type=int, default=4, help="persistence: snapshots a change must hold")
ap.add_argument("--rep", type=int, default=4)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--dt-fs", type=float, default=2.0)
ap.add_argument("--device", default="cuda")
ap.add_argument("--dtype", default="float32")
ap.add_argument("--model", default="medium")
ap.add_argument("--bench", type=int, default=0)
ap.add_argument("--out", required=True)
a = ap.parse_args()

from mace.calculators import mace_mp  # noqa: E402
calc = mace_mp(model=a.model, device=a.device, default_dtype=a.dtype)
rng = np.random.default_rng(a.seed)


def build(a0, with_vac=True):
    at = bulk("Ge", "diamond", a=a0, cubic=True).repeat((a.rep,) * 3)
    n = len(at)
    r = np.random.default_rng(a.seed)
    sym = np.array(["Ge"] * n, dtype=object)
    perm = r.permutation(n)
    nsn, nsi = int(round(a.x * n)), int(round(a.si * n))
    sym[perm[:nsn]] = "Sn"
    sym[perm[nsn:nsn + nsi]] = "Si"
    at.set_chemical_symbols(list(sym))
    sites = at.get_positions().copy()
    vac = []
    if with_vac:
        ge = [i for i in range(n) if sym[i] == "Ge"]
        vac = sorted(r.choice(ge, a.nvac, replace=False).tolist())
        del at[sorted(vac, reverse=True)]
    return at, sites, vac


# 1. zero-temperature lattice parameter of the vacancy-free alloy (5-point parabola)
a_vegard = 5.658 * (1 - a.x - a.si) + 6.489 * a.x + 5.431 * a.si
scan = []
for f in np.linspace(0.98, 1.04, 5):
    at0, _, _ = build(a_vegard * f, with_vac=False)
    at0.calc = calc
    scan.append((a_vegard * f, at0.get_potential_energy() / len(at0)))
cf = np.polyfit([s[0] for s in scan], [s[1] for s in scan], 2)
a0 = float(-cf[1] / (2 * cf[0]))

at, sites, vac0 = build(a0)
at.calc = calc
FIRE(at, logfile=None).run(fmax=0.05, steps=300)
L = a0 * a.rep
tree = cKDTree(sites % L, boxsize=L)
nsite = len(sites)
nb_i, nb_j = np.array(sorted(tree.query_pairs(a0 * np.sqrt(3) / 4 * 1.1))).T
neigh = [[] for _ in range(nsite)]
for p, q in zip(nb_i, nb_j):
    neigh[p].append(q); neigh[q].append(p)
isSn = np.array(at.get_chemical_symbols()) == "Sn"
sn_idx = np.where(isSn)[0]

MaxwellBoltzmannDistribution(at, temperature_K=a.T, rng=rng)
dyn = Langevin(at, a.dt_fs * units.fs, temperature_K=a.T, friction=0.01 / units.fs, rng=rng)
neq = int(round(a.eq_ps * 1000 / a.dt_fs))
t0 = time.time()
dyn.run(neq)
t_eq = time.time() - t0

if a.bench:
    t1 = time.time(); dyn.run(a.bench); dt = time.time() - t1
    import torch
    json.dump({"bench": True, "args": vars(a), "n_atoms": len(at), "a0_mace_A": a0, "a_vegard_A": a_vegard,
               "scan": scan, "s_per_step": dt / a.bench, "eq_s": t_eq,
               "gpu": torch.cuda.get_device_name(0) if a.device == "cuda" else "cpu"}, open(a.out, "w"), indent=1)
    print(f"{len(at)} atoms, {dt / a.bench * 1000:.1f} ms/step on {a.device}")
    raise SystemExit


def raw_state():
    d, s = tree.query(at.get_positions() % L)
    occ = np.bincount(s, minlength=nsite)
    return s, frozenset(np.where(occ == 0)[0].tolist()), float(d.max())


class Persist:
    """A value changes only after the new value held for K consecutive snapshots."""
    def __init__(self, v): self.v, self.cand, self.n = v, None, 0
    def update(self, v):
        if v == self.v: self.cand, self.n = None, 0; return False
        if v == self.cand: self.n += 1
        else: self.cand, self.n = v, 1
        if self.n >= a.K: self.v, self.cand, self.n = v, None, 0; return True
        return False


s0, V0, _ = raw_state()
site_of = {int(k): Persist(int(s0[k])) for k in range(len(at))}
vacset = Persist(V0)
events, series = [], []
nsteps = int(round(a.ps * 1000 / a.dt_fs))
counts = {"sn_hops": 0, "vac_hops": 0, "atom_hops": 0}


def snv_pairs():
    V = vacset.v
    return {(int(k), int(v)) for k in sn_idx for v in neigh[site_of[k].v] if v in V}


prev_pairs = snv_pairs()
t_prod0 = time.time()
for step in range(a.every, nsteps + 1, a.every):
    dyn.run(a.every)
    s, V, dmax = raw_state()
    t_ps = step * a.dt_fs / 1000
    for k in range(len(at)):
        old = site_of[k].v
        if site_of[k].update(int(s[k])):
            counts["atom_hops"] += 1
            if isSn[k]:
                counts["sn_hops"] += 1
                events.append({"t_ps": t_ps, "kind": "transition", "name": "Sn hop", "atoms": [k],
                               "from_site": old, "to_site": site_of[k].v,
                               "reaction": [[[1, "{Sn_Ge,V_Ge}"]], [[1, "{V_Ge,Sn_Ge}"]]]})
    oldV = vacset.v
    if vacset.update(V):
        counts["vac_hops"] += 1
        events.append({"t_ps": t_ps, "kind": "transition", "name": "vacancy hop",
                       "from_sites": sorted(oldV - vacset.v), "to_sites": sorted(vacset.v - oldV)})
    pairs = snv_pairs()
    for k, v in pairs - prev_pairs:
        events.append({"t_ps": t_ps, "kind": "reaction", "name": "Sn-V pairing", "atoms": [k], "site": v,
                       "reaction": [[[1, "Sn_Ge"], [1, "V_Ge"]], [[1, "{Sn_Ge,V_Ge}"]]]})
    for k, v in prev_pairs - pairs:
        events.append({"t_ps": t_ps, "kind": "reaction", "name": "Sn-V separation", "atoms": [k], "site": v,
                       "reaction": [[[1, "{Sn_Ge,V_Ge}"]], [[1, "Sn_Ge"], [1, "V_Ge"]]]})
    prev_pairs = pairs
    if step % (a.every * 20) == 0:
        snsites = {site_of[k].v for k in sn_idx}
        n_snsn = sum(1 for k in sn_idx for v in neigh[site_of[k].v] if v in snsites) // 2
        series.append({"t_ps": t_ps, "n_vac": len(vacset.v), "n_snv_pairs": len(pairs), "n_snsn_pairs": n_snsn,
                       "max_disp_A": dmax, "T_K": float(at.get_temperature()),
                       "epot_eV_atom": float(at.get_potential_energy() / len(at))})
wall = time.time() - t0
json.dump({"version": 2, "args": vars(a), "n_atoms": len(at), "n_sn": int(isSn.sum()), "n_sites": nsite,
           "a0_mace_A": a0, "a_vegard_A": a_vegard, "scan": scan, "vacancy_sites_start": vac0,
           "prod_ps": a.ps, "eq_ps": a.eq_ps, "counts": counts, "wall_s": wall,
           "prod_s_per_step": (time.time() - t_prod0) / max(nsteps, 1),
           "events": events, "series": series}, open(a.out, "w"), indent=1)
print(len(at), "atoms;", counts, f"{wall:.1f} s")
