"""Padres Wild Card Game 1 vs Matthew Boyd: the lineup vs LHP in 2026, career vs Boyd, and Boyd's 2026 splits and pitch mix vs RHH.

All data is Statcast via pybaseball with its cache on.
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pybaseball as pb
from pybaseball import cache

warnings.filterwarnings("ignore")
cache.enable()
D = Path(__file__).resolve().parent

SEASON = ("2026-03-25", "2026-09-27")  # official 2026 regular season (MLB Stats API)
BOYD = 571510                           # Matthew Boyd, MLBAM id
# Game 1 lineup in batting order: MLBAM id -> (name, bats)
LINEUP = {665487: ("Fernando Tatis Jr.", "R"), 669392: ("Samad Taylor", "R"), 592518: ("Manny Machado", "R"), 664034: ("Ty France", "R"),
          701538: ("Jackson Merrill", "L"), 669720: ("Austin Hays", "R"), 593428: ("Xander Bogaerts", "R"), 630105: ("Jake Cronenworth", "L"),
          669134: ("Luis Campusano", "R")}
HIT = {"single": 1, "double": 2, "triple": 3, "home_run": 4}
K = {"strikeout", "strikeout_double_play"}
BB = {"walk", "intent_walk"}
NON_AB = BB | {"hit_by_pitch", "sac_fly", "sac_bunt", "sac_fly_double_play", "sac_bunt_double_play", "catcher_interf"}
# Savant definitions: foul tips are whiffs, bunt attempts are swings
SWING = {"swinging_strike", "swinging_strike_blocked", "foul", "foul_tip", "hit_into_play", "foul_bunt", "missed_bunt", "bunt_foul_tip"}
WHIFF = {"swinging_strike", "swinging_strike_blocked", "foul_tip", "missed_bunt", "bunt_foul_tip"}
POST = {"F", "D", "L", "W"}


# ---------------------------------------------------------------- data
def season_pitches():
    """Every 2026 regular-season pitch (about 717,000)."""
    d = pb.statcast("2026-03-25", "2026-09-28", verbose=False)
    d = d[d.game_type == "R"]
    print(f"2026 regular season: {len(d):,} pitches, {d.game_date.min().date()} to {d.game_date.max().date()} (official: {SEASON[0]} to {SEASON[1]})")
    return d


def boyd_pitches():
    """Every Statcast pitch Boyd has thrown since 2015, labeled regular / postseason (spring training dropped)."""
    b = pb.statcast_pitcher("2015-03-01", "2026-09-28", BOYD)
    b["phase"] = np.where(b.game_type == "R", "regular", np.where(b.game_type.isin(POST), "postseason", "spring"))
    print(f"Boyd: {len(b):,} Statcast pitches, {b.game_date.min()} to {b.game_date.max()} | {b.phase.value_counts().to_dict()} (spring training dropped)")
    b = b[b.phase != "spring"]
    b[b.batter.isin(LINEUP)].to_csv(D / "boyd_vs_lineup_pitches_2015_2026.csv", index=False)
    b[(pd.to_datetime(b.game_date).dt.year == 2026) & (b.phase == "regular")].to_csv(D / "boyd_statcast_2026.csv", index=False)
    return b


# ---------------------------------------------------------------- helpers
def pa_rows(d):
    """One row per completed plate appearance (the pitch that ended it)."""
    return d[d.events.notna() & (d.events != "") & (d.events != "truncated_pa")]


def xwoba(p):
    num = np.where(p.estimated_woba_using_speedangle.notna() & (p.type == "X"), p.estimated_woba_using_speedangle, p.woba_value.fillna(0))
    den = p.woba_denom.fillna(0).sum()
    return num.sum() / den if den else np.nan


def line(p):
    ev = p.events
    pa, ab = len(p), int((~ev.isin(NON_AB)).sum())
    h, tb = int(ev.isin(HIT).sum()), ev.map(HIT).fillna(0).sum()
    bb, hbp, sf = int(ev.isin(BB).sum()), int((ev == "hit_by_pitch").sum()), int(ev.isin({"sac_fly", "sac_fly_double_play"}).sum())
    return {"PA": pa, "AB": ab, "H": h, "2B": int((ev == "double").sum()), "HR": int((ev == "home_run").sum()), "BB": bb, "K": int(ev.isin(K).sum()),
            "AVG": h / ab if ab else np.nan, "OBP": (h + bb + hbp) / (ab + bb + hbp + sf) if (ab + bb + hbp + sf) else np.nan,
            "SLG": tb / ab if ab else np.nan, "xwOBA": xwoba(p), "K%": ev.isin(K).mean() * 100 if pa else np.nan,
            "BB%": ev.isin(BB).mean() * 100 if pa else np.nan}


# ---------------------------------------------------------------- tables
def lineup_vs_lhp(season):
    """Each hitter's 2026 regular season vs left-handed pitchers, in lineup order, plus the MLB average vs LHP."""
    vs_l = pa_rows(season[season.p_throws == "L"])
    rows = [{"order": i, "hitter": nm, "bats": bats, **line(vs_l[vs_l.batter == bid])} for i, (bid, (nm, bats)) in enumerate(LINEUP.items(), 1)]
    t = pd.DataFrame(rows)
    t["small sample"] = np.where(t.PA < 60, "yes (under 60 PA)", "")
    mlb = line(vs_l)
    t = pd.concat([t, pd.DataFrame([{"order": None, "hitter": "MLB, all hitters vs LHP", "bats": "", **mlb, "small sample": ""}])], ignore_index=True)
    t.to_csv(D / "lineup_vs_lhp_2026.csv", index=False)
    print(f"   MLB average vs LHP, 2026: {mlb['PA']:,} PA, xwOBA {mlb['xwOBA']:.3f} -> lineup_vs_lhp_2026.csv")
    return t


