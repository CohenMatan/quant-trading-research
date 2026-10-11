# Owner message 2026-10-11: "Phase 11 — H026 Learned Stock Score → Top-15 Portfolio → Beat SPY"

Decision id: **D206** (closes H025 / Phase 10 as REJECTED — NO ROBUST INSIDER-CLUSTER EDGE and approves H026). Recorded and committed BEFORE any Data v2.1 build, H026 model, null world or return is computed. The owner's message follows verbatim.

---

Phase 11 — H026
Learned Stock Score → Top-15 Portfolio → Beat SPY
Ridge-Learned Interpretable Score, Walk-Forward Development, Final Holdout Still Sealed
Continue from:
P10-CP1 — H025 Insider Cluster Buying
Owner decision:
Close H025 / Phase 10 as REJECTED — NO ROBUST INSIDER-CLUSTER EDGE.
H022, H023, H024 and H025 remain permanently closed exactly as tested.
I now approve a materially different research programme:
H026 — Learned Stock Score Portfolio
The objective is no longer primarily:
Does a manually designed Score have a high next-month IC?
The economic objective is now:
Can an interpretable, data-learned stock Score construct a long-only portfolio that ends with materially more wealth than SPY, after realistic costs, without unacceptable additional risk?
The final target is portfolio performance versus SPY.
1. Why H026 is different
Previous work established:

```
H022:
manual Score v1 failed

H023:
92 layer-weight combinations failed

H024:
11 features / 415 equal-weight models failed

H025:
insider-cluster event hypothesis failed
```

Do not reopen those hypotheses.
H026 differs in three important ways:

```
1. weights are learned statistically rather than manually chosen;
2. the score is evaluated through an actual portfolio;
3. terminal wealth versus SPY is the primary economic objective.
```

2. H026 is not permission for unlimited machine learning
Use one simple, interpretable model family:
Ridge regression
Do not use:

```
neural networks
random forests
gradient boosting
XGBoost
LightGBM
AutoML
genetic algorithms
Bayesian optimisation
deep learning
```

Do not add another model class after seeing Ridge results.
If Ridge fails, H026 fails.
Any other learning architecture requires H027 or later.
3. Existing feature library only
For H026 use exactly the 11 already pre-registered H024 features:

```
MOM
LOWVOL
GPA
ACC
BM
AG
REV1M
CBOP
HI52
CFP
EQA
```

Use their H024 PIT-safe formulas unchanged.
Do not add:

* analyst estimates;
* earnings surprises;
* new momentum horizons;
* new valuation ratios;
* sector breadth;
* new technical indicators;
* interactions;
* polynomial features.

The purpose of H026 is to answer:
Can learned continuous weights + portfolio construction extract something that the previous manual/equal-weight searches missed?
4. Development period changes formally
For H026 redefine:

```
2011–2021 = DEVELOPMENT DATA
```

This is intentional.
2018–2021 must no longer be described as untouched validation for H026.
It has already been exposed by some earlier unrelated work and will now explicitly become part of the H026 development process.
Permanent disclosure:

```
2011–2021:
H026 DEVELOPMENT / MODEL-SELECTION DATA

2022-01-01 → 2026-08-31:
PROGRAMME-WIDE FINAL HOLDOUT
STILL SEALED
```

Do not access any 2022+ data.
5. Infrastructure extension comes first
Current frozen Data v2 infrastructure ends in 2017.
Before H026 modelling, extend the same PIT rules through:

```
2021-12-31
```

Create a versioned infrastructure extension, e.g.:

```
Data v2.1
```

This is an extension, not a redesign.
Do not modify historical 2011–2017 rules.
The following must remain conceptually identical:

```
universe definition
SEC market-cap repair
M2 timing
identity handling
restatement protection
share-class rule
corporate-action handling
review calendar
price / ADV rules
```

6. Data-extension integrity gate
Before computing any H026 model result, verify Data v2.1.
Report separately for:

```
2011–2017
2018
2019
2020
2021
```

At minimum:

* eligible stock-months;
* number of securities;
* survivor share;
* PIT audit;
* market-cap repair;
* identity coverage;
* fundamental coverage;
* feature coverage;
* corporate-action integrity;
* deterministic rebuild;
* truncation/future-invariance where applicable.

2011–2017 must reproduce the frozen historical H024/H022 population where expected.
If Data v2.1 changes the historical analysed population materially:
STOP.
Do not silently continue.
7. Freeze Data v2.1 before model research
Pin:

```
Data v2.1 manifest
reference hashes
review-calendar hash
feature-panel digest
actual LEAN build
```

before any real H026 learning result is computed.
The 2022–2026 Holdout must not be included in Data v2.1.
8. Feature representation
For every monthly review and every eligible stock, calculate the 11 H024 raw feature values using the existing frozen formulas.
Convert each feature independently within that review date to a percentile:

```
pct_i ∈ [0,1]
```

Then center:

```
x_i = 2 * pct_i - 1
```

Therefore:

```
x_i ∈ [-1,+1]
```

Do not pre-orient the variables as “good” or “bad”.
Ridge is allowed to learn either:

```
positive coefficient
or
negative coefficient
```

for each feature.
This is important.
9. Missing values
Primary rule:
A stock is model-eligible only when all 11 H026 features are valid at that review date.
Do not future-fill.
Do not interpolate fundamentals.
Do not perform return-informed imputation.
Report coverage.
If this unexpectedly removes a material fraction of the universe, STOP and report before altering the rule.
10. Prediction target
The model target is not one-month return.
Use:

```
63 trading-session forward total shareholder return
```

from:

```
next-session open after review
→
63rd trading-session close
```

Primary target before ranking:

```
stock TSR - SPY TSR
```

over the identical interval.
Then, within each review date, convert that forward excess return to its cross-sectional percentile rank:

```
y ∈ [-1,+1]
```

using the same:

```
2 * percentile - 1
```

mapping.
Thus the model learns:
Which stocks are likely to rank near the top of the cross-section over approximately the next three months?
11. Critical label-availability rule
A training observation may be used only after its full 63-session response is known.
At model-training timestamp `T`, include an observation only if:

```
response_exit_timestamp < T
```

No partially realised label.
No overlap leakage.
No label whose exit lies after the training cutoff.
This must be explicitly tested.
12. Equal weight by review date in model fitting
The number of eligible stocks changes through time.
Do not allow later months with larger universes to dominate the regression.
For model fitting:
Give each monthly review date equal total statistical weight.
Within a month containing `N_t` stocks:

```
observation weight = 1 / N_t
```

so every review month contributes equal aggregate weight.
13. Ridge model
Fit:

```
y =
β0
+ β1*MOM
+ β2*LOWVOL
+ β3*GPA
+ β4*ACC
+ β5*BM
+ β6*AG
+ β7*REV1M
+ β8*CBOP
+ β9*HI52
+ β10*CFP
+ β11*EQA
+ error
```

with L2 regularisation.
All 11 features remain in the model.
Do not perform subset selection.
Do not zero/remove features manually.
14. Ridge hyperparameter grid
Pre-register exactly:

```
λ ∈ {
    0.01,
    0.1,
    1,
    10,
    100
}
```

No additional values.
Do not widen the grid after seeing results.
15. Outer walk-forward
Primary H026 development evidence must be genuinely chronological.
Use:

```
2011–2014 → test 2015
2011–2015 → test 2016
2011–2016 → test 2017
2011–2017 → test 2018
2011–2018 → test 2019
2011–2019 → test 2020
2011–2020 → test 2021
```

Remember:
Training rows must also satisfy the 63-session label-availability rule.
16. Hyperparameter selection happens inside each outer fold
For each outer test year:

1. use only data available before that year;
2. perform expanding-window inner validation;
3. evaluate all five λ values;
4. choose λ without seeing the outer test year;
5. refit using all allowable pre-test data;
6. freeze coefficients for the entire outer test year.

