# P4 stage T3: open in-situ and anneal series for GeSn and SiGeSn (2026-10-09)

Stage T3 of the time-resolved evidence hypergraph (doc
`papers/notes/26_labels_and_hyper_tskg_2026-10-09.md`, sections 3.3 and 4) collects
open literature data on how GeSn and SiGeSn films change during annealing. No
instrument time and no HPC were used. Every number in `series.json` traces to a
sentence, a table or a figure of a source whose DOI was checked against Crossref.
The two arXiv-only preprints were checked against the arXiv API instead.

## Files

| File | Content |
|---|---|
| `series.json` | 163 series. Each records the material, process recipe, observable, unit, points `[x, value, uncertainty]`, extraction method and the verbatim source sentence or figure panel |
| `sources.csv` | 33 sources examined: Crossref title, first author, year and venue as Crossref returns them, open-access flag, number of series, and what each source was used for |
| `../../second_system/asta/q103_*.json` to `q131_*.json` | raw Asta search, snippet and batch-lookup results for this stage |

Extraction methods across the 163 series: 56 from text, 43 from tables and 64
read from figures by eye. Each figure-read series records its reading
uncertainty and how it was read. Abstract-only values are labelled as such in
`notes`.

## What was found

**Sources.** 33 sources were examined and 24 contribute series. The other 9
were examined but gave no usable values:

- 5 are behind paywalls or publisher bot protection: Cai 2022 (one of the three
  named starting candidates), Zaumseil 2018, Olorunsola 2021, Panayiotatos
  2017 and Chroneos 2011.
- 3 have no anneal numbers: Nicolas 2020, Sadofyev 2015 and Steuer 2024.
- Wahl 2020 studies Sn in diamond, not Ge, and is excluded.

Of the three starting candidates:

- Comrie 2016 (6 series) is open through the KU Leuven repository.
- Higashiyama 2019 (34 series) is open through the Kyutech repository.
- Cai 2022 is closed and has no public abstract, so it contributes nothing.

**Series by kind.**

| Kind | Series | With at least 3 distinct x values |
|---|---|---|
| Isothermal: value against anneal time at one temperature | 9 | 6 |
| In-situ ramp or stepwise in-situ heating | 29 | 9 |
| Isochronal: fixed time, varying temperature | 57 | 45 |
| Single anneal: before and after | 50 | 1 |
| Arrhenius parameters and energies | 18 | not applicable |

**Time resolution.** Six series have true time resolution. All six come from
one preprint (Attiaoui et al., arXiv:2609.17504, 2026), which used in-situ
spectroscopic ellipsometry on Si0.08Ge0.88Sn0.04 held at 550 C. The two samples,
uncapped and capped with 3 nm SiO2, each have three observables: the shift in
the E2 critical-point energy, its broadening, and its amplitude. Each series
has 12 to 13 points over about 130 min.

- **Uncapped film.** After a 50 min incubation, the E2 energy rises along a
  logistic curve with midpoint t0 = 74.2 ± 0.5 min and width w = 1.86 ± 0.15 min,
  then saturates at 423 meV. The E2 shift tracks loss of substitutional Sn near
  the surface.
- **Capped film.** The oxide cap suppresses this change.

The nine in-situ ramp series with at least 3 points are from Higashiyama 2019,
an in-situ TEM study of amorphous GeSn heated step by step. They give lattice
parameter and substitutional Sn against temperature. Hold times are not stated,
so they are temperature series, not time series.

Two further paywalled sources are known to contain time series, but only their
abstracts are open:

- Stanchu 2023 (300 C, Sn particle density over hours; only the 2 h peak of
  3.5e8 cm-2 is open).
- Fournier-Lupien 2014 (in-situ LEEM and PEEM).

**Main temperature series** (isochronal):

- Comrie 2016, Ge0.935Sn0.065: substitutional Sn fraction and tetragonal
  distortion against temperature, 300 to 700 C, 20 min each.
- Jia 2020: relaxation, lattice constants and Sn content, 300 to 600 C, 5 min
  each.
- Takase 2016, amorphous Ge0.862Sn0.138 crystallizing: lattice parameter,
  substitutional Sn, grain size.
- Decoster 2010, implanted Sn in Ge: fractions of Sn on substitutional and on
  split-vacancy sites, room temperature to 400 C.
