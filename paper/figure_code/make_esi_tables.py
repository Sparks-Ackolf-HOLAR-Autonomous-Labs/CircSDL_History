#!/usr/bin/env python3
"""Write esi_tables.tex (tables of the supplementary file) from committed data.
Standard library only. Run after analysis/build_record.py."""
import csv, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
MT = os.path.abspath(os.path.join(HERE, "..", ".."))
T1 = os.path.join(MT, "p4_tskg", "T1_md")
out = []


CLEAN = {"Kringho/j": "Kringh{\\o}j", "excluded from series.json": "excluded from the record",
         "a_perp vs T": "out-of-plane lattice parameter vs T", "cBOmega model": "cB$\\Omega$ model"}


def esc(s):
    s = str(s)
    for a, b in CLEAN.items():
        s = s.replace(a, "\x00" + str(list(CLEAN).index(a)) + "\x00")
    s = (s.replace("\\", "/").replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
            .replace("#", r"\#").replace("µ", r"$\mu$").replace("−", "-").replace("–", "-"))
    for i, b in enumerate(CLEAN.values()):
        s = s.replace("\x00" + str(i) + "\x00", b)
    return s


# ---- T1 runs
res = json.load(open(os.path.join(T1, "t1_result.json")))
out.append(r"""\begin{table}[ht]
\caption{MACE-MP-0 molecular-dynamics runs (510 atoms on 512 sites, 61 Sn, 2 vacancies placed, 0.5\,ns production after 5\,ps equilibration). Energies are the potential energy per atom averaged over the first five recorded snapshots and the last snapshot. Crystal order: ``kept'' if the potential energy never exceeds its starting average by more than 0.03\,eV/atom and the number of empty sites stays at two; ``equilibration'' if more than two empty sites are already present at the first recorded snapshot; otherwise the time at which the energy threshold is first crossed. Net Sn hops: hops left after cancelling those reversed within 10\,ps; rev.\ frac.: fraction of Sn hops cancelled; vac.\ hops: vacancy hops. GeSn: Ge$_{0.88}$Sn$_{0.12}$; SiGeSn: Si$_{0.10}$Ge$_{0.78}$Sn$_{0.12}$; s: seed.}
\label{tab:S_runs}
\centering
\small
\begin{tabular}{l r r r l r r r r}
\hline
Run & $E_\mathrm{start}$ & $E_\mathrm{end}$ & empty & crystal & Sn & net Sn & rev. & vac.\\
 & (eV/at.) & (eV/at.) & sites & order & hops & hops & frac. & hops\\
\hline""")
for run, r in res["runs"].items():
    o = r["order"]
    name = ("SiGeSn" if r["si"] else "GeSn") + f" {r['T']:.0f}\\,K, s{run[-1]}"
    if o["n_vac_start"] > 2:
        onset = "equilibration"
    elif o["order_lost_at_ps"] is None:
        onset = "kept"
    else:
        onset = f"{o['order_lost_at_ps']:.0f} ps"
    out.append(f"{name} & ${o['epot_start_eV_atom']:.4f}$ & ${o['epot_end_eV_atom']:.4f}$ & {o['n_vac_start']}/{o['n_vac_end']} & "
               f"{onset} & {r['sn_hops']} & {r['net_sn_hops']} & {r['cancelled_frac']:.2f} & {r['vac_hops']}\\\\")
out.append(r"""\hline
\end{tabular}
\end{table}
""")

# ---- O1 samples
d = json.load(open(os.path.join(T1, "out", "o1_x012_rep4.json")))
out.append(r"""\begin{table}[ht]
\caption{Sn-vacancy binding energy in Ge$_{0.88}$Sn$_{0.12}$ under MACE-MP-0 (512-site cell at the MACE lattice parameter 5.917\,\AA, positions relaxed to 0.01\,eV/\AA). Each sample is a different random alloy and a different chosen Sn atom. $E_b = E_\mathrm{far} - E_\mathrm{near}$; positive means bound. Largest displacement: the largest atomic displacement from the ideal site after relaxation, near-vacancy cell.}
\label{tab:S_o1}
\centering
\begin{tabular}{l r r r r}
\hline
Sample & $E_b$ & far vacancy & largest displacement & relaxation steps\\
 & (eV) & distance (\AA) & near cell (\AA) & near/far\\
\hline""")
for s in d["samples"]:
    out.append(f"{s['seed']} & {s['E_b_eV']:.3f} & {s['far_dist_A']:.1f} & {s['max_disp_near_A']:.2f} & {s['steps'][0]}/{s['steps'][1]}\\\\")
dl = d["dilute_Ge"]
out.append(r"\hline")
out.append(f"mean $\\pm$ s.d. & {d['E_b_mean_eV']:.3f} $\\pm$ {d['E_b_sd_eV']:.3f} & & & \\\\")
out.append(f"one Sn in Ge (5.776\\,\\AA) & {dl['E_b_eV']:.3f} & {dl['far_dist_A']:.1f} & {dl['max_disp_near_A']:.2f} & {dl['steps'][0]}/{dl['steps'][1]}\\\\")
out.append(r"""\hline
\end{tabular}
\end{table}
""")

