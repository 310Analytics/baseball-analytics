# Baseball Analytics Visualization Standards

When creating baseball analytics projects, reports, notebooks, dashboards, GitHub projects, or social-media graphics, prioritize baseball-specific visualizations rather than generic charts.

Visualizations should look professional enough for a baseball operations, player development, scouting, or analytics portfolio.

Use Statcast conventions whenever possible.

---

# GENERAL VISUALIZATION RULES

* Always clearly label the player, season/date range, sample size, and metric.
* Use consistent pitch-type colors throughout an entire project.
* Use baseball terminology rather than generic statistical terminology where appropriate.
* Include league-average reference lines when they improve interpretation.
* Include sample-size context.
* Avoid unnecessary chart clutter.
* Prefer direct labels over large legends when practical.
* Use equal aspect ratios when spatial relationships matter.
* Clearly identify pitcher handedness and batter handedness when relevant.
* When plotting pitch locations, always clarify that the view is from the catcher's perspective unless explicitly using another perspective.
* Do not create a chart merely because data exists. Every visualization should answer a baseball question.
* When comparing two seasons or time periods, keep scales identical.
* When displaying percentages, format them as percentages rather than decimals.
* When displaying velocity, label MPH.
* Movement should generally be displayed in inches.
* Spin rate should generally be displayed in RPM.
* Exit velocity should be displayed in MPH.
* Angles should be displayed in degrees.

---

# 1. PITCH MOVEMENT / PITCH SHAPE PLOT

One of the most important pitcher-analysis charts. Shows how each pitch moves relative to the pitcher's other offerings.

**Chart:** Scatter plot. X-axis: Horizontal Break/Movement. Y-axis: Induced Vertical Break (IVB). Points: individual pitches. Color: pitch type. Optional: larger/outlined markers for pitch-type averages.

**Important:** Keep x/y scales equal whenever possible. Include vertical line at 0 HB and horizontal line at 0 IVB. Include pitch-type average labels (e.g. FF: 16.8 IVB / -8.2 HB, SL: 2.3 IVB / 5.7 HB, CH: 7.1 IVB / -14.4 HB).

**Best for:** Arsenal analysis, pitch design, identifying pitch separation, comparing seasons, evaluating new pitches, fastball shape, slider/sweeper differences.

---

# 2. PITCH ARSENAL MOVEMENT PROFILE

Cleaner summary version of the movement plot. Instead of every pitch, plot one large point per pitch type's average movement. Each point includes pitch abbreviation, average velocity, IVB, horizontal break. Best for social graphics, scouting summaries, pitcher reports.

---

# 3. VELOCITY vs MOVEMENT PLOT

Shows relationship between velocity and movement. X-axis: velocity. Y-axis: IVB or HB. Color: pitch type. Can reveal fatigue, inconsistent pitch shape, intentional velocity manipulation, different pitch clusters, classification problems.

---

# 4. VELOCITY TREND GRAPH

Tracks velocity over time. X-axis: date/game/inning/pitch number. Y-axis: velocity. Lines: pitch types. Include rolling averages where appropriate. Best for velocity changes, injury/recovery analysis, in-season trends, mechanical changes, starter fatigue, first half vs second half.

---

# 5. ROLLING VELOCITY GRAPH

Use rolling average rather than individual game averages for trends. Common windows: 25/50/100 pitches, 5 games. Always label the rolling window — never present a rolling trend without explaining it.

---

# 6. RELEASE POINT PLOT

Shows consistency/changes in release position. X-axis: horizontal release position. Y-axis: vertical release position. Color: pitch type. Can reveal mechanical changes, arm-slot changes, pitch tipping risk, differences between pitches/seasons. Include average release point per pitch.

---

# 7. RELEASE POINT OVER TIME

X-axis: game date. Y-axis: release height or horizontal release position. Use separate graphs when necessary. Useful for detecting gradual mechanical changes.

---

# 8. ARM ANGLE / RELEASE ANGLE GRAPH

X-axis: date or pitch type. Y-axis: arm angle. Can be scatter, distribution, or rolling average. Useful for pitchers changing arm slots or adding sweep/drop.

