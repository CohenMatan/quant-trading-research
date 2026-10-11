# Owner message 2026-10-11: "Phase 8 — H023 Score v2 Weight Optimization. Develop on 2011–2017, Freeze One Formula, Keep 2018–2021 Sealed"

Decision id: **D199**. Recorded and committed BEFORE any H023 code is run on QuantConnect. The owner's message follows verbatim.



---



Phase 8 — H023
Score v2 Weight Optimization
Develop on 2011–2017, Freeze One Formula, Keep 2018–2021 Sealed
Continue from:
P7-CP7 — H022 Data v2 Real Evaluation
Owner decision:
H022 / Score v1 remains permanently Rejected / NOT QUALIFIED exactly as tested.
I now approve a new hypothesis, H023.
The objective is to determine whether the existing Score architecture can become useful by changing weights only, using the already-open 2011–2017 period as a development/training set.
This is not a rescue or rerun of H022.
It is:
H023 — Score v2 Weight Optimization
2011–2017 is now explicitly a training/development period for H023.
2018–2021 remains unopened and will later serve as the first genuine forward validation of the selected Score v2.
The 2022–2026 Holdout remains locked.
1. Preserve H022 permanently
Do not modify or reinterpret H022.
Permanent record:

```
H022 / Score v1
Data v2
Real test E024-07
NOT QUALIFIED
```

Its real result remains:

```
t_IC = 0.4771
mean IC = 0.00755
80+ excess = -12.57% / year
quintile monotonicity = -0.40
G1 = FAIL
G2 = FAIL
G3 = FAIL
G4 = FAIL
```

Do not overwrite these results.
Do not call H023 a corrected H022.
2. H023 research question
The new question is:
Can a different weighting of the existing frozen Score v1 information produce a robust cross-sectional predictive score during 2011–2017 that is strong and stable enough to justify one untouched validation on 2018–2021?
We are allowed to optimise weights because 2011–2017 is now the development set.
We are not allowed to change the underlying information yet.
3. Data Infrastructure v2 remains frozen
Use the frozen Data Infrastructure v2 exactly as already approved.
Do not change:

* universe;
* PIT market-cap repair;
* M2 fundamental timing;
* SEC identity;
* restatement guard;
* price handling;
* corporate actions;
* H1–H7;
* share-class rules;
* sector classification;
* response construction;
* research calendar.

Use the existing frozen Data v2 manifest.
This hypothesis changes the Score weights only.
4. What may change
Only the weighting of these three existing Score layers may change:

```
Technical
Fundamental
Sector
```

All calculations inside each layer remain unchanged.
No new indicators.
No removed indicators.
No changed lookbacks.
No changed scoring bands.
No changed fundamental definitions.
No changed sector definitions.
No feature-level weight optimisation in this checkpoint.
5. Normalise the existing layers
The existing layer maxima are:

```
Technical = 40
Fundamental = 45
Sector = 15
```

For weight-search purposes define:

```
T = TechnicalSubtotal / 40
F = FundamentalSubtotal / 45
S = SectorSubtotal / 15
```

Then candidate Score v2 is:

```
Score_v2 =
    wT * T
  + wF * F
  + wS * S
```

where:

```
wT + wF + wS = 100
```

The score therefore remains on an approximately 0–100 scale.
Do not alter the underlying layer values.
Do not introduce post-hoc rescaling based on observed returns.
6. Pre-register the entire weight search before seeing results
Use the following grid:

```
wT = 10, 15, 20, ..., 80
wF = 10, 15, 20, ..., 80
wS = 0, 5, 10, ..., 30
```

subject to:

```
wT + wF + wS = 100
```

Include the original:

```
40 / 45 / 15
```

as a control.
Do not add additional weights after seeing the results.
Do not switch to 1-point increments.
Do not extend a boundary because the best configuration happens to sit there.
If the search suggests a boundary problem, report it and STOP for owner approval before any expanded search.
7. Entry threshold remains 80
For this first Score v2 experiment keep:

```
80+ threshold = 80
```

unchanged.
Do not jointly optimise:

```
weights + entry threshold
```

