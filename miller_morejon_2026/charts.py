"""Mason Miller and Adrián Morejón charts. Each function prints the ranks it uses, checks the layout, and saves to ../figures/."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.text as mtext

D = Path(__file__).resolve().parent
FIG = D.parent / "figures"

# Padres colors: Miller brown, Morejón gold
BROWN, GOLD = "#5b3617", "#c9a227"
DOT, REF, INK, MUTED, LABEL = "#D6D6D6", "#8a8a8a", "#1f1f1f", "#6b6b6b", "#7a7a7a"
SHADE = {BROWN: "#F3ECE6", GOLD: "#FBF4DD"}
TEXT_ON_WHITE = {BROWN: BROWN, GOLD: INK}  # gold text is too light on white, so Morejón's text is ink
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})

MILLER, MOREJON = 695243, 670970  # MLBAM ids
AGE = {MILLER: 28, MOREJON: 27}  # MLB Stats API currentAge, Sept. 25, 2026
ord_ = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def pool():
    """All 855 reliever seasons since 2016 (FanGraphs tabs merged on Season + PlayerId) plus Savant xwOBA / whiff%."""
    df = None
    for t in ["standard", "advanced", "stuff_plus"]:
        d = pd.read_csv(D / f"mlb_rp_{t}_2016_2026.csv", encoding="utf-8-sig")
        df = d if df is None else df.merge(d[["Season", "PlayerId"] + [c for c in d.columns if c not in df.columns]],
                                           on=["Season", "PlayerId"], validate="one_to_one")
    sv = pd.read_csv(D / "mlb_rp_savant_history_2016_2026.csv")[["Season", "PlayerId", "xwOBA", "whiff%"]]
    df = df.merge(sv, on=["Season", "PlayerId"], validate="one_to_one")
    assert len(df) == 855
    return df


def rank(d, col, v, lower_better):
    s = d[col].dropna()
    return int(((s < v) if lower_better else (s > v)).sum() + 1)


def check_layout(fig, texts):
    fig.canvas.draw()
    rend, fb = fig.canvas.get_renderer(), fig.bbox
    # Text.get_window_extent (not Annotation's) = the text and its box only, without the connector line
    boxes = [(t.get_text()[:25].replace("\n", " "), t.get_bbox_patch().get_window_extent(rend) if t.get_bbox_patch() else mtext.Text.get_window_extent(t, rend))
             for t in texts if t.get_text() and t.get_visible()]
    off = [n for n, b in boxes if b.x0 < 0 or b.x1 > fb.x1 or b.y0 < 0 or b.y1 > fb.y1]
    clash = [(a, b) for i, (a, ba) in enumerate(boxes) for b, bb in boxes[i + 1:] if ba.overlaps(bb)]
    # phone check: shown full width on a 390-pt-wide phone screen, each text size in on-screen points
    k = 390 / (fig.get_size_inches()[0] * 72)
    sizes = sorted({round(t.get_fontsize() * k, 1) for t in texts if t.get_text() and t.get_visible()})
    print(f"   layout: off-figure {off or 'none'} | text overlaps {clash or 'none'} | text sizes on a phone: {sizes} pt")
    return not off and not clash


def visible_ticks(ax):
    (x0, x1), (y0, y1) = sorted(ax.get_xlim()), sorted(ax.get_ylim())
    xs = [t for t, v in zip(ax.get_xticklabels(), ax.get_xticks()) if x0 <= v <= x1]
    ys = [t for t, v in zip(ax.get_yticklabels(), ax.get_yticks()) if y0 <= v <= y1]
    return xs + ys


def finish(fig, title, subtitle, foot, name, extra_line=None):
    tax = fig.add_axes([0, 0.935, 1, 0.001]); tax.axis("off")
    tax.set_title(title, fontsize=26, fontweight="bold", color=INK, pad=0)
    fig.text(0.5, 0.884, subtitle, ha="center", fontsize=15, color=MUTED)
    if extra_line:
        fig.text(0.5, 0.842, extra_line, ha="center", fontsize=14.5, fontweight="bold", color=INK)
    fig.text(0.5, 0.036, foot, ha="center", va="bottom", fontsize=10.5, color=MUTED, style="italic", linespacing=1.45)
    fig.text(0.985, 0.006, "@310Analytics", ha="right", va="bottom", fontsize=11, color=MUTED)
    check_layout(fig, list(fig.texts) + [t for a in fig.axes for t in a.texts] + [t for a in fig.axes if a.axison for t in visible_ticks(a)]
                 + [a.xaxis.label for a in fig.axes if a.axison] + [a.yaxis.label for a in fig.axes if a.axison])
    fig.savefig(FIG / name, dpi=200)
    plt.close(fig)
    print("   saved", name)


def scatter(d, xc, yc, who, color, xlim, ylim, xfmt, yfmt, xlab, ylab, callout, callout_at, name_at, labels, y_flip=False, yticks=None):
    """Faint gray dot per season; the player's season as a big dot with his name beside it and a callout; dashed medians; shaded better corner."""
    fig = plt.figure(figsize=(11, 8.2))
    ax = fig.add_axes([0.12, 0.165, 0.82, 0.635])
    g = d[(d.MLBAMID == who) & (d.Season == 2026)].iloc[0]
    rest = d.drop(index=g.name)
    mx, my = d[xc].median(), d[yc].median()
    # better corner: more of x, and less of y when the y axis is flipped (lower is better) or more of y otherwise
    y0, y1 = (ylim[0], my) if y_flip else (my, ylim[1])
    ax.add_patch(plt.Rectangle((mx, y0), xlim[1] - mx, y1 - y0, facecolor=SHADE[color], edgecolor="none", zorder=0))
    ax.scatter(rest[xc], rest[yc], s=16, color=DOT, edgecolor="none", zorder=2)
    ax.axvline(mx, color=REF, lw=1.2, ls="--", zorder=1); ax.axhline(my, color=REF, lw=1.2, ls="--", zorder=1)
    ax.annotate(f"median {xfmt(mx)}", xy=(mx, 1), xycoords=ax.get_xaxis_transform(), xytext=(5, -5), textcoords="offset points",
                ha="left", va="top", fontsize=11, color=MUTED)
    ax.annotate(f"median {yfmt(my)}", xy=(1, my), xycoords=ax.get_yaxis_transform(), xytext=(-4, 4 if not y_flip else -4), textcoords="offset points",
                ha="right", va="bottom" if not y_flip else "top", fontsize=11, color=MUTED)
    # comparison seasons: a slightly darker small dot + small gray label
    for name, season, dx, dy, ha in labels:
        r = d[(d.Name == name) & (d.Season == season)].iloc[0]
        ax.scatter(r[xc], r[yc], s=34, color="#9a9a9a", edgecolor="white", linewidth=0.8, zorder=3)
        ax.annotate(f"{name.split()[-1]} {season}", xy=(r[xc], r[yc]), xytext=(dx, dy), textcoords="offset points",
                    ha=ha, va="center", fontsize=11, color=LABEL, zorder=3)
    # the player: big dot, thick white outline, bold name + year right beside it
    ax.scatter(g[xc], g[yc], s=320, color=color, edgecolor="white", linewidth=2.2, zorder=5)
    ax.annotate(f"{g.Name.replace('Adrian Morejon', 'Adrián Morejón')} 2026", xy=(g[xc], g[yc]), xytext=name_at[:2], textcoords="offset points",
                ha=name_at[2], va="center", fontsize=13, fontweight="normal", color=TEXT_ON_WHITE[color], zorder=6)
    ax.annotate(callout, xy=(g[xc], g[yc]), xytext=callout_at, textcoords="data",
                fontsize=11, fontweight="bold", color=TEXT_ON_WHITE[color], ha="center", va="center", linespacing=1.35, zorder=6,
                bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=color, linewidth=1.2),
                arrowprops=dict(arrowstyle="-", color=color, lw=1.4, shrinkB=9))
    ax.set_xlim(*xlim); ax.set_ylim(*(ylim[::-1] if y_flip else ylim))
    if yticks is not None:
        ax.set_yticks(yticks)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: xfmt(v))); ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: yfmt(v)))
    ax.set_xlabel(xlab, fontsize=13.5, color=INK, labelpad=8); ax.set_ylabel(ylab, fontsize=13.5, color=INK, labelpad=8)
    ax.tick_params(colors=MUTED, labelsize=13.5)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    return fig, ax


