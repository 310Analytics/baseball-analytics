"""Rank tables for Jack Gurevitch.

check_claims(): recomputes every number printed on the charts and in the post from the source files -> rank_check_2026.csv
top10_scan():   every stat where he ranks top 10 in each comparison group -> top10_ranks_2026.csv
"""
from pathlib import Path

import pandas as pd

D = Path(__file__).resolve().parent
GID, GAM = "sa3032859", 813668  # FanGraphs PlayerId, MLBAM id

FB, BR, OS = {"FF", "SI", "FC"}, {"SL", "ST", "CU", "KC", "SV"}, {"CH", "FS"}
f3 = lambda v: f"{v:.3f}".lstrip("0")
p1 = lambda v: f"{v:.1%}"
p0 = lambda v: f"{v:.0%}"
of = lambda r, n: f"{r} of {n}"


def fg(pre):
    """Every column of the FanGraphs standard, advanced and batted ball exports for one league, merged on PlayerId."""
    r = lambda k: pd.read_csv(D / f"{pre}_{k}_2026.csv", encoding="utf-8-sig")
    s, a, b = r("standard"), r("advanced"), r("batted_ball")
    ids = ["Name", "Team", "Level", "Age", "PA", "MinorMasterId", "NameASCII", "MLBAMID", "PlayerTeamId"]
    d = s.merge(a.drop(columns=ids + ["AVG"]), on="PlayerId").merge(b.drop(columns=ids + ["BABIP"]), on="PlayerId")
    assert len(d) == len(s) == len(a) == len(b) and d.PlayerId.is_unique
    d["HR/PA"] = d.HR / d.PA
    return d


def sources():
    return {
        "mwl": fg("high_a"), "tl": fg("aa"),
        "tj": pd.read_csv(D / "tjstats_batter_batted_ball_2026.csv"),
        "tjs": pd.read_csv(D / "gurevitch_tjstats_standard_2026.csv"),
        "tjb": pd.read_csv(D / "gurevitch_tjstats_batted_ball_2026.csv"),
        "tjp": pd.read_csv(D / "gurevitch_tjstats_plate_discipline_2026.csv"),
        "tjc": pd.read_csv(D / "gurevitch_tjstats_statcast_2026.csv"),
        "pit": pd.read_csv(D / "gurevitch_pitches_2026_statsapi.csv"),
    }