That would materially expand the search space.
The purpose of H023 is weight optimisation only.
8. Primary horizon remains one month
Keep the same primary response as H022:

```
next-session open after review
→
next monthly review close
```

and the same demeaned total-shareholder-return response.
Do not optimise holding horizon.
The 2-month and 3-month horizons may be calculated later as diagnostics only.
9. Development period
Use only:

```
2011-01-31 → 2017-11-30
```

for weight optimisation.
This period is no longer considered OOS for H023.
It is explicitly:

```
TRAINING / DEVELOPMENT
```

That fact must be permanently recorded.
10. 2018–2021 remains sealed
Do not access:

```
2018-01-01 → 2021-12-31
```

during:

* weight search;
* null calibration;
* robustness testing;
* score selection;
* diagnostics;
* plateau analysis.

This will be H023's first genuine external validation set.
11. Holdout remains sealed
Do not access:

```
2022-01-01 → 2026-08-31
```

for any purpose.
12. Metrics for every weight configuration
For every candidate weight triplet calculate on 2011–2017:
Ranking signal

```
monthly Spearman IC
mean IC
Newey-West t_IC, lag 2
```

Economic 80+ group

```
mean monthly demeaned return
annualised demeaned return
number of 80+ stock-months
number of months with an 80+ stock
mean 80+ count / month
```

Quintiles

```
Q1
Q2
Q3
Q4
Q5
Q5-Q1
quintile monotonicity Spearman
```

Stability

```
IC by year
first-half IC
second-half IC
2011–2012 contribution
2013–2014 contribution
2015–2016 contribution
2017 contribution
largest block contribution
```

Structural

```
score distribution
75+ count
80+ count
85+ count
90+ count
```

13. Do not select simply by maximum backtest result
The winning formula must not be:
whichever weight combination has the highest t_IC / highest return.
We already learned from earlier research that searching many configurations can manufacture apparent winners.
Therefore H023 must explicitly correct for the weight search itself.
14. Search-level null calibration
Before promoting any weight combination, run a multiple-testing-aware null calibration.
Use the same identity-tethering principle used in H022.
But in each null world:
evaluate the entire weight grid, exactly as the real optimiser will.
For null world `j`:

1. break own-stock score components ↔ own-stock future returns using the frozen identity-tether method;
2. evaluate every `(wT,wF,wS)` candidate;
3. calculate every candidate's `t_IC`;
4. record:


```
max_t_IC_across_entire_grid
```

This produces the distribution of what the best-looking weight combination looks like when no true signal exists.
15. Number of optimiser null worlds
Use:

```
5,000 optimiser null worlds
```

unless QuantConnect infrastructure makes this materially infeasible.
If infeasible:
STOP and report expected cost/runtime.
Do not silently reduce the number.
16. Search-adjusted development significance threshold
Calculate:

```
c_SEARCH =
max(
    empirical 99th percentile of
    max_t_IC_across_grid under the null,
    2.326
)
```

Use the same frozen one-sided empirical order-statistic convention as previous research.
This is a development/search threshold, not the eventual 2018–2021 validation threshold.
17. Development qualification filters
A candidate configuration is development-qualified only if all of these hold on 2011–2017:
D1 — search-adjusted signal

```
t_IC > c_SEARCH
AND
mean IC > 0
```

D2 — economic direction

```
80+ annualised demeaned return >= +3.0%
```

D3 — score ordering

```
quintile monotonicity >= 0.90
AND
Q5 > Q1
```

D4 — temporal stability

```
first half IC > 0
second half IC > 0
no calendar block > 50% of summed IC
```

D5 — usable 80+ population
Require:

```
80+ stocks exist in at least 60 of the 83 development months
AND
mean number of 80+ stocks >= 2 / month
```

Do not change these criteria after seeing the results.
18. Plateau requirement
A single isolated winning configuration is not enough.
Define grid adjacency as:
one 5-point transfer between two layers while the third is unchanged.
Examples:

```
40/45/15 → 45/40/15
40/45/15 → 40/50/10
```

A candidate must belong to a connected robust plateau.
A plateau is a connected set of at least:

```
4 configurations
```