---

# 9. EXTENSION PLOT

X-axis: date, pitch type, or velocity. Y-axis: release extension. Useful for perceived velocity and mechanical changes. Often paired with velocity.

---

# 10. PITCH LOCATION SCATTER PLOT

One of the most fundamental baseball charts. X-axis: horizontal plate location. Y-axis: vertical plate location. Color: pitch type. Draw the strike-zone rectangle. Default perspective: catcher's view. Useful filters: batter handedness, pitch type, count, result, season, two-strike situations.

---

# 11. PITCH LOCATION HEATMAP

Display pitch density instead of individual pitches. Shows where a pitcher generally attacks. Create separate heatmaps per pitch type when sample size permits (e.g. four-seam location, slider location, changeup location, two-strike location, first-pitch location). Do NOT use heatmaps with tiny samples.

---

# 12. RUN VALUE LOCATION HEATMAP

Display performance rather than frequency. Locations represent metrics like Run Value, xwOBA, Whiff%, Swing%, Chase%, SLG, exit velocity. Useful for finding where a pitcher is particularly effective or vulnerable.

---

# 13. WHIFF HEATMAP

Shows where pitches generate swinging strikes. Especially useful for sliders, sweepers, changeups, elevated fastballs. Use sufficient sample sizes and clearly display the denominator.

---

# 14. CHASE LOCATION MAP

Plot pitches outside the zone that produced swings. Useful for chase ability, breaking-ball effectiveness, two-strike approach, hitter plate discipline. May overlay all out-of-zone pitches with chase swings highlighted.

---

# 15. CALLED STRIKE LOCATION MAP

Shows where called strikes are generated. Especially useful for command analysis, edge locations, catcher framing discussions, fastball command.

---

# 16. PITCH RESULT LOCATION MAP

Plot pitches with markers representing results: Whiff, Called Strike, Foul, Ball, In Play. Useful for individual game breakdowns.

---

# 17. PITCH USAGE BAR CHART

Shows arsenal composition. X-axis: pitch type. Y-axis: usage %. Sort highest to lowest. Label percentages directly. Use when answering "What pitches does this pitcher throw?"

---

# 18. PITCH USAGE OVER TIME

One of the most useful charts for detecting approach changes. X-axis: date/game/month. Y-axis: usage %. Lines: pitch types. Can reveal newly introduced pitch, abandoned pitch, increased sweeper usage, decreased fastball reliance, midseason adjustments.

---

# 19. PITCH USAGE BY COUNT

Show pitch selection by count. Heatmap ideal. Rows: pitch type. Columns: counts (0-0 through 3-2). Values: usage %. Useful for sequencing and predictability analysis.

---

# 20. PITCH USAGE BY BATTER HANDEDNESS

Compare arsenal usage vs LHH and RHH. Grouped bar chart or two-panel comparison. Especially important for pitchers with large platoon differences.

---

# 21. PITCH PERFORMANCE TABLE / ARSENAL TABLE

Not technically a graph, but should appear in most pitcher analyses. Recommended columns: Pitch, Usage %, Velocity, Spin Rate, IVB, HB, Whiff %, Chase %, CSW %, xwOBA, Run Value, Extension. Only include relevant metrics. Apply sample-size filters.

---

# 22. WHIFF% BY PITCH TYPE

Bar chart. X-axis: pitch type. Y-axis: Whiff %. Include league-average lines if available. Especially useful for comparing secondary pitches.

---

# 23. CHASE% BY PITCH TYPE

Bar chart. X-axis: pitch type. Y-axis: Chase %. Useful for evaluating how well pitches expand the zone. Chase/O-Swing measures swings at pitches outside the strike zone, a standard plate-discipline measure.

---

# 24. CSW% BY PITCH TYPE

Called Strikes + Whiffs / total pitches. Bar chart by pitch type. Useful quick measure of pitch effectiveness. Clearly define CSW% somewhere in the report.

---

# 25. xwOBA ALLOWED BY PITCH TYPE

