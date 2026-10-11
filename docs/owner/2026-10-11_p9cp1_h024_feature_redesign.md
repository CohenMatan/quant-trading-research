# Owner message 2026-10-11: "Phase 9 — H024 Feature Redesign and Selection. Develop on 2011–2017, Keep 2018–2021 and Holdout Sealed"

Decision id: **D201** (closes H023 as NO ROBUST SCORE V2 CANDIDATE and approves H024). Recorded and committed BEFORE any H024 feature value, null world or return is computed. The owner's message follows verbatim.



---



Phase 9 — H024
Feature Redesign and Selection
Develop on 2011–2017, Keep 2018–2021 and Holdout Sealed
Continue from:
P8-CP1 — H023 Score v2 Weight Optimization
Owner decision:
Close H023 as NO ROBUST SCORE V2 CANDIDATE.
H022 remains rejected and H023 remains closed exactly as tested.
I now approve a new hypothesis:
H024 — Feature Redesign and Selection
The purpose is to determine whether the failure came from the information contained in Score v1, rather than merely from its layer weights.
For H024:

```
2011–2017 = DEVELOPMENT / TRAINING DATA
2018–2021 = SEALED VALIDATION
2022–2026 = SEALED HOLDOUT
```

We are now allowed to change the score's feature composition, but only under a tightly pre-registered search architecture.
1. Research question
Answer:
Can a small, interpretable set of point-in-time features, constructed from the existing approved data infrastructure, produce a robust cross-sectional predictor of next-month stock returns during 2011–2017 that is strong enough to justify one untouched validation on 2018–2021?
The objective is not to create the best historical backtest.
The objective is to identify a feature set whose signal is:

* statistically meaningful;
* economically meaningful;
* temporally stable;
* not dependent on one feature;
* not dependent on one year;
* not an isolated search winner;
* simple enough to freeze before forward validation.

2. Preserve all previous failures
Do not reinterpret previous research.
Permanent records remain:

```
H022 — Score v1:
REJECTED

H023 — Score v2 layer-weight optimisation:
NO ROBUST SCORE V2 CANDIDATE
```

H023's best `80/10/10` result is not a candidate and must not be promoted.
Do not extend the H023 weight grid.
Do not search Technical weights above 80 as part of H024.
3. Data Infrastructure v2 remains frozen
Use frozen Data Infrastructure v2 unchanged.
Do not change:

* universe;
* SEC market-cap repair;
* M2 timing;
* identity handling;
* restatement guard;
* security-life rules;
* share-class rules;
* price adjustment;
* corporate-action handling;
* monthly review calendar;
* next-open timing.

No Data v3.
4. Keep the prediction target fixed
Primary prediction target remains:

```
next-session open after review t
→
next monthly review close
```

Primary response:

```
stock total shareholder return
-
equal-weight return of the eligible population
```

Primary horizon:

```
1 month
```

Do not optimise the horizon.
2-month and 3-month results may be diagnostics only.
5. First step — inventory the existing Score v1 features
Before proposing anything new, create a complete feature inventory from the repository.
For every Score v1 feature record:

* feature name;
* exact formula;
* source data;
* PIT timing;
* lookback;
* transformation/bands;
* Technical/Fundamental/Sector family;
* correlation/redundancy with other features;
* whether prior research tested the same economic idea independently;
* Data v2 coverage.

Do not rely on memory or descriptions.
Read the actual frozen implementation.
6. Existing features may be removed
Unlike H023, H024 may remove Score v1 features.
But removal must happen through the pre-registered feature-selection process.
Do not remove a feature simply because its observed 2011–2017 return contribution looks bad after the fact.
7. New-feature eligibility
A new feature may enter the H024 library only if all of these are true:

1. There is a clear economic or behavioural rationale.
2. It can be constructed PIT-safely from data already available under Data v2 or from free public data that can be independently verified.
3. It has sufficient 2011–2017 coverage.
4. Its exact formula can be specified before its real H024 result is calculated.
5. It does not require 2018–2021 or Holdout data.
6. It does not require a new paid dataset.

