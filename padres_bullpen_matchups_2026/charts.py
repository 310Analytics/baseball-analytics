"""Padres bullpen matchups: Both charts. Reads the FanGraphs exports and matchup_quality_2026.csv; saves to ../figures/."""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))   # paths are relative to this folder

import warnings; warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.lines import Line2D
from pybaseball import cache, statcast, statcast_pitcher

cache.enable()
pd.set_option("display.width", 250)
FIG = "../figures"
LINEUPS = "../padres_game2_game3_starters_2026/opponent_lineups_post_asb_2026.csv"   # shared with the starters project

TEAMS = ["CHC", "PHI", "ATL", "AZ"]
TEAM_NAME = {"CHC": "Cubs", "PHI": "Phillies", "ATL": "Braves", "AZ": "Diamondbacks"}
ASB_START, END = "2026-07-16", "2026-09-24"
BUCKET = {"FF": "Four-seam", "SI": "Sinker", "FC": "Cutter", "SL": "Slider", "ST": "Sweeper",
          "CU": "Curveball", "KC": "Curveball", "SV": "Curveball", "CH": "Changeup", "FS": "Splitter"}
ORDER = ["Four-seam", "Sinker", "Cutter", "Slider", "Sweeper", "Curveball", "Changeup", "Splitter"]
MIN_HITTER_PITCHES, MIN_HAND_PA = 25, 20          # Table 2 flags
K_REG, K_H2H, MIN_LINEUP_PITCHES = 60, 100, 50    # quality model

# name: (file prefix, throwing hand, MLBAM ID). Canning was DFA'd and is excluded.
RELIEVERS = {"Morejon": ("morejon", "L", 670970), "Rodríguez": ("bradgley_rodriguez", "R", 699134),
             "Miller": ("mason_miller", "R", 695243), "Matsui": ("matsui", "L", 673513),
             "Peralta": ("peralta", "L", 593974), "Hart": ("hart", "L", 606996), "Vásquez": ("vasquez", "R", 681190)}
MORGAN = ("Morgan", "david_morgan", 688158)       # under 20 IP since the break: full-season relief mix, quality model only

FG = {"advanced": "mlb_rp_advanced_2h_2026.csv", "statcast": "mlb_rp_statcast_2h_2026.csv",
      "stuff": "mlb_rp_stuff_plus_2h_2026.csv", "wpa": "mlb_rp_win_probability_2h_2026.csv"}


def xwoba(g):
    """Savant-style xwOBA over PA-ending pitches: batted balls use expected wOBA, K/BB/HBP use woba_value."""
    p = g[g["is_pa"] & (g["woba_denom"] > 0)]
    if p.empty:
        return np.nan, 0
    val = np.where(p["type"].eq("X") & p["estimated_woba_using_speedangle"].notna(),
                   p["estimated_woba_using_speedangle"], p["woba_value"])
    return val.sum() / p["woba_denom"].sum(), len(p)


def xw_sums(p):
    """(sum of xwOBA values, sum of woba_denom) over PA-ending pitches."""
    p = p[p["is_pa"] & (p["woba_denom"] > 0)]
    v = np.where(p["type"].eq("X") & p["estimated_woba_using_speedangle"].notna(), p["estimated_woba_using_speedangle"], p["woba_value"])
    return v.sum(), p["woba_denom"].sum()


def weighted(g_same_hand, usage):
    """Usage-weighted lineup xwOBA vs same-handed pitchers; skips pitch types with no PAs and renormalizes."""
    wsum = wused = small = 0.0
    for b in ORDER:
        if usage[b] == 0:
            continue
        sub = g_same_hand[g_same_hand["bucket"] == b]
        x, _ = xwoba(sub)
        if pd.isna(x):
            continue
        wsum += usage[b] * x; wused += usage[b]
        if len(sub) < MIN_HITTER_PITCHES:
            small += usage[b]
    return (wsum / wused if wused else np.nan), wused, small


