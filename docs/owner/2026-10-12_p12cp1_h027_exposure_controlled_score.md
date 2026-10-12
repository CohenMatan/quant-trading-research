# Owner message 2026-10-12: "Phase 12 — H027 Exposure-Controlled Learned Stock Score"

Decision id: **D213**. It does four things:
- approves the Data v2.1 freeze as an owner exception for the NEW_YEARS_MAPPING specification error;
- keeps H026 permanently REJECTED;
- declines the optional H026 export run;
- approves H027 exactly as specified.

Recorded and committed before any H027 code, null world or result exists. The owner's message follows verbatim.

---

Phase 12 — H027
Exposure-Controlled Learned Stock Score
Does the learned Score contain stock-selection edge beyond LOWVOL while still beating SPY?
Continue from:
P11-CP2 — H026 Post-Mortem and Performance Attribution
This message is the owner approval for H027 exactly as specified below.
1. Owner decisions
Record the following owner decisions verbatim.
Decision 1 — Data v2.1
The owner explicitly approves the existing Data v2.1 freeze as an owner exception for the `NEW_YEARS_MAPPING` specification error.
The historical record must remain unchanged:

```
NEW_YEARS_MAPPING failed AS WRITTEN.
```

Do not rewrite it as a PASS.
Record instead:

```
OWNER-APPROVED EXCEPTION:
The failed criterion used an incorrect denominator.
No underlying data row was changed by the issue.
The SEC-identity denominator gives approximately
0.95–0.97 mapping coverage in 2018–2021.
```

Preserve:

```
D207
original failed gate
corrected-denominator analysis
-0.046% 2011–2017 population difference
```

Do not rebuild Data v2.1.
Decision 2 — H026
H026 remains permanently:

```
H026 REJECTED —
LEARNED SCORE PORTFOLIO DOES NOT ROBUSTLY BEAT SPY
```

Do not relabel H026.
Do not change H026's:

```
1% threshold
D1–D5
features
target
λ grid
portfolio
results
```

Decision 3 — optional export
Do not perform the optional H026 security-level export run.
The missing stock-level post-mortem items remain missing.
They are not required for H027.
Decision 4 — H027
Approve:
H027 — Exposure-Controlled Learned Stock Score
The purpose is to answer:
Does the learned 11-feature Score contain predictive stock-selection information beyond the LOWVOL exposure that largely explains H026's defensive behaviour, while still producing more terminal wealth than SPY?
2. Important interpretation
H027 is motivated by already-observed H026 results.
Therefore:

```
2011–2021 is fully seen development data.
```

H027 cannot provide independent confirmation.
Even if H027 passes every development gate, the strongest permissible conclusion is:

```
H027 DEVELOPMENT CANDIDATE
```

Confirmation requires the still-sealed programme Holdout:

```
2022-01-01 → 2026-08-31
```

Do not access the Holdout during Phase 12.
3. Why H027 exists
The H026 post-mortem found:

```
H026 terminal wealth ≈ $311,397
SPY terminal wealth  ≈ $262,325

H026 CAGR ≈ 17.6%
SPY CAGR  ≈ 14.8%

H026 beta ≈ 0.80
H026 volatility ≈ 16.4%
SPY volatility  ≈ 17.7%

H026 MaxDD ≈ -26.1%
SPY MaxDD  ≈ -33.7%
```

But:

```
D1 failed:
p ≈ 0.020 vs frozen 0.01 requirement

D3 failed:
H026 beat SPY only 3 of 7 years
```

The post-mortem further found:

```
SPY-down months:
H026 relative log wealth +0.202

SPY-up months:
H026 relative log wealth -0.030
```

and LOWVOL had a stable coefficient in every year.
Therefore H027 tests the narrower question:
After allowing LOWVOL to retain its real historical relationship with returns, do the remaining learned features add enough genuine stock-selection information to distinguish the real portfolio from noise?
4. H027 changes only the statistical question
The H027 real portfolio construction remains the H026 procedure.
Do not redesign the Score.
Freeze exactly:

```
11 features:
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

Use the exact H024/H026 PIT formulas.
Also freeze:

```
feature transformations
63-session target
SPY-relative target
monthly observation weighting
Ridge regression
λ grid
nested walk-forward
Top-15 portfolio
max initial 10%
max 3 per FF12 sector
monthly rebalance
next-open execution
$7 BUY
$7 SELL
0.10% slippage per side
long only
no leverage
$100K starting capital
```

5. Ridge grid remains unchanged
Use exactly:

```
λ ∈ {
0.01,
0.1,
1,
10,
100
}
```

Do not:

```
extend above 100
remove λ search
fix λ=100
use sign-only weights
use ElasticNet
```

Those ideas belong to separate hypotheses.
6. Development / walk-forward structure
Keep the H026 outer folds unchanged:

```
2011–2014 → 2015
2011–2015 → 2016
2011–2016 → 2017
2011–2017 → 2018
2011–2018 → 2019
2011–2019 → 2020
2011–2020 → 2021
```

Keep all label-availability rules unchanged.
No 63-session response may cross the relevant training cutoff.
7. Real H027 portfolio
The real H027 portfolio must be mathematically identical to the frozen H026 real procedure.
This is intentional.
H027 is not asking:
Can we build a better portfolio after seeing H026?
It asks:
Was H026's apparently attractive portfolio result more than a LOWVOL effect?
Therefore the real H027 wealth path should reproduce H026 exactly.
Expected reference values are approximately:

```
terminal wealth ≈ $311,397
S_WEALTH ≈ 0.1715
```

This is an integrity expectation, not a target.
If the real H027 portfolio does not reproduce H026:

```
STOP
```

and explain why.
8. The key methodological change: conditional null
H026's original null shuffled the entire 11-feature vector.
That also destroyed the genuine LOWVOL-to-stock relationship.
The H026 post-mortem showed this created a problem for the question now being asked:
None of the 5,000 original null portfolios had volatility as low as H026.
So H027 must use a different null designed specifically for the new hypothesis.
9. H027 conditional-null hypothesis
The null hypothesis is:
LOWVOL may contain a genuine return/risk relationship, but the other ten H026 features contain no stock-specific predictive information beyond LOWVOL.
Therefore in every null world:

```
LOWVOL remains attached to its real stock.
```

The following ten features are randomized:

```
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

10. Ten-feature vector must move together
Do not shuffle the ten features independently.
Define:

```
OTHER_VECTOR =
[
MOM,
GPA,
ACC,
BM,
AG,
REV1M,
CBOP,
HI52,
CFP,
EQA
]
```

Move the complete vector together.
This preserves:

```
cross-feature relationships among the ten features
```

within the donor stock.
11. Persistent identity tether
Use the same persistent identity-tether philosophy as the previously accepted H022/H026 null machinery.
For each seed:

```
recipient stock
→
persistent donor stock
```

The donor's ten-feature vector moves through time with the donor identity.
The recipient keeps:

```
its own LOWVOL
its own future returns
its own security identity
its own prices
its own corporate actions
```

Thus the null breaks:

```
recipient OTHER_VECTOR
↔
recipient future return
```

while retaining:

```
recipient LOWVOL
↔
recipient future return
```

12. No return permutation
Never shuffle:

```
prices
future returns
SPY
calendar
corporate actions
universe membership
```

Only the ten non-LOWVOL predictor vector is permuted.
13. Full pipeline must be rerun in every null world
Every H027 null world must repeat the complete learning process:

```
inner λ selection
outer Ridge fitting
coefficient estimation
monthly scoring
Top-15 construction
sector constraint
monthly trading
commissions
slippage
terminal wealth
```

LOWVOL is real in every world.
Do not use a shortcut statistic.
14. Why this is the correct new null
The original H026 null asked:
Could the entire Score look successful if all features were unrelated to their own stocks?
H027 asks:
Could the Score look successful if LOWVOL is real, but everything else provides no incremental stock-selection information?
These are different hypotheses.
Do not overwrite the H026 null.
Create a new:

```
H027 CONDITIONAL NULL
```

15. Conditional-null adequacy audit
Before interpreting the new null statistically, verify that preserving LOWVOL materially fixes the risk mismatch observed in H026.
For each of the 5,000 conditional-null worlds record:

```
annualized volatility
MaxDD
beta to SPY
up capture
down capture
```

where feasible without excessive memory.
Compare their distributions with the real H027/H026 portfolio.
The purpose is descriptive:
Does the H027 null now generate portfolios with defensive properties similar to the real portfolio?
If the null still produces essentially no worlds remotely similar to the real portfolio's risk profile, STOP before claiming an exposure-adjusted significance result.
Report:

```
CONDITIONAL NULL INADEQUATE
```

and explain why.
Do not invent another null after seeing the result.
A different null requires H028.
16. Number of null worlds
Run:

```
5,000
```

conditional-null worlds.
Seeds:

```
1–5000
```

No fewer without returning for owner approval.
17. Null determinism
Independently rerun:

```
seeds 1–25
```

Require exact or defined numerical-tolerance reproduction of:

```
λ selections
coefficients
yearly returns
terminal wealth
S_WEALTH
```

Failure:

```
STOP
```

18. Primary H027 statistic
Keep the direct economic statistic:

```
S_WEALTH =
ln(
    terminal wealth strategy
    /
    terminal wealth SPY
)
```

The real H027 statistic should reproduce H026:

```
approximately 0.1715
```

19. New search-adjusted threshold
From the 5,000 conditional null worlds define:

```
c_WEALTH_CONDITIONAL =
one-sided empirical 99th percentile
of S_WEALTH_null
```

using the exact same order-statistic convention as prior phases.
Pin it before formally mapping the real portfolio into the distribution.
Record:

```
conditional-null hash
seeds
pipeline hash
Data v2.1 manifest
c_WEALTH_CONDITIONAL
```

20. Primary Gate A1 — incremental information beyond LOWVOL
Require:

```
S_WEALTH_real
>
c_WEALTH_CONDITIONAL
```

and:

```
empirical p <= 0.01
```

This is H027's central test.
If A1 fails:
the existing evidence does not show stock-selection skill beyond LOWVOL.
H027 fails.
Do not modify the null.
21. LOWVOL-only control portfolio
Construct one pre-registered control portfolio using only the existing LOWVOL feature.
At each monthly review:

```
rank eligible stocks by LOWVOL
lowest realized 60-day volatility ranks highest
```

Select:

```
Top 15
```

subject to the exact same:

```
max 3 per FF12 sector
10% initial position cap
monthly rebalance
next-open trading
costs
cash handling
```

No Ridge.
No other feature.
Call it:

```
LV15_CONTROL
```

This is a control, not a candidate strategy.
Do not optimise it.
22. LOWVOL control purpose
LV15_CONTROL answers:
How much of H027's result can a simple explicit low-volatility stock-selection rule reproduce?
Report:

```
terminal wealth
CAGR
volatility
MaxDD
beta
up capture
down capture
turnover
```

for:

```
H027
LV15_CONTROL
SPY
```

23. Gate A2 — beat the defensive control
Require:

```
Terminal Wealth H027
>
Terminal Wealth LV15_CONTROL
```

after identical costs.
Also require:

```
H027 CAGR
>
LV15_CONTROL CAGR
```

No minimum percentage-point gap is added.
If it cannot beat a simple LOWVOL portfolio, there is no evidence that the other ten features improved the economic result.
24. Gate A3 — still beat SPY materially
The ultimate objective remains SPY.
Retain the same H026 economic requirement:

```
Terminal Wealth H027
>=
1.15 × Terminal Wealth SPY
```

and:

```
H027 CAGR - SPY CAGR
>=
+2.0 percentage points/year
```

after costs.
This requirement is already known to have been met by H026.
State explicitly that this is:

```
A CARRIED-FORWARD ECONOMIC REQUIREMENT,
NOT NEW INDEPENDENT EVIDENCE.
```

25. Gate A4 — temporal incremental robustness
For each outer year 2015–2021 calculate H027 relative to:

```
LV15_CONTROL
```

Require:

```
H027 beats LV15_CONTROL in at least 5 of 7 years
```

and:

```
2015–2017 compounded H027/LV15 relative return > 0
2018–2021 compounded H027/LV15 relative return > 0
```

This is the new temporal test.
Do not substitute SPY for LV15 in this gate.
26. Gate A5 — balanced risk
Retain:

```
|MaxDD_H027|
<=
1.25 × |MaxDD_SPY|
```

and:

```
volatility_H027
<=
1.25 × volatility_SPY
```

This is a safeguard, not evidence of alpha.
27. Gate A6 — doubled-cost robustness
Without retraining:

```
slippage = 0.20% per side
```

Apply the same stress to:

```
H027
LV15_CONTROL
SPY
```

Require:

```
H027 terminal wealth
>
SPY terminal wealth
```

and:

```
H027 terminal wealth
>
LV15_CONTROL terminal wealth
```

Do not retrain coefficients.
28. All gates required
H027 is a development candidate only if:

```
A1 PASS
A2 PASS
A3 PASS
A4 PASS
A5 PASS
A6 PASS
```

No partial promotion.
29. Exposure-adjusted regression diagnostic
As a non-gating diagnostic, construct a monthly LOWVOL factor from the eligible universe.
At each review/month define:

```
LOWVOL_FACTOR =
return of equal-weight lowest-volatility quintile
-
return of equal-weight eligible universe
```

using only PIT memberships.
Then estimate:

```
(H027 monthly return - SPY monthly return)
=
alpha
+
gamma * LOWVOL_FACTOR
+
error
```