X-axis: pitch type. Y-axis: xwOBA allowed. Lower is better for pitchers. Include league-average reference where possible. Use minimum BBE/sample requirements.

---

# 26. RUN VALUE BY PITCH TYPE

X-axis: pitch type. Y-axis: Run Value. Clearly explain the sign convention used — don't assume every datasource represents pitcher run value the same direction.

---

# 27. STUFF+ / PITCH MODEL GRAPH

When Stuff+, Pitching+, Location+, or custom pitch-quality models are available: display pitch-quality scores by pitch type. X-axis: pitch type. Y-axis: model score. Include reference line at 100 = league average. Explicitly state that 100 represents average if that's the model's scale. Pitch-quality models evaluate underlying pitch quality rather than relying entirely on observed outcomes.

---

# 28. VELOCITY DISTRIBUTION

Histogram, violin, or box plot. Display velocity distribution per pitch type. Useful for identifying multiple versions of pitches, velocity consistency, velocity gains/losses, possible classification problems.

---

# 29. MOVEMENT DISTRIBUTION

Distribution of IVB and horizontal break, separated by pitch type. Useful when pitch averages hide meaningful shape variation.

---

# 30. SPIN RATE DISTRIBUTION

Histogram or violin plot. X-axis: pitch type. Y-axis: Spin Rate. Useful for assessing consistency and changes in pitch characteristics.

---

# 31. SPIN RATE OVER TIME

X-axis: date/game. Y-axis: Spin Rate. Separate pitch types. Useful for researching significant pitch-shape changes. Avoid implying causation solely from a spin-rate change.

---

# 32. VELOCITY vs SPIN RATE

Scatter plot. X-axis: velocity. Y-axis: spin rate. Color: pitch type. Useful for seeing pitch clusters and unusual observations.

---

# 33. ACTIVE SPIN / SPIN EFFICIENCY CHART

When the datasource contains active spin: show Active Spin % by pitch type. Useful for analyzing how effectively spin contributes to movement. Do not estimate spin efficiency unless the data supports the calculation.

---

# 34. PITCH TUNNELING / SEPARATION GRAPH

When enough trajectory data exists, compare two pitches at release, early flight, decision point, plate. Goal: show pitches that travel similarly before separating. Common pairings: FF+SL, FF+CH, SI+SL, SI+CH, FF+SPL. Do not claim true tunneling from movement averages alone.

---

# 35. FASTBALL–SECONDARY SEPARATION GRAPH

Simpler public-data approximation. Calculate differences between pitch averages in velocity, IVB, horizontal break. Display arrows connecting arsenal averages. Useful for visualizing pitch-pair separation.

---

# 36. SPRAY CHART

Standard hitter visualization. Plot batted-ball locations on a field. Separate by singles/doubles/triples/HR/outs OR color by exit velocity/launch angle/result. Useful for pull tendencies, opposite-field power, ground-ball direction, HR direction. Standard visualization available through major public baseball analytics platforms.

---

# 37. SPRAY CHART BY BATTED-BALL TYPE

Different markers for Ground Ball, Line Drive, Fly Ball, Popup. Useful for understanding hitter contact profile.

---

# 38. EXIT VELOCITY vs LAUNCH ANGLE

One of the most important hitter charts. X-axis: Launch Angle. Y-axis: Exit Velocity. Points: batted balls. Color: outcome or barrel status. Can highlight barrels, home runs, hits. Add useful reference regions when appropriate.

---

# 39. LAUNCH ANGLE DISTRIBUTION

Histogram. Shows frequency of ground balls, line drives, fly balls, popups. Do not judge hitters solely from average launch angle — distribution is often more informative.

---

# 40. EXIT VELOCITY DISTRIBUTION

Histogram or density plot. Better than simply displaying average EV. Useful for distinguishing frequent hard contact, occasional extreme contact, weak-contact tails.

---

# 41. HARD-HIT% GRAPH

Track Hard-Hit% by season, month, rolling, or by pitch type. When using Statcast definitions, specify the underlying threshold/source.

---

# 42. BARREL% GRAPH