files = {"runs": out[:]}
out.clear()
# ---- literature sources
rows = list(csv.DictReader(open(os.path.join(MT, "p4_tskg", "T3_insitu", "sources.csv"))))
out.append(r"""\begin{small}
\begin{longtable}{p{0.27\textwidth} p{0.05\textwidth} p{0.05\textwidth} p{0.48\textwidth}}
\caption{Sources examined for the literature record: first author and year as returned by Crossref (arXiv API for the two preprints), number of series contributed, and what each source was used for.}\label{tab:S_sources}\\
\hline
First author, year, DOI or arXiv id & open & series & use\\
\hline
\endfirsthead
\hline
First author, year, DOI or arXiv id & open & series & use\\
\hline
\endhead
\hline
\endfoot""")
for r in sorted(rows, key=lambda r: (r["first_author"].split()[-1], r["year"])):
    out.append(f"{esc(r['first_author'])}, {r['year']}, \\nolinkurl{{{r['doi']}}} & {esc(r['open_access'][:1])} & {r['n_series']} & {esc(r['used_for'])}\\\\")
out.append(r"""\end{longtable}
\end{small}
""")

files["sources"] = out[:]
out.clear()
# ---- campaign record entries of this study
led = {}
for line in open(os.path.join(MT, "phase_c", "ledger_campaign.jsonl")):
    e = json.loads(line)
    led[e["seq"]] = e
plain = {
    122: "theorist brief, grading rubric and hash of the outcome key fixed before any answer",
    123: "answers of theorists A and B hashed before the outcome key was opened",
    124: "grades of theorists A and B against the opened outcome key, by the registered rubric",
    125: "round-2 protocol and payloads of the literature-grounded theorist fixed",
    126: "MD and static designs, code and grading rules for O1 and O2 fixed before production output",
    127: "placement change: three MD tasks resubmitted to other GPU nodes with the same runs and seeds",
    128: "answers of the literature-grounded theorist (C) hashed",
    131: "O1 raw output hashed before the registered rule was applied",
    132: "O1 graded: 0.434 eV, bound by more than 0.3 eV",
    143: "raw MD outputs of all seven runs hashed before analysis",
    144: "O2 read as registered (0.13 eV) and with the disclosed crystal-order screen (0.44 eV, labelled a lower bound)",
    150: "correction: 0.44 eV is the one-hop barrier, not a lower bound, since 46 net hops were seen at 500 K; grades unchanged",
    145: "range limit: MACE-MP-0 MD of GeSn and SiGeSn at 500 K and below",
}
out.append(r"""\begin{table}[ht]
\caption{Entries of the hash-chained campaign record that belong to this study, in the order written (UTC). Entry numbers are the record's own sequence numbers.}
\label{tab:S_ledger}
\centering
\small
\begin{tabular}{r l l p{0.50\textwidth}}
\hline
Entry & time (UTC) & kind & content\\
\hline""")
for s, txt in plain.items():
    e = led[s]
    kind = {"commitment": "commitment", "batch_commitment": "hashed outputs", "deviation": "deviation",
            "analysis": "analysis", "shard_operation": "decision"}[e["kind"]]
    out.append(f"{s} & {e['time'][:16].replace('T', ' ')} & {kind} & {esc(txt)}\\\\")
out.append(r"""\hline
\end{tabular}
\end{table}
""")

files["ledger"] = out[:]
out.clear()
# ---- implant range cross-check
cc = json.load(open(os.path.join(MT, "second_system", "implant_srim", "code_crosscheck.json")))
lab = {"C_Si_30keV": "C in Si", "C_Si0.8Ge0.2_30keV": "C in Si$_{0.8}$Ge$_{0.2}$", "Sn_Ge_30keV": "Sn in Ge"}
out.append(r"""\begin{table}[ht]
\caption{Projected range $R_p$ and straggle $\Delta R_p$ of 30\,keV ions at normal incidence from SRIM-2013 (about 5000 ions) and RustBCA (about 20\,000 ions). Difference: RustBCA relative to SRIM.}
\label{tab:S_implant}
\centering
\begin{tabular}{l r r r r r r}
\hline
 & \multicolumn{2}{c}{SRIM-2013} & \multicolumn{2}{c}{RustBCA} & \multicolumn{2}{c}{difference (\%)}\\
Ion in target & $R_p$ (nm) & $\Delta R_p$ (nm) & $R_p$ (nm) & $\Delta R_p$ (nm) & $R_p$ & $\Delta R_p$\\
\hline""")
for k, v in cc.items():
    a, b = v["SRIM-2013"], v["RustBCA"]
    out.append(f"{lab[k]} & {a['Rp_nm']:.1f} & {a['dRp_nm']:.1f} & {b['Rp_nm']:.1f} & {b['dRp_nm']:.1f} & {v['Rp_diff_pct']:+.1f} & {v['dRp_diff_pct']:+.1f}\\\\")
out.append(r"""\hline
\end{tabular}
\end{table}
""")
files["implant"] = out[:]
out.clear()
# ---- film conductivity model rows
rows = json.load(open(os.path.join(MT, "second_system", "gesn_transfer_check.json")))
k = {(r["y_Sn"], r["boundary"], r["eps"]): r["kappa"] for r in rows}
for y in sorted({r["y_Sn"] for r in rows}):
    out.append(f"{y:.2f} & " + " & ".join(f"{k[(y, b, e)]:.2f}" for b in ("100nm", "700nm", "bulk") for e in (0.0, 39.0)) + r"\\")
out.append(r"\hline")
files["film"] = out[:]
for name, lines in files.items():
    open(os.path.join(HERE, f"esi_tables_{name}.tex"), "w").write("\n".join(lines) + "\n")
    print(f"wrote esi_tables_{name}.tex")
