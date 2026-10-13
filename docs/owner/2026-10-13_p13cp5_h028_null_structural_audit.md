# Owner message 2026-10-13: P13-CP5 — H028 Conditional-Null Structural Audit

Decision id: **D238**. The owner's message is quoted verbatim below (as received).

---

P13-CP5 — H028 Conditional-Null Structural Audit
Does universe churn make the H028 conditional null artificially worse?
Continue from:
P13-CP4 — H028 30-Year Objective Alignment Review
and use the structural lesson discovered in:
P14-CP4 / P14-CP6a — H029 null turnover investigations
This is an audit of an already-rejected historical research result.
It is not a new H028 hypothesis.
It is not an attempt to rescue H028.
1. Formal status remains unchanged
H028 remains permanently:

```
ORIGINAL RESEARCH STATUS:
H028 REJECTED
```

and descriptively:

```
30-YEAR OBJECTIVE ALIGNMENT:
PARTIALLY OBJECTIVE-ALIGNED
```

Nothing in this audit may change those statuses.
Do not reopen H028.
Do not refit H028.
Do not create H028b.
Do not create H031.
2. Why this audit now exists
H028's strongest statistical evidence was its fixed-λ conditional null:

```
S_WEALTH_real ≈ 0.224
only 1 of 5,000 null worlds >= real
empirical p ≈ 0.0004
```

The H028 conditional null preserved:

```
LOWVOL
recipient identity
recipient returns
prices
corporate actions
```

while assigning the other ten features as a persistent donor vector:

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

Recent H029 work discovered a structural failure mode in persistent-donor nulls:
eligibility churn can force donor reassignments, creating artificial score/rank discontinuities, additional portfolio turnover and therefore additional trading costs even when there is no predictive signal.
H029's synthetic feasibility work showed that this can occur even in a known no-signal world.
Therefore H028's null significance requires a structural audit.
3. Primary scientific question
Answer only:
Does the H028 conditional-null construction create systematically more score instability, portfolio turnover, or trading cost than the equivalent no-signal real pipeline solely because of universe churn / donor rematching?
A second question follows:
If such an artifact exists, is it large enough that the previously reported H028 empirical p-value should no longer be treated as reliable evidence of stock-selection alpha?
4. Do not inspect new real performance
Do not calculate or re-run:

```
real H028 terminal wealth
real H028 CAGR
real H028 yearly returns
real SPY-relative performance
real H028 alpha
real future-return IC
```

The historical committed values may be referenced as frozen facts where necessary, but do not run a new real strategy evaluation.
5. Holdout remains sealed
Absolutely do not access:

```
2022-01-01 → 2026-08-31
```

No:

```
prices
returns
fundamentals
SPY
metadata
features
sanity checks
```

6. No new H028 null design
Do not design a replacement null.
Do not repair the existing null.
Do not try:

```
sector matching
size matching
turnover matching
trajectory matching
event-copy relay
block permutation
residualization
```

This checkpoint audits the historical H028 null only.
If it fails:
record the failure.
Do not fix it.
7. Reconstruct the exact historical H028 null
Before any synthetic experiment, document exactly:

```
what is randomized
what remains attached to the recipient
when donor mappings are created
when donor mappings persist
when they are re-formed
whether sector is preserved
whether eligibility changes force remapping
whether missingness moves with the donor vector
```

Use the frozen H028 code and specification.
Do not infer from H029.
H028 and H029 null mechanics are similar conceptually but not necessarily identical.
8. Critical donor-remapping audit
For the H028 historical null, determine structurally:

```
recipient-months
possible donor continuations
donors retained
donors re-formed
re-formations caused by:
  recipient entry
  recipient exit
  donor exit
  sector/stratum changes if applicable
  other
```

Report:

```
overall monthly re-pairing rate
average number of affected stocks per review
```

If the exact causes are not available from committed artifacts, inspect the frozen code and reproduce them in synthetic panels.
9. Separate H028 from H029
Explicitly answer:
Is the structural mechanism that caused H029 Null #2 to fail mathematically possible in H028's conditional null?
Do not assume yes.
Prove either:

```
YES — the same class of donor discontinuity exists
```

or:

```
NO — H028's construction prevents it
```

or:

```
PARTIALLY — similar mechanism, different magnitude
```

Explain why.
10. Important H028 difference: LOWVOL stays real
H028 does not randomize every feature.
The recipient keeps its own:

```
LOWVOL
```

while the other ten features are randomized together.
Therefore donor discontinuities affect only part of the Score.
Quantify structurally how much this matters.
Questions:
Can LOWVOL anchor the ranking enough to prevent donor churn from materially increasing turnover?
Or do the ten randomized features still create significant rank jumps?
Do not answer from intuition only.
Test this synthetically.
11. Important H028 difference: Ridge refitting
H028 is not a fixed equal-weight Score.
Every outer fold uses:

```
Ridge
λ = 100
```

Therefore null worlds also alter the model fitting process.
The audit must distinguish:

```
A. donor-remapping effects on feature paths
B. donor-remapping effects on fitted coefficients
C. resulting score/rank instability
D. portfolio turnover
E. trading costs
```

Do not audit only the final Top-15 lists.
12. Synthetic feasibility first
Before touching any real H028 null artifact requiring portfolio-performance computation, build offline synthetic panels.
No QuantConnect run yet.
Use no real market returns.
Generate independent synthetic future returns solely so the frozen Ridge fitting pipeline has a target.
The synthetic returns must contain:

```
NO predictive relation
```

to the eleven features.
The true null is known by construction.
13. Synthetic panel structure
Calibrate synthetic panels approximately to the H028 development environment using structural information only.
Include approximately:

```
realistic monthly eligible-stock count
realistic universe entry/exit rate
monthly review schedule
11 features
persistent feature paths
LOWVOL attached to recipient
ten OTHER features moving together under the historical tether
FF12 sector structure if H028 uses it
H028 Top-15 sector cap
```

Do not calibrate anything using returns.
14. Feature persistence
The synthetic features should not be pure monthly white noise only.
Use at least two structural regimes:

```
A. moderately persistent features
B. strongly persistent features
```

because the artifact may depend on temporal autocorrelation.
LOWVOL should itself be persistent.
The ten-feature vector should also have realistic cross-feature correlation.
No predictive relation to returns.
15. Required synthetic scenarios
Run at minimum:
Scenario S1 — no churn

```
fixed universe
no entries
no exits
```

Purpose:
establish baseline behavior when donor mappings never need repair.
Expected:
real no-signal pipeline and conditional-null worlds should be structurally similar.
Scenario S2 — realistic churn
Use universe churn calibrated to the development universe.
Purpose:
test whether donor-remapping alone creates excess turnover.
Scenario S3 — 2× churn
Purpose:
determine whether any structural bias grows monotonically with churn.
Scenario S4 — LOWVOL-only signal structure, but no return signal
LOWVOL remains persistent and attached to recipients.
The other ten features are noise.
Returns are independent.
Purpose:
determine whether the real attached LOWVOL mechanically stabilizes H028 relative to null worlds.
Scenario S5 — persistent ten-feature vectors, no return signal
Purpose:
stress the donor-continuity mechanism.
16. Full historical null mechanics
For every synthetic null world use the actual frozen H028 conditional-null implementation.
Do not simplify to a different permutation.
Use:

```
same donor persistence logic
same eligibility mechanics
same feature transformation
same λ=100 Ridge
same target construction principle
same outer-fold procedure
same Top-15 mechanics
same sector cap
same monthly rebalance
same transaction-cost model
```

Synthetic returns replace real returns only because this is a known no-signal test.
17. Synthetic sample size
Pre-register before observing results:

```
5 independent synthetic panel seeds
×
200 null worlds per panel
```

for the main realistic-churn scenario.
For S1 / S3 / S4 / S5, at least:

```
3 panel seeds
×
100 null worlds
```

unless computational profiling shows this is unreasonable.
If reduced, document the reason before interpreting results.
18. Primary structural statistics
For each synthetic panel compare the no-signal "real" pipeline with the null worlds on:

```
name turnover
number of new names per rebalance
commissions
slippage
total trading cost
score rank autocorrelation
Top-15 one-month survival
```

Also report where feasible:

```
coefficient-vector stability
score-change magnitude
rank-change magnitude
```

19. Primary audit criterion
The H028 null passes the churn audit only if, in the realistic no-signal synthetic panels:
the synthetic-real structural statistics are not systematically outside the conditional-null distributions.
Specifically for each of:

```
turnover
total trading cost
Top-15 survival
rank persistence
```

require the synthetic-real value to lie inside:

```
[0.5%, 99.5%]
```