def check_claims():
    S = sources()
    mwl, tl, tj, tjs, tjb, tjp, tjc, pit = (S[k] for k in ["mwl", "tl", "tj", "tjs", "tjb", "tjp", "tjc", "pit"])
    tj75 = tj[tj.bip >= 75]
    me = lambda d, key="PlayerId", v=GID: d[d[key] == v].iloc[0]
    hi = lambda d, c, v: int((d[c] > v).sum() + 1)
    lo = lambda d, c, v: int((d[c] < v).sum() + 1)
    pctile = lambda d, c: d[c].rank(pct=True, method="average")[d.PlayerId == GID].iloc[0] * 100
    gm, gt, gj = me(mwl), me(tl), me(tj75, "player_id", GAM)
    tot, lowa_sc = tjs[tjs.Lvl == "Minors"].iloc[0], tjc[tjc.Lvl == "A"].iloc[0]
    b = pit[(pit.level == "Low-A") & (pit.is_in_play == True) & pit.launch_speed.notna()]

    GM, GT, GJ = "Midwest League, 130+ PA", "Texas League, 130+ PA", "All Double-A leagues, 75+ BBE"
    SM, ST = "FanGraphs high_a_*", "FanGraphs aa_*"
    rows = []

    def claim(where, text, shown, actual, src, group):
        rows.append({"where": where, "claim": text, "shown": str(shown), "recomputed": str(actual), "source": src, "group": group,
                     "match": "yes" if str(shown) == str(actual) else "NO"})

    # ---- charts
    c = "projection chart"
    claim(c, "Midwest League hitters", 178, len(mwl), SM, GM)
    claim(c, "Midwest League minimum PA", 130, mwl.PA.min(), SM, GM)
    claim(c, "Midwest League HR / PA / ISO", "17/273/.264", f"{gm.HR}/{gm.PA}/{f3(gm.ISO)}", SM, GM)
    claim(c, "Midwest League HR rate rank", "6 of 178", of(hi(mwl, "HR/PA", gm["HR/PA"]), len(mwl)), SM, GM)
    claim(c, "Midwest League ISO rank", "12 of 178", of(hi(mwl, "ISO", gm.ISO), len(mwl)), SM, GM)
    claim(c, "Midwest League medians HR/PA, ISO", "2.5%/.158", f"{p1(mwl['HR/PA'].median())}/{f3(mwl.ISO.median())}", SM, GM)
    claim(c, "Texas League hitters", 154, len(tl), ST, GT)
    claim(c, "Texas League minimum PA", 130, tl.PA.min(), ST, GT)
    claim(c, "Texas League HR / PA / ISO", "9/141/.242", f"{gt.HR}/{gt.PA}/{f3(gt.ISO)}", ST, GT)
    claim(c, "Texas League HR rate rank", "8 of 154", of(hi(tl, "HR/PA", gt["HR/PA"]), len(tl)), ST, GT)
    claim(c, "Texas League ISO rank", "21 of 154", of(hi(tl, "ISO", gt.ISO), len(tl)), ST, GT)
    claim(c, "Texas League medians HR/PA, ISO", "2.9%/.160", f"{p1(tl['HR/PA'].median())}/{f3(tl.ISO.median())}", ST, GT)
    claim(c, "Age 22 in both leagues", "22/22", f"{gm.Age}/{gt.Age}", "FanGraphs *_standard Age", "him")
    claim(c, "Cardinals", "STL", gm.Team, "FanGraphs Team (1B: MLB Stats API /people/813668, not in project files)", "him")

    c = "age_power chart"
    claim(c, "Texas League ISO rank", "21 of 154", of(hi(tl, "ISO", gt.ISO), len(tl)), ST, GT)
    claim(c, "Share of Texas League hitters older", "77%", p0((tl.Age > gt.Age).mean()), "FanGraphs aa_standard Age", GT)
    claim(c, "Texas League median age, ISO", "24/.16", f"{tl.Age.median():.0f}/{f'{tl.ISO.median():.2f}'.lstrip('0')}", ST, GT)

    c = "batted_ball chart"
    claim(c, "Texas League HR/FB and rank", "47.4%, 1 of 154", f"{p1(gt['HR/FB'])}, {of(hi(tl, 'HR/FB', gt['HR/FB']), len(tl))}", "FanGraphs aa_batted_ball", GT)
    claim(c, "Texas League LD% and rank", "28.6%, 15 of 154", f"{p1(gt['LD%'])}, {of(hi(tl, 'LD%', gt['LD%']), len(tl))}", "FanGraphs aa_batted_ball", GT)
    claim(c, "Texas League medians HR/FB, LD%", "14%/24%", f"{p0(tl['HR/FB'].median())}/{p0(tl['LD%'].median())}", "FanGraphs aa_batted_ball", GT)

    c = "power_profile chart"
    for lab, col, sv, sp, fmt in [("SLG", "SLG", ".566", 97, f3), ("HR rate", "HR/PA", "6.2%", 97, p1), ("HR/FB", "HR/FB", "33.3%", 98, p1),
                                  ("ISO", "ISO", ".264", 94, f3), ("OPS", "OPS", ".941", 93, f3), ("AVG", "AVG", ".302", 93, f3),
                                  ("wRC+", "wRC+", "135", 89, lambda v: f"{v:.0f}")]:
        claim(c, f"{lab} value / percentile", f"{sv} / {sp}", f"{fmt(gm[col])} / {pctile(mwl, col):.0f}", SM + " (pct rank, ties averaged)", GM)

    c = "line_drives chart"
    claim(c, "Hitters with 75+ BBE", 479, len(tj75), "tjstats_batter_batted_ball", GJ)
    claim(c, "Teams in file (TL 10 + SL 8 + EL 12)", 30, len({t for s in tj.player_team for t in s.split("/")}), "tjstats_batter_batted_ball", "file coverage")
    claim(c, "Batted balls", 78, gj.bip, "tjstats_batter_batted_ball", GJ)
    claim(c, "Pop-up rate and rank (fewest)", "1.3%, 11 of 479", f"{p1(gj.pop_up_percent)}, {of(lo(tj75, 'pop_up_percent', gj.pop_up_percent), len(tj75))}", "tjstats_batter_batted_ball", GJ)
    claim(c, "LD rate and rank", "28.2%, 50 of 479", f"{p1(gj.line_drive_percent)}, {of(hi(tj75, 'line_drive_percent', gj.line_drive_percent), len(tj75))}", "tjstats_batter_batted_ball", GJ)
    claim(c, "Medians pop-up, LD", "7%/24%", f"{p0(tj75.pop_up_percent.median())}/{p0(tj75.line_drive_percent.median())}", "tjstats_batter_batted_ball", GJ)

    c = "exit_velo chart"
    for lab, m, sv in [("FB 93+", b.pitch_type.isin(FB) & (b.start_speed >= 93), "98.7 (13)"), ("FB under 93", b.pitch_type.isin(FB) & (b.start_speed < 93), "95.2 (26)"),
                       ("Breaking", b.pitch_type.isin(BR), "93.0 (17)"), ("Offspeed", b.pitch_type.isin(OS), "92.3 (9)")]:
        claim(c, f"Avg EV {lab} (BBE)", sv, f"{b[m].launch_speed.mean():.1f} ({int(m.sum())})", "gurevitch_pitches_2026_statsapi", "his Florida State League batted balls")
    claim(c, "Batted balls with EV", 65, len(b), "gurevitch_pitches_2026_statsapi", "his Florida State League batted balls")

    # ---- post
    c = "post"
    claim(c, "Age 22", 22, tot.Age, "gurevitch_tjstats_standard (Minors row)", "him")
    claim(c, "Three levels", 3, pit[pit.game_type == "R"].level.nunique(), "gurevitch_pitches_2026_statsapi", "him, regular season")
    claim(c, "32 HR, 96 RBI, 119 G", "32/96/119", f"{tot.HR}/{tot.RBI}/{tot.G}", "gurevitch_tjstats_standard (Minors row)", "him, regular season")
    claim(c, ".283/.360/.542", ".283/.360/.542", f"{f3(tot.AVG)}/{f3(tot.OBP)}/{f3(tot.SLG)}", "gurevitch_tjstats_standard (Minors row)", "him, regular season")
    a_plus = tjs[tjs.Lvl == "A+"].iloc[0]
    claim(c, "Peoria .302, 17 HR, 59 G", ".302/17/59", f"{f3(a_plus.AVG)}/{a_plus.HR}/{a_plus.G}", "gurevitch_tjstats_standard (A+ row)", "him")
    claim(c, "6th in HR rate of 178 Midwest League hitters", "6 of 178", of(hi(mwl, "HR/PA", gm["HR/PA"]), len(mwl)), SM, GM)
    claim(c, "12th in ISO", "12 of 178", of(hi(mwl, "ISO", gm.ISO), len(mwl)), SM, GM)
    claim(c, "9 HR in 141 PA at Springfield", "9/141", f"{gt.HR}/{gt.PA}", "FanGraphs aa_standard", GT)
    claim(c, "8th in HR rate of 154 Texas League hitters", "8 of 154", of(hi(tl, "HR/PA", gt["HR/PA"]), len(tl)), ST, GT)
    claim(c, "Younger than 77% of the league", "77%", p0((tl.Age > gt.Age).mean()), "FanGraphs aa_standard Age", GT)
    claim(c, "47.4% HR/FB led the Texas League", "47.4%, 1 of 154", f"{p1(gt['HR/FB'])}, {of(hi(tl, 'HR/FB', gt['HR/FB']), len(tl))}", "FanGraphs aa_batted_ball", GT)
    ties = int((mwl["HR/FB"] == gm["HR/FB"]).sum() - 1)
    claim(c, "4th in the Midwest League at 33.3% HR/FB", "33.3%, 4 of 178", f"{p1(gm['HR/FB'])}, {of(hi(mwl, 'HR/FB', gm['HR/FB']), len(mwl))}" + (f" (tied w/ {ties})" if ties else ""),
          "FanGraphs high_a_batted_ball", GM)
    claim(c, "Pop-up 1.3%, 11th lowest of 479", "1.3%, 11 of 479", f"{p1(gj.pop_up_percent)}, {of(lo(tj75, 'pop_up_percent', gj.pop_up_percent), len(tj75))}", "tjstats_batter_batted_ball", GJ)
    claim(c, "Line drives 28.2%", "28.2%", p1(gj.line_drive_percent), "tjstats_batter_batted_ball", GJ)
    claim(c, "Low-A is the only level with Statcast", "A", ",".join(tjc[tjc["Avg EV"] != "—"].query("Season == 2026").Lvl), "gurevitch_tjstats_statcast", "him")
    claim(c, "94.9 mph avg EV, 115 max (TJStats)", "94.9/115.0", f"{lowa_sc['Avg EV']}/{lowa_sc['Max EV']}", "gurevitch_tjstats_statcast (A row)", "his Florida State League batted balls")
    claim(c, "94.9 mph avg EV, 115 max (Stats API)", "94.9/115.0", f"{b.launch_speed.mean():.1f}/{b.launch_speed.max():.1f}", "gurevitch_pitches_2026_statsapi", "his Florida State League batted balls")
    m93 = b.start_speed >= 93
    claim(c, "98.7 avg EV vs 93+ (every pitch type)", "98.7", f"{b[m93].launch_speed.mean():.1f}", "gurevitch_pitches_2026_statsapi", f"his {int(m93.sum())} Florida State League BBE on 93+ pitches")

    # ---- cross-source consistency
    c = "cross-check"
    for lvl, row in [("A+", gm), ("AA", gt)]:
        t = tjs[tjs.Lvl == lvl].iloc[0]
        claim(c, f"{lvl} PA/HR/H/BB/SO: TJStats vs FanGraphs", f"{t.PA}/{t.HR}/{t.H}/{t.BB}/{t.SO}", f"{row.PA}/{row.HR}/{row.H}/{row.BB}/{row.SO}", "TJStats vs FanGraphs", "him")
        claim(c, f"{lvl} AVG/SLG: TJStats vs FanGraphs", f"{t.AVG:.3f}/{t.SLG:.3f}", f"{row.AVG:.3f}/{row.SLG:.3f}", "TJStats vs FanGraphs", "him")
    claim(c, "AA BBE: TJ player table vs TJ league file", tjb[tjb.Lvl == "AA"].BBE.iloc[0], gj.bip, "TJStats", "him")
    for lvl, lv in [("AA", "Double-A"), ("A+", "High-A"), ("A", "Low-A")]:
        claim(c, f"{lvl} regular-season pitches: TJStats vs Stats API", tjp[tjp.Lvl == lvl].Pitches.iloc[0], len(pit[(pit.level == lv) & (pit.game_type == "R")]),
              "TJStats vs Stats API", "him, regular season")

    out = pd.DataFrame(rows)
    out.to_csv(D / "rank_check_2026.csv", index=False)
    print(f"{(out.match == 'yes').sum()} of {len(out)} match | mismatches: {(out.match == 'NO').sum()} -> rank_check_2026.csv")
    print("Not checkable from project files: 2026 MLB avg EV 88.0 mph (cached Baseball Savant Statcast); draft round, USD stats.")
    return out


