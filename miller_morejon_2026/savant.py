"""Baseball Savant data for Mason Miller and Adrián Morejón, 2026, plus xwOBA and whiff% for every reliever season since 2016.

Savant's 2026 leaderboards keep changing while the season is on, so each pull only runs when its CSV is missing
(pass refresh=True to pull again). Pitch-level pulls go through pybaseball with its cache on.
"""
import io
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import pybaseball as pb
from pybaseball import cache

warnings.filterwarnings("ignore")
cache.enable()
D = Path(__file__).resolve().parent
P = {695243: "Mason Miller", 670970: "Adrián Morejón"}
FILE = {695243: "mason_miller", 670970: "morejon"}
YEARS = [2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025, 2026]  # no 2020 in the 60+ IP reliever pool
# Savant definitions (match its arsenal leaderboard exactly): foul tips are whiffs, bunt attempts are swings
SWING = {"swinging_strike", "swinging_strike_blocked", "foul", "foul_tip", "hit_into_play", "foul_bunt", "missed_bunt", "bunt_foul_tip"}
WHIFF = {"swinging_strike", "swinging_strike_blocked", "foul_tip", "missed_bunt", "bunt_foul_tip"}
CUSTOM = "https://baseballsavant.mlb.com/leaderboard/custom?year={y}&type=pitcher&filter=&min=1&selections={sel}&chart=false&x=pa&y=pa&r=no&chartType=beeswarm&sort=xwoba&sortDir=asc&csv=true"


def _cached(name, pull, refresh=False):
    path = D / name
    if path.exists() and not refresh:
        return pd.read_csv(path)
    d = pull()
    d.to_csv(path, index=False)
    print(f"   pulled -> {name}")
    return d


def _custom(y, sel):
    r = requests.get(CUSTOM.format(y=y, sel=sel), timeout=60); r.raise_for_status()
    return pd.read_csv(io.StringIO(r.content.decode("utf-8-sig")))


# ---------------------------------------------------------------- pulls
def percentiles(refresh=False):
    return _cached("savant_percentiles_2026.csv", lambda: pb.statcast_pitcher_percentile_ranks(2026).query("player_id in @P"), refresh)


def raw_2026(refresh=False):
    sel = "p_formatted_ip,pa,xwoba,xera,k_percent,whiff_percent,oz_swing_percent,barrel_batted_rate,hard_hit_percent,fastball_avg_speed,xslg"
    return _cached("savant_raw_2026.csv", lambda: _custom(2026, sel).query("player_id in @P"), refresh)


def pitches(refresh=False):
    out = {}
    for pid in P:
        pull = lambda pid=pid: (pb.statcast_pitcher("2026-03-01", "2026-11-30", pid).query("game_type == 'R'")
                                .sort_values(["game_date", "at_bat_number", "pitch_number"]).reset_index(drop=True))
        out[pid] = _cached(f"{FILE[pid]}_statcast_2026.csv", pull, refresh)
    return out


def arsenal(pitch_results, refresh=False):
    def pull():
        ars = pb.statcast_pitcher_arsenal_stats(2026, minPA=1).query("player_id in @P").copy()
        for t in ["avg_speed", "avg_spin"]:
            w = pb.statcast_pitcher_pitch_arsenal(2026, minP=1, arsenal_type=t).query("pitcher in @P")
            w = w.melt(id_vars=["pitcher"], value_vars=[c for c in w.columns if c.endswith(t.replace("avg_", "_avg_"))], var_name="c", value_name=t)
            w["pitch_type"] = w.c.str.split("_").str[0].str.upper()
            ars = ars.merge(w[["pitcher", "pitch_type", t]].rename(columns={"pitcher": "player_id"}), on=["player_id", "pitch_type"], how="left")
        mov = pitch_results[pitch_results.pitch != "All"][["pitcher", "pitch", "IVB in", "HB in"]].rename(columns={"pitch": "pitch_type"})
        mov["player_id"] = mov.pitcher.map({v: k for k, v in P.items()})
        ars = ars.merge(mov.drop(columns="pitcher"), on=["player_id", "pitch_type"], how="left")
        ars.insert(0, "pitcher", ars.player_id.map(P))
        return ars
    return _cached("savant_arsenal_2026.csv", pull, refresh)


def expected_stats(refresh=False):
    return _cached("savant_expected_stats_2016_2026.csv", lambda: pd.concat([pb.statcast_pitcher_expected_stats(y, minPA=1).assign(year=y) for y in YEARS]), refresh)


def custom_whiff(refresh=False):
    def pull():
        wf = pd.concat([_custom(y, "pa,whiff_percent,swing_percent,xwoba").assign(year=y) for y in YEARS])
        print(f"   custom leaderboard: dropping {wf.duplicated().sum()} exact duplicate rows (Pat Venditte, switch-pitcher, listed twice)")
        return wf.drop_duplicates()
    return _cached("savant_custom_whiff_2016_2026.csv", pull, refresh)