def starts(d):
    """Games he started: threw the first pitch of his team's defensive half of the 1st."""
    g = d.sort_values(["game_pk", "at_bat_number", "pitch_number"]).groupby("game_pk").head(1)
    home = g["inning_topbot"].eq("Top")
    st = g["inning"].eq(1) & g["outs_when_up"].eq(0) & g[["on_1b", "on_2b", "on_3b"]].isna().all(axis=1) & (~home | g["at_bat_number"].eq(1))
    return set(g.loc[st, "game_pk"])


fx = lambda v: "—" if pd.isna(v) else f"{v:.3f}".lstrip("0")
sgn = lambda v: f"{v:+.3f}".replace("0.", ".")

BROWN, GOLD, GRAY = "#5b3617", "#c9a227", "#B0AFAF"
INK, MUTED, REF, NEUTRAL, LEVER = "#1f1f1f", "#6b6b6b", "#B0AFAF", "#F1EFEB", "#8A8F96"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
# Chart 1: 2nd-half quality, percentile vs all 166 relievers (library #72)
fgread = lambda k: pd.read_csv(FG[k], encoding="utf-8-sig")
rp = (fgread("advanced")[["PlayerId", "Name", "Team", "K-BB%"]].merge(fgread("statcast")[["PlayerId", "IP", "xERA"]], on="PlayerId")
      .merge(fgread("stuff")[["PlayerId", "Stuff+"]], on="PlayerId").merge(fgread("wpa")[["PlayerId", "gmLI"]], on="PlayerId"))
assert len(rp) == 166
POOL = len(rp)
for c, asc in [("K-BB%", True), ("xERA", False), ("Stuff+", True), ("gmLI", True)]:
    rp[c + "_pct"] = rp[c].rank(pct=True, ascending=asc) * 100
pad = rp[(rp["Team"] == "SDP") & (rp["Name"] != "Griffin Canning")].sort_values("K-BB%_pct", ascending=True)   # best ends up on top
assert len(pad) == 7
HAND = {"Adrian Morejon": "L", "Bradgley Rodriguez": "R", "Yuki Matsui": "L", "Mason Miller": "R",
        "Wandy Peralta": "L", "Kyle Hart": "L", "Randy Vásquez": "R"}
DISPLAY = {"Bradgley Rodriguez": "Bradgley Rodríguez"}
PANELS = [("K-BB%", "K-BB%", lambda v: f"{v:.1%}", True), ("xERA", "xERA", lambda v: f"{v:.2f}", True),
          ("Stuff+", "Stuff+", lambda v: f"{v:.0f}", True), ("gmLI", "Leverage (gmLI)\nusage, not quality", lambda v: f"{v:.2f}", False)]
tier = lambda p: BROWN if p >= 67 else (GRAY if p >= 33 else GOLD)

fig = plt.figure(figsize=(16, 7.4))
L, R_, T, B = 0.17, 0.965, 0.76, 0.12
gs = fig.add_gridspec(1, 5, width_ratios=[1, 1, 1, 0.14, 1], left=L, right=R_, top=T, bottom=B, wspace=0.34)
axes = [fig.add_subplot(gs[0, i]) for i in (0, 1, 2, 4)]
y = np.arange(len(pad))
for k, (ax, (col, header, fmt, quality)) in enumerate(zip(axes, PANELS)):
    pct = pad[col + "_pct"].values
    colors = [tier(p) for p in pct] if quality else [LEVER] * len(pct)
    ax.barh(y, pct, height=0.56, color=colors, zorder=2)
    ax.scatter(pct, y, s=560, color=colors, edgecolor="white", linewidth=2, zorder=3)
    for yi, p, v in zip(y, pct, pad[col].values):
        ax.text(p, yi, f"{p:.0f}", ha="center", va="center", fontsize=9.5, fontweight="bold", color="white", zorder=4)
        ax.text(117, yi, fmt(v), ha="left", va="center", fontsize=11, fontweight="bold", color=INK)
    lo, hi = -0.6, len(pad) - 0.4
    ax.vlines(0, lo, hi, color=REF, linewidth=1.2)
    ax.vlines(50, lo, hi, color=REF, linewidth=1, linestyle="--")
    ax.vlines(100, lo, hi, color=REF, linewidth=1.2)
    ax.text(50, hi + 0.08, "League Average" if quality else "Median", ha="center", va="bottom", fontsize=8.5, color=MUTED)
    ax.set_xlim(-6, 138); ax.set_ylim(lo, hi + 0.6)
    ax.set_xticks([])
    ax.set_title(header, fontsize=12.5, fontweight="bold", color=INK if quality else MUTED, pad=18)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_yticks(y, [f"{DISPLAY.get(n, n)} ({HAND[n]}HP)\n{ip} IP" if k == 0 else "" for n, ip in zip(pad["Name"], pad["IP"])],
                  fontsize=11.5, fontweight="bold", color=INK)