# ---------------------------------------------------------------- top 10 scan
HI = ["H", "1B", "2B", "3B", "HR", "R", "RBI", "BB", "HBP", "SB", "AVG", "BB%", "BB/K", "OBP", "SLG", "OPS", "ISO", "Spd", "BABIP",
      "wSB", "wRC", "wRAA", "wOBA", "wRC+", "LD%", "HR/FB", "HR/PA"]
LO = ["K%", "IFFB%", "SwStr%"]  # SO, GDP, CS left out: a low count mostly means fewer PA
DESC = ["GB/FB", "GB%", "FB%", "Pull%", "Cent%", "Oppo%"]  # no better/worse: report whichever end he's on
COUNTING = {"H", "1B", "2B", "3B", "HR", "R", "RBI", "BB", "HBP", "SB", "wRC", "wRAA", "wSB"}
TJ_DIR = {"line_drive_percent": ("hi", "LD rate"), "pulled_air_percent": ("hi", "Pulled-air rate"), "pop_up_percent": ("lo", "Pop-up rate"),
          "ground_ball_percent": ("desc", "GB rate"), "fly_ball_percent": ("desc", "FB rate"), "pull_percent": ("desc", "Pull rate"),
          "straight_percent": ("desc", "Straight-away rate"), "oppo_percent": ("desc", "Oppo rate")}


