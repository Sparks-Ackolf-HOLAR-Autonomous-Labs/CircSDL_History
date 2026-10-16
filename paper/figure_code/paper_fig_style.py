"""Figure style for P4 (Semiconductor Science and Technology, IOP single-column
layout, text width 153 mm). Every figure is created at its true print size so
a 7 pt tick label is 7 pt on the page; draft.tex includes the PDFs at natural
size (no width= scaling). Fonts: ticks 7 pt, axis labels 8 pt, panel titles
8.5 pt, legends 7 pt. Colours: Okabe-Ito, one colour per evidence source, the
same in every figure."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

FULL = 6.0          # inches; text width is 6.02 in
HERE = Path(__file__).resolve().parent
FIGDIR = HERE / "figures"
MT = HERE.parents[1]  # project root

INK, GREY, LIGHT = "#333333", "#8C8C8C", "#EBEBEB"
C = {
    "lit": "#0072B2",      # measured values from the open literature
    "dft": "#009E73",      # published first-principles values
    "mace": "#CC79A7",     # MACE-MP-0 computations run in this project
    "bte": "#E69F00",      # phonon Boltzmann transport model run in this project
    "out": "#8C8C8C",      # outside the declared range
}
TEMP = {500.0: "#0072B2", 600.0: "#E69F00", 700.0: "#D55E00"}


def apply_style():
    plt.rcParams.update({
        "figure.dpi": 100, "savefig.dpi": 600,
        "font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"],
        "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": INK, "ytick.color": INK,
        "axes.grid": True, "grid.color": "#DDDDDD", "grid.linewidth": 0.5,
        "axes.axisbelow": True, "lines.linewidth": 1.2, "legend.frameon": False,
        "figure.constrained_layout.use": True, "pdf.fonttype": 42,
        "axes.titlelocation": "left",
    })


def save(fig, name):
    """figures/<name>.pdf (vector, used by the draft) and a 300 dpi PNG for review.
    No bbox_inches='tight': it would change the print size."""
    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGDIR / f"{name}.pdf", facecolor="white", metadata={"CreationDate": None})
    fig.savefig(FIGDIR / f"{name}.png", dpi=300, facecolor="white")
    w, h = fig.get_size_inches()
    plt.close(fig)
    print(f"wrote figures/{name}.pdf ({w:.2f} x {h:.2f} in)")
