"""Mason Miller's four-seamer, 2024-2026, vs 2026 league four-seamers (all, and 99+ mph).

League pitches come from pybaseball's statcast() with its cache on (2026-03-25 to 2026-09-24, about 700,000 pitches).
Miller's own seasons are the saved mason_miller_statcast_{year}.csv files.
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
MILLER = 695243
M = ["velo", "IVB", "HB arm", "spin", "ext", "rel ht", "arm ang", "VAA"]
LEAGUE_COLS = ["game_date", "game_type", "pitcher", "player_name", "p_throws", "pitch_type", "release_speed", "pfx_x", "pfx_z", "release_spin_rate",
               "release_extension", "release_pos_z", "release_pos_x", "arm_angle", "vx0", "vy0", "vz0", "ax", "ay", "az", "plate_z"]


def miller_seasons(refresh=False):
    out = {}
    for y in [2024, 2025, 2026]:
        path = D / f"mason_miller_statcast_{y}.csv"
        if not path.exists() or refresh:
            pb.statcast_pitcher(f"{y}-03-01", f"{y}-11-30", MILLER).query("game_type == 'R'").to_csv(path, index=False)
        out[y] = pd.read_csv(path)
    return out


def league_ff():
    d = pb.statcast("2026-03-25", "2026-09-24", verbose=False)
    return d[(d.pitch_type == "FF") & (d.game_type == "R")][LEAGUE_COLS]


def prep(d):
    d = d[(d.pitch_type == "FF") & (d.game_type == "R")].copy()
    d["velo"] = d.release_speed
    d["IVB"] = d.pfx_z * 12                                               # induced vertical break, inches
    d["HB arm"] = np.where(d.p_throws == "R", -1, 1) * d.pfx_x * 12       # horizontal break toward the arm side, inches
    d["spin"] = d.release_spin_rate
    d["ext"] = d.release_extension
    d["rel ht"] = d.release_pos_z
    d["arm ang"] = d.arm_angle
    # vertical approach angle at the front of the plate (degrees; closer to 0 = flatter)
    vyf = -np.sqrt(d.vy0 ** 2 - 2 * d.ay * (50 - 17 / 12))
    vzf = d.vz0 + d.az * (vyf - d.vy0) / d.ay
    d["VAA"] = -np.degrees(np.arctan(vzf / vyf))
    return d


def profile():
    """Year-by-year profile table, league comparison, and Miller's 2026 percentile among pitchers with 200+ four-seamers."""
    lg = prep(league_ff()).dropna(subset=["velo", "IVB", "VAA"])
    mil = {y: prep(d) for y, d in miller_seasons().items()}
    assert (lg.pitcher == MILLER).sum() == len(mil[2026]), "league pull and Miller's file disagree on his 2026 four-seamer count"
    # VAA depends on how high the pitch crosses the plate: compare to the league VAA at the same plate height
    vaa_fit = np.polyfit(lg.plate_z, lg.VAA, 1)
    # lower slots naturally produce less ride: compare IVB to the league IVB at the same arm angle (pitchers with 200+ FF)
    pit = lg.groupby("pitcher").agg(n=("velo", "size"), **{m: (m, "mean") for m in M})
    pit = pit[pit.n >= 200]
    ivb_fit = np.polyfit(pit["arm ang"], pit["IVB"], 1)
    for d in list(mil.values()) + [lg]:
        d["VAA vs exp"] = d.VAA - np.polyval(vaa_fit, d.plate_z)
        d["IVB vs slot"] = d.IVB - np.polyval(ivb_fit, d["arm ang"])
    cols = M + ["VAA vs exp", "IVB vs slot"]
    fast = lg[lg.velo >= 99]
    groups = {**{f"Miller {y}": mil[y] for y in mil}, "MLB FF 2026": lg, "MLB FF 99+ mph": fast}
    t = pd.DataFrame({k: {"pitches": len(v), **{m: v[m].mean() for m in cols}, "plate_z": v.plate_z.mean(), "max velo": v.velo.max()} for k, v in groups.items()}).T
    t.round(3).to_csv(D / "miller_fastball_profile_2024_2026.csv")

    pit = lg.groupby("pitcher").agg(n=("velo", "size"), **{m: (m, "mean") for m in cols})
    pit = pit[pit.n >= 200]
    g = pit.loc[MILLER]
    pct = pd.DataFrame({"Miller 2026": {m: g[m] for m in cols}, "percentile": {m: round((pit[m] < g[m]).mean() * 100) for m in cols}})
    pct.round(2).to_csv(D / "miller_fastball_percentiles_2026.csv")
    print(f"   {len(lg):,} league four-seamers ({lg.pitcher.nunique()} pitchers), {len(fast):,} at 99+ mph; percentiles among {len(pit)} pitchers with 200+ FF")
    print(f"   fits: VAA = {vaa_fit[0]:.2f} x plate_z + {vaa_fit[1]:.2f} | IVB = {ivb_fit[0]:.3f} x arm angle + {ivb_fit[1]:.2f}")
    print("   -> miller_fastball_profile_2024_2026.csv, miller_fastball_percentiles_2026.csv")
    return t, pct