def _rank(d, col, v, how):
    better = (d[col] > v) if how == "hi" else (d[col] < v)
    return int(better.sum() + 1), int((d[col] == v).sum() - 1)


def _scan(d, key, keyval, cols, group, mins, mincol, used_min, label=lambda c: c):
    out = []
    g = d[d[key] == keyval].iloc[0]
    base = d[d[mincol] >= used_min]
    for col, how in cols:
        for end in (["hi", "lo"] if how == "desc" else [how]):
            r, ties = _rank(base, col, g[col], end)
            if r > 10 or ties >= 5:  # a rank shared with 5+ hitters says nothing
                continue
            at = {m: _rank(d[d[mincol] >= m], col, g[col], end)[0] for m in mins if g[mincol] >= m}
            top_at = [m for m, rr in at.items() if rr <= 10]
            out.append({"group": group, "stat": label(col) + ("" if how != "desc" else (" (highest)" if end == "hi" else " (lowest)")),
                        "rank": r, "of": len(base), "tied_with": ties, "value": g[col],
                        "type": "descriptive" if how == "desc" else ("counting" if col in COUNTING else "rate"),
                        "minimum_check": "holds at every tested minimum" if len(top_at) == len(at) else f"top 10 only at min {top_at} (rank by min: {at})",
                        "tested_minimums": ",".join(map(str, at)), "his_sample": f"{g[mincol]} {mincol}"})
    return out