No monthly coefficient refitting inside the outer year.
17. Inner-fold objective
Hyperparameter selection must align with the actual portfolio objective.
For each λ, simulate its inner walk-forward Top-15 portfolio and calculate:

```
log(
    terminal wealth of strategy
    /
    terminal wealth of SPY
)
```

after costs.
Select the λ with the highest compounded relative terminal wealth across the inner validation folds.
Tie-break deterministically:

```
1. better worst validation-year relative return
2. larger λ (stronger regularisation)
3. numeric λ ordering
```

Do not use the outer test year for λ selection.
18. Model Score
For each eligible stock at review date:

```
raw_prediction =
β0 + Σ β_i*x_i
```

Convert predictions within that review to:

```
Score_H026 = percentile rank(raw_prediction) * 100
```

So:

```
0 = lowest predicted rank
100 = highest predicted rank
```

This gives an interpretable stock Score.
19. Portfolio construction
Primary portfolio:

```
Starting capital: $100,000
Long only
No leverage
Maximum positions: 15
Equal-weight selected positions
Maximum initial weight per position: 10%
Monthly review
Orders: next session open
```

Select the highest-scoring eligible stocks subject to:

```
maximum 3 stocks per FF12 sector
```

Continue down the ranking until 15 slots are filled where possible.
If fewer than 15 eligible slots satisfy constraints:

```
hold residual cash
```

20. Rebalancing
At every monthly review:
Reconstitute the portfolio to the current Top-15 constrained ranking.
No:

```
entry threshold
exit threshold
replacement buffer
stop loss
take profit
manual hold rule
```

H026 should isolate the quality of the learned Score.
Do not optimise portfolio mechanics.
21. Costs
Use the already frozen real-world assumptions:

```
$7 per executed BUY
$7 per executed SELL

slippage:
0.10% per side
```

No borrowing.
No leverage.
Primary capital:

```
$100,000
```

Secondary non-gating sensitivity:

```
$200,000
```

22. SPY benchmark
Benchmark:
Buy and hold SPY over the exact same outer walk-forward period.
Use total return including dividends.
Apply the same realistic assumptions to SPY entry/exit:

```
commission
slippage
```

Primary comparison period:

```
first 2015 portfolio entry
→
final 2021 portfolio liquidation
```

Both portfolios must start with identical capital at the identical timestamp.
23. Primary objective
The primary H026 economic objective is:

```
Terminal Wealth H026
>
Terminal Wealth SPY
```

after all trading costs.
Primary statistic:

```
S_WEALTH =
ln(
    terminal wealth H026
    /
    terminal wealth SPY
)
```

Positive means H026 wins.
24. Required portfolio metrics
Report at minimum:

```
terminal wealth
CAGR
excess CAGR vs SPY
annualised volatility
Sharpe
Max Drawdown
time underwater
monthly turnover
annual turnover
number of trades
total commissions
total slippage
average number of holdings
cash utilisation
sector concentration
```

For both H026 and SPY where meaningful.
25. Results by outer year
For every outer year 2015–2021 report:

```
selected λ
11 learned coefficients
strategy return
SPY return
relative return
turnover
max drawdown
```

This is essential.
We need to know whether the method works repeatedly or only because of one year.
26. Coefficient stability
Report coefficient paths by outer year.
For each feature show:

```
coefficient sign by year
coefficient magnitude by year
mean coefficient
SD
number of sign flips
```

Also report correlation of coefficient vectors between adjacent years.
A candidate whose formula changes completely every year should be treated cautiously even if terminal wealth is attractive.
27. Full-pipeline null test
Before computing the real H026 outer-walk-forward result, run a multiple-testing / learning-aware null.
Use:

```
5,000 null worlds
```

if feasible on the existing infrastructure.
If 5,000 full-pipeline worlds are materially infeasible:
STOP and report estimated runtime/cost before reducing the number.
Do not silently use fewer worlds.
28. Null construction
Use the existing identity-tether principle.
For each null world:
Reassign each stock the complete feature vector of another stock through the frozen persistent identity-tether mapping, while keeping that stock's actual subsequent prices/returns attached to itself.
This breaks:

```
own features ↔ own future returns
```

while preserving:

* cross-sectional feature distributions;
* feature correlation structure;
* feature persistence;
* market environment;
* actual stock returns;
* universe composition.

Do not independently shuffle each feature.
The entire 11-feature vector moves together.
29. Every null world reruns the complete H026 process
Each world must repeat:

```
inner λ selection
outer annual Ridge fitting
annual coefficients
monthly scoring
Top-15 constrained portfolio
monthly trading
commissions
slippage
SPY comparison
```

Do not calculate a shortcut statistic.
The null must measure:
How good can this entire learned-score procedure look when the stock features contain no genuine information about their own future returns?
30. Null primary statistic
For each world record:

```
S_WEALTH_null =
ln(
    terminal wealth null strategy
    /
    terminal wealth SPY
)
```

Also preserve:

```
excess CAGR
Max Drawdown
annualised volatility
number of years beating SPY
```

as diagnostics.
31. Search/learning-adjusted wealth threshold
Set:

```
c_WEALTH =
empirical one-sided 99th percentile
of S_WEALTH_null
```

using the same order-statistic convention used in previous phases.
Pin:

```
c_WEALTH
null result hash
feature-panel digest
portfolio-engine hash
model-engine hash
all null seeds
```

before running the one real H026 walk-forward pipeline.
32. Null determinism
Rerun a pre-specified sample:

```
seeds 1–25
```

independently.
Every statistic must reproduce exactly within the expected numeric tolerance.
Otherwise:
STOP.
33. Development Gate D1 — Search-adjusted wealth
Require:

```
S_WEALTH_real > c_WEALTH
AND
S_WEALTH_real > 0
```

This is the primary statistical protection against fitting noise.
34. Development Gate D2 — Economic outperformance
Require both:

```
Terminal Wealth H026
>= 1.15 × Terminal Wealth SPY
```

and:

```
H026 CAGR - SPY CAGR
>= +2.0 percentage points / year
```

after all costs.
35. Development Gate D3 — Temporal robustness
Require:

```
H026 beats SPY in at least 5 of 7
outer test years
```

and:

```
relative compounded return 2015–2017 > 0
relative compounded return 2018–2021 > 0
```

No single year may account for more than:

```
50%
```

of total positive log-relative wealth.
36. Development Gate D4 — Balanced risk
Require:

```
|MaxDD_H026|
<=
1.25 × |MaxDD_SPY|
```

and:

```
annualised volatility H026
<=
1.25 × annualised volatility SPY
```

This allows more risk than SPY, but not unlimited risk in exchange for extra return.
37. Development Gate D5 — Cost robustness
After the primary result is fixed, rerun the exact same selections with:

```
slippage = 0.20% per side
```

Do not retrain.
Do not change λ.
Do not change coefficients.
Require:

```
Terminal Wealth stressed-cost H026
>
Terminal Wealth SPY
```

This is a robustness gate.
38. All gates required
H026 becomes a development candidate only if:

```
D1 PASS
D2 PASS
D3 PASS
D4 PASS
D5 PASS
```

No partial promotion.
39. Non-gating diagnostics
After the primary result is fixed, report:

```
$200K starting-capital sensitivity

Top-10 portfolio using same frozen scores
Top-20 portfolio using same frozen scores

sector-neutral relative performance
market-regime performance
```

These are diagnostics only.
They cannot rescue H026.
Do not refit models for them.
40. Do not optimise K
Primary:

```
K = 15
```

is frozen.
Top 10 / Top 20 are diagnostics only.
Do not choose the one with the best result.
41. Do not change the prediction horizon
Primary model target:

```
63 trading sessions
```

Do not try:

```
21
42
84
126
```

after seeing H026.
A different target becomes H027.
42. Do not change the feature library
If H026 fails:
Do not:

```
remove bad coefficient features
add analyst data
add interactions
add new price features
flip formulas
change transformations
```