def career_vs_boyd(b):
    pa = pa_rows(b)
    rows = []
    for bid, (nm, bats) in LINEUP.items():
        q = pa[pa.batter == bid]
        L = line(q)
        rows.append({"hitter": nm, "bats": bats, **{k: L[k] for k in ["PA", "H", "2B", "HR", "BB", "K", "AB", "AVG", "SLG", "xwOBA"]},
                     "regular PA": int((q.phase == "regular").sum()), "postseason PA": int((q.phase == "postseason").sum()),
                     "tiny sample": "yes (under 10 PA)" if L["PA"] < 10 else ""})
    t = pd.DataFrame(rows).sort_values(["PA", "xwOBA"], ascending=False)
    t.to_csv(D / "career_vs_boyd_2015_2026.csv", index=False)
    print("   -> career_vs_boyd_2015_2026.csv")
    return t


def boyd_2026(b):
    b26 = b[(pd.to_datetime(b.game_date).dt.year == 2026) & (b.phase == "regular")]
    print(f"   Boyd 2026 regular season: {len(b26):,} pitches in {b26.game_pk.nunique()} games, {b26.game_date.min()} to {b26.game_date.max()}")
    splits = []
    for side in ["R", "L"]:
        L = line(pa_rows(b26[b26.stand == side]))
        splits.append({"vs": f"{side}HH", **{k: L[k] for k in ["PA", "xwOBA", "K%", "BB%", "HR", "AVG", "OBP", "SLG"]}})
    splits = pd.DataFrame(splits)
    splits.to_csv(D / "boyd_splits_2026.csv", index=False)
    r = b26[b26.stand == "R"]
    mix = []
    for pt, g in r.groupby("pitch_type"):
        sw, wh, pe = g.description.isin(SWING), g.description.isin(WHIFF), pa_rows(g)
        mix.append({"pitch": pt, "name": g.pitch_name.mode().iat[0], "pitches": len(g), "usage%": len(g) / len(r) * 100, "velo": g.release_speed.mean(),
                    "swings": int(sw.sum()), "whiff%": wh.sum() / sw.sum() * 100 if sw.sum() else np.nan, "PA ended": len(pe), "xwOBA": xwoba(pe)})
    mix = pd.DataFrame(mix).sort_values("pitches", ascending=False)
    mix.to_csv(D / "boyd_mix_vs_rhh_2026.csv", index=False)
    print("   -> boyd_splits_2026.csv, boyd_mix_vs_rhh_2026.csv")
    return splits, mix