tax = fig.add_axes([0, 0.93, 1, 0.001]); tax.axis("off")
tax.set_title("The Padres Bullpen, 2nd Half", fontsize=21, fontweight="bold", color=INK, pad=0)
fig.text(0.5, 0.885, f"Percentile vs all {POOL} MLB relievers with 20+ IP. Sorted by K-BB%.", ha="center", fontsize=12.5, color=MUTED)
fig.legend(handles=[Line2D([0], [0], marker="o", linestyle="", markersize=11, markerfacecolor=c, markeredgecolor="white", label=l)
                    for c, l in [(BROWN, "67th percentile+"), (GRAY, "33rd–66th"), (GOLD, "Below 33rd"), (LEVER, "Leverage (neutral)")]],
           loc="center", bbox_to_anchor=(0.5, 0.845), ncol=4, frameon=False, fontsize=10.5, handletextpad=0.3, columnspacing=1.8)
fig.text(0.5, 0.04, "Data: FanGraphs.com, 2nd half 2026 (7/16–9/23). xERA percentile flipped so higher = better. "
         "gmLI = average leverage when he enters: how he's used, not how well he pitches.",
         ha="center", fontsize=9, color=MUTED, style="italic")
fig.savefig(f"{FIG}/padres_bullpen_quality_2026.png", dpi=200)
plt.close(fig)

# Chart 2: quality-adjusted matchup grid (library #19)
BROWN, GOLD = "#5b3617", "#c9a227"
INK, MUTED, NEUTRAL = "#1f1f1f", "#6b6b6b", "#F1EFEB"
THIN_FILL, THIN_TEXT = "#E4E4E4", "#9A9A9A"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})

mt = pd.read_csv("matchup_quality_2026.csv")
teams = ["Cubs", "Phillies", "Braves", "Diamondbacks"]
rows = mt.groupby("Reliever")["w"].mean().sort_values().index.tolist()
piv = lambda v: mt.pivot(index="Reliever", columns="Opponent", values=v).loc[rows, teams]
W, D, TH, HP = piv("w"), piv("diff"), piv("thin").astype(bool), piv("h2h_pa")
base = mt.drop_duplicates(["Opponent", "hand"]).set_index(["Opponent", "hand"])["base"]
lim = float(np.ceil(mt["diff"].abs().max() * 100) / 100)          # scale from the data
cmap = LinearSegmentedColormap.from_list("sd", [BROWN, NEUTRAL, GOLD])
fx3 = lambda v: f"{v:.3f}".lstrip("0")

# ---- layout in inches
FW = 10.0
CELL = 1.25                                  # square cells
GRID_W, GRID_H = CELL * len(teams), CELL * len(rows)
LIFT = 0.18                                   # room for the extra footnote line
GRID_BOTTOM = 1.95 + LIFT
FH = 12.55 + 1.25 + 0.18
fig = plt.figure(figsize=(FW, FH))
ax = fig.add_axes([(FW - GRID_W) / 2 / FW, GRID_BOTTOM / FH, GRID_W / FW, GRID_H / FH])
ax.imshow(D.values, cmap=cmap, norm=TwoSlopeNorm(0, -lim, lim), aspect="equal")

