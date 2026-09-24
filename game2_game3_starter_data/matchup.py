"""Padres Games 2-3: Statcast pulls, opponent lineups, splits, matchup table, league averages."""
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

for name, (pid, _) in STARTERS.items():
    s = statcast_pitcher(STARTER_START, STARTER_END, pid)
    s = s.sort_values(["game_date", "at_bat_number", "pitch_number"])
    s.to_csv(f"{name.lower()}_statcast_aug20_sep24_2026.csv", index=False)
    print(f"{name:8s} {len(s):4d} pitches, {s.game_date.nunique()} games, "
          f"{s.game_date.min()} to {s.game_date.max()}")

# One league-wide pull (cached), split two ways:
#   opp       = every pitch where CHC/PHI/ATL/AZ are batting, post All-Star break
#   league_sp = every pitch by the 159 MLB starters (10+ IP) since 8/20, for league-average lines
mlb_sp = pd.read_csv("mlb_sp_10ip_2026.csv", encoding="utf-8-sig")
SP_IDS = set(mlb_sp["MLBAMID"])
COLS = ["game_pk", "game_date", "game_type", "home_team", "away_team", "inning_topbot", "at_bat_number",
        "pitch_number", "batter", "stand", "pitcher", "p_throws", "pitch_type", "description", "events", "type",
        "estimated_woba_using_speedangle", "woba_value", "woba_denom", "n_thruorder_pitcher"]

opp_parts, sp_parts = [], []
for s, e in [("2026-07-01", "2026-07-31"), ("2026-08-01", "2026-08-31"), ("2026-09-01", STARTER_END)]:
    raw = statcast(s, e, verbose=False)
    raw = raw[raw["game_type"] == "R"]
    bat = raw["away_team"].where(raw["inning_topbot"] == "Top", raw["home_team"])
    raw = raw.assign(bat_team=bat)
    opp_parts.append(raw[bat.isin(TEAMS) & (raw["game_date"] >= ASB_START)][COLS + ["bat_team"]])
    sp_parts.append(raw[raw["pitcher"].isin(SP_IDS) & (raw["game_date"] >= STARTER_START)][COLS])

opp = pd.concat(opp_parts, ignore_index=True)
league_sp = pd.concat(sp_parts, ignore_index=True)
opp["is_pa"] = opp["events"].notna() & (opp["events"] != "truncated_pa")
league_sp["is_pa"] = league_sp["events"].notna() & (league_sp["events"] != "truncated_pa")
for team, g in opp.groupby("bat_team"):
    print(f"{TEAM_NAME[team]:12s} {g.game_pk.nunique()} games, {len(g)} pitches, {g.is_pa.sum()} PA")
print(f"MLB SP since 8/20: {league_sp.pitcher.nunique()} pitchers, {len(league_sp)} pitches")

# Lineup = top 9 by PA post-break, among hitters with 25+ PA in the team's last 15 games
pa = opp[opp["is_pa"]]
names = playerid_reverse_lookup(pa["batter"].unique().tolist(), key_type="mlbam")
names = names.assign(Name=names.name_first.str.title() + " " + names.name_last.str.title()).set_index("key_mlbam")["Name"]

parts = []
for team in TEAMS:
    g = pa[pa["bat_team"] == team]
    games = opp[opp["bat_team"] == team].drop_duplicates("game_pk").sort_values(["game_date", "game_pk"])
    recent = g[g["game_pk"].isin(games.tail(RECENT_GAMES)["game_pk"])].groupby("batter").size()
    agg = g.groupby("batter").agg(PA=("events", "size"),
                                  hands=("stand", lambda s: "".join(sorted(s.unique())))).sort_values("PA", ascending=False)
    agg["Bats"] = agg["hands"].map({"L": "L", "R": "R", "LR": "S"})
    agg["PA_last15"] = recent.reindex(agg.index).fillna(0).astype(int)
    top = agg[agg["PA_last15"] >= MIN_RECENT_PA].head(9)
    parts.append(top.assign(bat_team=team, Name=top.index.map(names)).reset_index())

lineups = pd.concat(parts, ignore_index=True)[["bat_team", "batter", "Name", "Bats", "PA", "PA_last15"]]
lineups.to_csv("opponent_lineups_post_asb_2026.csv", index=False)
for team in TEAMS:
    print(f"\n{TEAM_NAME[team]}")
    print(lineups[lineups.bat_team == team][["Name", "Bats", "PA", "PA_last15"]].to_string(index=False))

def xwoba(g):
    """Savant-style xwOBA: batted balls use estimated_woba_using_speedangle; K/BB/HBP use woba_value."""
    p = g[g["is_pa"] & (g["woba_denom"] > 0)]
    if p.empty:
        return np.nan, 0
    val = np.where(p["type"].eq("X") & p["estimated_woba_using_speedangle"].notna(),
                   p["estimated_woba_using_speedangle"], p["woba_value"])
    return val.sum() / p["woba_denom"].sum(), len(p)


def summary(g):
    x, n_pa = xwoba(g)
    p = g[g["is_pa"]]
    swings = g["description"].isin(SWING).sum()
    return pd.Series({
        "Pitches": len(g), "PA": len(p), "xwOBA": x,
        "K%": p["events"].isin(K_EVENTS).mean() if len(p) else np.nan,
        "Whiff%": g["description"].isin(WHIFF).sum() / swings if swings else np.nan,
        "xwOBA PA": n_pa,
    })