inside H026.
That requires a new hypothesis.
43. Final model creation if H026 passes
Only if D1–D5 all pass:
Use the entire H026 development period to select the final λ with the exact same inner walk-forward selection procedure.
Use all training observations whose 63-session labels are fully known by:

```
2021-12-31
```

No label may cross into 2022.
Fit one final Ridge model.
Record:

```
final λ
β0
β_MOM
β_LOWVOL
β_GPA
β_ACC
β_BM
β_AG
β_REV1M
β_CBOP
β_HI52
β_CFP
β_EQA
```

This becomes the exact frozen H026 Score formula.
44. Final formula must be fixed for Holdout
For the eventual 2022–2026 Holdout:
Do not retrain annually.
The frozen end-of-2021 coefficients are the formula.
At every future monthly review:

```
calculate the 11 PIT features
transform to monthly percentiles
apply frozen coefficients
rank stocks
buy constrained Top 15
```

No parameter changes.
This gives us a clean test of whether the learned formula genuinely generalises.
45. Freeze candidate before Holdout
If H026 passes development, pin:

```
Data v2.1 manifest
feature formulas
feature-panel hash
prediction target
λ grid
selected final λ
all final coefficients
portfolio rules
cost rules
c_WEALTH
development result
null result
final score-code hash
```

Status:

```
H026 DEVELOPMENT CANDIDATE
FROZEN
FINAL HOLDOUT NOT RUN
```

46. Holdout remains completely sealed
Do not access:

```
2022-01-01 → 2026-08-31
```

during:

* Data v2.1 development;
* model training;
* null calibration;
* walk-forward analysis;
* diagnostics;
* final coefficient fitting.

No prices.
No fundamentals.
No SEC filings.
No benchmark result.
Nothing.
47. Future Holdout objective
If H026 passes development, a later owner-approved stage will extend the frozen PIT infrastructure through the Holdout and perform exactly one final evaluation.
The primary final question will be:
Starting with the same $100,000 on the same date, did frozen H026 finish with more money than SPY after costs?
No retraining.
No rescue.
No tuning.
48. Final Holdout success concept
Do not execute this now, but pre-register conceptually:

```
H1:
Terminal Wealth H026 > SPY

H2:
Excess CAGR > 0

H3:
risk does not materially exceed frozen development tolerance

H4:
outperformance is not entirely dependent on one calendar year
```

Exact Holdout gates may be pinned in the later pre-Holdout checkpoint, before any 2022+ value is read.
49. Infrastructure failure policy
If extending Data v2 to 2021 reveals:

* material PIT inconsistency;
* unacceptable identity loss;
* corporate-action mismatch;
* historical 2011–2017 population drift;
* irreproducibility;

STOP.
Do not modify the learning methodology to compensate for an infrastructure problem.
50. Required run order
Use exactly:

```
1. Record owner decision
2. Extend Data v2 rules through 2021
3. Audit Data v2.1
4. Freeze Data v2.1 manifest
5. Build 11-feature H026 panel
6. Verify feature formulas against H024
7. Build 63-session response machinery
8. Verify label-availability / purge logic
9. Implement weighted Ridge
10. Implement nested walk-forward
11. Implement Top-15 portfolio
12. Canary using synthetic/planted data
13. Freeze complete H026 pipeline
14. Run 5,000 full-pipeline null worlds
15. Determinism rerun
16. Pin c_WEALTH
17. Run exactly one real 2015–2021 outer walk-forward
18. Apply D1–D5
19. Run pre-registered diagnostics
20. If all gates pass, fit/freeze final coefficients
21. STOP
```

51. Canary requirements
Before any null or real H026 run, prove:

```
Ridge implementation vs independent reference
monthly weighting correct
63-session responses correct
no label crosses training cutoff
same-date feature percentiles correct
feature formulas equal H024
next-open execution correct
portfolio weights correct
sector cap correct
commissions correct
slippage correct
cash accounting correct
SPY total return correct
corporate actions correct
terminal wealth calculation correct
null feature-vector permutation correct
```

