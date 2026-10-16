#!/usr/bin/env python3
"""Regenerate every figure of the P4 manuscript and its supplement from
committed data. Run analysis/build_record.py first (it writes
analysis/record_summary.json). Python with matplotlib and numpy.

Figure            data read
fig1_record       p4_tskg/T1_md/out/gesn_x012_T500_s1.json (first Sn-V pairing event),
                  phase_c/ledger_campaign.jsonl (entries of the MD stage), analysis/record_summary.json
fig2_md           p4_tskg/T1_md/out/*.json (series), p4_tskg/T1_md/t1_result.json
fig3_energies     p4_tskg/T1_md/o1_result.json, p4_tskg/T1_md/out/o1_x012_rep4.json, analysis/record_summary.json
fig4_history      analysis/record_summary.json (segregation onsets), p4_tskg/T3_insitu/series.json (550 C series)
figS1_pairs       p4_tskg/T1_md/out/gesn_x012_T500_s*.json, analysis/record_summary.json
figS2_film        second_system/gesn_transfer_check.json
"""
import json
from pathlib import Path
import numpy as np
from matplotlib.patches import FancyBboxPatch
from paper_fig_style import apply_style, save, plt, FULL, MT, HERE, C, TEMP, GREY, INK

apply_style()
T1 = MT / "p4_tskg" / "T1_md"
REC = json.load(open(HERE / "analysis" / "record_summary.json"))
RES = json.load(open(T1 / "t1_result.json"))


def box(ax, x, y, text, fc, w=0.27, h=0.13, fs=7, ec=INK):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.01,rounding_size=0.02",
                                fc=fc, ec=ec, lw=0.6, zorder=3))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=4)


# ------------------------------------------------------------------ Figure 1
def fig1():
    """Drawn in inch coordinates on one axes so boxes keep their print size."""
    d = json.load(open(T1 / "out" / "gesn_x012_T500_s1.json"))
    ev = next(e for e in d["events"] if e["name"] == "Sn-V pairing")
    led = {}
    for line in open(MT / "phase_c" / "ledger_campaign.jsonl"):
        e = json.loads(line)
        led[e["seq"]] = e
    W, H = FULL, 2.6
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    ax.text(0.05, 2.47, "(a) one event on the material clock", fontsize=8.5, va="center")
    ax.text(3.1, 2.47, "(b) the same stage on the campaign clock", fontsize=8.5, va="center")

    def bx(x, y, w, h, text, fc="white", fs=6.5):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.0,rounding_size=0.05",
                                    fc=fc, ec=INK, lw=0.6, zorder=3))
        ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=4, linespacing=1.15)

    ax.add_patch(FancyBboxPatch((0.08, 0.12), 2.8, 1.98, boxstyle="round,pad=0.0,rounding_size=0.12",
                                fc="#F6EAF1", ec=C["mace"], lw=1.0, ls="--", zorder=1))
    ax.text(1.48, 1.95, "hyperedge: Sn$_{Ge}$ + V$_{Ge}$ $\\rightarrow$ (Sn$_{Ge}$V$_{Ge}$),  "
            f"window t = {ev['t_ps']:.1f} ps", ha="center", va="center", fontsize=6.8)
    bx(0.72, 1.48, 1.08, 0.48, "state before\nGe$_{0.88}$Sn$_{0.12}$ crystal,\n2 vacancies")
    bx(2.22, 1.48, 1.08, 0.48, "process step\nMD anneal at 500 K,\n0.5 ns")
    bx(0.72, 0.86, 1.08, 0.40, "species before\nSn$_{Ge}$, V$_{Ge}$")
    bx(2.22, 0.86, 1.08, 0.40, "species after\n(Sn$_{Ge}$V$_{Ge}$) pair")
    bx(1.48, 0.38, 2.4, 0.3, "evidence source: MACE-MP-0 MD run for this study")
    ax.annotate("", xy=(1.66, 0.86), xytext=(1.28, 0.86), arrowprops=dict(arrowstyle="-|>", lw=0.8, color=INK))
    ax.text(1.47, 1.02, "balanced", ha="center", fontsize=6.0, color=GREY)

    labels = {126: "rules\nregistered", 127: "placement\nchanged", 143: "raw outputs\nhashed",
              144: "registered\nreading", 145: "range limited\nto 500 K\nand below"}
    pos = {126: (3.55, 1.55), 127: (4.03, 0.72), 143: (4.51, 1.55), 144: (4.99, 0.72), 145: (5.47, 1.55)}
    bw, bh = 0.84, 0.5
    for s_, (x, y) in pos.items():
        bx(x, y, bw, bh, labels[s_], fc="#FDEBD9" if s_ == 145 else "#E8F1F8", fs=6.3)
        t = led[s_]["time"]
        ax.text(x, y + 0.36 if y > 1 else y - 0.36, t[8:10] + " Oct " + t[11:16], ha="center", va="center",
                fontsize=6.0, color=GREY)
    for s0, s1 in [(126, 127), (127, 143), (126, 143), (143, 144), (144, 145), (143, 145)]:
        (x0, y0), (x1, y1) = pos[s0], pos[s1]
        if y0 == y1:
            p0, p1 = (x0 + bw / 2, y0), (x1 - bw / 2, y1)
        elif y1 < y0:
            p0, p1 = (x0 + 0.15, y0 - bh / 2), (x1 - 0.15, y1 + bh / 2)
        else:
            p0, p1 = (x0 + 0.15, y0 + bh / 2), (x1 - 0.15, y1 - bh / 2)
        ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", lw=0.7, color=INK, shrinkA=0, shrinkB=0))
    ax.text(4.51, 0.14, "UTC time of each committed entry; an arrow means\nthe later entry rests on the earlier one",
            ha="center", va="center", fontsize=6.0, color=GREY)
    save(fig, "fig1_record")