where every member satisfies:

```
mean IC > 0
80+ annualised excess > 0
Q5 > Q1
both halves IC > 0
```

and its `t_IC` is at least:

```
80% of the highest t_IC
within that connected region
```

Do not use one sharp isolated optimum.
19. Final configuration selection rule
If multiple robust plateaus exist:

1. choose the plateau with the largest number of configurations;
2. tie-break by highest median t_IC across the plateau;
3. next tie-break by highest median 80+ annualised excess;
4. within the winning plateau choose its L1 medoid in weight space — the configuration with the smallest total weight-distance to other plateau members;
5. tie-break by higher t_IC;
6. final tie-break by smallest L1 distance to the original:


```
40 / 45 / 15
```

Do not manually choose a nicer-looking configuration.
20. If the maximum result does not belong to the chosen plateau
That is acceptable.
The objective is:
robustness, not the historical maximum.
Report both:

```
absolute best historical configuration
```

and:

```
pre-registered selected robust configuration
```

They may differ.
21. Weight-surface analysis
Produce a full map of the weight surface.
Report how performance changes as we move across:

```
Technical weight
Fundamental weight
Sector weight
```

At minimum show:

* `t_IC`;
* mean IC;
* 80+ excess;
* monotonicity;
* stability;
* pass/fail state.

We need to know whether the result is:

```
broad plateau
```

or:

```
sharp isolated peak
```

22. Layer-specific conclusions
After the search, report only descriptive conclusions such as:

```
higher technical weights generally helped/hurt
higher fundamental weights generally helped/hurt
sector weight appeared useful/useless
```

Do not launch another search based on these observations.
Any expanded or feature-level search requires a new owner-approved checkpoint.
23. Walk-forward diagnostic
As a robustness diagnostic, run an expanding-window exercise:

```
train through 2013 → select weights by the frozen H023 rule → observe 2014
train through 2014 → select → observe 2015
train through 2015 → select → observe 2016
train through 2016 → select → observe 2017
```

This is not the final validation.
It is only a diagnostic of whether the optimisation repeatedly chooses a similar region and whether the selected region completely collapses one year later.
Report:

* selected weights per fold;
* distance between fold selections;
* following-year IC;
* following-year 80+ excess;
* aggregate pseudo-OOS IC.

Do not use these results to redefine the search after the fact.
24. Final Score v2 candidate
If a robust plateau and development-qualified configuration exist, create:
Score v2 Candidate
with exact weights:

```
Technical = ?
Fundamental = ?
Sector = ?
```

Do not call it validated.
Its status should be:

```
DEVELOPMENT CANDIDATE — NOT YET VALIDATED
```

25. Freeze the candidate before touching 2018–2021
If H023 produces a candidate, pin:

* exact weights;
* formula;
* all existing layer hashes;
* Data v2 manifest;
* training period;
* search grid;
* optimiser-null hash;
* `c_SEARCH`;
* plateau definition;
* selected plateau;
* selection rule;
* final candidate hash.

Commit and merge this before accessing 2018–2021.
26. Pre-register the future 2018–2021 validation now
Before seeing 2018–2021, permanently record the future validation protocol.
Primary response remains one month.
Primary statistic remains:

```
monthly Spearman IC
Newey-West lag 2
```

Future validation gates:
V1 — significance
Before the real 2018–2021 mapping, run a fresh identity-tethered null calibration on that frozen validation panel and pin:

```
c_IC_VALIDATION
```

Then:

```
real t_IC > c_IC_VALIDATION
AND
mean IC > 0
```

V2 — economic

```
80+ annualised demeaned return >= +3.0%
```

V3 — monotonicity

```
quintile Spearman >= 0.90
AND
Q5 > Q1
```

V4 — stability
For 2018–2021:

```
2018–2019 mean IC > 0
2020–2021 mean IC > 0
```

and no single calendar year may contribute more than:

```
50%
```

of total summed IC.
All four must pass.
27. The validation result will be binary
When eventually opened:

```
V1 + V2 + V3 + V4 all PASS
```

means:

```
H023 VALIDATED
```

Any failure means:

```
H023 NOT VALIDATED
```

