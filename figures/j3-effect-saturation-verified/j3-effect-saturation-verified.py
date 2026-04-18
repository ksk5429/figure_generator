"""j3-effect-saturation-verified — Path B of the J3 saturation migration.

Re-derives what Path A asserts directly from analysis1/results/natural_frequencies.csv.
Surfaces three things:

1. The frequency-vs-SD curves the CSV currently supports (dry series only —
   SD is missing for T4/T5 in the source CSV).
2. Slope (scour sensitivity) per series, with saturated-series slopes
   flagged "unknown (no SD in CSV)".
3. A claim-witness panel that compares the CSV-derived dense/loose ratios
   (when computable) against the corrected 1.7-1.9x headline.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from figgen import io, utils

HERE = Path(__file__).resolve().parent
FIGURE_ID = HERE.name

C_T1 = "#4477AA"
C_T2 = "#EE6677"
C_T4 = "#4477AA"
C_T5 = "#EE6677"
FIG_WIDTH = 7.48


def _slope(sd: np.ndarray, f1: np.ndarray) -> float | None:
    """Absolute slope of normalised frequency decline vs SD, or None if SD is unusable."""
    sd = np.asarray(sd, dtype=float)
    f1 = np.asarray(f1, dtype=float)
    if np.isnan(sd).any() or len(sd) < 2:
        return None
    if np.ptp(sd) == 0:
        return None
    nf = (f1 - f1[0]) / f1[0] * 100.0
    return float(abs(np.polyfit(sd, nf, 1)[0]))


def main() -> None:
    cfg = io.load_config(HERE / "config.yaml")
    asset = io.load_tier2(cfg["paper"], cfg["tier2_slug"])
    df = asset.df.sort_values(["series", "f1_model_hz"]).reset_index(drop=True)

    series_order = ["T1", "T2", "T4", "T5"]
    rows = {k: df[df["series"] == k].sort_values("SD", na_position="last") for k in series_order}

    slopes: dict[str, float | None] = {}
    for k, sub in rows.items():
        slopes[k] = _slope(sub["SD"].to_numpy(), sub["f1_model_hz"].to_numpy())

    ratio_dense = None
    if slopes["T1"] and slopes["T4"]:
        ratio_dense = slopes["T1"] / slopes["T4"]
    ratio_loose = None
    if slopes["T2"] and slopes["T5"]:
        ratio_loose = slopes["T2"] / slopes["T5"]

    # Claim witness — corrected headline is 1.7-1.9x (loose pair)
    claim_lo, claim_hi = 1.7, 1.9
    witness = {
        "loose_T2_T5": None if ratio_loose is None
                       else ("pass" if claim_lo <= ratio_loose <= claim_hi else "fail"),
        "dense_T1_T4": None if ratio_dense is None else "measured",
    }

    utils.load_style(cfg["journal"])
    plt.rcParams.update({
        "font.size": 11, "axes.labelsize": 12,
        "xtick.labelsize": 10, "ytick.labelsize": 10,
        "legend.fontsize": 9, "lines.linewidth": 1.3,
    })

    fig, (ax_a, ax_b, ax_c) = plt.subplots(
        1, 3, figsize=(FIG_WIDTH, 3.4),
        gridspec_kw={"wspace": 0.45, "left": 0.065, "right": 0.985,
                     "bottom": 0.18, "top": 0.90,
                     "width_ratios": [1.0, 0.85, 1.15]},
    )

    # --- Panel (a): frequency decline vs SD, dry series only (CSV has SD) ---
    for key, color, marker, ls in [
        ("T1", C_T1, "o", "--"),
        ("T2", C_T2, "s", "--"),
    ]:
        sub = rows[key].dropna(subset=["SD"])
        if sub.empty:
            continue
        f1 = sub["f1_model_hz"].to_numpy()
        sd = sub["SD"].to_numpy()
        nf = np.abs((f1 - f1[0]) / f1[0] * 100.0)
        ax_a.plot(sd, nf, marker=marker, color=color, mec=color, mfc="white",
                  mew=1.2, ls=ls, lw=1.3, ms=7, label=f"{key} (dry)")

    ax_a.set_xlabel(r"Scour depth ratio, $S/D$")
    ax_a.set_ylabel(r"Frequency decline, $|\Delta f_1/f_{1,0}|$ (%)")
    ax_a.set_title("(a) CSV-derived decline (dry)",
                   fontsize=11, fontweight="bold", loc="left")
    ax_a.xaxis.set_major_locator(mticker.MultipleLocator(0.2))
    ax_a.yaxis.set_major_locator(mticker.MultipleLocator(0.5))
    ax_a.legend(loc="upper left", framealpha=0.95)

    # --- Panel (b): slope bars (NaN-aware) ---
    labels = ["T1", "T4", "T2", "T5"]
    colors = [C_T1, C_T4, C_T2, C_T5]
    hatches = ["//", "", "//", ""]
    x = np.arange(len(labels))
    vals = [slopes[k] if slopes[k] is not None else 0.0 for k in labels]
    bars = ax_b.bar(x, vals, 0.7, color=colors, hatch=hatches,
                    edgecolor="k", linewidth=0.6, alpha=0.88)

    for i, k in enumerate(labels):
        v = slopes[k]
        if v is None:
            ax_b.text(x[i], 0.2, "SD n/a", ha="center", va="bottom",
                      fontsize=9, color="0.35", fontstyle="italic")
        else:
            ax_b.text(x[i], v + 0.15, f"{v:.2f}", ha="center", va="bottom",
                      fontsize=9.5, fontweight="bold",
                      bbox=dict(facecolor="white", edgecolor="none",
                                alpha=0.8, pad=0.5))
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(labels)
    ax_b.set_ylabel(r"$|\Delta f/f_0|$ per $S\!/\!D$  (%)")
    ax_b.set_title("(b) CSV-derived slopes",
                   fontsize=11, fontweight="bold", loc="left")
    ymax = max([v for v in vals if v] + [0.5]) * 1.6
    ax_b.set_ylim(0, ymax)

    # --- Panel (c): claim witness ---
    ax_c.axis("off")
    ax_c.set_title("(c) Claim witness: j3-saturation-gain",
                   fontsize=11, fontweight="bold", loc="left")

    dense_rhs = "n/a (no SD in CSV)" if ratio_dense is None else f"{ratio_dense:.2f}x"
    loose_rhs = "n/a (no SD in CSV)" if ratio_loose is None else f"{ratio_loose:.2f}x"

    # Stack each (label, value) as two lines to avoid column-collision.
    def _pair(y, label, value, value_colour="0.15"):
        ax_c.text(0.04, y, label, transform=ax_c.transAxes,
                  fontsize=9, color="0.25", va="center")
        ax_c.text(0.04, y - 0.055, value, transform=ax_c.transAxes,
                  fontsize=11, fontweight="bold", va="center",
                  color=value_colour, family="DejaVu Sans Mono")

    _pair(0.93, "Headline (F-02 corrected)", "1.7 – 1.9 x", "#0b6ea0")
    _pair(0.77, "Dense pair  T1 / T4", dense_rhs, "0.25")
    _pair(0.61, "Loose pair  T2 / T5", loose_rhs, "0.25")

    # Separator
    ax_c.plot([0.04, 0.96], [0.47, 0.47], transform=ax_c.transAxes,
              color="0.7", lw=0.5, clip_on=False)

    verdict_colour = {"pass": "#2a8a3f", "fail": "#c23b22",
                      None: "#b26a00"}[witness["loose_T2_T5"]]
    verdict_text = {
        "pass": "PASS — loose ratio inside band",
        "fail": "FAIL — loose ratio outside band",
        None: "INCONCLUSIVE — loose ratio n/a",
    }[witness["loose_T2_T5"]]
    ax_c.text(0.04, 0.39, verdict_text, transform=ax_c.transAxes,
              fontsize=10, color=verdict_colour, fontweight="bold", va="center")

    ax_c.text(0.04, 0.25,
              "Source CSV lacks S/D for saturated\n"
              "tests (T4, T5). Recomputing the loose-\n"
              "pair ratio requires an auxiliary test-\n"
              "plan table before 1.7 – 1.9x can be\n"
              "re-derived from the CSV alone.",
              transform=ax_c.transAxes, fontsize=7.5, color="0.3",
              fontstyle="italic", va="top", linespacing=1.25)

    data_sources = asset.as_sources()
    written = utils.save_figure(
        fig, FIGURE_ID,
        formats=tuple(cfg.get("formats", ("png", "svg", "pdf"))),
        journal=cfg["journal"],
        data_sources=data_sources,
        paper=cfg["paper"],
        claim_id=cfg["claim_id"],
        tier=cfg["tier"],
        extra_metadata={
            "description": cfg.get("description", ""),
            "migration_path": "B_csv_verified",
            "csv_ratio_dense": "na" if ratio_dense is None else f"{ratio_dense:.3f}",
            "csv_ratio_loose": "na" if ratio_loose is None else f"{ratio_loose:.3f}",
            "witness_loose_T2_T5": witness["loose_T2_T5"] or "na",
        },
    )
    for p in written:
        print(f"wrote {p}")
    print("\n--- claim witness ---")
    print(f"headline: {claim_lo}-{claim_hi}x")
    # Strip non-ASCII for console output (Windows cp949 codec can't handle en-dash/times).
    print(f"dense T1/T4: {dense_rhs.encode('ascii', 'replace').decode('ascii')}")
    print(f"loose T2/T5: {loose_rhs.encode('ascii', 'replace').decode('ascii')}")
    print(f"witness[loose]: {witness['loose_T2_T5']}")


if __name__ == "__main__":
    main()