def top10_scan():
    S = sources()
    cols = [(c, "hi") for c in HI] + [(c, "lo") for c in LO] + [(c, "desc") for c in DESC]
    res = []
    # FanGraphs exports start at 130 PA; higher minimums are tested up to his own PA
    for d, lg, mins in [(S["mwl"], "Midwest League", [130, 150, 200, 250]), (S["tl"], "Texas League", [130, 141])]:
        res += _scan(d, "PlayerId", GID, cols, f"{lg}, 130+ PA", mins, "PA", 130)
        res += _scan(d[d.Age <= 22], "PlayerId", GID, cols, f"{lg}, age 22 or younger, 130+ PA", mins, "PA", 130)
    res += _scan(S["tj"], "player_id", GAM, [(c, h) for c, (h, _) in TJ_DIR.items()], "All Double-A leagues, 75+ BBE", [50, 60, 75, 78], "bip", 75,
                 label=lambda c: TJ_DIR[c][1])
    out = pd.DataFrame(res).sort_values(["rank", "group", "stat"]).reset_index(drop=True)
    out.to_csv(D / "top10_ranks_2026.csv", index=False)
    print(f"{len(out)} top-10 ranks -> top10_ranks_2026.csv")
    return out


if __name__ == "__main__":
    pd.set_option("display.width", 250, "display.max_colwidth", 70)
    print(check_claims().to_string(index=False))
    print(top10_scan().to_string(index=False))
