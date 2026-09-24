"""Padres Games 2-3: both charts. Reads the CSVs written by matchup.py."""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))   # paths are relative to this folder

import warnings; warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from pybaseball import cache, statcast, statcast_pitcher, playerid_reverse_lookup

cache.enable()
pd.set_option("display.width", 200)

FIG = "../figures"

# Padres starters: MLBAM ID, throwing hand
STARTERS = {"Buehler": (621111, "R"), "Mize": (663554, "R"), "Ray": (592662, "L"), "Pivetta": (601713, "R")}
STARTER_START, STARTER_END = "2026-08-20", "2026-09-24"

# Opponents: batting team abbreviations as Statcast uses them
TEAMS = ["CHC", "PHI", "ATL", "AZ"]
TEAM_NAME = {"CHC": "Cubs", "PHI": "Phillies", "ATL": "Braves", "AZ": "Diamondbacks"}
ASB_START = "2026-07-16"          # first game after the All-Star break
RECENT_GAMES, MIN_RECENT_PA = 15, 25

# Pitch-type buckets (knuckle curves and slurves count as curveballs)
BUCKET = {"FF": "Four-seam", "SI": "Sinker", "FC": "Cutter", "SL": "Slider", "ST": "Sweeper",
          "CU": "Curveball", "KC": "Curveball", "SV": "Curveball", "CH": "Changeup", "FS": "Splitter"}
ORDER = ["Four-seam", "Sinker", "Cutter", "Slider", "Sweeper", "Curveball", "Changeup", "Splitter"]
SWING = {"swinging_strike", "swinging_strike_blocked", "foul", "foul_tip", "hit_into_play"}
WHIFF = {"swinging_strike", "swinging_strike_blocked"}
K_EVENTS = {"strikeout", "strikeout_double_play"}

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

BROWN, GOLD = "#5b3617", "#c9a227"          # Padres good / bad
INK, MUTED, REF, NEUTRAL = "#1f1f1f", "#6b6b6b", "#B0AFAF", "#F1EFEB"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})

# Chart 1: starter profile vs MLB SP average (library #81 with #72's direction rule)
lg = pd.read_csv("mlb_sp_league_averages_2026.csv").set_index("metric")["value"].to_dict()
fg = lambda f: pd.read_csv(f, encoding="utf-8-sig").set_index("MLBAMID")
adv, fsc, stf = fg("padres_sp_advanced_2026.csv"), fg("padres_sp_statcast_2026.csv"), fg("padres_sp_stuff_plus_2026.csv")


def xwoba_pa(p):
    p = p[p["woba_denom"] > 0]
    v = np.where(p["type"].eq("X") & p["estimated_woba_using_speedangle"].notna(),
                 p["estimated_woba_using_speedangle"], p["woba_value"])
    return v.sum() / p["woba_denom"].sum()


vals, bf = {}, {}
for name, (pid, _) in STARTERS.items():
    s = pd.read_csv(f"{name.lower()}_statcast_aug20_sep24_2026.csv")
    p = s[s["events"].notna() & (s["events"] != "truncated_pa")]
    bf[name] = len(p)
    vals[name] = {
        "K-BB%": adv.loc[pid, "K-BB%"], "BB%": adv.loc[pid, "BB%"], "xERA": fsc.loc[pid, "xERA"],
        "Stuff+": stf.loc[pid, "Stuff+"], "Location+": stf.loc[pid, "Location+"],
        "P/BF": len(s) / len(p), "xwOBA 2nd TTO": xwoba_pa(p[p["n_thruorder_pitcher"] == 2]),
    }

# metric: (header, higher_is_better, formatter)
pct = lambda v: f"{v:.1%}"
METRICS = {
    "K-BB%": ("K-BB%", True, pct),
    "BB%": ("BB%", False, pct),
    "xERA": ("xERA", False, lambda v: f"{v:.2f}"),
    "Stuff+": ("Stuff+", True, lambda v: f"{v:.0f}"),
    "Location+": ("Location+", True, lambda v: f"{v:.0f}"),
    "P/BF": ("Pitches / BF", False, lambda v: f"{v:.2f}"),
    "xwOBA 2nd TTO": ("xwOBA, 2nd\ntime thru order", False, lambda v: f"{v:.3f}".lstrip("0")),
}

