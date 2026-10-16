# Ion implantation as a doping route: where SRIM/TRIM fits (2026-10-09)

Question: are new simulations needed, and should SRIM/TRIM (Ziegler,
http://www.srim.org/) be used for the doping set-up? This note answers it
and proposes a chain. No compute was launched;
SRIM is not installed anywhere yet.

Literature: Asta MCP searches q102-q110 and batch verification q111 in
`asta/` (every DOI below resolves to the stated paper in Asta).

## 1. What SRIM computes, in laboratory terms

SRIM (TRIM is its Monte Carlo engine) follows each implanted ion through the
target as a series of two-body collisions and electronic drag. For a chosen
ion, energy, dose and tilt it returns:

1. the depth profile of the implanted atoms (projected range and straggle);
2. the displacement damage: vacancies and interstitials per ion versus depth;
3. sputtering yield at the surface.

Reference: Ziegler, Ziegler and Biersack, Nucl. Instrum. Methods B 268,
1818 (2010), doi 10.1016/j.nimb.2010.02.091.

## 2. P1-P3 as drafted: no new simulation needed

In P1-P3 the dopant (B, P) enters sintered bulk material uniformly and acts
on heat flow only as a mass defect on lattice sites (at most 0.43% of
kappa_L); carbon enters as SiC precipitates whose location was settled by
MACE. None of the three papers has an implanted sample, so a SRIM profile
would change no reported number.

One optional addition: P1 recommends few-nanometre SiC formed in place. A
known route to that microstructure is ion-beam synthesis of SiC by carbon
implantation into Si followed by annealing (for example doi
10.1016/S0168-583X(01)00504-3; doi 10.1016/J.NIMB.2019.02.026), and SiGeC
layers have been made by C implantation and solid-phase epitaxy (doi
10.1063/1.117620). A SRIM run would turn the recommendation into an implant
recipe (energy and dose for 1 to 3 at% C over a chosen depth) for the
practical-implications paragraph. It adds a recipe, not a result.

## 3. The proposed SiGeSn and GaP-SiGe(C/Sn) chapters: yes, and SRIM fits there

Those chapters need new simulations in any case. Implantation
is a standard way the added elements enter thin-film devices in exactly
these systems:

| System | Implantation route in the literature | DOI |
|---|---|---|
| GeSn | Sn implantation plus pulsed laser melting | 10.1063/1.4891848; 10.1063/1.4948960 |
| SiGeSn | Sn implant source/drain stressors in strained-Si transistors | 10.1109/IEDM.2007.4418882; 10.1109/VTSA.2008.4530830 |
| SiGeC | C implantation and solid-phase epitaxy; C to suppress B diffusion in HBTs | 10.1063/1.117620; 10.1063/1.119110 |
| Ga in SiGe | Ga implant in high-Ge SiGe, laser activation | 10.1149/2162-8777/abe2ee; 10.23919/VLSIT.2017.7998176 |

This matters for the story because implantation is the clearest case of the
decision-to-sample edge in `../../papers/notes/23_decision_data_story_2026-10-09.md`:
the chosen ion, energy, dose and anneal decide the depth profile, the defect
population and whether the layer amorphises, and the measured conductivity
belongs to that processed layer. Damage, not dopant mass, controls the heat
flow of an implanted layer: self-ion irradiation of crystals separates the
point- and extended-defect contributions (Scott et al., Phys. Rev. Mater. 2,
095001 (2018), doi 10.1103/PhysRevMaterials.2.095001), and the conductivity
of Kr-implanted Si varies with depth along the damage profile (doi
10.1063/5.0094876). Both are measured validation targets for the chain below.

### Proposed chain (draft, for discussion)

1. **Profiles.** SRIM (or an open binary-collision code, below) for each
   recipe: added-atom profile and vacancy profile in Si(1-x)Ge(x)(C, Sn).
2. **Damage retained.** SRIM counts every displacement at 0 K and in an
   amorphous target; in crystalline Si most Frenkel pairs recombine. Use the
   Kinchin-Pease (quick calculation) setting recommended by Stoller et al.
   (doi 10.1016/j.nimb.2013.05.008; Weber and Zhang 2019 for multi-element
   targets, doi 10.1016/j.cossms.2019.06.001) and treat the retained
   fraction as an uncertain input calibrated against the two measured cases
   above. Short MD cascade runs (Tersoff or MACE) only as spot checks.
3. **Heat flow per depth slice.** Feed local composition and defect
   concentration into the existing BTE-plus-scattering model (vacancy as a
   strong point scatterer) to get a depth-resolved kappa and an effective
   film value.
4. **Validation gate before any claim.** Reproduce the Kr-implanted Si
   depth profile and the Scott et al. trend within a tolerance fixed in a
   campaign record pre-registration.

The retained-damage fraction is exactly the kind of weakly supported input
the provenance graph is built to name in advance, so the chain also tests
the method.

### Limits stated up front

- SRIM treats the target as amorphous (no channelling), at 0 K, with no
  recombination; vacancy counts are upper bounds.
- TRIM keeps the target composition fixed during the run. At the Sn doses
  used for GeSn (order 1e16 per cm2) sputtering and accumulation change the
  surface layer; a dynamic binary-collision code (SDTrimSP or TRIDYN class)
  would be needed there (to be cited from a verified record before use).
- Neither code models annealing, laser melting, regrowth or Sn segregation.
  Those are separate steps and would enter as their own processing variables.

## 4. Where it can run, and licence

| Option | Where | Note |
|---|---|---|
| SRIM-2013 | sparksone (Windows 10) | Windows-only executable; batch mode via TRIM.IN. Installation adds system components on sparksone. Licence: free for non-commercial use (srim.org download conditions), which covers this academic work; version must be disclosed. |
| RustBCA (Drobny and Curreli, JOSS 2021, doi 10.21105/joss.03298) | DGX or CHPC | Open source, builds from source; usable as an independent cross-check of SRIM on one shared recipe. |

Cost: minutes per recipe for profiles; the BTE step is seconds. No CHPC
allocation is needed except for optional MD cascades on guest partitions.