# ---------------------------------------------------------------- 1. Whiff Rate vs xwOBA Allowed
def whiff_xwoba():
    d = pool(); g = d[(d.MLBAMID == MILLER) & (d.Season == 2026)].iloc[0]
    rw, rx = rank(d, "whiff%", g["whiff%"], False), rank(d, "xwOBA", g.xwOBA, True)
    print(f"Miller 2026: whiff% {g['whiff%']} rank {rw}/855 | xwOBA {g.xwOBA:.3f} rank {rx}/855")
    assert (rw, rx) == (2, 2)
    fig, ax = scatter(d, "whiff%", "xwOBA", MILLER, BROWN, (12, 54), (0.17, 0.37), lambda v: f"{v:.0f}%", lambda v: f"{v:.3f}".lstrip("0"),
                      "Whiff%", "xwOBA",
                      f"Among 855 reliever\nseasons since 2016:\nWhiff% {ord_(rw)}\nxwOBA {ord_(rx)}", (47.5, 0.336), (-13, 0, "right"),
                      [("Edwin Díaz", 2022, 0, -14, "center"), ("Kenley Jansen", 2016, -9, 0, "right")], y_flip=True)
    finish(fig, "Whiff Rate vs xwOBA Allowed", f"Mason Miller, Padres, age {AGE[MILLER]} | All reliever seasons, 60+ IP, since 2016",
           "Relievers with 0 starts and 60+ IP. No 2020 seasons qualify. 2026 through Sept. 24. Data: Baseball Savant, FanGraphs.",
           "miller_whiff_xwoba_since2016.png")