Report:

```
alpha monthly
alpha annualized
Newey-West t(alpha), lag 2
gamma
R²
```

This is descriptive only.
Do not turn it into another pass/fail gate.
30. Sector-neutral diagnostic
Retain the previous non-gating sector-neutral analysis if it can be computed within the H027 artifacts.
Do not use it to rescue a failed A1–A6.
31. What H027 must NOT do
Do not:

```
change LOWVOL lookback
change 63-session target
remove LOWVOL
remove BM
remove any feature
change feature signs manually
change Top-15
change sector cap
add a market regime filter
reduce exposure during crashes
hold cash intentionally
change λ range
use λ=100 permanently
add VIX
add analyst estimates
add earnings data
add new factors
```

H027 isolates one question only.
32. 2018/2020 cannot become a rule
Do not introduce:

```
crash filter
bear-market filter
SPY trend filter
risk-off exposure reduction
```

because H026 happened to perform well in 2018/2020.
That would directly fit the periods already observed.
Such an idea would require a separate hypothesis.
33. March 2020
Report March 2020 again in attribution after the H027 result.
But:

```
do not remove it
do not winsorize it
do not change gates because of it
```

H027 must survive or fail with the historical path as it occurred.
34. H026 original null remains preserved
Do not replace H026's original 5,000 null worlds.
The research record must contain both:

```
H026 unconditional null
H027 LOWVOL-conditional null
```

Their different questions must be explained.
35. Memory reduction is authorised as infrastructure work
P11-CP2 reported:

```
7.6–8.2 GB
```

peak usage.
Before H027 heavy runs, memory reduction is authorised.
Allowed engineering changes include:

```
freeing construction intermediates before model stage
streaming null results instead of retaining redundant monthly structures
safe dtype reductions
avoiding duplicate price matrices
```

But:
Numerical research behaviour must not change.
36. Memory-refactor equivalence gate
Before H027 null calibration, demonstrate on deterministic fixtures and/or digest-only development checks that memory changes preserve:

```
eligible rows
features
responses
Ridge coefficients
λ decisions
portfolio calculations
cost calculations
```

within explicitly documented numerical tolerance.
Do not calculate the final H027 research statistic as part of this engineering test.
If equivalence fails:

```
STOP
```

37. Peak memory target
Report:

```
peak memory before
peak memory after
```

Target:

```
comfortably below the B2-8 limit
```

Prefer:

```
< 6.5 GB
```

but this is an engineering target, not a scientific gate.
Do not compromise numerical correctness merely to meet it.
38. Canary
Before the 5,000 worlds, create an H027 canary covering:

```
LOWVOL never permuted
other ten features move together
persistent donor identity
recipient returns unchanged
corporate actions unchanged
nested λ selection correct
Top-15 correct
LV15_CONTROL correct
costs correct
S_WEALTH correct
conditional-null threshold code correct
```

Also use planted synthetic data:
Synthetic world A
Only LOWVOL predicts returns.
Expected:

```
real-style full model should NOT systematically beat
the LOWVOL-conditional null.
```

Synthetic world B
LOWVOL plus one non-LOWVOL feature predicts returns.
Expected:

```
full model should outperform the conditional null.
```

This is critical.
39. Run order
Use exactly:

```
1. Record owner decisions
2. Record explicit D207 owner exception
3. Preserve H026 rejected status
4. Create H027 spec
5. Implement memory reduction
6. Verify numerical equivalence
7. Implement LV15_CONTROL
8. Implement LOWVOL-conditional null
9. Run synthetic canary
10. Freeze H027 code/spec
11. Run 5,000 conditional-null worlds
12. Rerun seeds 1–25
13. Audit conditional-null risk adequacy
14. Pin c_WEALTH_CONDITIONAL
15. Run/map the one real H027 development result
16. Verify exact H026 portfolio reproduction
17. Evaluate A1–A6
18. Run only pre-registered diagnostics
19. If all gates pass, fit/freeze final Score
20. STOP
```

40. If H027 fails A1
If:

```
S_WEALTH_real <= c_WEALTH_CONDITIONAL
```

the interpretation should be:
The H026 wealth advantage is not distinguishable from what can arise when LOWVOL retains its real relationship with returns and all other score information is noise.
Do not call the strategy useless.
It may still be a legitimate defensive portfolio.
But it fails our goal of demonstrating incremental stock-selection edge.
41. If H027 fails A2/A4
Interpretation:
The full learned Score does not improve consistently enough upon a simple low-volatility stock portfolio.
Do not tune feature weights.
Do not remove features.
42. If H027 passes
If and only if A1–A6 all pass:
Fit the final frozen Ridge Score using all permissible observations through 2021.
Use the exact H026 training method.
No label may extend into 2022.
Record:

```
final λ
intercept
all 11 coefficients
feature formulas
portfolio mechanics
cost assumptions
Data v2.1 manifest
conditional-null method
c_WEALTH_CONDITIONAL
LV15 control definition
```

Status:

```
H027 DEVELOPMENT CANDIDATE —
EXPOSURE-CONTROLLED SCORE FROZEN
HOLDOUT NOT RUN
```

43. Important limitation even if H027 passes
Because H027 was motivated by H026's already-seen 2015–2021 behaviour, do not write:

```
validated
confirmed
proven
out-of-sample success
```

Instead write:

```
development evidence only
```

The only remaining clean confirmation is the untouched Holdout.
44. Holdout policy
Do not access:

```
2022-01-01 → 2026-08-31
```

for any reason in this phase.
That means:

```
no prices
no fundamentals
no SPY returns
no SEC filings
no feature values
no benchmark values
no sanity check
```

Nothing.
45. No automatic Holdout run
Even if H027 passes all gates:

```
STOP
```

Return for owner review.
Do not automatically run 2022–2026.
46. Required checkpoint
Create:
P12-CP1 — H027 Exposure-Controlled Learned Stock Score
Include at minimum:

1. Owner decision ID.
2. Explicit D207 owner exception.
3. Original failed Data v2.1 criterion preserved.
4. Corrected-denominator explanation.
5. H026 permanently rejected.
6. H027 hypothesis.
7. Development period.
8. Holdout status.
9. Frozen 11 features.
10. Frozen target.
11. Frozen Ridge grid.
12. Frozen portfolio mechanics.
13. Memory before.
14. Memory after.
15. Memory equivalence result.
16. Conditional-null definition.
17. Proof LOWVOL remains attached.
18. Proof other ten features move as one vector.
19. Persistent-tether implementation.
20. Canary result.
21. Synthetic LOWVOL-only canary.
22. Synthetic LOWVOL+incremental-signal canary.
23. Null-world count.
24. Seeds.
25. Null determinism.
26. Conditional-null S_WEALTH distribution.
27. Conditional-null volatility distribution.
28. Conditional-null MaxDD distribution.
29. Conditional-null beta distribution.
30. Conditional-null down-capture distribution.
31. Null adequacy conclusion.
32. `c_WEALTH_CONDITIONAL`.
33. Real H027 terminal wealth.
34. H026 reproduction check.
35. Real SPY wealth.
36. `S_WEALTH_real`.
37. Conditional-null percentile.
38. Conditional-null empirical p.
39. A1.
40. LV15_CONTROL terminal wealth.
41. LV15 CAGR.
42. LV15 volatility.
43. LV15 MaxDD.
44. LV15 beta.
45. LV15 up/down capture.
46. H027 vs LV15.
47. A2.
48. H027/SPY wealth ratio.
49. H027/SPY excess CAGR.
50. A3.
51. H027 vs LV15 by year.
52. 2015–2017 H027/LV15 result.
53. 2018–2021 H027/LV15 result.
54. A4.
55. H027/SPY risk ratios.
56. A5.
57. 2× slippage H027 wealth.
58. 2× slippage LV15 wealth.
59. 2× slippage SPY wealth.
60. A6.
61. LOWVOL-factor regression alpha.
62. LOWVOL-factor gamma.
63. sector-neutral diagnostic.
64. March-2020 attribution.
65. confirmation no feature changed.
66. confirmation no target changed.
67. confirmation λ grid unchanged.
68. confirmation no regime filter.
69. confirmation no H026 result rewritten.
70. confirmation Holdout untouched.
71. all-gate result.
72. final Score coefficients if qualified.
73. final candidate hash if qualified.
74. exact next owner decision.

47. Final statuses
If any scientific gate fails:

```
H027 REJECTED —
NO ROBUST STOCK-SELECTION EDGE
BEYOND LOWVOL EXPOSURE
```

If the conditional null itself is inadequate:

```
H027 BLOCKED —
EXPOSURE-CONTROLLED NULL INADEQUATE
```

If all A1–A6 pass:

```
H027 DEVELOPMENT CANDIDATE —
INCREMENTAL EDGE BEYOND LOWVOL DETECTED
FINAL HOLDOUT SEALED
```

48. STOP
After P12-CP1:
STOP and return for owner review.
Do not begin H028.
Do not open the Holdout.
