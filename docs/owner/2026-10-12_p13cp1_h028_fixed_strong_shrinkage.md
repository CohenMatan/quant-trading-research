# Owner message 2026-10-12: "Phase 13 — H028 Fixed Strong Shrinkage Learned Stock Score"

Decision id: **D217**. It does two things:
- closes H027 formally as REJECTED — NO ROBUST STOCK-SELECTION EDGE BEYOND LOWVOL EXPOSURE;
- approves one narrow, explicitly post-hoc development hypothesis, H028: the frozen H027 architecture with λ = 100 fixed for every Ridge fit (no λ selection, no λ search).

Recorded and committed before any H028 code, null world or result exists. The owner's message follows verbatim.

---

# Phase 13 — H028
## Fixed Strong Shrinkage Learned Stock Score
### Same H027 Architecture, λ = 100 Fixed Everywhere

Continue from:

> **P12-CP1 — H027 Exposure-Controlled Learned Stock Score**

Owner decision:

> Close H027 formally as:
>
> **H027 REJECTED — NO ROBUST STOCK-SELECTION EDGE BEYOND LOWVOL EXPOSURE**
>
> H027 passed A1, A2, A3, A5 and A6, but failed A4 because the learned portfolio was still behind LV15 over 2015–2017.

I now approve one narrow, explicitly post-hoc development hypothesis:

> **H028 — Fixed Strong Shrinkage Learned Stock Score**

The sole scientific change is:

```text
λ = 100
```

for every Ridge fit.

No λ selection.

No λ search.

Everything else remains frozen.

---

# 1. Important interpretation

H028 is motivated directly by the already-observed H026/H027 results.

Therefore:

```text
2011–2021 is fully seen development data.
```

H028 cannot be described as:

```text
validation
confirmation
out-of-sample proof
```

Even if H028 passes every gate, the strongest permissible status is:

```text
H028 DEVELOPMENT CANDIDATE
```

The programme Holdout remains:

```text
2022-01-01 → 2026-08-31
```

and must remain completely sealed.

---

# 2. Why H028 exists

In H027:

```text
2015: λ = 0.01
2016: λ = 100
2017: λ = 100
2018: λ = 100
2019: λ = 100
2020: λ = 100
2021: λ = 100
```

The 2015 coefficient vector was approximately an order of magnitude larger than later years.

From 2016 onward the coefficient vectors were relatively stable.

Therefore H028 tests:

> Does removing annual λ selection and using the same strong regularisation rule from the beginning produce a more temporally stable stock-selection process?

This is not a search for the optimal λ.

`100` is chosen because it was already part of the frozen H026/H027 grid and was the selected value in 6 of 7 outer years.

Do not claim:

```text
λ=100 is optimal
```

The correct interpretation is:

```text
λ=100 is a pre-declared representative of strong shrinkage.
```

---

# 3. Critical fact: H028 should change only 2015

Because H027 already selected λ=100 in:

```text
2016
2017
2018
2019
2020
2021
```

H028 should reproduce H027 exactly for those six outer years.

Therefore pre-register an integrity requirement:

```text
2016–2021 H028 results must equal H027
within documented numerical tolerance.
```

This includes, for each year:

```text
coefficients
scores
portfolio holdings
year return
turnover
costs
terminal path
```

where the artifact exists.

If any 2016–2021 scientific result changes unexpectedly:

```text
STOP
```

Do not continue to the real H028 conclusion until the difference is explained.

---

# 4. Frozen data

Use the existing owner-approved:

```text
Data v2.1
```

exactly as frozen.

Preserve the historical note:

```text
NEW_YEARS_MAPPING failed as written
OWNER-APPROVED EXCEPTION applies
```

Do not rebuild or modify the dataset.

Do not change PIT rules.

---

# 5. Feature library remains identical

Use exactly the H026/H027 11 features:

```text
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

Use the exact same formulas and PIT timing.

No new features.

No deleted features.

No interactions.

No changed signs.

---

# 6. Feature transformation remains identical

At each monthly review:

1. calculate each feature PIT-safely;
2. convert it to its cross-sectional percentile;
3. map:

```text
x = 2 * percentile - 1
```

so every model input remains approximately:

```text
[-1,+1]
```

Do not alter transformations.

---

# 7. Prediction target remains identical

Use the existing H026/H027 target:

```text
63 trading-session forward TSR
minus SPY TSR over the identical interval
```

then cross-sectional rank-transform the target exactly as before.

No:

```text
21-day target
42-day target
126-day target
classification target
```

---

# 8. Label-availability rules remain identical

At training timestamp `T`, an observation may enter training only when its entire 63-session response was already known before `T`.

No response may cross the relevant outer-year training cutoff.

Use the exact H026/H027 purge/availability implementation.

---

# 9. The only model change

H027 used:

```text
λ ∈ {0.01, 0.1, 1, 10, 100}
```

with an inner selection process.

H028 removes this entire choice.

For every outer fold:

```text
λ = 100
```

No inner λ selection.

No comparison among λ values.

No fallback.

---

# 10. Do not search beyond 100

Do not test:

```text
30
50
200
300
1000
3000
```

Do not ask whether another strong-shrinkage value performs better.

That would be another hypothesis.

H028 answers only:

> Does the already-observed strong-shrinkage setting produce a more robust version of this learned score when fixed from the beginning?

---

# 11. Outer folds

Keep exactly:

```text
2011–2014 → test 2015
2011–2015 → test 2016
2011–2016 → test 2017
2011–2017 → test 2018
2011–2018 → test 2019
2011–2019 → test 2020
2011–2020 → test 2021
```

For every fold:

```text
fit Ridge with λ=100
```

using all eligible pre-test observations.

---

# 12. Portfolio mechanics remain frozen

Use exactly:

```text
Starting capital: $100,000
Top 15 stocks
equal target allocation
max initial position weight 10%
max 3 stocks per FF12 sector
long only
no leverage
monthly rebalance
next-session-open execution
```

No threshold.

No buffer.

No stop loss.

No take profit.

No regime rule.

No market timing.

---

# 13. Costs remain frozen

Use:

```text
$7 BUY
$7 SELL
0.10% slippage per side
```

Primary capital:

```text
$100,000
```

---

# 14. Benchmarks

Keep both:

```text
SPY Buy & Hold
LV15_CONTROL
```

LV15 definition remains exactly H027:

> every month select the 15 eligible stocks with the lowest realised 60-day volatility, subject to the same sector, sizing, execution and cost rules.

Do not optimise LV15.

---

# 15. Primary scientific question

H028 asks:

> Does a fixed strong-shrinkage learned score add robust stock-selection value beyond a simple LOWVOL portfolio, while still beating SPY after costs?

---

# 16. H027 conditional null remains the conceptual template

Use the same LOWVOL-conditional null logic:

```text
LOWVOL remains attached to the real recipient stock.
```

The other ten features move together as a persistent donor vector:

```text
MOM
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

Recipient keeps:

```text
LOWVOL
returns
prices
identity
corporate actions
```

---

# 17. H028 requires a fresh null calibration

Do not reuse H027's numerical threshold.

Because H028 removes λ selection, the research procedure is different.

Run:

```text
5,000 conditional-null worlds
```

and in every null world use:

```text
λ = 100
```

for every outer fold.

No λ search in null worlds.

---

# 18. Full pipeline in each null world

Each world must repeat:

```text
annual λ=100 Ridge fitting
monthly scores
Top-15 portfolio construction
sector cap
trading
commissions
slippage
SPY comparison
```

Do not shortcut the portfolio simulation.

---

# 19. Null determinism

Rerun:

```text
seeds 1–25
```

Require reproducibility of:

```text
coefficients
year returns
terminal wealth
S_WEALTH
```

within the existing numerical tolerance.

Failure:

```text
STOP
```

---

# 20. Conditional-null adequacy

Repeat the H027 adequacy audit.

Report distributions of:

```text
volatility
MaxDD
beta
up capture
down capture
```

The conditional null must remain a meaningful comparison for a defensive portfolio.

If materially inadequate:

```text
H028 BLOCKED — CONDITIONAL NULL INADEQUATE
```

Do not invent another null.

---

# 21. Primary statistic

Use:

```text
S_WEALTH =
ln(
    Terminal Wealth H028
    /
    Terminal Wealth SPY
)
```

---

# 22. New H028 threshold

From the 5,000 H028 fixed-λ conditional worlds set:

```text
c_WEALTH_H028 =
one-sided empirical 99th percentile
of S_WEALTH_null
```

Pin it before interpreting the real H028 result.

Record:

```text
null hash
seeds
Data v2.1 manifest
pipeline hash
λ=100 rule
c_WEALTH_H028
```

---

# 23. Gate B1 — conditional-null significance

Require:

```text
S_WEALTH_real > c_WEALTH_H028
```

and:

```text
empirical p <= 0.01
```

---

# 24. Gate B2 — beat LV15 economically

Require:

```text
Terminal Wealth H028
>
Terminal Wealth LV15
```

and:

```text
CAGR H028
>
CAGR LV15
```

after identical costs.

---

# 25. Gate B3 — beat SPY materially

Retain:

```text
Terminal Wealth H028
>=
1.15 × Terminal Wealth SPY
```

and:

```text
CAGR H028 - CAGR SPY
>=
+2.0 percentage points/year
```

This is an economic requirement.

---

# 26. Gate B4 — temporal robustness