# ---------------------------------------------------------------- 2. Strikeout Rate vs FIP
def k_fip():
    d = pool(); g = d[(d.MLBAMID == MILLER) & (d.Season == 2026)].iloc[0]
    rk, rf = rank(d, "K%", g["K%"], False), rank(d, "FIP", g.FIP, True)
    print(f"Miller 2026: K% {g['K%']:.1%} rank {rk}/855 | FIP {g.FIP:.2f} rank {rf}/855")
    assert (rk, rf) == (3, 2)
    fig, ax = scatter(d, "K%", "FIP", MILLER, BROWN, (0.10, 0.54), (0.5, 6.0), lambda v: f"{v:.0%}", lambda v: f"{v:.2f}",
                      "K%", "FIP",
                      f"Among 855 reliever\nseasons since 2016:\nK% {ord_(rk)}\nFIP {ord_(rf)}", (0.46, 4.85), (-13, 0, "right"),
                      [("Edwin Díaz", 2022, 9, 0, "left"), ("Craig Kimbrel", 2017, 2, -14, "left")], y_flip=True, yticks=[1, 2, 3, 4, 5])
    finish(fig, "Strikeout Rate vs FIP", f"Mason Miller, Padres, age {AGE[MILLER]} | All reliever seasons, 60+ IP, since 2016",
           "Relievers with 0 starts and 60+ IP. No 2020 seasons qualify. 2026 through Sept. 24. Data: FanGraphs.",
           "miller_k_fip_since2016.png")


# ---------------------------------------------------------------- 3. Pitching+ vs Innings Pitched
def pitching_ip():
    d = pool(); d = d[d["Pitching+"].notna()]
    g = d[(d.MLBAMID == MOREJON) & (d.Season == 2026)].iloc[0]
    rp = rank(d, "Pitching+", g["Pitching+"], False)
    only = d[(d.IP >= 80) & (d["Pitching+"] >= 130)]
    print(f"Morejón 2026: Pitching+ {g['Pitching+']:.1f} rank {rp}/{len(d)} | IP {g.IP} | 130+ Pitching+ with 80+ IP: {only[['Season', 'Name']].values.tolist()}")
    assert rp == 3 and len(d) == 510
    extra = "\nOnly 130+ Pitching+\nseason with 80+ IP" if len(only) == 1 and only.iloc[0].MLBAMID == MOREJON else ""
    fig, ax = scatter(d, "IP", "Pitching+", MOREJON, GOLD, (58, 90), (70, 142), lambda v: f"{v:.0f}", lambda v: f"{v:.0f}",
                      "IP", "Pitching+",
                      f"Among 510 reliever\nseasons since 2021:\nPitching+ {ord_(rp)}{extra}", (83.2, 80.5), (0, 17, "center"),
                      [("Emmanuel Clase", 2021, 9, 0, "left"), ("Emmanuel Clase", 2022, 9, 0, "left")])
    finish(fig, "Pitching+ vs Innings Pitched", f"Adrián Morejón, Padres, age {AGE[MOREJON]} | All reliever seasons, 60+ IP, since 2021",
           "Relievers with 0 starts and 60+ IP. No 2020 seasons qualify. 2026 through Sept. 24. Data: FanGraphs.",
           "morejon_pitching_ip_since2021.png")