8. Evidence before feature testing
Before calculating H024 real returns, use:

* existing project research;
* public academic literature where helpful;
* documentation/source code;
* economic rationale;

to propose the candidate feature library.
Do not use a broad automated indicator generator.
Do not create hundreds of arbitrary transformations.
9. Feature-search budget
Freeze a limited library before any H024 real feature result is computed.
Target:

```
maximum 15 candidate features total
```

including surviving Score v1 features and new features.
If more than 15 defensible candidates exist:
rank them based on prior evidence, interpretability, PIT quality and non-redundancy before looking at H024 returns, and retain at most 15.
Do not increase this limit after seeing results.
10. Feature families
Organise candidates into economically meaningful families.
Examples of acceptable families include, where Data v2 supports them safely:

```
Momentum / trend
Volatility / risk
Profitability
Cash-flow quality
Growth
Investment / asset growth
Balance-sheet strength
Valuation
Capital issuance / shareholder yield
Sector-relative information
```

These are conceptual examples, not automatic requirements.
Do not include a feature merely to fill every family.
11. Avoid duplicate signals
Do not treat minor variants of one signal as independent discoveries.
Examples:

```
momentum 11 months
momentum 12 months
momentum 13 months
```

should normally count as one feature family rather than three independent ideas.
Likewise avoid dozens of nearby lookbacks.
For any new feature requiring a lookback choice:
choose one economically justified specification before testing real H024 returns.
12. No continuous parameter optimisation
Do not optimise:

* lookbacks;
* clipping thresholds;
* winsorisation levels;
* decay constants;
* smoothing windows;

against 2011–2017 returns.
Parameters must be chosen ex ante from the feature definition.
H024 is feature selection, not unrestricted formula optimisation.
13. Standardise features cross-sectionally
For model construction, convert each eligible raw feature to a comparable cross-sectional score.
Preferred architecture:

```
within each review date:
    rank valid stocks by feature
    convert rank to percentile [0,1]
```

Direction must be defined before results:

```
higher-is-better
or
lower-is-better
```

Do not flip a feature's direction after seeing its return relationship.
If economic theory genuinely leaves direction ambiguous:
exclude it or pre-register both directions as two search candidates and count both in multiple-testing correction.
14. Missing data
Do not impute information using future observations.
Pre-register the missing-value rule.
Prefer:

```
model is calculated only when all features required by that model are valid
```

unless an already-approved PIT-safe alternative exists.
Report coverage for every feature and every candidate model.
15. Stage A — individual feature evaluation
For all pre-registered features calculate on 2011–2017:

```
monthly Spearman IC
mean IC
Newey-West t_IC, lag 2
positive-month fraction
IC by year
first-half / second-half IC
quintile responses
Q5-Q1
monotonicity
coverage
```

Also calculate pairwise feature rank correlations.
This stage is descriptive/search input.
Do not declare a feature valid merely from its unadjusted t-statistic.
16. Feature-level multiple-testing correction
Run:

```
5,000 identity-tethered null worlds
```

where every null world evaluates the entire feature library.
For each world record:

```
max absolute/appropriate one-sided feature t_IC
```

using the pre-registered direction convention.
Calculate a feature-search threshold:

```
c_FEATURE =
max(
    empirical one-sided 1% max-feature null threshold,
    2.326
)
```

Do not use ordinary `t > 2.326` without correcting for the library search.
17. Do not require every selected feature to pass c_FEATURE
`c_FEATURE` identifies individually convincing signals.
A useful multivariate model may contain complementary features that are individually weaker.
Therefore:

* report which individual features pass;
* but model construction follows the separately pre-registered model search below.

Do not cherry-pick weak features after seeing model results.
18. Redundancy control
Before building models, group highly redundant features.
If absolute cross-sectional rank correlation is consistently very high, e.g.:

```
|rho| >= 0.80
```

treat them as belonging to the same redundancy cluster.
A model may contain at most one member of a redundancy cluster unless there is a pre-specified economic reason.
Do not let ten versions of momentum dominate the search.
19. Model architecture
H024 candidate models must remain simple.
A candidate model may contain:

