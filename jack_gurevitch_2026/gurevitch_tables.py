"""Pitch-level tables from the MLB Stats API pull (gurevitch_pitches_2026_statsapi.csv). Each table prints and saves as a CSV.

Only the Low-A (Florida State League) games have pitch tracking, so tables 1-3 are Low-A only. Tables 4-6 use PA results,
which exist at every level. A warning sign (⚠) marks cells with under 20 PA or pitches.
"""
from pathlib import Path

import numpy as np
import pandas as pd

D = Path(__file__).resolve().parent
GROUP = {"FF": "Fastball", "SI": "Fastball", "FC": "Fastball", "SL": "Breaking", "ST": "Breaking", "CU": "Breaking", "KC": "Breaking",
         "SV": "Breaking", "CH": "Offspeed", "FS": "Offspeed"}
SWING, WHIFF = {"S", "W", "F", "T", "D", "E", "X"}, {"S", "W"}  # Stats API call codes; foul tips (T) count as contact
HIT = {"single": 1, "double": 2, "triple": 3, "home_run": 4}
AB_EV = set(HIT) | {"field_out", "strikeout", "strikeout_double_play", "grounded_into_double_play", "field_error", "force_out", "double_play"}
LEVELS = ["Low-A", "High-A", "Double-A", "Combined"]

flagP = lambda n: f"{n} ⚠" if n < 20 else f"{n}"
f3 = lambda v: "—" if pd.isna(v) else (f"{v:.3f}".lstrip("0") if v < 1 else f"{v:.3f}")
pc = lambda v: "—" if pd.isna(v) else f"{v:.1%}"


def load():
    df = pd.read_csv(D / "gurevitch_pitches_2026_statsapi.csv").sort_values(["game_pk", "at_bat_index", "pitch_number"])
    df["group"] = df["pitch_type"].map(GROUP)
    df["swing"], df["whiff"] = df["call"].isin(SWING), df["call"].isin(WHIFF)
    # count before each pitch = count after the previous pitch in the same PA (0-0 on the first)
    g = df.groupby(["game_pk", "at_bat_index"])
    df["pre_b"] = g["balls"].shift(1).fillna(0).astype(int)
    df["pre_s"] = g["strikes"].shift(1).fillna(0).astype(int)
    pa = df[df["pa_event_type"].notna() & ~df["pa_event_type"].str.startswith("caught_stealing", na=False)].copy()
    return df, pa


def line(p):
    ev = p["pa_event_type"]; n = len(p)
    ab = ev.isin(AB_EV).sum(); h = ev.isin(HIT).sum(); tb = ev.map(HIT).fillna(0).sum()
    bb = (ev == "walk").sum(); hbp = (ev == "hit_by_pitch").sum(); sf = (ev == "sac_fly").sum()
    k = ev.isin(["strikeout", "strikeout_double_play"]).sum(); obp_d = ab + bb + hbp + sf
    return {"PA": flagP(n), "AB": ab, "H": h, "AVG": f3(h / ab if ab else np.nan), "OBP": f3((h + bb + hbp) / obp_d if obp_d else np.nan),
            "SLG": f3(tb / ab if ab else np.nan), "HR": int((ev == "home_run").sum()), "K%": pc(k / n if n else np.nan),
            "BB%": pc(bb / n if n else np.nan), "2B": int((ev == "double").sum()), "3B": int((ev == "triple").sum()),
            "BB": int(bb), "K": int(k), "HBP": int(hbp)}


def pitch_block(p, pa_rows):
    bip = p[p["is_in_play"] == True]; ev = bip["launch_speed"].dropna(); sw = p["swing"].sum()
    L = line(pa_rows)
    return {"Pitches": flagP(len(p)), "Swing%": pc(sw / len(p) if len(p) else np.nan), "Whiff%": pc(p["whiff"].sum() / sw if sw else np.nan),
            "BBE w/ EV": flagP(len(ev)), "Avg EV": f"{ev.mean():.1f}" if len(ev) else "—", "Max EV": f"{ev.max():.1f}" if len(ev) else "—",
            "Hard-hit%": pc((ev >= 95).mean() if len(ev) else np.nan), "PA ending": L["PA"], "AVG": L["AVG"], "SLG": L["SLG"], "HR": L["HR"]}


def save(t, name, title, index=True):
    t.to_csv(D / name, index=index)
    print(f"\n{title}  -> {name}")
    print(t.to_string(index=index))


