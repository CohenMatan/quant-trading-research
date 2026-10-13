# Owner message 2026-10-13: "Phase 14 — P14-CP3b H029 / H030 Sector-Stratified Null Amendment"

Decision id: **D233**. The owner approved Option 1 of P14-CP3a: replace the original single-stratum H029 / H030 null with a sector-stratified (same-FF12-sector) identity tether.

**What does not change:**
- H029, H030, H028, Data v3, the gates (N1–N5, C1–C7), the costs and the mechanics;
- the adequacy rule;
- the P14-CP3a record, which stays permanently.

**Run order:** new canary (including synthetic A / B) → 5,000 sector-stratified null worlds → seeds 1–25 rerun → the same adequacy rule → (only if adequate) pin the new c_UP_H029 / c_INCREMENTAL_H030 (the old 0.2696 / 0.0059 are permanently invalid) → P14-CP3b frozen → ONE real development evaluation → the frozen gates → (only if C1–C7 all pass) the synthetic long-horizon stage → STOP.

**If the sector null fails adequacy:** H029/H030 BLOCKED — SECTOR-STRATIFIED NULL ALSO INADEQUATE → STOP. No third null.

**Holdout:** sealed.

Recorded and committed before any sector-stratified null world, canary or real H029 / H030 value was computed. The owner's message follows verbatim.

---

Phase 14 — P14-CP3b

H029 / H030 Sector-Stratified Null Amendment

Replace only the inadequate null — no strategy change, no real return access yet

Continue from:

> P14-CP3a — STOP: H029 / H030 NULL INADEQUATE



Owner decision:

> Approve Option 1: replace the original single-stratum H029/H030 null with a sector-stratified identity tether using the same FF12 sector.



This amendment is approved before any real H029 or H030 return, wealth, capture, threshold or gate result has been observed.

The purpose is to correct the structural inadequacy identified in P14-CP3a.


---

1. Preserve the existing stop record

Do not rewrite or remove:

P14-CP3a

Its conclusion remains historically correct:

ORIGINAL SINGLE-STRATUM NULL:
INADEQUATE

Specifically:

H029 real sector HHI = 0.1630

original null 99.5th percentile = 0.1599

only 2 / 5,000 original null worlds
reached the real sector concentration

That failure must remain permanently documented.


---

2. Why the amendment is scientifically allowed

Record explicitly:

> No real H029/H030 portfolio return or performance result was computed before this amendment.



The only real quantities observed were score-only structural quantities required by the pre-registered null-adequacy test.

Therefore this amendment is motivated by:

null structural inadequacy

not by:

poor or favorable strategy performance

Do not describe the new null as pre-registered from the beginning.

Describe it as:

> owner-approved pre-performance methodological amendment following a pre-registered adequacy failure.




---

3. H029 remains unchanged

Do not change any H029 scientific rule.

Preserve exactly:

F1 Revenue Growth Acceleration
F2 Gross Margin Improvement
F4 OCF / Assets Improvement
F5 ROA Improvement
F7 Share Dilution
F8 Asset Turnover Improvement

Preserve:

at least 5 of 6 signals
equal-weight normalized Score
no ML
no Ridge
no λ
Top 15
max 3 per FF12 sector
monthly review
next-open execution
$7 BUY
$7 SELL
10 bps slippage
$100,000 starting capital


---

4. H030 remains unchanged

Preserve exactly:

H030_SCORE =
0.50 * normalized H028 score
+
0.50 * normalized H029 score

Do not test alternative blends.

No:

40/60
60/40
30/70
70/30

H028 remains frozen.


---

5. Data v3 remains frozen

Do not modify:

Data v3
manifest
PIT rules
restatement handling
signal formulas
eligibility

Data v3 already passed P14-CP2.

Do not rebuild it.


---

6. All existing H029/H030 gates remain unchanged

Do not modify:

N1–N5
C1–C7

Do not alter any thresholds or economic requirements.

The only methodological change is the null donor matching rule.


---

7. New H029 null

The original null assigned each recipient stock a donor identity without regard to sector.

Replace this with:

> same-FF12-sector donor assignment



At each review date, for each H029-eligible recipient stock:

recipient sector =
FF12 sector of recipient

The donor must come from:

the same FF12 sector

at that review.


---

8. Preserve the six-signal vector

The donor's six H029 signals must move as a complete vector:

F1
F2
F4
F5
F7
F8

Do not independently shuffle individual features.

This preserves the real cross-feature relationships within the Business Improvement information.


---

9. Preserve recipient outcomes

The recipient must retain its own:

identity
prices
future returns
corporate actions
H028 score
sector
portfolio mechanics

Only the H029 signal vector is reassigned.


---

10. Preserve missingness / eligibility

The new null must preserve the frozen real:

H029 eligible universe

at every review.

Do not allow sector stratification to change which stocks qualify for H029.

