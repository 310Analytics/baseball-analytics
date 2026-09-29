"""FanGraphs ranks for Mason Miller and Adrián Morejón among every reliever season since 2016 (0 starts, 60+ IP)."""
from pathlib import Path

import pandas as pd

D = Path(__file__).resolve().parent
TABS = ["standard", "advanced", "statcast", "win_probability", "stuff_plus", "batted_ball"]
KEY = ["Season", "PlayerId"]
PLAYERS = {"Mason Miller": 695243, "Adrián Morejón": 670970}  # MLBAM ids
STATS = [("K%", "hi", "pct"), ("K-BB%", "hi", "pct"), ("xERA", "lo", "2"), ("FIP", "lo", "2"), ("xFIP", "lo", "2"), ("SIERA", "lo", "2"),
         ("WPA", "hi", "2"), ("gmLI", "hi", "2"), ("IP", "hi", "1"), ("HLD", "hi", "0"), ("Stuff+", "hi", "0"), ("Pitching+", "hi", "0")]
FMT = {"pct": lambda v: f"{v:.1%}", "2": lambda v: f"{v:.2f}", "1": lambda v: f"{v:.1f}", "0": lambda v: f"{v:.0f}"}


def merged():
    """The six FanGraphs tabs merged one-to-one on Season + PlayerId; shared columns (Name, Team, IP, ERA...) come from the first tab."""
    df = None
    for t in TABS:
        d = pd.read_csv(D / f"mlb_rp_{t}_2016_2026.csv", encoding="utf-8-sig")
        if df is None:
            df = d
        else:
            # the overlapping columns really are the same numbers in every tab
            for c in ["IP", "ERA"]:
                if c in d:
                    chk = d[KEY + [c]].merge(df[KEY + [c]], on=KEY, suffixes=("", "_first"))
                    assert (chk[c] - chk[f"{c}_first"]).abs().max() < 1e-9, (t, c)
            df = df.merge(d[KEY + [c for c in d.columns if c not in df.columns]], on=KEY, how="inner", validate="one_to_one")
    assert len(df) == 855 and (df.GS == 0).all() and (df.IP >= 60).all()
    return df


def _rank(pool, col, v, how):
    better = (pool[col] > v) if how == "hi" else (pool[col] < v)
    return int(better.sum() + 1), int((pool[col] == v).sum() - 1)


def fg_ranks():
    """2026 rank of each player on each stat, among all reliever seasons with a value (Stuff+ and Pitching+ start in 2021)."""
    df = merged()
    print(f"{len(df)} reliever seasons from {df.PlayerId.nunique()} relievers, {df.Season.min()}-{df.Season.max()} (no 2020)")
    rows = []
    for col, how, f in STATS:
        pool = df[df[col].notna()]
        for label, mlbam in PLAYERS.items():
            v = df[(df.MLBAMID == mlbam) & (df.Season == 2026)].iloc[0][col]
            r, ties = _rank(pool, col, v, how)
            rows.append({"pitcher": label, "stat": col, "better": "higher" if how == "hi" else "lower", "value": FMT[f](v),
                         "rank": r, "tied_with": ties, "of": len(pool), "pool": "2021-2026" if col in ("Stuff+", "Pitching+") else "2016-2026"})
    out = pd.DataFrame(rows)
    out.to_csv(D / "fg_ranks_2026.csv", index=False)
    print("-> fg_ranks_2026.csv")
    return out


def top5():
    df = merged()
    rows = []
    for col, how, f in [("K%", "hi", "pct"), ("xERA", "lo", "2"), ("FIP", "lo", "2"), ("Pitching+", "hi", "0"), ("Stuff+", "hi", "0")]:
        pool = df[df[col].notna()].sort_values(col, ascending=(how == "lo")).head(5)
        for i, (_, r) in enumerate(pool.iterrows(), 1):
            rows.append({"stat": col, "rank": i, "season": r.Season, "pitcher": r.Name, "team": r.Team, "value": FMT[f](r[col])})
    out = pd.DataFrame(rows)
    out.to_csv(D / "fg_top5_2016_2026.csv", index=False)
    print("-> fg_top5_2016_2026.csv")
    return out


def only_130_over_80():
    """Every reliever season since 2021 with 130+ Pitching+ and 80+ IP (checks the Morejón claim)."""
    df = merged()
    return df[(df["Pitching+"] >= 130) & (df.IP >= 80)][["Season", "Name", "IP", "Pitching+"]]


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print(fg_ranks().to_string(index=False)); print(top5().to_string(index=False)); print(only_130_over_80())
