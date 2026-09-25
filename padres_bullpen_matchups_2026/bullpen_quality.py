"""Padres bullpen matchups: Pitch quality and the quality-adjusted matchup table. Needs the post-break pulls from bullpen_matchup.py."""
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

# League xwOBA by pitch type and pitcher hand, full 2026 regular season (cached monthly pulls)
agg = []
for s, e in [("2026-03-01", "2026-03-31"), ("2026-04-01", "2026-04-30"), ("2026-05-01", "2026-05-31"), ("2026-06-01", "2026-06-30"),
             ("2026-07-01", "2026-07-31"), ("2026-08-01", "2026-08-31"), ("2026-09-01", END)]:
    raw = statcast(s, e, verbose=False)
    raw = raw[raw["game_type"] == "R"]
    raw = raw.assign(bucket=raw["pitch_type"].map(BUCKET), is_pa=raw["events"].notna() & (raw["events"] != "truncated_pa"))
    raw = raw[raw["is_pa"] & (raw["woba_denom"] > 0) & raw["bucket"].notna()]
    raw["xv"] = np.where(raw["type"].eq("X") & raw["estimated_woba_using_speedangle"].notna(), raw["estimated_woba_using_speedangle"], raw["woba_value"])
    agg.append(raw.groupby(["bucket", "p_throws"]).agg(xv=("xv", "sum"), n=("woba_denom", "sum")))
lg = pd.concat(agg).groupby(level=[0, 1]).sum()
LEAGUE = (lg["xv"] / lg["n"]).to_dict()            # (bucket, hand) -> league xwOBA
print(pd.Series(LEAGUE).unstack().reindex(ORDER).map(fx).to_string())

# Pitch quality: each reliever's full 2026 relief xwOBA by pitch, regressed 60 PA toward league for that pitch and hand
IDS = {name: pid for name, (_, _, pid) in RELIEVERS.items()}
IDS[MORGAN[0]] = MORGAN[2]
season, quality, pq_rows = {}, {}, []
for name, pid in IDS.items():
    d = statcast_pitcher("2026-03-01", END, pid)
    d = d[d["game_type"] == "R"]
    st = starts(d)
    d = d[~d["game_pk"].isin(st)].copy()
    d["bucket"] = d["pitch_type"].map(BUCKET)
    d["is_pa"] = d["events"].notna() & (d["events"] != "truncated_pa")
    if name == MORGAN[0]:
        RELIEVERS[name] = (MORGAN[1], d["p_throws"].iloc[0], pid)
        usage[name] = d["pitch_type"].map(BUCKET).value_counts(normalize=True).reindex(ORDER).fillna(0)   # full-season mix
    d.to_csv(f"{RELIEVERS[name][0]}_statcast_2026_relief.csv", index=False)
    season[name] = d
    hand = RELIEVERS[name][1]
    q = {}
    for b in ORDER:
        if usage[name][b] == 0:
            continue
        xs, n = xw_sums(d[d["bucket"] == b])
        reg = (xs + K_REG * LEAGUE[(b, hand)]) / (n + K_REG)          # (PA x his xwOBA + 60 x league) / (PA + 60)
        q[b] = reg
        pq_rows.append({"Reliever": name, "Pitch": b, "Usage": usage[name][b], "PA 2026": int(n), "Raw xwOBA": xs / n if n else np.nan,
                        "League": LEAGUE[(b, hand)], "Regressed": reg})
    quality[name] = q
    print(f"{name:10s} {hand}HP  2026 relief: {len(d)} pitches, {d.game_pk.nunique()} games (dropped {len(st)} starts)")
pq = pd.DataFrame(pq_rows)
pq.to_csv("pitch_quality_2026.csv", index=False)
q_only = {n: sum(usage[n][b] * v for b, v in quality[n].items()) / sum(usage[n][b] for b in quality[n]) for n in IDS}
print("Quality-only score:", {n: fx(v) for n, v in sorted(q_only.items(), key=lambda kv: kv[1])})

# Quality-adjusted matchup: per pitch, pitcher xwOBA x lineup xwOBA / league (same hand), weighted by usage,
# then blended with his 2026 head-to-head xwOBA vs the current lineup hitters at PA / (PA + 100)
rows = []
for team, g in df.groupby("bat_team"):
    hitters = set(lineups.loc[lineups["bat_team"] == team, "batter"])
    for name in IDS:
        hand = RELIEVERS[name][1]
        gh = g[g["p_throws"] == hand]
        base, _ = xwoba(gh)
        old, _, _ = weighted(gh, usage[name])
        num = den = 0.0; thin = False
        for b, pb in quality[name].items():
            sub = gh[gh["bucket"] == b]
            lb, _ = xwoba(sub)
            if len(sub) < MIN_LINEUP_PITCHES:
                thin = True
            if pd.isna(lb):
                continue
            num += usage[name][b] * pb * lb / LEAGUE[(b, hand)]
            den += usage[name][b]
        model = num / den
        xs, n_h2h = xw_sums(season[name][season[name]["batter"].isin(hitters)])
        w = n_h2h / (n_h2h + K_H2H)
        final = w * (xs / n_h2h) + (1 - w) * model if n_h2h else model
        rows.append({"Opponent": TEAM_NAME[team], "Reliever": f"{name} ({hand}HP)", "name": name, "hand": hand, "base": base,
                     "old": old, "model": model, "h2h_pa": int(n_h2h), "h2h_xwoba": xs / n_h2h if n_h2h else np.nan,
                     "w": final, "diff": final - base, "thin": thin})
new = pd.DataFrame(rows)
new.to_csv("matchup_quality_2026.csv", index=False)
print(new.pivot(index="Reliever", columns="Opponent", values="w")[["Cubs", "Phillies", "Braves", "Diamondbacks"]].map(fx).to_string())