fx = lambda v: "—" if pd.isna(v) else f"{v:.3f}".lstrip("0")
fp = lambda v: "—" if pd.isna(v) else f"{v:.1%}"

# lineup hitters only
df = opp.merge(lineups[["bat_team", "batter"]], on=["bat_team", "batter"])
df["bucket"] = df["pitch_type"].map(BUCKET)

team_hand = {}
for team, g in df.groupby("bat_team"):
    th = g.groupby("p_throws").apply(summary).reindex(["L", "R"])
    team_hand[team] = th
    print(f"\n{TEAM_NAME[team]}: lineup vs LHP / RHP")
    print(pd.DataFrame({
        "Pitches": th["Pitches"].astype(int).values, "PA": th["PA"].astype(int).values,
        "xwOBA": th["xwOBA"].map(fx).values, "K%": th["K%"].map(fp).values, "Whiff%": th["Whiff%"].map(fp).values,
    }, index=["vs LHP", "vs RHP"]).to_string())

    print(f"\n{TEAM_NAME[team]}: xwOBA / Whiff% by pitch type (pitches, PA)")
    cells = {}
    for b in ORDER:
        row = []
        for sub in [g, g[g.p_throws == "R"], g[g.p_throws == "L"]]:
            s = summary(sub[sub.bucket == b])
            row.append(f"{fx(s['xwOBA'])} / {fp(s['Whiff%'])} ({int(s['Pitches'])}, {int(s['xwOBA PA'])} PA)")
        cells[b] = row
    print(pd.DataFrame(cells, index=["All", "vs RHP", "vs LHP"]).T.to_string())

for team, g in df.groupby("bat_team"):
    print(f"\n{TEAM_NAME[team]}: hitter xwOBA vs LHP / RHP")
    out = []
    for lu in lineups[lineups.bat_team == team].itertuples():
        h = g[g.batter == lu.batter]
        row = {"Hitter": lu.Name, "Bats": lu.Bats, "PA": lu.PA}
        for hand in ["L", "R"]:
            x, n = xwoba(h[h.p_throws == hand])
            row[f"vs {hand}HP"] = f"{fx(x)} ({n} PA)"
        out.append(row)
    print(pd.DataFrame(out).to_string(index=False))

# Matchup score = lineup xwOBA on each pitch type (same-handed pitchers only),
# weighted by the starter's usage of that pitch since 8/20. Lower = better for SD.
usage, rows = {}, []
for sp, (_, hand) in STARTERS.items():
    s = pd.read_csv(f"{sp.lower()}_statcast_aug20_sep24_2026.csv")
    u = s["pitch_type"].map(BUCKET).value_counts(normalize=True).reindex(ORDER).fillna(0)
    usage[f"{sp} ({hand}HP)"] = u
    for team, g in df.groupby("bat_team"):
        gh = g[g.p_throws == hand]
        wsum = wused = 0.0
        for b in ORDER:
            if u[b] == 0:
                continue
            x, _ = xwoba(gh[gh.bucket == b])
            if pd.isna(x):
                continue
            wsum += u[b] * x
            wused += u[b]
        weighted = wsum / wused
        base = team_hand[team].loc[hand, "xwOBA"]
        rows.append({"Starter": f"{sp} ({hand}HP)", "Opponent": TEAM_NAME[team],
                     "Weighted xwOBA": weighted, "Lineup xwOBA vs hand": base, "Diff": weighted - base})

print("Starter pitch usage since 8/20")
print(pd.DataFrame(usage).map(lambda v: f"{v:.1%}" if v else "—").to_string())

matchup = pd.DataFrame(rows)
matchup.to_csv("matchup_table_post_asb_2026.csv", index=False)
for team in ["Cubs", "Phillies", "Braves", "Diamondbacks"]:
    t = matchup[matchup.Opponent == team].sort_values("Weighted xwOBA")
    print(f"\nvs {team}")
    print(pd.DataFrame({"Starter": t["Starter"], "Weighted xwOBA": t["Weighted xwOBA"].map(fx),
                        "Lineup vs hand": t["Lineup xwOBA vs hand"].map(fx),
                        "Diff": t["Diff"].map(lambda v: f"{v:+.3f}")}).to_string(index=False))

# MLB SP average lines for the starter chart (same 159 starters as mlb_sp_10ip_2026.csv)
lpa = league_sp[league_sp["is_pa"]]
k = lpa["events"].isin(K_EVENTS).mean()
bb = lpa["events"].isin(["walk", "intent_walk"]).mean()
ip = mlb_sp["IP"].apply(lambda v: int(v) + round((v % 1) * 10) / 3)   # FanGraphs 29.2 IP = 29 2/3
league = pd.Series({
    "K-BB%": k - bb, "BB%": bb, "xERA": (mlb_sp["xERA"] * ip).sum() / ip.sum(),
    "Stuff+": 100, "Location+": 100, "P/BF": len(league_sp) / len(lpa),
    "xwOBA 2nd TTO": xwoba(lpa[lpa["n_thruorder_pitcher"] == 2])[0],
}, name="value")
league.rename_axis("metric").to_csv("mlb_sp_league_averages_2026.csv")
print(league.round(4).to_string())