Where the existing tether supports recipient-compatible missingness/vector structure, preserve it exactly.


---

11. Persistent donor identity

Use the same persistent identity-tether principle already used in P14-CP3a.

A donor mapping should remain persistent through time as allowed by the existing tether implementation.

Do not independently redraw a new donor every month if the existing identity-tether design is persistent.


---

12. No self-matches

Require:

recipient != donor

If a sector/review does not contain enough valid donor identities to satisfy the rule:

STOP — SECTOR-STRATIFIED NULL NOT CONSTRUCTIBLE

Do not silently fall back to cross-sector assignment.


---

13. Sector definition

Use the same frozen:

FF12

classification already used in the strategy.

Do not create broader or narrower sector groups after viewing results.

Stocks without a valid FF12 classification must follow the already-frozen H029 universe handling.

Do not invent a new sector treatment.


---

14. H030 null

For every H030 null world:

H028 remains fully real and unchanged.

Use the sector-stratified randomized H029 Score as the second component.

Thus:

H030_null =
50% real H028
+
50% sector-stratified randomized H029

after the same frozen cross-sectional rank normalization.

Never randomize H028.


---

15. Scientific interpretation of the new null

The new H029 null asks:

> Within the same sector environment, does the real Business Improvement ranking select stocks with more useful future information than a randomized reassignment of Business Improvement signals among sector peers?



The H030 null asks:

> Does adding the real H029 information to frozen H028 improve the portfolio more than adding randomized same-sector H029 information?



This is now an incremental stock-selection test conditional on sector structure.


---

16. Important tradeoff

Record explicitly:

> The sector-stratified null intentionally does not test whether H029's sector allocation itself is predictive.



It controls that structural source of variation.

Therefore a future H029/H030 significance result should be interpreted as evidence of:

within-sector / conditional stock-selection information

rather than total alpha including sector timing.

This limitation must be disclosed.


---

17. New canary

Before generating 5,000 null worlds, create a new canary.

Verify at minimum:

Data v3 unchanged
H028 unchanged
H029 Score unchanged
H030 50/50 unchanged
recipient eligible sets unchanged
recipient sector unchanged
donor sector == recipient sector
complete six-feature vector moves together
no self-matches
persistent donor mapping
recipient returns unchanged
recipient H028 unchanged
costs unchanged
portfolio mechanics unchanged


---

18. Synthetic A / B

Repeat the existing synthetic checks under the new stratified null.

Synthetic A

Business Improvement is pure noise within sectors.

Expected:

real-style H029 should not systematically beat
sector-stratified null

Synthetic B

Business Improvement contains a planted within-sector predictive signal.

Expected:

real-style H029 should clearly exceed
sector-stratified null

The canary must distinguish these.


---

19. Null world count

If canary passes, generate:

5,000 sector-stratified null worlds

with deterministic:

seeds 1–5000

No real H029/H030 performance run yet.


---

20. Reproducibility

Rerun:

seeds 1–25

Require exact reproduction for all stored null statistics.

Failure:

STOP


---

21. Repeat the same adequacy test

Do not invent a more permissive adequacy test.

Use the exact same pre-existing structural rule:

> the real score-only selection structure must fall inside the null [0.5%, 99.5%] range.



Check again for:

H029 name turnover
H029 FF12 sector HHI
H030 name turnover
H030 FF12 sector HHI


---

22. Important expectation

The sector-stratified null is expected to better reproduce H029 sector concentration, but:

> do not assume it passes.



Calculate the null distribution first.

If the real H029 sector HHI remains outside:

[0.5%, 99.5%]

then:

STOP — SECTOR-STRATIFIED NULL INADEQUATE

Do not create a third null automatically.


---

23. Risk adequacy

Repeat the existing null risk-adequacy audit for:

beta
up capture
down capture
volatility

and any other pre-registered P14-CP3a adequacy statistics.

Use exactly the existing criteria.

If they fail:

STOP — SECTOR-STRATIFIED NULL INADEQUATE


---

24. Compare old and new null descriptively

Because the original null result is already committed, report side by side:

Original single-stratum null
Sector-stratified null

for:

H029 sector HHI distribution
H029 turnover distribution
H030 sector HHI distribution
H030 turnover distribution
beta
up capture
down capture
volatility

This comparison is descriptive.

Do not choose between nulls based on which produces a more favorable significance threshold.

The original null is already rejected on adequacy grounds.


---

25. Only if the new null passes adequacy

If and only if every new adequacy test passes:

calculate and pin:

c_UP_H029 =
99th percentile of S_UP_H029 sector-null

and:

c_INCREMENTAL_H030 =
99th percentile of S_INCREMENTAL_H030 sector-null

Do not reuse the old values:

0.2696
0.0059

Those belong to the inadequate null and are permanently invalid.


---

