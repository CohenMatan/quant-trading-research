# Owner message 2026-10-12: "Phase 14 — H029-A Fundamental / Business Improvement Score, Data Feasibility Audit + Design Pre-Registration Only"

Decision id: **D227**.

**What the owner approved:** the start of design work for a new, independent direction, H029 (Business Improvement / Fundamental Momentum). This phase, H029-A, is a data-feasibility audit only. It asks whether the committed point-in-time Data v2.1 can support eight pre-specified Business Improvement signal families (F1–F8), judged on:
- coverage;
- staleness;
- revision and restatement safety;
- survivorship.

**What is not allowed in this phase:**
- forward returns, IC, Sharpe, CAGR, wealth or any SPY-relative performance;
- feature-return correlations or any portfolio;
- choosing features by profitability.

**Unchanged:**
- H028 remains REJECTED and frozen; no H030.
- The Holdout (2022-01-01 → 2026-08-31) stays sealed.
- Nothing is purchased, and Data v2.1 is not rebuilt.

**Next:** STOP after P14-CP1. The next step would be a separately approved H029-B pre-registration.

Recorded and committed before any H029 feature value or coverage statistic was computed. The owner's message follows verbatim.

---

Phase 14 — H029-A

Fundamental / Business Improvement Score

Data Feasibility Audit + Design Pre-Registration Only

Continue from:

> P13-CP4 — H028 30-Year Objective Alignment Review



The owner has approved beginning design work for a new, independent research direction.

Do not implement or backtest H029 yet.

Do not start H030.


---

1. Research context

The standing long-term objective is now:

> Maximize approximately 30-year terminal wealth relative to SPY while maintaining strong participation in rising markets and materially better protection in falling markets.



Future strategies do not need to beat SPY every calendar year.

Isolated losing years are acceptable.

The desired structural behavior is:

strong upside participation
+
material downside protection
+
superior long-horizon compounding


---

2. H028 remains frozen

H028 remains permanently:

ORIGINAL RESEARCH STATUS:
H028 REJECTED

and descriptively:

30-YEAR OBJECTIVE ALIGNMENT:
PARTIALLY OBJECTIVE-ALIGNED

Do not modify H028.

Do not refit H028.

Do not use H028's weak years to choose H029 features.

Do not tune H029 specifically for:

2015
2016
2018
2020

H028 should remain available later only as a frozen research benchmark.


---

3. Why H029 exists

P13-CP4 showed that H028 already provides useful downside protection:

monthly up capture ≈ 0.97
monthly down capture ≈ 0.69

but its edge versus SPY was concentrated in falling-market episodes, especially 2018 and 2020.

The missing capability is:

> independent upside alpha in ordinary and rising markets.



Therefore H029 will investigate a fundamentally different information source:

> Business Improvement / Fundamental Momentum



The hypothesis is not:

> "Good companies outperform."



The hypothesis is:

> Companies whose underlying business fundamentals are improving may subsequently outperform companies whose fundamentals are stagnant or deteriorating.




---

4. H029 must initially be standalone

H029 must not include:

H028 score
LOWVOL overlay
H028 coefficients
H028 ranking
H028 regime logic

The reason is scientific separation.

We first need to determine whether Business Improvement contains useful information on its own.

Only a later, separately pre-registered H030 may combine H028 and H029.


---

5. H029-A purpose

This phase asks only:

> Can the existing committed point-in-time dataset support a clean Business Improvement Score without unacceptable missingness, staleness, revision leakage, or survivorship problems?



No return prediction is permitted in H029-A.

No strategy result is permitted in H029-A.


---

6. Strict prohibition on performance inspection

During H029-A do not calculate or inspect:

forward stock returns
future excess returns
IC
Sharpe
CAGR
terminal wealth
SPY-relative performance
feature-return correlations
portfolio performance
top-decile returns

Do not rank candidate features by historical profitability.

The audit must be based only on:

economic rationale
PIT feasibility
coverage
data quality
stability
staleness
outlier behavior


---

7. No Holdout access

Absolutely do not access:

2022-01-01 → 2026-08-31

No:

prices
returns
fundamentals
metadata
sanity checks
filings

The Holdout remains sealed.


---

8. Data source

Use the already frozen / owner-approved:

Data v2.1

Preserve all existing PIT and restatement rules.

Preserve the existing Data v2.1 owner exception documentation.

Do not rebuild the dataset.

Do not purchase data.


---

9. Allowed development data for feasibility

The feasibility audit may inspect already-seen development-period fundamental availability from:

2011–2021

This entire period is already development data.

But again:

> no future-return information may be examined.




---

10. Universe

Use the same basic investable universe definition already used by the programme:

US common stocks
price >= $5
market cap >= $2B
ADV20 >= $5M
long only

Use point-in-time eligibility.

