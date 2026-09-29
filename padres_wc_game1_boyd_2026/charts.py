"""Padres Game 1 lineup vs LHP chart. Reads lineup_vs_lhp_2026.csv and saves to ../figures/."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.text as mtext

D = Path(__file__).resolve().parent
FIG = D.parent / "figures"
BROWN, GOLD, INK, MUTED, REF = "#5b3617", "#c9a227", "#1f1f1f", "#6b6b6b", "#8a8a8a"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})


def check_layout(fig, texts):
    fig.canvas.draw()
    rend, fb = fig.canvas.get_renderer(), fig.bbox
    boxes = [(t.get_text()[:25], mtext.Text.get_window_extent(t, rend)) for t in texts if t.get_text() and t.get_visible()]
    off = [n for n, b in boxes if b.x0 < 0 or b.x1 > fb.x1 or b.y0 < 0 or b.y1 > fb.y1]
    clash = [(a, b) for i, (a, ba) in enumerate(boxes) for b, bb in boxes[i + 1:] if ba.overlaps(bb)]
    print(f"   layout: off-figure {off or 'none'} | text overlaps {clash or 'none'}")


def lineup_vs_lhp():
    t = pd.read_csv(D / "lineup_vs_lhp_2026.csv")
    mlb = t[t.order.isna()].iloc[0]
    t = t[t.order.notna()].reset_index(drop=True)
    assert list(t.order) == list(range(1, 10))
    print(f"MLB xwOBA vs LHP {mlb.xwOBA:.3f} | " + ", ".join(f"{int(r.order)}. {r.hitter.split()[-1] if 'Jr.' not in r.hitter else 'Tatis'} {r.xwOBA:.3f} ({r.PA} PA)" for r in t.itertuples()))
    fig = plt.figure(figsize=(11, 8.2))
    ax = fig.add_axes([0.25, 0.14, 0.62, 0.66])
    y = np.arange(len(t))
    ax.barh(y, t.xwOBA, height=0.62, color=BROWN, zorder=2)
    ax.vlines(mlb.xwOBA, -0.5, len(t) - 0.5, color=REF, lw=1.6, ls="--", zorder=3)  # stops at the bars, clear of its label
    ax.text(mlb.xwOBA, -0.62, f"MLB avg vs LHP {mlb.xwOBA:.3f}".replace("0.", "."), ha="center", va="bottom", fontsize=10.5, color=MUTED)
    for i, r in t.iterrows():
        ax.text(r.xwOBA + 0.006, i, f"{r.xwOBA:.3f}".lstrip("0"), ha="left", va="center", fontsize=12, fontweight="bold", color=INK)
        ax.text(0.505, i, f"{r.PA} PA", ha="right", va="center", fontsize=10.5, color=MUTED)
    labels = [f"{int(r.order)}. {r.hitter} ({r.bats})" for r in t.itertuples()]
    ax.set_yticks(y, labels, fontsize=12.5, color=INK)
    ax.tick_params(axis="y", length=0, pad=8)
    ax.set_ylim(len(t) - 0.5, -1.1)
    ax.set_xlim(0, 0.51)  # bars start at zero so their length matches the value
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.3f}".lstrip("0") if v else "0"))
    ax.set_xticks([0, 0.1, 0.2, 0.3, 0.4])
    ax.tick_params(axis="x", colors=MUTED, labelsize=11)
    ax.set_xlabel("xwOBA vs LHP", fontsize=13, color=INK)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    tax = fig.add_axes([0, 0.935, 1, 0.001]); tax.axis("off")
    tax.set_title("Padres Game 1 Lineup vs LHP", fontsize=24, fontweight="bold", color=INK, pad=0)
    fig.text(0.5, 0.884, "Wild Card Game 1 vs Matthew Boyd | 2026 regular season", ha="center", fontsize=14, color=MUTED)
    small = t[t.PA < 60]
    note = ", ".join(f"{r.hitter.split()[-1]} ({r.PA})" for r in small.itertuples())
    fig.text(0.5, 0.036, f"Small samples: {note} PA vs LHP. Data: Baseball Savant.", ha="center", va="bottom", fontsize=10.5, color=MUTED, style="italic")
    fig.text(0.985, 0.006, "@310Analytics", ha="right", va="bottom", fontsize=11, color=MUTED)
    check_layout(fig, list(fig.texts) + list(ax.texts) + ax.get_yticklabels() + [ax.xaxis.label])
    fig.savefig(FIG / "padres_game1_lineup_vs_lhp_2026.png", dpi=200)
    plt.close(fig)
    print("   saved padres_game1_lineup_vs_lhp_2026.png")


if __name__ == "__main__":
    lineup_vs_lhp()