Use planted synthetic worlds showing:

```
known predictive coefficients → recovered positive portfolio edge
zero relationship → no edge
```

No real H026 portfolio result during canary.
52. Required checkpoint
Create:
P11-CP1 — H026 Learned Stock Score Portfolio
Include at minimum:

1. Owner decision ID.
2. Confirmation H022–H025 remain closed.
3. Data v2.1 extension method.
4. Data v2.1 manifest hash.
5. 2011–2017 reproduction result.
6. 2018–2021 infrastructure coverage.
7. PIT audit.
8. Identity audit.
9. Corporate-action audit.
10. Feature list.
11. Feature-formula hashes.
12. Feature coverage.
13. 63-session target definition.
14. Label-availability rule.
15. Ridge equation.
16. λ grid.
17. Monthly observation weighting.
18. Outer fold definition.
19. Inner fold definition.
20. Hyperparameter-selection objective.
21. Canary result.
22. Null-world method.
23. Number of null worlds.
24. Null determinism result.
25. Null `S_WEALTH` distribution.
26. `c_WEALTH`.
27. Real outer-fold λ by year.
28. Real coefficients by year.
29. Coefficient stability.
30. H026 annual return 2015.
31. SPY annual return 2015.
32. Continue annually through 2021.
33. H026 terminal wealth.
34. SPY terminal wealth.
35. Wealth ratio.
36. H026 CAGR.
37. SPY CAGR.
38. Excess CAGR.
39. `S_WEALTH_real`.
40. Null percentile / p-value.
41. D1 PASS/FAIL.
42. Years beating SPY.
43. 2015–2017 relative result.
44. 2018–2021 relative result.
45. largest-year contribution.
46. D2 PASS/FAIL.
47. D3 PASS/FAIL.
48. H026 volatility.
49. SPY volatility.
50. H026 MaxDD.
51. SPY MaxDD.
52. time underwater comparison.
53. D4 PASS/FAIL.
54. turnover.
55. number of trades.
56. commission cost.
57. slippage cost.
58. 2× slippage terminal wealth.
59. D5 PASS/FAIL.
60. Average holdings.
61. cash utilisation.
62. sector concentration.
63. $200K diagnostic.
64. Top-10 diagnostic.
65. Top-20 diagnostic.
66. Final all-gate result.
67. Final λ if qualified.
68. Final coefficients if qualified.
69. Candidate hash if qualified.
70. Confirmation no retraining after development.
71. Confirmation no new feature added.
72. Confirmation no target changed.
73. Confirmation no K optimisation.
74. Confirmation Holdout untouched.
75. Confirmation nothing purchased.
76. Final status:


```
H026 DEVELOPMENT CANDIDATE —
LEARNED SCORE FROZEN,
FINAL HOLDOUT SEALED
```

or:

```
H026 REJECTED —
LEARNED SCORE PORTFOLIO DOES NOT ROBUSTLY BEAT SPY
```

or, if infrastructure fails:

```
H026 BLOCKED —
DATA v2.1 EXTENSION / PIPELINE INVALID
```

77. Exact next owner decision.

53. If H026 fails
STOP.
Do not:

* alter λ grid;
* remove features;
* change signs;
* change 63-day target;
* change Top-15;
* optimise sector cap;
* switch to ElasticNet;
* switch to nonlinear ML;
* open Holdout.

Any such change is H027+.
54. If H026 passes
Freeze the exact Score and portfolio rules.
STOP.
Do not access 2022+.
Return for owner approval for:
one final untouched 2022–2026 Holdout evaluation.
55. Final principle
H026 answers a different question from H022–H024:
Not “can I construct a pretty Score with good IC?”
but:
Can a learned, interpretable ranking formula repeatedly select a 15-stock portfolio that compounds more money than SPY after costs, while taking only moderately more risk?
That is now the primary research question.
Do not optimise for a statistically attractive score if it does not produce superior portfolio wealth.