This remains the key gate that H027 failed.

Require:

```text
H028 beats LV15 in >= 5 of 7 outer years
```

AND:

```text
2015–2017 compounded H028/LV15 relative return > 0
```

AND:

```text
2018–2021 compounded H028/LV15 relative return > 0
```

All three required.

Do not weaken this gate.

---

# 27. Additional B4 transparency

Report yearly H028 vs:

```text
LV15
SPY
H027
```

for 2015–2021.

Because H028 should differ from H027 only in 2015, explicitly calculate:

```text
change caused by fixing λ=100 in 2015
```

for:

```text
2015 return
2015 relative return vs SPY
2015 relative return vs LV15
2015 MaxDD
2015 turnover
2015 terminal year wealth
2015 coefficients
```

---

# 28. Gate B5 — risk

Require:

```text
|MaxDD_H028|
<=
1.25 × |MaxDD_SPY|
```

and:

```text
Volatility_H028
<=
1.25 × Volatility_SPY
```

---

# 29. Gate B6 — cost robustness

Without refitting, rerun exact frozen decisions using:

```text
0.20% slippage per side
```

Require:

```text
H028 wealth > SPY wealth
```

and:

```text
H028 wealth > LV15 wealth
```

---

# 30. All gates required

A development candidate requires:

```text
B1 PASS
B2 PASS
B3 PASS
B4 PASS
B5 PASS
B6 PASS
```

No partial promotion.

---

# 31. Important anti-overfitting restriction

If B4 still fails:

```text
STOP
```

Do not then try:

```text
λ=50
λ=200
λ=300
λ=1000
different feature weights
different K
different holding period
```

H028 should be the final λ-specific experiment for this architecture.

---

# 32. If H028 passes because of 2015 alone

This is possible and must be described carefully.

Because 2016–2021 should reproduce H027, any improvement in the failed 2015–2017 block will primarily come from changing 2015.

Therefore if H028 passes B4, explicitly disclose:

> The temporal gate was repaired by the pre-registered fixed-λ change primarily through 2015; the later years were already observed under H027.

Do not describe this as independent confirmation.

It remains development evidence.

---

# 33. 2016–2021 equality gate

Before final conclusions verify:

```text
for each year 2016–2021:
H028 coefficient vector ≈ H027 coefficient vector
H028 return ≈ H027 return
H028 turnover ≈ H027 turnover
```

Expected:

```text
identical except defined floating-point tolerance
```

If not:

```text
STOP — UNEXPECTED PIPELINE DIFFERENCE
```

---

# 34. H027 comparison

Report side by side:

| Metric | H027 | H028 |
|---|---:|---:|
| Terminal wealth | | |
| CAGR | | |
| Excess CAGR vs SPY | | |
| S_WEALTH | | |
| Null p | | |
| MaxDD | | |
| Volatility | | |
| Years > SPY | | |
| Years > LV15 | | |
| 2015–17 vs LV15 | | |
| 2018–21 vs LV15 | | |
| Turnover | | |

This comparison is descriptive.

Do not choose whichever looks better after the fact.

---

# 35. Coefficient comparison

Report 2015 coefficients under:

```text
H027 λ=0.01
H028 λ=100
```

For every feature show:

```text
H027 coefficient
H028 coefficient
absolute change
sign change yes/no
```

Explain in plain language how stronger shrinkage changed the 2015 ranking model.

---

# 36. Score stability

If already available without new infrastructure, report:

```text
2015 H027 vs H028 score rank correlation
Top-15 overlap
turnover difference
```

If not available:

```text
NOT COMPUTED
```

Do not launch an extra research run solely for this diagnostic.

---

# 37. LOWVOL-factor diagnostic

Retain the H027 non-gating regression:

```text
(H028 monthly return - SPY)
=
alpha
+
gamma * LOWVOL_FACTOR
+
error
```

Report:

```text
alpha
annualized alpha
NW t(alpha)
gamma
R²
```

Non-gating only.

---

# 38. March 2020 diagnostic

Report March 2020 contribution to:

```text
H028 vs SPY
H028 vs LV15
```

Because 2020 should be identical to H027, verify exact reproduction.

Do not alter or remove the month.

---

# 39. Memory

Use the H027 memory-reduced implementation.

Do not add memory-heavy exports.

Report peak memory.

The engineering target remains:

```text
preferably < 6.5 GB
```

but memory is not a scientific gate.

---

# 40. Canary

Before the real research run verify:

```text
λ is exactly 100 in every fold
no λ-search code is executed
2016–2021 reference fixtures reproduce H027
LOWVOL conditional null unchanged except fixed λ
LV15 unchanged
costs unchanged
portfolio mechanics unchanged
```

Synthetic checks:

### Synthetic A