Show Barrel% over time or against league average. Useful for evaluating quality of contact. Always include a minimum BBE threshold for player comparisons.

---

# 43. SWEET-SPOT% GRAPH

Show % of batted balls within the selected sweet-spot launch-angle definition. Include the exact definition/source used — don't assume every datasource defines this identically.

---

# 44. xwOBA vs wOBA SCATTER

Excellent luck/performance analysis chart. X-axis: xwOBA. Y-axis: wOBA. Add diagonal y=x. Players above line: results exceed expected. Below: results trail expected. Never automatically call the difference "luck" — describe it as over/underperformance relative to expected results unless further evidence exists.

---

# 45. xERA vs ERA SCATTER

Pitcher equivalent. X-axis: xERA. Y-axis: ERA. Add y=x diagonal. Useful for identifying pitchers whose run prevention differs substantially from Statcast expected results. Again, avoid automatically calling differences luck.

---

# 46. FIP vs ERA GRAPH

X-axis: FIP. Y-axis: ERA. Add diagonal reference. Useful for comparing actual run prevention with outcomes emphasized by FIP.

---

# 47. EXPECTED vs ACTUAL PERFORMANCE BAR CHART

For one player: ERA vs xERA, AVG vs xBA, SLG vs xSLG, wOBA vs xwOBA. Use grouped bars or dumbbell plots. Do NOT mix metrics with very different numerical scales on the same axis unless normalized.

---

# 48. PLATE DISCIPLINE PROFILE

Recommended hitter metrics: O-Swing/Chase%, Z-Swing%, Swing%, O-Contact%, Z-Contact%, Contact%, SwStr%. These are standard plate-discipline statistics describing how often hitters swing and make contact inside/outside the zone. Use radar charts only with strong reason — bar charts or percentile plots are usually easier to interpret.

---

# 49. CHASE% OVER TIME

X-axis: date/month/rolling PA. Y-axis: Chase %. Useful for detecting approach changes.

---

# 50. WHIFF% OVER TIME

Same format. Can identify swing changes, contact improvements, deterioration, injury-related trends.

---

# 51. SWING% BY ZONE

Create a strike-zone grid; each zone displays Swing%. Excellent hitter approach visualization. May use a 3x3 grid or detailed Statcast regions. Clearly define the zone system.

---

# 52. WHIFF% BY ZONE

Same structure, displaying Whiff%. Useful for identifying hitter weaknesses (e.g. high fastballs, sliders down and away, inside velocity).

---

# 53. xwOBA BY ZONE

Strike-zone heatmap. Excellent for identifying damage areas and weaknesses. Can be separated by pitch type.

---

# 54. EXIT VELOCITY BY ZONE

Heatmap of average exit velocity or hard-hit rate by location. Use only with adequate BBE counts per cell. Display minimum sample rules.

---

# 55. HITTER PERFORMANCE BY PITCH TYPE

Bar chart of xwOBA, wOBA, Run Value, Whiff%, SLG, xSLG against FF, SI, FC, SL, ST, CU, CH, FS. Useful for finding strengths and weaknesses.

---

# 56. PITCH-TYPE RUN VALUE GRAPH

For hitters: X-axis: pitch type. Y-axis: run value. Useful for understanding which pitch types a hitter has historically handled well or poorly. Pitch values/linear weights evaluate performance against individual pitch types.

---

# 57. VELOCITY BAND PERFORMANCE

Break fastballs into velocity ranges (<93, 93-95, 95-97, 97+). Plot xwOBA, Whiff%, Run Value. Useful for determining whether a hitter struggles with premium velocity. Require adequate samples.

---

# 58. PLATOON SPLIT GRAPH

Compare vs LHP and vs RHP: wOBA, xwOBA, K%, BB%, ISO, SLG, Whiff%. Grouped bar charts or dumbbell plots work well.

---

# 59. BATTED-BALL PROFILE

Show GB%, LD%, FB%, Pull%, Center%, Oppo%. Good summary hitter graph.

---

# 60. PULL / CENTER / OPPO GRAPH

Bar chart. Useful for evaluating directional approach changes. Can also be shown over time.

