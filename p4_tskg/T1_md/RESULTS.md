# P4 T1: MACE-MP-0 MD of GeSn with vacancies (collected 10 Oct 2026)

Runs: CHPC notchpeak-gpu-guest, arrays 16162739 (tasks 0-3) and 16162856
(tasks 4-6), 5.0 to 6.6 h each. Raw outputs hashed at campaign-record entries 143 before any
analysis; O2 reading at campaign-record entries 144; scope limit at campaign-record entries 145.

## What happened in the runs

| Run | Net Sn hops | All Sn hops | Vacancy hops | Vacancies start/end | Crystal order |
|---|---|---|---|---|---|
| GeSn 500 K, seed 1 | 22 | 242 | 231 | 2 / 2 | kept |
| GeSn 500 K, seed 2 | 24 | 292 | 260 | 2 / 2 | kept |
| GeSn 600 K, seed 1 | 4582 | 11998 | 2 | 2 / 3 | lost after 24 ps |
| GeSn 600 K, seed 2 | 4546 | 12198 | 0 | 8 / 8 | lost during equilibration |
| GeSn 700 K, seed 1 | 6063 | 13713 | 0 | 9 / 9 | lost during equilibration |
| GeSn 700 K, seed 2 | 6075 | 13895 | 0 | 26 / 26 | lost during equilibration |
| SiGeSn 600 K | 208 | 988 | 165 | 2 / 8 | lost after 484 ps |

At 500 K the lattice holds and Sn moves only by trading places with a
vacancy, as expected. At 600 and 700 K the model's crystal falls apart: the
potential energy rises by 0.06 to 0.11 eV per atom, the site finder counts
extra "vacancies", and thousands of Sn "hops" are atoms moving through a
disordered region, not vacancy jumps. Adding 10 % Si delays this by about
0.5 ns at 600 K but does not stop it.

## O2 (activation energy of Sn hops)

- **As registered:** the Arrhenius slope over 500, 600 and 700 K is
  0.13 eV. This number measures the onset of disorder in the model, not a
  barrier for Sn to move in a crystal. It is recorded and not used to grade.
  (Taken at face value it would mark theorist A's category right and B and C
  wrong.)
- **Restricted to runs that kept their order** (a check added after the
  runs, disclosed): only 500 K is left. The registered rule then returns
  kB T ln(nu t N) = 0.44 eV and labels it a lower bound. **Corrected
  2026-10-11 (campaign-record entries 150):** that expression is a lower bound only when no
  net hop is seen; it is the barrier at which one hop would be expected in
  the run. At 500 K, 46 net hops were seen, which with the same prefactor
  corresponds to about 0.28 eV. 91 % of Sn hops reverse within 10 ps
  (back-and-forth jumps with a nearby vacancy), so neither number bounds or
  estimates the Sn diffusion barrier. The ordered runs constrain the
  activation energy in neither direction, and O2 stays ungraded (grades
  unchanged).

## What this means for P4

- The model, not GeSn, sets the temperature limit. MACE-MP-0 puts the
  Ge0.88Sn0.12 lattice constant 2.8 % above Vegard's law (5.917 vs 5.758 A),
  a softer crystal, and in this model the crystal loses its order at 600 K within
  0.5 ns. Measured Ge0.88Sn0.12 films are annealed at 600 to 700 K and stay
  crystalline (strain relaxation can begin there and Sn leaves lattice sites only at
  about 820 to 870 K in published films, they do not disorder in
  picoseconds). So MACE-MP-0 MD of GeSn is scope-limited to 500 K and below
  (campaign-record entries 145).
- Hypothesis T1 (MD barriers vs the 2.9 to 3.3 eV bulk and 1.1 to 1.8 eV film
  activation energies) stays open. A test needs either a potential that
  keeps GeSn crystalline at 600 to 700 K (the newer MACE-MPA-0, or a
  fine-tuned model) or more 500 K time plus a 450 K point, so that two
  temperatures each have enough net hops.
- For the time-resolved hypergraph, only the two 500 K runs are loaded as
  defect events; the disordered runs are kept as a recorded model failure.

Files: `analyze_t1.py`, `t1_result.json`, `apply_t1.py`.
