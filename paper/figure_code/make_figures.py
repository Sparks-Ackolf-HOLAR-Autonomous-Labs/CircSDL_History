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
fig5_film         second_system/gesn_transfer_check.json, analysis/concepcion2024_fig2g_read.json
figS1_pairs       p4_tskg/T1_md/out/gesn_x012_T500_s*.json, analysis/record_summary.json
"""
import json
from pathlib import Path
import numpy as np
from matplotlib.patches import FancyBboxPatch
from paper_fig_style import apply_style, save, plt, FULL, MT, HERE, C, TEMP, TMARK, SIGESN, SIGESN_MARK, GREY, INK

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
    ax.text(3.05, 2.47, "(b) the same stage on the campaign clock", fontsize=8.5, va="center")

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

    # (b) the materials event behind each campaign entry, in time order top to bottom;
    # the chain 126 -> 127 -> 143 -> 144 -> 145 runs down the column, and the two
    # further inputs (126 -> 143, 143 -> 145) run as arcs on the right, so no arrows cross.
    labels = {126: "plan fixed before any run: GeSn at\n500, 600 and 700 K, SiGeSn at 600 K",
              127: "three runs moved to other GPU nodes;\nanneal plan unchanged",
              143: "seven 0.5 ns anneals finished; outputs\nfingerprinted before analysis",
              144: "600 K and 700 K runs lose crystal\norder (up to 26 empty sites)",
              145: "MD of GeSn limited to\n500 K and below"}
    order = [126, 127, 143, 144, 145]
    xc, bw, bh = 4.80, 1.84, 0.34
    ys = {s_: 2.10 - i * 0.455 for i, s_ in enumerate(order)}
    months = {"10": "Oct"}
    for s_ in order:
        y = ys[s_]
        bx(xc, y, bw, bh, labels[s_], fc="#FDEBD9" if s_ == 145 else "#E8F1F8", fs=6.3)
        t = led[s_]["time"]  # e.g. 2026-10-09T17:59:10Z
        ax.text(3.80, y, f"{int(t[8:10])} {months[t[5:7]]} {t[0:4]}\n{t[11:16]} UTC", ha="right", va="center",
                fontsize=6.0, color=GREY, linespacing=1.15)
    for s0, s1 in zip(order[:-1], order[1:]):
        ax.annotate("", xy=(xc, ys[s1] + bh / 2), xytext=(xc, ys[s0] - bh / 2),
                    arrowprops=dict(arrowstyle="-|>", lw=0.7, color=INK, shrinkA=0, shrinkB=0))
    xr = xc + bw / 2
    for s0, s1, dy0, dy1 in ((126, 143, 0.0, 0.07), (143, 145, -0.07, 0.0)):
        ax.annotate("", xy=(xr, ys[s1] + dy1), xytext=(xr, ys[s0] + dy0),
                    arrowprops=dict(arrowstyle="-|>", lw=0.7, color=INK, shrinkA=0, shrinkB=0,
                                    connectionstyle="arc3,rad=-0.35"))
    save(fig, "fig1_record")


# ------------------------------------------------------------------ Figure 2
def fig2():
    """One hue and one marker per temperature, SiGeSn its own hue and marker; seed 1
    solid, seed 2 dotted. In (b) runs that sit on the same whole number of empty sites
    are drawn with a small vertical offset (stated in the caption) so each stays visible.
    Loss-of-order times quoted in the text (24 ps, 600 K seed 1; 484 ps, SiGeSn) are
    read from t1_result.json and marked in (a)."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL, 2.75))
    runs = RES["runs"]
    KB = 8.617333e-5
    e500 = np.mean([p["epot_eV_atom"] for p in json.load(open(T1 / "out" / "gesn_x012_T500_s1.json"))["series"][:5]])
    offset = {"gesn_x012_T500_s1": -0.35, "gesn_x012_T500_s2": 0.0, "gesn_x012_T600_s1": 0.35,
              "gesn_x012_T600_s2": -0.35, "sigesn_si010_x012_T600_s1": 0.35}
    order = ["gesn_x012_T500_s1", "gesn_x012_T500_s2", "gesn_x012_T600_s1", "gesn_x012_T600_s2",
             "gesn_x012_T700_s1", "gesn_x012_T700_s2", "sigesn_si010_x012_T600_s1"]
    handles = []
    for k, run in enumerate(order):
        d = json.load(open(T1 / "out" / f"{run}.json"))
        s = d["series"]
        t = np.array([p["t_ps"] for p in s])
        e = np.array([p["epot_eV_atom"] for p in s])
        nv = np.array([p["n_vac"] for p in s], dtype=float)
        T = runs[run]["T"]
        si = runs[run]["si"] > 0
        col, mk = (SIGESN, SIGESN_MARK) if si else (TEMP[T], TMARK[T])
        ls = "--" if si else ("-" if run.endswith("s1") else ":")
        lab = (f"SiGeSn {T:.0f} K" if si else f"GeSn {T:.0f} K, seed {run[-1]}")
        exc = (e - e[:5].mean()) * 1000 if si else (e - e500 - 1.5 * KB * (T - 500.0)) * 1000
        kw = dict(ls=ls, color=col, lw=0.9, marker=mk, ms=3.2, mfc="white" if ls == ":" else col, mew=0.7,
                  markevery=(3 * k, 25))
        h, = a.plot(t, exc, label=lab, **kw)
        b.plot(t, nv + offset.get(run, 0.0), **kw)
        handles.append(h)
        lost = runs[run]["order"]["order_lost_at_ps"]
        if run in ("gesn_x012_T600_s1", "sigesn_si010_x012_T600_s1") and lost is not None:
            i = int(np.argmin(np.abs(t - lost)))
            a.annotate(f"order lost\nat {lost:.0f} ps", xy=(t[i], exc[i]),
                       xytext=(t[i] + 55, exc[i] - 20) if lost < 100 else (t[i] - 85, 52),
                       fontsize=6.3, color=col, ha="left" if lost < 100 else "right", va="center",
                       arrowprops=dict(arrowstyle="-|>", lw=0.6, color=col, shrinkA=1, shrinkB=2))
    for y, txt in ((1.8, "2"), (3.4, "3"), (7.4, "8"), (9.6, "9"), (26, "26")):
        b.text(508, y, txt, fontsize=6.3, va="center", ha="left", color=INK)
    a.set_xlabel("MD time (ps)")
    a.set_ylabel("excess potential energy (meV/atom)")
    a.set_ylim(-15, 125)
    a.set_title("(a) potential energy above the crystal value")
    b.set_xlabel("MD time (ps)")
    b.set_ylabel("empty lattice sites")
    b.set_ylim(0, 28)
    b.set_xlim(-10, 530)
    b.set_title("(b) empty lattice sites (2 vacancies placed)")
    fig.legend(handles=handles, loc="outside lower center", ncol=4, fontsize=6.5, handlelength=2.6,
               columnspacing=1.2)
    save(fig, "fig2_md")


