"""All six Jack Gurevitch charts. Each function prints the ranks it uses, checks the layout, and saves to ../figures/."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # same renderer inside and outside Jupyter, so saved PNGs match pixel for pixel
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

D = Path(__file__).resolve().parent
FIG = D.parent / "figures"

# Cardinals colors: red for Gurevitch, navy for titles and main text
RED, DOT, REF, INK, MUTED, SHADE = "#C41E3A", "#C9C9C9", "#8a8a8a", "#0C2340", "#6b6b6b", "#FBEAED"
MLB_AVG_EV = 88.0  # 2026 MLB regular season average exit velo, cached Baseball Savant Statcast
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
# Drawn at 11 x 8.2 in; the macOS backend snapped that to 11 x 8.19 (2200 x 1638 px at 200 dpi), so use that size directly
SCATTER_SIZE = (11, 8.19)

ord_ = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
f3 = lambda v: f"{v:.3f}".lstrip("0") if v else "0"
f2 = lambda v: f"{v:.2f}".lstrip("0") if v else "0"
fpct = lambda v: f"{v:.0%}"


def load(pre):
    """FanGraphs standard + advanced + batted ball export for one league, merged on PlayerId."""
    r = lambda k: pd.read_csv(D / f"{pre}_{k}_2026.csv", encoding="utf-8-sig")
    s, a, b = r("standard"), r("advanced"), r("batted_ball")
    d = (s[["PlayerId", "Name", "Age", "PA", "HR"]].merge(a[["PlayerId", "AVG", "OBP", "SLG", "OPS", "ISO", "wRC+"]], on="PlayerId")
         .merge(b[["PlayerId", "HR/FB", "LD%", "FB%"]], on="PlayerId"))
    assert len(d) == len(s) == len(a) == len(b)
    d["HR rate"] = d["HR"] / d["PA"]
    return d


def rank(d, c, hi=True):
    g = d[d.Name.str.contains("Gurevitch")].iloc[0]
    return int(((d[c] > g[c]) if hi else (d[c] < g[c])).sum() + 1)


def check_layout(fig, texts):
    """Print any text that runs off the figure or overlaps other text."""
    fig.canvas.draw()
    rend, fb = fig.canvas.get_renderer(), fig.bbox
    boxes = [(t.get_text()[:25], t.get_window_extent(rend)) for t in texts if t.get_text()]
    off = [n for n, b in boxes if b.x0 < 0 or b.x1 > fb.x1 or b.y1 > fb.y1]
    clash = [(a, b) for i, (a, ba) in enumerate(boxes) for b, bb in boxes[i + 1:] if ba.overlaps(bb)]
    print(f"   layout: off-figure {off or 'none'} | text overlaps {clash or 'none'}")


def save(fig, name):
    fig.savefig(FIG / name, dpi=200)
    plt.close(fig)
    print("   saved", name)


def finish(fig, title, subtitle, foot, name):
    """Shared title / subtitle / footnote / handle for the single-panel scatters."""
    tax = fig.add_axes([0, 0.935, 1, 0.001]); tax.axis("off")
    tax.set_title(title, fontsize=22, fontweight="bold", color=INK, pad=0)
    fig.text(0.5, 0.885, subtitle, ha="center", fontsize=13, color=MUTED)
    fig.text(0.5, 0.035, foot, ha="center", fontsize=9, color=MUTED, style="italic", linespacing=1.5)
    fig.text(0.985, 0.012, "@310Analytics", ha="right", va="bottom", fontsize=9, color=MUTED)
    check_layout(fig, list(fig.texts) + [t for a in fig.axes for t in a.texts])
    save(fig, name)


def scatter_panel(ax, d, xc, yc, xlim, ylim, callout, xfmt, yfmt, xlab, ylab, x_reverse=False, jitter=0.0, offset=(-0.2, 0.2)):
    """Gray dots for every hitter, Gurevitch as the big red dot with a callout, dashed medians, shaded good quadrant."""
    g = d[d.Name.str.contains("Gurevitch")].iloc[0]
    rest = d[d["PlayerId"] != g["PlayerId"]]
    rng = np.random.default_rng(7)
    xs = rest[xc] + (rng.uniform(-jitter, jitter, len(rest)) if jitter else 0)
    mx, my = d[xc].median(), d[yc].median()
    # light shading on the "good" quadrant: above the y median and on the good side of the x median
    x_good = (xlim[0], mx) if x_reverse else (mx, xlim[1])
    ax.add_patch(plt.Rectangle((x_good[0], my), x_good[1] - x_good[0], ylim[1] - my, facecolor=SHADE, edgecolor="none", zorder=0))
    ax.scatter(xs, rest[yc], s=30, color=DOT, edgecolor="white", linewidth=0.5, zorder=2)
    ax.axvline(mx, color=REF, lw=1.3, ls="--", zorder=1); ax.axhline(my, color=REF, lw=1.3, ls="--", zorder=1)
    xspan, yspan = xlim[1] - xlim[0], ylim[1] - ylim[0]
    # median labels placed in screen space so they sit right of the x line and inside the right edge, reversed axis or not
    ax.annotate(f"median {xfmt(mx)}", xy=(mx, 1), xycoords=ax.get_xaxis_transform(), xytext=(5, -5), textcoords="offset points",
                ha="left", va="top", fontsize=9, color=MUTED)
    ax.annotate(f"median {yfmt(my)}", xy=(1, my), xycoords=ax.get_yaxis_transform(), xytext=(-4, 4), textcoords="offset points",
                ha="right", va="bottom", fontsize=9, color=MUTED)
    ax.scatter(g[xc], g[yc], s=320, color=RED, edgecolor="white", linewidth=2.2, zorder=4)
    ax.annotate(callout, xy=(g[xc], g[yc]), xytext=(g[xc] + offset[0] * xspan, g[yc] + offset[1] * yspan),
                fontsize=11, fontweight="bold", color=RED, ha="center", va="bottom", linespacing=1.35, zorder=5,
                bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=RED, linewidth=1.2),
                arrowprops=dict(arrowstyle="-", color=RED, lw=1.4))
    ax.set_xlim(*(xlim[::-1] if x_reverse else xlim)); ax.set_ylim(*ylim)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: xfmt(v))); ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: yfmt(v)))
    ax.set_xlabel(xlab, fontsize=11.5, color=INK); ax.set_ylabel(ylab, fontsize=11.5, color=INK)
    ax.tick_params(colors=MUTED, labelsize=10)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)


# ---------------------------------------------------------------- Top 10 Power in Two Leagues
def projection():
    leagues = [("high_a", "High-A: Midwest League"), ("aa", "Double-A: Texas League")]
    data = {}
    for pre, _ in leagues:
        s = pd.read_csv(D / f"{pre}_standard_2026.csv", encoding="utf-8-sig")
        a = pd.read_csv(D / f"{pre}_advanced_2026.csv", encoding="utf-8-sig")
        d = s[["PlayerId", "Name", "PA", "HR"]].merge(a[["PlayerId", "ISO"]], on="PlayerId", how="inner")
        assert len(d) == len(s) == len(a)
        d["HR_PA"] = d["HR"] / d["PA"]
        for c in ["HR_PA", "ISO"]:
            d[c + "_rank"] = d[c].rank(ascending=False, method="min").astype(int)
        data[pre] = d

    # same ranges on both panels
    XMAX = np.ceil(max(d["HR_PA"].max() for d in data.values()) * 100 + 0.5) / 100
    YMAX = np.ceil(max(d["ISO"].max() for d in data.values()) * 20 + 0.5) / 20

    fig = plt.figure(figsize=(15, 8))
    for k, (pre, title) in enumerate(leagues):
        d = data[pre]
        g = d[d["Name"].str.contains("Gurevitch")].iloc[0]
        ax = fig.add_axes([0.07 + k * 0.49, 0.15, 0.41, 0.6])
        rest = d[d["PlayerId"] != g["PlayerId"]]
        ax.scatter(rest["HR_PA"], rest["ISO"], s=30, color=DOT, edgecolor="white", linewidth=0.5, zorder=2)
        mx, my = d["HR_PA"].median(), d["ISO"].median()
        ax.axvline(mx, color=REF, lw=1.3, ls="--", zorder=1)
        ax.axhline(my, color=REF, lw=1.3, ls="--", zorder=1)
        # light shading above both medians, same as the other Gurevitch scatters
        ax.add_patch(plt.Rectangle((mx, my), XMAX - mx, YMAX - my, facecolor=SHADE, edgecolor="none", zorder=0))
        ax.text(mx + 0.001, YMAX * 0.985, f"median {mx:.1%}", ha="left", va="top", fontsize=9, color=MUTED)
        ax.text(XMAX * 0.99, my + 0.006, f"median {my:.3f}".replace("0.", "."), ha="right", va="bottom", fontsize=9, color=MUTED)
        ax.scatter(g["HR_PA"], g["ISO"], s=320, color=RED, edgecolor="white", linewidth=2.2, zorder=4)
        n = len(d)
        ax.annotate(f"Jack Gurevitch\nAmong {n} {title.split(': ')[1]} hitters:\nHR rate: {ord_(g['HR_PA_rank'])}\nISO: {ord_(g['ISO_rank'])}",
                    xy=(g["HR_PA"], g["ISO"]), xytext=(g["HR_PA"] - 0.028, g["ISO"] + 0.085),
                    fontsize=11, fontweight="bold", color=RED, ha="center", va="bottom", linespacing=1.35, zorder=5,
                    bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=RED, linewidth=1.2),
                    arrowprops=dict(arrowstyle="-", color=RED, lw=1.4))
        ax.set_xlim(0, XMAX); ax.set_ylim(0, YMAX)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.2f}".lstrip("0") if v else "0"))
        ax.set_xlabel("HR per PA", fontsize=11.5, color=INK)
        ax.set_ylabel("ISO", fontsize=11.5, color=INK)
        ax.tick_params(colors=MUTED, labelsize=10)
        for sp in ["top", "right"]:
            ax.spines[sp].set_visible(False)
        ax.set_title(f"{title}\n", fontsize=14.5, fontweight="bold", color=INK, pad=4, linespacing=1.1)
        ax.text(0.5, 1.02, f"{n} hitters, 130+ PA · Gurevitch: {g['HR']} HR in {g['PA']} PA, {g['ISO']:.3f} ISO".replace(" 0.", " ."),
                transform=ax.transAxes, ha="center", va="bottom", fontsize=10, color=MUTED)
        print(f"{title}: HR/PA {g['HR_PA']:.1%} rank {g['HR_PA_rank']}/{n}, ISO {g['ISO']:.3f} rank {g['ISO_rank']}/{n}")

    tax = fig.add_axes([0, 0.935, 1, 0.001]); tax.axis("off")
    tax.set_title("Top 10 Power in Two Leagues", fontsize=22, fontweight="bold", color=INK, pad=0)
    fig.text(0.5, 0.885, "Jack Gurevitch, Cardinals 1B, age 22 | Midwest League and Texas League, 130+ PA, 2026", ha="center", fontsize=13, color=MUTED)
    fig.text(0.5, 0.035, "Minimum 130 PA in each league. HR rate = HR / PA. Ranks are among Midwest League or Texas League hitters with 130+ PA; dashed lines = league medians. "
             "Same axis ranges on both panels.\nData: FanGraphs.com minor league leaderboards, 2026 (Midwest League, Texas League).",
             ha="center", fontsize=9, color=MUTED, style="italic", linespacing=1.5)
    fig.text(0.985, 0.012, "@310Analytics", ha="right", va="bottom", fontsize=9, color=MUTED)
    check_layout(fig, list(fig.texts) + [t for a in fig.axes for t in a.texts])
    save(fig, "gurevitch_projection_2026.png")


# ---------------------------------------------------------------- Power Ahead of His Age
def age_power():
    d = load("aa"); n = len(d); g = d[d.Name.str.contains("Gurevitch")].iloc[0]
    iso_r = rank(d, "ISO"); older = (d["Age"] > g["Age"]).mean()
    print(f"Texas League: ISO {g.ISO:.3f} rank {iso_r}/{n} (top {iso_r / n:.1%}) | {older:.1%} of hitters older than {g.Age}")
    fig = plt.figure(figsize=SCATTER_SIZE)
    ax = fig.add_axes([0.1, 0.16, 0.84, 0.6])
    scatter_panel(ax, d, "Age", "ISO", (d.Age.min() - 0.8, d.Age.max() + 0.8), (0, 0.5),
                  f"Jack Gurevitch, {g.Age}\nAmong {n} Texas League hitters:\nISO: {ord_(iso_r)}\n{older:.0%} are older than him",
                  lambda v: f"{v:.0f}", f2, "Age (younger →)", "ISO", x_reverse=True, jitter=0.28, offset=(0.16, 0.14))
    ax.set_title("Double-A: Texas League\n", fontsize=14.5, fontweight="bold", color=INK, pad=4, linespacing=1.1)
    ax.text(0.5, 1.02, f"{n} hitters, 130+ PA · Gurevitch: {g.HR} HR in {g.PA} PA, {f3(g.ISO)} ISO", transform=ax.transAxes, ha="center", va="bottom", fontsize=10, color=MUTED)
    finish(fig, "Power Ahead of His Age", "Jack Gurevitch, Cardinals 1B, age 22 | Texas League, 130+ PA, 2026",
           "Double-A (Texas League), minimum 130 PA. Ages are FanGraphs season ages; dots are spread slightly left-right within each age so they don't stack.\n"
           "Dashed lines = league medians. Shaded = younger than the median and above-median ISO. Data: FanGraphs.com minor league leaderboards, 2026.",
           "gurevitch_age_power_2026.png")


# ---------------------------------------------------------------- No. 1 in HR/FB
def batted_ball():
    d = load("aa"); n = len(d); g = d[d.Name.str.contains("Gurevitch")].iloc[0]
    hrfb_r, ld_r = rank(d, "HR/FB"), rank(d, "LD%")
    print(f"Texas League: HR/FB {g['HR/FB']:.1%} rank {hrfb_r}/{n} (top {hrfb_r / n:.1%}) | LD% {g['LD%']:.1%} rank {ld_r}/{n} (top {ld_r / n:.1%})")
    fig = plt.figure(figsize=SCATTER_SIZE)
    ax = fig.add_axes([0.1, 0.16, 0.84, 0.6])
    scatter_panel(ax, d, "HR/FB", "LD%", (0, np.ceil(d["HR/FB"].max() * 20) / 20 + 0.02), (0, np.ceil(d["LD%"].max() * 20) / 20 + 0.02),
                  f"Jack Gurevitch\nAmong {n} Texas League hitters:\nHR/FB: {ord_(hrfb_r)}\nLD%: {ord_(ld_r)}", fpct, fpct, "HR/FB", "Line drive %", offset=(-0.22, 0.12))
    ax.set_title("Double-A: Texas League\n", fontsize=14.5, fontweight="bold", color=INK, pad=4, linespacing=1.1)
    ax.text(0.5, 1.02, f"{n} hitters, 130+ PA · Gurevitch: {g['HR/FB']:.1%} HR/FB, {g['LD%']:.1%} LD% ({g.HR} HR in {g.PA} PA)", transform=ax.transAxes, ha="center", va="bottom", fontsize=10, color=MUTED)
    finish(fig, "No. 1 in HR/FB", "Jack Gurevitch, Cardinals 1B, age 22 | Texas League, 130+ PA, 2026",
           "Double-A (Texas League), minimum 130 PA. HR/FB = home runs per fly ball; LD% = line drives per ball in play. Small sample: 141 PA in the Texas League.\n"
           "Dashed lines = league medians. Shaded = above the median on both. Data: FanGraphs.com minor league leaderboards, 2026.",
           "gurevitch_batted_ball_2026.png")


# ---------------------------------------------------------------- Midwest League Percentiles (chart library #72)
def power_profile():
    d = load("high_a"); n = len(d); g = d[d.Name.str.contains("Gurevitch")].iloc[0]
    metrics = [("SLG", "SLG", f3), ("HR rate", "HR rate (HR/PA)", lambda v: f"{v:.1%}"), ("HR/FB", "HR/FB", lambda v: f"{v:.1%}"),
               ("ISO", "ISO", f3), ("OPS", "OPS", f3), ("AVG", "AVG", f3), ("wRC+", "wRC+", lambda v: f"{v:.0f}")]
    pct = {c: d[c].rank(pct=True, method="average")[g.name] * 100 for c, _, _ in metrics}
    print("Midwest League percentiles:", {c: f"{pct[c]:.0f} (rank {rank(d, c)}/{n})" for c, _, _ in metrics})
    color = lambda p: RED if p >= 67 else ("#B0AFAF" if p >= 33 else INK)
    fig, ax = plt.subplots(figsize=(9, 8))
    y = np.arange(len(metrics))
    vals = [pct[c] for c, _, _ in metrics]
    cols = [color(p) for p in vals]
    ax.barh(y, vals, color=cols, height=0.6, zorder=2)
    for i, (p, (c, lab, fmt)) in enumerate(zip(vals, metrics)):
        ax.scatter(p, i, s=500, color=cols[i], edgecolor="white", linewidth=2, zorder=3)
        ax.text(p, i, f"{int(round(p))}", ha="center", va="center", fontsize=10, fontweight="bold", color="white", zorder=4)
        ax.text(103, i, fmt(g[c]), ha="left", va="center", fontsize=11, fontweight="bold", color=INK)
    ax.set_yticks(y, [lab for _, lab, _ in metrics], fontsize=12, fontweight="bold", color=INK)
    ax.set_xlim(0, 115); ax.set_ylim(-1.2, len(metrics) - 0.5); ax.invert_yaxis()
    ax.vlines(0, -0.5, len(metrics) - 0.5, color=INK, linewidth=2)
    ax.vlines(50, -0.5, len(metrics) - 0.5, color="gray", linewidth=1, linestyle="--", alpha=0.5)
    ax.vlines(100, -0.5, len(metrics) - 0.5, color=RED, linewidth=2)
    ax.text(50, -0.7, "Midwest League Median", ha="center", va="bottom", fontsize=11, fontweight="bold", color="gray")
    ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("Midwest League Percentiles", fontsize=22, fontweight="bold", color=INK, pad=34)
    ax.text(0.5, 1.012, "Jack Gurevitch, Cardinals 1B, age 22 | Midwest League, 130+ PA, 2026", transform=ax.transAxes, ha="center", va="bottom", fontsize=13, color=MUTED)
    fig.text(0.47, 0.035, "High-A (Midwest League), minimum 130 PA. HR rate = HR / PA. Data: FanGraphs.com minor league leaderboards, 2026.",
             ha="center", fontsize=9, style="italic", color="#555555")
    fig.text(0.985, 0.012, "@310Analytics", ha="right", va="bottom", fontsize=9, color=MUTED)
    plt.subplots_adjust(left=0.24, right=0.86, top=0.87, bottom=0.07)
    check_layout(fig, list(fig.texts) + list(ax.texts) + [ax.title])
    save(fig, "gurevitch_power_profile_2026.png")


# ---------------------------------------------------------------- Line Drives, Few Pop Ups
def line_drives():
    d = pd.read_csv(D / "tjstats_batter_batted_ball_2026.csv")
    d = d[d.bip >= 75].rename(columns={"player_name": "Name", "player_id": "PlayerId", "pop_up_percent": "PU", "line_drive_percent": "LD"}).reset_index(drop=True)
    n = len(d); g = d[d.Name.str.contains("Gurevitch")].iloc[0]
    pu_r, ld_r = rank(d, "PU", hi=False), rank(d, "LD")
    print(f"All Double-A leagues, 75+ BBE: {n} hitters | pop-up {g.PU:.1%} rank {pu_r}/{n} (top {pu_r / n:.1%}) | "
          f"LD {g.LD:.1%} rank {ld_r}/{n} (top {ld_r / n:.1%}) | {g.bip} batted balls")
    fig = plt.figure(figsize=SCATTER_SIZE)
    ax = fig.add_axes([0.1, 0.16, 0.84, 0.6])
    scatter_panel(ax, d, "PU", "LD", (-0.005, np.ceil(d.PU.max() * 20) / 20), (0.1, np.ceil(d.LD.max() * 20) / 20 + 0.02),
                  f"Jack Gurevitch\nAmong {n} hitters, all Double-A leagues:\nPop-up rate: {ord_(pu_r)}\nLine drive rate: {ord_(ld_r)}", fpct, fpct,
                  "Pop-up rate (lower →)", "Line drive rate", x_reverse=True, offset=(0.2, 0.16))
    ax.xaxis.set_major_locator(plt.MultipleLocator(0.05))
    ax.set_title("All Double-A Leagues (Texas, Southern, Eastern)\n", fontsize=14.5, fontweight="bold", color=INK, pad=4, linespacing=1.1)
    ax.text(0.5, 1.02, f"{n} hitters, 75+ batted balls · Gurevitch: {g.PU:.1%} pop-ups, {g.LD:.1%} line drives ({g.bip} batted balls)",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=10, color=MUTED)
    finish(fig, "Line Drives, Few Pop Ups", "Jack Gurevitch, Cardinals 1B, age 22 | All Double-A leagues, 75+ batted balls, 2026",
           f"All Double-A leagues (Texas, Southern, Eastern), minimum 75 batted balls. Rates are per batted ball. Dashed lines = all-Double-A medians.\n"
           f"Shaded = fewer pop-ups and more line drives than the median. Small sample: {g.bip} batted balls, all in the Texas League. Data: TJStats, 2026.",
           "gurevitch_line_drives_2026.png")


# ---------------------------------------------------------------- Exit Velo by Pitch Type (Florida State League pitch tracking)
GROUP = {"FF": "Fastball", "SI": "Fastball", "FC": "Fastball", "SL": "Breaking", "ST": "Breaking", "CU": "Breaking", "KC": "Breaking",
         "SV": "Breaking", "CH": "Offspeed", "FS": "Offspeed"}


def exit_velo():
    ev_ref = "#6b6b6b"  # this chart's MLB line is darker than the scatter medians
    df = pd.read_csv(D / "gurevitch_pitches_2026_statsapi.csv")
    bip = df[(df["level"] == "Low-A") & (df["is_in_play"] == True) & df["launch_speed"].notna()].copy()
    bip["group"] = bip["pitch_type"].map(GROUP)
    cats = [("Fastballs\n93+ mph", (bip.group == "Fastball") & (bip.start_speed >= 93)),
            ("Fastballs\nunder 93", (bip.group == "Fastball") & (bip.start_speed < 93)),
            ("Breaking", bip.group == "Breaking"), ("Offspeed", bip.group == "Offspeed")]
    labels = [c for c, _ in cats]
    ev = [bip.loc[m, "launch_speed"].mean() for _, m in cats]
    n = [int(m.sum()) for _, m in cats]
    assert sum(n) == len(bip) == 65, (n, len(bip))
    print("Florida State League avg EV (BBE):", dict(zip([l.replace("\n", " ") for l in labels], [f"{e:.1f} ({k})" for e, k in zip(ev, n)])))

    fig = plt.figure(figsize=(10, 7.0))
    ax = fig.add_axes([0.1, 0.17, 0.74, 0.66])
    x = np.arange(len(cats))
    bars = ax.bar(x, ev, width=0.58, color=RED, zorder=2)
    ax.axhline(MLB_AVG_EV, color=ev_ref, lw=1.8, ls="--", zorder=3)
    ax.text(1.015, MLB_AVG_EV, f"2026 MLB avg\n{MLB_AVG_EV:.1f} mph", transform=ax.get_yaxis_transform(), ha="left", va="center",
            fontsize=10.5, color=ev_ref, linespacing=1.25)
    for b, e, k in zip(bars, ev, n):
        cx = b.get_x() + b.get_width() / 2
        ax.text(cx, e + 1.5, f"{e:.1f} mph", ha="center", va="bottom", fontsize=14, fontweight="bold", color=INK)
        ax.text(cx, 12, f"{k} batted\nballs", ha="center", va="center", fontsize=10.5, color="white", fontweight="bold", linespacing=1.2, zorder=4)
    ax.set_xticks(x, labels, fontsize=12, color=INK)
    ax.set_ylim(0, 110)
    ax.set_ylabel("Avg exit velocity (mph)", fontsize=11.5, color=INK)
    ax.tick_params(axis="x", length=0)
    ax.tick_params(axis="y", colors=MUTED, labelsize=10)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.set_title("Exit Velo by Pitch Type", fontsize=22, fontweight="bold", color=INK, pad=38)
    ax.text(0.5, 1.03, "Jack Gurevitch, Cardinals 1B, age 22 | Florida State League, 65 tracked batted balls, 2026", transform=ax.transAxes, ha="center", fontsize=13, color=MUTED)
    fig.text(0.5, 0.025, f"Small sample: {len(bip)} Florida State League batted balls with exit velo ({min(n)}–{max(n)} per group).\n"
             "Fastballs = four-seam, sinker, cutter. Breaking = slider, sweeper, curveball. Offspeed = changeup, splitter.\n"
             "MLB average: 2026 regular season Statcast. Data: MLB Stats API (Florida State League pitch tracking), Baseball Savant.",
             ha="center", fontsize=8.8, color=MUTED, style="italic", linespacing=1.5)
    check_layout(fig, list(fig.texts) + list(ax.texts) + [ax.title])
    save(fig, "gurevitch_exit_velo_2026.png")


ALL = [projection, age_power, batted_ball, power_profile, line_drives, exit_velo]


def make_all():
    for f in ALL:
        print(f"== {f.__name__}")
        f()


if __name__ == "__main__":
    make_all()