# ---------------------------------------------------------------- 4. 2026 Savant Percentiles (chart library #72)
def savant_percentiles():
    pr = pd.read_csv(D / "savant_percentiles_2026.csv").set_index("player_id")
    raw = pd.read_csv(D / "savant_raw_2026.csv").set_index("player_id")
    metrics = [("xwOBA", "xwoba", "xwoba", lambda v: f"{v:.3f}".lstrip("0")), ("xERA", "xera", "xera", lambda v: f"{v:.2f}"),
               ("Strikeout %", "k_percent", "k_percent", lambda v: f"{v:.1f}%"), ("Whiff %", "whiff_percent", "whiff_percent", lambda v: f"{v:.1f}%"),
               ("Chase %", "chase_percent", "oz_swing_percent", lambda v: f"{v:.1f}%"), ("xSLG", "xslg", "xslg", lambda v: f"{v:.3f}".lstrip("0")),
               ("Hard-hit %", "hard_hit_percent", "hard_hit_percent", lambda v: f"{v:.1f}%"), ("FB velo", "fb_velocity", "fastball_avg_speed", lambda v: f"{v:.1f} mph")]
    tier = lambda p: BROWN if p >= 67 else ("#B0AFAF" if p >= 33 else GOLD)
    fig = plt.figure(figsize=(13, 9))
    for k, (pid, nm) in enumerate([(MILLER, "Mason Miller"), (MOREJON, "Adrián Morejón")]):
        vals = [float(pr.loc[pid, c]) for _, c, _, _ in metrics]
        print(f"{nm}: " + ", ".join(f"{m} {v:.0f}" for (m, *_), v in zip(metrics, vals)))
        ax = fig.add_axes([0.155 + k * 0.475, 0.125, 0.3, 0.59])
        y = np.arange(len(metrics)); cols = [tier(v) for v in vals]
        ax.barh(y, vals, color=cols, height=0.6, zorder=2)
        for i, (v, (lab, _, rc, fmt)) in enumerate(zip(vals, metrics)):
            ax.scatter(v, i, s=860, color=cols[i], edgecolor="white", linewidth=2.2, zorder=3, clip_on=False)
            ax.text(v, i, f"{v:.0f}", ha="center", va="center", fontsize=12.5, fontweight="bold", color="white", zorder=4)
            ax.text(113, i, fmt(raw.loc[pid, rc]), ha="left", va="center", fontsize=14, fontweight="bold", color=INK)
        ax.set_yticks(y, [m[0] for m in metrics], fontsize=14.5, fontweight="bold", color=INK)
        ax.tick_params(axis="y", length=0, pad=8)
        ax.set_xlim(0, 128); ax.set_ylim(-1.3, len(metrics) - 0.5); ax.invert_yaxis()
        for xv, c, st, a in [(0, "#9a9a9a", "-", 1), (50, "gray", "--", 0.5), (100, "#9a9a9a", "-", 1)]:
            ax.vlines(xv, -0.5, len(metrics) - 0.5, color=c, linewidth=1 if st == "--" else 2, linestyle=st, alpha=a)
        ax.text(50, -0.8, "League Average", ha="center", va="bottom", fontsize=12, fontweight="bold", color="gray")
        ax.set_xticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        # player's name big above his panel, centered over the 0-100 bars, with a team-color underline
        cx = 50 / 128
        ax.text(cx, 1.085, nm, transform=ax.transAxes, ha="center", va="bottom", fontsize=24, fontweight="bold", color=TEXT_ON_WHITE[BROWN if pid == MILLER else GOLD])
        ax.plot([cx - 0.32, cx + 0.32], [1.066, 1.066], transform=ax.transAxes, color=BROWN if pid == MILLER else GOLD, lw=4, clip_on=False, solid_capstyle="round")
    finish(fig, "2026 Savant Percentiles", "Mason Miller and Adrián Morejón, Padres | vs all qualified MLB pitchers",
           "Qualified MLB pitchers, 2026 through Sept. 24. Data: Baseball Savant.",
           "miller_morejon_savant_2026.png")


ALL = [whiff_xwoba, k_fip, pitching_ip, savant_percentiles]

if __name__ == "__main__":
    for f in ALL:
        print(f"== {f.__name__}"); f()
