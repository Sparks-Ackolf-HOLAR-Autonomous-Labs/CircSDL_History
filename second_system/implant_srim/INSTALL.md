# SRIM-2013 and RustBCA: installation and cross-check (2026-10-09)

Both codes were installed on 2026-10-09 so SRIM can be checked against an
independent code.

## Where each code lives

| Code | Machine | Location | Version / source |
|---|---|---|---|
| SRIM-2013 (SRIM, TRIM, SR) | sparksone (Windows 11, x64) | `C:\SRIM-2013` | `SRIM-2013-Pro.e` from srim.org, sha256 `07f7f46d...05cb40` |
| RustBCA | DGX (aarch64) | `~/tools/RustBCA/target/release/RustBCA` | git `a356280` (v3.0.0-17), Rust 1.99 via rustup in `~/.cargo` |

SRIM licence: free for non-commercial use (Ziegler, Ziegler and Biersack,
Nucl. Instrum. Methods B 268, 1818 (2010), doi 10.1016/j.nimb.2010.02.091).
RustBCA: open source (Drobny and Curreli, J. Open Source Softw. 6, 3298 (2021),
doi 10.21105/joss.03298).

## System changes made on sparksone

- Extracted the archive to `C:\SRIM-2013` (no SFX executable was run; the
  self-extractor was unpacked on the DGX with `unzip`).
- Ran the bundled Visual Basic 5 runtime installer (`MSVBvm50.exe /Q`).
- Copied and registered (32-bit `regsvr32 /s`) COMCTL32, COMDLG32, MSFLXGRD,
  TABCTL32, RICHTX32 `.OCX` into `C:\Windows\SysWOW64`.
- Installed the `Linedraw.ttf` font (copy to `C:\Windows\Fonts` + registry entry).

These are exactly the steps of SRIM's own `_SRIM-Setup (Right-Click).bat`,
done without the interactive prompts.

## Running TRIM over SSH (batch mode)

TRIM runs headless over SSH when `C:\SRIM-2013\TRIMAUTO` holds `1`:
copy a generated `TRIM.IN` into `C:\SRIM-2013`, start `TRIM.exe` with that
working directory, wait for exit (about 20 to 40 s for 5000 ions in quick
damage mode), then collect `SRIM Outputs\RANGE_3D.txt` and the other text
outputs. `srim/make_trim_in.py` writes the inputs (CRLF line endings,
quick Kinchin-Pease damage, plot type 5 = no plots).

## Cross-check on identical targets (`code_crosscheck.json`)

Same ion, energy, atomic density and surface binding energy in both codes;
normal incidence; SRIM 5000 ions, RustBCA 20 000 ions.

| Recipe (30 keV) | SRIM Rp / dRp (nm) | RustBCA Rp / dRp (nm) | Rp difference |
|---|---|---|---|
| C into Si | 97.3 / 36.7 | 105.6 / 41.9 | +8.5% |
| C into Si0.8Ge0.2 | 89.5 / 36.5 | 95.7 / 41.1 | +6.9% |
| Sn into Ge | 14.7 / 6.7 | 14.2 / 6.5 | -3.4% |

Reading: for the heavy ion (Sn in Ge, nuclear stopping dominated) the codes
agree within 3.5%. For the light ion (C in Si and SiGe) RustBCA puts the ions
7 to 9% deeper with a 13 to 14% wider profile. Switching RustBCA's
electronic-stopping model (Lindhard-Scharff, equipartition) or its
interatomic potential (Kr-C, ZBL) moves the C-in-Si range between 105.6 and
110.7 nm, so the gap is not a set-up error but the known spread between
SRIM's fitted stopping tables and RustBCA's analytic models. For implant
recipes this spread enters as a named uncertainty on depth (about 10% for C,
about 4% for Sn), carried with every profile.

## Files

- `rustbca/smoke.py` (inputs + range statistics), `rustbca/run/*.toml`,
  `rustbca/run/*_summary.output`, `rustbca/run/smoke_ranges.json`
- `srim/make_trim_in.py`, `srim/inputs/*.TRIM.IN`, `srim/raw/*` (SRIM outputs)
- `compare_codes.py` -> `code_crosscheck.json`