# sign-adjusted gap to MLB SP average: positive = better
gap = {n: {m: (v[m] - lg[m]) * (1 if METRICS[m][1] else -1) for m in METRICS} for n, v in vals.items()}
order = sorted(STARTERS, key=lambda n: (sum(g > 0 for g in gap[n].values()), vals[n]["Stuff+"] + vals[n]["Location+"]))

fig, axes = plt.subplots(1, len(METRICS), figsize=(16, 6.2), sharey=True)
plt.subplots_adjust(left=0.10, right=0.97, top=0.72, bottom=0.12, wspace=0.22)
y = np.arange(len(order))
for ax, (m, (header, hib, f)) in zip(axes, METRICS.items()):
    g = np.array([gap[n][m] for n in order])
    lim = max(abs(g).max(), 1e-9) * 2.6
    ax.barh(y, g, height=0.62, color=[BROWN if v > 0 else GOLD for v in g], edgecolor="white", linewidth=2)
    ax.vlines(0, -0.6, len(order) - 0.4, color=REF, linestyle="--", linewidth=1.2)
    for yi, (gv, n) in enumerate(zip(g, order)):
        ax.text(gv + (lim * 0.06 if gv >= 0 else -lim * 0.06), yi, f(vals[n][m]), va="center",
                ha="left" if gv >= 0 else "right", fontsize=11, fontweight="bold", color=INK)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-0.6, len(order) - 0.4)
    ax.set_xticks([])
    ax.set_title(f"{header}\n", fontsize=12, fontweight="bold", color=INK, pad=4, linespacing=1.1)
    ax.text(0.5, 1.02, "MLB SP avg " + f(lg[m]).replace("\n", " "), transform=ax.transAxes,
            ha="center", va="bottom", fontsize=9, color=MUTED)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(axis="y", length=0)
axes[0].set_yticks(y, [f"{n}\n{bf[n]} BF" for n in order], fontsize=12, fontweight="bold", color=INK)

# spanning invisible axis carries the centered title
tax = fig.add_axes([0.0, 0.925, 1.0, 0.001]); tax.axis("off")
tax.set_title("Who Starts Games 2 and 3?", fontsize=20, fontweight="bold", color=INK, pad=0)
fig.text(0.5, 0.885, "Padres SP since 8/20/26", ha="center", fontsize=13, color=MUTED)
fig.text(0.5, 0.852, "Bars right of the dashed line = better than MLB SP average; left = worse. Labels are each pitcher's actual value.",
         ha="center", fontsize=10, color=MUTED)
fig.text(0.5, 0.04, "Data: FanGraphs.com & Baseball Savant, 8/20/26–9/24/26. MLB SP avg = 159 starters with 10+ IP. "
         "Stuff+/Location+: 100 = average.", ha="center", fontsize=9, color=MUTED, style="italic")
fig.savefig(f"{FIG}/padres_game2_game3_starters_2026.png", dpi=200)
plt.close(fig)
print("Saved", f"{FIG}/padres_game2_game3_starters_2026.png")

# Chart 2: best matchups by opponent (library #19 heatmap format)
mt = pd.read_csv("matchup_table_post_asb_2026.csv")
teams = ["Cubs", "Phillies", "Braves", "Diamondbacks"]
rows = ["Buehler (RHP)", "Mize (RHP)", "Ray (LHP)", "Pivetta (RHP)"]
W = mt.pivot(index="Starter", columns="Opponent", values="Weighted xwOBA").loc[rows, teams]
D = mt.pivot(index="Starter", columns="Opponent", values="Diff").loc[rows, teams]
base = mt.pivot(index="Starter", columns="Opponent", values="Lineup xwOBA vs hand").loc[rows, teams]