```
2, 3 or 4 features
```

Maximum:

```
4 features
```

No 5+ feature model in this checkpoint.
20. Model weighting
Do not optimise continuous feature weights.
For the primary H024 search:
all included features receive equal weight.
If a model contains `k` features:

```
ModelScore =
100 × mean(feature_percentiles)
```

This keeps the output on a 0–100 scale without another weight optimiser.
Do not use regression-fitted coefficients.
Do not use machine learning.
Do not use neural networks, trees, boosting, random forests or Bayesian optimisation.
21. Candidate model library
Generate every model satisfying:

* 2–4 features;
* features come from the frozen H024 library;
* at most one feature from each redundancy cluster;
* no explicitly incompatible feature combination defined during pre-registration.

Freeze the complete candidate-model list and its hash before evaluating model returns.
Report how many models exist.
If the combinatorial search exceeds:

```
500 candidate models
```

STOP before real evaluation and reduce the feature library using pre-registered non-return criteria.
Do not test thousands of models.
22. Model score threshold
Because candidate scores are percentile averages on a 0–100 scale, use:

```
Score >= 80
```

for the economic high-score group.
Do not optimise the threshold.
Also calculate quintiles independently of the 80 threshold.
23. Metrics for every model
Calculate:
Signal

```
mean monthly IC
Newey-West t_IC
```

High-score economic effect

```
80+ mean monthly demeaned return
80+ annualised demeaned return
number of 80+ stocks/month
```

Ordering

```
Q1-Q5 returns
Q5-Q1
quintile Spearman
```

Stability

```
first half IC
second half IC
IC by year
calendar block contributions
```

Coverage

```
stock-months
stocks/month
80+ months
```

24. Full-search null calibration
The key anti-overfitting test:
Run:

```
5,000 model-search null worlds
```

In every null world:

1. preserve the full historical panel;
2. break own features/score ↔ own future return through the frozen identity-tethered method;
3. evaluate the entire candidate model library;
4. apply the exact real-model selection procedure;
5. record the best null model's statistic.

At minimum record:

```
max t_IC across candidate models
```

and preferably the complete promotion rule result.
25. Search-adjusted model threshold
Calculate:

```
c_MODEL =
max(
    empirical 99th percentile of
    max t_IC across all models in each null world,
    2.326
)
```

Use the same empirical order-statistic convention as earlier phases.
Pin `c_MODEL` before the one real model search.
26. Development qualification gates
A model becomes development-qualified only if all of these pass.
D1 — Search-adjusted significance

```
t_IC > c_MODEL
AND
mean IC > 0
```

D2 — Economic magnitude

```
80+ annualised demeaned return >= +3.0%
```

D3 — Ordering

```
quintile Spearman >= 0.90
AND
Q5 > Q1
```

D4 — Temporal stability

```
first-half IC > 0
second-half IC > 0
no calendar block > 50% of summed IC
```

D5 — Coverage

```
at least 60 of 83 months contain 80+ stocks
mean 80+ count >= 2 per month
```

D6 — No single-feature dependence
For every feature in the model, remove it and recompute the model.
The model fails D6 if removing one feature destroys essentially the entire signal.
Pre-register a precise criterion before seeing real model results.
Suggested rule:

```
every leave-one-feature-out model must retain:
mean IC > 0
and
at least 40% of the full model's mean IC
```

Freeze the exact rule before the real search.
27. Robust-neighbourhood requirement
Do not accept an isolated feature combination.
For a selected `k`-feature model, define neighbours as models formed by replacing one included feature with another pre-registered feature from a different non-redundant cluster while keeping model size fixed.
Require evidence that the surrounding feature region is not entirely dead.
Pre-register a simple neighbourhood rule before the real search, for example:

```
at least 3 neighbouring models must have:
mean IC > 0
80+ excess > 0
Q5 > Q1
```

Do not invent the rule after seeing the winner.
28. Selection rule
If multiple models qualify:

1. prefer the smallest model size;
2. then highest median `t_IC` among its robust neighbourhood;
3. then highest model `t_IC`;
4. then highest 80+ excess;
5. final deterministic tie-break by sorted feature IDs/names.

Do not manually pick the model that "looks best".
Simplicity wins over a tiny historical improvement.
29. Walk-forward diagnostic
Run an expanding-window diagnostic:

```
2011–2013 development → evaluate selected model in 2014
2011–2014 development → evaluate in 2015
2011–2015 development → evaluate in 2016
2011–2016 development → evaluate in 2017
```

At each fold:

* apply the same frozen feature/model-selection rule;
* do not manually intervene.

Report:

```
selected features per fold
feature overlap
following-year IC
following-year 80+ excess
pseudo-OOS aggregate IC
```

A stable H024 candidate should not select a completely unrelated model every fold.
30. Feature-selection stability
Report how frequently each feature appears in:

* qualifying models;
* top 10 models;
* walk-forward fold selections.

We want to distinguish:

```
stable useful feature
```

from:

```
feature that appears only in one historical optimum
```

31. Existing Score v1 as controls
Include as controls:

```
original Score v1
best H023 80/10/10 layer weighting
```

for descriptive comparison only.
They remain failed hypotheses.
They cannot become H024 candidates.
32. Boundary / search-expansion rule
If the strongest H024 model suggests an omitted neighbouring feature/lookback/variant:
do not add it.
Report the observation and STOP.
Any expanded library becomes H025 or another explicitly approved hypothesis.
33. No second H024 search
H024 gets:

* one frozen feature library;
* one frozen model library;
* one null calibration;
* one real development search.

Do not perform:

```
H024 v1
H024 v2
H024 v3
```

until something works.
If it fails, H024 fails.
34. If a candidate survives
Create:
H024 Score v3 Candidate
Use a new version name to avoid confusing it with the failed Score v1 / H023 weight experiment.
Status:

```
DEVELOPMENT CANDIDATE
NOT YET VALIDATED
```

Freeze:

* exact feature set;
* exact feature formulas;
* directions;
* transformations;
* missing-value rules;
* equal-weight rule;
* score construction;
* threshold 80;
* Data v2 manifest;
* `c_MODEL`;
* candidate-model library hash;
* development result;
* walk-forward result.

35. Pre-register 2018–2021 validation before opening it
If and only if H024 yields a development candidate:
prepare the future validation protocol before accessing 2018–2021.
Validation uses exactly the frozen H024 candidate.
No feature reselection.
No weight changes.
No threshold changes.
No formula changes.
36. Data extension for 2018–2021
Current frozen Data v2 reference coverage ends at 2017.
Therefore do not access 2018–2021 automatically.
If a candidate exists, first return to the owner with a separate proposal to extend the same frozen PIT infrastructure through 2021.
That extension must itself be audited and frozen before validation.
Do not intermingle infrastructure extension with observing validation returns.
37. Future validation gates
Pre-register now the conceptual validation requirements.
Once a 2018–2021 panel is safely frozen:
V1
Fresh panel-specific identity-tethered null calibration, pinned before the real mapping:

```
real t_IC > c_IC_VALIDATION
AND
mean IC > 0
```

V2

```
80+ annualised demeaned return >= +3.0%
```

V3

```
quintile Spearman >= 0.90
AND
Q5 > Q1
```

V4

```
2018–2019 mean IC > 0
2020–2021 mean IC > 0
```

plus the pre-registered concentration rule.
All must pass.
38. Validation remains one-shot
If H024 reaches validation:

```
one frozen candidate
one frozen validation panel
one real validation
```

No post-validation tuning.
Failure ends H024.
39. Holdout remains completely untouched
Do not access:

```
2022-01-01 → 2026-08-31
```

during any H024 development or infrastructure work.
40. No portfolio research
Do not optimise or evaluate:

* Entry/Exit;
* K;
* sector cap;
* regime limits;
* turnover;
* holding period;
* position sizing;
* transaction-cost P&L;
* terminal wealth;
* CAGR;
* Sharpe;
* drawdown;
* SPY outperformance.

