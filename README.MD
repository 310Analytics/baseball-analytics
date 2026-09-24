310Analytics. Baseball analytics by Garon, former D3 pitcher. Statcast, FanGraphs, and TJStats breakdowns, mostly Padres.

Using Python, FanGraphs, and Statcast data to break down players and figure out what's actually behind their numbers.

## Project Goal
The purpose of this project is to answer one question: how can data be used to make pitchers and hitters better?

## Why
After 4 years of D3 baseball I'm trying to learn the analytics side to work in baseball.

## What I look at

**Pitching**
* Statcast data (Savant)
* Pitch usage
* Whiff rate and chase rate
* Pitch shape, spin axis, movement
* Velocity, spin rate
* Release point, extension, arm slot
* xBA, xwOBA, run value per pitch
* ERA vs FIP
* Sequencing
* Stuff+, Pitching+, Location+

**Hitting**
* Exit velocity, barrel rate, hard-hit rate
* xwOBA, xSLG, xBA vs actual results
* Plate discipline: Z-Swing%, O-Swing%, Swing%, Whiff%, Z-Contact%, chase rate
* Batted ball profile: pull%, launch angle, GB/FB/LD splits
* wRC+, wOBA, and other park-adjusted production stats
* Win Probability Added and clutch
* Percentile rankings, pulled or modeled from TJStats

**General**
* Defensive run value (OAA, DRS, FRV)
* WAR and value breakdowns (offense, defense, base running)
* Before/after splits tied to mechanical, approach changes or hot/cold streaks

## Tools
Python, PyBaseball, Pandas, Matplotlib, Jupyter Notebook, FanGraphs, Baseball Savant, TJStats, VS Code

## Projects

### [Padres Games 2 and 3 Starters](padres_game2_game3_starters_2026/README.md)
Who starts after King? Matched each starter's pitch mix against the Cubs, Phillies, Braves, and D-backs lineups since the break, then weighed it against recent form.

### [Ty France 2026: Breakout vs Career](ty_france_2026/README.md)
140 wRC+ vs a 110 career mark, and the gains are all contact quality.

### [Walker Buehler: Arsenal Change, 2024–2026](buehler_arsenal_change_2026/README.md)
Rebuilt his pitch mix every year since 2024. Contact quality hasn't followed.

### [Jackson Merrill: Since the All-Star Break](merrill_post_asb_2026/README.md)
99th percentile wRC+, 100th percentile xSLG and Barrel% against qualified outfielders since the break.

### [Casey Mize: Padres Debut Breakdown](mize_padres_debut_2026/README.md)
Debut looked bad on paper, but the stuff held up. Pitch sequencing was the problem.

### [Randy Vásquez: Underusing His Best Weapons](vasquez_pitch_mix_2026/README.md)
His slider and changeup miss the most bats and get thrown the least.

### [Pete Crow-Armstrong vs Shohei Ohtani: MVP Case](pca_vs_ohtani_mvp_2026/README.md)
Out hitting Ohtani, out running him, and his defense is worth about 2x what Ohtani's pitching has added.

### [Fernando Tatis Jr.: Opening His Stance](tatis_open_stance_2026/README.md)
Opened up his stance and has returned to elite play since June.

### [Adrian Morejon: Best Lefty Reliever in Baseball](morejon_bullpen_2026/README.md)
Top of the board in Stuff+, Pitching+, K-BB%, FIP-, xFIP-, and SIERA against every lefty reliever with 30+ IP.

### [Yuki Matsui: The Slider Takeover](matsui_slider_2026/README.md)
ERA dropped this year and it traces back to one reshaped pitch: the slider.

### [Bradgley Rodríguez: Pitch Usage vs Whiff Rate](bradgley_rodriguez_pitch_usage_2026/README.md)
First one I did. Usage vs whiff rate, checking if he was underusing pitches that were actually working.