---

# 61. CONTACT QUALITY QUADRANT

X-axis: Average Exit Velocity or Hard-Hit %. Y-axis: launch-angle quality, Barrel%, xwOBA, etc. Add league-average vertical/horizontal lines creating four quadrants. Useful for comparing hitters.

---

# 62. PITCHER COMMAND MAP

Compare intended/typical location to actual distribution when target data exists. If target data is NOT available, do not call simple pitch-location clustering "command" — use terms like location, zone rate, edge rate, location consistency instead. Command should not be inferred solely from pitch coordinates.

---

# 63. ZONE% GRAPH

Track % of pitches in the strike zone, by pitch, by month, or over time. Useful for command/control discussions.

---

# 64. FIRST-PITCH STRIKE% GRAPH

Track F-Strike%. Useful for evaluating how aggressively a pitcher gets ahead.

---

# 65. WALK% vs STRIKEOUT% SCATTER

X-axis: BB%. Y-axis: K%. Add league averages. Excellent quick pitcher or hitter comparison.

---

# 66. K-BB% GRAPH

Very useful pitcher metric. Display season-to-season, rolling, league comparison, leaderboard. Because K and BB stabilize differently from ERA, K-BB% provides useful process information.

---

# 67. WHIFF% vs CHASE% SCATTER

X-axis: Chase%. Y-axis: Whiff%. Color by pitcher or pitch type. Add league-average quadrant lines. Excellent for identifying pitches that both miss bats and expand the zone.

---

# 68. STUFF vs COMMAND QUADRANT

X-axis: Location+/command metric. Y-axis: Stuff+. Add lines at 100 where applicable. Quadrants: High Stuff/High Command, High Stuff/Low Command, Low Stuff/High Command, Low Stuff/Low Command. Useful for pitcher profiling.

---

# 69. VELOCITY vs IVB FASTBALL LEADERBOARD

X-axis: velocity. Y-axis: IVB. Show league-average quadrant lines. Color or highlight the pitcher being analyzed. Excellent for identifying unusual fastball shapes.

---

# 70. VELOCITY vs HORIZONTAL BREAK

Especially useful for sinkers, sweepers, changeups. Same quadrant structure.

---

# 71. PITCH SHAPE LEAGUE COMPARISON

Plot every league pitch of a specific type in light/low-emphasis points. Highlight the target pitcher (e.g. all MLB sweepers, X=HB, Y=IVB, highlight the pitcher). Useful for showing HOW unusual a pitch actually is.

---

# 72. PERCENTILE RANK GRAPH

Baseball Savant-style percentile presentation. Metrics could include Velocity, Whiff%, Chase%, K%, BB%, Barrel%, Hard-Hit%, xwOBA, Stuff+. Display percentile 0-100. Always make directionality clear — higher percentile should visually represent better performance whenever possible; transform appropriately for metrics where lower is better.

---

# 73. PLAYER COMPARISON DUMBBELL CHART

Great for comparing two seasons (e.g. 2025 vs 2026). Metrics: Velocity, Whiff%, Chase%, Zone%, xwOBA, K%. A line connects the two values. Often superior to grouped bars for showing change.

---

# 74. BEFORE / AFTER CHANGE GRAPH

When investigating a mechanical or pitch-mix adjustment: split data around a meaningful date. Show BEFORE/AFTER for Velocity, Usage, Movement, Whiff%, Chase%, xwOBA, release point. Do not arbitrarily choose a date simply because it creates a better narrative — explain how the breakpoint was selected.

---

# 75. ROLLING PERFORMANCE GRAPH

One of the most important tools for identifying changes. Possible metrics: ERA, FIP, xFIP, K%, BB%, K-BB%, Whiff%, Chase%, xwOBA, Velocity, Hard-Hit%, Barrel%. X-axis: game/date/PA. Y-axis: metric. Clearly state the rolling window (e.g. "50 PA rolling xwOBA" or "100 pitch rolling fastball velocity").

---

# 76. CUMULATIVE PERFORMANCE GRAPH

