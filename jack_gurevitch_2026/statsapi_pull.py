"""Every pitch Jack Gurevitch saw in 2026 (Low-A, High-A, Double-A, regular season + playoffs) from the MLB Stats API.

Game logs come from /people/{id}/stats, pitch data from each game's v1.1 live feed. Feeds are cached in a temp
folder (about 74 MB for 124 games), so a rerun only downloads games it hasn't seen.
"""
import json
import os
import tempfile
import time
from pathlib import Path

import pandas as pd
import requests

D = Path(__file__).resolve().parent
OUT = D / "gurevitch_pitches_2026_statsapi.csv"
FEEDS = Path(tempfile.gettempdir()) / "gurevitch_statsapi_feeds"
PID = 813668  # MLBAM id
BASE = "https://statsapi.mlb.com/api/v1"
LVL = {12: "Double-A", 13: "High-A", 14: "Low-A"}  # Stats API sportId -> level


def game_log():
    games = []
    for sport, lvl in LVL.items():
        for gt in ["R", "F,D,L,W"]:
            j = requests.get(f"{BASE}/people/{PID}/stats?stats=gameLog&group=hitting&season=2026&sportId={sport}&gameType={gt}", timeout=30).json()
            for st in j.get("stats", []):
                for s in st["splits"]:
                    games.append({"gamePk": s["game"]["gamePk"], "date": s["date"], "level": lvl, "game_type": s.get("gameType", gt[0]),
                                  "log_pa": s["stat"].get("plateAppearances", 0)})
    return pd.DataFrame(games).drop_duplicates("gamePk")


def pull():
    FEEDS.mkdir(exist_ok=True)
    games = game_log()
    rows, fetched = [], 0
    for g in games.itertuples():
        path = FEEDS / f"{g.gamePk}.json"
        if not path.exists():
            r = requests.get(f"https://statsapi.mlb.com/api/v1.1/game/{g.gamePk}/feed/live", timeout=60); r.raise_for_status()
            path.write_text(r.text); fetched += 1; time.sleep(0.25)
        feed = json.loads(path.read_text())
        for play in feed["liveData"]["plays"]["allPlays"]:
            m = play["matchup"]
            if m["batter"]["id"] != PID:
                continue
            pitches = [e for e in play["playEvents"] if e.get("isPitch")]
            for k, e in enumerate(pitches):
                d, pdt, hd = e.get("details", {}), e.get("pitchData", {}) or {}, e.get("hitData", {}) or {}
                c = pdt.get("coordinates", {}) or {}
                rows.append({
                    "game_pk": g.gamePk, "game_date": g.date, "level": g.level, "game_type": g.game_type,
                    "inning": play["about"]["inning"], "half": play["about"]["halfInning"], "at_bat_index": play["about"]["atBatIndex"],
                    "pitch_number": e.get("pitchNumber"), "balls": e.get("count", {}).get("balls"), "strikes": e.get("count", {}).get("strikes"),
                    "pitcher_id": m["pitcher"]["id"], "pitcher_name": m["pitcher"].get("fullName"), "p_throws": m.get("pitchHand", {}).get("code"),
                    "stand": m.get("batSide", {}).get("code"),
                    "pitch_type": (d.get("type") or {}).get("code"), "pitch_name": (d.get("type") or {}).get("description"),
                    "call": (d.get("call") or {}).get("code"), "description": d.get("description"),
                    "is_in_play": d.get("isInPlay"), "is_strike": d.get("isStrike"), "is_ball": d.get("isBall"),
                    "start_speed": pdt.get("startSpeed"), "end_speed": pdt.get("endSpeed"), "zone": pdt.get("zone"),
                    "px": c.get("pX"), "pz": c.get("pZ"), "sz_top": pdt.get("strikeZoneTop"), "sz_bot": pdt.get("strikeZoneBottom"),
                    "spin_rate": (pdt.get("breaks") or {}).get("spinRate"), "extension": pdt.get("extension"),
                    "launch_speed": hd.get("launchSpeed"), "launch_angle": hd.get("launchAngle"), "hit_distance": hd.get("totalDistance"),
                    "trajectory": hd.get("trajectory"), "hardness": hd.get("hardness"),
                    "pa_result": play["result"].get("event") if k == len(pitches) - 1 else None,
                    "pa_event_type": play["result"].get("eventType") if k == len(pitches) - 1 else None,
                })
    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)
    print(f"games: {len(games)} ({fetched} feeds downloaded, rest cached) | pitches: {len(df)} -> {OUT.name}")
    chk = df[df.pa_result.notna()].groupby(["level", "game_type"]).size().rename("PA_feed").to_frame().join(games.groupby(["level", "game_type"])["log_pa"].sum())
    print(chk.to_string())
    return df


if __name__ == "__main__":
    pull()