# ------------------------------------------------------------------ Figure 2
def fig2():
    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL, 2.35))
    ref = None
    runs = RES["runs"]
    for run in sorted(runs):
        d = json.load(open(T1 / "out" / f"{run}.json"))
        s = d["series"]
        t = np.array([p["t_ps"] for p in s])
        e = np.array([p["epot_eV_atom"] for p in s])
        nv = np.array([p["n_vac"] for p in s])
        T = runs[run]["T"]
        si = runs[run]["si"] > 0
        ls = "--" if si else ("-" if run.endswith("s1") else ":")
        col = TEMP[T]
        lab = (f"SiGeSn {T:.0f} K" if si else f"GeSn {T:.0f} K, seed {run[-1]}")
        KB = 8.617333e-5
        if si:
            base = e[:5].mean()
            exc = (e - base) * 1000
        else:
            e500 = np.mean([p["epot_eV_atom"] for p in json.load(open(T1 / "out" / "gesn_x012_T500_s1.json"))["series"][:5]])
            exc = (e - e500 - 1.5 * KB * (T - 500.0)) * 1000
        a.plot(t, exc, ls=ls, color=col, lw=1.0, label=lab)
        b.plot(t, nv, ls=ls, color=col, lw=1.0, label=lab)
    a.set_xlabel("MD time (ps)")
    a.set_ylabel("excess potential energy (meV/atom)")
    a.set_title("(a) potential energy above the crystal value")
    b.set_xlabel("MD time (ps)")
    b.set_ylabel("empty lattice sites")
    b.set_ylim(0, 30)
    b.set_title("(b) empty lattice sites (2 vacancies placed)")
    b.legend(loc="upper center", bbox_to_anchor=(0.5, 0.86), fontsize=6.3, ncol=2, handlelength=2.2, columnspacing=1.0)
    save(fig, "fig2_md")


