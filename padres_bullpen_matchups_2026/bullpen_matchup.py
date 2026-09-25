"""Padres bullpen matchups: Relief-only pulls since the break, opponent lineups, Table 1 (mix fit) and Table 2 (heart of lineup)."""
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

# Relief-only Statcast since the break for the 7 relievers (starts dropped)
for name, (f, hand, pid) in RELIEVERS.items():
    d = statcast_pitcher(ASB_START, END, pid)
    d = d[d["game_type"] == "R"]
    st = starts(d)
    d = d[~d["game_pk"].isin(st)].sort_values(["game_date", "at_bat_number", "pitch_number"])
    d.to_csv(f"{f}_statcast_post_asb_2026.csv", index=False)
    print(f"{name:10s} {hand}HP  {len(d)} relief pitches since 7/16 (dropped {len(st)} starts)")

# Opponent pitches (cached league pull), current lineup hitters only
cols = ["game_pk", "game_date", "game_type", "home_team", "away_team", "inning_topbot", "batter", "stand",
        "p_throws", "pitch_type", "events", "type", "estimated_woba_using_speedangle", "woba_value", "woba_denom"]
parts = []
for s, e in [("2026-07-01", "2026-07-31"), ("2026-08-01", "2026-08-31"), ("2026-09-01", END)]:
    raw = statcast(s, e, verbose=False)
    raw = raw[raw["game_type"] == "R"]
    bat = raw["away_team"].where(raw["inning_topbot"] == "Top", raw["home_team"])
    raw = raw.assign(bat_team=bat)
    parts.append(raw[bat.isin(TEAMS) & (raw["game_date"] >= ASB_START)][cols + ["bat_team"]])
opp = pd.concat(parts, ignore_index=True)
lineups = pd.read_csv(LINEUPS)
df = opp.merge(lineups[["bat_team", "batter"]], on=["bat_team", "batter"])
df["bucket"] = df["pitch_type"].map(BUCKET)
df["is_pa"] = df["events"].notna() & (df["events"] != "truncated_pa")

# Reliever usage: 2nd half, relief only
usage = {}
for name, (f, hand, _) in RELIEVERS.items():
    s = pd.read_csv(f"{f}_statcast_post_asb_2026.csv")
    assert s["p_throws"].iloc[0] == hand
    usage[name] = s["pitch_type"].map(BUCKET).value_counts(normalize=True).reindex(ORDER).fillna(0)
print("lineup pitches:", len(df), "| relievers:", list(usage))

# Table 1: pitch-mix fit only (lineup xwOBA by pitch type vs same-handed pitchers, weighted by 2nd-half usage)
rows = []
for team, g in df.groupby("bat_team"):
    for name, (_, hand, _) in RELIEVERS.items():
        gh = g[g["p_throws"] == hand]
        base, _ = xwoba(gh)
        w, used, _ = weighted(gh, usage[name])
        thin = any(usage[name][b] > 0 and (gh["bucket"] == b).sum() < MIN_LINEUP_PITCHES for b in ORDER)
        rows.append({"Opponent": TEAM_NAME[team], "Reliever": f"{name} ({hand}HP)", "hand": hand, "w": w, "base": base, "diff": w - base, "thin": thin})
t1 = pd.DataFrame(rows)
t1.to_csv("table1_mix_fit_2026.csv", index=False)
wide = t1.pivot(index="Reliever", columns="Opponent", values="w")[["Cubs", "Phillies", "Braves", "Diamondbacks"]]
diff = t1.pivot(index="Reliever", columns="Opponent", values="diff")[wide.columns]
best = wide.idxmin()
cells = wide.copy().astype(object)
for r in wide.index:
    for c in wide.columns:
        cells.loc[r, c] = f"{fx(wide.loc[r, c])} ({sgn(diff.loc[r, c])})" + (" ★" if best[c] == r else "")
print("TABLE 1: weighted xwOBA (diff vs lineup's own xwOBA vs that hand). Lower = better for SD.")
print(cells.loc[wide.mean(axis=1).sort_values().index].to_string())

# Table 2: heart of each lineup (top 4 xwOBA post-break) vs each reliever's mix, hitter's own splits vs same-handed pitchers
out = []
for team in TEAMS:
    lu = lineups[lineups["bat_team"] == team]
    hx = []
    for r in lu.itertuples():
        x, n = xwoba(df[df["batter"] == r.batter])
        hx.append((r.batter, r.Name, r.Bats, x, n))
    heart = sorted(hx, key=lambda t: -t[3])[:4]
    for batter, hname, bats, x, n in heart:
        h = df[df["batter"] == batter]
        scores = []
        for name, (_, hand, _) in RELIEVERS.items():
            hh = h[h["p_throws"] == hand]
            base, n_hand = xwoba(hh)
            w, used, small = weighted(hh, usage[name])
            scores.append((w, name, hand, base, n_hand, used, small))
        thin = sorted({s[2] for s in scores if s[4] < MIN_HAND_PA})
        scores = sorted([s for s in scores if not pd.isna(s[0]) and s[4] >= MIN_HAND_PA])
        b1, b2, worst = scores[0], scores[1], scores[-1]
        out.append({"Team": TEAM_NAME[team], "Hitter": hname, "Bats": bats, "xwOBA": x, "PA": n,
                    "Best": b1[1], "Best score": b1[0], "Best small-cell share": b1[6],
                    "Second": b2[1], "Second score": b2[0], "Worst": worst[1], "Worst score": worst[0],
                    "Hands skipped (<20 PA)": ", ".join(f"{hd}HP" for hd in thin)})
t2 = pd.DataFrame(out)
t2.to_csv("table2_heart_of_lineup_2026.csv", index=False)
print(t2.assign(**{c: t2[c].map(fx) for c in ["xwOBA", "Best score", "Second score", "Worst score"]}).to_string(index=False))