Only LOWVOL has genuine signal.

Expected:

```text
H028 should not systematically beat
the conditional null.
```

### Synthetic B

LOWVOL plus another real predictor has signal.

Expected:

```text
H028 can exceed
the conditional-null distribution.
```

---

# 41. Exact run order

Use:

```text
1. Record owner approval
2. Close H027 as rejected
3. Create H028 specification
4. Implement fixed λ=100
5. Prove no λ selection remains
6. Run equivalence/unit tests
7. Run canary
8. Freeze code/spec
9. Run 5,000 fixed-λ conditional-null worlds
10. Rerun seeds 1–25
11. Verify conditional-null adequacy
12. Pin c_WEALTH_H028
13. Run exactly one real H028 development evaluation
14. Verify 2016–2021 equality with H027
15. Apply B1–B6
16. Run pre-registered diagnostics
17. If all gates pass, fit/freeze final λ=100 Score
18. STOP
```

---

# 42. Final model if H028 qualifies

Only if all B1–B6 pass:

Fit Ridge once using:

```text
λ = 100
```

on all permissible development observations whose labels are fully known before 2022.

Record:

```text
intercept
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

Freeze the exact coefficients.

For any future Holdout test:

```text
do not retrain
do not reselect λ
```

---

# 43. Holdout remains sealed

Do not access:

```text
2022-01-01 → 2026-08-31
```

No:

```text
prices
fundamentals
SPY returns
SEC filings
features
sanity checks
```

Even if H028 passes.

---

# 44. If H028 passes

Status:

```text
H028 DEVELOPMENT CANDIDATE —
FIXED λ=100 SCORE FROZEN
FINAL HOLDOUT SEALED
```

Then STOP.

Return for owner review.

Do not automatically run the Holdout.

---

# 45. If H028 fails

Status:

```text
H028 REJECTED —
FIXED STRONG SHRINKAGE DOES NOT
ROBUSTLY SOLVE THE TEMPORAL-STABILITY PROBLEM
```

Then STOP.

Do not search for another λ.

Do not widen the Ridge grid.

Do not automatically create H029.

The interpretation should be:

> The instability was not adequately explained by annual λ selection. The problem is deeper than the shrinkage hyperparameter.

---

# 46. Required checkpoint

Create:

> **P13-CP1 — H028 Fixed Strong Shrinkage Learned Stock Score**

Include at minimum:

1. Owner decision ID.
2. H027 permanent rejected status.
3. H028 hypothesis.
4. Explicit post-hoc/development-only disclosure.
5. Data v2.1 manifest.
6. D207 owner exception reference.
7. Frozen features.
8. Frozen target.
9. Fixed `λ=100`.
10. Proof no λ selection exists.
11. Outer folds.
12. Portfolio mechanics.
13. Costs.
14. LV15 definition.
15. Conditional-null method.
16. Null world count.
17. Null determinism.
18. Null adequacy.
19. `c_WEALTH_H028`.
20. H028 2015 coefficients.
21. H027 2015 coefficients.
22. 2015 coefficient difference.
23. H028 2015 return.
24. H027 2015 return.
25. 2015 difference vs SPY.
26. 2015 difference vs LV15.
27. 2016 equality check.
28. 2017 equality check.
29. 2018 equality check.
30. 2019 equality check.
31. 2020 equality check.
32. 2021 equality check.
33. H028 terminal wealth.
34. SPY terminal wealth.
35. LV15 terminal wealth.
36. H028 CAGR.
37. SPY CAGR.
38. LV15 CAGR.
39. `S_WEALTH`.
40. conditional-null p.
41. B1.
42. B2.
43. B3.
44. years H028 > LV15.
45. 2015–2017 H028/LV15 compounded result.
46. 2018–2021 H028/LV15 compounded result.
47. B4.
48. volatility.
49. MaxDD.
50. B5.
51. doubled-cost H028 wealth.
52. doubled-cost SPY wealth.
53. doubled-cost LV15 wealth.
54. B6.
55. H027/H028 comparison table.
56. LOWVOL-factor diagnostic.
57. March-2020 diagnostic.
58. memory peak.
59. confirmation no λ search after results.
60. confirmation no other parameter changed.
61. confirmation Holdout untouched.
62. all-gate result.
63. final coefficients if qualified.
64. candidate hash if qualified.
65. exact next owner decision.

---

# 47. Final principle

H028 is not:

> "Find a λ that makes the backtest pass."

H028 is:

> "Remove the λ-selection degree of freedom and test one already-observed strong-shrinkage rule."

The only scientific change from H027 is:

```text
λ selection → fixed λ=100
```

Everything else must remain identical.

---

# 48. STOP

After P13-CP1:

> **STOP and return for owner review.**

Do not open the Holdout.

Do not start H029.