# ------------------------------------------------------------------ Figure 3
def fig3():
    o1 = json.load(open(T1 / "o1_result.json"))
    ea = REC["activation_energy_conflict"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL, 2.6), gridspec_kw={"width_ratios": [0.8, 1.2]})
    eb = np.array(o1["E_b_per_sample_eV"])
    rng = np.random.default_rng(0)
    a.scatter(np.zeros_like(eb) + rng.uniform(-0.08, 0.08, eb.size), eb, s=14, color=C["mace"], zorder=3,
              label="8 alloy configurations")
    m, sd = eb.mean(), eb.std(ddof=1)
    a.errorbar([0.3], [m], yerr=[sd], fmt="o", color=INK, ms=4, capsize=3, lw=1, zorder=4, label="mean $\\pm$ s.d.")
    a.scatter([1.0], [o1["dilute_Ge_E_b_eV"]], marker="s", s=18, color=C["mace"], zorder=3,
              label="one Sn in pure Ge")
    a.axhline(0.3, color=GREY, lw=0.7, ls="--")
    a.text(1.38, 0.29, "category edge:\nbound by > 0.3 eV", fontsize=6.3, color=GREY, va="top", ha="right")
    a.scatter([1.0], [0.56], marker="D", s=16, color=C["dft"], zorder=3, label="published DFT energies\n(difference taken here)")
    a.set_xticks([0.15, 1.0]); a.set_xticklabels(["Ge$_{0.88}$Sn$_{0.12}$", "dilute"])
    a.set_xlim(-0.35, 1.4); a.set_ylim(0.0, 0.64)
    a.set_ylabel("Sn$-$vacancy binding energy (eV)")
    a.set_title("(a) MACE-MP-0 statics, 0 K")
    a.legend(loc="lower left", fontsize=6.3, handletextpad=0.3, borderaxespad=0.2)

    rows = [("implanted bulk Ge", "implanted bulk crystal"),
            ("film, anneals above about 650$\\,^\\circ$C", "metastable film, anneals above about 650 C"),
            ("film, anneals below about 650$\\,^\\circ$C", "metastable film, anneals below about 650 C")]
    for i, (lab, key) in enumerate(rows):
        for r in ea["rows"]:
            if r["state"] == key and (r["si_fraction"] or 0) <= 0.1:
                mk = "^" if (r["si_fraction"] or 0) > 0 else "o"
                mfc = "white" if r["series"].startswith("wang2016") else C["lit"]  # Ge/GeSn MQW interdiffusion
                b.errorbar([r["Ea_eV"]], [i], xerr=[r["unc_eV"] or 0], fmt=mk, color=C["lit"], mfc=mfc, ms=4.5, capsize=2, lw=0.8)
    dft = [r["Ea_eV"] for r in ea["rows"] if r["kind"] == "computed"]
    b.plot([min(dft), max(dft)], [3, 3], color=C["dft"], lw=3, solid_capstyle="butt")
    b.plot([ea["md_500K_observed_hops_eV"]], [4], "x", color=C["out"], ms=6, mew=1.5)
    b.text(ea["md_500K_observed_hops_eV"] + 0.12, 4, "back-and-forth hops: not a diffusion barrier", va="center",
           fontsize=6.3, color=GREY)
    b.plot([ea["md_registered_slope_eV"]], [5], "x", color=C["out"], ms=6, mew=1.5)
    b.text(ea["md_registered_slope_eV"] + 0.12, 5, "order lost: not a hop barrier", va="center", fontsize=6.3, color=GREY)
    b.set_yticks(range(6))
    b.set_yticklabels([r[0] for r in rows] + ["DFT, Sn$-$vacancy pairs in Ge", "MACE-MP-0 MD, 500 K\n(crystal kept)",
                                             "MACE-MP-0 MD, 500$-$700 K"], fontsize=6.6)
    b.invert_yaxis()
    b.set_xlim(0, 4.0)
    b.set_xlabel("activation energy (eV)")
    b.set_title("(b) one quantity, six records")
    b.plot([], [], "o", color=C["lit"], ms=4, label="Ge or GeSn")
    b.plot([], [], "^", color=C["lit"], ms=4, label="SiGeSn, 4 at.% Si")
    b.plot([], [], "o", color=C["lit"], mfc="white", ms=4, label="Ge/GeSn quantum wells")
    b.legend(loc="upper left", fontsize=6.3, handletextpad=0.2, title="measured", title_fontsize=6.3)
    save(fig, "fig3_energies")


# ------------------------------------------------------------------ Figure 4
def fig4():
    on = REC["segregation_onsets"]
    S = {s["series_id"]: s for s in json.load(open(MT / "p4_tskg" / "T3_insitu" / "series.json"))}
    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL, 2.55))
    hold_txt = {60: "1 min", 300: "5 min", 1200: "20 min", 1800: "30 min"}
    for r in on:
        if r["sn_fraction"] is None:
            continue
        x = 100 * r["sn_fraction"]
        am = r["start"] == "amorphous film"
        mk = "o" if am else ("^" if r["si_fraction"] else "s")
        a.errorbar([x], [r["onset_C"]], yerr=[r["unc_C"] or 0], fmt=mk, ms=4.5, capsize=2, lw=0.8,
                   color=C["lit"], mfc="white" if am else C["lit"])
        if not am:
            txt = hold_txt.get(r["hold_s"], "ramp") + (" (SiGeSn)" if r["si_fraction"] else "")
            a.text(x + 0.8, r["onset_C"], txt, fontsize=6.3, va="center", color=INK)
    a.plot([], [], "s", color=C["lit"], ms=4, label="epitaxial film (hold time)")
    a.plot([], [], "o", color=C["lit"], mfc="white", ms=4, label="amorphous film, crystallized")
    a.legend(loc="upper right", fontsize=6.3)
    a.set_xlabel("Sn content (at.%)")
    a.set_ylabel("onset of Sn segregation ($^\\circ$C)")
    a.set_xlim(0, 45); a.set_ylim(50, 800)
    a.set_title("(a) reported onsets with their history")
    for sid, lab, ls in (("attiaoui2026_E2shift_1", "uncapped", "-"), ("attiaoui2026_E2shift_6", "3 nm SiO$_2$ cap", "--")):
        s = S[sid]
        p = np.array(s["points"], dtype=float)
        b.errorbar(p[:, 0] / 60, p[:, 1], yerr=p[:, 2], fmt="o", ls=ls, ms=3, lw=0.9, capsize=1.5, color=C["lit"],
                   mfc="white" if ls == "--" else C["lit"], label=lab)
    b.set_xlabel("time at 550 $^\\circ$C (min)")
    b.set_ylabel("E$_2$ critical-point shift (meV)")
    b.set_title("(b) Si$_{0.08}$Ge$_{0.88}$Sn$_{0.04}$, same anneal, in situ")
    b.legend(loc="center right", fontsize=6.3)
    save(fig, "fig4_history")