No tuning after seeing 2018–2021.
28. 2/3-month horizons remain diagnostic
Do not switch primary horizon based on training results.
For both development and eventual validation:

```
1 month = PRIMARY
2 months = diagnostic
3 months = diagnostic
```

A strong 2/3-month result cannot rescue a failed primary test.
29. No portfolio optimisation yet
Do not optimise:

* K;
* Entry;
* Exit;
* regime limits;
* sector cap;
* replacement buffer;
* position size;
* holding period;
* costs.

Those remain frozen.
H023 is a Score-weight experiment only.
30. No terminal-wealth optimisation yet
Do not choose weights based on:

* CAGR;
* SPY outperformance;
* terminal wealth;
* Sharpe;
* max drawdown.

The current stage asks whether the weighted score contains predictive information.
Portfolio economics come only after a Score v2 survives untouched forward validation.
31. If no candidate survives
If no configuration:

* beats the search-adjusted threshold;
* passes the development gates;
* and belongs to a robust plateau;

then conclude:

```
H023 — NO ROBUST SCORE V2 CANDIDATE
```

Do not:

* widen the grid;
* change the horizon;
* change the 80 threshold;
* optimise feature-level weights;
* remove Sector;
* add indicators;

without a new explicit owner decision.
32. If a candidate does survive
STOP after freezing it.
Do not open 2018–2021 yet.
Return for owner approval to begin the external validation stage.
33. Required checkpoint
Create:
P8-CP1 — H023 Score v2 Weight Optimization
Include at minimum:

1. Owner decision ID.
2. Confirmation H022 remains rejected.
3. Frozen Data v2 manifest.
4. Training period.
5. Confirmation 2011–2017 is now development data.
6. Exact Score v2 formula.
7. Weight grid.
8. Number of configurations.
9. Confirmation only layer weights changed.
10. Original 40/45/15 result as control.
11. Metrics for every configuration.
12. Optimiser-null method.
13. Number of null worlds.
14. Optimiser-null distribution.
15. `c_SEARCH`.
16. Highest real t_IC.
17. Search-adjusted percentile/p-value.
18. Number of development-qualified configurations.
19. Number of robust plateaus.
20. Plateau membership.
21. Plateau sizes.
22. Weight-surface summary.
23. Absolute-best configuration.
24. Pre-registered selected configuration.
25. Reason selection differs, if applicable.
26. Selected Technical weight.
27. Selected Fundamental weight.
28. Selected Sector weight.
29. Selected mean IC.
30. Selected t_IC.
31. Selected 80+ annualised excess.
32. Selected quintile results.
33. Selected monotonicity.
34. Selected first/second-half IC.
35. Selected yearly ICs.
36. Selected block concentration.
37. 80+ population coverage.
38. Walk-forward fold selections.
39. Walk-forward pseudo-OOS results.
40. Whether fold weights cluster.
41. Whether a stable plateau exists.
42. Candidate Score v2 hash if one exists.
43. Candidate freeze commit if one exists.
44. Pre-registered 2018–2021 validation protocol.
45. Confirmation 2018–2021 untouched.
46. Confirmation Holdout untouched.
47. Confirmation no portfolio optimisation.
48. Confirmation no feature definition changed.
49. Confirmation nothing purchased.
50. Final result:


```
DEVELOPMENT CANDIDATE — SCORE V2 FROZEN, VALIDATION STILL SEALED
```

or:

```
NO ROBUST SCORE V2 CANDIDATE
```

51. Exact next owner decision.

34. Important interpretation
We are deliberately using 2011–2017 to learn the weights.
Therefore:
A fantastic 2011–2017 result is not evidence that Score v2 works out of sample.
It is only evidence that the optimisation found a candidate worth testing.
The real evidence will come from:

```
2018–2021
```

which must remain untouched until the formula is frozen.
35. Final STOP
After P8-CP1:
STOP.
Do not:

* access 2018–2021;
* access the Holdout;
* alter the selected weights;
* optimise internal feature weights;
* optimise threshold 80;
* optimise horizon;
* optimise portfolio mechanics.

Return the full training/search result for owner review.
