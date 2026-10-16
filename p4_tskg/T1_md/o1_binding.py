#!/usr/bin/env python3
"""P4 stage T1, question O1: MACE-MP-0 static Sn-vacancy binding energy in
Ge(1-x)Sn(x).

For each sample (random alloy configuration and one chosen Sn atom):
  E_near: vacancy on a first-neighbour Ge site of the chosen Sn atom;
  E_far:  vacancy on a Ge site whose first and second neighbour shells hold
          no Sn atom, as far from the chosen Sn as the cell allows;
  E_b = E_far - E_near   (positive = Sn and vacancy bound).
Both cells keep the same atoms and composition; positions are relaxed
(FIRE, fmax 0.01 eV/A, cell fixed at the MACE lattice parameter of the
vacancy-free alloy). The split-vacancy configuration (Sn relaxing to the
bond centre) is allowed by the relaxation and is recorded through the Sn
displacement.
A dilute reference (one Sn in pure Ge) is computed the same way.
Usage: o1_binding.py --x 0.12 --rep 4 --samples 8 --seed 1 --out o1.json
"""
import argparse, json, time
import numpy as np
from ase.build import bulk
from ase.optimize import FIRE
from scipy.spatial import cKDTree

ap = argparse.ArgumentParser()
ap.add_argument("--x", type=float, default=0.12)
ap.add_argument("--rep", type=int, default=4)
ap.add_argument("--samples", type=int, default=8)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--fmax", type=float, default=0.01)
ap.add_argument("--device", default="cuda")
ap.add_argument("--model", default="medium")
ap.add_argument("--out", required=True)
a = ap.parse_args()

from mace.calculators import mace_mp  # noqa: E402
calc = mace_mp(model=a.model, device=a.device, default_dtype="float64")


def lattice(x, rep, seed):
    av = 5.658 * (1 - x) + 6.489 * x
    best = None
    pts = []
    for f in np.linspace(0.98, 1.04, 5):
        at = alloy(x, rep, av * f, seed)
        at.calc = calc
        pts.append((av * f, at.get_potential_energy() / len(at)))
    cf = np.polyfit(*zip(*pts), 2)
    return float(-cf[1] / (2 * cf[0])), pts


def alloy(x, rep, a0, seed, nsn=None):
    at = bulk("Ge", "diamond", a=a0, cubic=True).repeat((rep,) * 3)
    n = len(at)
    r = np.random.default_rng(seed)
    k = int(round(x * n)) if nsn is None else nsn
    sym = np.array(["Ge"] * n, dtype=object)
    sym[r.permutation(n)[:k]] = "Sn"
    at.set_chemical_symbols(list(sym))
    return at


def relaxed_energy(at, vac):
    b = at.copy()
    del b[[vac]]
    b.calc = calc
    p0 = b.get_positions().copy()
    opt = FIRE(b, logfile=None)
    conv = opt.run(fmax=a.fmax, steps=1500)
    d = np.linalg.norm(b.get_positions() - p0, axis=1)
    return float(b.get_potential_energy()), bool(conv), int(opt.nsteps), float(d.max())


def one(x, rep, a0, seed, sn_pick):
    at = alloy(x, rep, a0, seed, nsn=1 if x == 0 else None)
    L = a0 * rep
    pos = at.get_positions()
    tree = cKDTree(pos % L, boxsize=L)
    sym = np.array(at.get_chemical_symbols())
    sn = np.where(sym == "Sn")[0]
    s = int(sn[sn_pick % len(sn)])
    r1 = a0 * np.sqrt(3) / 4 * 1.1
    r2 = a0 / np.sqrt(2) * 1.05
    nn = [j for j in tree.query_ball_point(pos[s] % L, r1) if j != s and sym[j] == "Ge"]
    if not nn:
        return None
    near = int(nn[0])
    d_all = np.linalg.norm(((pos - pos[s]) + L / 2) % L - L / 2, axis=1)
    cand = [j for j in np.argsort(-d_all) if sym[j] == "Ge" and
            not any(sym[k] == "Sn" for k in tree.query_ball_point(pos[j] % L, r2) if k != j)]
    if not cand:
        return None
    far = int(cand[0])
    en, cn, sn_, dn = relaxed_energy(at, near)
    ef, cfar, sf, df = relaxed_energy(at, far)
    return {"seed": seed, "sn_atom": s, "near_site": near, "far_site": far, "far_dist_A": float(d_all[far]),
            "E_near": en, "E_far": ef, "E_b_eV": ef - en, "converged": [cn, cfar], "steps": [sn_, sf],
            "max_disp_near_A": dn, "max_disp_far_A": df}


t0 = time.time()
a0, scan = lattice(a.x, a.rep, a.seed)
rows = []
for i in range(a.samples):
    r = one(a.x, a.rep, a0, a.seed + i, i)
    if r:
        rows.append(r)
a0d, scand = lattice(0.0, a.rep, a.seed)
dil = one(0.0, a.rep, a0d, a.seed, 0)
eb = [r["E_b_eV"] for r in rows if all(r["converged"])]
json.dump({"args": vars(a), "a0_mace_A": a0, "scan": scan, "samples": rows,
           "E_b_mean_eV": float(np.mean(eb)) if eb else None, "E_b_sd_eV": float(np.std(eb, ddof=1)) if len(eb) > 1 else None,
           "n_converged": len(eb), "dilute_Ge": dil, "a0_Ge_mace_A": a0d, "wall_s": time.time() - t0},
          open(a.out, "w"), indent=1)
print("E_b", np.mean(eb) if eb else None, "n", len(eb), "dilute", dil["E_b_eV"] if dil else None)