First establish whether the new feature set predicts returns.
41. No machine-learning escalation
If simple feature combinations fail, do not automatically move to:

* neural networks;
* gradient boosting;
* random forests;
* genetic algorithms;
* AutoML;
* unrestricted regressions.

That would be a new research programme requiring separate approval.
42. Required run order
Use this order:

```
1. Inventory existing features
2. Design new feature library
3. Freeze feature library
4. Freeze all formulas/directions/parameters
5. Freeze candidate-model library
6. Canary
7. Feature-search null calibration
8. Model-search null calibration
9. Pin c_FEATURE and c_MODEL
10. One real H024 development search
11. Apply frozen qualification + selection rule
12. Walk-forward diagnostic
13. Freeze candidate if one exists
14. STOP
```

No real H024 development result before the null thresholds are pinned.
43. Required checkpoint
Create:
P9-CP1 — H024 Feature Redesign and Selection
Include at minimum:

1. Owner decision ID.
2. H022 permanent result.
3. H023 permanent result.
4. Frozen Data v2 manifest.
5. Development period.
6. Confirmation 2018–2021 sealed.
7. Confirmation Holdout sealed.
8. Full Score v1 feature inventory.
9. Candidate feature library.
10. Economic rationale per feature.
11. Formula per feature.
12. Direction per feature.
13. PIT availability per feature.
14. Coverage per feature.
15. Redundancy clusters.
16. Feature-library hash.
17. Number of features.
18. Candidate-model construction rule.
19. Candidate-model count.
20. Candidate-model hash.
21. Confirmation max 4 features/model.
22. Confirmation equal weights only.
23. Canary status.
24. Feature-level null methodology.
25. `c_FEATURE`.
26. Model-search null methodology.
27. `c_MODEL`.
28. Null-world counts.
29. Null determinism check.
30. Individual-feature IC results.
31. Individual-feature search-adjusted results.
32. Full model-search results.
33. Highest historical model `t_IC`.
34. Search-adjusted percentile / p-value.
35. Number passing D1.
36. Number passing D2.
37. Number passing D3.
38. Number passing D4.
39. Number passing D5.
40. Number passing D6.
41. Number passing all gates.
42. Robust-neighbourhood results.
43. Final deterministic selected model, if any.
44. Selected feature names.
45. Selected formulas.
46. Selected mean IC.
47. Selected `t_IC`.
48. Selected 80+ annualised excess.
49. Selected quintiles.
50. Selected monotonicity.
51. Selected half-period results.
52. Selected yearly IC.
53. Selected block concentration.
54. Leave-one-feature-out results.
55. Walk-forward fold selections.
56. Walk-forward feature overlap.
57. Walk-forward pseudo-OOS IC.
58. Walk-forward economic result.
59. Comparison with Score v1.
60. Comparison with H023 80/10/10 control.
61. Candidate freeze hash if applicable.
62. Confirmation no parameter was added after seeing results.
63. Confirmation no portfolio was evaluated.
64. Confirmation 2018–2021 untouched.
65. Confirmation Holdout untouched.
66. Confirmation nothing purchased.
67. Final result:


```
DEVELOPMENT CANDIDATE — H024 SCORE FROZEN, VALIDATION SEALED
```

or:

```
NO ROBUST H024 FEATURE MODEL
```

68. Exact next owner decision.

44. If no model survives
STOP.
Do not:

* add more features;
* alter feature formulas;
* search more lookbacks;
* add feature weights;
* change threshold 80;
* switch horizon;
* run machine learning;
* access 2018–2021.

Return the negative result.
45. If a model survives
Freeze it and STOP.
Do not open 2018–2021.
The owner must separately approve:

1. extension of the frozen Data v2 infrastructure through 2021;
2. validation null calibration;
3. exactly one real validation.

46. Final principle
2011–2017 is now deliberately being used to learn.
Therefore an excellent H024 development result is not proof of an edge.
We are only looking for:
a sufficiently simple, stable, multiple-testing-adjusted candidate worth risking our untouched 2018–2021 validation set on.
The real test remains ahead.