Do not silently introduce today's index membership.

Do not require current survivors.


---

11. Candidate signal families

Audit these eight pre-specified Business Improvement families.

Do not add additional signal families after seeing coverage.

F1 — Revenue Growth Acceleration

Concept:

> Is revenue growth accelerating?



Preferred construction concept:

current YoY revenue growth
minus
previous-quarter YoY revenue growth

Example:

Q1 YoY growth = +8%
Q2 YoY growth = +14%

Acceleration = +6 percentage points


---

F2 — Gross Margin Improvement

Concept:

> Is the company's gross profitability improving?



Preferred concept:

current gross margin
minus
comparable prior-period gross margin

Prefer TTM or YoY-comparable constructions rather than quarter-to-quarter seasonality when feasible.


---

F3 — Operating Margin Improvement

Concept:

> Is operating profitability improving?



Preferred concept:

current operating margin
minus
comparable prior-period operating margin


---

F4 — Operating Cash-Flow Improvement

Concept:

> Is cash generation improving?



Audit viable PIT-safe forms such as:

OCF / Revenue change

or:

OCF / Assets change

Do not choose between alternatives based on returns.

Report which is structurally cleaner given the existing data.


---

F5 — Profitability Improvement

Concept:

> Is economic profitability improving?



Audit whether a clean PIT-safe measure such as:

ROA change

or an already-supported gross-profitability metric can be constructed consistently.

Again, do not choose based on returns.


---

F6 — Leverage / Net Debt Improvement

Concept:

> Is the balance sheet becoming less leveraged?



Audit whether existing data supports a stable measure such as:

Debt / Assets change

or preferably:

Net Debt / Assets change

if cash and debt coverage is sufficient.

Improvement should mean lower leverage.


---

F7 — Share Dilution

Concept:

> Is the company issuing additional equity or reducing share count?



Audit PIT-safe share-count availability.

Candidate concept:

YoY percentage change in shares outstanding

Lower dilution / buybacks would score more favorably.

Do not use future split-adjusted information incorrectly.


---

F8 — Asset Efficiency Improvement

Concept:

> Is the company generating more revenue from its asset base?



Candidate:

Revenue / Assets

and its comparable-period change.


---

12. These are candidate families, not yet the final H029 formula

H029-A must not silently decide:

which features receive weight
which features are dropped
which transformation wins

except where a feature is objectively infeasible under the pre-registered data-quality criteria below.

Return findings to the owner first.


---

13. Raw-field inventory

For every F1–F8 identify exactly which frozen dataset fields would be required.

Produce a table:

Signal	Required raw fields	Available?	PIT timestamp available?	History depth



Include any denominator fields needed.


---

14. PIT availability audit

For every required accounting value determine:

statement period end
actual availability timestamp used by Data v2.1
restatement handling
earliest permissible trading date

Confirm that H029 could never use a filing before it was available to the market.


---

15. Restatement audit

Improvement signals are especially vulnerable to restatements because they compare multiple periods.

For each candidate determine whether Data v2.1 can reconstruct:

> what the investor would have believed at that historical timestamp



rather than using a later-restated historical quarter.

If not, flag:

PIT RESTATEMENT RISK

Do not proceed with that feature silently.


---

16. History requirements

Determine how much history each candidate requires.

For example:

YoY growth acceleration
may require at least 5 historical quarters

because both current and previous YoY growth must exist.

Report exact warm-up requirements.


---

17. Monthly coverage

For every candidate F1–F8 compute, without using returns:

eligible stock-months
feature-available stock-months
coverage percentage

for each month.

Summarize separately:

2011–2014
2015–2017
2018–2021

and overall.


---

18. Coverage criteria

Pre-register these descriptive feasibility levels:

STRONG:
median monthly coverage >= 85%

USABLE:
median monthly coverage >= 70% and < 85%

WEAK:
median monthly coverage >= 50% and < 70%

UNUSABLE:
median monthly coverage < 50%

Also flag any feature where:

more than 10% of development months
have coverage below 50%

Do not change thresholds after seeing results.


---

19. Cross-sectional breadth

For each candidate report monthly:

median number of eligible stocks
median number with valid feature
minimum
5th percentile

A feature with acceptable percentage coverage but very small cross-section must be clearly flagged.


---

20. Sector coverage

Check whether missingness is strongly concentrated by FF12 sector.

For every candidate report:

coverage by sector

and identify any sector with structurally weak availability.

This is data-quality analysis, not performance analysis.


---

21. Time trend in availability

Determine whether coverage improves materially over time.

For example:

> 55% in 2011–2013 but 92% by 2018–2021.



This matters because apparent future performance could otherwise reflect changes in data availability.

Do not fix this in H029-A.

Just report it.


---

22. Staleness

For every stock-month feature observation calculate, where possible:

days since latest underlying financial disclosure

Report:

median
75th percentile
90th percentile
95th percentile
maximum

by candidate.

We need to know whether H029 would often rank stocks using very stale information.


---

23. Update frequency

Report how frequently each candidate actually changes:

monthly
quarterly
irregularly

and empirical median months between updates.

Because a monthly portfolio using quarterly fundamentals may repeatedly reuse the same score.

That is acceptable, but must be understood.


---

24. Outlier audit

Without reference to returns, inspect raw candidate distributions.

For every candidate report:

1st percentile
5th
median
95th
99th
minimum
maximum

Identify common accounting-pathology problems such as:

tiny denominators
negative equity
near-zero revenue
M&A discontinuities
sign flips
very small asset bases

Do not implement winsorization yet unless already part of the frozen Data v2.1 feature methodology.

Return recommendations separately.


---

25. Seasonality risk

For F1–F5 and F8 specifically assess whether:

quarter-over-quarter

comparisons would create unacceptable seasonality.

Prefer comparable-period logic such as:

YoY
TTM vs prior TTM

when supported.

But H029-A should only recommend the cleanest construction.

Do not backtest alternatives.


---

26. TTM feasibility

For relevant features determine whether PIT-safe trailing-twelve-month values can be constructed from available quarterly filings.

Audit:

coverage
warm-up
restatement safety
missing-quarter behavior

Do not interpolate missing quarters.


---

27. Negative-denominator problems

Audit whether candidate ratios become unstable when:

revenue <= 0
assets <= 0
equity <= 0
net income near zero

Recommend deterministic mathematical handling where necessary.

Do not choose handling based on performance.


---

28. Duplicate information audit

Without using returns, measure cross-sectional correlation among candidate feature values.

Use monthly rank correlations and summarize over development.

This is permitted because it only examines redundancy among inputs.

Produce a correlation matrix and identify:

near duplicates
strongly overlapping feature families

Suggested descriptive threshold:

median |Spearman rho| >= 0.80

Flag as high redundancy.

Do not automatically delete one.


---

29. Relationship with H028 features

This is allowed only as an input-overlap diagnostic.

Compare candidate H029 features against the existing H028 feature values:

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

using feature-value correlations only.

Do not inspect portfolio returns.

The goal is to determine whether H029 really adds a different information family.


---

30. LOWVOL independence

Specifically report correlation of each H029 candidate with:

LOWVOL

because H029 is intended to be fundamentally distinct from H028's defensive behavior.

A high correlation is not an automatic rejection.

Just disclose it.


---

31. Proposed transformation framework

Do not choose weights yet.

Recommend whether the same simple monthly cross-sectional transformation used elsewhere is feasible:

percentile rank
→ map to [-1,+1]

For "lower is better" features such as dilution or leverage increase, direction may be inverted.

But final signs must come from economic definition, not returns.


---

32. No machine learning in initial H029

The preliminary H029 concept should remain:

no Ridge
no λ
no random forest
no boosting
no neural network
no feature-selection optimization

The preferred future design is a transparent fixed Score.

H029-A should determine whether this is feasible.


---

33. Equal-weight concept

The provisional design principle is:

> If a feature is ultimately approved for H029, each approved feature initially receives equal weight after cross-sectional normalization.



For example, with six features:

H029_SCORE =
(F1 + F2 + F3 + F4 + F5 + F6) / 6

This is a design principle only.

Do not finalize the number of features until the feasibility audit is reviewed by the owner.


---

34. Missing-feature handling audit

Assess these possible approaches without testing returns:

A. Require all approved signals to be present.
B. Average available signals if a minimum count is met.

Quantify resulting universe coverage under each approach.

Do not select the method based on future performance.

Return the tradeoff to the owner.


---

35. Preliminary minimum-feature-count analysis

For the candidate set F1–F8 report what fraction of eligible stock-months would have at least:

8 / 8
7 / 8
6 / 8
5 / 8
4 / 8

signals available.

This will help decide a future deterministic missing-data rule.


---

36. Potential universe bias

Compare companies with valid H029 data versus companies without valid H029 data using only contemporaneous characteristics already available:

market cap
price
ADV
sector

Do not compare future returns.

Determine whether H029 availability would systematically bias the universe toward:

larger
more liquid
specific sectors


---

37. Candidate feasibility classification

For each F1–F8 assign one:

A — CLEANLY FEASIBLE
B — FEASIBLE WITH DOCUMENTED DATA HANDLING
C — MATERIAL DATA QUALITY CONCERN
D — NOT FEASIBLE

Base this only on data integrity.

For every classification provide the reason.


---

38. Overall H029 feasibility gate

H029-A may conclude:

H029 DATA FEASIBILITY — PASS

only if at least:

5 of the 8