cmap = LinearSegmentedColormap.from_list("sd", [BROWN, NEUTRAL, GOLD])
lim = 0.03
fig = plt.figure(figsize=(10, 9.4))
GW = 0.56
ax = fig.add_axes([0.5 - GW / 2, 0.16, GW, GW * 10 / 9.4])   # grid centered on the canvas, square cells
ax.imshow(D.values, cmap=cmap, norm=TwoSlopeNorm(0, -lim, lim), aspect="equal")
fx3 = lambda v: f"{v:.3f}".lstrip("0")
for i in range(len(rows)):
    for j in range(len(teams)):
        d, w = D.iat[i, j], W.iat[i, j]
        tc = "white" if d < -lim * 0.45 else INK
        ax.text(j, i - 0.08, fx3(w), ha="center", va="center", fontsize=20, fontweight="bold", color=tc)
        ax.text(j, i + 0.26, f"{d:+.3f} vs lineup".replace("0.", ".").replace("-", "−"),
                ha="center", va="center", fontsize=9.5, color=tc)
# best (lowest weighted xwOBA) per opponent
for j, t in enumerate(teams):
    i = int(np.argmin(W[t].values))
    ax.add_patch(plt.Rectangle((j - 0.47, i - 0.47), 0.94, 0.94, fill=False, edgecolor=INK, linewidth=3))
    ax.text(j, i - 0.37, "BEST", ha="center", va="center", fontsize=8.5, fontweight="bold",
            color="white" if D.iat[i, j] < -lim * 0.45 else INK)
ax.set_xticks(range(len(teams)), [f"{t}\nvs RHP {fx3(base.loc['Buehler (RHP)', t])}\nvs LHP {fx3(base.loc['Ray (LHP)', t])}"
                                  for t in teams], fontsize=10.5, linespacing=1.3)
for lbl in ax.get_xticklabels():
    lbl.set_color(INK)
ax.xaxis.tick_top()
ax.set_yticks(range(len(rows)), rows, fontsize=13, fontweight="bold", color=INK)
ax.tick_params(length=0)
for sp in ax.spines.values():
    sp.set_visible(False)
ax.set_xticks(np.arange(-0.5, len(teams)), minor=True)
ax.set_yticks(np.arange(-0.5, len(rows)), minor=True)
ax.grid(which="minor", color="white", linewidth=4)
ax.tick_params(which="minor", length=0)
ax.set_title("Best Matchups by Opponent", fontsize=20, fontweight="bold", color=INK, pad=96)
ax.text(0.5, 1.185, "Starter pitch mix since 8/20 vs opponent lineup, post All-Star break", transform=ax.transAxes,
        ha="center", fontsize=12.5, color=MUTED)

# legend bar: brown = better for SD, gold = worse
cax = fig.add_axes([0.29, 0.088, 0.42, 0.02])
cax.imshow(np.linspace(-lim, lim, 256)[None, :], cmap=cmap, norm=TwoSlopeNorm(0, -lim, lim), aspect="auto")
cax.set_xticks([0, 127.5, 255], [f"−{lim:.3f}".replace("0.", "."), "lineup avg", f"+{lim:.3f}".replace("0.", ".")], fontsize=9)
cax.set_yticks([])
for sp in cax.spines.values():
    sp.set_visible(False)
cax.tick_params(length=0)
fig.text(0.275, 0.098, "Better for SD  ◀", ha="right", va="center", fontsize=10.5, fontweight="bold", color=BROWN)
fig.text(0.725, 0.098, "▶  Worse for SD", ha="left", va="center", fontsize=10.5, fontweight="bold", color=INK)
fig.text(0.5, 0.012, "Big number = opponent lineup's xwOBA vs each pitch type (from same-handed pitchers), weighted by the starter's usage.\n"
         "Lower = better for SD. Color = gap to that lineup's own xwOBA vs the starter's hand.\n"
         "Lineup = top 9 hitters by PA post All-Star break (7/16–9/23/26) with 25+ PA in the last 15 games. Data: Baseball Savant.",
         ha="center", fontsize=8.3, color=MUTED, style="italic", linespacing=1.45)
fig.savefig(f"{FIG}/padres_starter_matchups_2026.png", dpi=200)
plt.close(fig)
print("Saved", f"{FIG}/padres_starter_matchups_2026.png")
