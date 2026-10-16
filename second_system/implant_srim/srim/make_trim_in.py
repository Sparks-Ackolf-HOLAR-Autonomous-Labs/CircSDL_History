"""Write SRIM-2013 TRIM.IN batch inputs for the three install cross-check recipes.

Same recipes, atomic densities and surface binding energies as
../rustbca/smoke.py, so the two codes are compared on identical targets.
Quick (Kinchin-Pease) damage mode, as recommended by Stoller et al. (2013).
"""
import pathlib, sys
NA = 6.02214e23
EL = {"C": (6, 12.011, 7.37), "Si": (14, 28.0855, 4.72),
      "Ge": (32, 72.630, 3.85), "Sn": (50, 118.71, 3.12)}
N_SI, N_GE = 4.995e22, 4.416e22  # atoms per cm^3
CASES = [("C_Si_30keV", "C", 30, 0.0), ("C_Si0.8Ge0.2_30keV", "C", 30, 0.2),
         ("Sn_Ge_30keV", "Sn", 30, 1.0)]

def trim_in(name, ion, e_kev, x, n_ions=5000, width_A=20000):
    els = [e for e, f in (("Si", 1 - x), ("Ge", x)) if f > 0]
    frac = {"Si": 1 - x, "Ge": x}
    n = (1 - x) * N_SI + x * N_GE
    rho = n * sum(frac[e] * EL[e][1] for e in els) / NA
    Z, M, _ = EL[ion]
    L = ["==> SRIM-2013.00 This file controls TRIM Calculations.",
         "Ion: Z1 ,  M1,  Energy (keV), Angle,Number,Bragg Corr,AutoSave Number.",
         f"     {Z}   {M:.3f}   {e_kev}   0   {n_ions}   0   {n_ions + 1}",
         "Cascade Type[1=None;2=Full;3=Mono/Sputt;4-5=Ions(TRIM.dat);6-7=Recoils(TRIM.dat)], Random Number Seed, Reminders",
         "                      1                                   1       0",
         "Diskfiles (0=no,1=yes): Ranges, Backscatt, Transmit, Sputtered, Collisions(1=Ion;2=Ion+Recoils), Special EXYZ.txt file",
         "                          1       0           0       0               0                               0",
         "Target material : Number of Elements & Layers",
         f"\"{name:<40s}\"       {len(els)}               1",
         "PlotType (0-5); Plot Depths: Xmin, Xmax(Ang.) [=0 0 for Viewing Full Target]",
         f"       5                         0            {width_A}",
         "Target Elements:    Z   Mass(amu)"]
    for i, e in enumerate(els, 1):
        L.append(f"Atom {i} = {e} =        {EL[e][0]}  {EL[e][1]:.3f}")
    L += ["Layer   Layer Name /               Width Density " + " ".join(f"{e}({EL[e][0]})" for e in els),
          "Numb.   Description                (Ang) (g/cm3) " + " ".join("Stoich" for e in els),
          f" 1      \"SiGe\"           {width_A}  {rho:.4f} " + " ".join(f"{frac[e]:.4f}" for e in els),
          "0  Target layer phases (0=Solid, 1=Gas)", "0 ",
          "Target Compound Corrections (Bragg)", " 1 ",
          "Individual target atom displacement energies (eV)", " ".join("15" for e in els),
          "Individual target atom lattice binding energies (eV)", " ".join("2" for e in els),
          "Individual target atom surface binding energies (eV)", " ".join(str(EL[e][2]) for e in els),
          "Stopping Power Version (1=2008, 0=2008)", " 0 "]
    return "\r\n".join(L) + "\r\n"

if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for name, ion, e, x in CASES:
        (out / f"{name}.TRIM.IN").write_bytes(trim_in(name, ion, e, x).encode("ascii"))
        print(name)