of the null distribution in at least:

```
4 of 5
```

main panel seeds.
If the same directional failure occurs in:

```
3 or more of 5
```

panel seeds, classify the null as structurally suspect.
Do not weaken this after results.
20. Strong failure criterion
Immediately classify:

```
H028 NULL STRUCTURAL AUDIT — FAIL
```

if all or nearly all realistic-churn synthetic panels show:

```
synthetic real turnover < every null world
```

or:

```
synthetic real trading cost < every null world
```

analogous to the H029 failure.
21. Churn dose-response
Compare:

```
S1 no churn
S2 realistic churn
S3 2× churn
```

If the real-vs-null structural gap increases systematically with churn, report this as strong evidence of a tether artifact.
Do not fit a model to force a monotonic relation.
Descriptive comparison is sufficient.
22. Decompose the artifact
If a gap exists, estimate how much is attributable to:

```
donor remapping
coefficient refitting
ranking effects
sector-cap interaction
eligibility turnover itself
LOWVOL anchoring
```

Use synthetic experiments that change one structural mechanism at a time.
No return-based optimization.
23. Frozen-coefficient diagnostic
As a diagnostic only, repeat a small subset using fixed synthetic-real coefficients rather than refitting Ridge.
Purpose:
separate the effect of donor churn on the input/ranking process from the effect introduced through retraining.
This is not a candidate strategy.
Do not compare profitability.
24. LOWVOL anchoring diagnostic
Compare structurally:

```
historical H028 conditional null:
LOWVOL real + 10 shuffled
```

with a diagnostic synthetic case where:

```
all 11 features are shuffled
```

Do not use the second version as a proposed null.
Purpose only:
quantify how much keeping LOWVOL attached stabilizes the actual H028 null.
25. Cost amplification
Because H028's empirical statistic is terminal wealth after costs, quantify:

```
extra null turnover
→
extra commissions
→
extra slippage
```

under the frozen H028 cost model:

```
$7 BUY
$7 SELL
10 bps per side
```

On synthetic panels only.
Report:
how much of a null-vs-real wealth difference could arise mechanically from different trading intensity even with no predictive signal.
26. Optional zero-cost diagnostic
If straightforward, rerun a small synthetic subset with:

```
commission = 0
slippage = 0
```

This is diagnostic only.
Question:
Does the structural difference remain in rankings/holdings even after cost effects are removed?
Do not use this to redefine H028's historical test.
27. Real committed H028 null artifacts
Only after the synthetic result is understood, inspect the committed H028 null outputs for structural fields already stored.
Allowed:

```
turnover
trade counts
cost totals
portfolio persistence
coefficient selections
risk metrics
```

Do not launch a new real H028 return run.
If committed null artifacts do not contain these fields, state:

```
NOT AVAILABLE FROM COMMITTED ARTIFACTS
```

Do not rerun 5,000 real null worlds solely to obtain them.
28. Real H028 vs null turnover
If committed data permits, report:

```
real H028 turnover
null turnover median
0.5%
99.5%
real percentile
```

and similarly for:

```
commissions
slippage
trade count
```

This is descriptive audit evidence.
It must not create a new gate retroactively.
29. Historical p-value interpretation
At the end classify the old H028 null evidence into exactly one of:

```
A — STRUCTURALLY SUPPORTED
No material churn-induced bias detected.

B — STRUCTURALLY SUSPECT
Synthetic no-signal worlds show the historical null mechanics systematically disadvantage null portfolios.

C — INCONCLUSIVE
Available evidence cannot determine whether the effect is material.
```

30. Consequences of A
If:

```
A — STRUCTURALLY SUPPORTED
```

state:
H028 remains REJECTED, but its previously reported conditional-null significance remains usable as development evidence.
Do not upgrade H028.
31. Consequences of B
If:

```
B — STRUCTURALLY SUSPECT
```

state:
H028 remains REJECTED, and its historical B1 / p≈0.0004 null-based significance should no longer be treated as reliable evidence of stock-selection alpha.
Do not recompute a corrected p-value.
Do not design a replacement null.
Do not rerun H028.
32. Consequences of C
If:

```
C — INCONCLUSIVE
```

state:
H028 remains REJECTED and the null-based evidence should be treated cautiously.
Do not resolve uncertainty by designing another null.
33. What does not change regardless of result
The following historical evidence remains separate from the null audit:

```
H028 terminal wealth history
H028 CAGR history
H028 MaxDD
H028 volatility
H028 SPY comparison
H028 2015–2017 instability
H028 B4 failure
H028 dependence on 2018 / 2020
```

Do not erase or rewrite those facts.
34. Explicit distinction
The report must clearly distinguish:
economic backtest evidence
from:
statistical null-based evidence.
If the null fails, the economic path still happened in the development backtest.
What changes is how much confidence we place in the claim that the result reflects stock-selection skill rather than structural properties of the test.
35. No impact on H029/H030 closure decision
Do not use this audit to reopen:

```
H029
H030
```

Their null problem is separate.
This audit is historical due diligence on H028 only.
36. Bug rule
If an actual implementation bug is found in the frozen H028 null:

```
STOP
```

and report:

```
H028 HISTORICAL NULL IMPLEMENTATION BUG FOUND
```

Do not silently repair it.
Do not regenerate the historical p-value.
Owner review required.
37. No new QuantConnect run by default
Prefer:

```
frozen pure modules
offline synthetic panels
committed artifacts
```

Only if the exact historical H028 tether logic cannot be exercised offline should a structural-only QuantConnect run be proposed.
Do not execute it without owner approval.
38. Required owner-facing answers
At the top of the checkpoint answer:
Q1
Does H028 use a donor mechanism vulnerable to universe-churn remapping?
Q2
How often would donor remapping occur under realistic synthetic churn?
Q3
Does realistic churn make H028 null portfolios trade more than an equivalent no-signal real portfolio?
Q4
Does keeping LOWVOL attached materially protect against that artifact?
Q5
Does Ridge refitting amplify or reduce it?
Q6
How much extra trading cost does the artifact create?
Q7
Does the effect disappear in the no-churn control?
Q8
Is there a clear churn dose-response?
Q9
Can the historical `p≈0.0004` still be treated as reliable development evidence?
Q10
Does anything here change H028's formal REJECTED status?
Expected answer to Q10:

```
NO
```

39. Required checkpoint
Create:
P13-CP5 — H028 Conditional-Null Structural Audit
Include at minimum:

```
1. H028 permanent REJECTED status
2. Objective-alignment status
3. Audit motivation
4. Historical null specification
5. Exact randomized features
6. Exact preserved features
7. Donor-persistence mechanics
8. Donor-remapping mechanics
9. Comparison with H029 mechanism
10. Synthetic design
11. No-churn scenario
12. Realistic-churn scenario
13. 2× churn scenario
14. LOWVOL-anchor scenario
15. Persistent-feature scenario
16. Synthetic panel counts
17. Null world counts
18. Turnover results
19. Trade-count results
20. Commission results
21. Slippage results
22. Total-cost results
23. Rank-persistence results
24. Top-15 survival results
25. Coefficient-stability results
26. Fixed-coefficient diagnostic
27. LOWVOL anchoring diagnostic
28. Zero-cost diagnostic if performed
29. Churn dose-response
30. Mechanism decomposition
31. Real committed structural fields available
32. Real-vs-null turnover if available
33. Historical p-value interpretation
34. Economic-vs-statistical evidence distinction
35. Bug status
36. Holdout untouched confirmation
37. No new H028 optimization
38. Q1–Q10
39. Final audit classification
40. Exact next owner decision
```

40. Final classification
End with exactly one:

```
H028 NULL STRUCTURAL AUDIT — PASS
HISTORICAL CONDITIONAL-NULL EVIDENCE REMAINS STRUCTURALLY SUPPORTED
```

or:

```
H028 NULL STRUCTURAL AUDIT — FAIL
HISTORICAL CONDITIONAL-NULL SIGNIFICANCE IS STRUCTURALLY SUSPECT
```

or:

```
H028 NULL STRUCTURAL AUDIT — INCONCLUSIVE
```

Then immediately state:

```
H028 FORMAL STATUS REMAINS REJECTED.
```

41. STOP
After committing P13-CP5:

```
STOP
```

Do not:

```
repair the H028 null
create a replacement null
re-run real H028
re-fit H028
change λ
change features
open the Holdout
restart H029/H030
start a new hypothesis
```

Return the audit evidence to the owner.

---

Recorded before any audit statistic was computed. The pre-registered audit is `research/phase13/cp5/P13_CP5_audit.py` (commit 1d7ff5c; Amendment 1 in b61b83e, before any result was read).