for i in range(len(rows)):
    for j in range(len(teams)):
        d, w, thin = D.iat[i, j], W.iat[i, j], TH.iat[i, j]
        if thin:                                               # flat gray: not scored reliably
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor=THIN_FILL, edgecolor="none", zorder=2))
            tc = THIN_TEXT
            ax.text(j, i - 0.33, "thin data", ha="center", va="center", fontsize=8.5, style="italic", color=THIN_TEXT, zorder=4)
        else:
            tc = "white" if d < -lim * 0.45 else INK
        ax.text(j, i + 0.02, fx3(w), ha="center", va="center", fontsize=20, fontweight="bold", color=tc, zorder=4)
        ax.text(j, i + 0.27, f"{d:+.3f} vs lineup".replace("0.", ".").replace("-", "−"),
                ha="center", va="center", fontsize=8.5, color=tc, zorder=4)

# white grid lines between cells
GAP_PT, OUT_LW = 12, 4.5                                     # white gap between cells; outline width (points)
PT = 1 / (CELL * 72)                                         # one point in data units
for x in np.arange(-0.5, len(teams) + 0.5):
    ax.axvline(x, color="white", linewidth=GAP_PT, zorder=5, clip_on=False)
for y in np.arange(-0.5, len(rows) + 0.5):
    ax.axhline(y, color="white", linewidth=GAP_PT, zorder=5, clip_on=False)
ax.set_xlim(-0.5, len(teams) - 0.5); ax.set_ylim(len(rows) - 0.5, -0.5)
EDGE = 0.5 - GAP_PT / 2 * PT                                 # edge of the colored area (same for every cell)
OUT = EDGE + (OUT_LW / 2 - 0.8) * PT                                 # outline sits in the cell's own half of the gap

# ---- 1 / 2 tags: outline drawn on the cell edge, badge in the top-left corner
for j, t in enumerate(teams):
    ranked = W[t][~TH[t]].sort_values()                        # thin cells can't rank
    for rank, (num, ls, badge_fill, num_color) in enumerate([("1", "-", "#111111", "white"), ("2", (0, (2.2, 1.2)), "white", "#111111")]):
        i = rows.index(ranked.index[rank])
        ax.add_patch(plt.Rectangle((j - OUT, i - OUT), 2 * OUT, 2 * OUT, fill=False, edgecolor="#111111", linewidth=OUT_LW,
                                   linestyle=ls, joinstyle="miter", zorder=6, clip_on=False))
        ax.add_patch(plt.Circle((j - 0.31, i - 0.31), 0.1, facecolor=badge_fill, edgecolor="#111111", linewidth=1.8, zorder=7))
        ax.text(j - 0.31, i - 0.31, num, ha="center", va="center", fontsize=12, fontweight="heavy", color=num_color, zorder=8)

ax.set_xticks(range(len(teams)), [f"{t}\nvs RHP {fx3(base[(t, 'R')])}\nvs LHP {fx3(base[(t, 'L')])}" for t in teams],
              fontsize=10.5, linespacing=1.3)
ax.xaxis.tick_top()
ax.set_yticks(range(len(rows)), [r.replace("Morgan (RHP)", "Morgan (RHP)*") for r in rows], fontsize=12.5, fontweight="bold", color=INK)
ax.tick_params(length=0)
ax.tick_params(axis="y", pad=12)
ax.tick_params(axis="x", pad=10)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_title("Bullpen Matchups by Opponent", fontsize=20, fontweight="bold", color=INK, pad=92)
ax.text(0.5, 1 + 0.62 / GRID_H * 1.0 + 0.0, "", transform=ax.transAxes)   # placeholder keeps text list stable
sub = fig.text(0.5, (GRID_BOTTOM + GRID_H + 1.02) / FH, "Pitch quality x lineup fit, 2nd half", ha="center", fontsize=12.5, color=MUTED)