Use for cumulative WAR, Run Value, HR, K, WPA over a season. Do not use cumulative charts when a rate statistic would better answer the question.

---

# 77. GAME-BY-GAME TREND GRAPH

X-axis: Game Date. Y-axis: metric. Useful for velocity, pitch usage, innings, strikeouts, CSW, Whiff%, release point. Use rolling averages if individual games are excessively noisy.

---

# 78. MONTH-BY-MONTH GRAPH

Good when game-level data is too noisy. Use equal-sample warnings when monthly samples differ substantially.

---

# 79. CORRELATION SCATTER PLOT

Used when exploring relationships (Velocity vs Whiff%, IVB vs Whiff%, Chase% vs K%, Barrel% vs xwOBA, Extension vs perceived velocity). Include trend line, correlation value when appropriate, sample-size thresholds. Never imply causation from correlation.

---

# 80. LEAGUE DISTRIBUTION + PLAYER MARKER

Excellent analytical visualization. Show the league distribution for a metric, then mark the player's value (e.g. MLB SP fastball velocity distribution, player = 96.4 MPH). Provides much more context than a bare number.

---

# 81. Z-SCORE / STANDARD DEVIATION PROFILE

Normalize metrics against league average. Useful when comparing different units. Display how many standard deviations a player sits above/below league average. Excellent for arsenal profiles. Explain the normalization.

---

# 82. RADAR / SPIDER CHART

Use sparingly. Possible dimensions: Velocity, Movement, Whiff, Chase, Command, Stuff. Radar charts look attractive but can distort comparisons. Use percentile values rather than mixing metrics with different scales. Prefer bars or dot plots when precise comparisons matter.

---

# 83. PITCH SEQUENCE CHART

Shows pitch sequence within plate appearances. Include Pitch #, Pitch Type, Velocity, Location, Count, Result. Can visualize pitches connected chronologically around the strike zone. Useful for sequencing, setup pitches, two-strike strategy, individual game analysis.

---

# 84. COUNT PROGRESSION / DECISION TREE

Analyze what a pitcher throws depending on count progression (e.g. 0-0→FF, 0-1→SL, 0-2→SL/CH). Can use Sankey diagram, decision tree, or count heatmap. Only use Sankey diagrams when flow genuinely helps interpretation.

---

# 85. TIMES THROUGH THE ORDER GRAPH

For starting pitchers: compare 1st/2nd/3rd time through on xwOBA, wOBA, K%, Whiff%, Velocity. Useful for starter usage and fatigue discussions.

---

# 86. INNING VELOCITY / PERFORMANCE GRAPH

X-axis: Inning. Y-axis: Velocity/Whiff%/xwOBA. Useful for detecting fatigue patterns.

---

# 87. PITCH NUMBER FATIGUE GRAPH

X-axis: pitch number, can bucket (1-25, 26-50, 51-75, 76-100, 100+). Y-axis: Velocity, Movement, Whiff%, xwOBA. Use large enough samples.

---

# 88. HOME / ROAD SPLITS

Grouped comparison of meaningful metrics. Do not overinterpret small or park-influenced samples.

---

# 89. PARK-ADJUSTED COMPARISON

When comparing offensive performance across parks, use park-adjusted statistics when available (wRC+, ERA-, FIP-). Clearly identify metrics where 100 = league average.

---

# 90. AGE CURVE

X-axis: Age. Y-axis: performance metric. Can overlay player vs league average age curve. Useful for projection and development analysis. Do not infer an individual's future solely from a population-level age curve.

---

# 91. PLAYER SIMILARITY MAP

Use multiple metrics to identify similar players. Possible methods: PCA, UMAP, nearest neighbors. Plot players in two-dimensional space. Highlight target player and nearest comps. Clearly explain methodology.

---

# 92. CLUSTERING / PITCH CLASSIFICATION MAP

Cluster pitches using velocity, IVB, HB, spin, release position. Useful for identifying unusual pitches, hybrid pitches, classification errors, pitch-shape groups. Do not automatically replace official Statcast classifications without explaining the model.

---

# 93. WAR / VALUE TREND