26. Pin before real performance

Commit and merge the following before the one real run:

new null methodology
code hashes
Data v3 manifest
H028 hash
H029/H030 spec hash
5,000 null seeds
adequacy results
c_UP_H029
c_INCREMENTAL_H030

Only then may real performance be computed.


---

27. One real development run

After thresholds are pinned:

run exactly one real:

H029
H030

development evaluation for the frozen:

2015–2021

period.

Do not perform exploratory real runs beforehand.


---

28. Apply the already-frozen H029 gates

Apply exactly:

N1 — upside-null significance
N2 — up capture >= 1.00 and positive SPY-up relative contribution
N3 — upside temporal breadth
N4 — downside sanity
N5 — doubled-slippage upside robustness

No changes.


---

29. Apply the already-frozen H030 gates

Apply exactly:

C1 — incremental-null significance
C2 — >=5% terminal wealth improvement over H028
C3 — up capture >=1.00 and positive up-month contribution
C4 — down capture <=0.80
C5 — regime-concentration stress
C6 — risk
C7 — doubled-slippage robustness

No changes.


---

30. Do not reinterpret significance

Because the null now controls for sector clustering, if H029 passes N1 the correct interpretation is:

> H029 contains significant predictive information beyond randomized same-sector Business Improvement assignments.



Do not claim:

> H029 proves sector allocation itself is alpha.



That question is no longer being tested by this null.


---

31. H029/H030 statuses

If H029 fails its gates:

H029 UPSIDE SIGNAL REJECTED

If it passes:

H029 UPSIDE SIGNAL CANDIDATE

If H030 fails:

H030 REJECTED —
PRE-REGISTERED 50/50 COMBINATION
DOES NOT SUFFICIENTLY IMPROVE H028

If all H030 gates pass:

H030 DEVELOPMENT CANDIDATE —
PRE-REGISTERED H028 + H029 COMBINATION

Holdout remains sealed in every case.


---

32. Synthetic long-horizon stage

Preserve the existing rule:

> Run the expensive long-horizon synthetic stage only if H030 passes all C1–C7.



If it does not:

STOP

Do not run the 30-year simulation simply for curiosity.


---

33. If sector null fails again

If the sector-stratified null fails adequacy:

H029/H030 BLOCKED —
SECTOR-STRATIFIED NULL ALSO INADEQUATE

Then STOP.

Do not automatically try:

industry matching
sector + size matching
sector + market-cap deciles
propensity matching
residualized nulls

Any third null requires separate owner review.


---

34. Engineering

Current host is already at approximately:

7.7 GB
50 project files

Do not add a new subclass simply for the amendment if it exceeds the file limit.

Consolidating test/helper files is allowed as infrastructure work provided:

scientific calculations remain exactly unchanged

Verify all prior frozen digests after any consolidation.


---

35. Required checkpoint before the real run

Create:

> P14-CP3b — H029/H030 Sector-Stratified Null Amendment



Include at minimum:

1. P14-CP3a original null failure.
2. Owner amendment approval.
3. Confirmation no real performance existed before amendment.
4. Original null methodology.
5. New same-FF12-sector methodology.
6. Scientific rationale.
7. Limitation: sector alpha is conditioned out.
8. H029 unchanged.
9. H030 unchanged.
10. Data v3 unchanged.
11. H028 unchanged.
12. Gates unchanged.
13. Canary result.
14. Synthetic A result.
15. Synthetic B result.
16. 5,000-world completion.
17. seeds 1–25 reproducibility.
18. H029 turnover adequacy.
19. H029 sector-HHI adequacy.
20. H030 turnover adequacy.
21. H030 sector-HHI adequacy.
22. risk adequacy.
23. old-vs-new null comparison.
24. final null adequacy decision.
25. new c_UP_H029 if adequate.
26. new c_INCREMENTAL_H030 if adequate.
27. proof old thresholds were not reused.
28. proof thresholds pinned before real result.
29. exact next step.


---

36. If adequacy passes, continue under original P14-CP3 protocol

After P14-CP3b is frozen:

run the ONE real development evaluation

and continue the already-approved H029/H030 assessment.

Do not redesign the experiment.


---

37. Holdout

Absolutely do not access:

2022-01-01 → 2026-08-31

No prices.

No fundamentals.

No SPY returns.

No diagnostic peek.


---

38. Final principle

The methodological change is exactly:

OLD NULL:
donor may come from any sector

NEW NULL:
donor must come from the recipient's FF12 sector

Nothing else changes.

The reason is:

> The first null failed because it destroyed a structural sector-clustering property of the real Business Improvement signal.



The amendment must not be used as an opportunity to modify the strategy or its success criteria.


---

39. STOP condition

If the sector-stratified null passes adequacy, continue only according to the already-approved run order.

If it fails:

STOP

and return to the owner.

Do not design a third null.