- Von den Driesch 2020: Sn and Si diffusion coefficients at 14 temperatures from
  500 to 850 C, in GeSn and in SiGeSn.

**SiGeSn coverage.** 38 series concern Si-containing material:

- von den Driesch 2020: Si0.10Ge0.81Sn0.09 (uncapped relaxation samples) and
  Si0.040Ge0.895Sn0.065 (Ge-capped diffusion samples).
- Attiaoui 2026: Si0.08Ge0.88Sn0.04.
- Fournier-Lupien 2014: Ge0.84Si0.04Sn0.12, abstract only.
- Kringhoj 1994: implanted Sn in SiGe.

## Reported activation energies for Sn diffusion and segregation in Ge, GeSn and SiGeSn

| Process | Material | Ea (eV) | D0 (cm2/s) | Kind | DOI |
|---|---|---|---|---|---|
| Sn diffusion, implanted | Ge | 3.05 | 70 (quoted by Lieten 2014 as "70 exp(-3.05 eV/kT)" from its ref. 29, a germanium handbook (Claeys and Simoen), not from Kringhoj; Kringhoj gives the 3.05 eV only) | measured, SIMS | 10.1063/1.112360 |
| Sn diffusion, implanted | Si0.47Ge0.53 | 3.88 | not in abstract | measured | 10.1063/1.112360 |
| Sn diffusion, implanted | Si0.79Ge0.21 | 4.61 | not in abstract | measured | 10.1063/1.112360 |
| Sn diffusion, implanted | Si | 4.91 | not in abstract | measured | 10.1063/1.112360 |
| Sn interdiffusion, above about 650 C | Ge-capped Ge0.94Sn0.06 | 3.10 ± 0.07 | 264 ± 220 | measured, SIMS | 10.1103/PhysRevMaterials.4.033604 |
| Sn interdiffusion, above about 650 C | Ge-capped Si0.040Ge0.895Sn0.065 | 2.87 ± 0.03 | 12 ± 5 | measured | same |
| Sn interdiffusion, below about 650 C (enhanced regime) | Ge-capped Ge0.94Sn0.06 | 1.81 ± 0.09 | not given | measured | same |
| Sn interdiffusion, below about 650 C | Ge-capped Si0.040Ge0.895Sn0.065 | 1.13 ± 0.10 (text) or ± 0.11 (table) | not given | measured | same |
| Si diffusion, above about 700 C | Ge-capped Si0.040Ge0.895Sn0.065 | 3.27 ± 0.03 | 31 ± 9 | measured | same |
| Si diffusion, below about 700 C | Ge-capped Si0.040Ge0.895Sn0.065 | 0.50 ± 0.10 | not given | measured | same |
| Ge-Sn interdiffusion, fit over 380 to 450 C (anneals 300 to 600 C) | strained Ge/Ge0.9Sn0.1 multiple quantum wells | 1.21 | 2.9e-7 (quoted by Xia, arXiv:1901.10105, eq. 11) | measured, HRXRD satellite decay; abstract + review (article closed); added 2026-10-14 | 10.1088/0022-3727/49/22/225102 |
| Sn diffusion through SnV pairs, Fermi-level dependent | Ge | 2.48 to 3.65 | not applicable | DFT, GGA+U | 10.1063/1.3653472 |
| Sn bulk diffusion | SiGeSn context | 2.6 to 2.7 | not given | quoted (Brotzmann 2008) | arXiv:2609.17504 |
| Sn pipe diffusion along dislocations | SiGeSn context | 1.5 to 1.8 | not given | asserted, no reference | arXiv:2609.17504 |

Composition note (corrected 2026-10-11 from full-text snippets, Asta q13/q14 in
`asta_search_results/literature_2026-10-11/`): von den Driesch 2020 used two
sample sets. The uncapped relaxation samples were Ge0.914Sn0.086 and
Si0.10Ge0.81Sn0.09 (corrected again on 2026-10-11 from the full text,
arXiv:1911.02334, which gives Ge0.914Sn0.086, not Ge0.92Sn0.08); the activation energies come from the Ge-capped films
Ge0.94Sn0.06 and Si0.040Ge0.895Sn0.065, as in `series.json`. An earlier
version of this table put the relaxation-sample compositions on the
diffusion values.

Von den Driesch 2020 also states a literature spread of 2.90 to 3.26 eV for
implanted Sn in Ge.