# ------------------------------------------------------------------ Figure S1
def figS1():
    md = REC["md_500K_events"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL, 2.2))
    for run, ls in (("gesn_x012_T500_s1", "-"), ("gesn_x012_T500_s2", ":")):
        d = json.load(open(T1 / "out" / f"{run}.json"))
        t = [p["t_ps"] for p in d["series"]]
        a.plot(t, [p["n_snsn_pairs"] for p in d["series"]], ls=ls, color=C["mace"], lw=1.0, label=f"seed {run[-1]}")
        b.plot(t, [p["n_snv_pairs"] for p in d["series"]], ls=ls, color=C["mace"], lw=1.0, label=f"seed {run[-1]}")
    a.axhline(md["snsn_pairs_random_expectation"], color=GREY, ls="--", lw=0.8)
    a.text(10, md["snsn_pairs_random_expectation"] + 0.4, "random arrangement", fontsize=6.3, color=GREY)
    b.axhline(md["sn_next_to_vacancy_random_expectation"], color=GREY, ls="--", lw=0.8)
    b.text(10, md["sn_next_to_vacancy_random_expectation"] + 0.2, "random arrangement", fontsize=6.3, color=GREY)
    a.set_xlabel("MD time at 500 K (ps)"); a.set_ylabel("first-neighbour Sn$-$Sn pairs")
    b.set_xlabel("MD time at 500 K (ps)"); b.set_ylabel("Sn atoms next to a vacancy")
    a.set_title("(a) Sn$-$Sn pairs"); b.set_title("(b) Sn$-$vacancy neighbours")
    a.set_ylim(0, 20); b.set_ylim(0, 8.6)
    a.legend(loc="lower right", fontsize=6.3)
    save(fig, "figS1_pairs")


# ------------------------------------------------------------------ Figure S2
def figS2():
    rows = json.load(open(MT / "second_system" / "gesn_transfer_check.json"))
    fig, a = plt.subplots(figsize=(3.6, 2.4))
    for bnd, x in (("100nm", 100), ("700nm", 700)):
        v = [r["kappa"] for r in rows if r["y_Sn"] == 0.12 and r["boundary"] == bnd]
        a.plot([x, x], [min(v), max(v)], color=C["bte"], lw=5, solid_capstyle="butt")
    a.plot([], [], color=C["bte"], lw=5, label="model, mass-only to\nmass-plus-strain Sn term")
    meas = json.load(open(Path(__file__).resolve().parent / "analysis" / "concepcion2024_fig2g_read.json"))
    pts = [p for p in meas["points"] if p["t_nm"] >= 100]  # relaxed films only
    a.errorbar([p["t_nm"] for p in pts], [p["kappa"] for p in pts], yerr=[p["err"] for p in pts],
               fmt="o", ms=3, color=C["lit"], capsize=1.5, lw=0.7, label="measured films, 3$\\omega$ (read from figure)")
    a.set_xlabel("film thickness (nm)"); a.set_ylabel("$\\kappa$ at 300 K (W m$^{-1}$ K$^{-1}$)")
    a.set_xlim(0, 800); a.set_ylim(0, 7.5)
    a.set_title("Ge$_{0.88}$Sn$_{0.12}$ films, 300 K")
    a.legend(loc="lower right", fontsize=6.3)
    save(fig, "figS2_film")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); figS1(); figS2()
