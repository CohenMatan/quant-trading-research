# Owner message 2026-10-12: "Phase 13 — P13-CP3 H028 Long-Horizon Synthetic Path Robustness Study"

Decision id: **D223**. A descriptive, offline long-horizon bootstrap study of the already-observed 2015–2021 H028 / LV15 / SPY monthly returns. It has five parts:
- complete-year blocks (primary);
- 12- and 24-month moving blocks;
- leave-one-year-out and leave-2018-and-2020-out stresses;
- a 7-year resampling interval;
- regime frequency.

H028 stays permanently REJECTED. The study is not a null test, not validation and not a repair of B4.
- No new QuantConnect run, no new data and no Holdout.
- The methodology is committed before any aggregate result.

Recorded and committed before any bootstrap statistic was computed. The owner's message follows verbatim.

---

Phase 13 — P13-CP3

H028 Long-Horizon Synthetic Path Robustness Study

30-Year Bootstrap Worlds — Descriptive Only

Continue from:

> P13-CP2 — H028 2015–2016 Descriptive Post-Mortem



The formal status remains permanently:

> H028 REJECTED — FIXED STRONG SHRINKAGE DOES NOT ROBUSTLY SOLVE THE TEMPORAL-STABILITY PROBLEM



Do not reopen H028.

Do not start H029.

Do not modify B4 or any historical gate.

This task is a descriptive long-horizon robustness study only.


---

1. Research question

The owner wants to understand:

> If the types of relative performance observed during 2015–2021 occurred repeatedly in different orders over a much longer investment horizon, how often would H028 finish ahead of SPY and LV15?



Specifically:

> What would H028's long-run path risk look like over synthetic 5-, 10-, 20- and 30-year histories?



This is not intended to manufacture new evidence.

It is intended to understand the implications of the evidence already observed.


---

2. Critical interpretation

State prominently in the checkpoint:

> Synthetic 30-year paths do NOT equal 30 years of new historical evidence.



They reuse the already-seen:

2015–2021

development returns.

Therefore they cannot:

- validate H028;
- repair B4;
- turn H028 into a candidate;
- estimate unbiased future success probability;
- create new market regimes;
- substitute for the sealed Holdout.

The correct interpretation is:

> Conditional on the return/regime behavior observed during 2015–2021, how sensitive is H028's long-run result to the order and repetition of those observed environments?




---

3. No new strategy research

Do not change:

λ
features
feature weights
target
Top-15 rule
sector cap
rebalance frequency
cost assumptions
execution timing
LOWVOL definition

Do not retrain anything.

Do not search for a better version of H028.


---

4. Holdout remains completely sealed

Do not access:

2022-01-01 → 2026-08-31

in any form.

No:

prices
SPY returns
fundamentals
features
market statistics
sanity checks

The bootstrap donor pool must contain only the already-used development period.


---

5. Offline only

This study should use committed outputs only.

No new QuantConnect backtest.

No external data.

No web data.

No purchased data.

Use the existing committed H028, LV15 and SPY equity/return artifacts.


---

6. Reconstruct a clean monthly return panel

Build one aligned monthly panel covering:

2015-01 through 2021-12

with:

month
H028_return
LV15_return
SPY_return

That should produce:

84 aligned months

before any simulation.

The three return series must stay paired.

Never independently resample H028, LV15 and SPY.


---

7. Return integrity

H028 and LV15 returns should reflect the already-realized strategy results after their actual transaction costs.

SPY must use the same benchmark definition as P13-CP1.

Before simulation, verify that compounding the reconstructed monthly series reproduces the committed terminal performance within documented tolerance.

Report:

reconstructed H028 wealth
committed H028 wealth

reconstructed LV15 wealth
committed LV15 wealth

reconstructed SPY wealth
committed SPY wealth


---

8. Final-liquidation artifact check

Explicitly inspect whether a forced final liquidation cost at the end of 2021 contaminates the final monthly return.

A terminal backtest liquidation is not a normal recurring monthly event and must not accidentally be repeated every time the bootstrap samples December 2021.

If such an artifact exists and can be removed deterministically using committed cost records, remove only that artificial terminal component for the bootstrap donor return series and document it.