candidate signal families are rated:

A or B

and the proposed combined-score universe can maintain:

median monthly coverage >= 70%

under at least one transparent missing-data approach.

Otherwise:

H029 DATA FEASIBILITY — FAIL

This is only a data gate.

It says nothing about expected profitability.


---

39. Do not automatically proceed after PASS

Even if H029-A passes:

STOP

Do not implement the Score.

Do not calculate returns.

Return to owner review.

The next step would be a separately approved:

> H029-B Final Hypothesis & Strategy Pre-Registration




---

40. Future H029 research objective

For context only, if later approved, H029 will primarily test:

> Does a fixed Business Improvement Score produce independent stock-selection alpha, particularly during rising markets?



The future evaluation standard should eventually include:

SPY terminal wealth
up capture
down capture
SPY-positive-month excess return
strong-up-market participation
rolling 3y / 5y results
risk
cost robustness
null worlds
regime concentration
synthetic long-horizon robustness

But none of these are to be computed in H029-A.


---

41. Future benchmark structure

If H029 eventually reaches backtesting, expected comparisons are:

SPY — primary market benchmark
H028 — frozen champion research benchmark
LV15 — defensive reference where useful

But H029-A must not compare their returns.


---

42. Important anti-tuning rule

Do not use this audit to say:

> "Feature X had poor coverage, but Feature Y would probably make more money."



No return-based judgments are permitted.

Likewise, do not add a replacement ninth feature after seeing audit results.

If fewer than five features survive:

> return to owner.




---

43. Engineering feasibility

Also report:

estimated additional memory required
new files/modules required
whether the current QuantConnect 50-file limit affects future implementation

Recall S030 already reached:

50 project files

H029-A may recommend consolidation/refactoring before implementation.

Do not perform a large architectural refactor unless required merely to inspect existing data.


---

44. Existing-host separation

Prefer that future H029 implementation not become another subclass layered indefinitely on:

S028 → S029 → S030

Recommend whether Phase 14 should begin from a cleaner standalone research host while preserving frozen components.

Design recommendation only.


---

45. Owner-facing questions

At the top of the checkpoint answer these simply:

Q1

Do we have enough PIT fundamental data to build a Business Improvement Score?

Q2

Which of F1–F8 are cleanly feasible?

Q3

Which are problematic and why?

Q4

How many stocks per month would receive a usable H029 Score?

Q5

Does coverage materially worsen in the earlier years?

Q6

Are restatements or publication timing a serious leakage risk?

Q7

Are any proposed signals essentially duplicates of one another?

Q8

How different are these signals from H028's existing information?

Q9

Can we build H029 without ML, λ, or optimized weights?

Q10

What exact decisions must the owner make before any backtest is allowed?


---

46. Required checkpoint

Create:

> P14-CP1 — H029 Business Improvement Data Feasibility Audit



Include at minimum:

1. Owner objective.
2. H028 frozen status.
3. H029 rationale.
4. Explicit no-return-analysis confirmation.
5. Data v2.1 reference.
6. Holdout confirmation.
7. Universe definition.
8. F1 definition.
9. F2 definition.
10. F3 definition.
11. F4 definition.
12. F5 definition.
13. F6 definition.
14. F7 definition.
15. F8 definition.
16. Raw-field mapping.
17. PIT timing audit.
18. Restatement audit.
19. Warm-up/history requirements.
20. Monthly coverage by feature.
21. Early/middle/late coverage.
22. Sector coverage.
23. Staleness.
24. Update frequency.
25. Outlier audit.
26. Seasonality assessment.
27. TTM feasibility.
28. Denominator/pathology risks.
29. Candidate correlation matrix.
30. Correlation with H028 features.
31. Correlation with LOWVOL.
32. Transformation recommendation.
33. Missing-data alternatives.
34. Minimum-feature-count coverage.
35. Universe-bias audit.
36. F1 feasibility class.
37. F2 feasibility class.
38. F3 feasibility class.
39. F4 feasibility class.
40. F5 feasibility class.
41. F6 feasibility class.
42. F7 feasibility class.
43. F8 feasibility class.
44. Combined feasibility gate.
45. Memory estimate.
46. 50-file-limit impact.
47. Host/refactor recommendation.
48. Confirmation no backtest.
49. Confirmation no H029 strategy result.
50. Exact owner decisions required for H029-B.


---

47. Final status

End with exactly one of:

H029 DATA FEASIBILITY — PASS

or:

H029 DATA FEASIBILITY — FAIL

Then state clearly:

> This is a data-quality result only. No evidence regarding H029 profitability has been generated.




---

48. STOP

After committing P14-CP1:

STOP

Do not implement H029.

Do not calculate any strategy return.

Do not start H030.

Do not access the Holdout.

Return the feasibility evidence to the owner.