**Sn-vacancy energetics**, the closest available to a vacancy-Sn binding
energy:

- **Decoster 2010 (DFT).** Heat of formation 0.19 eV for substitutional Sn and
  2.23 eV for the neutral vacancy, so 2.42 eV for the unbound pair, against
  1.86 eV for the split-vacancy SnV complex. The binding energy implied by the
  difference is 0.56 eV. The paper gives the components; the difference was
  computed here.
- **Markevich 2011.** The Sn-V complex in electron-irradiated Ge anneals out
  between 50 and 100 C, and its acceptor level gives 0.19 eV hole emission.
- **Decoster 2010 (measured).** Implanted Sn on split-vacancy sites is stable up
  to at least 400 C, at 5 to 15 % of the Sn.
- **Assali 2019 (quoted).** A Sn-divacancy complex in irradiated Ge anneals out
  at 220 K, and divacancy migration in Ge needs more than 1 eV.

No source reports an activation energy for the onset of Sn segregation or
precipitation itself, as distinct from diffusion. The literature gives onset
temperatures instead. For epitaxial GeSn the reported onsets lie between about
550 and 700 C for 5 to 8 % Sn: 550 C in Jia 2020 (5 min RTA), 600 C in Comrie
2016 (20 min), above 580 C in Li 2013, and 700 C in Zhang 2017 (1 min RTA). For amorphous
GeSn, Higashiyama 2019 reports crystallization onset falling from 375 to 110 C
as Sn rises from 9 to 41 at.%.

## Gaps

1. **One open time series, at one temperature.** The only open isothermal kinetic
   data come from one preprint, one SiGeSn composition, one temperature (550 C)
   and an optical proxy (the E2 shift) rather than a direct substitutional Sn
   fraction. With one temperature, an Arrhenius energy for segregation cannot be
   fitted from time series.
2. **Paywalled kinetic data.** The isothermal data in Stanchu 2023 (300 C, hours)
   and Cai 2022 are paywalled. The in-situ XRD ramps in Zaumseil 2018 and the
   in-situ LEEM in Fournier-Lupien 2014 are behind publisher bot protection or
   a paywall. Asking these authors for data, or a library download, would add up
   to four in-situ or time-resolved sources.
3. **No measured Sn-vacancy binding energy in Ge.** The only number is the
   0.56 eV difference implied by Decoster's DFT heats of formation. The DFT
   values in Tahini 2011 and Chroneos 2011 are paywalled.
4. **Implant-plus-anneal coverage is thin.** Decoster 2010 covers implanted Sn at
   1e12 cm-2 doses. There is no open series for Sn-rich GeSn after dopant
   implantation and anneal.
5. **Thin SiGeSn coverage.** Data cover two compositions, Si0.10Ge0.81Sn0.09 and
   Si0.08Ge0.88Sn0.04. None is near the Si0.1Ge0.78Sn0.12 planned for stage T1.
6. **Untraced reference.** "Thermal stability and Sn diffusion in GeSn
   heterostructures" (Rainko et al., 2017) appeared in Asta results without a
   DOI and was not traced.

## Does the "fewer than about ten in-situ series" risk of doc 26 section 3.5 apply?

**Partly.**

- **True time series.** Six open series have true time resolution, below the
  threshold of about ten. They come from a single preprint at a single
  temperature. For hypothesis T2 (predicting a held-out anneal schedule), this
  is not enough to fit or test rate laws on literature time series alone. The
  held-out test would need to use temperature series (45 isochronal series with
  stated hold times) or rely on simulated kinetics from stage T2, as section
  3.5 anticipates.
- **Counting the in-situ temperature ramps.** Adding the nine in-situ TEM
  temperature series gives 15 in-situ series. The threshold is met only in that
  looser sense.
- **Hypothesis T1.** Matching MD and NEB barriers to literature activation
  energies is well supported. The literature gives a consistent band for Sn
  diffusion in Ge (2.9 to 3.3 eV measured, 2.48 to 3.65 eV computed), an
  enhanced low-temperature regime in metastable GeSn and SiGeSn (1.1 to 1.8 eV),
  and DFT energetics for the SnV complex.

The P4 draft should state that its kinetic validation rests on temperature
series and diffusion energies from the literature, and on simulation for the
time axis.