Do not alter ordinary trading costs.

If it cannot be separated reliably:

STOP — BOOTSTRAP RETURN SERIES NOT CLEANLY RECONSTRUCTIBLE


---

9. Primary bootstrap design — complete calendar years

This is the main study.

Treat each real calendar year:

2015
2016
2017
2018
2019
2020
2021

as one joint 12-month block.

For one synthetic 30-year world:

1. sample 30 calendar-year blocks with replacement;
2. preserve all 12 months inside each sampled year in their original order;
3. use the exact same sampled block for H028, LV15 and SPY;
4. concatenate the 30 blocks;
5. obtain a 360-month synthetic history.

Do not modify returns inside a sampled year.


---

10. Number of worlds

Run:

10,000 synthetic 30-year worlds

using deterministic seeds:

1 → 10,000

This is not a null test.

Do not calculate a null threshold.


---

11. Why paired sampling matters

Every sampled block must preserve the actual contemporaneous relationship among:

H028
LV15
SPY

For example, if 2020 is sampled, all three portfolios must receive their real 2020 return sequence together.

Never create a world where:

H028 gets 2020
SPY gets 2016
LV15 gets 2019

That would destroy the economic comparison.


---

12. Wealth construction

Start every synthetic portfolio at:

$100,000

Compound the sampled monthly returns.

For numerical stability, preferably accumulate:

log(1 + monthly_return)

and convert back to wealth when reporting.


---

13. Required horizons

Although every simulated path is 30 years, evaluate results after:

5 years
10 years
20 years
30 years

For every horizon calculate:

P(H028 terminal wealth > SPY)
P(H028 terminal wealth > LV15)

P(H028 wealth >= 1.15 × SPY)

P(H028 excess CAGR vs SPY >= +2 percentage points)

median H028/SPY wealth ratio
5th percentile
25th percentile
75th percentile
95th percentile

median H028/LV15 wealth ratio
5th percentile
25th percentile
75th percentile
95th percentile

median excess CAGR vs SPY
5th percentile excess CAGR
95th percentile excess CAGR


---

14. Probability of ending behind

For:

5
10
20
30 years

report:

percentage of worlds where H028 ends below SPY
percentage where H028 ends below LV15

This is one of the primary owner-facing outputs.


---

15. Long underperformance streaks

For each 30-year synthetic world calculate annual returns.

Then calculate the longest consecutive streak in which:

H028 annual return < SPY annual return

and separately:

H028 annual return < LV15 annual return

Report the distribution of longest losing streaks:

median
75th percentile
90th percentile
95th percentile
99th percentile
maximum

Also calculate:

P(at least 3 consecutive years behind SPY)
P(at least 5 consecutive years behind SPY)
P(at least 10 consecutive years behind SPY)

and the same versus LV15.


---

16. Number of winning years

For each 30-year world report the number of calendar years in which:

H028 > SPY

and:

H028 > LV15

Summarize:

median
5th percentile
25th percentile
75th percentile
95th percentile

This is important because H028 historically beat SPY in only a minority of individual development years despite winning strongly in terminal wealth.


---

17. Relative-wealth drawdown

Construct:

RelativeWealth_SPY =
H028 cumulative wealth / SPY cumulative wealth

For every world calculate the maximum drawdown of this relative-wealth series.

This measures:

> How far can H028 fall behind SPY before recovering?



Report:

median relative MaxDD
75th percentile
90th percentile
95th percentile
99th percentile
worst world

Repeat versus LV15.


---

18. Rolling 5-year underperformance

Inside each synthetic 30-year world calculate every rolling 60-month H028/SPY return.

Report:

P(world contains at least one 5-year period where H028 loses to SPY)

P(world contains at least one 5-year period where H028 trails SPY by >= 10%)

P(world contains at least one 5-year period where H028 trails SPY by >= 20%)

Repeat versus LV15.

This is important for understanding investor patience required.


---

19. Time-to-recovery

Whenever H028/SPY relative wealth falls below its previous high-water mark, calculate the duration until a new relative high is reached.

Report across all worlds:

median longest recovery
90th percentile
95th percentile
99th percentile

in months and years.

Repeat versus LV15.


---

20. Main 30-year result table

Produce a compact owner-facing table:

Metric	H028 vs SPY	H028 vs LV15

% winning after 5y		
% winning after 10y		
% winning after 20y		
% winning after 30y		
Median 30y wealth ratio		
5th percentile wealth ratio		
95th percentile wealth ratio		
Median excess CAGR		
P(5 consecutive losing years)		
Median max relative DD		
95th percentile max relative DD		



---

21. Sensitivity test A — 12-month moving blocks

The complete-year bootstrap may depend on calendar-year boundaries.

Therefore run a second pre-registered simulation.

Create every available contiguous 12-month block from the 84-month donor series.

A block must contain the paired:

H028
LV15
SPY

returns.

Sample blocks with replacement until at least:

360 months

then truncate exactly to 360 months.

Run:

10,000 worlds

using deterministic seeds.

Do not use circular wrapping inside donor blocks.


---

22. Sensitivity test B — 24-month moving blocks

Repeat using contiguous:

24-month blocks

sampled with replacement.

Again generate:

10,000 × 30-year worlds

with the three portfolios sampled jointly.

This preserves longer regime persistence.


---

23. Compare bootstrap methods

Compare:

calendar-year blocks
12-month moving blocks
24-month moving blocks

for at least:

P(H028 > SPY after 30 years)
median H028/SPY ratio
5th percentile H028/SPY ratio
median excess CAGR
P(5 consecutive losing years)
95th percentile relative MaxDD

The purpose is to determine whether the conclusion is highly sensitive to bootstrap construction.


---

24. Critical concentration stress — remove one year

The original research already identified substantial period dependence.

Therefore run a pre-registered leave-one-year-out analysis.

For each donor year:

2015
2016
2017
2018
2019
2020
2021

remove that complete year from the calendar-year donor pool.

Then generate:

5,000 × 30-year worlds

from the remaining six years.

Report for every exclusion:

P(H028 > SPY after 30 years)
median wealth ratio
5th percentile wealth ratio
median excess CAGR

This is a stress diagnostic only.


---

25. Special 2018 + 2020 exclusion stress

Because earlier H026/H027 analysis identified 2018 and 2020 as unusually favorable periods, perform one additional pre-registered stress:

Remove both:

2018
2020

from the donor set.

Use only:

2015
2016
2017
2019
2021

Generate:

10,000 × 30-year worlds

using complete-year sampling.

Report the same long-run metrics.

This test is intentionally harsh.

Do not interpret it as a realistic probability model.

It asks:

> If the two strongest defensive environments never recur, what remains of H028's observed edge?




---

26. Conversely, avoid favorable cherry-picking

Do not run:

best-year-only worlds
bull-only worlds
crash-only worlds

Do not search arbitrary subsets of years.

Only the pre-registered exclusions above are permitted.


---

27. Sampling uncertainty in the observed edge

Using complete-year resampling, create:

100,000 bootstrap samples

of length:

7 years

from the seven observed years.

For each sample calculate annualized:

log(H028/SPY)

and:

log(H028/LV15)

Report bootstrap:

median
2.5th percentile
97.5th percentile

This is a descriptive uncertainty interval.

Do not call it an independent confidence interval for future alpha, because H028 was developed on these same years.


---

28. Regime-frequency output

For the primary 30-year bootstrap report how often each donor year is sampled across worlds.

Verify approximately uniform sampling.

Also report, for illustration, the relationship between terminal H028/SPY wealth and number of occurrences of:

2015
2016
2017
2018
2019
2020
2021

Do not use this to optimize a regime rule.

This is descriptive only.


---

29. 2018/2020 dependence

Explicitly answer:

> How much of the favorable 30-year synthetic result depends on repeatedly sampling 2018 and/or 2020?



Use:

- leave-2018-out;
- leave-2020-out;
- leave-both-out;

rather than narrative speculation.


---

30. Important statistical warning

Include prominently:

Because H028 was created after observing much of 2011–2021 and was evaluated repeatedly during development:

> these bootstrap frequencies are conditional robustness statistics, not unbiased probabilities that H028 will beat SPY in the real future.



For example:

87% of synthetic worlds beat SPY

must be written as:

> H028 beat SPY in 87% of synthetic paths generated from the observed 2015–2021 return blocks.



Never write:

> There is an 87% chance H028 will beat SPY.




---

31. Do not use the results to repair B4

Even if:

99% of 30-year worlds beat SPY

H028 remains:

REJECTED

because its original pre-registered B4 failed.

This study may influence what we research next.

It may not rewrite the past gate.


---

32. No automatic Holdout decision

Even very strong synthetic results do not authorize:

2022–2026 Holdout

After this study:

STOP

and return to the owner.


---

33. Reproducibility

Before viewing aggregate results, commit:

bootstrap algorithm
block definitions
world counts
seeds
metrics
leave-one-out rules
2018+2020 stress rule

Then run.

Rerun at least:

seeds 1–100

and require exact reproduction.


---

34. No changing methodology after results

After seeing results do not change:

block length
number of worlds
sampling weights
year exclusions
metrics

Any additional simulation design would require a new owner decision.


---

35. Required owner-facing answers

At the top of the final checkpoint answer these in plain English.

Q1

If we repeatedly remix the observed 2015–2021 environments, how often does H028 finish above SPY after 5, 10, 20 and 30 years?

Q2

How often does H028 finish above LV15?

Q3

How long can H028 realistically appear broken and remain behind SPY in these synthetic paths?

Q4

How bad can the relative drawdown become?

Q5

Does the result remain favorable under 12-month and 24-month block sampling?

Q6

How much does the result depend on 2018?

Q7

How much does it depend on 2020?

Q8

What happens when both 2018 and 2020 are removed?

Q9

Does the study strengthen the case that H028 has an economically interesting development signal, without changing its REJECTED status?

Q10

What can this study NOT tell us?


---

36. Required checkpoint

Create:

> P13-CP3 — H028 Long-Horizon Synthetic Path Robustness



Include at minimum:

1. H028 permanent REJECTED status.
2. Study purpose.
3. Explicit synthetic-data limitation.
4. Donor period.
5. Number of donor months.
6. Monthly-series reconciliation.
7. Final-liquidation audit.
8. Primary year-block algorithm.
9. 10,000-world count.
10. Seeds.
11. 5-year results.
12. 10-year results.
13. 20-year results.
14. 30-year results.
15. H028/SPY distributions.
16. H028/LV15 distributions.
17. excess CAGR distributions.
18. losing-year streak distributions.
19. relative drawdown distributions.
20. rolling 5-year underperformance.
21. recovery-time distributions.
22. 12-month-block results.
23. 24-month-block results.
24. method sensitivity comparison.
25. leave-2015-out.
26. leave-2016-out.
27. leave-2017-out.
28. leave-2018-out.
29. leave-2019-out.
30. leave-2020-out.
31. leave-2021-out.
32. leave-2018-and-2020-out.
33. 7-year bootstrap uncertainty.
34. regime-frequency analysis.
35. 2018/2020 dependence.
36. reproducibility result.
37. no parameter changes.
38. no new QC run.
39. no new data.
40. Holdout untouched.
41. direct Q1–Q10 answers.
42. exact next owner decision.


---

37. Final output language

End with a descriptive summary, not a candidate status.

Use one of:

SYNTHETIC ROBUSTNESS RESULT —
H028 REMAINS FAVORABLE ACROSS MOST RESAMPLED LONG-HORIZON PATHS

or:

SYNTHETIC ROBUSTNESS RESULT —
H028 IS HIGHLY SENSITIVE TO PATH / REGIME COMPOSITION

or:

SYNTHETIC ROBUSTNESS RESULT —
H028 LONG-HORIZON EVIDENCE IS MIXED

The chosen wording must be supported by the pre-registered metrics.

Then state separately:

FORMAL RESEARCH STATUS:
H028 REJECTED


---

38. STOP

After committing P13-CP3:

STOP

Do not start H029.

Do not open the Holdout.

Return the results to the owner.