# ---------------------------------------------------------------- tables
def pitch_results(pitch_data):
    """By pitch, 2026 regular season: usage, velo, spin, movement, whiff%, chase%, CSW%, hard-hit%, barrel%, avg EV."""
    rows = []
    for pid, d in pitch_data.items():
        for pt, g in [(pt, g) for pt, g in d.groupby("pitch_type")] + [("All", d)]:
            sw, wh = g.description.isin(SWING), g.description.isin(WHIFF)
            oz = g.zone.isin([11, 12, 13, 14])
            bbe = g[(g.description == "hit_into_play") & g.launch_speed.notna()]
            rows.append({"pitcher": P[pid], "pitch": pt, "name": g.pitch_name.mode().iat[0] if pt != "All" else "All pitches", "pitches": len(g),
                         "usage%": len(g) / len(d) * 100, "velo": g.release_speed.mean(), "spin": g.release_spin_rate.mean(),
                         "IVB in": g.pfx_z.mean() * 12, "HB in": g.pfx_x.mean() * 12, "swings": int(sw.sum()),
                         "whiff%": wh.sum() / sw.sum() * 100 if sw.sum() else np.nan,
                         "chase%": (sw & oz).sum() / oz.sum() * 100 if oz.sum() else np.nan,
                         "CSW%": g.description.isin(WHIFF | {"called_strike"}).sum() / len(g) * 100,
                         "BBE": len(bbe), "hard hit%": (bbe.launch_speed >= 95).mean() * 100 if len(bbe) else np.nan,
                         "barrel%": (bbe.launch_speed_angle == 6).mean() * 100 if len(bbe) else np.nan, "avg EV": bbe.launch_speed.mean()})
    t = pd.DataFrame(rows)
    # each pitcher's pitches from most to least thrown, "All" last (pitcher order as given)
    t["_p"] = t.pitcher.map({nm: i for i, nm in enumerate(t.pitcher.unique())}); t["_all"] = t.pitch == "All"
    t = t.sort_values(["_p", "_all", "pitches"], ascending=[True, True, False]).drop(columns=["_p", "_all"])
    t.to_csv(D / "savant_pitch_results_2026.csv", index=False)
    return t


def history(ex, wf):
    """xwOBA (expected stats) and whiff% (custom leaderboard) for all 855 reliever seasons, matched on MLBAMID + season."""
    pool = pd.read_csv(D / "mlb_rp_standard_2016_2026.csv", encoding="utf-8-sig")[["Season", "Name", "Team", "IP", "PlayerId", "MLBAMID"]]
    for n, t in [("expected", ex), ("custom", wf)]:
        assert not t.duplicated(["player_id", "year"]).any(), n
    h = pool.merge(ex[["player_id", "year", "pa", "est_woba"]].rename(columns={"player_id": "MLBAMID", "year": "Season", "pa": "PA_savant", "est_woba": "xwOBA"}),
                   on=["MLBAMID", "Season"], how="left", validate="one_to_one")
    h = h.merge(wf[["player_id", "year", "whiff_percent", "xwoba"]].rename(columns={"player_id": "MLBAMID", "year": "Season", "whiff_percent": "whiff%", "xwoba": "xwOBA_custom"}),
                on=["MLBAMID", "Season"], how="left", validate="one_to_one")
    assert h.xwOBA.notna().all() and h["whiff%"].notna().all(), "unmatched reliever seasons"
    assert (h.xwOBA - h.xwOBA_custom).abs().max() < 0.0005, "the two Savant xwOBA sources disagree"
    h = h.drop(columns="xwOBA_custom")
    h.to_csv(D / "mlb_rp_savant_history_2016_2026.csv", index=False)
    print(f"   matched all {len(h)} reliever seasons to Savant xwOBA and whiff% -> mlb_rp_savant_history_2016_2026.csv")
    return h


def history_ranks(h):
    """Every Miller / Morejón season in the pool, ranked on xwOBA (lower = better) and whiff% (higher = better)."""
    rows = []
    for pid, nm in P.items():
        for _, r in h[h.MLBAMID == pid].sort_values("Season").iterrows():
            row = {"pitcher": nm, "season": r.Season, "IP": r.IP}
            for col, lower in [("xwOBA", True), ("whiff%", False)]:
                s = h[col]
                row[col] = r[col]
                row[f"{col} rank"] = int(((s < r[col]) if lower else (s > r[col])).sum() + 1)
                row[f"{col} tied"] = int((s == r[col]).sum() - 1)
            rows.append(row)
    t = pd.DataFrame(rows)
    t.to_csv(D / "savant_history_ranks_2016_2026.csv", index=False)
    print("   -> savant_history_ranks_2016_2026.csv")
    return t
