# Processing history attached to each value separates conflicting evidence on metastable (Si)GeSn semiconductors

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23413461.svg)](https://doi.org/10.5281/zenodo.23413461)

Code, data and figure scripts for the paper "Processing history attached to each value separates conflicting evidence on metastable (Si)GeSn semiconductors" (Semiconductor Science and Technology (IOP)). The manuscript itself is not part of this folder.

Licences: code (Python, shell and SLURM scripts) under the MIT License (`LICENSE`); data, result files, figures and text under CC BY 4.0 (`LICENSE-CC-BY-4.0.txt`). Archived third-party datasets keep their own terms and are cited in the paper: the Starrydata slice is CC BY 4.0 (Katsura et al., Sci. Technol. Adv. Mater.: Methods 5, 2506976 (2025), doi:10.1080/27660400.2025.2506976; cite it and the source paper of each curve used), and the Citrine release keeps its published terms.

Every path below is relative to this folder, and every script runs from it. The folder depends on no other folder or repository.

Analysis, figure and checker scripts run on any machine with the Python packages in `requirements.txt`. Acquisition scripts (SLURM job files and run generators) name the cluster paths and simulation binaries (LAMMPS, GPUMD, almaBTE, MACE) used at the time, so re-running a simulation needs those paths edited to the local installation. The recorded outputs of those runs are included, so no simulation has to be repeated to check a result.

Files whose SHA-256 the campaign record stores (designs, pre-registration digests, the scripts and raw outputs they name, and some notes) are kept byte-for-byte as they ran, because any edit would break verification. They keep their original wording, which includes operator decisions with dates, internal step numbers and the run paths of the time. Raw simulation logs are also kept as written.

Terms used in folder names and notes: a *party* is one evidence source of the campaign (for example Tersoff MD, MACE-MP rNEMD, almaBTE first-principles transport or a curated database); a *gate* is the acceptance check a run must pass before its result enters the campaign record; `phase_c/` holds the main campaign and `pilot/` the campaign-record library and the first trial campaign.

## Campaign material

| path | what it holds |
|---|---|
| `p4_tskg` | data model, schema tests, record replay, literature series and sources, MACE-MP-0 MD and Sn-vacancy binding runs (inputs, run scripts, raw outputs, analysis) |
| `second_system/gesn_transfer_check.json` | film conductivity check |
| `second_system/implant_srim` | SRIM and RustBCA implant range cross-check |
| `phase_c/ledger_campaign.jsonl` | the campaign record (entries 122 to 128, 131, 132, 143 to 145, 150) |
| `pilot/src` | campaign-record library |

## Figures

One script draws every figure at its print size into `paper/figure_code/figures/` (PDF used by the paper, PNG for review). Run from this folder with a Python that has numpy, scipy and matplotlib:

    python3 paper/figure_code/make_figures.py

Figures: `fig1_record`, `fig2_md`, `fig3_energies`, `fig4_history`, `fig5_film`, `figS1_pairs`.

## Checkers and analyses

| command |
|---|
| `python3 paper/figure_code/analysis/build_record.py ` |
| `python3 paper/figure_code/make_esi_tables.py ` |
| `python3 p4_tskg/test_t0.py ` |

`traced_inputs.json` lists every file each command opened when the folder was built; `FILES.sha256` lists the digest of every file in the folder.