def build_tables():
    df, pa = load()
    lowA, lowA_pa = df[df.level == "Low-A"], pa[pa.level == "Low-A"]
    print(f"Florida State League (Low-A): pitch type tracked on {lowA.pitch_type.notna().sum()} of {len(lowA)} pitches; "
          f"{lowA.launch_speed.notna().sum()} batted balls with exit velo.   ⚠ = under 20 PA or pitches")

    t1 = pd.DataFrame({gn: pitch_block(lowA[lowA.group == gn], lowA_pa[lowA_pa.group == gn]) for gn in ["Fastball", "Breaking", "Offspeed"]}).T
    save(t1, "pitch_table1_by_pitch_group_2026.csv", "1. BY PITCH GROUP, Florida State League (results = PAs ending on that pitch group)")

    fb, fb_pa = lowA[lowA.group == "Fastball"], lowA_pa[lowA_pa.group == "Fastball"]
    t2 = pd.DataFrame({"93+ mph": pitch_block(fb[fb.start_speed >= 93], fb_pa[fb_pa.start_speed >= 93]),
                       "Under 93": pitch_block(fb[fb.start_speed < 93], fb_pa[fb_pa.start_speed < 93])}).T
    save(t2, "pitch_table2_fastball_velo_2026.csv", "2. FASTBALLS BY VELOCITY, Florida State League")

    bip = lowA[(lowA.is_in_play == True) & lowA.launch_speed.notna()]
    rows = []
    for z in list(range(1, 10)) + [11, 12, 13, 14]:
        b = bip[bip.zone == z]; hh = b[b.launch_speed >= 95]
        rows.append({"Zone": z, "Region": "in zone" if z <= 9 else "chase", "BBE": len(b), "Hard-hit": len(hh),
                     "Hard-hit avg EV": f"{hh.launch_speed.mean():.1f}" if len(hh) else "—"})
    t3 = pd.DataFrame(rows)
    save(t3, "pitch_table3_hard_hit_by_zone_2026.csv",
         "3. HARD-HIT BALLS (95+ mph) BY ZONE, Florida State League (1-9 = strike zone, catcher's view; 11-14 = chase zones)", index=False)
    print(f"   in zone: {t3[t3.Zone <= 9]['Hard-hit'].sum()} hard-hit of {t3[t3.Zone <= 9].BBE.sum()} BBE | chase: {t3[t3.Zone > 9]['Hard-hit'].sum()} of {t3[t3.Zone > 9].BBE.sum()} | no zone: {bip.zone.isna().sum()}")

    rs = pa[pa.game_type == "R"].copy()
    rs["state"] = np.select([rs.pre_b > rs.pre_s, rs.pre_b == rs.pre_s], ["Ahead", "Even"], "Behind")
    sub = lambda lvl: rs if lvl == "Combined" else rs[rs.level == lvl]
    t4 = pd.DataFrame({(lvl, f"vs {h}HP"): {c: line(sub(lvl)[sub(lvl).p_throws == h])[c] for c in ["PA", "AVG", "OBP", "SLG", "HR", "K%", "BB%"]}
                       for lvl in LEVELS for h in ["R", "L"]}).T.rename_axis(["level", "split"])
    save(t4, "pitch_table4_vs_hand_2026.csv", "4. VS RHP AND LHP, regular season (Low-A = Florida State League, High-A = Midwest League, Double-A = Texas League)")

    t5 = pd.DataFrame({(lvl, st): {c: line(sub(lvl)[sub(lvl).state == st])[c] for c in ["PA", "AVG", "SLG", "HR"]}
                       for lvl in LEVELS for st in ["Ahead", "Even", "Behind"]}).T.rename_axis(["level", "count"])
    save(t5, "pitch_table5_by_count_2026.csv", "5. BY COUNT BEFORE THE PA's FINAL PITCH, regular season (ahead = more balls than strikes)")

    po = pa[(pa.level == "Double-A") & (pa.game_type != "R")]
    ng = df[(df.level == "Double-A") & (df.game_type != "R")].game_pk.nunique()
    L = line(po)
    t6 = pd.DataFrame([{"games": ng, "first": po.game_date.min(), "last": po.game_date.max(),
                        **{k: L[k] for k in ["PA", "AB", "H", "2B", "3B", "HR", "BB", "K", "HBP", "AVG", "OBP", "SLG", "K%", "BB%"]}}])
    save(t6, "pitch_table6_playoffs_2026.csv", "6. TEXAS LEAGUE PLAYOFFS (Springfield)", index=False)

    print("\nCross-check vs TJStats regular-season lines:")
    for lvl in LEVELS[:3]:
        L = line(sub(lvl)); print(f"   {lvl}: PA {L['PA']}, AVG {L['AVG']}, OBP {L['OBP']}, SLG {L['SLG']}, HR {L['HR']}, K% {L['K%']}, BB% {L['BB%']}")
    return {"t1": t1, "t2": t2, "t3": t3, "t4": t4, "t5": t5, "t6": t6}


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    build_tables()