# ---- legend bar and footnote
cax = fig.add_axes([0.29, (1.12 + LIFT) / FH, 0.42, 0.18 / FH])
cax.imshow(np.linspace(-lim, lim, 256)[None, :], cmap=cmap, norm=TwoSlopeNorm(0, -lim, lim), aspect="auto")
cax.set_xticks([0, 127.5, 255], [f"−{lim:.3f}".replace("0.", "."), "lineup avg", f"+{lim:.3f}".replace("0.", ".")], fontsize=9)
cax.set_yticks([])
for s in cax.spines.values():
    s.set_visible(False)
cax.tick_params(length=0)
fig.text(0.275, (1.21 + LIFT) / FH, "Better for SD  ◀", ha="right", va="center", fontsize=10.5, fontweight="bold", color=BROWN)
fig.text(0.725, (1.21 + LIFT) / FH, "▶  Worse for SD", ha="left", va="center", fontsize=10.5, fontweight="bold", color=INK)
fig.text(0.5, 0.22 / FH,
         "Score = his 2026 relief xwOBA on each pitch (regressed 60 PA to league) x the lineup's post-break xwOBA on that pitch vs his hand / league,\n"
         f"weighted by his 2nd-half usage, blended with head-to-head xwOBA at PA / (PA + 100); H2H is {int(HP.values.min())}–{int(HP.values.max())} PA per cell. Lower = better for SD.\n"
         "1 = best, 2 = second best. Gray = thin data: lineup has seen < 50 lefty splitters since the break (Cubs 1, Phillies 5, D-backs 23); can't rank. Data: Baseball Savant.\n"
         "*Full season mix, under 20 IP since the break",
         ha="center", fontsize=8.3, color=MUTED, style="italic", linespacing=1.5)

# ---- checks: text vs outlines/badges/figure edge, and top margin
fig.canvas.draw()
rend, fb = fig.canvas.get_renderer(), fig.bbox
problems = []
for t in fig.texts + ax.texts:
    if not t.get_text():
        continue
    bb = t.get_window_extent(rend)
    if bb.x0 < fb.x0 or bb.x1 > fb.x1 or bb.y1 > fb.y1:
        problems.append(f"off-figure: {t.get_text()[:40]!r}")
outlines = [p for p in ax.patches if isinstance(p, plt.Rectangle) and p.get_linewidth() == OUT_LW]
badges = [p for p in ax.patches if isinstance(p, plt.Circle)]
for p in outlines:
    ob = p.get_window_extent(rend); lw = OUT_LW * fig.dpi / 72
    inner = (ob.x0 + lw / 2, ob.y0 + lw / 2, ob.x1 - lw / 2, ob.y1 - lw / 2)
    for t in ax.texts:
        if not t.get_text():
            continue
        tb = t.get_window_extent(rend); cx, cy = (tb.x0 + tb.x1) / 2, (tb.y0 + tb.y1) / 2
        if ob.x0 < cx < ob.x1 and ob.y0 < cy < ob.y1:
            if tb.x0 < inner[0] or tb.x1 > inner[2] or tb.y0 < inner[1] or tb.y1 > inner[3]:
                problems.append(f"text touches outline: {t.get_text()!r}")
            if t.get_text() not in ("1", "2") and any(c.get_window_extent(rend).overlaps(tb) for c in badges):
                problems.append(f"text overlaps badge: {t.get_text()!r}")
title_top_in = ax.title.get_window_extent(rend).y1 / fig.dpi
print(f"layout check: {problems or 'clean'} | top margin above title: {FH - title_top_in:.2f} in")
for t in W.columns:
    r_ = W[t][~TH[t]].sort_values(); print(f"{t}: 1 {r_.index[0]} {r_.iloc[0]:.3f} | 2 {r_.index[1]} {r_.iloc[1]:.3f}")
fig.savefig(f"{FIG}/padres_bullpen_matchups_2026.png", dpi=200)
plt.close(fig)