# ------------------------------------------------------------------ Figure 3
def fig3():
    o1 = json.load(open(T1 / "o1_result.json"))
    ea = REC["activation_energy_conflict"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL, 3.05), gridspec_kw={"width_ratios": [0.8, 1.2]})
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
    b.plot([ea["md_registered_slope_eV"]], [5], "x", color=C["out"], ms=6, mew=1.5)
    b.set_yticks(range(6))
    b.set_yticklabels([r[0] for r in rows] + ["DFT, Sn$-$vacancy pairs in Ge",
                                             "MACE-MP-0 MD, 500 K: crystal kept,\nback-and-forth hops",
                                             "MACE-MP-0 MD, 500$-$700 K:\ncrystal order lost"], fontsize=6.6)
    b.invert_yaxis()
    b.set_xlim(0, 4.0)
    b.set_xlabel("activation energy (eV)")
    b.set_title("(b) one quantity, six records")
    b.plot([], [], "o", color=C["lit"], ms=4, label="measured, Ge or GeSn")
    b.plot([], [], "^", color=C["lit"], ms=4, label="measured, SiGeSn (4 at.% Si)")
    b.plot([], [], "o", color=C["lit"], mfc="white", ms=4, label="measured, Ge/GeSn quantum wells")
    b.plot([], [], color=C["dft"], lw=3, label="published DFT range")
    b.plot([], [], "x", color=C["out"], ms=5, mew=1.3, label="MACE-MP-0, not a diffusion barrier")
    h, l = b.get_legend_handles_labels()
    fig.legend(h, l, loc="outside lower right", fontsize=6.3, ncol=3, handletextpad=0.3, columnspacing=1.0)
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
            txt = hold_txt.get(r["hold_s"], "ramp")
            a.text(x + 0.8, r["onset_C"], txt, fontsize=6.3, va="center", color=INK)
    a.plot([], [], "s", color=C["lit"], ms=4, label="epitaxial GeSn (hold time)")
    a.plot([], [], "^", color=C["lit"], ms=4, label="epitaxial SiGeSn, in-situ ramp")
    a.plot([], [], "o", color=C["lit"], mfc="white", ms=4, label="amorphous GeSn, crystallized")
    a.legend(loc="upper right", fontsize=6.3, handletextpad=0.3, borderaxespad=0.1)
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
    """Seed 1 solid, seed 2 dotted (MACE-MP-0 pink, as in every figure); thin lines of
    the same style mark each seed's time average (record_summary.json), with its value
    at the right edge; the random-arrangement expectation is a grey dashed line named
    in the legend, not on the data."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL, 2.45))
    dark = "#8E4A74"  # darker shade of the MACE-MP-0 pink for seed 2
    for run, ls, col in (("gesn_x012_T500_s1", "-", C["mace"]), ("gesn_x012_T500_s2", ":", dark)):
        d = json.load(open(T1 / "out" / f"{run}.json"))
        t = [p["t_ps"] for p in d["series"]]
        for ax_, key, mkey in ((a, "n_snsn_pairs", "snsn_pairs_time_mean"),
                               (b, "n_snv_pairs", "sn_next_to_vacancy_time_mean")):
            ax_.plot(t, [p[key] for p in d["series"]], ls=ls, color=col, lw=0.9, label=f"seed {run[-1]}")
            m = md[mkey][run]
            ax_.plot([0, 500], [m, m], ls="-", color=col, lw=1.6, alpha=0.55)
            dy = 0.7 if (ax_ is a and run.endswith("s2")) else 0.0  # 14.5 sits next to the random 14.3
            ax_.text(507, m + dy, f"{m:.1f}", fontsize=6.3, color=col, va="center", ha="left")
    for ax_, key in ((a, "snsn_pairs_random_expectation"), (b, "sn_next_to_vacancy_random_expectation")):
        r = md[key]
        ax_.plot([0, 500], [r, r], color=GREY, ls="--", lw=0.8, label="random arrangement")
        ax_.text(507, r - (0.7 if ax_ is a else 0.0), f"{r:.2f}" if r < 2 else f"{r:.1f}", fontsize=6.3,
                 color=GREY, va="center", ha="left")
        ax_.plot([], [], color=INK, lw=1.6, alpha=0.55, label="time average")
        ax_.set_xlim(-10, 540)
    a.set_xlabel("MD time at 500 K (ps)"); a.set_ylabel("first-neighbour Sn$-$Sn pairs")
    b.set_xlabel("MD time at 500 K (ps)"); b.set_ylabel("Sn atoms next to a vacancy")
    a.set_title("(a) Sn$-$Sn pairs"); b.set_title("(b) Sn$-$vacancy neighbours")
    a.set_ylim(0, 20); b.set_ylim(0, 8.6)
    h, l = a.get_legend_handles_labels()
    fig.legend(h, l, loc="outside lower center", ncol=4, fontsize=6.5)
    save(fig, "figS1_pairs")


# ------------------------------------------------------------------ Figure 5 (main text)
def fig5():
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
    save(fig, "fig5_film")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5(); figS1()
