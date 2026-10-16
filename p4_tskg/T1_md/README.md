# P4 stage T1: MACE-MP-0 MD of GeSn with vacancies (prepared, not registered, not submitted)

Purpose (papers/26 section 4): run Ge(1-x)Sn(x) (x = 0.12) and
Si(0.1)Ge(0.78)Sn(0.12) with vacancies at anneal temperatures (500 to
700 K) and write defect events (Sn-vacancy pairing and separation, Sn-Sn
pairing, vacancy hops) as material-clock hyperedges while the run goes.

State on 2026-10-09:
- `md_events.py` written; smoke run on the DGX CPU only (62 atoms, 100
  steps, float64, 104 s): `smoke_cpu_62atoms_100steps.json`. This is a
  code check, not data.
- The smoke run shows the first fix needed before registration: thermal
  vibration moves neighbours across the 3.05 A cutoff, so the first
  snapshots report pairings that are not events. Add a persistence rule
  (a change counts only if it holds for k consecutive snapshots, k fixed in
  the design) and an initial relaxation before event detection starts.
- Cost is unmeasured on a GPU. First CHPC step: a 30-minute benchmark job
  on `notchpeak-gpu-guest` (the template is `../../p3_mace/chpc/sbatch_bench.sh`,
  same MACE module), then the design is written with the measured cost and
  registered on the campaign record before any production run.
- Needs a Duo approval for CHPC. The DGX GPU is not used (reserved).

Hypothesis T1 (papers/26 section 3.4) compares barriers of the events MD
finds with the activation energies reported for Sn segregation and
diffusion in the open literature; those reference values are collected in
`../T3_insitu/`.