X-axis: Season. Y-axis: WAR. May compare fWAR vs bWAR. Never combine different WAR systems as though they are identical — name the source.

---

# 94. OFFENSIVE PRODUCTION PROFILE

Common summary metrics: wRC+, wOBA, xwOBA, ISO, K%, BB%. Can be represented using percentile bars. wOBA weights offensive events according to their run value rather than treating all ways of reaching base equally.

---

# 95. DEFENSIVE VALUE GRAPH

Depending on available data: OAA, DRS, UZR, FRV. Show season-to-season or positional comparison. Do not combine defensive metrics from different systems into one number unless methodology is explicitly explained.

---

# 96. CATCH PROBABILITY / OAA VISUAL

For outfield defense: plot plays by distance/opportunity difficulty, catch probability, outcome. Useful when appropriate Statcast fielding data exists.

---

# 97. SPRINT SPEED DISTRIBUTION

Show player sprint speed, league distribution, percentile. Useful for baserunning and athleticism analysis.

---

# 98. HOME RUN / BATTED-BALL DISTANCE GRAPH

Can show exit velocity, launch angle, projected distance. Useful for power analysis. Avoid treating projected distance as a complete measure of hitter quality.

---

# 99. WIN PROBABILITY GRAPH

X-axis: game progression. Y-axis: Win Probability. Mark major plays. Useful for game analysis rather than player talent evaluation.

---

# 100. WIN PROBABILITY ADDED GRAPH

Show cumulative WPA throughout a game or season. Use primarily for storytelling/context. Do not treat WPA as a pure talent metric.

---

# CHART SELECTION PRIORITY

**Pitcher default order:** 1. Pitch Arsenal Table 2. Pitch Usage 3. Movement Profile 4. Velocity 5. Release Point 6. Location 7. Whiff% 8. Chase% 9. CSW% 10. xwOBA/Run Value 11. Usage Over Time 12. Velocity Over Time 13. Movement Over Time 14. Handedness Splits 15. League Comparison 16. Rolling Performance

**Hitter default order:** 1. Overall Statistical Profile 2. Percentile Profile 3. Exit Velocity 4. Launch Angle 5. EV × Launch Angle 6. Spray Chart 7. Plate Discipline 8. Zone Heatmaps 9. Pitch-Type Performance 10. Platoon Splits 11. Hard-Hit% 12. Barrel% 13. xwOBA vs wOBA 14. Rolling Performance 15. League Comparison

---

# PITCHER CHANGE ANALYSIS TEMPLATE

When asked "What changed with [Pitcher]?" investigate in this order: 1. Velocity 2. Pitch usage 3. Pitch movement 4. Release point 5. Extension/arm angle 6. Pitch location 7. Zone% 8. Chase% 9. Whiff% 10. CSW% 11. Batter handedness 12. Count-based usage 13. Expected results 14. Contact quality allowed.

Create charts showing changes over time instead of simply comparing aggregate statistics. Try to determine whether the change came from Stuff, Location, Pitch mix, Sequencing, Platoon strategy, Contact management, Velocity, Mechanics, or some combination. Do not force a causal conclusion when the data only establishes correlation.

---

# HITTER CHANGE ANALYSIS TEMPLATE

When asked "What changed with [Hitter]?" investigate: 1. Swing% 2. Chase% 3. Contact% 4. Whiff% 5. Zone performance 6. Pitch-type performance 7. Exit velocity 8. Hard-Hit% 9. Barrel% 10. Launch-angle distribution 11. Pull% 12. Spray distribution 13. Platoon splits 14. Performance against velocity 15. Expected vs actual results.

---

# SMALL SAMPLE RULE

Always flag small samples. Do not confidently interpret pitch performance from a handful of pitches, hitter splits from a handful of plate appearances, zone heatmaps with sparse cells, xwOBA based on very few batted balls, or short-term ERA changes as proof of skill changes. Prefer "Early evidence suggests..." instead of "This proves..."

---

# STATCAST DATA FIELDS TO PRIORITIZE

When using Baseball Savant / pybaseball Statcast data, commonly useful fields include:

**Pitch characteristics:** pitch_type, release_speed, release_spin_rate, pfx_x, pfx_z, release_pos_x, release_pos_z, release_extension

**Location:** plate_x, plate_z, zone

**Context:** game_date, inning, balls, strikes, stand, p_throws

**Pitch result:** description, events

**Batted ball:** launch_speed, launch_angle, hit_distance_sc, hc_x, hc_y, bb_type

**Expected statistics when available:** estimated_ba_using_speedangle, estimated_woba_using_speedangle, woba_value, woba_denom

Always consult current datasource documentation before assuming a field's meaning or units.

---

# FINAL VISUALIZATION STANDARD

Every important chart should answer one sentence. Examples: "Cease's slider gained approximately X inches of horizontal movement." "Ray increased four-seam usage from X% to Y%." "The hitter's chase rate has dropped substantially since June." "His fastball occupies an unusual velocity/IVB combination relative to MLB fastballs."

If the analyst cannot clearly state what question a chart answers, reconsider including it. The objective is not to produce the maximum number of charts. The objective is to use the smallest set of high-quality visualizations necessary to explain what happened, why it matters, and what changed.

---

# Baseball Analytics Project — Preferences (this project specifically)

## Chart Style — Percentile Charts (TJStats-inspired, hitting & value)
- Horizontal bar percentile charts, Savant-style colors: Elite (67+): #D22D49 (red), Average (33-66): #B0AFAF (gray), Poor (below 33): #3571A3 (blue)
- Circle percentile markers at bar end, white bold text, number only
- Raw stat value printed to the right of each bar
- Reference lines at 0, 50 (dashed gray), 100 — use `ax.vlines` with explicit y-limits, NOT `ax.axvline` (draws full-height, collides with title/labels)
- "League Average" label above the bars, not overlapping — position above y=-0.5
- Remove top, right, bottom, left spines
- Title: use `ax.set_title` (not `fig.suptitle`, miscenters when left labels vary in width), `pad=20`
- Layout: `plt.subplots_adjust(left=..., right=..., top=..., bottom=...)` with fixed margins — do NOT combine `plt.tight_layout()` with a title
- Save with `plt.savefig(..., dpi=200)` — do NOT use `bbox_inches='tight'` (crops asymmetrically, throws off centering)
- Caption: "Data: FanGraphs.com, [date range]" — simple, no over-explaining

## Chart Style — Pitching Charts (team-specific)
- Padres brown/gold color scheme for pitch mix, arsenal, and team-specific breakdowns
- Same spine removal and layout rules as above
- Match visual language of prior notebooks (Mize, Morejon, Rodriguez, Matsui, Vasquez) for portfolio consistency

## Stat Selection
- Avoid redundant/overlapping stats in the same chart (don't show both wRC+ and wOBA — pick one)
- Prefer widely-recognized stats over obscure ones when possible
- Flag noisy small-sample stats (e.g. Clutch is volatile under ~100 PA)
- When comparing to a position group, note the qualifier and PA minimum used

## Writing Voice (Twitter/X posts, referencing the "Action Jackson" Merrill post)
- Open with a punchy, direct statement of the storyline — no throat-clearing
- Numbers-first: stat, then percentile/context immediately after
- Short sentences, fragments fine. Bullet lists over paragraphs for multiple stats
- No AI-sounding filler ("elite," "showcase," "underscore," "notably," "it's worth noting")
- Minimal adjectives — let the numbers carry the weight
- End with a takeaway line, not a question or hedge
- Hashtag: #Padres, standalone final line

## Data Sources
- FanGraphs: manual export only (site blocks scraping) — user provides CSVs directly
- Baseball Savant / Statcast: pull via `pybaseball` when possible
- Baseball Reference: pull directly via code when possible
- Merge key: PlayerId, not Name
- Position-filtered comparisons require position-filtered exports

## GitHub Workflow
- Repo: 310Analytics/baseball-analytics
- Notebooks and figures live together per player/topic
- `git add .`, `git commit -m "..."`, `git push` for updates — already connected via `origin main`
