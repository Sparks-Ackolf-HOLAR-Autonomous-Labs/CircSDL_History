"""RustBCA install smoke test: ion ranges for three implant recipes.

Runs RustBCA (1D layered mode) for C->Si, C->Si0.8Ge0.2 and Sn->Ge at 30 keV,
normal incidence, and reports the mean projected range and straggle of the
stopped ions. These are cross-checked later against SRIM-2013 on sparksone.
Usage: python smoke.py /path/to/RustBCA/binary outdir
"""
import json, subprocess, sys, pathlib, numpy as np

EL = {  # Z, mass (amu), surface binding Es (eV), cutoff Ec (eV)
    "C": (6, 12.011, 7.37, 1.0), "Si": (14, 28.0855, 4.72, 1.0),
    "Ge": (32, 72.630, 3.85, 1.0), "Sn": (50, 118.71, 3.12, 1.0)}
N_SI, N_GE = 4.995e10, 4.416e10  # atoms per cubic micron (pure crystals)

def target(x_ge):
    n = (1 - x_ge) * N_SI + x_ge * N_GE  # Vegard-type atomic density
    return {"Si": (1 - x_ge) * n, "Ge": x_ge * n}

CASES = [("C_Si_30keV", "C", 30e3, target(0.0)),
         ("C_Si0.8Ge0.2_30keV", "C", 30e3, target(0.2)),
         ("Sn_Ge_30keV", "Sn", 30e3, target(1.0))]

def toml(name, ion, E, comp, n_ions=20000):
    els = [e for e in ("Si", "Ge") if comp[e] > 0]
    Z, m, Es, Ec = EL[ion]
    dens = ", ".join(f"{comp[e]:.4e}" for e in els)
    return f"""[options]
name = "{name}_"
track_trajectories = false
track_recoils = false
track_recoil_trajectories = false
write_buffer_size = 8000
weak_collision_order = 3
suppress_deep_recoils = false
high_energy_free_flight_paths = false
electronic_stopping_mode = "LOW_ENERGY_NONLOCAL"
mean_free_path_model = "LIQUID"
interaction_potential = [["KR_C"]]
scattering_integral = [["MENDENHALL_WELLER"]]
root_finder = [[{{"NEWTON"={{max_iterations=100, tolerance=1E-6}}}}]]
num_threads = 8
num_chunks = 10
track_displacements = false
track_energy_losses = false
energy_min = 0.0
energy_max = {E}
energy_num = 20
angle_min = 0.0
angle_max = 90.0
angle_num = 20
x_min = 0.0
y_min = -0.5
z_min = -0.5
x_max = 0.5
y_max = 0.5
z_max = 0.5
x_num = 50
y_num = 2
z_num = 2

[particle_parameters]
length_unit = "MICRON"
energy_unit = "EV"
mass_unit = "AMU"
N = [{n_ions}]
m = [{m}]
Z = [{Z}]
E = [{E}]
Ec = [{Ec}]
Es = [0.0]
interaction_index = [0]
pos = [[-1.0e-8, 0.0, 0.0]]
dir = [[0.9999999999, 0.0000141421, 0.0]]

[geometry_input]
length_unit = "MICRON"
densities = [[{dens}]]
layer_thicknesses = [2.0]
electronic_stopping_correction_factors = [1.0]

[material_parameters]
energy_unit = "EV"
mass_unit = "AMU"
Eb = [{", ".join("0.0" for e in els)}]
Es = [{", ".join(str(EL[e][2]) for e in els)}]
Ec = [{", ".join(str(EL[e][3]) for e in els)}]
Z = [{", ".join(str(EL[e][0]) for e in els)}]
m = [{", ".join(str(EL[e][1]) for e in els)}]
interaction_index = [{", ".join("0" for e in els)}]
surface_binding_model = {{"PLANAR"={{calculation="TARGET"}}}}
bulk_binding_model = "AVERAGE"
"""

def main(binary, outdir):
    out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    res = {}
    for name, ion, E, comp in CASES:
        f = out / f"{name}.toml"; f.write_text(toml(name, ion, E, comp))
        subprocess.run([binary, "1D", f.name], cwd=out, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        dep = np.loadtxt(out / f"{name}_deposited.output", delimiter=",", ndmin=2)
        x_nm = dep[:, 2] * 1e3  # columns: Z, m, x, y, z, collisions (micron)
        res[name] = {"ions_stopped": int(len(x_nm)),
                     "Rp_nm": round(float(x_nm.mean()), 1),
                     "dRp_nm": round(float(x_nm.std()), 1)}
        print(name, res[name])
    (out / "smoke_ranges.json").write_text(json.dumps(res, indent=1))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
